from direct.showbase.ShowBase import ShowBase, DirectObject

from simple_objects.primitives import ParametricLinePrimitive
from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk

from composed_objects.composed_objects import Point3dCursor

from panda3d.core import Vec3, Mat4, Vec4

import numpy as np

from plot_utils.edgemousetools import EdgeHoverer, EdgeMouseClicker

from local_utils import math_utils

from sequence.sequence import Sequence

from playback.playbackersm import PlaybackerSM

import os

import inspect

class EdgeGraphics:
    """ Parent class of recorder and of player
    This class is just an abstraction, and should not be used directly, but
    only be derived from. """

    def __init__(self, get_lps_rate_func, get_duration_func, *args, **kwargs):
        """ """
        self.v1 = None
        self.v_dir = None

        self.line = None
        self.primary_color = None
        self.cursor_sequence = None
        self.extraArgs = []

        self.get_lps_rate_func = get_lps_rate_func
        self.get_duration_func = get_duration_func

        self.v2_override = None

        pass

    def set_v_dir(self, v_dir):
        """ direction vector, normalizing the input vector """
        self.v_dir = v_dir/np.linalg.norm(v_dir)

    def get_v_dir(self):
        """ """
        return self.v_dir

    def set_v1(self, v1, update_graphics=True):
        """ set the starting point of the edge
        Args:
        - v1: p3d Vec3 """
        self.v1 = v1

        if update_graphics == True:
            # ---
            self.line.setTipPoint(self.get_v1())
            self.line.setTailPoint(self.get_v2())

            # call update_while_moving_function manually
            self.update_while_moving_function(
                self.state.get_s_a(), *tuple(self.extraArgs))

    def get_v1(self):
        """ """
        return self.v1

    def set_primary_color(self, primary_color, cursor_color_special=None,
                          line_color_special=None,
                          change_logical_primary_color=True):
        """ A part of the cursor and the line get by default
            the primary color. Optionally, they can be changed individually.

        Args:
            change_logical_primary_color:
               if False, the logical primary_color is not modified, if True, it is.
               This is good for e.g. on-hover short and temporary modifications of the
               primary color. """

        if change_logical_primary_color is True:
            self.primary_color = primary_color

        cursor_color = None
        line_color = None

        if cursor_color_special:
            cursor_color = cursor_color_special
        else:
            cursor_color = primary_color

        if line_color_special:
            line_color = line_color_special
        else:
            line_color = primary_color

        self.p_c.setColor(cursor_color)
        self.line.setColor(line_color)

    def get_primary_color(self):
        return self.primary_color

    def update_line(self, update_graphics=True):
        """ set the line to the appropriate dimensions """
        if self.line is None:
            self.line = Line1dSolid()

        if update_graphics == True:
            self.line.setTipPoint(self.get_v1())
            self.line.setTailPoint(self.get_v2())

    def update(self, *args, **kwargs):
        a = args[0]
        # self.state.set_s_a(s_a)  # update s_a
        self.update_while_moving_function(a, *args, **kwargs)

    def set_cursor_position(self, a):
        """ """
        cursor_pos = math_utils.np_to_p3d_Vec3(
            math_utils.p3d_to_np(self.get_v1()) +
            a * (math_utils.p3d_to_np(self.get_v2()) - math_utils.p3d_to_np(self.get_v1())))

        self.p_c.setPos(cursor_pos)

    def update_while_moving_function(self, a, *args, **kwargs):
        """ calculating everything that changes while
        playing """
        # self.state.set_s_a(s_a)  # update s_a

        # covered_time = s_a * (s_l/lps_rate)

        s_l = self.get_lps_rate_func() * self.get_duration_func()

        # covered_length = s_l * a

        # set cursor point:
        self.set_cursor_position(a)
        self.update_line()

    def set_v2_override(self, v2_override):
        """ """
        self.v2_override = v2_override

        # update the direction
        self.set_v_dir(v2_override - self.get_v1())

    def get_v2(self):
        """ """
        if self.v2_override is not None:
            return self.v2_override

        return self.v1 + self.get_v_dir() * self.get_lps_rate_func() * self.get_duration_func()

    def remove(self):
        """ removes all
        - p3d sequences
        - p3d nodes (detaches them from render)
        - p3d events (directobjects)
        their references. """

        self.cursor_sequence.pause()  # remove it from the interval manager
        del self.cursor_sequence  # remove the reference

        self.line.nodePath.removeNode()
        self.p_c.remove()
