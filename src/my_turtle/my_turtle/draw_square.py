import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
import math

class DrawSquare(Node):
    def __init__(self):
        super().__init__('draw_square')

        self.publisher_ = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.subscriber_ = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.operation,
            10
        )

        self.state = 'forward'
        self.start_x = None
        self.start_y = None

        self.declare_parameter('side_length', 1.5)
        self.declare_parameter('forward_speed', 1.0)
        self.declare_parameter('turn_speed',0.2)

        self.side_length = self.get_parameter('side_length').value
        self.forward_speed = self.get_parameter('forward_speed').value
        self.turn_speed = self.get_parameter('turn_speed').value


        self.cnt = 0
        self.get_logger().info('初始化成功')

    def operation(self, msg):
        if self.start_x is None:
            self.start_x = msg.x
            self.start_y = msg.y
            self.get_logger().info(f'起点: ({msg.x:.2f}, {msg.y:.2f})')

        dist = math.hypot(msg.x-self.start_x, msg.y-self.start_y)

        cmd = Twist()

        if self.state == 'forward':
            if dist < self.side_length:
                cmd.linear.x = self.forward_speed
            else:
                self.get_logger().info('走够了，停！')
                self.start_theta = msg.theta
                self.state = 'turn'

        elif self.state == 'turn':
            dtheta = abs(msg.theta - self.start_theta)
            self.get_logger().info(f'start_theta={self.start_theta:.3f}  now={msg.theta:.3f}  dtheta={dtheta:.3f}')
            if dtheta < math.pi/2:
                cmd.angular.z = self.turn_speed
            else:
                self.get_logger().info('转够了，停！')
                self.cnt += 1
                if self.cnt >= 4:
                    self.state = 'done'
                else:
                    self.state = 'forward'
                    self.start_x = msg.x
                    self.start_y = msg.y
        else:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0

        self.publisher_.publish(cmd)

def main():
    rclpy.init()
    node = DrawSquare()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()