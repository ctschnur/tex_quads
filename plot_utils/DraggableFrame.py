import engine
from direct.showbase.ShowBase import ShowBase, DirectObject
from engine.tq_graphics_basics import TQGraphicsNodePath
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3, PlaneNode, Plane, LPlanef

from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle, TextureOf2dImageData

from simple_objects.primitives import IndicatorPrimitive, Box2dCentered, ConePrimitive, Box2d

from interactive_tools.picking import CollisionPicker, PickableObjectManager

from plot_utils.quad import Quad

from interactive_tools.dragging_and_dropping_objects import DragAndDropObjectsManager
from interactive_tools.pickables import PickablePoint, PickablePointDragger
from interactive_tools.pickable_object_dragger import PickableObjectDragger

from interactive_tools.pickable_object_drawer import PanelDragDrawer

from local_utils import math_utils

from local_utils.math_utils import Panel

from composed_objects.composed_objects import ParallelLines, GroupNode, Vector

from simple_objects.text import BasicOrientedText
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


class DRFrame(DraggableFrame):
    """ draggable and resizeable frame """
    resize_box_handle_scale = 0.05
    normal_vec_0 = Vec3(0., 1., 0.)  # text is written with the normal vector pointing out of the board; this is the standard normal vector
    up_vec_0 = Vec3(0., 0., 1.)
    height_0 = 0.9
    width_0 = 1.6
    height_min = 0.2
    width_min = height_min * 1.6

    def __init__(self, camera_gear, helper_graphics_active=False, **kwargs):
        """ """
        DraggableFrame.__init__(self, camera_gear, **kwargs)

        # init geometry
        self.v0 = Vec3(0., 0., 0.)
        self.normal_vec = DRFrame.normal_vec_0
        self.up_vec = DRFrame.up_vec_0
        self.width = DRFrame.width_0
        self.height = DRFrame.height_0

        self.resize_handle_vec = np.array([1., 0., -1.])
        self.resize_handle_vec_color = Vec4(1., 1., 1., 1.)

        # make a small quad in the lower right hand corner
        self.resize_move_ctr = 0
        self.resize_box_handle = Box2d(center_it=True)
        self.resize_box_handle.reparentTo(engine.tq_graphics_basics.tq_render)
        self.resize_box_handle.setScale(DRFrame.resize_box_handle_scale)
        self.resize_box_handle.setColor(Vec4(0., 1., 1., 1.), 1)

        self.resize_box_handle_2 = Box2d(center_it=True)
        self.resize_box_handle_2.reparentTo(engine.tq_graphics_basics.tq_render)
        self.resize_box_handle_2.setScale(DRFrame.resize_box_handle_scale)
        self.resize_box_handle_2.setColor(Vec4(0., 0.5, 0.5, 0.5), 1)

        self.helper_graphics_active = helper_graphics_active

        # set resizing action
        self.pom.tag(self.resize_box_handle.get_p3d_nodepath())

        self.resize_b2d_dragger = PickableObjectDragger(self.resize_box_handle, self.camera_gear)
        self.resize_b2d_dragger.add_on_state_change_function(self.resize_frame_when_dragged)

        self.dadom.add_dragger(self.resize_b2d_dragger)

        if self.helper_graphics_active == True:
            self.init_helper_graphics()

        self.resize()
        self.update_window_graphics()

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
        DRFrame.label_vector2(self.v0_g, "v0", self.camera_gear)
        DRFrame.label_vector2(self.v1_g, "v1", self.camera_gear)
        DRFrame.label_vector2(self.vc_g, "vc", self.camera_gear)

    def move_frame_when_dragged(self):
        new_handle_pos = self.drag_point.getPos()
        self.v0 = new_handle_pos

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

        return DRFrame.resize_box_handle_scale/2 * down_vec/np.linalg.norm(down_vec) - DRFrame.resize_box_handle_scale/2 * right_vec/np.linalg.norm(right_vec)

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

        self.width, self.height = DRFrame.clamp_width_height(new_width, new_height)

        # print("new_height", new_height, ", new_width", new_width)
        self.update_window_graphics()

    @staticmethod
    def clamp_width_height(width, height):
        right_width = DRFrame.width_min
        right_height = DRFrame.height_min

        if height >= DRFrame.height_min:
            right_height = height

        if width >= DRFrame.width_min:
            right_width = width

        return right_width, right_height

    def resize_frame_when_dragged(self):
        # print("resizing", self.resize_move_ctr)
        self.resize_move_ctr += 1
        self.resize(handle_dragged=True)

    def setPos(self, *args, **kwargs):
        """ """
        DraggableFrame.setPos(self, *args, **kwargs)
        self.drag_point.setPos(*args, **kwargs)
        self.update_window_graphics()

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


class DRDrawFrame(DRFrame):
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
        DRFrame.__init__(self, *args, **kwargs)

        self.pom.tag(self.bg_quad.get_p3d_nodepath())

        # self.v0 = Vec3(0., 0., 0.)
        # self.normal_vec = DRFrame.normal_vec_0
        # self.up_vec = DRFrame.up_vec_0
        # self.width = DRFrame.width_0
        # self.height = DRFrame.height_0

        self.panel_drag_drawer = PanelDragDrawer(self.bg_quad, self.camera_gear, self.get_panel())
        # self.panel_drag_drawer.add_on_state_change_function(self.refresh_panel)

        self.dadom.add_dragger(self.panel_drag_drawer)

        self.draw_parent_node = TQGraphicsNodePath()
        self.draw_parent_node.reparentTo(self.bg_quad)

        self.draw_point = Point3d()
        self.draw_point.reparentTo(engine.tq_graphics_basics.tq_render)
        self.draw_point.setColor(Vec4(1, 0.5, 1., 1.), 1)

        self.change_ctr = 0

    def get_panel(self):
        return Panel(self.v0, self.get_right_vec_norm(), self.get_down_vec_norm(), self.width, self.height)

    def move_frame_when_dragged(self):
        self.panel_drag_drawer.set_panel(self.get_panel())
        DRFrame.move_frame_when_dragged(self)
        # print("custom move_frame_when_dragged: ", )

    def resize_frame_when_dragged(self):
        self.panel_drag_drawer.set_panel(self.get_panel())
        DRFrame.resize_frame_when_dragged(self)
        # print("custom resize_frame_when_dragged: ", )

    # def draw_pick(self):
    #     # new_handle_pos = self.drag_point.getPos()
    #     # self.v0 = new_handle_pos

    #     # # self.update_helper_graphics()
    #     # self.update_window_graphics()

    #     self.change_ctr += 1

    #     print("picked, self.change_ctr: ", self.change_ctr)

    #     self.draw_point.setPos(Vec3(1., 1., 0.))
