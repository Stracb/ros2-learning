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
> **URDF 和 SRDF 不是一回事**（这两行要先分清）：
>
> | 文件 | 是什么 | 谁要它 |
> |---|---|---|
> | **URDF** | **机器人的样子** —— link / joint / 几何 / 惯量 | **所有系统都要**（RViz、Gazebo、`ros2_control`、MoveIt）|
> | **SRDF** | **给 MoveIt 的说明书** —— 分组、自碰撞豁免、末端执行器、`virtual_joint` | **只有 MoveIt 要**；**不进 URDF**，也不影响仿真 |
>
> 两者的分工与"四个约定"见 `08-踩坑总集.md` 坑 116（第 54 天）。
>
> 建立于第 28 天（2026-10-16）—— 把原先散在 `05` 形状 21 / 22 与阶段四、阶段五里的
> URDF 知识汇总到一处。**它对应的学习阶段：`02-学习路线.md` 阶段四（URDF/Xacro 建模）/
> 阶段五（Gazebo 仿真）；当前进度看 `04-学习进度存档.md` 第一节。**
> **最后更新**：**2026-11-17（第 55 天）** —— 第 50–55 天补了段 11 的模型知识
> （mimic / limit 余量 / bullet-featherstone / `/clock`）


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
| **`mimic` 从关节（夹爪那种）怎么写** | **第二部分 · 形状 10** |
| **`<ros2_control>` 怎么接进 URDF** | **第二部分 · 形状 11** |
| **最容易搞错的四个点** | **第三部分** |
| ⭐ **遇到没见过的插件 / 传感器，怎么查怎么写** | **第四部分** |
| **写完模型怎么验证（5 步）** | **第五部分** |
| **现象不对 / 报错了** | **第六部分** → `08` |

### 第二部分「形状 1–11」一览

> **忘了怎么写，就按编号直接跳到那一节。** 编号是固定的，新增小节不占编号。

| # | 形状 | 一句话 |
|---|---|---|
| **1** | 一个 `link`（三块齐全） | `visual` + `collision` + `inertial` |
| **2** | `continuous` 关节（轮子） | 无限转，**但 `<limit effort velocity>` 也要写** |
| **3** | `fixed` 关节（传感器） | 焊死，**只有 `origin`，没有 `axis`** |
| **4** | `revolute` 关节（有限角度） | 必须写 `<limit>`，而且**两端都要留余量**（贴边 = 控制器永久失效）|
| **5** | `<xacro:property>` | 变量：`name` + `value`，用的时候写 `${名字}` |
| **6** | `<xacro:macro>` 定义 + 调用 | 模板：**定义一次，带参数生成多份** |
| **7** | 把模型挂进 Gazebo | `<gazebo reference="link名">` + 摩擦 / 颜色 |
| **8** | URDF 里的 Gazebo **插件与传感器** | `<sensor type="gpu_lidar">` + 三个 `gz-sim-*-system` 插件 + `<gz_frame_id>` |
| **9** | **世界文件放进包** | `worlds/xxx.sdf` + CMake `install(DIRECTORY ...)` + `get_package_share_directory` |
| **10** | **`mimic` 从关节** | 一个命令带两个手指 —— **只读不写** + 换 `bullet-featherstone` + `limit` 留余量 |
| **11** | **`<ros2_control>` 接入** | `<hardware><plugin>` + `<gazebo>` 插件 + `<parameters>` 路径（⚠️ 草案）|

> **形状 2 的一句话要说准**：`continuous` **也要写 `<limit effort velocity>`** ——
> RViz 不看，**但 Gazebo / `ros2_control` 缺了它，关节拿不到力矩上限**（形状 2 关键点 1 / 6）。

> **命令怎么敲一律看 `06-ROS2命令速查.md`**（本篇只写"文件怎么写"）——
> 编译 `06 §2.5`、Gazebo / `gz` 命令 `06 §3.12`。
>
> **本工程的实际文件**：`~/ros2_ws/src/my_robot/urdf/my_robot.urdf.xacro`
> —— **7 link / 6 joint，10 个 property，2 个宏（`wheel` / `caster`）**，
> 差速驱动 + `gpu_lidar`（目录树见 `04` 第四节）。
> **下面骨架里的 `${...}` 名字以那份文件为准** —— 本篇给的是"形状"，不是逐字原文。
>
> ⚠️ **包名第 31 天改过**：`my_robot_description` → **`my_robot`**
> —— 原因见 `08` 坑 82：**`<parameters>` 的路径里不能出现 `robot_description`**。
> 见到的旧笔记里若还写 `my_robot_description`，一律按 `my_robot` 读。

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
  <limit effort="20" velocity="20"/>    <!-- ★ continuous 也要写：Gazebo / ros2_control 靠它拿上限 -->
</joint>
```

### 关键点

| # | 关键点 | 说明 |
|---|---|---|
| 1 | **`continuous` = 无限转，但 `<limit effort velocity>` 必须写** | RViz 不看这个；**Gazebo / `ros2_control` 缺了它，关节拿不到力矩上限 —— 轮子和夹爪都推不动** |
| 2 | **`origin` 写在【父】坐标系里** | 位置是"相对 `base_link`"的 → **见第三部分第 1 条** |
| 3 | **`axis` 写在【子】坐标系里** | 而且是"**被 `rpy` 转过之后**的子坐标系" → 同上 |
| 4 | **轮子的轴是 `0 1 0`（y 轴）** | 车轮是"侧着滚"的：**绕左右方向转**，不是绕竖直方向 |
| 5 | **可动关节靠 `/joint_states` 才有 TF** | 没有 `/joint_states` → RViz 报 `No transform from [wheel_left] to [base_link]`（**坑 70**）|
| 6 | **进 Gazebo 必须补 `<limit effort velocity>`** | 第 18 天 `continuous` 关节**没写 `<limit>`**（RViz 不在意）。旧引用「`04` 第一节」**已作废**（`04` 已重构，顶部三节不再编号）；现在的出处是 **`08` 坑 115**（`limit` 的完整教训）+ **`12` 第 50 天**（Gazebo 版 Panda 三控制器接管）|

> ⚠️ **草案：待用虚拟机里的实际文件核对后转正**
> —— **"`continuous` 缺 `<limit>` → Gazebo / `ros2_control` 里推不动"这条后果**，
> 手上只有 `08` 坑 115（`limit` 贴边 / 没留余量 → 夹爪怎么推都只动 0.0027）与第 50 天的接管经验，
> **还没在虚拟机上"故意删掉轮子的 `<limit>`"单独复现**；`effort="20" velocity="20"` 也**不是**本机文件里的原值。


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

### 变体：机械臂进 Gazebo 要加一个 `world` 固定根

**`fixed` 的另一个用途：把一个"根 link"焊到 Gazebo 的世界上。**
（下面四行照抄 `08` 坑 115「完整配置（可直接抄）」的开头）

```xml
<link name="world"/>                      <!-- Gazebo 的固定根 -->
<joint name="world_to_panda" type="fixed">
  <parent link="world"/><child link="panda_link0"/>
</joint>
```

| # | 关键点 | 说明 |
|---|---|---|
| 1 | **不加 → 底座瘫倒** | 机械臂没有轮子、不靠摩擦站住，**必须焊死**。第 50 天的原话：**"底座没固定会瘫倒"**（`12` 第 50 天、`08` 坑 115）|
| 2 | **`world` 是 Gazebo 的固定根** | 它**不是**你机器人的 link —— **`robot_state_publisher` 不发这一帧**，RViz 里看不到 `world`。别拿它当 TF 父帧 |
| 3 | **车（差速驱动）不需要它** | 车靠轮子落地，根还是 `base_link`；**只有"要焊在地上"的模型才加** |


## 形状 4：一个 `revolute` 关节（有限角度的关节）

```xml
<joint name="arm_joint" type="revolute">
  <parent link="base_link"/>
  <child  link="arm_link"/>
  <origin xyz="0 0 0.2" rpy="0 0 0"/>
  <axis xyz="0 0 1"/>
  <limit lower="-1.57" upper="1.57" effort="10.0" velocity="1.0"/>   <!-- ★ 必须有；两端都要留余量（关键点 5）-->
</joint>
```

### 关键点

| # | 关键点 | 说明 |
|---|---|---|
| 1 | **和 `continuous` 只差一个 `<limit>`** | **`revolute` 不写 `<limit>` = 直接报错** |
| 2 | **`lower` / `upper` 是弧度** | `-1.57` ≈ `-90°`，`1.57` ≈ `+90°` |
| 3 | **`effort` = 最大力矩，`velocity` = 最大角速度** | Gazebo 里"能不能转得动"看这两个 |
| 4 | **五种关节类型** | `fixed` / `revolute`（有限转）/ `continuous`（无限转）/ `prismatic`（平移）/ `floating`（自由）—— `02` 阶段四「学习内容」第 2 条 |
| 5 | **`lower` / `upper` 两端都要离开初始位置留余量** | **初始位置正好落在边界 = 控制器永久失效** —— 夹爪写 `lower="0.0"` 踩过：出生就站在下限上，被重力/碰撞推过界 0.0001，之后**怎么推都只动 0.0027**（`08` 坑 115 条件 3）。本机改法是两端都往外让一点：`<limit effort="20" lower="-0.01" upper="0.045" velocity="0.2"/>` |


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
| 3 | **本工程的两个宏：`wheel`（驱动轮）/ `caster`（万向轮）** | `wheel` 用 `continuous`，`caster` 用 `fixed`（写法见形状 2 / 形状 3）|
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
> **另有一块 `/clock` 桥接不在 URDF 里**，是 launch 的事（形状 9 ⑥）—— **漏了它控制器就在用墙钟跑**。

```xml
<!-- ① 传感器：挂在某个 link 上（用 <gazebo reference="link名"> 包住）-->
<gazebo reference="base_link">
  <sensor name="laser" type="gpu_lidar">        <!-- ★ GPU 传感器 -->
    <gz_frame_id>laser_link</gz_frame_id>       <!-- ★ 坑 73：强制指定 frame_id -->
    <pose>0 0 ${laser_z} 0 0 0</pose>            <!-- 相对【所在 link】；本机 ${laser_z} = 0.12（见本节末尾的隐患）-->
    <topic>scan</topic>                         <!-- bridge 按这个名字认它 -->
    <update_rate>10</update_rate>
    <lidar>                                     <!-- ★ Harmonic 是 <lidar>，<ray> 是 Classic 的写法 -->
      <scan><horizontal><samples>360</samples></horizontal></scan>
      <range><min>0.1</min><max>20.0</max></range>
      <noise>                                   <!-- 必须在这一层，见关键点 7 -->
        <type>gaussian</type>
        <mean>0.0</mean>
        <stddev>0.01</stddev>
      </noise>
    </lidar>
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
| 4 | **`Sensors` 插件只能写一处** | 留在 URDF、删世界文件里的那个 —— **同时写两处 → 段错误崩溃**（坑 77）。注意：**这不是说 `<sensor>` 只能写一处** —— **`<sensor>` 写两处不会崩，只是世界里多一台传感器** |
| 5 | **GPU 传感器在虚拟机里要软渲染兜底** | 用 `gpu_lidar` / 相机前先 `export LIBGL_ALWAYS_SOFTWARE=1`，否则**一半扫描是空的、2 米内固定盲区**（**坑 81**）|
| 6 | **换成别的传感器只改两处** | 改 `type`（`gpu_lidar` / `camera` / `imu`…）+ 换插件块 —— **怎么查写法见第四部分** |
| 7 | **噪声写在 `<lidar>` 里面** | **`<sensor>` → `<lidar>` → `<noise>`**。写在 `<sensor>` 下会被 SDF **静默丢弃**，只留一条警告（**坑 94**）。`<mean>0.0</mean>` + `<stddev>0.01</stddev>`（= 1 厘米）。⚠️ **这一层的名字是 `<lidar>`** —— `<ray>` 是 Gazebo Classic 的写法，Harmonic 的 `gpu_lidar` 不认它 |

### 坑：**固定关节会被合并进父 link**

`laser_link` 是用 **`fixed` 关节**接到 `base_link` 上的 ——
**Gazebo 转 SDF 时会把 fixed 子 link "合并"进父 link**。所以帧名 / 归属对不上有**两条并列原因**，别只记住一条：

| # | 原因 | 表现 |
|---|---|---|
| **①** | **不写 `<gz_frame_id>`** | `frame_id` 就是 **Gazebo 的限定名 `<模型>/<link>/<传感器名>`**（如 `my_robot/base_link/laser`）—— RViz 认不出这个名字 |
| **②** | **传感器写在 `fixed` 子 link 上** | 那个子 link 被合并后，**这段限定名里的 link 会变成父 link 名**（写在 `laser_link` 上，出来是 `base_link/laser`）|

- **`<gazebo reference="laser_link">` 上的东西不一定会按你想象生效**（那个 link 可能已经不存在了）。
- **怎么确认 link 还在不在**：**`gz sdf -p` 看转换产物**（第五部分第 2 步）—— 名字没了就是被合并了，**别假设它还在**。
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

| 项 | 值（第 32 天修**之前**）|
|---|---|
| **传感器挂在哪** | `<gazebo reference="base_link">` |
| **`<pose>`** | **`0 0 0.5 0 0 0`** → **实际在车体原点上方 0.5 米** |
| **`<gz_frame_id>`** | **`laser_link`** |
| **而 `laser_link` 的关节位置** | **`z = 0.12`**（第 27 天用 `tf2_echo odom laser_link` 实测过）|

> **这张表里有两件事，别混成一件**（两条并列原因，见前面「固定关节会被合并进父 link」那一节）：
> ① **`<gz_frame_id>` 写什么，`frame_id` 就是什么** —— 这里写了 `laser_link`，所以 TF 用的是这个名字；
> ② **`laser_link` 这个 link 在 SDF 里已经被合并进 `base_link`** —— **用 `gz sdf -p` 确认它还在不在**，
> 别假设这个名字背后一定站着一个真实的 link。

> ## **⟹ TF 说"雷达在 0.12 米高处"，而它实际在 0.5 米高处 —— 差了 0.38 米。**

> ## **✅ 第 32 天已修**：`<pose>` 改成 **`0 0 ${laser_z} 0 0 0`** ——
> ## **两处用【同一个 property】算出来，不再各写各的数字**（写死数字 = 迟早对不上）。

**后果**：
- **RViz 里激光点云的位置会整体偏高**（看不出来，但量一下就不对）
- **以后做建图 / 避障时，这个偏差会变成"地图错位"**（墙的位置整体平移）

**怎么修（二选一，让两者一致）**：

| 方案 | 改哪里 |
|---|---|
| **A** | **把 `<pose>` 改成 `0 0 ${laser_z} 0 0 0`** —— 让传感器真的待在 `laser_link` 那个位置 |
| **B** | **把 `laser_link` 的关节 `z` 也改成 `<pose>` 里那个值** —— 让 `laser_link` 跟着传感器走 |

> **这不是"必须马上改"的 bug** —— **它不影响"车能跑、雷达有数据"** ✅
> **但它是个【真错误】**：等到建图时才发现，会表现为**墙的位置整体平移**，极难查。
>
> **本机选的是 A**：不写死两处数字，而是**定义一次、两处都引用** ——
> **只留一种算法**（以前这里同时存在 `0.12` 和 `0.16` 两种算法，第 55 天统一成一个 property）：

```xml
<xacro:property name="laser_z" value="0.12"/>   <!-- 第 27 天 tf2_echo odom laser_link 实测的那个值 -->
<!-- 传感器（挂在 base_link 上）-->
<pose>0 0 ${laser_z} 0 0 0</pose>
<!-- laser_link 的关节 -->
<origin xyz="0 0 ${laser_z}" rpy="0 0 0"/>
```

> **要抬就一起抬**：如果确实想把雷达升到 **0.16**（几何来源 = 车体半高 `0.1` + 雷达半高 `0.06`），
> **只改 `${laser_z}` 这一个值**，两处自动同步 —— **绝不允许一处 `0.12`、一处 `0.16`**。
> 这也是唯一允许的"第二种算法"：**换个 property 的值，不是换个公式**。

> ## **⟹ 判据：两处数字要么【同一个 property】，要么【根本不写数字】。** ✅

> **完整因果链见 `08-踩坑总集.md` 坑 72 / 73 / 77。**
> **"改了没生效 / 数据不对"的现象排查见 `10-原理与排查方法.md` §4.4（坐标系 / TF）与 §4.5（模型行为）。**

## 形状 9：世界文件放进包

> **原先住在 `05` 形状 22**（第 28 天搬到本篇，`05` 只留指针）。
> **一句话**：**要重复用到的东西（世界、模型、配置）都要进包** ——
> **放 `/tmp` 重启就没了**（坑 78）。

**① 文件放哪**：

```
~/ros2_ws/src/my_robot/worlds/my_world.sdf
```

> ⚠️ 包名第 31 天从 `my_robot_description` 改成了 **`my_robot`** ——
> 原因见 `08` 坑 82（`<parameters>` 路径里不能出现 `robot_description`）。

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
    pkg_share = get_package_share_directory('my_robot')             # 第 31 天改名，见 08 坑 82
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

**⑤ 有 `mimic` 的模型必须换【物理引擎】= `bullet-featherstone`**

> **为什么**：**DART 不支持 mimic → 从关节速度直接 `NaN`，一动不动**
> （`12` 第 51 天原话；`08` 坑 115 条件 2）。**换引擎不是优化，是前提。**

**写法一：`gz sim` 命令行**（抄自 `08` 坑 115「完整配置（可直接抄）」）：

```bash
gz sim -r empty.sdf --physics-engine gz-physics-bullet-featherstone-plugin
```

**写法二：launch 的 `gz_args` 里**（把同一串参数交给 `gz sim`）：

```python
'gz_args': '--physics-engine gz-physics-bullet-featherstone-plugin -r ' + world_file
```

> ⚠️ **草案：待用虚拟机里的实际文件核对后转正** ——
> `gz_args` 这一种是**从命令行写法推出来的**（`ros_gz_sim` 把 `gz_args` 原样交给 `gz sim`），
> **本机还没在 launch 里跑通过**；`panda_gazebo.launch.py` 里实际是 `cmd=['gz','sim',...]` 还是 `gz_args`，
> 以那份文件为准。

**⑥ `/clock` 必须 bridge —— 否则控制器在用墙钟跑**

> **摘要照抄 `08` 坑 114**：`gz sim` **不直接发 ROS 话题**（它走 gz-transport），
> **凡 ROS 侧要用的 gz 数据（`/clock`、传感器、`/tf`）都必须显式 bridge，没有"自动转发"。**

```python
Node(
    package='ros_gz_bridge',
    executable='parameter_bridge',
    arguments=['/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'],
    output='screen'
),
```

| 要点 | 说明 |
|---|---|
| **方向符号** | `[` = gz → ROS，`]` = ROS → gz，`@` = 双向（`08` 坑 114 原文）|
| **漏了会怎样** | 一直刷 `[controller_manager]: No clock received, using time argument instead!` —— 控制器照样 `active`、机器人照样能动，**只是所有轨迹时间都错** |
| **怎么验** | `ros2 topic list \| grep -i clock` 有没有 `/clock`；`ros2 topic hz /clock` 有没有频率 |
| **`use_sim_time` 谁要设** | **控制器和自写节点都要设**；**`gz_ros2_control` 的 `use_sim_time` 要写在插件的 `<ros>` 块里**（第 50 天踩过，`12` 第 50 天）|

> ⚠️ **草案：待用虚拟机里的实际文件核对后转正** ——
> **`<ros>` 块里到底放 `<parameters>` 还是 `<param>`**，本机没落成文档（`08` 坑 82 只留下"`<parameters>` 的值不能含 `robot_description`"这一条）。
> 骨架见**形状 11**，那里整段都标了草案。

### 两个容易忘的前提

- **障碍物 / 地图要写进世界文件本身** —— **运行中 `ros_gz_sim create` 放的模型，GPU 传感器看不见**（坑 79）。
- **改完 `worlds/` 里的文件要重编**（CMake 包的资源是"拷贝"进 `install/` 的）→ `06 §2.5`。

> **完整因果链见 `08-踩坑总集.md` 坑 78 / 79 / 76。**
> **"世界文件怎么起、怎么验证"的命令见 `06-ROS2命令速查.md` §3.12。**

## 形状 10：一个 `mimic` 从关节（夹爪那种"一个命令带两个手指"）

> **出处**：`08` 坑 115（第 50–52 天，`12` 日志第 50–52 天）—— 下面四条件是**那次调通的配方**，照抄。
> **一句话原则**：**mimic 关节跟着主关节动 → 对它【只读不写】。**

```xml
<!-- 从关节：保留 <mimic> + 给 limit 留余量（这两块照抄 08 坑 115）-->
<joint name="panda_finger_joint2" type="prismatic">
  <mimic joint="panda_finger_joint1"/>                                <!-- ① 保留 -->
  <limit effort="20" lower="-0.01" upper="0.045" velocity="0.2"/>     <!-- ④ 留余量 -->
</joint>
```

> `parent` / `child` / `axis` 按你的模型填（见形状 4）；**命令接口那边在形状 11 里**。

### 四个条件，缺一不可

| # | 条件 | 不满足会怎样 |
|---|---|---|
| **①** | **保留 `<mimic joint="主关节"/>`**，不删 | 删掉 + 两个都给 command → 控制器能起，但**主关节 `joint1` 反而 `NaN`**（`08` 坑 115 的 ③）|
| **②** | **从关节只给 `state_interface`，控制器只列主关节** | 给从关节 `command_interface` → `Activated mimic joints cannot have command interfaces`，**三个控制器全 `unconfigured`** |
| **③** | **`--physics-engine` 换 `bullet-featherstone`** | **DART 不支持 mimic → 从关节速度 `NaN`，一动不动**（`08` 坑 115 条件 2、`12` 第 51 天）|
| **④** | **`limit` 两端都留余量** | `lower` 正好等于初始位置 → **越界 0.0001 就永久失效，怎么推都只动 0.0027**（`08` 坑 115 条件 3、形状 4 关键点 5）|

### 四条弯路（症状对照，遇到好认）

| # | 当时怎么配的 | 表现 |
|---|---|---|
| ① | mimic + 从关节**给 command** | 三控制器全 `unconfigured` |
| ② | mimic + 从关节**只 state**，**DART 引擎** | 控制器 active，手指速度 **`NaN`**、不动 |
| ③ | **删 mimic** + 两关节都给 command | 控制器 active，**主关节还是 `NaN`**（从关节动了）|
| ④ | 官方 `<param name="mimic">` 写法 | **控制器起不来** —— 这版二进制和官方文档不一致 |

> **顺带一个现象**：为了推动夹爪把 `position_proportional_gain` 调到 10 → **手臂跟着抖** ——
> 这个增益是**全局**的，本质是"弹簧硬度"：**拉得动蚂蚁的力，会把大象弹飞**（`08` 坑 115）。
> **`limit` 修好之后小增益也能推**，不需要大增益。

## 形状 11：`<ros2_control>` 怎么接进 URDF

> ⚠️ **草案：待用虚拟机里 `my_robot` 的实际文件核对后转正**
> —— 第 30–31 天写通过一次，但**成品没贴进任何文档**。下面只写**三处位置 + 两条硬规则**，
> **不是逐字原文**；`filename` / 类名的确切写法尤其要核对。

**三处位置（错一处就全盘不生效）**：

| # | 位置 | 写什么 | 错了会怎样 |
|---|---|---|---|
| **①** | `<ros2_control>` → `<hardware>` → `<plugin>` | 硬件插件类名（Gazebo 里是 `gz_ros2_control` 那一支）| 控制器找不到硬件 → 全部 `unconfigured` |
| **②** | `<gazebo>` 里的 `<plugin>` | `filename` = 插件库名、`name` = 类名；**`use_sim_time` 写在它的 `<ros>` 块里** | 插件不加载；或控制器用墙钟（坑 114）|
| **③** | `<parameters>` 的路径 | 指向控制器 yaml | **路径里出现 `robot_description` → 所有控制器加载失败**（坑 82）|

**骨架（⚠️ 草案，别当原文抄）**：

```xml
<ros2_control name="MyRobotSystem" type="system">
  <hardware>
    <plugin>gz_ros2_control/GazeboSimSystem</plugin>     <!-- ⚠️ 写法待核对 -->
  </hardware>

  <joint name="left_wheel_joint">
    <command_interface name="velocity"/>
    <state_interface name="position"/>
    <state_interface name="velocity"/>
  </joint>
  <!-- 每个受控关节一段；mimic 从关节【只给 state】（形状 10）-->
</ros2_control>

<gazebo>
  <plugin filename="gz_ros2_control-system" name="...">   <!-- ⚠️ 两处名字待核对 -->
    <parameters>$(find my_robot)/config/ros2_control.yaml</parameters>
    <ros>                                                  <!-- use_sim_time 在这一层 -->
      <parameters>$(find my_robot)/config/ros2_control.yaml</parameters>
    </ros>
  </plugin>
</gazebo>
```

**两条硬规则**（这两条是**已知的**，不是草案）：

| # | 规则 | 依据 |
|---|---|---|
| **1** | **`<parameters>` 的路径里不能出现 `robot_description`**（子串匹配，跟长度无关）| `08` 坑 82。报错伪装成 `spawner` 的 `Failed loading controller`，真错误是 `Couldn't parse params file: '--params-file -p'`。**这就是第 31 天把包名改成 `my_robot` 的原因** |
| **2** | **mimic 关节不能有 `command_interface`** | `08` 坑 115。报 `Activated mimic joints cannot have command interfaces` |

> **`<ros2_control>` 块在 `gz sdf -p` 的输出里【看不到】是正常的** —— 它是 URDF 扩展标签，
> **`gz_ros2_control` 直接读 URDF，不经过 SDF**（第四部分末尾也提了一句）。
> **控制器 yaml 里只列主关节**（形状 10 条件 ②）。

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
| 2 | **示例是 SDF、你的模型是 URDF** —— **`<sensor>` 可搬（`<lidar>` 那层要一起搬）**；**`<plugin>` 只搬 model 级 system 插件**（diff-drive / sensors / joint-state-publisher），**世界级插件**（physics / scene-broadcaster / user-commands）**留在 `.sdf` 里**，搬进 URDF 无效甚至崩 |
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
xacro ~/ros2_ws/src/my_robot/urdf/my_robot.urdf.xacro > /tmp/my_robot.urdf    # 包名第 31 天改过（08 坑 82）
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
> **`view_frames` 怎么读**（`rate: 10000` + `most_recent_transform: 0` = 静态变换）→ `04` 顶部「更早的归档」第 25 天。
> **每次实验前先清残留进程** → `06 §3.12` 末尾 + `08` 坑 80。

> ⚠️ **改了 URDF 之后，"上一次的结果"还在原地**：
> `robot_state_publisher` 只在启动时读一次 URDF；Gazebo 里那台车也是旧的
> —— **要重启 rsp / 重新 `create`**（`10 §4.3`）。

---

# 第六部分：常见坑 → 指针

> **只列 URDF / 模型 / 控制器接入相关的** —— **每条坑的完整记录（现象 → 原因 → 解决 → 教训）在 `08-踩坑总集.md`。**

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
| **所有控制器都加载失败**，`spawner` 只说 `Failed loading controller`，真错误是 `--params-file -p` | `08` **坑 82**（`<parameters>` 路径里不能有 `robot_description`）|
| 控制器一直刷 `No clock received, using time argument instead!` | `08` **坑 114**（`/clock` 没桥接）|
| **mimic 夹爪动不了** / 从关节速度 `NaN` / 控制器起不来 | `08` **坑 115**（四条件：只给 state、`bullet-featherstone`、`limit` 留余量、保留 mimic）|
| 自己配 MoveIt2 卡在"约定"上（SRDF 的 `parent_group`、`planning_pipelines` 类型…）| `08` **坑 116**（URDF 是样子，SRDF 是给 MoveIt 的说明书）|

> **一个能扩展到使用层的补充**：`gpu_lidar` 在虚拟机上半瞎（坑 81）——
> **`export LIBGL_ALWAYS_SOFTWARE=1` 是跑传感器实验前的固定动作。**
>
> **按现象查错（不是按坑号）→ `10-原理与排查方法.md` §4.4 / §4.5。**
> **按报错原文查 → `08-踩坑总集.md` 开头的「按报错原文查」索引。**
