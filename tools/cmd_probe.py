import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from nav_msgs.msg import Odometry

rclpy.init()
n = Node('cmd_probe')
st = {'cmd': (0.0, 0.0), 'odom': (0.0, 0.0)}

def on_cmd(m):
    st['cmd'] = (m.twist.linear.x, m.twist.angular.z)

def on_odom(m):
    st['odom'] = (m.pose.pose.position.x, m.pose.pose.position.y)

n.create_subscription(TwistStamped, '/diff_drive_controller/cmd_vel', on_cmd, 10)
n.create_subscription(Odometry, '/diff_drive_controller/odom', on_odom, 10)

import time
t0 = time.time()
last = st['odom']
while time.time() - t0 < 20.0:
    rclpy.spin_once(n, timeout_sec=0.5)
    x, y = st['odom']
    dx = ((x - last[0]) ** 2 + (y - last[1]) ** 2) ** 0.5
    print(f'cmd: lin={st["cmd"][0]:+.3f} ang={st["cmd"][1]:+.3f} | '
          f'odom=({x:+.2f},{y:+.2f}) 本周期动了 {dx*100:5.1f} cm')
    last = (x, y)
