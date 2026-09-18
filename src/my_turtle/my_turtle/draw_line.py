import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class TurtleLiner(Node):
    def __init__(self):
        super().__init__("turtle_liner")

        self.publisher_ = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.timer = self.create_timer(0.1, self.send_command)

    def send_command(self):
        msg = Twist()
        msg.linear.x = 1.0
        self.publisher_.publish(msg)

def main():
    rclpy.init()
    node = TurtleLiner()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == "__main__":  
    main()