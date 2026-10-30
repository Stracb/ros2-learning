import math, rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy, ReliabilityPolicy
from nav_msgs.msg import OccupancyGrid, Path

qos = QoSProfile(depth=1, durability=DurabilityPolicy.TRANSIENT_LOCAL,
                 reliability=ReliabilityPolicy.RELIABLE)

rclpy.init()
n = Node('plan_stats')
maps, plans = [], []
n.create_subscription(OccupancyGrid, '/map', lambda m: maps.append(m), qos)
n.create_subscription(Path, '/plan', lambda p: plans.append(p), 1)

print('等 /map 和 /plan ...（去另一个终端发目标点）')
while not (maps and plans):
    rclpy.spin_once(n, timeout_sec=0.5)

m = maps[-1]; p = plans[-1]
w, h, res = m.info.width, m.info.height, m.info.resolution
ox, oy = m.info.origin.position.x, m.info.origin.position.y
occ = [(i % w, i // w) for i, v in enumerate(m.data) if v > 65]

def nearest(x, y):
    return min(math.hypot(x - (ox + (cx + .5) * res), y - (oy + (cy + .5) * res))
               for cx, cy in occ)

ds = [nearest(ps.pose.position.x, ps.pose.position.y) for ps in p.poses]
print(f'路径点数: {len(ds)}')
print(f'离最近障碍: 最小 {min(ds):.2f} m | 平均 {sum(ds)/len(ds):.2f} m | 最大 {max(ds):.2f} m')
print('  (robot_radius=0.36, inflation_radius=0.7, cost_scaling=3.0)')
