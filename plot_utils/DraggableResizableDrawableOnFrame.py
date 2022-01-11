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

        panel_graphics = PanelGraphics()
        panel_graphics.reparentTo(self)

        self.panel_drag_drawer = PanelDragDrawer(self.bg_quad, self.camera_gear, self.get_panel_geometry(), panel_graphics)
        self.dadom.add_dragger(self.panel_drag_drawer)

        self.change_ctr = 0

    def move_frame_when_dragged(self):
        self.update_logical_position_from_drag_point()
        self.panel_drag_drawer.set_panel_geometry(self.get_panel_geometry())
        self.update_window_graphics()

    def resize_frame_when_dragged(self):
        self.panel_drag_drawer.set_panel_geometry(self.get_panel_geometry())
        DraggableResizableFrame.resize_frame_when_dragged(self)
