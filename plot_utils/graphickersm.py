from direct.showbase.ShowBase import ShowBase, DirectObject

from simple_objects.primitives import ParametricLinePrimitive
from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk

from composed_objects.composed_objects import Point3dCursor

from panda3d.core import Vec3, Mat4, Vec4

import numpy as np

from plot_utils.edgehoverer import EdgeHoverer, EdgeMouseClicker

from local_utils import math_utils

from sequence.sequence import Sequence

from playback.playback import Playbacker

import os

import inspect

from plot_utils.edgegraphics import EdgeGraphics

import playback.audiofunctions

from plot_utils.edgestate import EdgeState

from statemachine.statemachine import StateMachine, BatchEvents

import threading


class GraphickerSM(StateMachine, EdgeGraphics):
    """ """
    stopped_at_beginning_primary_color = ((1., 0., 0., 1.), 1)
    stopped_at_beginning_cursor_color = ((1., 0., 0., 1.), 1)
    # this is only set, if the line (edge) is 'engaged' (at a node, multiple edges diverge)
    stopped_at_beginning_line_color = ((1., 0., 0., 1.), 1)

    stopped_at_end_primary_color = ((1., .5, 0., 1.), 1)
    stopped_at_end_cursor_color = ((1., .5, 0., 1.), 1)
    # this is only set, if the line (edge) is 'engaged' (at a node, multiple edges diverge)
    stopped_at_end_line_color = ((1., .5, 0., 1.), 1)

    playing_primary_color = ((.5, .5, 0., 1.), 1)
    playing_cursor_color = ((.5, .5, 0., 1.), 1)
    # this is only set, if the line (edge) is 'engaged' (at a node, multiple edges diverge)
    playing_line_color = ((.5, .5, 0., 1.), 1)

    paused_primary_color = ((0., .5, .5, 1.), 1)
    paused_cursor_color = ((0., .5, .5, 1.), 1)
    # this is only set, if the line (edge) is 'engaged' (at a node, multiple edges diverge)
    paused_line_color = ((0., .5, .5, 1.), 1)

    lps_rate = 0.25/1.  # length per second

    t_epsilon = 0.001

    def __init__(self, wave_file_duration, *args, **kwargs):
        """ """
        StateMachine.__init__(self, *args, **kwargs)
        EdgeGraphics.__init__(self)

        self.v1 = None
        self.v_dir = None
        self.duration = wave_file_duration
        self.line = None
        self.primary_color = None
        self.cursor_sequence = None
        self.extraArgs = None
        # self.camera_gear = None
        self.state = EdgeState()

        self.add_batch_events_for_setup(
            BatchEvents(
                [self.state_stopped_at_beginning,
                 self.state_stopped_at_end,
                 self.state_play,
                 self.state_pause],
                [lambda: self.on_key_event_once("a", self.state_stopped_at_beginning),
                 lambda: self.on_key_event_once("e", self.state_stopped_at_end)]))


        self.add_batch_events_for_setup(
            BatchEvents(
                [
                 self.state_play,
                 self.state_pause],
                [lambda: self.on_key_event_once("arrow_left",
                                           self.skip_back_state,
                                           next_state_args=(self.get_current_state(),))]))

        self.add_batch_events_for_setup(
            BatchEvents(
                [
                 self.state_stopped_at_beginning,
                 self.state_play,
                 self.state_pause],
                [lambda: self.on_key_event_once("arrow_right",
                                           self.skip_forward_state,
                                           next_state_args=(self.get_current_state(),))]))

        self.transition_into(self.state_load_graphics)

    def get_skipped_time(self, direction=+1):
        """
        Args:
            direction: +- 1, to indicate if backwards or forwards"""

        calculated_time = (self.state.get_s_a() * self.get_duration() + direction *
                           self.short_skipping_time_step)

        return np.clip(calculated_time, GraphickerSM.t_epsilon, self.get_duration())

    def skip_back_state(self, previous_state):
        """ """
        self.transition_into(
            previous_state, next_state_args=(self.get_skipped_time(direction=-1),))

    def skip_forward_state(self, previous_state):
        """ """
        self.transition_into(
            previous_state, next_state_args=(self.get_skipped_time(direction=+1),))

    def state_stopped_at_beginning(self, *opt_args):
        """ """
        self.state.set_s_a(0.)

        self.cursor_sequence.pause()
        self.cursor_sequence.set_t(self.state.get_s_a() * self.get_duration())

        self.set_primary_color(self.stopped_at_beginning_primary_color)

        self.on_key_event_once("space", self.state_play)

    def state_stopped_at_end(self, *opt_args):
        """ """
        self.state.set_s_a(1.)
        self.cursor_sequence.finish()
        self.set_primary_color(self.stopped_at_end_primary_color)

        self.on_key_event_once("arrow_left", self.state_play,
                               next_state_args=(self.get_skipped_time(direction=-1),))

    def state_load_graphics(self):
        """ """
        # self.load_thread = threading.Thread(target=self.load, daemon=True)
        # self.load_thread.start()

        self.set_v1(Vec3(-.5, -.5, 0.), update_graphics=False)

        self.set_v_dir(Vec3(1., 1., 0.)/np.linalg.norm(Vec3(1., 1., 0.)))

        self.set_duration(self.duration, update_cursor_sequence=False)

        # interactive forward/backward skipping, in seconds
        self.short_skipping_time_step = 0.5

        # -- do graphics stuff
        self.p_c = Point3dCursor(self.get_v1())

        self.update_line()

        self.set_primary_color(
            self.stopped_at_beginning_primary_color)  # initially

        self.cursor_sequence = Sequence()
        self.extraArgs = []
        self.cursor_sequence.set_sequence_params(
            duration=self.get_duration(),
            extraArgs=self.extraArgs,
            update_function=self.update,
            on_finish_function=lambda: self.transition_into(self.state_stopped_at_end))

        # -- init hover and click actions
        # self.camera_gear = camera_gear

        # self.edge_hoverer = EdgeHoverer(self, self.camera_gear)

        # self.edge_mouse_clicker = EdgeMouseClicker(self)

        self.transition_into(self.state_stopped_at_beginning)

    def on_finish_cursor_sequence(self):
        self.set_stopped_at_end()

    def set_stopped_at_end(self,  # already_at_end=False
                           ):
        self.state.set_s_a(1.)
        print("stopped at end ", self)
        self.cursor_sequence.finish()
        self.set_primary_color(self.stopped_at_end_primary_color)

    def state_play(self, change_time_to=None):
        """ """
        if change_time_to is not None:
            a = change_time_to / self.get_duration()
            self.state.set_s_a(a)
            self.cursor_sequence.set_t(a * self.get_duration())

        self.cursor_sequence.resume()
        self.set_primary_color(self.playing_primary_color)

        self.on_key_event_once("space", self.state_pause)

    def state_pause(self, change_time_to=None):
        """ """
        if change_time_to is not None:
            self.cursor_sequence.set_t(change_time_to)

        self.cursor_sequence.pause()

        self.set_primary_color(self.paused_primary_color)

        self.on_key_event_once("space", self.state_play)

    def set_duration(self, duration, update_cursor_sequence=True):
        """ the logical duration and the sequence's duration are being updated """
        self.duration = duration

        if update_cursor_sequence == True:
            self.cursor_sequence.set_sequence_params(duration=duration)
            # if it has an EdgePlayerState, otherwise in the update_while_moving_function
            # will fail
            if self.state.get_s_a():
                self.cursor_sequence.update_sequence_graphics()

    def get_duration(self):
        return self.duration

    def update_line(self, update_graphics=True):
        """ set the line to the appropriate dimensions """
        if self.line is None:
            self.line = Line1dSolid()

        if update_graphics == True:
            self.line.setTipPoint(self.get_v1())
            self.line.setTailPoint(self.get_v2())

    def update(self, *args, **kwargs):
        s_a = args[0]
        self.state.set_s_a(s_a)  # update s_a
        self.update_while_moving_function(*args, **kwargs)

    def update_while_moving_function(self, *args, **kwargs):
        """ calculating everything that changes while
        playing """
        # self.state.set_s_a(s_a)  # update s_a

        # covered_time = s_a * (s_l/lps_rate)

        s_l = self.lps_rate * self.get_duration()

        covered_length = s_l * self.state.get_s_a()

        # set cursor point:
        cursor_pos = math_utils.np_to_p3d_Vec3(
            covered_length * math_utils.p3d_to_np(self.get_v_dir()) +
            math_utils.p3d_to_np(self.v1))

        self.p_c.setPos(cursor_pos)

        self.update_line()

    def set_paused(self, a_to_set_paused_at=None):
        self.state.set_paused(a_to_set_paused_at=a_to_set_paused_at)

        if a_to_set_paused_at:
            self.cursor_sequence.set_t(
                a_to_set_paused_at * self.get_duration())
            print("a_to_set_paused_at: ", a_to_set_paused_at)

        self.cursor_sequence.pause()

        self.set_primary_color(self.paused_primary_color)

    def get_v2(self):
        return self.v1 + self.get_v_dir() * self.lps_rate * self.get_duration()
