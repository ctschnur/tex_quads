from direct.showbase.ShowBase import ShowBase, DirectObject

from simple_objects.primitives import ParametricLinePrimitive
from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk

from composed_objects.composed_objects import Point3dCursor

from panda3d.core import Vec3, Mat4, Vec4

from direct.interval.IntervalGlobal import Wait as P3dWait
from direct.interval.IntervalGlobal import Sequence as P3dSequence



import numpy as np

from plot_utils.edgehoverer import EdgeHoverer, EdgeMouseClicker

from local_utils import math_utils

from sequence.sequence import Sequence

from playback.playbackersm import PlaybackerSM

import os

import inspect

from plot_utils.edgegraphics import EdgeGraphics

import playback.audiofunctions

from plot_utils.edgestate import EdgeState

from statemachine.statemachine import StateMachine, SMBatchEvents

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

    def __init__(self, wave_file_duration, *args, camera_gear=None, **kwargs):
        """ """
        StateMachine.__init__(self, *args, **kwargs)
        EdgeGraphics.__init__(self, *args, **kwargs)

        self.v1 = None
        self.v_dir = None
        self.duration = wave_file_duration
        self.line = None
        self.primary_color = None
        self.cursor_sequence = None
        self.extraArgs = None

        self.camera_gear = camera_gear

        self.state = EdgeState()

        self.add_batch_events_for_setup(
            SMBatchEvents(
                [self.state_stopped_at_beginning,
                 self.state_stopped_at_end,
                 self.state_play,
                 self.state_pause],
                [lambda: self.on_key_event_once(
                    "a", self.state_stopped_at_beginning,
                ),
                 lambda: self.on_key_event_once(
                     "e", self.state_stopped_at_end,
                 )]))

        self.add_batch_events_for_setup(
            SMBatchEvents(
                [self.state_play,
                 self.state_pause],
                [lambda: self.on_key_event_once(
                    "arrow_left",
                    self.state_skip_back,
                    next_state_args=(self.get_current_state(),),
                )]))

        self.add_batch_events_for_setup(
            SMBatchEvents(
                [self.state_stopped_at_beginning,
                 self.state_play,
                 self.state_pause],
                [lambda: self.on_key_event_once(
                    "arrow_right",
                    self.state_skip_forward,
                    next_state_args=(self.get_current_state(),),
                )]))

    def state_stopped_at_beginning(self, *opt_args):
        """ """
        self.cursor_sequence.pause()
        self.cursor_sequence.set_t(0.)

        self.set_primary_color(self.stopped_at_beginning_primary_color)

        self.on_key_event_once("space", self.state_play)

    def state_stopped_at_end(self, *opt_args):
        """ """
        self.cursor_sequence.finish()
        self.set_primary_color(self.stopped_at_end_primary_color)

        self.on_key_event_once("arrow_left", self.state_play,
                               next_state_args=(self.get_skipped_time(direction=-1),))

    def state_load_graphics(self):
        """ """
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

        self.edge_hoverer = EdgeHoverer(self, self.camera_gear)

        self.edge_mouse_clicker = EdgeMouseClicker(self)

        self.transition_into(self.state_stopped_at_beginning)

        # import time
        # time.sleep(2.)

        # P3dSequence(P3dWait(1.)).start()

    def state_play(self, time=None):
        """ """
        if time is not None:
            a = time / self.get_duration()
            self.cursor_sequence.set_t(a * self.get_duration())

        self.cursor_sequence.resume()
        self.set_primary_color(self.playing_primary_color)

        self.on_key_event_once("space", self.state_pause)

    def state_pause(self, time=None):
        """ """
        if time is not None:
            self.cursor_sequence.set_t(time)

        self.cursor_sequence.pause()

        self.set_primary_color(self.paused_primary_color)

        self.on_key_event_once("space", self.state_play)

    # -- skipping begin
    def state_skip_back(self, previous_state):
        """ """
        self.transition_into(
            previous_state, next_state_args=(self.get_skipped_time(direction=-1),))

    def state_skip_forward(self, previous_state):
        """ """
        self.transition_into(
            previous_state, next_state_args=(self.get_skipped_time(direction=+1),))
    # -- end


    # -- all other than states

    def get_skipped_time(self, direction=+1):
        """
        Args:
            direction: +- 1, to indicate if backwards or forwards"""

        calculated_time = (self.cursor_sequence.get_t() + direction *
                           self.short_skipping_time_step)

        return np.clip(calculated_time, GraphickerSM.t_epsilon, self.get_duration())

    def set_duration(self, duration, update_cursor_sequence=True):
        """ the logical duration and the sequence's duration are being updated """
        self.duration = duration

        if update_cursor_sequence == True:
            self.cursor_sequence.set_sequence_params(duration=duration)
            if self.cursor_sequence is not None:
                self.cursor_sequence.update_sequence_graphics()

    def get_duration(self):
        """ """
        return self.duration

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

    def update_while_moving_function(self, a, *args, **kwargs):
        """ calculating everything that changes while
        playing """
        # self.state.set_s_a(s_a)  # update s_a

        # covered_time = s_a * (s_l/lps_rate)

        s_l = self.lps_rate * self.get_duration()

        # covered_length = s_l * self.state.get_s_a()
        covered_length = s_l * a

        # set cursor point:
        cursor_pos = math_utils.np_to_p3d_Vec3(
            covered_length * math_utils.p3d_to_np(self.get_v_dir()) +
            math_utils.p3d_to_np(self.v1))

        self.p_c.setPos(cursor_pos)

        self.update_line()

    def get_v2(self):
        return self.v1 + self.get_v_dir() * self.lps_rate * self.get_duration()


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

        self.space_direct_object.ignoreAll()
        self.space_direct_object.removeAllTasks()

        # setup keys for jumping to beginning/end
        self.set_stopped_at_beginning_direct_object.ignoreAll()
        self.set_stopped_at_beginning_direct_object.removeAllTasks()

        self.set_stopped_at_end_direct_object.ignoreAll()
        self.set_stopped_at_end_direct_object.removeAllTasks()

        self.set_short_forward_direct_object.ignoreAll()
        self.set_short_forward_direct_object.removeAllTasks()

        self.set_short_backward_direct_object.ignoreAll()
        self.set_short_backward_direct_object.removeAllTasks()
