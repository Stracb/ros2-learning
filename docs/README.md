# ROS 2 学习工作区

> 目标：**机器人仿真 + 求职**，最终产出「完整项目 + GitHub 仓库 + 演示视频」。
> 环境：Windows 11 宿主机 + VMware Workstation 17.6.3 + Ubuntu 24.04.5 + ROS 2 Jazzy + Gazebo Harmonic。
> 当前进度：第 11 天（2026-09-21）。本文件是仓库首页，内容与现状一致。

---

## 文档索引

| 文件 | 内容 |
|---|---|
| [00-接续说明.md](00-接续说明.md) | 换新对话时先读这个 —— 用户背景、环境状态、教学方式 |
| [01-环境搭建.md](01-环境搭建.md) | 从零搭建虚拟机 → Ubuntu → ROS 2 → Gazebo，含避坑与验证命令（已完成，留作参考）|
| [02-学习路线.md](02-学习路线.md) | 14 周分阶段学习路线，每阶段带验收标准，含求职准备 |
| [03-Linux命令速查.md](03-Linux命令速查.md) | 常用 Linux 命令逐段拆解 |
| [04-学习进度存档.md](04-学习进度存档.md) | **主进度档案 —— 想知道「现在到哪儿了」看这个** |
| [05-写节点清单.md](05-写节点清单.md) | 写节点时照着做 —— 8 步流程 + 20 个形状模板 |
| [06-ROS2命令速查.md](06-ROS2命令速查.md) | ROS 2 命令参考：项目全流程、查看类命令、报错对照表 |
| [07-draw_square代码解析.md](07-draw_square代码解析.md) | 闭环控制程序（画正方形）的完整结构解析 |
| [08-踩坑总集.md](08-踩坑总集.md) | 踩过的所有坑 —— 67 条，现象 / 原因 / 解决 / 教训 |

> 要了解「现在到哪儿了」，看 [`04-学习进度存档.md`](04-学习进度存档.md)。

---

## 当前环境（现在唯一的环境）

| 项 | 值 |
|---|---|
| 位置 | `E:\Ubuntu-24.04.5\`（虚拟文件放在宿主机这个目录） |
| 系统 | Ubuntu 24.04.5 LTS (Noble) |
| ROS | **ROS 2 Jazzy Jalisco** |
| 仿真 | **Gazebo Harmonic 8.11.0** |
| 内存 | 12 GB |
| CPU | 8 vCPU |
| 磁盘 | 40 GB |
| 网络 | IP `192.168.150.129`（NAT）。**IP 会变，用 `hostname -I` 查当前值** |
| 用户 | `pummy` |
| 开发方式 | 宿主机 VS Code Remote-SSH 连进虚拟机写代码 |
| 快照 | **`12-自定义服务`**（第 12 天拍）。**它勾了"拍摄虚拟机内存"，带一个约 12.4 GB 的 `.vmem`** —— 拍快照时务必取消勾选 |

> 第 1 天使用过的 Ubuntu 22.04 + ROS 2 Humble 旧环境**已删除**，细节只作历史记录保留，见下文。

---

## 工作区结构

代码放在虚拟机内部的工作空间 `~/ros2_ws`，里面有两个包：

| 包 | 构建类型 | 内容 |
|---|---|---|
| `my_turtle` | **ament_python** | 11 个节点，全部学习练习集中在这里 |
| `my_interfaces` | **ament_cmake** | 自定义接口：已有 `msg/TurtleStatus.msg`；`srv/DrawPolygon.srv` 计划第 12 天做 |

### 节点清单（11 个）

| 节点 | 用途 | 需要先启动 `turtlesim_node` |
|---|---|---|
| `draw_circle` | 发布者 + 参数 | 是 |
| `draw_line` | 发布者 | 是 |
| `read_pose` | 订阅者 | 是 |
| `pubsub` | 发布 + 订阅闭环 | 是 |
| `greeter` | 服务端 | 否 |
| `turtle_control` | 发布 + 服务端 + 定时器 | 是 |
| `draw_square` | 发布 + 订阅 + 状态机 + 参数 | 是 |
| `move_client` | 服务客户端 | 是 |
| `rotate_client` | 动作客户端 | 是 |
| `my_rotate_server` | 动作服务端 | 否 |
| `status_bridge` | 订阅 Pose → 发布自定义 `TurtleStatus` | 是 |

> 除 `greeter` 和 `my_rotate_server` 外，其余 9 个节点都需要先启动 `turtlesim_node` 才能工作。

---

## 学习进度

**已进行到第 11 天**，路线共 10 个阶段，当前进度如下：

| 阶段 | 内容 | 状态 |
|---|---|---|
| 阶段 0 | 环境 | ✅ 已完成 |
| 阶段 1 | 核心概念与 CLI | 🔄 只剩 `ros2 bag` 和 QoS |
| 阶段 2 | rclpy 编程基础 | ✅ 已完成 |
| 阶段 3 | 自定义接口 / Launch / 参数 | 🔄 launch、参数、自定义 msg 已完成，只差自定义 srv |
| 阶段 4 及以后 | —— | ⬜ 未开始 |

---

## 历史记录（已完成，仅作记录）

### 旧环境：为什么换掉、怎么换的

第 1 天使用过的旧环境：

| 项 | 值 |
|---|---|
| 系统 | Ubuntu 22.04.5 LTS |
| ROS | ROS 2 Humble |
| 内存 | 4 GB（跑不动仿真） |
| 仿真 | 无 Gazebo |

换环境的三个原因：4 GB 内存是硬伤，Gazebo + RViz + Nav2 起步就要 6–8 GB；Humble 默认搭配的 Gazebo Classic 已停止维护；当时尚未开始学习，沉没成本为零。

**迁移已完成**：先备份个人文件，再建新环境并验收全部通过，最后删除旧虚拟机。删除旧环境共回收约 **50 GB**。旧的 `E:\Ubuntu-22.04.5\` 目录已不存在。

### 2026-09-11 新环境验收记录（历史）

| 检查项 | 实际结果 | 判断 |
|---|---|---|
| 系统版本 | 24.04.5 LTS (Noble Numbat) | ✅ |
| 内存 | 11 GiB 总量，可用 10 GiB | ✅ |
| CPU | `nproc` = 8 | ✅ |
| 磁盘 | `/dev/nvme0n1p2` 40 GB，可用 28 G | ✅ 够用 |
| VMware Tools | `open-vm-tools` + `open-vm-tools-desktop` 均已安装 | ✅ |
| 3D 加速 | `glxinfo -B` 显示 `SVGA3D`，OpenGL 4.3（需 ≥ 3.3） | ✅ 关键闸门通过 |
| Gazebo | `gz sim --versions` = `8.11.0`（gz-sim 8 = Harmonic） | ✅ 与 Jazzy 官方配对 |
| ROS 2 桥接 | `ros_gz_sim` 启动后 ROS 2 侧出现 `/clock` | ✅ |

> 当时同时清理了旧快照与 ISO 安装镜像。**快照习惯**：拍摄快照时务必取消勾选「拍摄虚拟机内存」—— 宿主机共 12 GB，勾选后每个快照就占 12 GB，不勾选只要几百 MB。

### 环境搭建要点（详见 [01-环境搭建.md](01-环境搭建.md)）

- **ROS 2 安装方式已变更**：官方改为 `ros2-apt-source` 配置包，网上大量教程还在用 `apt-key add` 的老办法，那个已经失效。
- `ros2.sources` 是符号链接，`grep -r` 默认不跟随符号链接，找它要用 `grep -R` 或直接 `cat`。
- 镜像源：Ubuntu 用清华 TUNA，ROS 2 用中科大 USTC（实测最快，4.3 MB/s）。

---

## 关键坑：Gazebo 在 VMware 里必须用 ogre 渲染引擎

**症状**：`gz sim shapes.sdf` 能启动、不报错，但 3D 视图**持续频闪**。

**原因**：Gazebo Harmonic 默认用 **Ogre2** 渲染引擎，它在 VMware 的 **SVGA3D** 虚拟显卡上存在兼容性问题。

> 注意：**这与「3D 加速是否开启」无关**。`glxinfo` 显示 `SVGA3D`（硬件加速正常）也会出现这个问题。

**解决**：把渲染引擎从 `ogre2` 改成 `ogre`。配置文件是 `~/.gz/sim/8/gui.config` 和 `~/.gz/sim/8/server.config`：

```bash
mkdir -p ~/.gz/sim/8
for f in gui server; do
  SRC=$(find /usr /opt -name "$f.config" 2>/dev/null | head -1)
  [ -n "$SRC" ] && cp "$SRC" ~/.gz/sim/8/$f.config && \
    sed -i 's|<engine>ogre2</engine>|<engine>ogre</engine>|g' ~/.gz/sim/8/$f.config
done
grep -n "engine" ~/.gz/sim/8/gui.config ~/.gz/sim/8/server.config
```

两个文件都要改：`gui.config` 管窗口显示，`server.config` 管服务端渲染（相机、深度相机等传感器仿真走这条路径）。改完不带参数运行 `gz sim shapes.sdf`，画面应该稳定不闪。

**经验教训**：在虚拟机里遇到 Gazebo / RViz 渲染异常，第一反应应该是「换渲染引擎」，而不是怀疑 3D 加速没开。完整的现象、排查过程和参考资料见 [08-踩坑总集.md](08-踩坑总集.md)。

---

## 快速开始

```bash
# 1. 连上虚拟机后先看 IP（NAT 地址会变）
hostname -I

# 2. 加载环境并编译工作空间
source /opt/ros/jazzy/setup.bash   # 已写入 ~/.bashrc，新终端自动生效
cd ~/ros2_ws && colcon build && source install/setup.bash

# 3. 终端 1：启动小乌龟
ros2 run turtlesim turtlesim_node

# 4. 终端 2：跑一个闭环节点
ros2 run my_turtle draw_square

# 5. 需要仿真时启动 Gazebo
gz sim shapes.sdf
```

---

## Git 与文档约定

- **代码仓库**：虚拟机内 `~/ros2_ws`，远程是 GitHub，认证用 SSH。已有连续 11 天的提交记录。
- **`.gitignore`** 包含：`build/` `install/` `log/` `__pycache__/` `*.pyc` `.vscode/`。
- **文档主副本在本目录 `E:\ROS2\`**，每次提交前同步到虚拟机的 `~/ros2_ws/docs/`。
- 工作空间必须放在虚拟机内部，不要放共享文件夹，跨文件系统的 I/O 会让 `colcon build` 慢到无法忍受。
- 在 [02-学习路线.md](02-学习路线.md) 中，每完成一个阶段就勾选对应验收标准；验收标准全部通过才进入下一阶段。
