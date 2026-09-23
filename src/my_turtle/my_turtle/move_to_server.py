import math
import time

import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from my_interfaces.action import MoveTo


class MoveToServer(Node):
    def __init__(self):
        super().__init__('move_to_server')

        self.cb_group = ReentrantCallbackGroup()
        self.latest_pose = None

        self.publisher_ = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel', 
            10
        )

        self.subscription = self.create_subscription(
            Pose, 
            '/turtle1/pose', 
            self.pose_callback, 
            10,
            callback_group=self.cb_group
        )

        self._action_server = ActionServer(
            self, 
            MoveTo, 
            'move_to', 
            self.execute_callback,
            callback_group=self.cb_group
        )

        self.get_logger().info('move_to_server 已启动')

    def pose_callback(self, msg):
        self.latest_pose = msg

    def execute_callback(self, goal_handle):
        target_x = goal_handle.request.target_x
        target_y = goal_handle.request.target_y
        self.get_logger().info(
            f'收到目标: ({goal_handle.request.target_x:.2f}, '
            f'{goal_handle.request.target_y:.2f})')
        pose = self.latest_pose
        dist = math.hypot(target_x - pose.x, target_y - pose.y)

        count = 0          # ← 计数器（局部变量，不用 self）

                # ══ 【新加】循环 ══
        while True:
            pose = self.latest_pose
            dist = math.hypot(target_x - pose.x, target_y - pose.y)
            self.get_logger().info(f'还差 {dist:.2f}')

            if dist < 0.3:                 # 够近了
                self.get_logger().info('到了！')
                break                      # ← 跳出循环

                        # ══ 【新加】算方向 + 发速度 ══
            angle_to_target = math.atan2(target_y - pose.y, target_x - pose.x)
            angle_error = math.atan2(math.sin(angle_to_target - pose.theta),
                                     math.cos(angle_to_target - pose.theta))

            cmd = Twist()
            cmd.angular.z = 2.0 * angle_error          # 转
            if abs(angle_error) < 0.2:                  # 大致朝准了才走
                cmd.linear.x = min(1.5, dist)           # 越近越慢
            self.publisher_.publish(cmd)

                        # ══ 【新加】发反馈 ══
            count += 1
            if count % 10 == 0:                    # 每 10 轮发一次
                feedback_msg = MoveTo.Feedback()
                feedback_msg.distance_remaining = dist
                goal_handle.publish_feedback(feedback_msg)

            time.sleep(0.05)                # 每 0.5 秒看一次
            

        goal_handle.succeed()
        result = MoveTo.Result()
        result.success = True
        result.final_distance = dist
        return result


def main(args=None):
    rclpy.init(args=args)
    node = MoveToServer()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()