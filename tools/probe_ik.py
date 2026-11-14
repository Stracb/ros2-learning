import math, sys
import rclpy
from rclpy.node import Node
from moveit_msgs.srv import GetPositionIK

X, Y, Z = 0.40, 0.0, 0.52

class Probe(Node):
    def __init__(self):
        super().__init__('ik_probe')
        self.ik = self.create_client(GetPositionIK, 'compute_ik')
        if not self.ik.wait_for_service(timeout_sec=5.0):
            sys.exit('compute_ik 没起来')

    def try_ik(self, deg):
        th = math.radians(deg) / 2.0
        req = GetPositionIK.Request()
        r = req.ik_request
        r.group_name = 'panda_arm'
        r.pose_stamped.header.frame_id = 'panda_link0'
        r.pose_stamped.pose.position.x = X
        r.pose_stamped.pose.position.y = Y
        r.pose_stamped.pose.position.z = Z
        # 手朝下，再绕竖直轴转 deg
        r.pose_stamped.pose.orientation.x = -math.sin(th)
        r.pose_stamped.pose.orientation.y =  math.cos(th)
        r.pose_stamped.pose.orientation.z = 0.0
        r.pose_stamped.pose.orientation.w = 0.0
        r.avoid_collisions = True
        fut = self.ik.call_async(req)
        rclpy.spin_until_future_complete(self, fut)
        res = fut.result()
        if res is None or res.error_code.val != 1:
            return None
        return list(res.solution.joint_state.position[:7])

def main():
    rclpy.init()
    n = Probe()
    print('位置 (%.2f, %.2f, %.2f)，试 8 个朝向：' % (X, Y, Z))
    print('%-6s %-46s %s' % ('转角', '7 个关节角', '最大|q|'))
    best = None
    for deg in range(0, 360, 45):
        q = n.try_ik(deg)
        if q is None:
            print('%-6d %s' % (deg, '无解'))
            continue
        mx = max(abs(v) for v in q)
        flag = '  <-- 舒服' if mx < 2.7 else ('  <-- 接近极限' if mx > 2.85 else '')
        print('%-6d %-46s %.2f%s' % (deg, '[%.2f, %.2f, %.2f, %.2f, %.2f, %.2f, %.2f]' % tuple(q), mx, flag))
        if best is None or mx < best[1]:
            best = (deg, mx)
    if best:
        print('\n推荐转角: %d 度（最大关节角 %.2f）' % best)
    n.destroy_node(); rclpy.shutdown()

if __name__ == '__main__':
    main()
