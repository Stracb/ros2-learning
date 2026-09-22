import rclpy
from rclpy.node import Node
import math

from my_interfaces.srv import DrawPolygon
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

class PolygonDrawer(Node):
    def __init__(self):
        super().__init__('draw_polygon')

        self.declare_parameter('forward_speed', 2.0)
        self.declare_parameter('turn_speed',0.3)

        self.forward_speed = self.get_parameter('forward_speed').value
        self.turn_speed = self.get_parameter('turn_speed').value

        self.reset_state()
        self.state = 'idle'

        self.publisher_ = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )
        self.subscriber_ = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.handle_subs,
            10
        )
        self.service_ = self.create_service(
            DrawPolygon,
            'draw_polygon',
            self.handle_srv
        )

        self.get_logger().info('初始化成功')

    def handle_srv(self,request,response):
        self.sides_ = request.sides
        self.length_ = request.side_length
        self.get_logger().info(f"收到 边数={self.sides_} 边长={self.length_}")
        response.success = True
        self.reset_state()
        self.state = 'forward'      # ← 一定放最后  
        return response

    def handle_subs(self,msg):
        if self.start_x is None:
            self.start_x = msg.x
            self.start_y = msg.y
            self.get_logger().info(f'起点: ({msg.x:.2f}, {msg.y:.2f})')

        dist = math.hypot(msg.x-self.start_x, msg.y-self.start_y)

        cmd = Twist()

        if self.state == 'forward':
            if dist < self.length_:
                cmd.linear.x = self.forward_speed
            else:
                self.get_logger().info('走够了，停！')
                self.start_theta = msg.theta
                self.state = 'turn'

        elif self.state == 'turn':
            dtheta = abs(math.atan2(math.sin(msg.theta - self.start_theta),
                        math.cos(msg.theta - self.start_theta)))
            self.get_logger().info(f'start_theta={self.start_theta:.3f}  now={msg.theta:.3f}  dtheta={dtheta:.3f}')
            if dtheta < 2*math.pi/self.sides_:
                cmd.angular.z = self.turn_speed
            else:
                self.get_logger().info('转够了，停！')
                self.cnt += 1
                if self.cnt >= self.sides_:
                    self.state = 'done'
                else:
                    self.state = 'forward'
                    self.start_x = msg.x
                    self.start_y = msg.y
        else:
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0

        self.publisher_.publish(cmd)

    def reset_state(self):
        """把状态机退回初始状态（__init__ 和 服务回调 都调它）"""
        self.cnt = 0
        self.start_x = None
        self.start_y = None
        self.start_theta = None

def main():
    rclpy.init()
    node = PolygonDrawer()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()