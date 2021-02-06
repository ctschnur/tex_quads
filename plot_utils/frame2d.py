import engine
import engine.tq_graphics_basics
from engine.tq_graphics_basics import TQGraphicsNodePath

import numpy as np
import math

from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3, PlaneNode, Plane, LPlane, LPlanef
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

from plot_utils.colors.colors import get_color


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

            line = Line1dSolid(thickness=1.5)
            line.setTipPoint(Vec3(pos, 0., self.tick_length/2.))
            line.setTailPoint(Vec3(pos, 0., -self.tick_length/2.))

            label = BasicOriente2dText(self.camera_gear, text="{:.2f}".format(c_num))

            pt1, pt2 = label.getTightBounds()
            width = pt2.getX()  - pt1.getX()
            height = pt2.getY() - pt1.getY()

            if axis_direction_index==0:
                label.setPos(Vec3(pos, 0., -4.*width
                ))
            elif axis_direction_index==1:
                label.setPos(Vec3(pos, 0., height
                ))

            t = Tick()
            t.set_line(line)
            t.set_label(label)
            t.reparentTo(self)
            self.ticks.append(t)

class LinesIn2dFrame(TQGraphicsNodePath):
    """ used e.g. for clipping in a frame2d (and not affecting other things like borders) """
    def __init__(self):
        """ """
        TQGraphicsNodePath.__init__(self)

        self.lines = []

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

        # self.lines = []  # lines

        # self.linesin2dframe = None
        self.linesin2dframe = LinesIn2dFrame()
        self.linesin2dframe.reparentTo(self)

        self.d = 2                  # dimension of frame

        self.xmin_hard = None
        self.xmax_hard = None

        self.ymin_hard = None
        self.ymax_hard = None

        self._xmin_soft = 0.
        self._xmax_soft = 1.

        self._ymin_soft = 0.
        self._ymax_soft = 1.

        self.ticks_arr_numbers = None
        self.regenerate_ticks_arr_numbers()

        self.clipping_planes_p3d_nodepaths = []

        self.quad = Quad(thickness=1.5)
        self.quad.reparentTo(self)
        self.quad.setPos(Vec3(0., 0., self.height))

        self.set_figsize(self.height, self.width, update_graphics=None)

        self.set_xlim(self.xmin_hard, self.xmax_hard, update_graphics=False)
        self.set_ylim(self.ymin_hard, self.ymax_hard, update_graphics=False)

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

    def toggle_clipping_planes(self):
        """ """
        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
        if len(self.clipping_planes_p3d_nodepaths) == 0: # no clipping planes enabled
            self.set_clipping_planes()
        else:
            self.remove_clipping_planes()

    def remove_clipping_planes(self):
        """ """
        for nodepath in self.clipping_planes_p3d_nodepaths:
            nodepath.removeNode()

        self.linesin2dframe.get_p3d_nodepath().setClipPlaneOff()

        self.clipping_planes_p3d_nodepaths = []

    def set_clipping_planes(self):
        """ the lines may extend outside of the 'frame'
            setting clipping planes are one way to prevent them from being
            rendered outside """

        self.remove_clipping_planes()

        for i, normal_vector in zip(Frame2d.axis_direction_indices, Frame2d.axis_direction_vectors):
            d = self.get_p3d_axis_length_from_axis_direction_index(i)
            a, b, c = math_utils.p3d_to_np(normal_vector)

            plane1 = LPlanef(a, b, c, 0)
            plane1_node = PlaneNode('', plane1)
            plane1_node.setClipEffect(1)
            plane1_nodepath = NodePath(plane1_node)

            plane2 = LPlanef(-a, -b, -c, d)
            plane2_node = PlaneNode('', plane2)
            plane2_node.setClipEffect(1)
            plane2_nodepath = NodePath(plane2_node)

            clipped_thing_nodepath = self.linesin2dframe.get_p3d_nodepath()

            plane1_nodepath.reparentTo(clipped_thing_nodepath)
            clipped_thing_nodepath.setClipPlane(plane1_nodepath)
            self.clipping_planes_p3d_nodepaths.append(plane1_nodepath)

            plane2_nodepath.reparentTo(clipped_thing_nodepath)
            clipped_thing_nodepath.setClipPlane(plane2_nodepath)
            self.clipping_planes_p3d_nodepaths.append(plane2_nodepath)

            # clipped_thing_nodepath.setPos(0., 0., 0.)

        pass


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

    def update_ticks(self, regenerate_ticks=False):
        """ make sure the density of ticks is between ticks_max_density and ticks_min_density, then adjust the ticks """
        if regenerate_ticks == True:
            self.regenerate_ticks_arr_numbers(possibly_update_lims_from_internal_data=True)

        for i, axis_p3d_length, axis_direction_index in zip(range(self.d), [self.width, self.height], Frame2d.axis_direction_indices):
            self.ticks_arr[i].set_ticks_by_arr(self.ticks_arr_numbers[i], axis_p3d_length, axis_direction_index=axis_direction_index)

    def set_figsize(self, height, width, update_graphics=True):
        """ set the size of the figure, in p3d units """

        self.height = height
        self.width = width

        self.quad.set_height(self.height)
        self.quad.set_width(self.width)

        if update_graphics==True:
            self.quad.setPos(Vec3(0., 0., self.height))
            self.set_clipping_planes()
            self.update_graphics_alignment(regenerate_ticks=True)

    def update_graphics_alignment(self, regenerate_ticks=False):
        """ """
        self.update_ticks(regenerate_ticks=regenerate_ticks)
        self.update_alignment()

    def lims_hard_p(self):
        """ """
        return [self.xmin_hard is not None or self.xmax_hard is not None,
                self.ymin_hard is not None or self.ymax_hard is not None]

    def get_lims_from_internal_data(self):
        """ TODO: update this if to take into account not just lines,
            but also e.g. scatter data or color plot data """

        xmin = np.inf
        xmax = -np.inf

        ymin = np.inf
        ymax = -np.inf

        changed = False

        for line in self.linesin2dframe.lines:
            p3d_xyz_coords = line.getCoords_np()
            frame_x_coords = p3d_xyz_coords[:, 0]
            frame_y_coords = p3d_xyz_coords[:, 2]  # in p3d, z is up, but in my frame2d, y is up

            cur_xmin = min(frame_x_coords)
            if cur_xmin < xmin:
                xmin = cur_xmin
                changed = True

            cur_xmax = max(frame_x_coords)
            if cur_xmax > xmax:
                xmax = cur_xmax
                changed = True

            cur_ymin = min(frame_y_coords)
            if cur_ymin < ymin:
                ymin = cur_ymin
                changed = True

            cur_ymax = max(frame_y_coords)
            if cur_ymax > ymax:
                ymax = cur_ymax
                changed = True

        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

        assert changed==False or (xmin < xmax and ymin < ymax)

        if changed==True:
            return [(xmin, xmax), (ymin, ymax)]
        else:
            return []


    def regenerate_ticks_arr_numbers(self, possibly_update_lims_from_internal_data=False):
        """ """
        if possibly_update_lims_from_internal_data == True:
            # set soft xlims if xlims are not hard
            auto_lims = self.get_lims_from_internal_data()
            if len(auto_lims) > 0:            # auto_lims can not be determined if there is no data
                if not self.lims_hard_p()[0]: # x axis
                    self.set_xlim(*auto_lims[0], update_graphics=False, hard=False, regenerate=False)

                if not self.lims_hard_p()[1]: # y axis
                    self.set_ylim(*auto_lims[1], update_graphics=False, hard=False, regenerate=False)

        self.ticks_arr_numbers = [
            np.linspace(*self.get_preceding_xlims(), num=5, endpoint=True),
            np.linspace(*self.get_preceding_ylims(), num=5, endpoint=True)
        ]

    def set_xlim(self, xmin, xmax, update_graphics=True, hard=True, regenerate=True):
        """ if hard == False, figure out the preceding limits automatically
            from the line data """
        if hard == True:
            self.xmin_hard = xmin
            self.xmax_hard = xmax
        elif hard == False:
            self.unset_hard_xylims(reset_x_lim=True, reset_y_lim=False)

            self._xmin_soft = xmin
            self._xmax_soft = xmax
        else:
            print("hard should be boolean")
            exit(1)

        if regenerate == True:
            self.regenerate_ticks_arr_numbers()

        if update_graphics == True:
            self.update_graphics_alignment(regenerate_ticks=True)

    def unset_hard_xylims(self, reset_x_lim=True, reset_y_lim=True):
        """ """
        if reset_x_lim == True:
            self.xmax_hard = None
            self.xmin_hard = None
            assert self._xmax_soft is not None
            assert self._xmin_soft is not None

        if reset_y_lim == True:
            self.ymax_hard = None
            self.ymin_hard = None
            assert self._ymax_soft is not None
            assert self._ymin_soft is not None

    def get_preceding_xlims(self):
        """ """
        return ((self.xmin_hard if self.xmin_hard is not None else self._xmin_soft),
                (self.xmax_hard if self.xmax_hard is not None else self._xmax_soft))

    def get_preceding_ylims(self):
        """ """
        return ((self.ymin_hard if self.ymin_hard is not None else self._ymin_soft),
                (self.ymax_hard if self.ymax_hard is not None else self._ymax_soft))


    def set_ylim(self, ymin, ymax, update_graphics=True, hard=True, regenerate=True):
        """ if hard == False, figure out the preceding limits automatically
            from the line data """
        if hard == True:
            self.ymin_hard = ymin
            self.ymax_hard = ymax
        elif hard == False:
            self.unset_hard_xylims(reset_x_lim=False, reset_y_lim=True)

            self._ymin_soft = ymin
            self._ymax_soft = ymax
        else:
            print("hard should be boolean")
            exit(1)

        self.regenerate_ticks_arr_numbers()

        if update_graphics == True:
            self.update_graphics_alignment(regenerate_ticks=True)

    def get_p3d_to_frame_unit_length_scaling_factor(self, axis_direction_index):
        """ """
        ticks_arr_numbers_y_max = max(self.ticks_arr_numbers[axis_direction_index])
        ticks_arr_numbers_y_min = min(self.ticks_arr_numbers[axis_direction_index])
        max_y_p3d_pos = Ticks.get_tick_pos_along_axis(self.get_p3d_axis_length_from_axis_direction_index(axis_direction_index),
                                                      self.ticks_arr_numbers[axis_direction_index], max(self.ticks_arr_numbers[axis_direction_index]))
        min_y_p3d_pos = Ticks.get_tick_pos_along_axis(self.get_p3d_axis_length_from_axis_direction_index(axis_direction_index),
                                                      self.ticks_arr_numbers[axis_direction_index], min(self.ticks_arr_numbers[axis_direction_index]))

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

        for line in self.linesin2dframe.lines:
            print("set scale: ", self.get_p3d_to_frame_unit_length_scaling_factor(0), 1., self.get_p3d_to_frame_unit_length_scaling_factor(1))
            line.setScale(self.get_p3d_to_frame_unit_length_scaling_factor(0), 1., self.get_p3d_to_frame_unit_length_scaling_factor(1))
            print("self.get_p3d_to_frame_unit_length_scaling_factor(1): ", self.get_p3d_to_frame_unit_length_scaling_factor(1))
            line.setPos(math_utils.np_to_p3d_Vec3(pos_tmp))


    def get_p3d_axis_length_from_axis_direction_index(self, axis_direction_index):
        """ """
        if axis_direction_index == 0:
            return self.width
        elif axis_direction_index == 1:
            return self.height
        else:
            print("axis_direction_index: ", axis_direction_index, " does not correspond to any axis")
            exit(1)

    def plot(self, x, y,
             color="white",
             thickness=2):
        """ x, y: discrete points (each one a 1d numpy array, same size)"""
        if x is not None and y is not None:
            assert np.shape(x) == np.shape(y)

            sl = primitives.SegmentedLinePrimitive(color=get_color(color), thickness=thickness)
            sl.extendCoords([Vec3(x[i], 0., y[i]) for i in range(len(x))])
            sl.reparentTo(self.linesin2dframe)
            self.linesin2dframe.lines.append(sl)

        self.update_graphics_alignment(regenerate_ticks=True)

    def clear_plot(self):
        """ """
        for line in self.linesin2dframe.lines:
            line.removeNode()

        self.linesin2dframe.lines = []

        self.update_graphics_alignment(regenerate_ticks=True)

    def get_plot_x_range(self):
        return self.xmax_hard - self.xmin_hard

    def get_plot_y_range(self):
        return self.ymax_hard - self.ymin_hard

    def get_frame_p3d_origin(self):
        pos = self.quad.getPos()
        return np.array([pos[0], pos[2]])

    def get_frame_p3d_width(self):
        return self.width

    def get_frame_p3d_height(self):
        return self.height

    def shift_curve_to_match_up_zeros():
        pos0 = self.get_frame_p3d_origin()
