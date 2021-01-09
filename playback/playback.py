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


class Playbacker:
    """ Handling audio playback (thread in parallel to rendering). """

    CHUNK = 1024  # number of bytes in a buffer (a buffer is 'one frame')

    def __init__(self):
        """ Call do_playback to initiate stuff. """

        # --- state swiches, controlled from outside ---

        # this function is queried to know if to stop the playback or go on
        # it should return True or False

        # tip: plug in the edgeplayer functions here
        self.is_playing_query_function = None
        self.is_paused_query_function = None
        self.is_playing_stopped_query_function = None

        self.play_at_time_query_function = None

        self.wave_file_path = None

        self.playbacker_thread = None

        self._playbacker_thread_done = None

        self.short_skipping_time_step = 1.

        pass

    def is_playbacker_thread_done(self):
        return self._playbacker_thread_done

    def do_playback(self,
                    is_playing_query_function,
                    is_paused_query_function,
                    is_playing_stopped_query_function,
                    play_at_time_query_function,
                    wave_file_path):
        """ at each press of the play button,
            - open a new thread
            - assign a set of audio state variables that can be accessed from both threads.
              - in the rendering thread (which is considered to never be blocked), a task is run monitoring the state of the audio playbacker thread
                - the actual playback is started only after the setup of the playback is done (playback_setup_done)
            - open a file for streaming

            - play the file at the time of the cursor

            """

        self.wave_file_path = wave_file_path

        if not os.path.isfile(self.wave_file_path):
            print("ERR: not os.path.isfile(self.wave_file_path), ",
                  self.wave_file_path)
            os._exit(1)

        self.playbacker_thread = threading.Thread(
            target=self.playback_blocking_mode)

        self.playbacker_thread.deamon = True  # end the thread if the main thread ends
        # TODO: check if this actually works in p3d, or if the callback for an event has
        # it's own thread which terminates immediately after the callback has been processed

        self.playbacker_thread.start()

        self.frames = []
        self.is_playing_query_function = (
            is_playing_query_function)

        self.is_paused_query_function = (
            is_paused_query_function)

        self.is_playing_stopped_query_function = (
            is_playing_stopped_query_function)

        self.play_at_time_query_function = (
            play_at_time_query_function
        )

        return self.playbacker_thread, self.wave_file_path

    def end_playback(self):
        """ """
        assert self.playbacker_thread.is_alive()
        print("end_playback. thread ended?")

    def playback_blocking_mode(self):
        """ boilerplate playback code for blocking mode """

        self._playbacker_thread_done = False

        if self.is_playing_query_function is None:
            print("is_playing_query_function is None, ",
                  " call do_playback before playback")
            os._exit()

        # wave_file_path = (
        #     os.path.join(os.getcwd(),
        #                  "local_tests/playing_back_audio/"
        #                  "test.wav"))

        wf = wave.open(self.wave_file_path, 'rb')
        # TODO: check rb vs r changes the meaning of wf.setpos(...)

        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        print("playback_blocking_mode: start playback")

        play_at_time = None

        while True:
            if (self.is_playing_query_function() == True):

                if stream.is_active() == False:
                    stream.start_stream()

                    play_at_time = self.play_at_time_query_function()

                    # calculate frame number from time
                    framerate = wf.getframerate()
                    frame_num = framerate * play_at_time

                    try:
                        wf.setpos(frame_num)  # assuming pos is frame number
                    except wave.Error:
                        print("Bad position")
                        os._exit()

                data = wf.readframes(Playbacker.CHUNK)

                if not (len(data) > 0):
                    print("-> playing finished, breaking the while loop")
                    break

                # this is actually doing the playing (writing to soundcard?)
                stream.write(data)

                # print("-> stream.is_active(): ", stream.is_active())
                # print("-> appending chunks: ", len(data))
            elif (self.is_paused_query_function() == True):
                if stream.is_active() == True:
                    stream.stop_stream()

                # print("-> stream.is_active(): ", stream.is_active())
                # print("-> playing paused, stopping stream")
            elif (self.is_playing_stopped_query_function() == True):
                print("-> playing stopped, breaking the while loop")
                break

        print("playback_blocking_mode: done with playback")

        stream.stop_stream()
        stream.close()
        p.terminate()

        self.end_playback()

        self._playbacker_thread_done = True

        # at this point, the playback thread is done
        # from the main loop of an outside rendering thread, the state can be queried
        # by calling self.playback.is_playbacker_thread_done()


class Playbacker:
    """ Handling audio playback (thread in parallel to rendering). """

    CHUNK = 1024  # number of bytes in a buffer (a buffer is 'one frame')

    def __init__(self):
        """ Call do_playback to initiate stuff. """

        # --- state swiches, controlled from outside ---

        # this function is queried to know if to stop the playback or go on
        # it should return True or False

        # tip: plug in the edgeplayer functions here
        self.is_playing_query_function = None
        self.is_paused_query_function = None
        self.is_playing_stopped_query_function = None

        self.play_at_time_query_function = None

        self.wave_file_path = None

        self.playbacker_thread = None

        self._playbacker_thread_done = None

        pass

    def is_playbacker_thread_done(self):
        return self._playbacker_thread_done

    def do_playback(self,
                    is_playing_query_function,
                    is_paused_query_function,
                    is_playing_stopped_query_function,
                    play_at_time_query_function,
                    wave_file_path):
        """ at each press of the play button,
            - open a new thread
            - assign a set of audio state variables that can be accessed from both threads.
              - in the rendering thread (which is considered to never be blocked), a task is run monitoring the state of the audio playbacker thread
                - the actual playback is started only after the setup of the playback is done (playback_setup_done)
            - open a file for streaming

            - play the file at the time of the cursor

            """

        self.wave_file_path = wave_file_path

        if not os.path.isfile(self.wave_file_path):
            print("ERR: not os.path.isfile(self.wave_file_path), ",
                  self.wave_file_path)
            os._exit(1)

        self.playbacker_thread = threading.Thread(
            target=self.playback_blocking_mode)

        self.playbacker_thread.deamon = True  # end the thread if the main thread ends
        # TODO: check if this actually works in p3d, or if the callback for an event has
        # it's own thread which terminates immediately after the callback has been processed

        self.playbacker_thread.start()

        self.frames = []
        self.is_playing_query_function = (
            is_playing_query_function)

        self.is_paused_query_function = (
            is_paused_query_function)

        self.is_playing_stopped_query_function = (
            is_playing_stopped_query_function)

        self.play_at_time_query_function = (
            play_at_time_query_function
        )

        return self.playbacker_thread, self.wave_file_path

    def end_playback(self):
        """ """
        assert self.playbacker_thread.is_alive()
        print("end_playback. thread ended?")

    def playback_blocking_mode(self):
        """ boilerplate playback code for blocking mode """

        self._playbacker_thread_done = False

        if self.is_playing_query_function is None:
            print("is_playing_query_function is None, ",
                  " call do_playback before playback")
            os._exit()

        # wave_file_path = (
        #     os.path.join(os.getcwd(),
        #                  "local_tests/playing_back_audio/"
        #                  "test.wav"))

        self.wf = wave.open(self.wave_file_path, 'rb')
        # TODO: check rb vs r changes the meaning of self.wf.setpos(...)

        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(self.wf.getsampwidth()),
                        channels=self.wf.getnchannels(),
                        rate=self.wf.getframerate(),
                        output=True)

        print("playback_blocking_mode: start playback")

        play_at_time = None

        while True:
            if (self.is_playing_query_function() == True):

                if stream.is_active() == False:
                    stream.start_stream()

                    play_at_time = self.play_at_time_query_function()

                    # calculate frame number from time
                    framerate = self.wf.getframerate()
                    frame_num = framerate * play_at_time

                    try:
                        # assuming pos is frame number
                        self.wf.setpos(frame_num)
                    except wave.Error:
                        print("Bad position")
                        os._exit()

                data = self.wf.readframes(Playbacker.CHUNK)

                if not (len(data) > 0):
                    print("-> playing finished, breaking the while loop")
                    break

                # this is actually doing the playing (writing to soundcard?)
                stream.write(data)

                # print("-> stream.is_active(): ", stream.is_active())
                # print("-> appending chunks: ", len(data))
            elif (self.is_paused_query_function() == True):
                if stream.is_active() == True:
                    stream.stop_stream()

                # print("-> stream.is_active(): ", stream.is_active())
                # print("-> playing paused, stopping stream")
            elif (self.is_playing_stopped_query_function() == True):
                print("-> playing stopped, breaking the while loop")
                break

        print("playback_blocking_mode: done with playback")

        stream.stop_stream()
        stream.close()
        p.terminate()

        self.end_playback()

        self._playbacker_thread_done = True

        # at this point, the playback thread is done
        # from the main loop of an outside rendering thread, the state can be queried
        # by calling self.playback.is_playbacker_thread_done()



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
                    self.skip_back_state,
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
                    self.skip_forward_state,
                    next_state_args=(self.get_current_state(),),
                    # called_from_sm=self.get_controlling_state_machine()
                )]))

    def state_stopped_at_beginning(self, *opt_args):
        """ """
        # if it's playing, stop it: done automatically by the fact that it transitions out of state_play
        # if it's not loaded? Can't be! loading occurs always in the first state that is entered, the state_load_wav
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

    def get_a_internally(self):
        """ """
        assert self.wf

        current_time = float(self.wf.tell()) / float(self.wf.getframerate())
        return current_time / self.duration

    def get_framenumber_from_time(self, time):
        """ """
        start_frame = int(time * self.wf.getframerate())
        assert time <= self.duration
        return start_frame

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
                self.transition_into(self.state_stopped_at_end)  # this transition happens from inside the thread! But then the thread finishes

    def state_pause(self, change_time_to=None):
        """ """
        if change_time_to is not None:
            self.wf.setpos(change_time_to)

        self.on_key_event_once("space", self.resume_from_pause_state)
        pass

    def resume_from_pause_state(self):
        """ """
        a = self.get_a_internally()
        cur_time = a * self.duration

        self.transition_into(self.state_play, next_state_args=(cur_time, ))

    def state_end(self):
        """ """
        self.stream.close()
        self.p.terminate()

    def skip_back_state(self, previous_state):
        """ """
        self.transition_into(
            previous_state, next_state_args=(self.get_skipped_time(direction=-1),))

    def skip_forward_state(self, previous_state):
        """ """
        self.transition_into(
            previous_state, next_state_args=(self.get_skipped_time(direction=+1),))

    def get_skipped_time(self, direction=+1):
        """
        Args:
            direction: +- 1, to indicate if backwards or forwards"""

        calculated_time = (self.get_a_internally() * self.get_duration() + direction *
                           self.short_skipping_time_step)

        return np.clip(calculated_time, PlaybackerSM.t_epsilon, self.get_duration())

    def get_duration(self):
        """ """
        return self.duration
