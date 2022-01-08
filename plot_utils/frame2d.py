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

from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk
from local_utils import math_utils

from simple_objects.text import BasicText, BasicOrientedText, Basic2dText

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
    def __init__(self, camera_gear, update_labels_orientation=False, attach_to_space="render"):
        """
        Args:
            arr: numbers at which to create the tick lines """
        TQGraphicsNodePath.__init__(self)
        self.camera_gear = camera_gear

        self.attach_to_space = attach_to_space

        self.update_labels_orientation = update_labels_orientation

        # self.lines = []
        self.ticks = []
        self.tick_length = 0.05

        self.num_arrs = [[0.0, 1.0], [0.0, 1.0]]

    def remove_ticks_graphics(self):
        """ """
        for tick in self.ticks:
            tick.removeNode()

    @staticmethod
    def get_tick_pos_along_axis(p3d_axis_length, num_arr, c_num):
        """ """
        arr_span = Ticks.get_arr_span(num_arr)
        return (p3d_axis_length/arr_span) * (c_num - min(num_arr))

    @staticmethod
    def get_arr_span(num_arr):
        """ """
        return np.abs(np.max(num_arr) - np.min(num_arr))

    def regenerate_ticks_graphics(self, num_arr, p3d_axis_length, axis_direction_index):
        """ pass an array, generate a bunch of vertical lines """
        self.remove_ticks_graphics()
        self.num_arrs[axis_direction_index] = num_arr

        for c_num in num_arr:
            pos = Ticks.get_tick_pos_along_axis(p3d_axis_length, num_arr, c_num)

            if (np.abs(pos) == np.inf):
                print("warning: (np.abs(math_utils.p3d_to_np(pos)) == np.inf).any() == True: ",
                      "TODO: improve this mechanism!")
                # TODO: before updating the ticks check if the range
                # of the ticks is near zero. then set the minimum range
                # and center it around the middle
                return

            line = Line1dSolid(thickness=1.5)
            a = Vec3(pos, 0., self.tick_length/2.)
            b = Vec3(pos, 0., -self.tick_length/2.)

            # print("a: ", a)
            # print("b: ", b)
            line.setTipPoint(a)
            line.setTailPoint(b)

            label = None
            if axis_direction_index == 0:
                alignment = "center"
            if axis_direction_index == 1:
                alignment = "center"

            text_kwargs = dict(
                text="{:.1e}".format(c_num),
                alignment=alignment
            )

            if self.update_labels_orientation == True:
                label = BasicOrientedText(
                    self.camera_gear,
                    update_orientation_on_camera_rotate=self.update_labels_orientation,
                    **text_kwargs
                    )
            else:
                # label = BasicText(**text_kwargs)
                # Basic2dText
                label = Basic2dText(rotate_angle_2d=0, **text_kwargs)

            label.showTightBounds()
            height = engine.tq_graphics_basics.get_pts_to_p3d_units(label.pointsize)
            width = (label.textNode.getWidth()/label.textNode.getHeight()) * height

            # if self.update_labels_orientation == True:
            if axis_direction_index==0:
                label.setPos(Vec3(pos, 0., -height*1.5))
                # print("height: ", height, ", width: ", width)
            elif axis_direction_index==1:  # y axis in 2d
                label.setPos(Vec3(pos - (height/4.), 0., width))

                if self.attach_to_space == "render":
                    None  # do not rotate the label
                elif self.attach_to_space == "aspect2d":
                    h, p, r = aspect2d.getHpr()
                    label.setHpr(h, p, r+90)
                else:
                    print("ERR: self.attach_to_space must be aspect2d or render")
                    exit(1)
            # else:
            #     if axis_direction_index==0:
            #         label.setPos(Vec3(pos, 0., -height*1.5))
            #         # print("height: ", height, ", width: ", width)
            #     elif axis_direction_index==1:
            #         label.setPos(Vec3(pos - (height/4.), 0., width))

            t = Tick()
            t.set_line(line)
            t.set_label(label)
            t.reparentTo(self)
            self.ticks.append(t)

            # re-face the camera again after being reparented to a tick, since
            # the relative orientation to render has changed by the reparenting
            # print("face camera")

            if self.update_labels_orientation == True:
                t.label.face_camera()


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

    def __init__(self, camera_gear=None, update_labels_orientation=False, with_ticks=True,
                 attach_to_space="aspect2d",  # or "render",
                 attach_directly=True
                 ):
        """ """
        TQGraphicsNodePath.__init__(self)

        self.attached_p = False

        if attach_to_space == "aspect2d":
            if update_labels_orientation==True:
                print("WARNING: do not set attach_to_space to aspect2d and update_labels_orientation=True simultaneously!")
                update_labels_orientation = False

        if attach_to_space == "render":
            if camera_gear is None:
                print("ERR: if attach_to_space == render, supply a camera_gear as well that is not None!")
                exit(1)

        self.attach_to_space = attach_to_space  # "render" or "aspect2d"

        self.quad = None

        # if camera_gear == None:
        #     self.update_labels_orientation == False

        # if update_labels_orientation == True and camera_gear == None:
        #     print("WARNING: if update_labels_orientation == True, camera_gear cannot be None")
        #      exit(1)


        self.camera_gear = camera_gear

        self.update_labels_orientation = update_labels_orientation

        size = 0.5
        self.height = size
        self.width = size * 1.618

        # self.lines = []  # lines

        # self.linesin2dframe = None
        self.linesin2dframe = LinesIn2dFrame()
        self.linesin2dframe.reparentTo(self)

        self.with_ticks = with_ticks

        self.d = 2                  # dimension of frame

        self.xmin_hard = None
        self.xmax_hard = None

        self.ymin_hard = None
        self.ymax_hard = None

        self._xmin_soft = 0.
        self._xmax_soft = 1.

        self._ymin_soft = 0.
        self._ymax_soft = 1.

        self.axes_ticks_numbers = None
        self.regenerate_axes_ticks_numbers()

        self.clipping_planes_p3d_nodepaths = []

        self.quad = Quad(thickness=1.5)
        self.quad.reparentTo(self)

        # --- Ticks -----
        print("with_ticks: ", self.with_ticks)
        if self.with_ticks == True:
            self.axes_ticks = []

            for i, n_vec in zip(range(self.d), Frame2d.axis_direction_vectors):
                ticks = Ticks(camera_gear, update_labels_orientation=self.update_labels_orientation, attach_to_space="aspect2d")
                self.axes_ticks.append(ticks)
                ticks.reparentTo(self)
                ticks.setMat_normal(math_utils.getMat4by4_to_rotate_xhat_to_vector(n_vec))
                # h, p, r = ticks.getHpr()
                # ticks.setHpr(h, p , r - i * 90.)

            self.regenerate_ticks()

        self.update_alignment()

        if attach_directly == True and self.attached_p == False:
            # print("Attaching directly")
            if attach_to_space == "aspect2d":
                self.attach_to_aspect2d()
            elif attach_to_space == "render":
                self.attach_to_render()
            else:
                exit(1)


    def toggle_clipping_planes(self):
        """ """
        if len(self.clipping_planes_p3d_nodepaths) == 0: # no clipping planes enabled
            self.turn_clipping_planes_on()
        else:
            self.turn_clipping_planes_off()

    def turn_clipping_planes_off(self):
        """ """
        for nodepath in self.clipping_planes_p3d_nodepaths:
            nodepath.removeNode()

        self.linesin2dframe.get_p3d_nodepath().setClipPlaneOff()

        self.clipping_planes_p3d_nodepaths = []

    def turn_clipping_planes_on(self):
        """ the lines may extend outside of the 'frame'
            setting clipping planes are one way to prevent them from being
            rendered outside

            if dimensions of the frame are updated, set_clipping_panel_geometry must be called before this
            with the appriopriate panel geometry """

        self.turn_clipping_planes_off()

        for i, normal_vector in zip(Frame2d.axis_direction_indices,
                                    Frame2d.axis_direction_vectors):
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

    @staticmethod
    def get_axis_direction_index_from_char_index(char_index):
        if x_or_y_str == "x":
            return 0
        elif x_or_y_str == "y":
            return 1
        assert False

    def regenerate_ticks(self):
        """ make sure the density of ticks is between ticks_max_density and ticks_min_density,
        then adjust the ticks """

        self.regenerate_axes_ticks_numbers(possibly_update_lims_from_internal_data=True)

        for i, axis_p3d_length, axis_direction_index in zip(
                range(self.d),
                [self.width, self.height],
                Frame2d.axis_direction_indices):
            self.axes_ticks[i].regenerate_ticks_graphics(
                self.axes_ticks_numbers[i],
                axis_p3d_length,
                axis_direction_index=axis_direction_index)

    def set_figsize(self, width, height, update_graphics=True):
        """ set the size of the figure, in p3d units """

        self.height = height
        self.width = width

        self.quad.set_height(self.height)
        self.quad.set_width(self.width)

        if update_graphics==True:
            self.quad.setPos(Vec3(0., 0., self.height))
            self.turn_clipping_planes_on()
            self.update_graphics_alignment()

    def update_graphics_alignment(self):
        """ """
        if self.with_ticks == True:
            self.regenerate_ticks()

        self.update_alignment()

    def lims_hard_p(self):
        """ """
        return [self.xmin_hard is not None or self.xmax_hard is not None,
                self.ymin_hard is not None or self.ymax_hard is not None]

    def lims_fully_hard(self):
        """ """
        return (self.xmin_hard is not None and self.xmax_hard is not None and
                self.ymin_hard is not None and self.ymax_hard is not None)

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

        _vars = [xmin, xmax, ymin, ymax]

        if np.inf in _vars or -np.inf in _vars:
            # print("ERR: infinity is not a valid axes limit!")
            return []
        else:
            # set an offset to the data
            # offset the margin of the plot by 0.1 times the span of the displayed data
            margin_factor = 0.05

            xspan = np.abs(xmax - xmin)
            offset = xspan * margin_factor
            xmin -= offset
            xmax += offset

            yspan = np.abs(ymax - ymin)
            offset = yspan * margin_factor
            ymin -= offset
            ymax += offset

            return [(xmin, xmax), (ymin, ymax)]

    def regenerate_axes_ticks_numbers(self, possibly_update_lims_from_internal_data=False):
        """ """
        if possibly_update_lims_from_internal_data == True:
            # set soft xlims if xlims are not hard
            auto_lims = self.get_lims_from_internal_data()
            if len(auto_lims) > 0:            # auto_lims can not be determined if there is no data
                if not self.lims_hard_p()[0]: # x axis
                    self.set_xlim(*auto_lims[0], update_graphics=False, hard=False, regenerate=False)

                if not self.lims_hard_p()[1]: # y axis
                    self.set_ylim(*auto_lims[1], update_graphics=False, hard=False, regenerate=False)

        self.axes_ticks_numbers = [
            np.linspace(*self.get_preceding_xlims(), num=5, endpoint=True),
            np.linspace(*self.get_preceding_ylims(), num=5, endpoint=True)
        ]

    def set_xlim(self, xmin, xmax, update_graphics=True, hard=True, regenerate=True):
        """ if hard == False, figure out the preceding limits automatically
            from the line data """

        if math_utils.equal_up_to_epsilon(xmin, xmax):
            span_abs = np.abs(xmax-xmin)
            center = xmin + span_abs / 2.
            padding0 = 0.1
            xmin = center - padding0
            xmax = center + padding0

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
            self.regenerate_axes_ticks_numbers()

        if update_graphics == True:
            self.update_graphics_alignment()

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

        if math_utils.equal_up_to_epsilon(ymin, ymax):
            span_abs = np.abs(ymax-ymin)
            center = ymin + span_abs / 2.
            padding0 = 0.1
            ymin = center - padding0
            ymax = center + padding0

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

        self.regenerate_axes_ticks_numbers()

        if update_graphics == True:
            self.update_graphics_alignment()

    def get_p3d_to_frame_unit_length_scaling_factor(self, axis_direction_index):
        """ """
        axes_ticks_numbers_y_max = max(self.axes_ticks_numbers[axis_direction_index])
        axes_ticks_numbers_y_min = min(self.axes_ticks_numbers[axis_direction_index])
        max_y_p3d_pos = Ticks.get_tick_pos_along_axis(self.get_p3d_axis_length_from_axis_direction_index(axis_direction_index),
                                                      self.axes_ticks_numbers[axis_direction_index], max(self.axes_ticks_numbers[axis_direction_index]))
        min_y_p3d_pos = Ticks.get_tick_pos_along_axis(self.get_p3d_axis_length_from_axis_direction_index(axis_direction_index),
                                                      self.axes_ticks_numbers[axis_direction_index], min(self.axes_ticks_numbers[axis_direction_index]))

        return np.abs(max_y_p3d_pos - min_y_p3d_pos)/np.abs(axes_ticks_numbers_y_max - axes_ticks_numbers_y_min)

    def update_alignment(self):
        """ """
        pos_for_x = math_utils.p3d_to_np(Frame2d.axis_direction_vectors[0]) * Ticks.get_tick_pos_along_axis(self.width, self.axes_ticks_numbers[0], 0.0)
        pos_for_y = math_utils.p3d_to_np(Frame2d.axis_direction_vectors[1]) * Ticks.get_tick_pos_along_axis(self.height, self.axes_ticks_numbers[1], 0.0)

        pos_tmp = math_utils.p3d_to_np(pos_for_y) + math_utils.p3d_to_np(pos_for_x)

        for line in self.linesin2dframe.lines:
            x_scale = self.get_p3d_to_frame_unit_length_scaling_factor(0)
            y_scale = self.get_p3d_to_frame_unit_length_scaling_factor(1)

            # print("x_scale, y_scale: ", x_scale, y_scale)
            cond = np.abs(x_scale) > 1e-8 and np.abs(y_scale) > 1e-8
            if cond:
                line.setScale(x_scale, 1., y_scale)
                line.setPos(math_utils.np_to_p3d_Vec3(pos_tmp))
            else:
                print("scaling by too low is not supported by p3d, do it differently!")
                self.clear_plot()


    def get_p3d_axis_length_from_axis_direction_index(self, axis_direction_index):
        """ """
        if axis_direction_index == 0:
            return self.width
        elif axis_direction_index == 1:
            return self.height
        else:
            print("axis_direction_index: ", axis_direction_index, " does not correspond to any axis")
            exit(1)

    def plot(self, x, y, color="white", thickness=2):
        """ x, y: discrete points (each one a 1d numpy array, same size) """
        # TODO: check if it is a line along only x or only y and then set soft xlims with a flag

        if x is not None and y is not None:
            assert np.shape(x) == np.shape(y)

            sl = primitives.SegmentedLinePrimitive(color=get_color(color), thickness=thickness)
            sl.extendCoords([Vec3(x[i], 0., y[i]) for i in range(len(x))])
            sl.reparentTo(self.linesin2dframe)
            self.linesin2dframe.lines.append(sl)

        if self.with_ticks == True and not self.lims_fully_hard():
            self.regenerate_ticks()

        self.update_alignment()

    def clear_plot(self, update_alignment=True):
        """ """
        for line in self.linesin2dframe.lines:
            line.removeNode()

        self.linesin2dframe.lines = []

        if update_alignment == True:
            if not self.lims_fully_hard():
                self.update_graphics_alignment()

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

    def attach_to_aspect2d(self):
        if self.attach_to_space == "aspect2d":
            super().attach_to_aspect2d()
            self.attached_p = True
            self.set_figsize(self.width, self.height, update_graphics=True)
        else:
            print("ERR: Do not call attach_to_aspect2d() to a frame for",
                  "which self.attach_to_space is not set to aspect2d")
            exit(1)

    def attach_to_render(self):
        if self.attach_to_space == "render":
            super().attach_to_render()
            self.attached_p = True
            self.set_figsize(self.width, self.height, update_graphics=True)
        else:
            print("ERR: Do not call attach_to_render() to a frame for",
                  "which self.attach_to_space is not set to render")
            exit(1)
