import time
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.time import Time
from rclpy.duration import Duration
import tf2_ros
from sensor_msgs.msg import LaserScan

rclpy.init()
node = Node('tf_at_scan2', parameter_overrides=[Parameter('use_sim_time', value=True)])
buf = tf2_ros.Buffer(cache_time=Duration(seconds=30.0))
tf2_ros.TransformListener(buf, node)

ok, bad, printed = 0, 0, 0
def cb(msg):
    global ok, bad, printed
    st = Time.from_msg(msg.header.stamp)
    try:
        buf.lookup_transform('odom', 'laser_link', st, timeout=Duration(seconds=0.2))
        ok += 1
    except Exception as e:
        bad += 1
        if printed < 3:
            printed += 1
            print(f"--- 第 {printed} 个失败 ---")
            print(f"扫描时间 {st.nanoseconds/1e9:.3f}")
            print(f"错误原文: {e}")
            print()

node.create_subscription(LaserScan, '/scan', cb, 10)

end = time.time() + 15
while time.time() < end:
    rclpy.spin_once(node, timeout_sec=0.2)
print(f"共 {ok+bad} 帧: 查到 {ok}, 查不到 {bad}")
