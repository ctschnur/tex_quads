from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3

from simple_objects.simple_objects import Line2dObject, PointPrimitive, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, Point3d

from simple_objects import primitives

from plot_utils.colors.colors import get_color

from interactive_tools.event_managers import DragDropEventManager

from local_utils import math_utils

# from local_utils.math_utils import Panel

# from plot_utils.DraggableFrame import Panel

import numpy as np

from engine.tq_graphics_basics import TQGraphicsNodePath

from conventions import conventions
import engine

class PanelDragDrawer(DragDropEventManager):
    """ Inspired by PickableObjectDragger """
    def __init__(self, object_for_dragger, camera_gear, panel_geometry, panel_graphics):
        """ """
        self.object_for_dragger = object_for_dragger
        self.camera_gear = camera_gear
        self.panel_graphics = panel_graphics  # object to attach the drawn geometry to

        # # FIXME: figure out a better way than passing the nodepath in here
        self._dragger_nodepath_handle = object_for_dragger.get_p3d_nodepath()
        # # this should only be used after the picking event and when the draggers are searched for the nodepath that was picked

        self.panel_geometry = panel_geometry
        self.current_line = None

        DragDropEventManager.__init__(self)
        self.add_on_state_change_function(self.update)

    def set_panel_geometry(self, panel_geometry):
        self.panel_geometry = panel_geometry
        # print("set panel_geometry: ", self.panel_geometry)

    def get_tq_nodepath_handle_for_dragger(self):
        """ """
        return self._dragger_nodepath_handle

    def init_dragging(self):
        """ save original position """

        print("######## init drag drawing")

        # init stroke graphics
        self.current_line = primitives.SegmentedLinePrimitive(color=get_color("blue"), thickness=2)

        coords_2d = np.array([self.getCoords2dForStroke()])
        coords_3d = self.convertPanel2dTo3dCoords(coords_2d)

        self.current_line.extendCoords(coords_3d)
        self.current_line.reparentTo(self.panel_graphics)

        DragDropEventManager.init_dragging(self)

    def update(self):
        """ """
        if self.current_line is None:
            print("-------- hey")
            self.init_dragging()
        else:
            coords_2d = np.array([self.getCoords2dForStroke()])
            coords_3d = self.convertPanel2dTo3dCoords(coords_2d)

            # coord_3d_now = coords_3d[0]

            parent_p3d_node = self.current_line.getParent_p3d()

            self.current_line.extendCoords(coords_3d)
            self.current_line.reparentTo(self.panel_graphics)

            # if np.any(self.current_line.coords[-1] != coords_3d_now):  # new coordinate
            #     self.current_line.setCoords(self.current_line.getCoords_np())
            #     print("new coordinate")
            # else:
            #     print("no new coordinate")


    def convertPanel2dTo3dCoords(self, coords_2d):
        """
        args:
            coords_2d: np.array([[1,2],
                                 [3,4],
                                 ...  ]), i.e. the effective x, y coordinates
        returns:
            coords_3d: np.array([[1, 0, 2],
                                 [3, 0, 4],
                                 ...      ]), i.e. the actual x, y, z coordinates """

        return np.c_[coords_2d[:,0], np.zeros(np.shape(coords_2d)[0]), -coords_2d[:,1]]


    def getCoords2dForStroke(self):
        """ mouse_pos as returned from base.mouseWatcherNode.getMouse() """
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

        # print("r0_shoot: ", r0_shoot)
        # print("self.panel_geometry.get_plane_normal_vector(): ", self.panel_geometry.get_plane_normal_vector())
        r_strike = math_utils.LinePlaneCollision(self.panel_geometry.get_plane_normal_vector(), self.panel_geometry.r0, self.camera_gear.get_cam_forward_vector_normalized(), r0_shoot)

        # print("self.camera_gear.get_cam_forward_vector_normalized():, ", self.camera_gear.get_cam_forward_vector_normalized())
        # print("r_strike: ", r_strike)

        in_plane_vec = r_strike - self.panel_geometry.r0


        x1_strike = np.dot(self.panel_geometry.n1, in_plane_vec)
        x2_strike = np.dot(self.panel_geometry.n2, in_plane_vec)

        # print("x1_strike, x2_strike: ", x1_strike, x2_strike)
        return np.array([x1_strike, x2_strike])

    # def cleanup_after_dragging(self):
    #     print("#-#-#-#-#-#-#-#-# cleanup")
    #     self.current_line = None
    #     # self.strokes_in_2d_panel.lines.append(sl)
    #     # DragDropEventManager.remove_on_state_change_function(self, self.update)

    def end_dragging(self):
        self.current_line = None
        print("####### end drag drawing")
        DragDropEventManager.end_dragging(self)




class PanelDragDrawer2dLines(PanelDragDrawer):
    """ """
    def __init__(self, *args, **kwargs):
        PanelDragDrawer.__init__(self, *args, **kwargs)

    def init_dragging(self):
        """ save original position """

        # print("######## init drag drawing")

        # init stroke graphics
        # self.current_line = primitives.SegmentedLinePrimitive(color=get_color("blue"), thickness=2)
        # self.current_line = primitives.SegmentedSmooth2dLinePrimitive(color=get_color("blue"), thickness=2)

        self.current_line = primitives.Stroke2d()

        # s2d2.add_point((0., 0.))

        coords_2d = np.array([self.getCoords2dForStroke()])
        coords_3d = self.convertPanel2dTo3dCoords(coords_2d)

        self.current_line.extendCoords(coords_3d)
        self.current_line.reparentTo(self.panel_graphics)

        DragDropEventManager.init_dragging(self)
