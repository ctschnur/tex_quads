from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle, TextureOf2dImageData

from interactive_tools.picking import CollisionPicker, PickableObjectManager

from plot_utils.quad import Quad

from interactive_tools.dragging_and_dropping_objects import DragAndDropObjectsManager
from interactive_tools.pickables import PickablePoint, PickablePointDragger
from interactive_tools.pickable_object_dragger import PickableObjectDragger

class DraggableFrame(TQGraphicsNodePath):
    """ """
    def __init__(self, camera_gear, **kwargs):
        """ """
        TQGraphicsNodePath.__init__(self, **kwargs)

        self.camera_gear = camera_gear
        self.point3d = Point3d()

        self.quad = Quad(thickness=1.5)
        self.quad.set_height(0.25)
        self.quad.set_width(0.25)

        self.quad.reparentTo(self)
        self.point3d.reparentTo(self)
        self.point3d.setPos(Vec3(0., 0., 0.))

        # -------------------------------------

        self.pom = PickableObjectManager()
        self.pom.tag(self.point3d.get_p3d_nodepath())

        self.dadom = DragAndDropObjectsManager()

        self.pt_dragger = PickableObjectDragger(self.point3d, self.camera_gear)
        self.pt_dragger.add_on_state_change_function(self.move_frame_when_dragged)

        self.dadom.add_dragger(self.pt_dragger)

        self.collisionPicker = CollisionPicker(
            camera_gear, engine.tq_graphics_basics.tq_render,
            base.mouseWatcherNode, self.dadom)

        # -- add a mouse task to check for picking
        self.p3d_direct_object = DirectObject.DirectObject()
        self.p3d_direct_object.accept(
            'mouse1', self.collisionPicker.onMouseTask)

    def move_frame_when_dragged(self):
        new_handle_pos = self.point3d.getPos()
        self.quad.setPos(new_handle_pos)
