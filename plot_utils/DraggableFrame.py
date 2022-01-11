import engine
from direct.showbase.ShowBase import ShowBase, DirectObject
from engine.tq_graphics_basics import TQGraphicsNodePath
from panda3d.core import Vec4, Vec3

from simple_objects.simple_objects import Point3d

from interactive_tools.picking import CollisionPicker, PickableObjectManager

from plot_utils.quad import Quad

from interactive_tools.dragging_and_dropping_objects import DragAndDropObjectsManager
from interactive_tools.pickables import PickablePoint, PickablePointDragger
from interactive_tools.pickable_object_dragger import PickableObjectDragger

from interactive_tools.pickable_object_drawer import PanelDragDrawer

import numpy as np

class DraggableFrame(TQGraphicsNodePath):
    """ """
    def __init__(self, camera_gear, height=None, width=None, **kwargs):
        """ """
        height_0 = 0.5
        width_0 = 16/9*height_0

        TQGraphicsNodePath.__init__(self, **kwargs)

        self.camera_gear = camera_gear
        self.drag_point = Point3d()
        self.drag_point.reparentTo(engine.tq_graphics_basics.tq_render)
        self.drag_point.setColor(Vec4(1.0, 0., 0., 1.), 1)

        self.bg_quad = Quad(thickness=1.5)

        if height is None:
            height = height_0

        if width is None:
            width = width_0

        self.bg_quad.set_height(height)
        self.bg_quad.set_width(width)
        self.bg_quad.reparentTo(self)
        self.bg_quad.setPos(Vec3(0., 0., 0.))
        self.bg_quad.setColor(Vec4(1., 1., 1., 0.5), 1)

        # -------------------------------------
        self.pom = PickableObjectManager()
        self.pom.tag(self.drag_point.get_p3d_nodepath())

        self.dadom = DragAndDropObjectsManager()

        self.pt_dragger = PickableObjectDragger(self.drag_point, self.camera_gear)
        self.pt_dragger.add_on_state_change_function(self.move_frame_when_dragged)

        self.dadom.add_dragger(self.pt_dragger)

        self.collisionPicker = CollisionPicker(
            camera_gear, engine.tq_graphics_basics.tq_render,
            base.mouseWatcherNode, self.dadom)

        # -- add a mouse task to check for picking
        self.p3d_draw_direct_object = DirectObject.DirectObject()
        self.p3d_draw_direct_object.accept(
            'mouse1', self.collisionPicker.onMouseTask)

    def update_logical_position_from_drag_point(self):
        new_handle_pos = self.drag_point.getPos()
        self.v0 = new_handle_pos
