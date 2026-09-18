import rclpy
from rclpy.node import Node
from std_srvs.srv import SetBool

class Moveclient(Node):
    def __init__(self):
        super().__init__('move_client')

        self.client_ = self.create_client(
            SetBool,
            'movemove'
        )

    def send_request(self, value):
        while not self.client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('等待服务')

        request = SetBool.Request()
        request.data = value

        future = self.client_.call_async(request)

        rclpy.spin_until_future_complete(self, future)

        response = future.result()

        self.get_logger().info(f'返回: success={response.success}, message={response.message}')

def main():
    rclpy.init()
    node = Moveclient()
    node.send_request(True)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()