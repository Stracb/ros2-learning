import sys, re

path = sys.argv[1] if len(sys.argv) > 1 else '/home/pummy/ros2_ws/my_map_final.pgm'
CX   = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
CY   = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0
RAD  = float(sys.argv[4]) if len(sys.argv) > 4 else 0.5

OX, OY, RES = -11.846, -15.389, 0.05

data = open(path, 'rb').read()
m = re.match(rb'P5\s+(\d+)\s+(\d+)\s+(\d+)\s', data)
if not m:
    print('不是 P5 格式的 pgm'); sys.exit(1)
w, h, maxv = int(m.group(1)), int(m.group(2)), int(m.group(3))
px = bytearray(data[m.end():])

n = 0
for row in range(h):
    y = OY + (h - 1 - row + 0.5) * RES
    if abs(y - CY) > RAD:
        continue
    for col in range(w):
        x = OX + (col + 0.5) * RES
        if (x - CX) ** 2 + (y - CY) ** 2 <= RAD ** 2:
            if px[row * w + col] < 65:      # 黑的（障碍）→ 擦成白（空闲）
                px[row * w + col] = 254
                n += 1

open(path, 'wb').write(data[:m.end()] + bytes(px))
print(f'擦掉 {n} 个格子（以 ({CX},{CY}) 为心、半径 {RAD} m）')
