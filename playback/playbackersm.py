from playback.audiofunctions import get_wave_file_duration
from statemachine.statemachine import StateMachine
import threading
from queue import Queue
import time


from datetime import datetime


import pyaudio
import wave
import sys

import os

import numpy as np

from statemachine.statemachine import StateMachine, equal_states, SMBatchEvents

from plot_utils.edgestate import EdgeState

from sequence.sequence import WavSequence

class PlaybackerSM(StateMachine):
    """ """
    CHUNK = 1024  # number of bytes in a buffer (a buffer is 'one frame')

    t_epsilon = 0.001

    def __init__(self, wave_file_path, *args, **kwargs):
        """ """
        StateMachine.__init__(self, *args, **kwargs)

        self.wf = None
        self.p = None
        self.stream = None
        self.wave_file_path = wave_file_path

        self.duration = get_wave_file_duration(self.wave_file_path)

        # self.transition_into(self.state_load_wav)

        # self.play_session_num_frames = 0

        self.short_skipping_time_step = 0.5

        self.play_thread = None

        self.state = EdgeState()

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

    def state_stopped_at_beginning(self, *opt_args):
        """ """
        # if it's playing, stop it: done automatically by the fact that it transitions out of state_play
        # if it's not loaded? Can't be! loading occurs always in the first state that is entered, the state_load_wav

        self.wav_sequence.pause()
        self.wav_sequence.set_t(0.)

        self.on_key_event_once("space", self.state_play)

    def state_stopped_at_end(self, *opt_args):
        """ """
        self.wav_sequence.finish()

        self.on_key_event_once("arrow_left", self.state_play,
                               next_state_args=(self.get_skipped_time(direction=-1),))


    def state_load_wav(self):
        """ """
        self.wav_sequence = WavSequence(self.wave_file_path,
                                        defer_loading=True)
        self.wav_sequence.start_load_thread()

        def load_thread_done_after_started_p():
            """ """
            res = False
            if self.wav_sequence.load_thread is not None:
                if self.wav_sequence.load_thread.is_alive() == False:
                    res = True
            return res

        self.wav_sequence.start(block_to_join_threads=True, start_paused=True)

        self.on_bool_event(
            load_thread_done_after_started_p,
            self.state_stopped_at_beginning)

    def state_play(self, time=None):
        """ """
        if time is not None:
            a = time / self.get_duration()
            self.wav_sequence.set_t(a * self.get_duration())

        self.wav_sequence.resume()

        self.on_key_event_once("space", self.state_pause)

    def state_pause(self, time=None):
        """ """
        if time is not None:
            self.wav_sequence.set_t(time)

        self.wav_sequence.pause()

        # self.on_key_event_once("space", self.state_resume_from_pause)
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

        calculated_time = (self.wav_sequence.state.get_t() + direction *
                           self.short_skipping_time_step)

        return np.clip(calculated_time, PlaybackerSM.t_epsilon, self.get_duration())

    def get_duration(self):
        """ """
        return self.duration
