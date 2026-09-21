# import rclpy
# from turtlesim.msg import Pose
# from my_interfaces.msg import TurtleStatus

# class Stat(Node):


#!/usr/bin/env python3
"""把 turtlesim 的 Pose 翻译成自定义的 TurtleStatus。

用法：
    ros2 run my_turtle status_bridge
"""

# ══════ ① import ══════
import rclpy
from rclpy.node import Node

from turtlesim.msg import Pose                 # 收的：turtlesim 的位置消息
from my_interfaces.msg import TurtleStatus     # 发的：你自己造的消息


# ══════ ② 类 ══════
class StatusBridge(Node):                      # ← 类名（驼峰，首字母大写）
    def __init__(self):
        super().__init__('status_bridge')      # ← 节点名（小写下划线）

        # ---- 发布者：把 TurtleStatus 发到 /turtle_status ----
        self.publisher_ = self.create_publisher(
            TurtleStatus,          # ① 消息类型（你造的类，不加引号）
            '/turtle_status',      # ② 话题名（字符串，你自己起）
            10                     # ③ 队列长度
        )

        # ---- 订阅者：收 /turtle1/pose ----
        self.subscription = self.create_subscription(
            Pose,                  # ① 消息类型（turtlesim 的）
            '/turtle1/pose',       # ② 话题名
            self.operation,        # ③ 回调函数名（不加括号！）
            10                     # ④ 队列长度
        )

    # ══════ ③ 回调：消息到达时自动执行 ══════
    def operation(self, msg):                  # ← 回调名（要和上面第③个位置一致）
        cmd = TurtleStatus()
        cmd.x = msg.x
        cmd.y = msg.y
        cmd.theta = msg.theta

        self.publisher_.publish(cmd)
        # 【这一段必须你自己写】三步：
        #   1. 造一条空的 TurtleStatus 消息
        #   2. 把 msg.x / msg.y / msg.theta 填进去
        #   3. 调用 publish 发出去
        #
        # 提示：翻 `05-写节点清单.md` 的【形状 5】


# ══════ ④ main（所有节点都一样）══════
def main():
    rclpy.init()
    node = StatusBridge()          # ← 类名（和上面 class 那个一致）
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()