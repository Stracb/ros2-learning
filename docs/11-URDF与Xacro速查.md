# 11 · URDF 与 Xacro 速查

> **用途**：**回答"URDF / xacro 怎么写"。写机器人模型时照着做。**
> **它只给"骨架形状"（骨架 + 关键点 + 坑指针），不写完整教程、不写长篇原理** ——
> 所以它能帮你回忆起结构，而不会把整份文件直接给你。
>
> **它和别的文件的分工**：
> | 我想… | 去哪 |
> |---|---|
> | **想知道"现在到哪儿了"** | `04-学习进度存档.md` |
> | **写节点** | `05-写节点清单.md` |
> | **敲命令** | `06-ROS2命令速查.md` |
> | **报错了** | `08-踩坑总集.md` |
> | **说不清的现象** | `10-原理与排查方法.md` |
> | **URDF / xacro 怎么写** | **本篇（唯一权威）** |
>
> 建立于第 28 天（2026-10-16）—— 把原先散在 `05` 形状 21 / 22 与阶段四、阶段五里的
> URDF 知识汇总到一处。**它对应的学习阶段：`02-学习路线.md` 阶段四（URDF/Xacro 建模）/
> 阶段五（Gazebo 仿真）；当前进度看 `04-学习进度存档.md` 第一节。**
> **最后更新**：2026-10-30（第 40 天）


---

## 快速查找（先看这里）

**引用写法**：本篇与别篇互相引用一律用「文件名 §编号」或「文件名 坑 N」
（如 `06 §3.12`、`08 坑 73`），**不用 markdown 锚点** —— 锚点依赖标题文字，标题一改就断链。

| 我想知道… | 去哪 |
|---|---|
| **URDF 到底是个什么东西** | **第一部分** |
| **`link` 的三块各管什么、能不能省** | **第一部分** |
| **一个 `link` 怎么写** | **第二部分 · 形状 1** |
| **`continuous` 关节（轮子）怎么写** | **第二部分 · 形状 2** |
| **`fixed` 关节（装传感器）怎么写** | **第二部分 · 形状 3** |
| **`revolute` 关节（有限角度）怎么写** | **第二部分 · 形状 4** |
| **变量（`property`）怎么写** | **第二部分 · 形状 5** |
| **宏（`macro`）的定义与调用** | **第二部分 · 形状 6** |
| **怎么把模型挂进 Gazebo** | **第二部分 · 形状 7** |
| **URDF 里的 Gazebo 插件与传感器** | **第二部分 · 形状 8** |
| **世界文件（`.sdf`）怎么放进包** | **第二部分 · 形状 9** |
| **最容易搞错的四个点** | **第三部分** |
| ⭐ **遇到没见过的插件 / 传感器，怎么查怎么写** | **第四部分** |
| **写完模型怎么验证（5 步）** | **第五部分** |
| **现象不对 / 报错了** | **第六部分** → `08` |

### 第二部分「形状 1–9」一览

> **忘了怎么写，就按编号直接跳到那一节。** 编号是固定的，新增小节不占编号。

| # | 形状 | 一句话 |
|---|---|---|
| **1** | 一个 `link`（三块齐全） | `visual` + `collision` + `inertial` |
| **2** | `continuous` 关节（轮子） | 无限转，**只要 `origin` + `axis`** |
| **3** | `fixed` 关节（传感器） | 焊死，**只有 `origin`，没有 `axis`** |
| **4** | `revolute` 关节（有限角度） | 和 `continuous` 一样，**但必须写 `<limit>`** |
| **5** | `<xacro:property>` | 变量：`name` + `value`，用的时候写 `${名字}` |
| **6** | `<xacro:macro>` 定义 + 调用 | 模板：**定义一次，带参数生成多份** |
| **7** | 把模型挂进 Gazebo | `<gazebo reference="link名">` + 摩擦 / 颜色 |
| **8** | URDF 里的 Gazebo **插件与传感器** | `<sensor type="gpu_lidar">` + 三个 `gz-sim-*-system` 插件 + `<gz_frame_id>` |
| **9** | **世界文件放进包** | `worlds/xxx.sdf` + CMake `install(DIRECTORY ...)` + `get_package_share_directory` |

> **命令怎么敲一律看 `06-ROS2命令速查.md`**（本篇只写"文件怎么写"）——
> 编译 `06 §2.5`、Gazebo / `gz` 命令 `06 §3.12`。
>
> **本工程的实际文件**：`~/ros2_ws/src/my_robot_description/urdf/my_robot.urdf.xacro`
> —— **7 link / 6 joint，10 个 property，2 个宏（`wheel` / `caster`）**，
> 差速驱动 + `gpu_lidar`（目录树见 `04` 第四节）。
> **下面骨架里的 `${...}` 名字以那份文件为准** —— 本篇给的是"形状"，不是逐字原文。

---

# 第一部分：URDF 是什么（先给结构，再给细节）

## 一句话

> **URDF 是"用两种标签描述一台机器人"的文件 —— 只有 `link`（刚体）和 `joint`（连接）。**

```xml
<robot name="my_robot" xmlns:xacro="http://www.ros.org/wiki/xacro">
  <link name="base_link"> ... </link>          <!-- 骨头 -->
  <joint name="xxx_joint" type="..."> ... </joint>   <!-- 关节 -->
</robot>
```

> `xmlns:xacro="..."` 这一行是**用 xacro 的前提**（`<xacro:...>` 标签靠它认出来）。

## 心智模型

| 概念 | 类比 | 说明 |
|---|---|---|
| **`link`** | **骨头** | 一个刚体（车体、轮子、雷达…）|
| **`joint`** | **关节** | 两个 link 之间的连接，**决定"能不能动、怎么动"** |
| 整体 | **一棵树** | 从根往下一层层挂 —— **只能有一个根**（本工程是 `base_link`）|

> **`check_urdf` 会报 `root Link: base_link has N child(ren)`** ——
> **N 就是"直接挂在根下面的 link 个数"**（本工程是 6）。
>
> **关节的父/子是单向的**：`<parent>` 与 `<child>` 合起来决定树的朝向 ——
> **不能有环，也不能有两个根**，否则 `check_urdf` 直接报错。

## 每个 link 的三块：`visual` / `collision` / `inertial`

| 块 | 管什么 | 能不能省 | 省了会怎样 |
|---|---|---|---|
| **`visual`** | **长什么样**（RViz 里看到的形状、颜色）| 能省 | 模型**在 RViz 里看不见**（但物理世界还在）|
| **`collision`** | **物理体积**（Gazebo 算碰撞、算接触用）| 能省 | Gazebo 里**穿模 / 掉进地面**；缺了它，轮子和地面就"碰不上" |
| **`inertial`** | **质量、质心、惯量**（`mass` + `inertia`）| 能省（不推荐）| Gazebo 会**自己补一个默认惯量** → **车会抖、会飘、会陷进地面** |

> **`visual` 和 `collision` 为什么要分开**（`02` 阶段四验收第 3 条）：
> **"看起来的形状"和"算碰撞的形状"可以不一样** ——
> 外观可以做得很精细，碰撞用一个简化盒 / 圆柱就够（**省算力**）；
> 反过来，也可以用不可见的 `collision` 占一块体积（比如给轮子加个"魔改"接触面）。
>
> **同一个 link 里，`visual` 和 `collision` 的 `geometry` 通常一样** ——
> **改了 `visual` 别忘了改 `collision`**（第 18 天在 `laser_link` 上就是这么漏的）。

---

# 第二部分：骨架形状（忘了怎么写的时候查这里）

> **你只需要记"形状"，不用背整行。**
> **每个形状 = 骨架代码块 + 「关键点」表 + 坑指针。**

## 形状 1：一个 link（三块齐全的最小写法）

```xml
<link name="base_link">
  <!-- ① 长什么样 -->
  <visual>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry><box size="0.5 0.3 0.15"/></geometry>   <!-- ★ size 是【全长】，见第三部分 -->
    <material name="blue"><color rgba="0 0 1 1"/></material>
  </visual>

  <!-- ② 物理体积（跟 visual 分开写，别偷懒省掉）-->
  <collision>
    <origin xyz="0 0 0" rpy="0 0 0"/>
    <geometry><box size="0.5 0.3 0.15"/></geometry>
  </collision>

  <!-- ③ 质量 / 质心 / 惯量 -->
  <inertial>
    <origin xyz="0 0 0" rpy="0 0 0"/>              <!-- 质心位置 -->
    <mass value="5.0"/>
    <inertia ixx="..." ixy="0" ixz="0"
             iyy="..." iyz="0"
             izz="..."/>                            <!-- 数值以实际文件为准 -->
  </inertial>
</link>
```

### 关键点

| # | 关键点 | 说明 |
|---|---|---|
| 1 | **`name` 是全局唯一的** | `joint` 的 `parent` / `child`、`<gazebo reference="...">` **都靠这个名字对上** |
| 2 | **`origin` = 「这个块相对 link 自己」的位姿** | 车体的几何中心不一定在 link 原点上 —— 用 `origin` 挪 |
| 3 | **`box` 的 `size` 是全长** | `0.5 0.3 0.15` = 长 0.5 米（不是半长 0.25）→ **见第三部分第 2 条** |
| 4 | **`inertia` 六个分量给全** | `ixx ixy ixz iyy iyz izz` —— **`ixy`/`ixz`/`iyz` 是"惯性积"，对称形状填 `0`** |
| 5 | **数值不要写死** | 尺寸/半径一律用 `<xacro:property>`（形状 5），改一个参数全模型跟着变 |

> **`inertial` 填错的后果（现象 + 因果）见 `10-原理与排查方法.md` §4.5；**
> **惯性参数为什么重要见 `02` 阶段四「学习内容」第 4 条。**

## 形状 2：一个 `continuous` 关节（轮子那种）

```xml
<joint name="left_wheel_joint" type="continuous">
  <parent link="base_link"/>            <!-- 父：挂在谁身上 -->
  <child  link="left_wheel_link"/>      <!-- 子：挂上去的是谁 -->
  <origin xyz="${x_offset} ${wheel_separation / 2} ${wheel_offset_z}" rpy="0 0 0"/>
  <axis xyz="0 1 0"/>                   <!-- ★ 转轴：绕【自己的 y 轴】转 = 左右方向 -->
</joint>
```

### 关键点

| # | 关键点 | 说明 |
|---|---|---|
| 1 | **`continuous` = 无限转** | 轮子就该用它 —— **不需要 `<limit>`** |
| 2 | **`origin` 写在【父】坐标系里** | 位置是"相对 `base_link`"的 → **见第三部分第 1 条** |
| 3 | **`axis` 写在【子】坐标系里** | 而且是"**被 `rpy` 转过之后**的子坐标系" → 同上 |
| 4 | **轮子的轴是 `0 1 0`（y 轴）** | 车轮是"侧着滚"的：**绕左右方向转**，不是绕竖直方向 |
| 5 | **可动关节靠 `/joint_states` 才有 TF** | 没有 `/joint_states` → RViz 报 `No transform from [wheel_left] to [base_link]`（**坑 70**）|
| 6 | **进 Gazebo 可能要补 `<limit effort velocity>`** | 第 18 天 `continuous` 关节**没写 `<limit>`**（RViz 不在意）—— `04` 第一节标了"进 Gazebo 可能要补"，**以实际文件为准** |

> **轮子在 RViz 里不跟着转 / 报 `No transform` → `08-踩坑总集.md` 坑 70。**
> **Gazebo 里轮子要转起来，还要有 `gz-sim-joint-state-publisher-system` 插件**（形状 8 ③）。

## 形状 3：一个 `fixed` 关节（传感器安装那种）

```xml
<joint name="laser_joint" type="fixed">
  <parent link="base_link"/>
  <child  link="laser_link"/>
  <origin xyz="0 0 0.12" rpy="0 0 0"/>   <!-- 焊在哪个位置；具体数值以实际文件为准 -->
</joint>
```

### 关键点

| # | 关键点 | 说明 |
|---|---|---|
| 1 | **`fixed` = 焊死** | **只有 `origin`，没有 `axis`、没有 `<limit>`** —— 写了反而是多余的 |
| 2 | **不需要 `/joint_states`** | 静态关系 → `robot_state_publisher` **启动时就算出来了**（发在 `/tf_static`）|
| 3 | ⚠️ **子 link 会被【合并】进父 link** | Gazebo 转 SDF 时把 fixed 子 link 并进父 link → **见第三部分第 3 条**（这就是坑 73 的根）|
| 4 | **所以传感器的帧名要显式写 `<gz_frame_id>`** | 别指望它自动跟着 URDF 的 link 名走（**形状 8 关键点 2**）|

## 形状 4：一个 `revolute` 关节（有限角度的关节）

```xml
<joint name="arm_joint" type="revolute">
  <parent link="base_link"/>
  <child  link="arm_link"/>
  <origin xyz="0 0 0.2" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
  <limit lower="-1.57" upper="1.57" effort="10.0" velocity="1.0"/>   <!-- ★ 必须有 -->
</joint>
```

### 关键点

| # | 关键点 | 说明 |
|---|---|---|
| 1 | **和 `continuous` 只差一个 `<limit>`** | **`revolute` 不写 `<limit>` = 直接报错** |
| 2 | **`lower` / `upper` 是弧度** | `-1.57` ≈ `-90°`，`1.57` ≈ `+90°` |
| 3 | **`effort` = 最大力矩，`velocity` = 最大角速度** | Gazebo 里"能不能转得动"看这两个 |
| 4 | **五种关节类型** | `fixed` / `revolute`（有限转）/ `continuous`（无限转）/ `prismatic`（平移）/ `floating`（自由）—— `02` 阶段四「学习内容」第 2 条 |

## 形状 5：一个 `<xacro:property>`（变量）

```xml
<!-- 定义：放在 <robot> 里、被用到之前 -->
<xacro:property name="wheel_radius" value="0.1"/>
<xacro:property name="caster_radius" value="0.03"/>

<!-- ★ 派生变量：值可以是表达式，引用别的 property -->
<xacro:property name="caster_offset_z"
                value="${wheel_offset_z - wheel_radius + caster_radius}"/>
```

**用的时候写 `${名字}` —— 属性里和文本里都一样：**

```xml
<origin xyz="${x_offset} 0 ${caster_offset_z}" rpy="0 0 0"/>
<cylinder radius="${wheel_radius}" length="0.05"/>
```

### 关键点

| # | 关键点 | 说明 |
|---|---|---|
| 1 | **`value` 可以是表达式** | `${a - b + c}` —— **变量之间可以互相引用**，改上游、下游全部跟着变（第 20 天"改 3 个参数 → 9 处跟着变"）|
| 2 | **能带单位吗？不能** | URDF / xacro 里的长度默认是**米**、角度默认是**弧度**，**不要写 `0.1m`** |
| 3 | **别写死数字** | 本工程 `caster_offset_z` 就是用表达式算的 —— **以后改轮子半径，万向轮自动跟着对齐**（**坑 74**）|
| 4 | **`${}` 里不能有空格问题** | 表达式写简单点；复杂了不如拆成两个 property |
| 5 | **`property` = 变量；`macro` = 模板** | 第 20 天复习时定义说偏过 —— **这两个别混** |

## 形状 6：一个 `<xacro:macro>` 的定义 + 调用

```xml
<!-- ① 定义：name = 宏名，params = 参数表（空格分隔，不是逗号）-->
<xacro:macro name="wheel" params="prefix y">
  <link name="${prefix}_wheel_link"> ... </link>
  <joint name="${prefix}_wheel_joint" type="continuous">
    <parent link="base_link"/>
    <child  link="${prefix}_wheel_link"/>
    <origin xyz="${x_offset} ${y} ${wheel_offset_z}" rpy="0 0 0"/>
    <axis xyz="0 1 0"/>
  </joint>
</xacro:macro>

<!-- ② 调用：把参数当属性传进去 -->
<xacro:wheel prefix="left"  y="0.15"/>
<xacro:wheel prefix="right" y="-0.15"/>
```

### 关键点

| # | 关键点 | 说明 |
|---|---|---|
| 1 | **`params` 用【空格】分隔** | 不是逗号（**CMake 列表也是空格**，见 `05` 形状 18）；**参数名以实际文件为准** |
| 2 | **宏 = 模板，可以带参数重复生成** | **定义一次 → 生成左右两个轮子**（第 17 天"复制的代价"就是被这个解决的）|
| 3 | **本工程的两个宏：`wheel`（驱动轮）/ `caster`（万向轮）** | `wheel` 用 `continuous`，`caster` 用 `fixed`（`04` 第一节）|
| 4 | **展开后才是真 URDF** | `xacro xxx.urdf.xacro > /tmp/a.urdf` —— **想看宏到底生成了什么，就看这个产物** |
| 5 | **改宏 = 改所有调用处** | 这是好处也是风险：**改之前先想清楚"两个轮子要不要一起变"** |

## 形状 7：把模型挂进 Gazebo（`<gazebo reference="...">`）

```xml
<!-- ① 挂在【某个 link】上：改它的 Gazebo 专属属性 -->
<gazebo reference="left_wheel_link">
  <mu1>0.8</mu1>          <!-- ★ 摩擦系数：轮子打滑不前进就是它太低 -->
  <mu2>0.8</mu2>
</gazebo>

<gazebo reference="base_link">
  <material>Gazebo/Blue</material>       <!-- Gazebo 里的颜色（Gazebo 自己的材质名）-->
</gazebo>
```

> **② 不写 `reference` 的 `<gazebo>` 块是【全局】的** ——
> **插件就写在这种块里**（形状 8）。

### 关键点

| # | 关键点 | 说明 |
|---|---|---|
| 1 | **`reference="link名"` 必须和 URDF 里的 link 名一模一样** | 写错了**不报错，只是不生效** |
| 2 | **摩擦是"轮子转但车不走"的第一嫌疑** | `mu1` / `mu2` 太低 → 原地打滑（`10 §4.5`、`02` 阶段五常见坑）|
| 3 | **`<gazebo>` 块是 URDF 的"扩展槽"** | URDF 标准里没有它 —— **它是给 Gazebo 看的**，`check_urdf` 不管 |
| 4 | ⚠️ **`fixed` 子 link 已经不存在了** | 挂在 `laser_link` 这类 fixed 子 link 上的 `<gazebo reference>` **不一定会按你想象生效**（形状 3 关键点 3）|

## 形状 8：URDF 里的 Gazebo 插件与传感器

> **原先住在 `05` 形状 21**（第 28 天搬到本篇，`05` 只留指针）。
> **写在 `.urdf.xacro` 里**（文件本身还是 URDF，只是多了 `<gazebo>` 块）。
> 一共四块：**一个传感器 + 三个 `gz-sim-*-system` 插件**。

```xml
<!-- ① 传感器：挂在某个 link 上（用 <gazebo reference="link名"> 包住）-->
<gazebo reference="base_link">
  <sensor name="laser" type="gpu_lidar">        <!-- ★ GPU 传感器 -->
    <gz_frame_id>laser_link</gz_frame_id>       <!-- ★ 坑 73：强制指定 frame_id -->
    <pose>0 0 0.5 0 0 0</pose>                  <!-- 相对【所在 link】；本机实测 = 0.5 -->
    <topic>scan</topic>                         <!-- bridge 按这个名字认它 -->
    <update_rate>10</update_rate>
    <ray>
      <scan><horizontal><samples>360</samples></horizontal></scan>
      <range><min>0.1</min><max>20.0</max></range>
    </ray>
  </sensor>
</gazebo>

<!-- ② 差速驱动：车怎么动（第 22 天）-->
<gazebo>
  <plugin filename="gz-sim-diff-drive-system"
          name="gz::sim::systems::DiffDrive">
    <left_joint>left_wheel_joint</left_joint>
    <right_joint>right_wheel_joint</right_joint>
    <wheel_separation>${wheel_separation}</wheel_separation>   <!-- 引用 property，别写死 -->
    <wheel_radius>${wheel_radius}</wheel_radius>
    <topic>cmd_vel</topic>
    <odom_topic>odom</odom_topic>
  </plugin>
</gazebo>

<!-- ③ 传感器系统：让 gpu_lidar 真的产出数据（第 23 天）-->
<gazebo>
  <plugin filename="gz-sim-sensors-system"
          name="gz::sim::systems::Sensors">
    <render_engine>ogre2</render_engine>        <!-- ★ 坑 72/76：GPU 传感器要 ogre2 -->
  </plugin>
</gazebo>

<!-- ④ 关节状态发布：RViz 里轮子才会跟着转（第 23 天）-->
<gazebo>
  <plugin filename="gz-sim-joint-state-publisher-system"
          name="gz::sim::systems::JointStatePublisher">
    <topic>joint_states</topic>
  </plugin>
</gazebo>
```

### 关键点

| # | 关键点 | 说明 |
|---|---|---|
| 1 | **`filename` vs `name`** | `filename` = **插件库名**（`gz-sim-*-system`）；`name` = **类名**（`gz::sim::systems::Xxx`）。**两个都要写**，别混 |
| 2 | **`<gz_frame_id>`** | 不写 → `frame_id` 是 Gazebo 的**完整限定名**（如 `my_robot/base_link/laser`），RViz 认不出 → **加这一行**（坑 73）|
| 3 | **`<render_engine>ogre2</render_engine>`** | **GPU 传感器靠"渲染"看世界** —— 引擎是 `ogre` 就全返回 `range_min`（坑 72 / 76）|
| 4 | **`<sensor>` 只能写一处** | **同时**写进【世界文件】和【URDF】→ 段错误崩溃（坑 77）|
| 5 | **GPU 传感器在虚拟机里要软渲染兜底** | 用 `gpu_lidar` / 相机前先 `export LIBGL_ALWAYS_SOFTWARE=1`，否则**一半扫描是空的、2 米内固定盲区**（**坑 81**）|
| 6 | **换成别的传感器只改两处** | 改 `type`（`gpu_lidar` / `camera` / `imu`…）+ 换插件块 —— **怎么查写法见第四部分** |
| 7 | **噪声写在 `<lidar>` 里面** | **`<sensor>` → `<lidar>` → `<noise>`**。写在 `<sensor>` 下会被 SDF **静默丢弃**，只留一条警告（**坑 94**）。`<mean>0.0</mean>` + `<stddev>0.01</stddev>`（= 1 厘米）|

### 坑：**固定关节会被合并进父 link**

`laser_link` 是用 **`fixed` 关节**接到 `base_link` 上的 ——
**Gazebo 转 SDF 时会把 fixed 子 link "合并"进父 link**，所以：

- **传感器实际归属 `base_link`** —— 这就是坑 73 里 `frame_id` 变成
  `my_robot/base_link/laser` 的原因（**不是 `laser_link`**）。
- **`<gazebo reference="laser_link">` 上的东西不一定会按你想象生效**（那个 link 已经不存在了）。
- **结论**：**帧名字一律用 `<gz_frame_id>` 显式指定**，别指望它自动跟着 URDF 的 link 名走。

### 噪声：`<noise>` 的位置和写法（第 32 天）

**位置**：`<sensor>` → **`<lidar>`** → `<noise>`。**写在 `<sensor>` 下面会被丢掉。**

```xml
<lidar>
  <scan> ... </scan>
  <range> ... </range>
  <noise>
    <type>gaussian</type>
    <mean>0.0</mean>
    <stddev>0.01</stddev>      <!-- 0.01 m = 1 厘米抖动 -->
  </noise>
</lidar>
```

| 字段 | 含义 |
|---|---|
| `<type>gaussian</type>` | 高斯噪声（也有 `uniform`）|
| `<mean>` | 平均值，**填 0**（否则整体偏置，等于把墙挪走了）|
| `<stddev>` | **抖动幅度**（米）。0.01 = 1 厘米 |

**验证（不能省）**：

```bash
gz model -m <模型名> -l | grep -A10 "Noise"
```

看 `Standard deviation` 是不是你设的值 —— **是 0 就说明噪声没进去**。

> **为什么要加噪声**：仿真里数据太完美，算法"看起来很稳"；真机上数据会抖，
> 阈值判定就会**反复触发**（抖振 chattering）。**解法**：滞回（两个阈值）或**多帧确认**。
> 详见 `02` 阶段七的验收原话 + `08` 坑 94。

---

### ⚠️ 本机的一个真实隐患（**第 32 天已修**）：帧名对了，但【位置】没对上

**本机的 URDF 当时是这样写的**：

| 项 | 值 |
|---|---|
| **传感器挂在哪** | `<gazebo reference="base_link">` |
| **`<pose>`** | **`0 0 0.5 0 0 0`** → **实际在车体原点上方 0.5 米** |
| **`<gz_frame_id>`** | **`laser_link`** |
| **而 `laser_link` 的关节位置** | **`z = 0.12`**（第 27 天用 `tf2_echo odom laser_link` 实测过）|

> ## **⟹ TF 说"雷达在 0.12 米高处"，而它实际在 0.5 米高处 —— 差了 0.38 米。**

> ## **✅ 第 32 天已修**：`<pose>` 改成 **`0 0 ${base_height/2 + laser_height/2} 0 0 0`** ——
> ## **两处用【同一个 xacro 表达式】算出来，不再各写各的数字**（写死数字 = 迟早对不上）。

**后果**：
- **RViz 里激光点云的位置会整体偏高**（看不出来，但量一下就不对）
- **以后做建图 / 避障时，这个偏差会变成"地图错位"**（墙的位置整体平移）

**怎么修（二选一，让两者一致）**：

| 方案 | 改哪里 |
|---|---|
| **A** | **把 `<pose>` 改成 `0 0 0.12 0 0 0`** —— 让传感器真的待在 `laser_link` 那个位置 |
| **B** | **把 `laser_link` 的关节 `z` 改成 `0.5`** —— 让 `laser_link` 跟着传感器走 |

> **这不是"必须马上改"的 bug** —— **它不影响"车能跑、雷达有数据"** ✅
> **但它是个【真错误】**：等到建图时才发现，会表现为**墙的位置整体平移**，极难查。
>
> **本机选的是 A 的变体**：不是写死 `0.12`，而是让两处**都从同一组 xacro 参数算**：

```xml
<xacro:property name="base_height" value="0.2"/>
<xacro:property name="laser_height" value="0.12"/>
<!-- 传感器 -->
<pose>0 0 ${base_height/2 + laser_height/2} 0 0 0</pose>
<!-- laser_link 的关节 -->
<origin xyz="0 0 ${base_height/2 + laser_height/2}" rpy="0 0 0"/>
```

> ## **⟹ 判据：两处数字要么【同一个表达式】，要么【根本不写数字】。** ✅

> **完整因果链见 `08-踩坑总集.md` 坑 72 / 73 / 77。**
> **"改了没生效 / 数据不对"的现象排查见 `10-原理与排查方法.md` §4.4（坐标系 / TF）与 §4.5（模型行为）。**

## 形状 9：世界文件放进包

> **原先住在 `05` 形状 22**（第 28 天搬到本篇，`05` 只留指针）。
> **一句话**：**要重复用到的东西（世界、模型、配置）都要进包** ——
> **放 `/tmp` 重启就没了**（坑 78）。

**① 文件放哪**：

```
~/ros2_ws/src/my_robot_description/worlds/my_world.sdf
```

**② `CMakeLists.txt` 里把它装上**（和 `config`/`launch`/`urdf` 同一句）：

```cmake
install(
  DIRECTORY urdf config launch worlds
  DESTINATION share/${PROJECT_NAME}
)
```

**③ launch 文件里用 `get_package_share_directory` 算路径**：

```python
import os
from ament_index_python.packages import get_package_share_directory
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource


def generate_launch_description():
    pkg_share = get_package_share_directory('my_robot_description')
    world_file = os.path.join(pkg_share, 'worlds', 'my_world.sdf')   # ← 算出来的路径

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(get_package_share_directory('ros_gz_sim'),
                             'launch', 'gz_sim.launch.py')
            ),
            launch_arguments={'gz_args': '-r ' + world_file}.items(),  # ← 交给 gz_args
        ),
        # ... 还有 rsp / create / bridge
    ])
```

> **骨架就是这两句**：`get_package_share_directory('包名')` 拿到安装路径，
> `os.path.join(...)` 往里拼 `'worlds'` 和文件名。
> **具体怎么包进你的 `gazebo.launch.py`，以你实际那份为准。**

**④ 启动 Gazebo 时引擎要分开指定**（一分开就出事，坑 76）—— 就是上面那个 `gz_args` 的内容：

```python
'gz_args': '--render-engine-gui ogre --render-engine-server ogre2 -r ' + world_file
```

> **`--render-engine`（不带后缀）是【全局】的，会把 GUI 和服务器一起改掉** ——
> 要么频闪、要么传感器瞎。**必须用 `-gui` / `-server` 两个分开写。**

### 两个容易忘的前提

- **障碍物 / 地图要写进世界文件本身** —— **运行中 `ros_gz_sim create` 放的模型，GPU 传感器看不见**（坑 79）。
- **改完 `worlds/` 里的文件要重编**（CMake 包的资源是"拷贝"进 `install/` 的）→ `06 §2.5`。

> **完整因果链见 `08-踩坑总集.md` 坑 78 / 79 / 76。**
> **"世界文件怎么起、怎么验证"的命令见 `06-ROS2命令速查.md` §3.12。**

---

# 第三部分：四个最容易搞错的点

> **每一条都配一句"错了会怎样"** —— 这四条是第 17–23 天反复出现的那几个。

## 1. `joint` 的 `origin` 在【父】坐标系；`axis` 在【转过 rpy 之后的子】坐标系

> **第 17 天答错、第 20 天答对 → 归入"要写 2 遍"的类，别指望一次记住。**

| 写在哪 | 参照系 | 直觉说法 |
|---|---|---|
| **`origin`** | **父 link** | "**相对爸爸**，我要装在哪" |
| **`axis`** | **子 link**，而且**是 `rpy` 转过之后的**子坐标系 | "**在我自己身上**，绕哪根轴转" |

**错了会怎样**：轮子/雷达**装到车顶上、装反、转轴朝错** —— RViz 里模型立刻不对；
更阴的是**看起来对、动起来不对**（轴朝错 → 车原地打转，见 `10 §4.5`）。

## 2. `box` 的 `size` 是【全长】，不是半长

```xml
<box size="0.5 0.3 0.15"/>   <!-- 长 0.5 米 / 宽 0.3 米 / 高 0.15 米 -->
```

**错了会怎样**：把半长当全长填 → **模型只有设计的一半大**；
比例感一崩，后面所有 `origin` 的对齐都得重算。

## 3. `fixed` 关节的子 link 会被合并进父 link

**所以挂在它下面的传感器，实际归属【父 link】** ——
**这也是为什么传感器帧名要显式写 `<gz_frame_id>`（坑 73）。**

**错了会怎样**：你以为 `frame_id` 会是 `laser_link`，实际是
`my_robot/base_link/laser` → **RViz 里激光画不出来**（数据是好的，只是摆不到位置上）。

## 4. 惯量 / 质量填错 → 车会抖、会飘、会陷进地面

> **`<inertial>` 省了，Gazebo 转换时会替你补一个默认惯量** ——
> **那个默认值几乎一定不是你想要的。**
> **补了什么，`gz sdf -p` 看转换产物就知道**（第五部分第 2 步）。

| 现象 | 一行原因 | 去哪看 |
|---|---|---|
| 模型自己抖 / 掉进地面 / 飞起来 | `inertial` 参数（质量、质心、惯性矩阵）| `10 §4.5`、`02` 阶段五 |
| 轮子转但车原地打滑 | 摩擦系数太低 → `<mu1>` / `<mu2>`（形状 7）| `10 §4.5` |
| 车体【倾斜】，传感器跟着歪 | **支撑点底部没对齐**（万向轮半径 ≠ 驱动轮半径）| **坑 74** |

> **本工程的实例（坑 74）**：驱动轮半径 `wheel_radius = 0.1`、万向轮 `caster_radius = 0.03`
> —— 两者**底部差 0.07 米** → 车翘约 15.6° → **雷达斜着扫地面**，
> `ranges` 出现一串"平滑渐变"的数。
> 修法：**让底部对齐**，`caster_offset_z = wheel_offset_z - wheel_radius + caster_radius`
> （即 `-0.1 - 0.1 + 0.03 = -0.17`），**用表达式而不是写死数字**。

---

# 第四部分：⭐ 遇到没见过的插件 / 传感器，怎么查怎么写

> **这一节是第 28 天用户专门问的**：
> "要用一个我没见过的传感器 / 插件，我上哪儿找它的写法？"
> **答案是：本机就自带一本"字典"，不用联网也能查到完整可运行的写法。**

## 六步（照顺序走）

```
① 想清楚要什么             "我要测距离" → 关键字 lidar
② 在官方示例目录里搜        ls /opt/ros/jazzy/opt/gz_sim_vendor/share/gz/gz-sim8/worlds/ | grep -i lidar
③ 打开那个 .sdf 看完整写法   cat .../worlds/gpu_lidar_sensor.sdf
④ 抄 <sensor> 和 <plugin> 两块结构，改参数
⑤ 验证转换对不对            xacro 模型.urdf.xacro > /tmp/a.urdf && gz sdf -p /tmp/a.urdf
⑥ 跑起来看数据              ros2 topic echo /scan --once
```

> ### ⚠️ `gz sdf` / `check_urdf` **只认【纯 URDF】，不认 `.xacro`**
>
> **直接喂 `.xacro` 会报一堆 `Unable to parse component [${base_length}]`**（第 30 天实测）
> —— **因为工具读到的还是 `${...}` 变量，没人替换它们** ✅
>
> **所以永远分两步**：
> ```bash
> xacro urdf/my_robot.urdf.xacro > /tmp/my_robot.urdf     # ① 展开成纯 URDF
> gz sdf -p /tmp/my_robot.urdf                            # ② 再喂给工具
> ```

> **②③ 里的路径是"本机这份安装"的位置** ——
> **换机器 / 换版本可能不同，先用 `ls` 摸一下实际路径**（找 `gz-sim*` 那一层）。

## 四个要点

| # | 要点 |
|---|---|
| 1 | **本机自带几百个官方示例世界**（`.../gz-sim8/worlds/`），**每个传感器、每个插件都有完整可运行写法** —— **这是最实用的"字典"** |
| 2 | **示例是 SDF、你的模型是 URDF** —— **但 `<sensor>` 和 `<plugin>` 这两块可以原样搬进去**（形状 8 就是这么来的）|
| 3 | **另外两个去处**：**官方文档 `gazebosim.org/docs`**（按任务组织，如 "Sensors" 一节）、**`gz sim --help`**（命令行本身也是说明书）|
| 4 | ⭐ **加插件前先问**："**这个功能是不是有现成的 system 插件？**" —— **有就抄，不要自己写** |

## 怎么搜（三个常用动作）

```bash
# ① 按关键字列示例（lidar / camera / imu / diff_drive / buoyancy ...）
ls /opt/ros/jazzy/opt/gz_sim_vendor/share/gz/gz-sim8/worlds/ | grep -i lidar

# ② 读整个示例（完整、可运行）
cat /opt/ros/jazzy/opt/gz_sim_vendor/share/gz/gz-sim8/worlds/gpu_lidar_sensor.sdf

# ③ 你自己的模型到底被转换成了什么（★ 最有用的一条）
#    ⚠️ 先展开！gz sdf 不认 .xacro
xacro ~/ros2_ws/src/my_robot_description/urdf/my_robot.urdf.xacro > /tmp/my_robot.urdf
gz sdf -p /tmp/my_robot.urdf
```

> **`gz sdf -p` 会把【纯 URDF】转成 SDF 打出来** ——
> **它就是"Gazebo 真正看到的东西"**，还能顺便看到 `frame_id` 变成了什么（坑 73）。
> **⚠️ 它不认 `.xacro`** —— 直接喂会报 `Unable to parse component [${...}]`（第 30 天实测）。
> **命令的完整说明见 `06-ROS2命令速查.md` §3.12。**
> **⚠️ 注意**：**`<ros2_control>` 块在 SDF 里【看不到】是正常的** —— 它是 URDF 扩展标签，
> **`gz_ros2_control` 直接读 URDF，不经过 SDF** ✅

---

## ⭐ 把官方示例【跑起来看】（比读十页文档管用）

**本机自带的示例世界有 126 个**，**每一个都是【能直接运行的 SDF】** ——
所以"我想看看这东西长什么样"是可以做到的，不只是读代码。

### 三步

```bash
# ① 定一个变量，省得每次打一长串路径
WORLDS=/opt/ros/jazzy/opt/gz_sim_vendor/share/gz/gz-sim8/worlds

# ② 按关键字筛出候选（lidar / camera / imu / depth / sonar ...）
ls $WORLDS | grep -iE "camera|imu|lidar"

# ③ 挑一个，把它【交给 gz sim】—— 这就是"取出来跑"
gz sim $WORLDS/<你挑的那个文件名>.sdf
```

> ## **`gz sim <某个.sdf 的路径>`** —— 跑一个示例就这么简单。
> **路径 = `$WORLDS/文件名`**；文件名从第 ② 步的清单里挑。

### 跑之前先设这一条（坑 81）

```bash
export LIBGL_ALWAYS_SOFTWARE=1
```

**不设的话**：`gpu_lidar` / 相机这类 GPU 传感器，会**一半扫描是空的、2 米内固定盲区** —— **而且不报错**。

**建议带上的完整命令**：

```bash
export LIBGL_ALWAYS_SOFTWARE=1
gz sim --render-engine-gui ogre --render-engine-server ogre2 $WORLDS/gpu_lidar_sensor.sdf
```

### 跑起来之后，看三件事

| # | 命令 | 看什么 |
|---|---|---|
| **1** | `gz topic -l` | **它发了哪些话题** —— 你关心的传感器叫什么名字 |
| **2** | `gz model --list` | **世界里有什么**（车、墙、地面）|
| **3** | `gz topic -e -t <话题名>` | **数据长什么样**（这就是你要抄进自己项目的东西）|

> ## **目标不是"读懂那个文件"，而是【看到它跑起来、看到数据】。**
> ## **看到了，再回头抄结构就快了。**

### 挑哪个先跑

| 建议 | 原因 |
|---|---|
| ✅ **`imu_sensor.sdf` 之类的小世界** | **不依赖图形渲染，最不容易出问题** |
| ⚠️ **带 `gpu_lidar` / `camera` 的** | 一定要先设 `LIBGL_ALWAYS_SOFTWARE=1`（坑 81）|
| ⚠️ **有些示例会去 Fuel 下载模型** | 首次运行可能等一会儿，甚至需要联网 |

## 拿不准"该不该自己写"时的判据

| 你想干的事 | 该怎么做 |
|---|---|
| 让车动起来 | **有现成插件** → `gz-sim-diff-drive-system`（形状 8 ②）|
| 让 GPU 传感器产出数据 | **有现成插件** → `gz-sim-sensors-system`（形状 8 ③）|
| 发布关节角度 | **有现成插件** → `gz-sim-joint-state-publisher-system`（形状 8 ④）|
| **上面都没有的怪需求** | 先在这一节的"字典"里搜一遍关键字，**搜不到再考虑自己写** |

> **这一节的方法论和 `10-原理与排查方法.md` §5 是同一套**：
> **先看事实（示例怎么写的、转换产物是什么），再动手写。**

---

# 第五部分：验证套路（写完模型后依次做）

| 步 | 命令 | 看什么 |
|---|---|---|
| **1** | `check_urdf <你的.urdf>`<br>（xacro 要先展开：`xacro xxx.urdf.xacro > /tmp/a.urdf`）| **树结构对不对、有没有报错** —— 期望 `Successfully Parsed XML` + `root Link: base_link has N child(ren)` |
| **2** | `gz sdf -p <你的.urdf>` | ✅ **URDF→SDF 的转换结果**（Gazebo 真正看到的东西），顺便能看到 `frame_id` 变成了什么 |
| **3** | `ros2 launch ...` 起 rsp + RViz | **模型显示对不对、TF 树全不全**（RViz 的 `Fixed Frame` 选 `base_link`）|
| **4** | `ros2 run tf2_tools view_frames` | **关节的 TF 有没有发出来**（可动关节没 TF 就是**坑 70**）|
| **5** | `gz model --list` | **Gazebo 里到底有没有这台车**（★ 验证事实的硬手段）|

> **仿真命令怎么敲**（起 Gazebo / 桥接 / `create` / `gz` 系列）→ `06-ROS2命令速查.md` §3.12。
> **`view_frames` 怎么读**（`rate: 10000` + `most_recent_transform: 0` = 静态变换）→ `04` 第一节第 25 天成果。
> **每次实验前先清残留进程** → `06 §3.12` 末尾 + `08` 坑 80。

> ⚠️ **改了 URDF 之后，"上一次的结果"还在原地**：
> `robot_state_publisher` 只在启动时读一次 URDF；Gazebo 里那台车也是旧的
> —— **要重启 rsp / 重新 `create`**（`10 §4.3`）。

---

# 第六部分：常见坑 → 指针

> **只列 URDF / 模型相关的** —— **每条坑的完整记录（现象 → 原因 → 解决 → 教训）在 `08-踩坑总集.md`。**

| 现象 | 坑号 |
|---|---|
| 可动关节**没有变换**（RViz 报 `No transform from [wheel_left] to [base_link]`）| `08` **坑 70** |
| Gazebo 发来的数据 `frame_id` 和 rsp **对不上**（`my_robot/base_link/laser`）| `08` **坑 73** |
| **车体倾斜**，传感器跟着歪（万向轮与驱动轮底部没对齐 → 车翘）| `08` **坑 74** |
| 改了 SDF 里的 `<pose>`，模型**还是出生在原点**（`create` 的 `-x -y -z` 覆盖它）| `08` **坑 75** |
| `Scene already exists with name: scene` + **段错误**（`Sensors` 插件写了两遍）| `08` **坑 77** |
| 重启后 `Unable to find or download file`（世界文件放在 `/tmp` 或包外）| `08` **坑 78** |
| `create` 在运行中放进去的**障碍物，雷达看不见** | `08` **坑 79** |
| 噪声加了却**没效果**（数据仍完美平滑、`Standard deviation` 是 0）| `08` **坑 94**（`<noise>` 要写进 `<lidar>`）|

> **一个能扩展到使用层的补充**：`gpu_lidar` 在虚拟机上半瞎（坑 81）——
> **`export LIBGL_ALWAYS_SOFTWARE=1` 是跑传感器实验前的固定动作。**
>
> **按现象查错（不是按坑号）→ `10-原理与排查方法.md` §4.4 / §4.5。**
> **按报错原文查 → `08-踩坑总集.md` 开头的「按报错原文查」索引。**
