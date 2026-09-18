import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_srvs.srv import SetBool

class ControlTurtle(Node):
    def __init__(self):
        super().__init__('turtle_control')

        self.moving = False

        self.srv_ = self.create_service(
            SetBool,
            'movemove',
            self.operation
        )

        self.publisher_ = self.create_publisher(
            Twist,
            '/turtle1/cmd_vel',
            10
        )

        self.timer_ = self.create_timer(
            0.1, 
            self.send_spd
        )

        self.get_logger().info('turtle_control 已启动')

    def operation(self, request, response):
        self.get_logger().info('被调用了')
        self.moving = request.data
        response.success = True
        response.message = '开始动了'
        return response
    

    def send_spd(self):
        cmd = Twist()
        if self.moving == True:
            cmd.linear.x = 1.0
        else:
            cmd.linear.x = 0.0
        self.publisher_.publish(cmd)

def main():
    rclpy.init()
    node = ControlTurtle()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
