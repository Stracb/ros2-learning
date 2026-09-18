import rclpy
from rclpy.node import Node
from std_srvs.srv import Trigger

class Greeter(Node):
    def __init__(self):
        super().__init__('greeter')

        self.srv = self.create_service(
            Trigger,
            'say_hello',
            self.operation,
        )

        self.get_logger().info('greeter 已启动，等待调用...')

    def operation(self, request, response):
        self.get_logger().info('被调用了')
        response.success = True
        response.message = '但愿我会让你感到骄傲'
        return response

def main():
    rclpy.init()
    node = Greeter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()