import math
import time
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from nav2_msgs.action import NavigateToPose

POINTS = [
    ('P1', 0.0, 0.0),
    ('P2', 2.5, 1.2),
    ('P3', 1.5, -1.3),
    ('P4', -1.8, -0.8),
    ('P5', -3.0, 1.2),
]


class Patrol(Node):
    def __init__(self):
        super().__init__('patrol')
        self.cli = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.get_logger().info('等 navigate_to_pose ...')
        self.cli.wait_for_server()
        self.rec = 0
        self.px = None
        self.py = None

    def fb(self, msg):
        self.rec = msg.feedback.number_of_recoveries

    def goto(self, name, x, y, timeout=180.0):
        g = NavigateToPose.Goal()
        g.pose.header.frame_id = 'map'
        g.pose.pose.position.x = float(x)
        g.pose.pose.position.y = float(y)
        if self.px is None:
            g.pose.pose.orientation.w = 1.0
        else:
            yaw = math.atan2(y - self.py, x - self.px)
            g.pose.pose.orientation.z = math.sin(yaw / 2.0)
            g.pose.pose.orientation.w = math.cos(yaw / 2.0)
        self.px, self.py = x, y
        self.rec = 0
        t0 = time.time()
        f = self.cli.send_goal_async(g, feedback_callback=self.fb)
        rclpy.spin_until_future_complete(self, f)
        gh = f.result()
        if gh is None or not gh.accepted:
            return name, x, y, 'REJECTED', 0.0, 0
        rf = gh.get_result_async()
        while not rf.done() and time.time() - t0 < timeout:
            rclpy.spin_once(self, timeout_sec=0.1)
        dt = time.time() - t0
        if not rf.done():
            gh.cancel_goal_async()
            return name, x, y, 'TIMEOUT', dt, self.rec
        code = rf.result().result.error_code
        return name, x, y, ('OK' if code == 0 else 'FAIL(%d)' % code), dt, self.rec


def main():
    rclpy.init()
    n = Patrol()
    rows = []
    try:
        for name, x, y in POINTS:
            r = n.goto(name, x, y)
            rows.append(r)
            print('%-3s (%+.1f,%+.1f)  %-9s %6.1f s  recoveries=%d'
                  % (r[0], r[1], r[2], r[3], r[4], r[5]), flush=True)
    finally:
        ok = sum(1 for r in rows if r[3] == 'OK')
        tot = sum(r[4] for r in rows)
        print('\n===== 汇总 =====')
        print('完成: %d/%d  总耗时 %.1f s  平均 %.1f s/点  总恢复 %d'
              % (ok, len(rows), tot, tot / max(1, len(rows)),
                 sum(r[5] for r in rows)))
        n.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
