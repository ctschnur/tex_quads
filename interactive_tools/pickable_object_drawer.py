from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3

from simple_objects.simple_objects import Line2dObject, PointPrimitive, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, Point3d

from interactive_tools.event_managers import DragDropEventManager

from local_utils import math_utils

from local_utils.math_utils import Panel

import numpy as np

from conventions import conventions
import engine

class PanelDragDrawer(DragDropEventManager):
    """ Inspired by PickableObjectDragger """
    def __init__(self, object_to_draw_on, camera_gear, panel):
        """ """
        self.object_to_draw_on = object_to_draw_on
        self.camera_gear = camera_gear

        # # FIXME: figure out a better way than passing the nodepath in here
        self._dragger_nodepath_handle = object_to_draw_on.get_p3d_nodepath()
        # # this should only be used after the picking event and when the draggers are searched for the nodepath that was picked

        self.last_frame_drag_drawing_pos = None

        DragDropEventManager.__init__(self)

        self.panel = panel

        self.last_mouse_pos = None
        self.current_mouse_pos = self.mouse_position_before_dragging

        self.add_on_state_change_function(self.update)

        self.strokes = []  # list of np.arrays with x an y coordinates of the stroke points
        self.current_stroke = None

    def set_panel(self, panel):
        self.panel = panel
        print("set panel: ", self.panel)

    def get_tq_nodepath_handle_for_dragger(self):
        """ """
        return self._dragger_nodepath_handle

    def init_dragging(self):
        """ save original position """
        DragDropEventManager.init_dragging(self)

    def update(self):
        """ """
        mouse_pos = base.mouseWatcherNode.getMouse()
        mouse_p_x, mouse_p_y = conventions.getFilmCoordsFromMouseCoords(mouse_pos[0], mouse_pos[1]  # , self.p_xy_at_init_drag[0], self.p_xy_at_init_drag[1]
        )

        # print("self.p_xy_at_init_drag: ", self.p_xy_at_init_drag)
        # print("mouse_p_x, mouse_p_y: ", mouse_p_x, mouse_p_y)

        cam_pos = self.camera_gear.get_cam_pos()

        # print("cam_pos: ", cam_pos)

        r0_shoot = (cam_pos +  # camera position
                    self.camera_gear.get_e_x_prime() * mouse_p_x + self.camera_gear.get_e_y_prime() * mouse_p_y  # camera plane
                    )

        # print("self.camera_gear.get_e_y_prime(): ", self.camera_gear.get_e_y_prime())
        # print("self.camera_gear.get_e_x_prime(): ", self.camera_gear.get_e_x_prime())


        print("r0_shoot: ", r0_shoot)

        # print("self.panel.get_plane_normal_vector(): ", self.panel.get_plane_normal_vector())

        r_strike = math_utils.LinePlaneCollision(self.panel.get_plane_normal_vector(), self.panel.r0, self.camera_gear.get_cam_forward_normal_vector(), r0_shoot)

        print("self.camera_gear.get_cam_forward_normal_vector():, ", self.camera_gear.get_cam_forward_normal_vector())

        print("r_strike: ", r_strike)


        in_plane_vec = r_strike - self.panel.r0

        self.last_x1_strike = np.dot(self.panel.n1, in_plane_vec)
        # assert x1_strike >= 0.

        self.last_x2_strike = np.dot(self.panel.n2, in_plane_vec)
        # assert x2_strike >= 0.
        # print("x1_strike, x2_strike: ", x1_strike, x2_strike)





    def on_mouse_pos_changed(self):
        print("on_mouse_pos_changed")

    def end_dragging(self):
        """ """
        self.position_of_drawn_on_object = None

        DragDropEventManager.remove_on_state_change_function(self, self.update)

        DragDropEventManager.end_dragging(self)
