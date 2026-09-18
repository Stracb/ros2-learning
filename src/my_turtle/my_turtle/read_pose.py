import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose

class ReadPose(Node):
    def __init__(self):
        super().__init__('read_pose')

        self.subscriber_ = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.read_pose,
            10
        )

    def read_pose(self,msg):
        self.x = msg.x
        self.y = msg.y
        self.get_logger().info(f"收到 x={self.x} y={self.y}")

def main():
    rclpy.init()
    node = ReadPose()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()