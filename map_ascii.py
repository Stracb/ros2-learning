import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid

rclpy.init()
node = Node('map_ascii')
box = []
node.create_subscription(OccupancyGrid, '/map', lambda m: box.append(m), 1)
while not box:
    rclpy.spin_once(node, timeout_sec=1.0)

m = box[0]
w, h, res = m.info.width, m.info.height, m.info.resolution
ox, oy = m.info.origin.position.x, m.info.origin.position.y
data = m.data

COLS, ROWS = 76, 30
print(f"地图 {w}x{h} 格 = {w*res:.2f} x {h*res:.2f} m")
print(f"x: {ox:.2f} .. {ox + w*res:.2f}    y: {oy:.2f} .. {oy + h*res:.2f}")
print(f"每个字符 = {w*res/COLS:.3f} m 宽 x {h*res/ROWS:.3f} m 高")
print("# 障碍   . 空闲   空格 未知")
for ry in range(ROWS - 1, -1, -1):
    cy = int((ry + 0.5) * h / ROWS)
    line = ''
    for rx in range(COLS):
        cx = int((rx + 0.5) * w / COLS)
        v = data[cy * w + cx]
        line += '#' if v > 65 else ('.' if v == 0 else ' ')
    print(f"{oy + (cy + 0.5) * res:6.1f} |{line}|")
