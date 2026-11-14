import sys, time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from moveit_msgs.srv import GetMotionPlan
from moveit_msgs.msg import Constraints, JointConstraint
from moveit_msgs.action import ExecuteTrajectory

class Gripper(Node):
    def __init__(self):
        super().__init__('gripper_client')
        self.plan = self.create_client(GetMotionPlan, 'plan_kinematic_path')
        self.exec = ActionClient(self, ExecuteTrajectory, 'execute_trajectory')
        if not self.plan.wait_for_service(timeout_sec=5.0): sys.exit('规划服务没起来')
        if not self.exec.wait_for_server(timeout_sec=5.0): sys.exit('执行 action 没起来')

    def move(self, opening):
        req = GetMotionPlan.Request()
        m = req.motion_plan_request
        m.group_name = 'hand'
        m.allowed_planning_time = 2.0
        m.num_planning_attempts = 5
        c = Constraints()
        for name in ('panda_finger_joint1', 'panda_finger_joint2'):
            jc = JointConstraint()
            jc.joint_name = name
            jc.position = opening
            jc.tolerance_above = 0.001
            jc.tolerance_below = 0.001
            jc.weight = 1.0
            c.joint_constraints.append(jc)
        m.goal_constraints.append(c)
        fut = self.plan.call_async(req)
        rclpy.spin_until_future_complete(self, fut)
        res = fut.result()
        if res.motion_plan_response.error_code.val != 1:
            print('夹爪规划失败 code=%d' % res.motion_plan_response.error_code.val); return False
        goal = ExecuteTrajectory.Goal()
        goal.trajectory = res.motion_plan_response.trajectory
        g = self.exec.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, g)
        rf = g.result().get_result_async()
        while not rf.done():
            rclpy.spin_once(self, timeout_sec=0.05)
        ok = rf.result().result.error_code.val == 1
        print('夹爪 -> %.3f m  %s' % (opening, 'OK' if ok else 'FAIL'))
        return ok

def main():
    rclpy.init()
    n = Gripper()
    n.move(0.04)   # 张开
    n.move(0.0)    # 闭合
    n.move(0.04)   # 再张开
    n.destroy_node(); rclpy.shutdown()

if __name__ == '__main__':
    main()
