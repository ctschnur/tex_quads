import engine
import engine.tq_graphics_basics
from engine.tq_graphics_basics import TQGraphicsNodePath

import numpy as np
import math

from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

from plot_utils.quad import Quad

from simple_objects.primitives import ParametricLinePrimitive

import numpy as np
import scipy.special

from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, Fixed2dLabel
from local_utils import math_utils

from simple_objects.simple_objects import BasicText, BasicOriente2dText

from simple_objects import primitives


class Tick(TQGraphicsNodePath):
    """ Line and (optionally) Label """
    def __init__(self):
        """ """
        TQGraphicsNodePath.__init__(self)

        self.line = None
        self.label = None

    def set_line(self, line):
        """ """
        self.line = line
        self.line.reparentTo(self)

    def set_label(self, label):
        """ """
        self.label = label
        self.label.reparentTo(self)

class Ticks(TQGraphicsNodePath):
    """ """
    def __init__(self, camera_gear):
        """
        Args:
            arr: numbers at which to create the tick lines """
        TQGraphicsNodePath.__init__(self)
        self.camera_gear = camera_gear

        # self.lines = []
        self.ticks = []
        self.tick_length = 0.05

        self.num_arrs = [[0.0, 1.0], [0.0, 1.0]]

    def remove_all_ticks(self):
        """ """
        for tick in self.ticks:
            tick.remove()

    def x_p3d_to_axes(x_ticks_numbers_arr):
        """ """
        arr_span = np.abs(np.max(x_ticks_numbers_arr) - np.min(x_ticks_numbers_arr))
        arr_num_min = np.min(self.arr)

    @staticmethod
    def get_tick_pos_along_axis(p3d_axis_length, num_arr, c_num):
        """ """
        return (p3d_axis_length/Ticks.get_arr_span(num_arr)) * (c_num - min(num_arr))

    @staticmethod
    def get_arr_span(num_arr):
        """ """
        return np.abs(np.max(num_arr) - np.min(num_arr))

    @staticmethod
    def get_tick_pos(p3d_axis_length, num_arr, c_num):
        """ """
        return Ticks.get_tick_pos_along_axis(p3d_axis_length, num_arr, c_num)

    def set_ticks_by_arr(self, num_arr, p3d_axis_length, axis_direction_index):
        """ pass an array, generate a bunch of vertical lines """
        self.remove_all_ticks()
        self.num_arrs[axis_direction_index] = num_arr

        for c_num in num_arr:
            pos = Ticks.get_tick_pos(p3d_axis_length, num_arr, c_num)

            line = Line1dSolid(thickness=1.0)
            line.setTipPoint(Vec3(pos, 0., self.tick_length/2.))
            line.setTailPoint(Vec3(pos, 0., -self.tick_length/2.))

            label = BasicOriente2dText(self.camera_gear, text="{:.1f}".format(c_num))

            pt1, pt2 = label.getTightBounds()
            width = pt2.getX()  - pt1.getX()
            height = pt2.getY() - pt1.getY()

            if axis_direction_index==0:
                label.setPos(Vec3(pos, 0., -height))
            elif axis_direction_index==1:
                label.setPos(Vec3(pos, 0., height))

            t = Tick()
            t.set_line(line)
            t.set_label(label)
            t.reparentTo(self)
            self.ticks.append(t)


class Frame2d(TQGraphicsNodePath):
    """ a 2d frame within which 2d data can be displayed, i.e. numpy x and y arrays """

    axis_direction_indices = [0, 1] # 0 for x axis, 1 for y axis
    axis_direction_indices_chars = ["x", "y"]
    axis_direction_vectors = [Vec3(1., 0., 0.), Vec3(0., 0., 1.)]

    def __init__(self, camera_gear):
        """ """
        TQGraphicsNodePath.__init__(self)

        self.quad = None

        self.camera_gear = camera_gear

        size = 0.5
        self.height = size
        self.width = size * 1.618

        self.lines = []  # lines

        self.d = 2                  # dimension of frame

        self.xmin = 0.
        self.xmax = 1.

        self.ymin = 0.
        self.ymax = 1.

        self.ticks_arr_numbers = None
        self.regenerate_arrays()

        # self.additional_trafo_nodepath = TQGraphicsNodePath()
        # self.additional_trafo_nodepath.reparentTo_p3d(self.getParent_p3d())
        # self.set_p3d_nodepath(
        #     self.additional_trafo_nodepath.attachNewNode_p3d(self.get_node_p3d()))
        # self.additional_trafo_nodepath.setMat_normal(# self.get_additional_trafo_mat()
        #     math_utils.getTranslationMatrix4x4(self.width, 0., self.height)
        # )

        self.quad = Quad(thickness=2.0)
        self.quad.reparentTo(self)
        self.quad.setPos(Vec3(0., 0., self.height))

        # self.setMat_normal(self.get_quad_base_transform_mat())

        self.set_figsize(self.height, self.width, update_graphics=None)

        self.set_xlim(self.xmin, self.xmax, update_graphics=False)
        self.set_ylim(self.ymin, self.ymax, update_graphics=False)

        # self.plp1 = None

        self.ticks_arr = []

        for i, n_vec in zip(range(self.d), Frame2d.axis_direction_vectors):
            ticks = Ticks(camera_gear)
            self.ticks_arr.append(ticks)
            ticks.reparentTo(self)
            ticks.setMat_normal(math_utils.getMat4by4_to_rotate_xhat_to_vector(n_vec))
            # h, p, r = ticks.getHpr()
            # ticks.setHpr(h, p , r - i * 90.)

        # self.ticks_max_density = 10. # per p3d length unit
        # self.ticks_min_density = 3. # per p3d length unit

        self.update_ticks()

        # transform the y=0 of the curve in p3d coordinates to frame coordinates
        # self.getPos()[2] + Ticks.get_tick_pos_along_axis(self.height, self.ticks_arr_numbers[1], 0)

    # def reparentTo(self, *args, **kwargs):
    #     """ """
    #     return self.additional_trafo_nodepath.reparentTo(*args, **kwargs)


    @staticmethod
    def get_axis_direction_index_from_char_index(char_index):
        if x_or_y_str == "x":
            return 0
        elif x_or_y_str == "y":
            return 1
        assert False

    # def get_quad_base_transform_mat(self):
    #     """ transform to set it's position in the center and scale it's dimensions to [1,1]"""
    #     return math_utils.getTranslationMatrix4x4(0., 0., self.height).dot(
    #         math_utils.getTranslationMatrix4x4(self.pos_x, 0., self.pos_y))

    def update_ticks(self):
        """ make sure the density of ticks is between ticks_max_density and ticks_min_density, then adjust the ticks """
        for i, axis_p3d_length, axis_direction_index in zip(range(self.d), [self.width, self.height], Frame2d.axis_direction_indices):
            self.ticks_arr[i].set_ticks_by_arr(self.ticks_arr_numbers[i], axis_p3d_length, axis_direction_index=axis_direction_index)

    def set_figsize(self, height, width, update_graphics=True):
        """ set the size of the figure, in p3d units """
        self.quad.set_height(self.height)
        self.quad.set_width(self.width)

        if update_graphics==True:
            self.update_ticks()
            self.update_alignment()

    def regenerate_arrays(self):
        """ """
        self.ticks_arr_numbers = [
            np.linspace(self.xmin, self.xmax, num=5, endpoint=True),
            np.linspace(self.ymin, self.ymax, num=7, endpoint=True)
        ]

    def set_xlim(self, xmin, xmax, update_graphics=True):
        """ """
        self.xmin = xmin
        self.xmax = xmax

        self.regenerate_arrays()

        if update_graphics == True:
            self.update_ticks()
            self.update_alignment()

    def set_ylim(self, ymin, ymax, update_graphics=True):
        """ """
        self.ymin = ymin
        self.ymax = ymax

        self.regenerate_arrays()

        if update_graphics == True:
            self.update_ticks()
            self.update_alignment()

    def get_p3d_to_frame_unit_length_scaling_factor(self, axis_direction_index):
        """ """
        ticks_arr_numbers_y_max = max(self.ticks_arr_numbers[axis_direction_index])
        ticks_arr_numbers_y_min = min(self.ticks_arr_numbers[axis_direction_index])
        max_y_p3d_pos = Ticks.get_tick_pos_along_axis(self.height, self.ticks_arr_numbers[axis_direction_index], max(self.ticks_arr_numbers[axis_direction_index]))
        min_y_p3d_pos = Ticks.get_tick_pos_along_axis(self.height, self.ticks_arr_numbers[axis_direction_index], min(self.ticks_arr_numbers[axis_direction_index]))

        return np.abs(max_y_p3d_pos - min_y_p3d_pos)/np.abs(ticks_arr_numbers_y_max - ticks_arr_numbers_y_min)

    def update_alignment(self):
        """ """
        # p = Point3d(scale=0.25, color=Vec4(1., 0., 0., 1.))
        # p.reparentTo(self)

        pos_for_x = math_utils.p3d_to_np(Frame2d.axis_direction_vectors[0]) * Ticks.get_tick_pos_along_axis(self.width, self.ticks_arr_numbers[0], 0.0)
        pos_for_y = math_utils.p3d_to_np(Frame2d.axis_direction_vectors[1]) * Ticks.get_tick_pos_along_axis(self.height, self.ticks_arr_numbers[1], 0.0)

        pos_tmp = math_utils.p3d_to_np(pos_for_y) + math_utils.p3d_to_np(pos_for_x)
        # p.setPos(math_utils.np_to_p3d_Vec3(pos_tmp))

        # pos_tmp = math_utils.p3d_to_np(pos_for_y)

        for line in self.lines:
            line.setScale(self.get_p3d_to_frame_unit_length_scaling_factor(0), 1., self.get_p3d_to_frame_unit_length_scaling_factor(1))
            print("self.get_p3d_to_frame_unit_length_scaling_factor(1): ", self.get_p3d_to_frame_unit_length_scaling_factor(1))
            line.setPos(math_utils.np_to_p3d_Vec3(pos_tmp))

    def plot(self, x, y):
        """ x, y: discrete points (each one a 1d numpy array, same size)"""
        # if self.plp1 is not None:
        #     self.plp1.removeNode()
        #     self.plp1 = None

        if x is not None and y is not None:
            # self.plp1 = ParametricLinePrimitive(
            #     lambda t: np.array([func_xy_of_t(t)[0], 0., func_xy_of_t(t)[1]]),
            #     howmany_points=100, param_interv=np.array([0, 2.0 * np.pi]))
            assert np.shape(x) == np.shape(y)

            sl = primitives.SegmentedLinePrimitive(color=Vec4(1., 1., 1., 1.))
            sl.extendCoords([Vec3(x[i], 0., y[i]) for i in range(len(x))])

            sl.reparentTo(self)
            self.lines.append(sl)

            # math_utils.np_to_p3d_Vec3(pos_of_particle_np)

            # self.plp1.reparentTo(self)
            # self.plp1.setPos(self.quad.get_pos_vec3())

            # get xlim and ylim
            # map p3d coordinates (from top left corner of frame) -> figure coordinates
        # else:
            # if self.plp1 is not None:
            #     self.plp1.remove()

            self.update_alignment()

    def get_plot_x_range(self):
        return self.xmax - self.xmin

    def get_plot_y_range(self):
        return self.ymax - self.ymin

    def get_frame_p3d_origin(self):
        pos = self.quad.getPos()
        return np.array([pos[0], pos[2]])

    def get_frame_p3d_width(self):
        return self.width

    def get_frame_p3d_height(self):
        return self.height

    def shift_curve_to_match_up_zeros():
        pos0 = self.get_frame_p3d_origin()

        # ticks0 =

    def remove():
        """ """
        self.quad.remove()
