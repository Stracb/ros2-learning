#!/usr/bin/env python3
"""自己写的数值逆解（雅可比迭代），用来和 MoveIt 的 IK 对比。"""
import numpy as np
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Pose
from moveit_msgs.srv import GetPositionFK, GetPositionIK

# Panda 的关节限位（弧度）
JMIN = np.array([-2.8973, -1.7628, -2.8973, -3.0718, -2.8973, -0.0175, -2.8973])
JMAX = np.array([ 2.8973,  1.7628,  2.8973, -0.0698,  2.8973,  3.7525,  2.8973])
JNAMES = ['panda_joint%d' % i for i in range(1, 8)]
READY = np.array([0.0, -0.785, 0.0, -2.356, 0.0, 1.571, 0.785])


def quat_to_R(x, y, z, w):
    return np.array([
        [1-2*(y*y+z*z),  2*(x*y-z*w),    2*(x*z+y*w)],
        [2*(x*y+z*w),    1-2*(x*x+z*z),  2*(y*z-x*w)],
        [2*(x*z-y*w),    2*(y*z+x*w),    1-2*(x*x+y*y)],
    ])


def R_to_rotvec(R):
    """旋转矩阵 -> 旋转向量（小角度近似，稳定无除零）"""
    return 0.5 * np.array([R[2, 1] - R[1, 2],
                           R[0, 2] - R[2, 0],
                           R[1, 0] - R[0, 1]])


class NumIK(Node):
    def __init__(self):
        super().__init__('num_ik')
        self.fk_cli = self.create_client(GetPositionFK, 'compute_fk')
        self.mv_cli = self.create_client(GetPositionIK, 'compute_ik')
        assert self.fk_cli.wait_for_service(timeout_sec=5.0), 'compute_fk 没起来'
        assert self.mv_cli.wait_for_service(timeout_sec=5.0), 'compute_ik 没起来'
        self.n_fk = 0

    def fk(self, q):
        """正运动学：7 个关节角 -> (位置, 四元数)"""
        req = GetPositionFK.Request()
        req.header.frame_id = 'panda_link0'
        req.fk_link_names = ['panda_link8']
        req.robot_state.joint_state.name = JNAMES
        req.robot_state.joint_state.position = [float(v) for v in q]
        fut = self.fk_cli.call_async(req)
        rclpy.spin_until_future_complete(self, fut)
        self.n_fk += 1
        ps = fut.result().pose_stamped[0].pose
        p = np.array([ps.position.x, ps.position.y, ps.position.z])
        quat = np.array([ps.orientation.x, ps.orientation.y,
                         ps.orientation.z, ps.orientation.w])
        return p, quat

    def jacobian(self, q, eps=1e-4):
        """数值微分：每个关节扰动 eps，看末端怎么变"""
        p0, q0 = self.fk(q)
        R0 = quat_to_R(*q0)
        J = np.zeros((6, 7))
        for i in range(7):
            q2 = q.copy(); q2[i] += eps
            p1, q1 = self.fk(q2)
            J[:3, i] = (p1 - p0) / eps
            J[3:, i] = R_to_rotvec(quat_to_R(*q1) @ R0.T) / eps
        return J

    def ik(self, target_p, target_quat, q0, iters=100, tol=1e-4, step=0.5, verbose=False):
        q = np.array(q0, float)
        R_tgt = quat_to_R(*target_quat)
        err_norm = 1e9
        for k in range(iters):
            p, quat = self.fk(q)
            R_cur = quat_to_R(*quat)
            err = np.concatenate([target_p - p, R_to_rotvec(R_tgt @ R_cur.T)])
            err_norm = np.linalg.norm(err)
            if verbose and k % 10 == 0:
                print('   iter %3d  |err| = %.6f' % (k, err_norm))
            if err_norm < tol:
                return q, k, err_norm
            J = self.jacobian(q)
            dq = step * (np.linalg.pinv(J) @ err)      # ← 核心
            q = np.clip(q + dq, JMIN, JMAX)            # 夹限位
        return q, iters, err_norm

    def moveit_ik(self, target_p, target_quat):
        req = GetPositionIK.Request()
        r = req.ik_request
        r.group_name = 'panda_arm'
        r.pose_stamped.header.frame_id = 'panda_link0'
        r.pose_stamped.pose.position.x = float(target_p[0])
        r.pose_stamped.pose.position.y = float(target_p[1])
        r.pose_stamped.pose.position.z = float(target_p[2])
        r.pose_stamped.pose.orientation.x = float(target_quat[0])
        r.pose_stamped.pose.orientation.y = float(target_quat[1])
        r.pose_stamped.pose.orientation.z = float(target_quat[2])
        r.pose_stamped.pose.orientation.w = float(target_quat[3])
        r.robot_state.joint_state.name = JNAMES
        r.robot_state.joint_state.position = [float(v) for v in READY]
        r.avoid_collisions = False
        fut = self.mv_cli.call_async(req)
        rclpy.spin_until_future_complete(self, fut)
        res = fut.result()
        if res.error_code.val != 1:
            return None
        return np.array(res.solution.joint_state.position[:7])



def batch_test(n, target_quat):
    """在 (0.3~0.6, -0.2~0.2, 0.3~0.6) 的 3x3x3 网格上测 IK 成功率"""
    import itertools
    xs = np.linspace(0.30, 0.60, 3)
    ys = np.linspace(-0.20, 0.20, 3)
    zs = np.linspace(0.30, 0.60, 3)
    ok, fails, iters, errs = 0, [], [], []
    total = 0
    for x, y, z in itertools.product(xs, ys, zs):
        total += 1
        p = np.array([x, y, z])
        q, k, err = n.ik(p, target_quat, READY, iters=100)
        if err < 1e-3:
            ok += 1
            iters.append(k)
            errs.append(err)
        else:
            fails.append((x, y, z, err))
    print('\n===== 批量测试 =====')
    print('目标点总数 : %d' % total)
    print('成功       : %d  (%.0f%%)' % (ok, 100.0 * ok / total))
    if iters:
        print('平均迭代   : %.1f 次' % np.mean(iters))
        print('平均末端误差: %.6f m  (%.3f mm)' % (np.mean(errs), np.mean(errs) * 1000))
        print('最大末端误差: %.6f m' % np.max(errs))
    if fails:
        print('失败的点   :')
        for x, y, z, e in fails:
            print('   (%.2f, %.2f, %.2f)  err=%.4f' % (x, y, z, e))
    print('FK 调用次数 :', n.n_fk)


def main():
    rclpy.init()
    n = NumIK()
    target_quat = np.array([0.0, 1.0, 0.0, 0.0])   # 手朝下（对比用）
    import sys
    if '--batch' in sys.argv:
        batch_test(n, target_quat)
        n.destroy_node(); rclpy.shutdown(); return

    print('目标位置:', target_p, ' 姿态: w=1')
    print('初值(ready):', np.round(READY, 3))

    q, k, err = n.ik(target_p, target_quat, READY, verbose=True)
    print('\n我的解   :', np.round(q, 3))
    print('迭代次数 :', k, '  末端误差: %.6f' % err)

    fk_p, fk_q = n.fk(q)
    print('FK 验证  :', np.round(fk_p, 4), '  误差: %.5f m' % np.linalg.norm(fk_p - target_p))

    qm = n.moveit_ik(target_p, target_quat)
    if qm is not None:
        print('\nMoveIt 解:', np.round(qm, 3))
        print('两者关节角差(范数): %.4f' % np.linalg.norm(q - qm))
    print('\nFK 调用次数:', n.n_fk)

    n.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
