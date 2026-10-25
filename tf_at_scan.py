import time
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.time import Time
from rclpy.duration import Duration
import tf2_ros
from sensor_msgs.msg import LaserScan

rclpy.init()
node = Node('tf_at_scan', parameter_overrides=[Parameter('use_sim_time', value=True)])
buf = tf2_ros.Buffer(cache_time=Duration(seconds=30.0))
tf2_ros.TransformListener(buf, node)

stats = {'ok': 0}
errs = {}

def cb(msg):
    try:
        buf.lookup_transform('odom', 'laser_link', Time.from_msg(msg.header.stamp),
                             timeout=Duration(seconds=0.2))
        stats['ok'] += 1
    except Exception as e:
        name = type(e).__name__
        errs[name] = errs.get(name, 0) + 1

node.create_subscription(LaserScan, '/scan', cb, 10)

end = time.time() + 20
while time.time() < end:
    rclpy.spin_once(node, timeout_sec=0.2)

total = stats['ok'] + sum(errs.values())
print(f"20 秒内共 {total} 帧")
print(f"  查到: {stats['ok']}")
for k, v in errs.items():
    print(f"  查不到 [{k}]: {v}")
