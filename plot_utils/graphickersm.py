from direct.showbase.ShowBase import ShowBase, DirectObject

from simple_objects.primitives import ParametricLinePrimitive
from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk

from composed_objects.composed_objects import Point3dCursor

from panda3d.core import Vec3, Mat4, Vec4

from direct.interval.IntervalGlobal import Wait as P3dWait
from direct.interval.IntervalGlobal import Sequence as P3dSequence



import numpy as np

from plot_utils.edgemousetools import EdgeHoverer, EdgeMouseClicker

from local_utils import math_utils

from sequence.sequence import Sequence

from playback.playbackersm import PlaybackerSM

import os

import inspect

from plot_utils.edgegraphics import EdgeGraphics

import playback.audiofunctions

from statemachine.statemachine import StateMachine, SMBatchEvents

import threading


class GraphickerSM(StateMachine):
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

    short_skipping_time_step = 0.5

    def __init__(self, wave_file_duration, *args, camera_gear=None, edge_graphics=None, on_valid_press_func=None, **kwargs):
        """ """
        StateMachine.__init__(self, *args, **kwargs)

        self.edge_graphics = None
        if edge_graphics is None:
            self.edge_graphics = EdgeGraphics(get_lps_rate_func=lambda: GraphickerSM.lps_rate, get_duration_func=lambda: self.get_duration())
        else:
            self.edge_graphics = edge_graphics

        self.on_valid_press_func = on_valid_press_func # for edgemouseclicker

        self.duration = wave_file_duration
        self.camera_gear = camera_gear

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
        self.edge_graphics.cursor_sequence.pause()
        self.edge_graphics.cursor_sequence.set_t(0.)

        self.edge_graphics.set_primary_color(self.stopped_at_beginning_primary_color)

        self.on_key_event_once("space", self.state_play)

    def state_stopped_at_end(self, *opt_args):
        """ """
        self.edge_graphics.cursor_sequence.finish()
        self.edge_graphics.set_primary_color(self.stopped_at_end_primary_color)

        self.on_key_event_once("arrow_left", self.state_play,
                               next_state_args=(self.get_skipped_time(direction=-1),))

    def state_load_graphics(self):
        """ """
        self.edge_graphics.init_edge_graphics_by_setters()

        self.set_duration(self.duration, update_cursor_sequence=False)

        # -- do graphics stuff
        self.edge_graphics.p_c = Point3dCursor(self.edge_graphics.get_v1(), self.camera_gear)
        self.edge_graphics.p_c.reparentTo(self.edge_graphics)

        self.edge_graphics.update_line()

        self.edge_graphics.set_primary_color(
            self.stopped_at_beginning_primary_color)  # initially

        self.edge_graphics.cursor_sequence = Sequence()
        self.extraArgs = []
        self.edge_graphics.cursor_sequence.set_sequence_params(
            duration=self.get_duration(),
            extraArgs=self.extraArgs,
            update_function=self.edge_graphics.update,
            on_finish_function=lambda: self.transition_into(self.state_stopped_at_end))

        # -- init hover and click actions
        self.edge_hoverer = EdgeHoverer(self.edge_graphics, self.camera_gear)

        self.edge_mouse_clicker = EdgeMouseClicker(self.edge_graphics, self.edge_hoverer, self.on_valid_press_func)

        self.transition_into(self.state_stopped_at_beginning)

    def state_play(self, time=None):
        """ """
        if time is not None:
            a = time / self.get_duration()
            self.edge_graphics.cursor_sequence.set_t(a * self.get_duration())

        self.edge_graphics.cursor_sequence.resume()
        self.edge_graphics.set_primary_color(self.playing_primary_color)

        self.on_key_event_once("space", self.state_pause)

    def state_pause(self, time=None):
        """ """

        # print("SETZE Zeit, ", time)
        if time is not None:
            self.edge_graphics.cursor_sequence.set_t(time)

        self.edge_graphics.cursor_sequence.pause()

        self.edge_graphics.set_primary_color(self.paused_primary_color)

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

        calculated_time = (self.edge_graphics.cursor_sequence.get_t() + direction *
                           self.short_skipping_time_step)

        return np.clip(calculated_time, GraphickerSM.t_epsilon, self.get_duration())

    def set_duration(self, duration, update_cursor_sequence=True):
        """ the logical duration and the sequence's duration are being updated """
        self.duration = duration

        if update_cursor_sequence == True:
            self.edge_graphics.cursor_sequence.set_sequence_params(duration=duration)
            if self.edge_graphics.cursor_sequence is not None:
                self.edge_graphics.cursor_sequence.update_sequence_graphics()

    def get_duration(self):
        """ """
        return self.duration

    def remove(self):
        """ """
        self.edge_graphics.remove()
