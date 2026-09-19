import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient                    # ← 动作客户端
from turtlesim.action import RotateAbsolute              # ← 动作类型


class RotateClient(Node):
    def __init__(self):
        super().__init__('rotate_client')

        self._action_client = ActionClient(
            self,
            RotateAbsolute,
            '/turtle1/rotate_absolute'                   # ← 动作名
        )

    def send_goal(self, theta):
        """① 发送目标"""
        goal_msg = RotateAbsolute.Goal()                 # 造目标
        goal_msg.theta = theta                           # 填字段（要转到多少弧度）

        self.get_logger().info('等待动作服务器...')
        self._action_client.wait_for_server()            # 等服务端上线

        self.get_logger().info(f'发送目标: theta={theta}')
        self._send_goal_future = self._action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback     # ← 注册反馈回调
        )
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        """② 服务端回应"接受/拒绝"时调用"""
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('目标被拒绝')
            return

        self.get_logger().info('目标被接受，开始执行')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        """④ 任务完成时调用"""
        result = future.result().result
        self.get_logger().info(f'完成！实际转了 delta={result.delta:.2f} 弧度')
        rclpy.shutdown()                                  # 拿到结果就退出

    def feedback_callback(self, feedback_msg):
        """③ 执行过程中持续调用 —— 这就是"实时反馈" """
        feedback = feedback_msg.feedback
        self.get_logger().info(f'反馈: 还差 {feedback.remaining:.2f} 弧度')


def main():
    rclpy.init()
    node = RotateClient()
    node.send_goal(1.5708)                                # 转 90°
    rclpy.spin(node)                                      # ← 这里要 spin！
    node.destroy_node()


if __name__ == '__main__':
    main()