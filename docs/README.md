# ROS 2 学习工作区

> 目标：**机器人仿真 + 求职**
> 环境：Windows 11 宿主机 + VMware Workstation 17.6.3 + Ubuntu 24.04 LTS + ROS 2 Jazzy + Gazebo Harmonic
> 建立日期：2026-09-11

---

## 文档索引

| 文件 | 内容 |
|---|---|
| [01-环境搭建.md](01-环境搭建.md) | 从零搭建虚拟机 → Ubuntu → ROS 2 → Gazebo，含避坑与验证命令 |
| [02-学习路线.md](02-学习路线.md) | 14 周分阶段学习路线，每阶段带**验收标准**，含求职准备 |

---

## 当前状态（重要）

### 已有环境（旧，保留不删）

| 项 | 值 |
|---|---|
| 位置 | `E:\Ubuntu-22.04.5\Ubuntu 64 位.vmx` |
| 系统 | Ubuntu 22.04.5 LTS |
| ROS | **ROS 2 Humble — 已确认安装完好**<br>`/opt/ros/humble/`，`ROS_DISTRO=humble`，已装 314 个 `ros-humble-*` 包（相当于 desktop 完整版）|
| 内存 | **4 GB** ← 无法跑仿真 |
| CPU | 4 vCPU |
| 磁盘 | 60 GB 虚拟硬盘（已用 19.85 GB，占 33%，剩余约 40 GB）✅ 充足 |

**处理方式：先保留，不要删。** 新环境跑通后再删除回收空间（见下方「旧环境清理」）。

### 旧环境实测数据

在旧虚拟机内实测确认：

| 命令 | 输出 | 结论 |
|---|---|---|
| `ls /opt/ros/` | `humble` | ROS 2 Humble 安装完好 |
| `echo $ROS_DISTRO` | `humble` | 环境变量已配置 |
| `dpkg -l \| grep -c ros-humble` | `314` | 相当于 desktop 完整版 |
| `free -h` | total **3.8 GiB**，available 2.6 GiB | ❌ 内存硬伤 |
| `df -h /` | 59G 总 / 17G 已用 / **可用 39G** | ✅ 磁盘充足 |
| Gazebo | `/usr/bin/gazebo` 和 `/usr/bin/gz` **都不存在** | ❌ **仿真环境为零** |
| Nav2 / slam_toolbox | 未安装 | ❌ 导航栈为零 |

已装的关键包：`ros-humble-desktop`、`rviz2`、`turtlesim`、`xacro`、
`robot-state-publisher`、`joint-state-broadcaster`、`ros2-control`。
家目录有自写的 `ros2_talker.py` / `ros2_listener.py`。

> **关键结论**：装了 `ros2_control` 却没有 Gazebo —— 这正是之前跟着
> 「URDF + ros2_control + Gazebo」教程时卡住的地方，没有仿真器就无从验证。
> 换到 Jazzy + Gazebo Harmonic 后这条路才走得通。

---

## 新环境验收记录（2026-09-11 通过）

| 检查项 | 命令 | 实际结果 | 判断 |
|---|---|---|---|
| 系统版本 | `grep VERSION= /etc/os-release` | `24.04.5 LTS (Noble Numbat)` | ✅ |
| 内核 | `uname -r` | `7.0.0-31-generic` | ✅ |
| 内存 | `free -h` | `11Gi` 总量，可用 10Gi | ✅ |
| CPU | `nproc` | `8` | ✅ |
| 磁盘 | `df -h /` | `/dev/nvme0n1p2` **40 GB**，可用 28 G | ⚠️ 实际设成 40 GB（原计划 80 GB），够用 |
| VMware Tools | `dpkg -l \| grep open-vm-tools` | `open-vm-tools` + `open-vm-tools-desktop` 均已安装 | ✅ |
| 网络 | `ping baidu.com` | 0% 丢包，RTT 14 ms | ✅ |
| **3D 加速** | `glxinfo -B` | **`SVGA3D; build: RELEASE; LLVM`**<br>OpenGL **4.3** (需 ≥3.3) | ✅✅ **关键闸门通过** |

**附带确认**：Ubuntu apt 源已是清华 TUNA（`mirrors.tuna.tsinghua.edu.cn/ubuntu noble`），无需再换源。

> **3D 加速通过是一切的基石。** 没有掉进 `llvmpipe` 软件渲染，意味着
> RViz2 和 Gazebo Harmonic 都能硬件加速运行，仿真的性能问题解决了。

### Gazebo Harmonic 验证记录

| 检查项 | 命令 | 结果 | 判断 |
|---|---|---|---|
| 安装 | `which gz` | `/opt/ros/jazzy/opt/gz_tools_vendor/bin/gz` | ✅ |
| 版本 | `gz sim --versions` | **`8.11.0`**（gz-sim 8 = Harmonic）| ✅ 与 Jazzy 官方配对 |
| GUI 启动 | `gz sim shapes.sdf` | 窗口弹出，但**持续频闪** | ⚠️ 见下方修复 |
| 渲染引擎修复 | `--render-engine ogre` | **频闪消失** | ✅ 根因确认 |
| 永久修复 | 改 `~/.gz/sim/8/gui.config` + `server.config` | **不带参数启动也不闪** | ✅ **已永久解决** |
| ROS 2 桥接 | `ros2 launch ros_gz_sim gz_sim.launch.py gz_args:="shapes.sdf"`<br>`ros2 topic list` | ROS 2 侧出现 **`/clock`** | ✅ 桥接正常 |

> **桥接话题很少是正常的**：`shapes.sdf` 是静态示例世界，没有机器人也没有传感器，
> 所以只有 `/clock` 被桥接。加载自己的机器人时才需要显式配置 `/cmd_vel`、`/odom`、
> `/scan`、`/tf` 的桥接（学习路线第 5 阶段）。

### 快照记录

| 快照名 | 时间点 | 内容 | 状态 |
|---|---|---|---|
| `01-系统就绪` | 2026-09-11 | Ubuntu 24.04.5 + open-vm-tools + 3D 加速已验证 | 🗑️ 已删除 |
| `02-ROS2就绪` | 2026-09-11 | ROS 2 Jazzy desktop 安装完成，talker/listener 通信验证通过 | 🗑️ 已删除 |
| **`03-仿真就绪`** | 2026-09-11 | ROS 2 Jazzy + Gazebo Harmonic(ogre引擎) + colcon + rqt 全部验证通过 | ✅ **唯一保留的回滚点** |

> ⚠️ **重要习惯**：拍摄快照时**务必取消勾选「拍摄虚拟机内存」**。
> 本机内存 12 GB，勾选后**每个快照占 12 GB**；不勾选只要几百 MB，
> 代价仅是恢复后需要重新开机（20 秒）。3 个快照曾因此占用 37 GB。

### 清理记录（2026-09-11）

| 项目 | 回收 | 说明 |
|---|---|---|
| 快照 `01`、`02` | ~24 GB | 内容已被 `03` 完全覆盖 |
| ISO 安装镜像 | 5.88 GB | 系统装好后不再需要 |
| 旧虚拟机 `E:\Ubuntu-22.04.5\` | 20 GB | 已备份个人文件后删除 |
| **虚拟机文件夹** | **66.86 GB → 23.31 GB** | |

**遗留**：`E:\` 回收站内还有约 10 GB 未清空；`E:\VMware\Ubuntu-24.04.5\` 空文件夹待删（需管理员权限）。


### 镜像源配置（已完成）

| 源 | 配置 |
|---|---|
| Ubuntu | 清华 TUNA（`mirrors.tuna.tsinghua.edu.cn/ubuntu`），`noble-security` 也已从 `security.ubuntu.com` 改为 TUNA |
| ROS 2 | **中科大 USTC**（`mirrors.ustc.edu.cn/ros2/ubuntu`），`Types: deb`（已移除 `deb-src`，因 TUNA/USTC 不镜像源码包）|

实测镜像速度（ROS 2 源）：

| 镜像 | 速度 |
|---|---|
| **USTC 中科大** | **4.3 MB/s** ✅ 选用 |
| NJU 南大 | 2.4 MB/s |
| TUNA 清华 | 2.0 MB/s |
| Aliyun 阿里 | 198 KB/s |
| BFSU / SJTU | 重定向，不可用 |

> **重要教训**：最初 `apt update` 只有 12.8 kB/s，原因**不是镜像慢**，而是
> `security.ubuntu.com`（美国服务器）反复超时重试，把平均速度拖垮了。
> 把安全源也换成国内镜像后，速度直接变成 **4,643 kB/s**。

### ROS 2 安装方式（2025 年后已变更）

官方安装方式已改为 `ros2-apt-source` 配置包（当前版本 **1.3.0**），
**网上大量教程还在用 `apt-key add` 的老办法，那个已经失效**。

```bash
sudo apt update && sudo apt install -y curl
export ROS_APT_SOURCE_VERSION=$(curl -s https://api.github.com/repos/ros-infrastructure/ros-apt-source/releases/latest | grep -F "tag_name" | awk -F'"' '{print $4}')
curl -L -o /tmp/ros2-apt-source.deb "https://github.com/ros-infrastructure/ros-apt-source/releases/download/${ROS_APT_SOURCE_VERSION}/ros2-apt-source_${ROS_APT_SOURCE_VERSION}.$(. /etc/os-release && echo ${UBUNTU_CODENAME:-${VERSION_CODENAME}})_all.deb"
sudo dpkg -i /tmp/ros2-apt-source.deb
sudo apt install -y ros-jazzy-desktop
```

> **踩坑记录**：`/etc/apt/sources.list.d/ros2.sources` 是**符号链接**（指向 `/usr/share/ros-apt-source/ros2.sources`）。
> `grep -r` 默认**不跟随符号链接**，所以用 `grep -r` 找它永远找不到，要用 `grep -R` 或直接 `cat`。
> 用 `sed -i` 修改时会自动把符号链接替换成普通文件（GNU sed 行为），这正是想要的效果。

---

## ⚠️ 关键坑：Gazebo 在 VMware 里必须用 ogre 渲染引擎

### 症状

`gz sim shapes.sdf` 能启动、**不报错**，但 3D 视图**持续频闪**。

### 原因

Gazebo Harmonic 默认使用 **Ogre2** 渲染引擎。在 VMware 的 **SVGA3D** 虚拟显卡上，
Ogre2 存在兼容性问题。这是被记录在案的经典坑：

- [gz-sim Issue #1492](https://github.com/gazebosim/gz-sim/issues/1492)：虚拟机中 `ogre2` = 黑屏，`ogre` = 画面 1Hz 闪烁
- [Robotics StackExchange #117720](https://robotics.stackexchange.com/questions/117720/how-to-permanently-set-gazebo-default-render-engine-to-ogre)：完全相同场景（24.04 + Jazzy + gz-sim 8.x）
- [Gazebo 官方 Troubleshooting](https://gazebosim.org/docs/latest/troubleshooting/) 给出的对策命令：
  `gz sim -v 3 shapes.sdf --render-engine ogre`

> 注意：**这与 3D 加速是否开启无关**。`glxinfo` 显示 `SVGA3D`（硬件加速正常）也会出现此问题。

### 解决方法

**临时**（单次生效，用于验证）：

```bash
gz sim --render-engine ogre shapes.sdf
```

**永久**（改配置文件，对 `ros2 launch` 启动也生效）：

必须改**两个**文件 —— `gui.config` 管窗口显示，`server.config` 管
**服务端渲染**（相机/深度相机等传感器仿真走这条路径，第 7 阶段会用到）：

```bash
GUI_SRC=$(find /usr /opt -name "gui.config" 2>/dev/null | head -1)
SRV_SRC=$(find /usr /opt -name "server.config" 2>/dev/null | head -1)

mkdir -p ~/.gz/sim/8

[ -n "$GUI_SRC" ] && cp "$GUI_SRC" ~/.gz/sim/8/gui.config && \
  sed -i 's|<engine>ogre2</engine>|<engine>ogre</engine>|g' ~/.gz/sim/8/gui.config
[ -n "$SRV_SRC" ] && cp "$SRV_SRC" ~/.gz/sim/8/server.config && \
  sed -i 's|<engine>ogre2</engine>|<engine>ogre</engine>|g' ~/.gz/sim/8/server.config

grep -n "engine" ~/.gz/sim/8/gui.config ~/.gz/sim/8/server.config
```

**验证**：不带任何参数运行 `gz sim shapes.sdf`，画面应该稳定不闪。

> 原理：Gazebo 优先读取 `~/.gz/sim/8/` 下的用户配置，覆盖 `/usr/share/gz/` 里的默认值。
> 修改的是 `MinimalScene` 插件里的 `<engine>` 标签。

### 经验教训

**在虚拟机里遇到 Gazebo/RViz 渲染异常，第一反应应该是"换渲染引擎"，而不是怀疑 3D 加速没开。**
先试 `--render-engine ogre`，能用再去改配置文件永久化。

---

## 旧环境清理（等新环境验收通过后再做）

### 核心原则：不需要单独卸载 ROS 2

ROS 2 Humble 整个装在 `.vmdk` 内部，而 `.vmdk` 就是虚拟机的整块硬盘。
**删除虚拟机 = 删除这块硬盘 = Ubuntu + ROS 2 Humble + 全部文件一次性消失。**
不需要、也不应该在删虚拟机之前单独去卸载 ROS 2。

### 删除顺序（顺序搞反会两头空）

1. **备份**个人文件（`~/ros2_talker.py`、`~/ros2_listener.py`、笔记等）
2. 新建虚拟机，把 Ubuntu 24.04 + ROS 2 Jazzy + Gazebo Harmonic **验收全部通过**
3. 确认新环境可用后，**再**删除旧虚拟机

### 可回收空间（实测）

| 文件 | 大小 |
|---|---|
| `Ubuntu 64 位.vmdk` | 19.85 GB |
| `ubuntu-22.04.5-desktop-amd64.iso` | 4.44 GB |
| `<uuid>.vmem` | 4.00 GB |
| 其余 | ~0.15 GB |
| **合计** | **28.44 GB** |

### 删除方法

**方式 1（推荐）**：VMware 左侧库右键虚拟机 → **管理** → **从磁盘中删除**

**方式 2**：关闭虚拟机并**完全退出 VMware**（含托盘图标）→ 删除 `E:\Ubuntu-22.04.5\` 整个文件夹

> ⚠️ **两个坑**：
> 1. 关机时**不要用「挂起 (Suspend)」** —— 挂起状态会保留 `.vmem`，删不干净。
>    判断方法：文件夹里若有 `*.lck` 锁文件和 `*.vmem`，说明虚拟机正在运行或挂起中，无法删除。
> 2. 28 GB 的文件**通常不进回收站**，是直接永久删除，操作前务必确认。

### 如果确实要保留 Ubuntu 22.04 只卸载 ROS 2

（一般不需要，仅备查）

```bash
sudo apt purge -y "ros-humble-*"
sudo apt autoremove --purge -y
sudo rm -rf /opt/ros/humble
sed -i '/source \/opt\/ros\/humble\/setup.bash/d' ~/.bashrc
sudo rm -f /etc/apt/sources.list.d/ros2.list /etc/apt/sources.list.d/ros2.sources
sudo apt update
```

### 为什么要建新环境

| 问题 | 说明 |
|---|---|
| 内存只有 4 GB | 宿主机有 31.8 GB，却只分了 4 GB。Gazebo + RViz + Nav2 起步需要 6–8 GB，4 GB 会 OOM 卡死。**这是硬伤，必须改。** |
| Gazebo Classic 已 EOL | Humble 默认搭配 Gazebo Classic 11，该版本已于 **2025 年 1 月停止维护**。Jazzy 搭配的 Gazebo Harmonic 才是当前标准。 |
| Humble 临近 EOL | Humble 于 **2027 年 5 月** 结束支持，只剩 8 个月。 |
| 沉没成本为零 | 尚未开始学习，环境里没有任何自有代码。此刻切换成本约半天，写几个项目后再切换成本约两周。 |

### 目标环境（新）

| 项 | 值 |
|---|---|
| 位置 | `E:\Ubuntu-24.04-ROS2\` |
| 系统 | Ubuntu 24.04 LTS (Noble) |
| ROS | **ROS 2 Jazzy Jalisco**（LTS 至 2029 年） |
| 仿真 | Gazebo Harmonic |
| 内存 | 12 GB |
| CPU | 8 vCPU |
| 磁盘 | 80 GB |

> **为什么不用 Lyrical Luth（2026/5 发布的最新 LTS）？**
> 它才发布 4 个月，第三方包与教程跟进不足；企业迁移周期通常 12–24 个月。
> 求职场景下，Jazzy 是当下企业实际在用的版本，是更稳妥的选择。

---

## 快速开始

```bash
# 1. 确认 ROS 2 环境已加载
source /opt/ros/jazzy/setup.bash   # 已写入 ~/.bashrc，新终端自动生效
ros2 doctor

# 2. 键盘控制小乌龟（验证基础通信）
ros2 run turtlesim turtlesim_node      # 终端 1
ros2 run turtlesim turtle_teleop_key   # 终端 2

# 3. 启动 Gazebo Harmonic（验证仿真环境）
gz sim shapes.sdf

# 4. ROS 2 与 Gazebo 桥接
ros2 launch ros_gz_sim gz_sim.launch.py gz_args:="shapes.sdf"
```

---

## 工作区约定

- **代码工作空间放虚拟机内部**：`~/ros2_ws`
  不要放在 `/mnt/hgfs/...`（共享文件夹）或 `/mnt/e/...`，跨文件系统的 I/O 会让 `colcon build` 慢到无法忍受。
- **本目录 `E:\ROS2` 用于**：笔记、文档、下载的资料、备份。
- 在虚拟机内访问本目录的路径为 `/mnt/hgfs/ROS2`（需在 VMware 中开启共享文件夹）。

---

## 学习进度追踪

在 [02-学习路线.md](02-学习路线.md) 中，每完成一个阶段就勾选对应的验收标准。**验收标准全部通过才进入下一阶段**，不要跳阶段。
