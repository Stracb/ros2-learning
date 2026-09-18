# #!/usr/bin/env python3
# """让 turtlesim 里的乌龟绕圈走。

# 这个节点做的事，等同于之前手敲的命令：
#     ros2 topic pub -r 10 /turtle1/cmd_vel geometry_msgs/msg/Twist \
#         "{linear: {x: 2.0}, angular: {z: 1.0}}"

# 区别是：现在由程序自动、精确、持续地完成。
# """

# # ===== 导入需要的库 =====
# import rclpy                              # ROS 2 的 Python 库
# from rclpy.node import Node               # Node 类（所有节点的"母版"）
# from geometry_msgs.msg import Twist       # Twist 消息类型


# # ===== 定义我们的节点类 =====
# class TurtleCircler(Node):
#     """一个让乌龟转圈的节点。

#     括号里的 Node 表示"继承"——
#     所有 ROS 2 Python 节点都必须继承它，
#     这样才能获得 create_publisher、create_timer 这些能力。
#     """

#     def __init__(self):
#         """构造函数：创建这个节点对象时，自动执行一次。"""

#         # 调用父类 Node 的构造函数，给节点起名为 turtle_circler
#         super().__init__('turtle_circler')

#         # 创建发布者：往 /turtle1/cmd_vel 发送 Twist 类型的数据
#         # 三个参数分别是：消息类型、话题名、队列长度
#         self.publisher_ = self.create_publisher(
#             Twist,                # 发什么类型的数据
#             '/turtle1/cmd_vel',   # 发到哪个话题
#             10                    # 队列长度（早期照抄即可）
#         )

#         # 创建定时器：每隔 0.1 秒调用一次 self.send_command
#         self.timer = self.create_timer(0.1, self.send_command)

#         # 在终端打印一条日志，方便确认节点启动了
#         self.get_logger().info('乌龟转圈节点已启动！')

#     def send_command(self):
#         """发送速度指令。定时器每 0.1 秒调用一次这个函数。"""

#         msg = Twist()           # 创建一个空的 Twist 消息
#         msg.linear.x = 2.0      # 设置前进速度
#         msg.angular.z = 1.0     # 设置转向速度

#         self.publisher_.publish(msg)   # 把消息发出去


# # ===== 程序入口 =====
# def main(args=None):
#     rclpy.init(args=args)        # ① 初始化 ROS 2

#     node = TurtleCircler()       # ② 创建节点对象

#     try:
#         rclpy.spin(node)         # ③ 让节点持续运行（处理定时器等）
#     except KeyboardInterrupt:
#         pass                     # 用户按了 Ctrl+C，正常退出
#     finally:
#         node.destroy_node()      # ④ 销毁节点
#         rclpy.shutdown()         # ⑤ 关闭 ROS 2


# if __name__ == '__main__':
#     main()

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

class TurtleCircler(Node):                    #← 类名 + 父类
    def __init__(self):                # ← 配置块的名字
        super().__init__('turtle_circler')            #  ← 调用父类 + 节点名

        self.publisher_ = self.create_publisher(
            Twist,                         #   ← 消息类型（类名）
            '/turtle1/cmd_vel',                         # ← 话题名（带引号）
            10                                # ← 队列长度
        )
                         
        self.timer = self.create_timer(0.1, self.send_command)          #← 间隔秒数  # ← 回调函数名（不加括号！）

    def send_command(self):                # ← 干活块的名字
        msg = Twist()                     #    ← 造一条空消息
        msg.linear.x = 6.0                 #  ← 前进速度
        msg.angular.z = 1.0                  #← 转向速度
        self.publisher_.publish(msg)             # ← 发出去

def main():                           # ← 启动块的名字
    rclpy.init()                       #       ← 开机
    node = TurtleCircler()              #               ← 造对象
    rclpy.spin(node)                     #     ← 让它转
    node.destroy.node()                    #           ← 注销节点
    rclpy.shutdown()                       #       ← 断开 ROS 2

if __name__ == '__main__':
    main()