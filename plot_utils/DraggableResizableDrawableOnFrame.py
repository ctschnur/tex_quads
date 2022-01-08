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

from plot_utils.panel import PanelGeometry, PanelGraphics

from plot_utils.DraggableFrame import DraggableFrame

from plot_utils.DraggableResizableFrame import DraggableResizableFrame

class DraggableResizableDrawableOnFrame(DraggableResizableFrame):
    """ draggable, resizable and drawable-on frame
        1) make the background quad pickable
        2) draw LINE Strips interactively
          i) draw point3d's at the intersection point of pen and quad
          ii) every time the mouse moves during drawing, update the drawing
        3) eradicate diseases:
          i) prevent from drawing when the frame isn't focused (i.e. if the normal vector isn't antiparallel to the camera's lookat vector)
          ii) prevent from drawing if you hit the frame from behind (essentially the same as (i))

    """
    def __init__(self, *args, **kwargs):
        """ """
        DraggableResizableFrame.__init__(self, *args, **kwargs)

        self.pom.tag(self.bg_quad.get_p3d_nodepath())

        # self.v0 = Vec3(0., 0., 0.)
        # self.normal_vec = DraggableResizableFrame.normal_vec_0
        # self.up_vec = DraggableResizableFrame.up_vec_0
        # self.width = DraggableResizableFrame.width_0
        # self.height = DraggableResizableFrame.height_0


        panel_graphics = PanelGraphics()
        panel_graphics.reparentTo(self)

        self.panel_drag_drawer = PanelDragDrawer(self.bg_quad, self.camera_gear, self.get_panel_geometry(), panel_graphics)
        # self.panel_drag_drawer.add_on_state_change_function(self.refresh_panel)

        self.dadom.add_dragger(self.panel_drag_drawer)

        self.draw_parent_node = TQGraphicsNodePath()
        self.draw_parent_node.reparentTo(self.bg_quad)

        self.draw_point = Point3d()
        self.draw_point.reparentTo(engine.tq_graphics_basics.tq_render)
        self.draw_point.setColor(Vec4(1, 0.5, 1., 1.), 1)

        self.change_ctr = 0

    def move_frame_when_dragged(self):
        self.panel_drag_drawer.set_panel_geometry(self.get_panel_geometry())
        DraggableResizableFrame.move_frame_when_dragged(self)
        # print("custom move_frame_when_dragged: ", )

    def resize_frame_when_dragged(self):
        self.panel_drag_drawer.set_panel_geometry(self.get_panel_geometry())
        DraggableResizableFrame.resize_frame_when_dragged(self)
        # print("custom resize_frame_when_dragged: ", )

    # def draw_pick(self):
    #     # new_handle_pos = self.drag_point.getPos()
    #     # self.v0 = new_handle_pos

    #     # # self.update_helper_graphics()
    #     # self.update_window_graphics()

    #     self.change_ctr += 1

    #     print("picked, self.change_ctr: ", self.change_ctr)

    #     self.draw_point.setPos(Vec3(1., 1., 0.))
