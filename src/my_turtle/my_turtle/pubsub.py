import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

class PubSub(Node):
    def __init__(self):
        super().__init__('pub_sub')

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

    def operation(self, msg):
        cmd = Twist()
        if msg.x > 10.0:
            cmd.linear.x = 0.0
        else:
            cmd.linear.x = 1.0

        self.publisher_.publish(cmd)

def main():
    rclpy.init()
    node = PubSub()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
