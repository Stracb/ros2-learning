import subprocess, math, time, sys, re
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped

def gz_pose():
    try:
        out = subprocess.run(['gz','model','-m','my_robot','-p'],
                             capture_output=True, text=True, timeout=5).stdout
        m = re.search(r'XYZ \(m\)\s*\]\s*\[[^\]]*\]\s*:\s*\n?\s*\[([^\]]+)\]', out)
        r = re.findall(r'\[([-\d\.\s]+)\]', out)
        nums = [float(x) for x in r[-2].split()] if len(r) >= 2 else None
        nums2 = [float(x) for x in r[-1].split()] if len(r) >= 2 else None
        return nums, nums2
    except Exception as e:
        return None, None

rclpy.init()
n = Node('loc_check')
box = []
n.create_subscription(PoseWithCovarianceStamped, '/amcl_pose', lambda m: box.append(m), 1)
while not box:
    rclpy.spin_once(n, timeout_sec=0.2)

dur = float(sys.argv[1]) if len(sys.argv) > 1 else 60.0
t0 = time.time()
print(f'{"t":>5} | {"真值 gz (x,y,yaw°)":>24} | {"AMCL (x,y,yaw°)":>24} | 差')
while time.time() - t0 < dur:
    rclpy.spin_once(n, timeout_sec=0.2)
    xyz, rpy = gz_pose()
    if not xyz or not rpy:
        continue
    p = box[-1].pose.pose
    yaw = 2*math.atan2(p.orientation.z, p.orientation.w)
    d = math.hypot(p.position.x - xyz[0], p.position.y - xyz[1])
    dyaw = abs(math.degrees(yaw - rpy[2])) % 360.0
    dyaw = min(dyaw, 360.0 - dyaw)
    print(f'{time.time()-t0:5.1f} | ({xyz[0]:+.2f},{xyz[1]:+.2f},{math.degrees(rpy[2]):+6.1f}) '
          f'| ({p.position.x:+.2f},{p.position.y:+.2f},{math.degrees(yaw):+6.1f}) | {d:5.2f} m / {dyaw:4.1f}°')
    time.sleep(0.8)
