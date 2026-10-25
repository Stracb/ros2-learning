import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid

rclpy.init()
node = Node('map_ascii2')
box = []
node.create_subscription(OccupancyGrid, '/map', lambda m: box.append(m), 1)
while not box:
    rclpy.spin_once(node, timeout_sec=1.0)

m = box[0]
w, h, res = m.info.width, m.info.height, m.info.resolution
ox, oy = m.info.origin.position.x, m.info.origin.position.y
d = m.data
COLS, ROWS = 76, 30
print(f"地图 {w}x{h} = {w*res:.2f} x {h*res:.2f} m, origin ({ox:.2f},{oy:.2f})")
print("块内取最大值：有障碍就 #（细线不会被漏掉）")
for ry in range(ROWS - 1, -1, -1):
    y0 = int(ry * h / ROWS); y1 = max(y0 + 1, int((ry + 1) * h / ROWS))
    line = ''
    for rx in range(COLS):
        x0 = int(rx * w / COLS); x1 = max(x0 + 1, int((rx + 1) * w / COLS))
        occ = free = False
        for cy in range(y0, y1):
            base = cy * w
            for cx in range(x0, x1):
                v = d[base + cx]
                if v > 65: occ = True
                elif v == 0: free = True
        line += '#' if occ else ('.' if free else ' ')
    print(f"{oy + (y0 + 0.5) * res:6.1f} |{line}|")
