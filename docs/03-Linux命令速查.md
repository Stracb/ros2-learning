# 03 · Linux 命令速查表

> 为 ROS 2 学习整理的。**只收录你实际会用到的部分**，不求全。
> 每次遇到新命令，我会在这里补充。

---

## 一、命令的通用结构

一条 Linux 命令通常是这个形状：

```
命令名   选项        参数
  │       │          │
  ls     -l    /home/pummy
  │       │          │
 干什么   怎么干     对谁干
```

| 部分 | 说明 | 例子 |
|---|---|---|
| **命令名** | 要执行什么程序 | `ls`、`cd`、`apt` |
| **选项** | 通常以 `-` 开头，调整行为 | `-l` 详细列表、`-a` 显示隐藏文件 |
| **参数** | 操作对象 | 文件名、目录名、包名 |

> 多个短选项可以合写：`ls -la` 等于 `ls -l -a`

---

## 二、权限：`sudo`

```bash
sudo apt install openssh-server
```

| 部分 | 含义 |
|---|---|
| `sudo` | **SuperUser DO** —— 以"管理员权限"执行后面的命令 |
| `apt install` | 要执行的命令 |
| `openssh-server` | 参数（要装的包名）|

**为什么要 sudo？**
Linux 里"改系统"的操作（装软件、改系统配置、动 `/opt` 里的文件）需要管理员权限。
普通用户直接执行会被拒绝（`Permission denied`）。

>  **sudo 会要密码**。输入时**屏幕上不显示任何字符**（连星号都没有），这是正常的，
> 盲打密码然后回车即可。

---

## 三、文件与目录

| 命令 | 全称/含义 | 作用 | 例子 |
|---|---|---|---|
| `pwd` | **P**rint **W**orking **D**irectory | 我现在在哪个目录 | `pwd` |
| `ls` | **l**i**s**t | 列出目录内容 | `ls`、`ls -la`、`ls -R` |
| `cd` | **c**hange **d**irectory | 切换目录 | `cd ~/ros2_ws` |
| `mkdir` | **m**a**k**e **dir**ectory | 创建目录 | `mkdir -p ~/a/b/c` |
| `cp` | **c**o**p**y | 复制 | `cp a.txt b.txt` |
| `mv` | **m**o**v**e | 移动 / 重命名 | `mv old.txt new.txt` |
| `rm` | **r**e**m**ove | 删除 | `rm file.txt`、`rm -r 目录` |
| `cat` | con**cat**enate | 打印文件全部内容 | `cat package.xml` |
| `nano` | — | 终端里的文本编辑器 | `nano ~/.bashrc` |
| `touch` | — | 创建一个空文件 | `touch test.py` |

### 常用选项

| 选项 | 含义 |
|---|---|
| `-l` | 详细列表（权限、大小、时间）|
| `-a` | 显示隐藏文件（以 `.` 开头的）|
| `-h` | 人类可读的大小（KB/MB/GB）|
| `-R` | 递归（对子目录也生效）|
| `-r` | 递归（`rm`、`cp` 用）|
| `-p` | `mkdir`：父目录不存在就一起创建 |

### 特殊路径符号

| 符号 | 含义 | 例子 |
|---|---|---|
| `/` | 根目录 | `/opt/ros` |
| `~` | 用户主目录 | `~` = `/home/pummy` |
| `.` | 当前目录 | `./script.sh` |
| `..` | 上一级目录 | `cd ..` |
| `*` | 通配符 | `*.py` 所有 py 文件 |

---

## 四、软件包管理：`apt`

```bash
sudo apt update
sudo apt install -y ros-jazzy-desktop
```

| 部分 | 含义 |
|---|---|
| `sudo` | 管理员权限 |
| `apt` | Ubuntu 的**软件包管理器** |
| `update` | 子命令：**刷新软件清单**（不是升级！）|
| `install` | 子命令：安装 |
| `-y` | 所有询问自动回答 yes |
| `ros-jazzy-desktop` | 要装的包名 |

### 常用子命令

| 命令 | 作用 |
|---|---|
| `apt update` | 刷新"有哪些软件可装"的清单（**不升级任何东西**）|
| `apt upgrade` | 升级已装的软件 |
| `apt install <包名>` | 安装 |
| `apt remove <包名>` | 卸载 |
| `apt search <关键词>` | 搜索 |
| `dpkg -l <包名>` | **查询某个包装没装** |
| `apt list --installed` | 列出所有已装包 |

> **常见困惑**：`update` 和 `upgrade` 完全不是一回事。
> `update` 只是去网上拿最新的"软件目录"，`upgrade` 才是真的升级。

---

## 五、服务管理：`systemctl`

```bash
sudo systemctl enable --now ssh
```

| 部分 | 含义 |
|---|---|
| `systemctl` | **system control** —— 管理系统服务 |
| `enable` | 设为**开机自动启动** |
| `--now` | 顺便**现在就启动**（等于 enable + start）|
| `ssh` | 服务名 |

| 命令 | 作用 |
|---|---|
| `systemctl status <服务>` | 查看运行状态 |
| `systemctl start <服务>` | 启动 |
| `systemctl stop <服务>` | 停止 |
| `systemctl restart <服务>` | 重启 |
| `systemctl enable <服务>` | 设为开机自启 |
| `systemctl is-enabled <服务>` | 查是否已设自启 |

---

## 六、查找与过滤

| 命令 | 作用 | 例子 |
|---|---|---|
| `which <命令>` | 命令的可执行文件在哪 | `which ros2` |
| `grep <关键词> <文件>` | 在文件里搜关键词 | `grep depend package.xml` |
| `find <目录> -name <名字>` | 按名字找文件 | `find /opt -name "*.msg"` |
| `hostname -I` | 查看本机 IP 地址 | `hostname -I` |
| `ps aux` | 列出所有进程 | `ps aux \| grep ros` |
| `pkill -f <关键词>` | 按关键词杀进程 | `pkill -f "gz sim"` |

### `grep` 常用选项

| 选项 | 含义 |
|---|---|
| `-i` | 忽略大小写 |
| `-r` | 递归搜索目录（**不跟随符号链接**）|
| `-R` | 递归（**跟随符号链接**）|
| `-l` | 只输出文件名 |
| `-n` | 显示行号 |
| `-c` | 只输出匹配行数 |

>  踩过的坑：`grep -r` **不跟随符号链接**，找不到 `ros2.sources` 就是这原因。

---

## 七、管道与重定向（很重要）

### 管道 `|`

**把前一个命令的输出，交给后一个命令处理。**

```bash
dpkg -l | grep ros-jazzy
```
```
dpkg -l 的输出 ──▶ │ ──▶ grep 从里面筛出含 "ros-jazzy" 的行
```

**可以串联多个：**
```bash
ros2 pkg list | grep msgs | head -5
```

### 输出重定向 `>` 和 `>>`

| 符号 | 作用 |
|---|---|
| `>` | 把输出**写入**文件（**覆盖**原内容）|
| `>>` | 把输出**追加**到文件末尾（**不覆盖**）|

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
```
↑ 把这句话**追加**到 `.bashrc` 末尾

---

## 八、环境变量

```bash
echo $ROS_DISTRO
export MY_VAR=hello
source ~/.bashrc
```

| 部分 | 含义 |
|---|---|
| `echo` | 打印内容 |
| `$ROS_DISTRO` | `$` 表示"取出这个变量的值" |
| `export` | 定义一个环境变量（对当前终端及其子进程有效）|
| `source <文件>` | **在当前终端里执行这个文件** |

### `source` 是 ROS 2 的核心机制

```bash
source /opt/ros/jazzy/setup.bash
```

**它在干什么？** 执行那个 `setup.bash` 文件，而那个文件做的事是：
**把 ROS 2 的各种路径写进环境变量**，比如：

| 环境变量 | 作用 |
|---|---|
| `PATH` | 让终端能找到 `ros2`、`rviz2` 这些命令 |
| `AMENT_PREFIX_PATH` | 让 ROS 2 能找到已安装的包 |
| `PYTHONPATH` | 让 Python 能 `import rclpy` |
| `LD_LIBRARY_PATH` | 让系统能找到 ROS 2 的动态库 |

**不 source 会怎样？** 直接报 `ros2: command not found` —— 因为系统不知道去哪找。

### `~/.bashrc` 是什么

**`.bashrc` = 每次打开终端时自动执行的文件。**

```bash
echo "source /opt/ros/jazzy/setup.bash" >> ~/.bashrc
```

**这行的意思**：让每次打开终端时，都自动 source 一次 ROS 2 的环境。

**所以新开的终端不用手动 source，旧终端要手动 source 或重开。**

> 只改了 `.bashrc` 但不想重开终端？执行 `source ~/.bashrc` 立即生效。

---

## 九、终端操作快捷键

| 快捷键 | 作用 |
|---|---|
| `Ctrl + Shift + T` | 新开一个终端标签页 |
| `Ctrl + Shift + W` | 关闭当前标签页 |
| `Ctrl + C` | **终止当前正在运行的程序**（最常用）|
| `Ctrl + L` | 清屏 |
| `Ctrl + Shift + V` | **粘贴**（不是 Ctrl+V！）|
| `Ctrl + A` | 光标跳到行首 |
| `Ctrl + E` | 光标跳到行尾 |
| `Tab` | **自动补全**（命令、文件名都能补，多按几次）|
| `↑` / `↓` | 翻历史命令 |

> **`Tab` 补全是效率神器。** 打 `cd ~/ros` 然后按 Tab，会自动补成 `cd ~/ros2_ws/`。

---

## 十、ROS 2 常用组合

```bash
# 查看 ROS 版本
echo $ROS_DISTRO

# 列出所有包
ros2 pkg list

# 找某个包装在哪
ros2 pkg prefix turtlesim

# 看某个包提供哪些程序
ros2 pkg executables turtlesim

# 找 ROS 相关进程
ps aux | grep ros

# 强杀卡住的 Gazebo
pkill -f "gz sim"
```

---

## 十一、遇到问题时

| 想知道 | 命令 |
|---|---|
| 这个命令是什么、怎么用 | `<命令> --help`（如 `ros2 topic --help`）|
| 这个命令装在哪 | `which <命令>` |
| 某个包装没装 | `dpkg -l <包名>` |
| 磁盘还剩多少 | `df -h` |
| 内存用了多少 | `free -h` |

---

> **最后一句**：不需要背。**常用的十几个命令用两三天就自然熟了**，
> 剩下的随时回来查这份表。
