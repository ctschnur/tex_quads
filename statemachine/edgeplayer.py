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

from plot_utils.edgegraphics import EdgeGraphics

import playback.audiofunctions

from statemachine.statemachine import StateMachine

# import local_utils.math_utils

from statemachine.statemachine import StateMachine, equal_states, SMBatchEvents

from playback.playbackersm import PlaybackerSM
from plot_utils.graphickersm import GraphickerSM
from playback.audiofunctions import get_wave_file_duration

class EdgePlayerSM(StateMachine):
    """ """

    t_epsilon = 0.001

    def __init__(self, wave_file_path, camera_gear, *args, edge_graphics=None, **kwargs):
        """ """
        StateMachine.__init__(self, *args, **kwargs)

        self.dobj = base

        self.duration = get_wave_file_duration(wave_file_path)

        self.edge_graphics = edge_graphics

        self.pbsm = PlaybackerSM(wave_file_path, taskMgr, directobject=base,
                                 controlling_sm=self)
        # self.pbsm.transition_into(self.pbsm.state_load_wav)

        def on_valid_press_func(a):
            """ """
            time = a * self.get_duration()

            cond1 = math_utils.equal_up_to_epsilon(self.get_t(), time, epsilon=0.01)
            # print("COND: ", cond1, ", :", self.get_t(), time)
            # if cond1 and (self.get_current_state() == self.state_play or self.get_current_state() == self.state_pause):
            #     return

            # print("HEYY a: ", a, "set time to: ", time)

            next_state = None
            current_state = self.get_current_state()
            if current_state != self.state_play:
                next_state = self.state_pause
            else:
                next_state = current_state

            self.transition_into(
                next_state, next_state_args=(time,))

        self.gcsm = GraphickerSM(self.duration, taskMgr, directobject=base,
                                 controlling_sm=self, camera_gear=camera_gear,
                                 edge_graphics=self.edge_graphics, 
                                 on_valid_press_func=on_valid_press_func)

        # self.gcsm.transition_into(self.gcsm.state_load_graphics)

        # self.transition_into(self.state_load)

        self.short_skipping_time_step = 0.5

        # --------

        self.add_batch_events_for_setup(
            SMBatchEvents(
                [self.state_stopped_at_beginning,
                 self.state_stopped_at_end,
                 self.state_play,
                 self.state_pause],
                [lambda: self.on_key_event_once("a", self.state_stopped_at_beginning),
                 lambda: self.on_key_event_once("e", self.state_stopped_at_end)]))

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

    def state_load(self, *opt_args):
        """ """
        self.pbsm.transition_into(self.pbsm.state_load_wav, called_from_sm=self)
        self.gcsm.transition_into(self.gcsm.state_load_graphics, called_from_sm=self)
        print("###: ", self.gcsm.get_current_state())

        self.on_bool_event(
            lambda: (
                not self.pbsm.get_current_state() != self.pbsm.state_load_wav), self.state_stopped_at_beginning, called_from_sm=self)
        # TODO: check why it is registering get_current_state != current, if it's not actually transitioning ...

    def state_stopped_at_beginning(self, *opt_args):
        """ """
        self.pbsm.transition_into(self.pbsm.state_stopped_at_beginning, called_from_sm=self)
        self.gcsm.transition_into(self.gcsm.state_stopped_at_beginning, called_from_sm=self)

        self.on_key_event_once("space", self.state_play)

    def state_stopped_at_end(self, *opt_args):
        """ """
        self.pbsm.transition_into(self.pbsm.state_stopped_at_end, called_from_sm=self)
        self.gcsm.transition_into(self.gcsm.state_stopped_at_end, called_from_sm=self)

        self.on_key_event_once("arrow_left", self.state_play,
                               next_state_args=(self.get_skipped_time(direction=-1),))

    def state_play(self, time=None):
        """ """
        self.pbsm.transition_into(self.pbsm.state_play, next_state_args=(time,),
                                  called_from_sm=self)
        self.gcsm.transition_into(self.gcsm.state_play, next_state_args=(time,),
                                  called_from_sm=self)

        self.on_key_event_once("space", self.state_pause)


    def state_pause(self, time=None):
        """ """
        self.pbsm.transition_into(self.pbsm.state_pause, next_state_args=(time,),
                                  called_from_sm=self)
        self.gcsm.transition_into(self.gcsm.state_pause, next_state_args=(time,),
                                  called_from_sm=self)

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

    def get_skipped_time(self, direction=+1):
        """
        Args:
            direction: +- 1, to indicate if backwards or forwards"""

        calculated_time = (self.get_t() + direction *
                           self.short_skipping_time_step)

        return np.clip(calculated_time, EdgePlayerSM.t_epsilon, self.get_duration())

    def get_t(self):
        """ """
        tp = self.pbsm.wav_sequence.get_t()
        tg = self.gcsm.edge_graphics.cursor_sequence.get_t()

        # assert not math_utils.equal_up_to_epsilon(tp, tg, epsilon=0.005)

        return tp               # just take one of them?

    def get_duration(self):
        """ """
        return self.duration
