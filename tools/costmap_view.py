import rclpy
from rclpy.node import Node
from nav_msgs.msg import OccupancyGrid

rclpy.init()
n = Node('costmap_view')
box = []
n.create_subscription(OccupancyGrid, '/local_costmap/costmap', lambda m: box.append(m), 1)
print('等 /local_costmap/costmap ...')
while not box:
    rclpy.spin_once(n, timeout_sec=1.0)

m = box[0]
w, h = m.info.width, m.info.height
ox, oy = m.info.origin.position.x, m.info.origin.position.y
print(f'窗口 {w}x{h}, 原点 ({ox:.2f},{oy:.2f}), 分辨率 {m.info.resolution}')
print('图例: # 致命(>=253)  + 很贵(>=150)  - 有代价  . 自由  空格 未知')

COLS = 60
for row in range(h - 1, -1, -1):
    line = ''
    for c in range(COLS):
        col = int(c * w / COLS)
        v = m.data[row * w + col]
        if v >= 253: line += '#'
        elif v >= 150: line += '+'
        elif v > 0: line += '-'
        elif v == 0: line += '.'
        else: line += ' '
    print(line)
