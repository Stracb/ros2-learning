import sys, math, rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid

PX = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0
PY = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
RAD = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0

rclpy.init()
node = Node('map_near')

# ★ 关键：用 transient_local，才能拿到"订阅之前发过"的那一帧
qos = QoSProfile(depth=1,
                 durability=DurabilityPolicy.TRANSIENT_LOCAL,
                 reliability=ReliabilityPolicy.RELIABLE)

box = []
node.create_subscription(OccupancyGrid, '/map', lambda m: box.append(m), qos)

import time
t0 = time.time()
while not box and time.time() - t0 < 10:
    rclpy.spin_once(node, timeout_sec=0.5)
if not box:
    print("10 秒内没收到 /map —— map_server 没在跑？")
    raise SystemExit(1)

m = box[0]
w, res = m.info.width, m.info.resolution
ox, oy = m.info.origin.position.x, m.info.origin.position.y

hits = []
for i, v in enumerate(m.data):
    if v > 65:
        cx, cy = i % w, i // w
        x = ox + (cx + 0.5) * res
        y = oy + (cy + 0.5) * res
        d = math.hypot(x - PX, y - PY)
        if d <= RAD:
            hits.append((d, x, y))

hits.sort()
print(f"距 ({PX:.2f}, {PY:.2f}) 半径 {RAD:.2f} m 内的障碍格：{len(hits)} 个")
for d, x, y in hits[:20]:
    print(f"  距 {d:.2f} m   ({x:+.2f}, {y:+.2f})")
