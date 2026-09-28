# import rclpy
# from rclpy.node import Node
# from turtlesim.msg import Pose

# class ReadPose(Node):
#     def __init__(self):
#         super().__init__('read_pose')

#         self.subscriber_ = self.create_subscription(
#             Pose,
#             '/turtle1/pose',
#             self.read_pose,
#             10
#         )

#     def read_pose(self,msg):
#         self.x = msg.x
#         self.y = msg.y
#         self.get_logger().info(f"收到 x={self.x} y={self.y}")

# def main():
#     rclpy.init()
#     node = ReadPose()
#     rclpy.spin(node)
#     node.destroy_node()
#     rclpy.shutdown()

# if __name__ == '__main__':
#     main

import rclpy
from rclpy.node import Node
from turtlesim.msg import Pose

class PoseReader(Node):
    def __init__(self):
        super().__init__('read_pose')

        self.subscriber_ = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.operation,
            10
        )

    def operation(self,msg):
        self.posx = msg.x
        self.posy = msg.y
        self.get_logger().info(f"收到 x={self.posx} y={self.posy}")

def main():
    rclpy.init(args=args)
    node = PoseReader()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass                    # 用户按 Ctrl+C，正常退出
    finally:                    # ★ 不管怎么退出，都会执行
        node.destroy_node()
        rclpy.shutdown()
if __name__ == '__main__':
    main()