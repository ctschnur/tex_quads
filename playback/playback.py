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

from statemachine.statemachine import StateMachine, equal_states, BatchEvents


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

    def __init__(self, wave_file_path, *args, **kwargs):
        """ """
        StateMachine.__init__(self, *args, **kwargs)

        self.wf = None
        self.p = None
        self.stream = None
        self.wave_file_path = wave_file_path

        self.transition_into(self.state_load_wav)

        self.play_session_num_frames = 0

        self.s_a = None

        self.add_batch_events_for_setup(
            BatchEvents(
                [self.state_stopped_at_beginning,
                 self.state_stopped_at_end,
                 self.state_play,
                 self.state_pause],
                [lambda: self.on_key_event("a", self.state_stopped_at_beginning),
                 lambda: self.on_key_event("e", self.state_stopped_at_end)]))

    def state_stopped_at_beginning(self, *opt_args):
        """ """
        self.time_to_play_at = 0.
        self.transition_into(self.state_pause)

    def state_stopped_at_end(self, *opt_args):
        """ """
        durat = get_wave_file_duration(self.wave_file_path)
        self.time_to_play_at = durat
        self.transition_into(self.state_pause)

    def state_load_wav(self):
        """ """
        self.load_thread = threading.Thread(target=self.load, daemon=True)
        self.load_thread.start()

        self.on_bool_event(
            lambda: not self.load_thread.is_alive(), self.state_play)

    def state_play(self):
        """ """
        self.play_thread = threading.Thread(target=self.play, daemon=True)
        self.play_thread.start()

        self.on_key_event("space", self.state_pause)

        # self.on_bool_event(
        #     lambda: not self.play_thread.is_alive(), self.ending_state)
        self.on_bool_event(
            lambda: not self.play_thread.is_alive(), self.state_stopped_at_beginning)

    def state_pause(self):
        """ """
        self.on_key_event("space", self.resume_from_pause_state)
        pass

    def ending_state(self):
        """ """
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        self.transition_into(self.ended_state)

    def ended_state(self):
        """ """
        pass

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

    def play(self):
        """ """
        while equal_states(self.get_current_state(), self.state_play):
            if self.stream.is_active() == False:
                self.stream.start_stream()

                # calculate frame number from time
                self.framerate = self.wf.getframerate()
                self.frame_num = int(self.framerate * self.time_to_play_at)

                try:
                    # assuming pos is frame number
                    self.wf.setpos(self.frame_num)
                    self.play_session_num_frames = self.frame_num
                except wave.Error:
                    print("Bad position")
                    break

            data = self.wf.readframes(PlaybackerSM.CHUNK)
            self.play_session_num_frames += int(len(data)/PlaybackerSM.CHUNK)

            if not (len(data) > 0):
                print("-> playing finished, breaking the while loop")
                break

            # this is actually doing the playing (writing to soundcard?)
            self.stream.write(data)

        self.stream.stop_stream()

    def resume_from_pause_state(self):
        """ """
        # remember the position in the buffer
        self.time_to_play_at = self.play_session_num_frames / self.wf.getframerate()

        assert self.play_thread.is_alive() == False
        self.transition_into(self.state_play)
