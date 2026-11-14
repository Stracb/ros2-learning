import sys
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from moveit_msgs.srv import GetPositionIK, GetMotionPlan
from moveit_msgs.msg import Constraints, JointConstraint
from sensor_msgs.msg import JointState
from moveit_msgs.action import ExecuteTrajectory

class ArmClient(Node):
    def __init__(self):
        super().__init__('arm_client')
        self.ik = self.create_client(GetPositionIK, 'compute_ik')
        self.plan = self.create_client(GetMotionPlan, 'plan_kinematic_path')
        self.exec = ActionClient(self, ExecuteTrajectory, 'execute_trajectory')
        for cli, name in ((self.ik, 'compute_ik'), (self.plan, 'plan_kinematic_path')):
            if not cli.wait_for_service(timeout_sec=5.0):
                self.get_logger().error('服务没起来: ' + name)
                sys.exit(1)
        if not self.exec.wait_for_server(timeout_sec=5.0):
            self.get_logger().error('执行 action 没起来')
            sys.exit(1)
        self.js = None
        self.create_subscription(JointState, '/joint_states', self.on_js, 10)

    def on_js(self, msg):
        self.js = msg

    def solve_ik(self, x, y, z):
        req = GetPositionIK.Request()
        r = req.ik_request
        r.group_name = 'panda_arm'
        r.pose_stamped.header.frame_id = 'panda_link0'
        r.pose_stamped.pose.position.x = x
        r.pose_stamped.pose.position.y = y
        r.pose_stamped.pose.position.z = z
        r.pose_stamped.pose.orientation.y = 1.0   # 手朝下
        r.pose_stamped.pose.orientation.w = 0.0
        r.avoid_collisions = True
        for _ in range(20):
            rclpy.spin_once(self, timeout_sec=0.05)
            if self.js is not None:
                break
        if self.js is not None:
            r.robot_state.joint_state.name = list(self.js.name)
            r.robot_state.joint_state.position = list(self.js.position)
        fut = self.ik.call_async(req)
        rclpy.spin_until_future_complete(self, fut)
        res = fut.result()
        if res.error_code.val != 1:
            return None
        return list(res.solution.joint_state.position[:7])

    def plan_to(self, joints):
        req = GetMotionPlan.Request()
        m = req.motion_plan_request
        m.group_name = 'panda_arm'
        m.allowed_planning_time = 5.0
        m.num_planning_attempts = 10
        c = Constraints()
        for i, q in enumerate(joints, start=1):
            jc = JointConstraint()
            jc.joint_name = 'panda_joint%d' % i
            jc.position = q
            jc.tolerance_above = 0.001
            jc.tolerance_below = 0.001
            jc.weight = 1.0
            c.joint_constraints.append(jc)
        m.goal_constraints.append(c)
        fut = self.plan.call_async(req)
        rclpy.spin_until_future_complete(self, fut)
        res = fut.result()
        if res.motion_plan_response.error_code.val != 1:
            self.get_logger().error('规划失败 code=%d' % res.motion_plan_response.error_code.val)
            return None
        return res.motion_plan_response.trajectory

    def execute(self, traj):
        goal = ExecuteTrajectory.Goal()
        goal.trajectory = traj
        fut = self.exec.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, fut)
        gh = fut.result()
        if gh is None or not gh.accepted:
            self.get_logger().error('执行目标被拒')
            return False
        rf = gh.get_result_async()
        while not rf.done():
            rclpy.spin_once(self, timeout_sec=0.05)
        res = rf.result()
        ok = (res.status == 4) and (res.result.error_code.val == 1)
        if not ok:
            self.get_logger().error('执行失败 status=%d code=%d' % (res.status, res.result.error_code.val))
        return ok

def main():
    rclpy.init()
    n = ArmClient()
    q = n.solve_ik(0.4, 0.0, 0.5)
    if q is None:
        print('IK 无解'); return
    print('IK  ->', [round(v, 3) for v in q])
    traj = n.plan_to(q)
    if traj is None:
        print('规划失败'); return
    pts = traj.joint_trajectory.points
    dur = pts[-1].time_from_start.sec + pts[-1].time_from_start.nanosec / 1e9
    print('规划 -> %d 个轨迹点，时长 %.2f s' % (len(pts), dur))
    print('执行中 ...')
    if n.execute(traj):
        print('执行 -> 到位')
    n.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
