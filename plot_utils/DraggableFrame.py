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

from local_utils import math_utils

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

        self.quad = Quad(thickness=1.5)

        if height is None:
            height = height_0

        if width is None:
            width = width_0

        self.quad.set_height(height)
        self.quad.set_width(width)
        self.quad.reparentTo(self)
        self.quad.setPos(Vec3(0., 0., 0.))

        self.drag_point.reparentTo(engine.tq_graphics_basics.tq_render)
        # self.drag_point.reparentTo(self)
        # self.drag_point.setPos(self.getPos() # + self.quad.left.getTailPoint()
        # )

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
        self.p3d_direct_object = DirectObject.DirectObject()
        self.p3d_direct_object.accept(
            'mouse1', self.collisionPicker.onMouseTask)

        self.drag_point.setColor(1.0, 0., 0)
        self.quad.setColor(Vec4(1., 1., 1., 0.5), 1)

    # def set_width(self, width):
    #     self.quad.set_width(width)

    # def set_height(self, height):
    #     self.quad.set_height(height)

class DRFrame(DraggableFrame):
    """ """
    resize_box_handle_scale = 0.05
    normal_vec_0 = Vec3(0., 1., 0.)  # text is written with the normal vector pointing out of the board; this is the standard normal vector
    up_vec_0 = Vec3(0., 0., 1.)
    height_0 = 0.9
    width_0 = 1.6

    def __init__(self, camera_gear, **kwargs):
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

        # set resizing action
        self.pom.tag(self.resize_box_handle.get_p3d_nodepath())

        self.resize_b2d_dragger = PickableObjectDragger(self.resize_box_handle, self.camera_gear)
        self.resize_b2d_dragger.add_on_state_change_function(self.resize_frame_when_dragged)

        self.dadom.add_dragger(self.resize_b2d_dragger)

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
        return -math_utils.p3d_to_np(self.normal_vec)/np.linalg.norm(self.normal_vec)

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
        # # plane: one vector pointing 'right' (up_vec x normal_vec) and one down (-up_vec)
        # # point: 'upper left'
        # right_vec = self.get_right_vec()
        # down_vec = self.get_down_vec()

        # # self.height and self.width are in actual coordinates
        # v0 = self.get_v0()
        # v1 = self.get_v1(down_vec, right_vec)
        # box_dim_offset = self.get_box_dim_offset()

        self.update_helper_graphics()
        pass

    def update_helper_graphics(self):
        right_vec = self.get_right_vec()
        down_vec = self.get_down_vec()

        # self.height and self.width are in actual coordinates
        v0 = self.get_v0()
        v1 = self.get_v1(down_vec, right_vec)

        vc = v1 - v0

        print("v0: ", v0, ", v1: ", v1, ", vc: ", vc)

        print("self.width: ", self.width, ", self.height: ", self.height)
        print("right_vec: ", right_vec, ", down_vec: ", down_vec)

        DraggableFrame.setPos(self, Vec3(*v0))
        self.drag_point.setPos(Vec3(*v0))

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

        self.resize_box_handle.setPos(*(v0 + self.resize_handle_vec))
        self.resize_box_handle_2.setPos(*(v0 + self.resize_handle_vec))

        self.quad.set_height(self.height)
        self.quad.set_width(self.width)
        self.quad._update_b2d()

        # # set box corners from upper left clockwise
        # # TODO: generalize to arbitrary normal vector
        # p0 = [0, 0, 0.] # v0

        # p1 = [
        #     v2p[0], # x coord
        #     0.,
        #     0.
        #     ]

        # p2 = v2p

        # p3 = [
        #     0.,
        #     0.,
        #     v2p[2], # y coord
        # ]

        # self.set_quad_box_corners(p0, p1, p2, p3)

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

        self.resize_box_handle_2.setPos(Vec3(*resize_to_pos))
        self.resize_box_handle.setPos(Vec3(*resize_to_pos))

        print("resize_box_handle_pos: ", resize_box_handle_pos)
        print("resize_to_pos: ", resize_to_pos)

        self.resize_handle_vec = resize_to_pos - v0

        down_vec_normalized = down_vec / np.linalg.norm(down_vec)
        right_vec_normalized = right_vec / np.linalg.norm(right_vec)

        new_vc_ver_comp = np.dot(down_vec_normalized, self.resize_handle_vec)
        new_vc_hor_comp = np.dot(right_vec_normalized, self.resize_handle_vec)

        print("new_vc_ver_comp: ", new_vc_ver_comp, ", new_vc_hor_comp: ", new_vc_hor_comp)

        height_min = 0.2
        width_min = height_min * 1.6

        new_height = new_vc_ver_comp
        new_width = new_vc_hor_comp

        if new_vc_ver_comp > height_min:
            self.height = new_height

        if new_vc_hor_comp > width_min:
            self.width = new_width

        print("new_height", new_height, ", new_width", new_width)
        self.update_window_graphics()


    def resize_frame_when_dragged(self):
        print("resizing", self.resize_move_ctr)
        self.resize_move_ctr += 1
        self.resize(handle_dragged=True)

    def setPos(self, *args, **kwargs):
        """ """
        DraggableFrame.setPos(self, *args, **kwargs)
        self.drag_point.setPos(*args, **kwargs)
        self.update_window_graphics()

    def set_quad_box_corners(p0=None, p1=None, p2=None, p3=None):
        # if p2 is not None:
        #     self.quad.right.setTipPoint(Vec3(*p2))
        # if p1 is not None:
        #     self.quad.right.setTailPoint(Vec3(*p1))

        # if p2 is not None:
        #     self.quad.bottom.setTipPoint(Vec3(*p2))
        # if p3 is not None:
        #     self.quad.bottom.setTailPoint(Vec3(*p3))

        # if p1 is not None:
        #     self.quad.top.setTipPoint(Vec3(*p1))
        # if p3 is not None:
        #     self.quad.left.setTipPoint(Vec3(*p3))

        # self.quad._update_b2d()
        pass

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
