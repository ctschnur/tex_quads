import engine
from direct.showbase.ShowBase import ShowBase, DirectObject
from engine.tq_graphics_basics import TQGraphicsNodePath
from panda3d.core import Vec4, Vec3, NodePath, LPlanef, PlaneNode, Plane, LPlane

from simple_objects.simple_objects import Point3d

from interactive_tools.picking import CollisionPicker, PickableObjectManager

from plot_utils.quad import Quad

from interactive_tools.dragging_and_dropping_objects import DragAndDropObjectsManager
from interactive_tools.pickables import PickablePoint, PickablePointDragger
from interactive_tools.pickable_object_dragger import PickableObjectDragger

from interactive_tools.pickable_object_drawer import PanelDragDrawer

import numpy as np

from plot_utils.panel import PanelGeometry

from plot_utils.DraggableFrame import DraggableFrame

from simple_objects.primitives import Box2d

from local_utils import math_utils

class ClipperToPanel:
    """ use this to clip a nodepath to a rectangle """
    def __init__(self):
        self.clipping_planes_p3d_nodepaths = []
        self.clipped_thing_p3d_nodepath = None
        self.clipping_panel_geometry = None
        pass

    def set_clipped_thing_nodepath(self, clipped_thing_p3d_nodepath):
        """ this clipper acts on a nodepath """
        self.clipped_thing_p3d_nodepath = clipped_thing_p3d_nodepath

    def set_clipping_panel_geometry(self, clipping_panel_geometry):
        """
        args:
            clipping_panel_geometry: PanelGeometry object that specifices the geometry for the clipping """

        self.clipping_panel_geometry = clipping_panel_geometry

    def turn_clipping_planes_off(self):
        """ """
        for nodepath in self.clipping_planes_p3d_nodepaths:
            nodepath.removeNode()

        self.clipped_thing_p3d_nodepath.setClipPlaneOff()
        self.clipping_planes_p3d_nodepaths = []

    def turn_clipping_planes_on(self):
        """ the lines may extend outside of the 'frame'
            setting clipping planes are one way to prevent them from being
            rendered outside """

        self.turn_clipping_planes_off()

        for length, normal_vector in zip([self.clipping_panel_geometry.l1,
                                          self.clipping_panel_geometry.l2],
                                         [self.clipping_panel_geometry.n1,
                                          self.clipping_panel_geometry.n2]):
            d = length
            a, b, c = math_utils.p3d_to_np(normal_vector)

            plane1 = LPlanef(a, b, c, 0)
            plane1_node = PlaneNode('', plane1)
            plane1_node.setClipEffect(1)
            plane1_nodepath = NodePath(plane1_node)

            plane2 = LPlanef(-a, -b, -c, d)
            plane2_node = PlaneNode('', plane2)
            plane2_node.setClipEffect(1)
            plane2_nodepath = NodePath(plane2_node)

            plane1_nodepath.reparentTo(self.clipped_thing_p3d_nodepath)
            self.clipped_thing_p3d_nodepath.setClipPlane(plane1_nodepath)
            self.clipping_planes_p3d_nodepaths.append(plane1_nodepath)

            plane2_nodepath.reparentTo(self.clipped_thing_p3d_nodepath)
            self.clipped_thing_p3d_nodepath.setClipPlane(plane2_nodepath)
            self.clipping_planes_p3d_nodepaths.append(plane2_nodepath)


class DraggableResizableFrame(DraggableFrame):
    """ draggable and resizeable frame """
    resize_box_handle_scale = 0.05
    normal_vec_0 = Vec3(0., 1., 0.)  # text is written with the normal vector pointing out of the board; this is the standard normal vector
    up_vec_0 = Vec3(0., 0., 1.)
    height_0 = 0.9
    width_0 = 1.6
    height_min = 0.2
    width_min = height_min * 1.6
    v0_0 = Vec3(0., 0., 0.)

    def __init__(self, camera_gear, helper_graphics_active=False, **kwargs):
        """ """
        DraggableFrame.__init__(self, camera_gear, **kwargs)

        # init geometry
        self.v0 = DraggableResizableFrame.v0_0
        self.normal_vec = DraggableResizableFrame.normal_vec_0
        self.up_vec = DraggableResizableFrame.up_vec_0
        self.width = DraggableResizableFrame.width_0
        self.height = DraggableResizableFrame.height_0

        self.resize_handle_vec = np.array([1., 0., -1.])
        self.resize_handle_vec_color = Vec4(1., 1., 1., 1.)

        # make a small quad in the lower right hand corner
        self.resize_move_ctr = 0
        self.resize_box_handle = Box2d(center_it=True)
        self.resize_box_handle.reparentTo(engine.tq_graphics_basics.tq_render)
        self.resize_box_handle.setScale(DraggableResizableFrame.resize_box_handle_scale)
        self.resize_box_handle.setColor(Vec4(0., 1., 1., 1.), 1)

        self.resize_box_handle_2 = Box2d(center_it=True)
        self.resize_box_handle_2.reparentTo(engine.tq_graphics_basics.tq_render)
        self.resize_box_handle_2.setScale(DraggableResizableFrame.resize_box_handle_scale)
        self.resize_box_handle_2.setColor(Vec4(0., 0.5, 0.5, 0.5), 1)

        self.helper_graphics_active = helper_graphics_active

        # set resizing action
        self.pom.tag(self.resize_box_handle.get_p3d_nodepath())

        self.resize_b2d_dragger = PickableObjectDragger(self.resize_box_handle, self.camera_gear)
        self.resize_b2d_dragger.add_on_state_change_function(self.resize_frame_when_dragged)

        self.dadom.add_dragger(self.resize_b2d_dragger)

        # TODO: plot a DraggableResizableFrame on it's own and assign the box and
        # clipping
        self.clipper_to_panel = ClipperToPanel()
        self.clipper_to_panel.set_clipped_thing_nodepath(self.get_p3d_nodepath())

        self.clipper_to_panel.set_clipping_panel_geometry(self.get_panel_geometry())
        self.clipper_to_panel.turn_clipping_planes_on()

        if self.helper_graphics_active == True:
            self.init_helper_graphics()

        self.resize()
        self.update_window_graphics()

    def get_panel_geometry(self):
        return PanelGeometry(self.v0, self.get_right_vec_norm(), self.get_down_vec_norm(), self.width, self.height)

    def init_helper_graphics(self):
        self.v0_g = Vector()
        # self.v0_g.setTailPoint(Vec3(0., 0., 0.))
        # self.v0_g.setTipPoint(Vec3(1., 0., 1.))
        self.v0_g.reparentTo(engine.tq_graphics_basics.tq_render)
        self.v0_g.setColor(Vec4(1., 0., 0., 1.), 1)

        self.v1_g = Vector()
        # self.v1_g.setTailPoint(Vec3(0., 0., 0.))
        # self.v1_g.setTipPoint(Vec3(1., 0., 1.))
        self.v1_g.reparentTo(engine.tq_graphics_basics.tq_render)
        self.v1_g.setColor(Vec4(0., 1., 0., 1.), 1)

        self.vc_g = Vector()
        # self.vc_g.setTailPoint(Vec3(0., 0., 0.))
        # self.vc_g.setTipPoint(Vec3(1., 0., 1.))
        self.vc_g.reparentTo(engine.tq_graphics_basics.tq_render)
        self.vc_g.setColor(Vec4(1., 1., 0., 1.), 1)

        self.right_vec_g = Vector()
        # self.right_vec_g.setTailPoint(Vec3(0., 0., 0.))
        # self.right_vec_g.setTipPoint(Vec3(1., 0., 1.))
        self.right_vec_g.reparentTo(engine.tq_graphics_basics.tq_render)
        self.right_vec_g.setColor(Vec4(1., 1., 1., 1.), 1)

        self.down_vec_g = Vector()
        # self.down_vec_g.setTailPoint(Vec3(0., 0., 0.))
        # self.down_vec_g.setTipPoint(Vec3(1., 0., 1.))
        self.down_vec_g.reparentTo(engine.tq_graphics_basics.tq_render)
        self.down_vec_g.setColor(Vec4(1., 1., 1., 1.), 1)

        self.resize_handle_vec_g = Vector()  # not a global vector, but relative to
        # self.resize_handle_vec_g.setTailPoint(Vec3(0., 0., 0.))
        # self.resize_handle_vec_g.setTipPoint(Vec3(1., 0., 1.))
        self.resize_handle_vec_g.reparentTo(engine.tq_graphics_basics.tq_render)
        self.resize_handle_vec_g.setColor(self.resize_handle_vec_color, 1)

        # self.resize()
        DraggableResizableFrame.label_vector2(self.v0_g, "v0", self.camera_gear)
        DraggableResizableFrame.label_vector2(self.v1_g, "v1", self.camera_gear)
        DraggableResizableFrame.label_vector2(self.vc_g, "vc", self.camera_gear)

    def move_frame_when_dragged(self):
        self.update_logical_position_from_drag_point()

        # self.update_helper_graphics()
        self.update_window_graphics()

    def get_right_vec_norm(self):
        cross = - np.cross(math_utils.p3d_to_np(self.up_vec), math_utils.p3d_to_np(self.normal_vec)) # in standard p3d view, the normal vector (0, 1, 0) points into the screen
        norm = cross/np.linalg.norm(cross)
        return norm

    def get_right_vec(self, width=None):
        if width is None:
            width = self.width
        return self.get_right_vec_norm() * width

    def get_normal_vec(self):
        return math_utils.p3d_to_np(self.normal_vec)/np.linalg.norm(self.normal_vec)

    def get_down_vec_norm(self):
        vec = -math_utils.p3d_to_np(self.up_vec)
        norm = vec/np.linalg.norm(vec)
        return norm

    def get_down_vec(self, height=None):
        if height is None:
            height = self.height
        return self.get_down_vec_norm() * height

    def get_v0(self):
        return math_utils.p3d_to_np(self.v0)

    def get_v1(self, down_vec, right_vec):
        # placement of the resize box
        return self.get_v0() + self.get_vc(down_vec, right_vec)

    def get_vc(self, down_vec, right_vec):
        return down_vec + right_vec

    def get_box_dim_offset(self):
        right_vec = self.get_right_vec()
        down_vec = self.get_down_vec()

        return DraggableResizableFrame.resize_box_handle_scale/2 * down_vec/np.linalg.norm(down_vec) - DraggableResizableFrame.resize_box_handle_scale/2 * right_vec/np.linalg.norm(right_vec)

    def set_width(self, width):
        self.width = width
        self.update_window_graphics()

    def set_height(self, height):
        self.height = height
        self.update_window_graphics()

    def update_window_graphics(self):
        self.bg_quad.set_height(self.height)
        self.bg_quad.set_width(self.width)

        right_vec = self.get_right_vec()
        down_vec = self.get_down_vec()

        v0 = self.get_v0()
        v1 = self.get_v1(down_vec, right_vec)
        vc = v1 - v0

        DraggableFrame.setPos(self, Vec3(*v0))
        self.drag_point.setPos(Vec3(*v0))

        # print(self.width, self.height)

        self.resize_box_handle.setPos(*(v0 + vc))
        self.resize_box_handle_2.setPos(*(v0 + vc))

        if self.helper_graphics_active == True:
            self.update_helper_graphics()

        # print("self.get_panel_geometry(): ", self.get_panel_geometry())
        self.clipper_to_panel.set_clipping_panel_geometry(self.get_panel_geometry())
        self.clipper_to_panel.turn_clipping_planes_on()

    def update_helper_graphics(self):
        right_vec = self.get_right_vec()
        down_vec = self.get_down_vec()

        # self.height and self.width are in actual coordinates
        v0 = self.get_v0()
        v1 = self.get_v1(down_vec, right_vec)

        vc = v1 - v0

        # print("v0: ", v0, ", v1: ", v1, ", vc: ", vc)
        # print("self.width: ", self.width, ", self.height: ", self.height)
        # print("right_vec: ", right_vec, ", down_vec: ", down_vec)

        self.v0_g.setTailPoint(Vec3(0., 0., 0.))
        self.v0_g.setTipPoint(Vec3(*v0))

        self.v1_g.setTailPoint(Vec3(0., 0., 0.))
        self.v1_g.setTipPoint(Vec3(*v1))

        self.vc_g.setTailPoint(Vec3(*v0))
        self.vc_g.setTipPoint(Vec3(*v1))

        self.down_vec_g.setTailPoint(Vec3(*v0))
        self.down_vec_g.setTipPoint(Vec3(*(v0 + down_vec)))

        self.right_vec_g.setTailPoint(Vec3(*v0))
        self.right_vec_g.setTipPoint(Vec3(*(v0 + right_vec)))

        self.resize_handle_vec_g.setTailPoint(Vec3(*v0))
        self.resize_handle_vec_g.setTipPoint(Vec3(*(v0 + self.resize_handle_vec)))
        self.resize_handle_vec_g.setColor(self.resize_handle_vec_color, 1)

    def resize(self, handle_dragged=False):
        resize_box_handle_pos = math_utils.p3d_to_np(self.resize_box_handle.getPos())

        normal_vec = self.get_normal_vec()
        right_vec = self.get_right_vec()
        # print("right_vec", right_vec)
        down_vec = self.get_down_vec()
        # print("down_vec", down_vec)

        # self.height and self.width are in actual coordinates
        v0 = self.get_v0()
        v1 = self.get_v1(down_vec, right_vec)

        resize_to_pos = None
        if handle_dragged == True:
            resize_to_pos = math_utils.LinePlaneCollision(normal_vec, # plane normal
                                                          v0, # plane point
                                                          normal_vec, # ray direction
                                                          resize_box_handle_pos, # the position of the resize_box_handle
                                                          epsilon=1e-6)
        else:
            resize_to_pos = v1

        tmp_resize_handle_vec = resize_to_pos - v0

        down_vec_normalized = down_vec / np.linalg.norm(down_vec)
        right_vec_normalized = right_vec / np.linalg.norm(right_vec)

        new_height = np.dot(down_vec_normalized, tmp_resize_handle_vec)
        new_width = np.dot(right_vec_normalized, tmp_resize_handle_vec)

        self.width, self.height = DraggableResizableFrame.clamp_width_height(new_width, new_height)

        # print("new_height", new_height, ", new_width", new_width)
        self.update_window_graphics()

    @staticmethod
    def clamp_width_height(width, height):
        right_width = DraggableResizableFrame.width_min
        right_height = DraggableResizableFrame.height_min

        if height >= DraggableResizableFrame.height_min:
            right_height = height

        if width >= DraggableResizableFrame.width_min:
            right_width = width

        return right_width, right_height

    def resize_frame_when_dragged(self):
        # print("resizing", self.resize_move_ctr)
        self.resize_move_ctr += 1
        self.resize(handle_dragged=True)

    def setPos(self, *args, **kwargs):
        """ """
        # DraggableFrame.setPos(self, *args, **kwargs)
        # self.drag_point.setPos(*args, **kwargs)


        self.v0 = np.array(*args)  # logical
        self.update_window_graphics()  # for this to work, the logical v0 has to be set

        self.move_frame_when_dragged()


    @staticmethod
    def label_vector(vec, text, camera_gear):
            # label the vector
            text_kwargs = dict(
                text=text
                # text="{:.1e}".format(c_num),
                # alignment=None
                )

            from simple_objects.text import BasicOrientedText

            label = BasicOrientedText(
                camera_gear,
                update_orientation_on_camera_rotate=True,
                **text_kwargs
                )

            label.reparentTo(vec)

            height = engine.tq_graphics_basics.get_pts_to_p3d_units(label.pointsize)
            width = (label.textNode.getWidth()/label.textNode.getHeight()) * height

            # pos = vec.getTipPoint()
            # label.setPos(pos)

            pos = Vec3(width*3/4, 0., -height)
            label.setPos(pos)
            vec.set_label(label, set_to_tip=True)

    @staticmethod
    def label_vector2(vec, text, camera_gear):
        label = BasicOrientedText(camera_gear, update_orientation_on_camera_rotate=True, text=text)
        label.reparentTo(vec)
        vec.set_label(label, set_to="tip")

    def switch_clip_on(self):
        """ """
        right_vec_normal = self.get_right_vec()
        down_vec_normal = self.get_down_vec()
        pass

    def switch_clip_off(self):
        """ """
        pass

