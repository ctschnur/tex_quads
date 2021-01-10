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
                    # called_from_sm=self.get_controlling_state_machine()
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
                    # called_from_sm=self.get_controlling_state_machine()
                )]))

    def state_stopped_at_beginning(self, *opt_args):
        """ """
        # if it's playing, stop it: done automatically by the fact that it transitions out of state_play
        # if it's not loaded? Can't be! loading occurs always in the first state that is entered, the state_load_wav
        self.state.set_s_a(0.)

        if self.stream is not None and self.stream.is_active():
            self.stream.stop_stream()

        self.on_key_event_once("space", self.state_play, next_state_args=(0.,))

    def state_stopped_at_end(self, *opt_args):
        """ """
        if self.stream is not None and self.stream.is_active():
            self.stream.stop_stream()

    def state_load_wav(self):
        """ """

        self.load_thread = threading.Thread(target=self.load, daemon=True)
        self.load_thread.start()

        self.on_bool_event(
            lambda: not self.load_thread.is_alive(), self.state_stopped_at_beginning)

    def load(self):
        """ """
        self.wf = wave.open(self.wave_file_path, 'rb')
        # TODO: check rb vs r changes the meaning of self.wf.setpos(...)

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
                                  channels=self.wf.getnchannels(),
                                  rate=self.wf.getframerate(),
                                  output=True)
        # time.sleep(2.)

    def state_play(self, time):
        """ """
        # if this function is called, the state_load_wav has already run and time_to_play must be already defined
        # it starts the play thread if it is not running
        # it starts the stream, which is stopped by the state_stopped... functions
        # print("FROM STATE_PLAY: ", "self.get_current_state(): ", self.get_current_state())

        if self.play_thread is None or self.play_thread.is_alive() == False:
            self.play_thread = threading.Thread(target=self.play, args=(time,), daemon=True)
            self.play_thread.start()
            print("- > starting play thread")

        self.on_key_event_once("space", self.state_pause)

    def play(self, change_time_to=None):
        """ """
        print("equal_states(self.get_current_state(), self.state_play): ",
              equal_states(self.get_current_state(), self.state_play))

        try:
            if change_time_to is not None:
                self.wf.setpos(self.get_framenumber_from_time(change_time_to))
        except wave.Error:
            print("Bad position for start_frame")
            os._exit()

        while (equal_states(self.get_current_state(), self.state_play)):
            data = self.wf.readframes(PlaybackerSM.CHUNK)
            # self.play_session_num_frames += int(len(data)/PlaybackerSM.CHUNK)

            if len(data) > 0:
                # write to sound device

                if self.stream is not None and self.stream.is_active() == False:
                    self.stream.start_stream()

                self.stream.write(data)
            else:
                self.transition_into(self.state_stopped_at_end)
                # this transition happens from inside the thread! But then the thread finishes

    def state_pause(self, change_time_to=None):
        """ """
        if change_time_to is not None:
            self.wf.setpos(change_time_to)

        self.on_key_event_once("space", self.state_resume_from_pause)
        pass

    def state_resume_from_pause(self):
        """ """
        a = self.get_a()
        cur_time = a * self.duration

        self.transition_into(self.state_play, next_state_args=(cur_time, ))

    def state_end(self):
        """ """
        self.stream.close()
        self.p.terminate()


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

        calculated_time = (self.get_a() * self.get_duration() + direction *
                           self.short_skipping_time_step)

        return np.clip(calculated_time, PlaybackerSM.t_epsilon, self.get_duration())

    def get_duration(self):
        """ """
        return self.duration
