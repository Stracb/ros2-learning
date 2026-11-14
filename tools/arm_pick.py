#!/usr/bin/env python3
"""抓取并搬运：从 --pick 抓起来，放到 --place。

用法:
  python3 arm_pick.py                          # 默认 A(0.4,0,0.3) -> B(0.3,-0.3,0.3)
  python3 arm_pick.py --pick 0.4 0 0.3 --place 0.3 -0.3 0.3 --yaw 180
"""
import sys, copy, math, argparse
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from sensor_msgs.msg import JointState
from geometry_msgs.msg import Pose
from shape_msgs.msg import SolidPrimitive
from trajectory_msgs.msg import JointTrajectoryPoint
from moveit_msgs.srv import GetPositionIK, GetMotionPlan, GetCartesianPath, ApplyPlanningScene
from moveit_msgs.msg import (Constraints, JointConstraint, RobotTrajectory,
                             PlanningScene, CollisionObject, AttachedCollisionObject)
from moveit_msgs.action import ExecuteTrajectory

READY = [0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785]
LIFT   = 0.10          # 抓取点上方留多少
GRIP_Z = 0.09          # link8 到指尖的距离（近似）
BOX_ID = 'target_box'

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pick',  nargs=3, type=float, default=[0.40,  0.00, 0.30])
    ap.add_argument('--place', nargs=3, type=float, default=[0.30, -0.30, 0.30])
    ap.add_argument('--size',  type=float, default=0.05)
    ap.add_argument('--yaw',   type=float, default=180.0, help='绕竖直轴转角(度)')
    return ap.parse_args()

class Picker(Node):
    def __init__(self, yaw_deg, size):
        super().__init__('arm_pick')
        th = math.radians(yaw_deg) / 2.0
        self.qx, self.qy = -math.sin(th), math.cos(th)   # 手朝下 + 绕竖直轴 yaw
        self.size = size
        self.ik   = self.create_client(GetPositionIK, 'compute_ik')
        self.plan = self.create_client(GetMotionPlan, 'plan_kinematic_path')
        self.cart = self.create_client(GetCartesianPath, 'compute_cartesian_path')
        self.aps  = self.create_client(ApplyPlanningScene, 'apply_planning_scene')
        self.exec = ActionClient(self, ExecuteTrajectory, 'execute_trajectory')
        for cli, nm in ((self.ik,'compute_ik'), (self.plan,'plan_kinematic_path'),
                        (self.cart,'compute_cartesian_path'), (self.aps,'apply_planning_scene')):
            if not cli.wait_for_service(timeout_sec=5.0):
                sys.exit('服务没起来: ' + nm)
        if not self.exec.wait_for_server(timeout_sec=5.0):
            sys.exit('执行 action 没起来')
        self.js = None
        self.create_subscription(JointState, '/joint_states', self.on_js, 10)

    def on_js(self, msg):
        self.js = msg

    def _spin(self, fut, t=20.0):
        rclpy.spin_until_future_complete(self, fut, timeout_sec=t)
        return fut.result()

    # ---------- 基础能力 ----------
    def solve_ik(self, x, y, z):
        req = GetPositionIK.Request()
        r = req.ik_request
        r.group_name = 'panda_arm'
        r.pose_stamped.header.frame_id = 'panda_link0'
        r.pose_stamped.pose.position.x = x
        r.pose_stamped.pose.position.y = y
        r.pose_stamped.pose.position.z = z
        r.pose_stamped.pose.orientation.x = self.qx
        r.pose_stamped.pose.orientation.y = self.qy
        r.pose_stamped.pose.orientation.w = 0.0
        r.avoid_collisions = True
        for _ in range(20):
            rclpy.spin_once(self, timeout_sec=0.05)
            if self.js is not None:
                break
        if self.js is not None:
            r.robot_state.joint_state.name = list(self.js.name)
            r.robot_state.joint_state.position = list(self.js.position)
        res = self._spin(self.ik.call_async(req))
        if res is None or res.error_code.val != 1:
            return None
        return list(res.solution.joint_state.position[:7])

    def plan_to(self, joints, group='panda_arm', names=None):
        req = GetMotionPlan.Request()
        m = req.motion_plan_request
        m.group_name = group
        m.allowed_planning_time = 5.0
        m.num_planning_attempts = 10
        c = Constraints()
        if names is None:
            names = ['panda_joint%d' % i for i in range(1, 8)]
        for nm, q in zip(names, joints):
            jc = JointConstraint()
            jc.joint_name = nm
            jc.position = q
            jc.tolerance_above = 0.001
            jc.tolerance_below = 0.001
            jc.weight = 1.0
            c.joint_constraints.append(jc)
        m.goal_constraints.append(c)
        res = self._spin(self.plan.call_async(req))
        if res is None or res.motion_plan_response.error_code.val != 1:
            return None
        return res.motion_plan_response.trajectory

    def cartesian_line(self, p0, p1, steps=10, avoid_collisions=True):
        req = GetCartesianPath.Request()
        req.header.frame_id = 'panda_link0'
        req.group_name = 'panda_arm'
        req.link_name = 'panda_link8'
        req.start_state.is_diff = True
        req.max_step = 0.005
        req.jump_threshold = 0.0
        req.avoid_collisions = avoid_collisions
        for i in range(1, steps + 1):
            t = i / steps
            ps = Pose()
            ps.position.x = p0[0] + (p1[0]-p0[0]) * t
            ps.position.y = p0[1] + (p1[1]-p0[1]) * t
            ps.position.z = p0[2] + (p1[2]-p0[2]) * t
            ps.orientation.x = self.qx
            ps.orientation.y = self.qy
            ps.orientation.w = 0.0
            req.waypoints.append(ps)
        res = self._spin(self.cart.call_async(req))
        if res is None:
            return None
        print('    直线 fraction = %.2f' % res.fraction)
        return res.solution if res.fraction > 0.99 else None

    def execute(self, traj):
        if traj is None:
            return False
        goal = ExecuteTrajectory.Goal()
        goal.trajectory = traj
        g = self._spin(self.exec.send_goal_async(goal))
        if g is None or not g.accepted:
            print('    [execute] 目标被拒'); return False
        rf = g.get_result_async()
        while not rf.done():
            rclpy.spin_once(self, timeout_sec=0.05)
        res = rf.result()
        if res.status != 4 or res.result.error_code.val != 1:
            print('    [execute] 失败 status=%d code=%d' % (res.status, res.result.error_code.val))
            return False
        return True

    def gripper_direct(self, opening, sec=1.0):
        cur = [0.0, 0.0]
        if self.js is not None:
            for i, nm in enumerate(self.js.name):
                if nm == 'panda_finger_joint1': cur[0] = self.js.position[i]
                elif nm == 'panda_finger_joint2': cur[1] = self.js.position[i]
        traj = RobotTrajectory()
        traj.joint_trajectory.joint_names = ['panda_finger_joint1', 'panda_finger_joint2']
        p0 = JointTrajectoryPoint(); p0.positions = [cur[0], cur[1]]; p0.time_from_start.sec = 0
        p1 = JointTrajectoryPoint(); p1.positions = [opening, opening]
        p1.velocities = [0.0, 0.0]
        p1.time_from_start.sec = int(sec); p1.time_from_start.nanosec = 0
        traj.joint_trajectory.points = [p0, p1]
        return self.execute(traj)

    # ---------- 场景：抓 / 放 ----------
    def _box(self, x, y, z):
        co = CollisionObject()
        co.header.frame_id = 'panda_link0'
        co.id = BOX_ID
        prim = SolidPrimitive(); prim.type = SolidPrimitive.BOX
        prim.dimensions = [self.size] * 3
        pose = Pose()
        pose.position.x, pose.position.y, pose.position.z = x, y, z
        pose.orientation.w = 1.0
        co.primitives.append(prim)
        co.primitive_poses.append(pose)
        return co

    def add_to_world(self, x, y, z):
        co = self._box(x, y, z); co.operation = CollisionObject.ADD
        sc = PlanningScene(); sc.is_diff = True
        sc.world.collision_objects.append(co)
        req = ApplyPlanningScene.Request(); req.scene = sc
        res = self._spin(self.aps.call_async(req))
        return res is not None and res.success

    def grab(self, x, y, z):
        """盒子从世界挪到手上"""
        co = self._box(x, y, z); co.operation = CollisionObject.REMOVE
        sc = PlanningScene(); sc.is_diff = True
        sc.world.collision_objects.append(co)
        aco = AttachedCollisionObject()
        aco.link_name = 'panda_hand'
        aco.object = copy.deepcopy(self._box(x, y, z))
        aco.object.operation = CollisionObject.ADD
        aco.touch_links = ['panda_hand', 'panda_leftfinger', 'panda_rightfinger']
        sc.robot_state.attached_collision_objects.append(aco)
        req = ApplyPlanningScene.Request(); req.scene = sc
        return self._spin(self.aps.call_async(req)).success

    def release(self, x, y, z):
        """盒子从手上挪回世界（放到 x,y,z）"""
        co = self._box(x, y, z); co.operation = CollisionObject.ADD
        sc = PlanningScene(); sc.is_diff = True
        sc.world.collision_objects.append(co)
        aco = AttachedCollisionObject()
        aco.link_name = 'panda_hand'
        aco.object.id = BOX_ID
        aco.object.operation = CollisionObject.REMOVE
        sc.robot_state.attached_collision_objects.append(aco)
        req = ApplyPlanningScene.Request(); req.scene = sc
        return self._spin(self.aps.call_async(req)).success

def main():
    args = parse_args()
    rclpy.init()
    n = Picker(args.yaw, args.size)
    px, py, pz = args.pick
    qx, qy, qz = args.place
    gz = n.size / 2 + GRIP_Z

    print('== 抓取: (%.2f, %.2f, %.2f)   放置: (%.2f, %.2f, %.2f)   yaw=%.0f =='
          % (px, py, pz, qx, qy, qz, args.yaw))

    print('1) 清场：盒子放回世界原点位')
    n.add_to_world(px, py, pz)

    print('2) 回 ready')
    print('   ->', 'OK' if n.execute(n.plan_to(READY)) else 'FAIL')

    print('3) 张爪')
    print('   ->', 'OK' if n.gripper_direct(0.04) else 'FAIL')

    print('4) 到抓取点上方')
    q = n.solve_ik(px, py, pz + gz + LIFT)
    if q is None:
        print('   IK 无解，换个 --yaw 试试'); return
    print('   ->', 'OK' if n.execute(n.plan_to(q)) else 'FAIL')

    print('5) 竖直下落')
    print('   ->', 'OK' if n.execute(n.cartesian_line((px, py, pz+gz+LIFT), (px, py, pz+gz))) else 'FAIL')

    print('6) 闭爪 + attach')
    n.gripper_direct(0.0)
    print('    attach ->', 'OK' if n.grab(px, py, pz) else 'FAIL')

    print('7) 提到安全高度')
    print('   ->', 'OK' if n.execute(n.cartesian_line((px, py, pz+gz), (px, py, pz+gz+LIFT), avoid_collisions=False)) else 'FAIL')

    print('8) 移到放置点上方')
    q = n.solve_ik(qx, qy, qz + gz + LIFT)
    if q is None:
        print('   放置点 IK 无解'); return
    print('   ->', 'OK' if n.execute(n.plan_to(q)) else 'FAIL')

    print('9) 竖直下落')
    print('   ->', 'OK' if n.execute(n.cartesian_line((qx, qy, qz+gz+LIFT), (qx, qy, qz+gz), avoid_collisions=False)) else 'FAIL')

    print('10) 张爪 + release')
    n.gripper_direct(0.04)
    print('    release ->', 'OK' if n.release(qx, qy, qz) else 'FAIL')

    print('11) 提起离开')
    print('   ->', 'OK' if n.execute(n.cartesian_line((qx, qy, qz+gz), (qx, qy, qz+gz+LIFT), avoid_collisions=False)) else 'FAIL')

    print('== 完成 ==')
    n.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
