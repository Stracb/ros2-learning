import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan

rclpy.init()
n = Node('scan_min')
box = []
n.create_subscription(LaserScan, '/scan', lambda m: box.append(m), 1)
while not box:
    rclpy.spin_once(n, timeout_sec=1.0)

m = box[0]
print('frame:', m.header.frame_id)
print(f'range_min={m.range_min:.3f}  range_max={m.range_max:.3f}  points={len(m.ranges)}')
rs = [(r, m.angle_min + i * m.angle_increment)
      for i, r in enumerate(m.ranges) if m.range_min <= r <= m.range_max]
rs.sort()
print('最小 10 个：')
for r, a in rs[:10]:
    print(f'  {r:7.3f} m   @ {a*57.2958:7.1f}°')
