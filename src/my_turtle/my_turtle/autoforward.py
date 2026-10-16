import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan

class AutoForward(Node):
    def __init__(self):
        super().__init__('autoforward')

        self.last_dist = 9999.0

        self.subscriber_ = self.create_subscription(
            LaserScan,
            '/scan',
            self.forward,
            10
        )

        self.publisher_ = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

    def forward(self,msg):
        cmd = Twist()
        self.i_left = int((-0.175-msg.angle_min)/msg.angle_increment)
        self.i_right = int((0.175-msg.angle_min)/msg.angle_increment)
        eff = [r for r in msg.ranges[int(self.i_left):int(self.i_right)] if r != float('inf')]
        self.get_logger().info(f'扇区里有效数据 = {len(eff)} 个')
        # self.get_logger().info(f'ranges 总长度 = {len(msg.ranges)}')
        # self.get_logger().info(f'ranges[180] = {msg.ranges[180]}')
        # self.judg = float(min(msg.ranges[self.i_left:self.i_right]))
        # self.get_logger().info(f'judg = {self.judg}')
        if len(eff) > 0:
            self.last_dist = eff[-1]
            self.get_logger().info(f'最后距离 = {self.last_dist}')
        if self.last_dist < 1.5:
            cmd.linear.x = 0.0
        else:
            cmd.linear.x = -0.3
        self.publisher_.publish(cmd)

def main():
    rclpy.init()
    node = AutoForward()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
