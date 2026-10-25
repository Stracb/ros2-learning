import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid
from collections import Counter

rclpy.init()
node = Node('map_stats')
box = []
node.create_subscription(OccupancyGrid, '/map', lambda m: box.append(m), 1)
while not box:
    rclpy.spin_once(node, timeout_sec=1.0)

m = box[0]
w, h, res = m.info.width, m.info.height, m.info.resolution
ox, oy = m.info.origin.position.x, m.info.origin.position.y

xs, ys, n_occ = [], [], 0
for i, v in enumerate(m.data):
    if v > 65:
        n_occ += 1
        cx, cy = i % w, i // w
        xs.append(ox + (cx + 0.5) * res)
        ys.append(oy + (cy + 0.5) * res)

print(f"地图 {w} x {h} 格 ({w*res:.2f} x {h*res:.2f} m), 原点 ({ox:.3f}, {oy:.3f})")
print(f"障碍格子: {n_occ}")
if n_occ:
    print(f"障碍 x 范围 {min(xs):.2f} .. {max(xs):.2f}   跨度 {max(xs)-min(xs):.2f} m")
    print(f"障碍 y 范围 {min(ys):.2f} .. {max(ys):.2f}   跨度 {max(ys)-min(ys):.2f} m")
    hx = Counter(round(x * 2) / 2 for x in xs)
    print("沿 x 的分布（两堵墙应该在这里长出两个尖峰）:")
    for k in sorted(hx):
        print(f"  x={k:6.1f} : {'#' * min(hx[k], 50)} {hx[k]}")
