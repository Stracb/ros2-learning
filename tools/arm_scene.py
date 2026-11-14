import sys
import rclpy
from rclpy.node import Node
from moveit_msgs.srv import ApplyPlanningScene
from moveit_msgs.msg import PlanningScene, CollisionObject
from shape_msgs.msg import SolidPrimitive
from geometry_msgs.msg import Pose

class Scene(Node):
    def __init__(self):
        super().__init__('scene_client')
        self.cli = self.create_client(ApplyPlanningScene, 'apply_planning_scene')
        if not self.cli.wait_for_service(timeout_sec=5.0):
            sys.exit('apply_planning_scene 没起来')

    def add_box(self, x, y, z, size=0.05, name='target_box'):
        co = CollisionObject()
        co.header.frame_id = 'panda_link0'
        co.id = name
        prim = SolidPrimitive()
        prim.type = SolidPrimitive.BOX
        prim.dimensions = [size, size, size]
        pose = Pose()
        pose.position.x = x
        pose.position.y = y
        pose.position.z = z
        pose.orientation.w = 1.0
        co.primitives.append(prim)
        co.primitive_poses.append(pose)
        co.operation = CollisionObject.ADD

        scene = PlanningScene()
        scene.is_diff = True
        scene.world.collision_objects.append(co)

        req = ApplyPlanningScene.Request()
        req.scene = scene
        fut = self.cli.call_async(req)
        rclpy.spin_until_future_complete(self, fut)
        ok = fut.result().success
        print('盒子 %s @ (%.2f, %.2f, %.2f) 边长 %.2f m  -> %s'
              % (name, x, y, z, size, 'OK' if ok else 'FAIL'))
        return ok

def main():
    rclpy.init()
    n = Scene()
    n.add_box(0.40, 0.0, 0.30)
    n.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
