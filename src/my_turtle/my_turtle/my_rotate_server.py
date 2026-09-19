import time                          # 用来模拟"干活耗时"
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from turtlesim.action import RotateAbsolute      # 复用现成的动作类型


class MyRotateServer(Node):
    def __init__(self):
        super().__init__('my_rotate_server')

        # 注意：第一个参数是 self，回调叫 execute_callback
        self._action_server = ActionServer(
            self,
            RotateAbsolute,
            'my_rotate',                 # 服务名（换个名字，避免和 turtlesim 冲突）
            self.execute_callback
        )
        self.get_logger().info('动作服务端已启动，等待目标...')

    def execute_callback(self, goal_handle):
        """收到目标时执行 —— 注意参数只有一个 goal_handle"""

        # 1. 读目标
        target = goal_handle.request.theta
        self.get_logger().info(f'收到目标: 转到 {target:.2f} 弧度')

        feedback_msg = RotateAbsolute.Feedback()
        total_steps = 20                 # 把任务分成 20 步（纯模拟）

        for i in range(1, total_steps + 1):

            # 2. 每一步先检查：有没有人要求取消？
            if goal_handle.is_cancel_requested:
                goal_handle.canceled()   # 标记为"已取消"
                self.get_logger().info('目标被取消')
                return RotateAbsolute.Result()    # 取消也要返回一个结果对象

            # 3. 发反馈（这就是"实时进度"）
            feedback_msg.remaining = target * (1 - i / total_steps)
            goal_handle.publish_feedback(feedback_msg)

            time.sleep(0.2)              # 模拟干活耗时

        # 4. 标记成功 + 返回结果
        goal_handle.succeed()
        result = RotateAbsolute.Result()
        result.delta = target
        self.get_logger().info('任务完成')
        return result


def main():
    rclpy.init()
    node = MyRotateServer()
    rclpy.spin(node)                     # 需要 spin（等目标）
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()