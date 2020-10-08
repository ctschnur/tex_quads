import threading
from queue import Queue
import time


from datetime import datetime


import pyaudio
import wave
import sys

import os


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
        """ create and start an audio-playback thread """

        self.wave_file_path = wave_file_path

        if not os.path.isfile(self.wave_file_path):
            print("ERR: not os.path.isfile(self.wave_file_path), ", self.wave_file_path)
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
