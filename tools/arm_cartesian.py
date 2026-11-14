import sys
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import Pose
from moveit_msgs.srv import GetCartesianPath
from moveit_msgs.action import ExecuteTrajectory

class Cartesian(Node):
    def __init__(self):
        super().__init__('cartesian_client')
        self.cart = self.create_client(GetCartesianPath, 'compute_cartesian_path')
        self.exec = ActionClient(self, ExecuteTrajectory, 'execute_trajectory')
        if not self.cart.wait_for_service(timeout_sec=5.0): sys.exit('cartesian 服务没起来')
        if not self.exec.wait_for_server(timeout_sec=5.0): sys.exit('执行 action 没起来')

    def line_down(self, x, y, z0, z1, steps=10):
        req = GetCartesianPath.Request()
        req.header.frame_id = 'panda_link0'
        req.group_name = 'panda_arm'
        req.link_name = 'panda_link8'
        req.start_state.is_diff = True
        req.max_step = 0.005
        req.jump_threshold = 0.0
        req.avoid_collisions = True
        for i in range(1, steps + 1):
            t = i / steps
            ps = Pose()
            ps.position.x = x
            ps.position.y = y
            ps.position.z = z0 + (z1 - z0) * t
            ps.orientation.w = 1.0
            req.waypoints.append(ps)
        fut = self.cart.call_async(req)
        rclpy.spin_until_future_complete(self, fut)
        res = fut.result()
        print('笛卡尔: fraction = %.2f   error_code = %d' % (res.fraction, res.error_code.val))
        return res.solution if res.fraction > 0.99 else None

    def execute(self, traj):
        goal = ExecuteTrajectory.Goal()
        goal.trajectory = traj
        g = self.exec.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, g)
        gh = g.result()
        if gh is None or not gh.accepted:
            print('执行被拒'); return False
        rf = gh.get_result_async()
        while not rf.done():
            rclpy.spin_once(self, timeout_sec=0.05)
        ok = (rf.result().status == 4) and (rf.result().result.error_code.val == 1)
        print('执行 -> %s' % ('到位' if ok else '失败'))
        return ok

def main():
    rclpy.init()
    n = Cartesian()
    traj = n.line_down(0.4, 0.0, 0.5, 0.4)
    if traj is None:
        print('笛卡尔路径不完整（fraction < 1），不执行')
    else:
        n.execute(traj)
    n.destroy_node(); rclpy.shutdown()

if __name__ == '__main__':
    main()
