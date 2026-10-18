import rclpy
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener
from tf2_geometry_msgs import do_transform_point     # ★ 新 import
from geometry_msgs.msg import PointStamped           # ★ 新 impor

class TFlookup(Node):
    def __init__(self):
        super().__init__('tf_lookup')
        self.buffer = Buffer()
        self.listener = TransformListener(self.buffer, self)
        self.timer = self.create_timer(0.5, self.tick)

    def tick(self):
        try:
            t = self.buffer.lookup_transform('odom', 'base_link', rclpy.time.Time())
            self.get_logger().info(f'x={t.transform.translation.x:.2f}')
        except Exception as e:
            self.get_logger().warn(f'查不到：{e}')     # ★ 必须 try

        # ★ 新的一段
        t = self.buffer.lookup_transform('odom', 'laser_link', rclpy.time.Time())

        p = PointStamped()
        p.header.frame_id = 'laser_link'
        p.point.x = 1.0          # 假设雷达正前方 1 米有个点
        p_out = do_transform_point(p, t)

        self.get_logger().info(f'转完：x={p_out.point.x:.2f}, y={p_out.point.y:.2f}')

def main():
    rclpy.init()
    node = TFlookup()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
