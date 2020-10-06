import threading
from queue import Queue
import time


from datetime import datetime


import pyaudio
import wave
import sys

import os

class Recorder:
    """ There should be one recording going on at a time in the program (so far).
    Therefore, this is a class that encapsulates global variables and
    static methods. """

    CHUNK = 1024  # number of bytes in a buffer (a buffer is 'one frame')
    FORMAT = pyaudio.paInt16  # 16 bit per sample (audio bit depth)
    CHANNELS = 2
    RATE = 44100  # sample rate (i.e. how many times per second is a sample produced)
    # a sample is a number (all samples make up the discrete approximate
    # representation of the the wave that is heard)

    # RECORD_SECONDS = 5

    num_of_chunks_to_cut_away_end = 8
    num_of_chunks_to_drop_start = 5

    # TODO: calculate amount of time to cut away (makes more sense as measure
    # independent of the chunk size, rate, channels and format)

    def __init__(self):
        """ Call do_record to initiate stuff. """

        self.frames = []

        # --- state swiches, controlled from outside ---

        # this function is queried to know if to stop the recording or go on
        # it should return True or False

        # tip: plug in the edgerecorder functions here
        self.is_recording_query_function = None
        self.is_paused_query_function = None
        self.is_recording_finished_query_function = None

        self.output_filename = None

        self.recorder_thread = None

        self._recorder_thread_done = None

        pass

    def is_recorder_thread_done(self):
        return self._recorder_thread_done

    @staticmethod
    def get_current_output_filename():
        now = datetime.now() # current date and time
        return ("/home/chris/Desktop/output_" +
                now.strftime("%Y-%m-%d_%H.%M.%S") + ".wav")

    def do_record(self,
                  is_recording_query_function,
                  is_paused_query_function,
                  is_recording_finished_query_function):
        """ create and start an audio-recording thread """

        self.output_filename = Recorder.get_current_output_filename()

        self.recorder_thread = threading.Thread(
            target=self.record_blocking_mode)

        self.recorder_thread.deamon = True  # end the thread if the main thread ends
        # TODO: check if this actually works in p3d, or if the callback for an event has
        # it's own thread which terminates immediately after the callback has been processed

        self.recorder_thread.start()

        self.frames = []
        self.is_recording_query_function = (
            is_recording_query_function)

        self.is_paused_query_function = (
            is_paused_query_function)

        self.is_recording_finished_query_function = (
            is_recording_finished_query_function)

        return self.recorder_thread, self.output_filename

    def end_record(self):
        """ """
        assert self.recorder_thread.is_alive()
        print("end_record. thread ended?")
        # return self.output_filename

    def record_blocking_mode(self):
        """ boilerplate recording code for blocking mode """
        p = pyaudio.PyAudio()

        stream = p.open(format=Recorder.FORMAT,
                            channels=Recorder.CHANNELS,
                            rate=Recorder.RATE,
                            input=True,  # input stream: recording
                            frames_per_buffer=Recorder.CHUNK,
                        start=False  # start stream immediately, default: True
                        # stream_callback=my_callback  # no callback in blocking-mode
                        )

        self._recorder_thread_done = False

        print("record_blocking_mode: start recording")

        # for i in range(0, int(Recorder.RATE / Recorder.CHUNK * Recorder.RECORD_SECONDS)):
        if self.is_recording_query_function is None:
            print("is_recording_query_function is None, ",
                  " call do_record before recording")
            os._exit()


        # crude cutting away of spacebar sound
        start_positions = []  # length of the frames array when hitting spacebar to start
        stop_positions = []  # length of the frames array when hitting spacebar to stop

        while True:
            if (self.is_recording_query_function() == True):

                if stream.is_active() == False:
                    stream.start_stream()
                    start_positions.append(len(self.frames))

                data = stream.read(Recorder.CHUNK)
                self.frames.append(data)

                # print("-> stream.is_active(): ", stream.is_active())
                # print("-> appending chunks: ", len(data))

            elif (self.is_paused_query_function() == True):
                if stream.is_active() == True:
                    stream.stop_stream()
                    stop_positions.append(len(self.frames))

                # print("-> stream.is_active(): ", stream.is_active())
                # print("-> paused, not appending to frames, but stopping stream")
            elif (self.is_recording_finished_query_function() == True):
                print("-> finished, breaking the while loop, not appending to frames")
                break

        print("record_blocking_mode: done recording")

        # if it has not been paused before finishing
        if stop_positions and stop_positions[-1] != len(self.frames):
            stop_positions.append(len(self.frames))

        stream.stop_stream()
        stream.close()
        p.terminate()


        # -- now do the 'filtering'/cutting
        frames_new = self.frames.copy()

        print("start_positions: ", start_positions)
        print("stop_positions: ", stop_positions)
        # print("zip(start_positions, stop_positions): ",
        #       zip(start_positions, stop_positions))

        start_positions.reverse()
        stop_positions.reverse()

        for startp, stopp in zip(start_positions, stop_positions):
            print("startp: ", startp, ", " "stopp: ", stopp)
            
            prev_length = len(frames_new)

            if ((stopp - Recorder.num_of_chunks_to_cut_away_end)
                > (startp + Recorder.num_of_chunks_to_drop_start)):
                frames_new[stopp - Recorder.num_of_chunks_to_cut_away_end:stopp] = []
                frames_new[startp:startp + Recorder.num_of_chunks_to_drop_start] = []
                print("trimmed frames_new from", prev_length, "to", len(frames_new))
            else:
                print("Warning: Don't press the recording start/stop so fast one after",
                      "the other! -> not trimming")

        self.frames = frames_new

        # -- save to file

        wf = wave.open(self.output_filename, 'wb')
        wf.setnchannels(Recorder.CHANNELS)
        wf.setsampwidth(p.get_sample_size(Recorder.FORMAT))
        wf.setframerate(Recorder.RATE)
        wf.writeframes(b''.join(self.frames))
        wf.close()

        print("frames written to ", self.output_filename,
              "len(frames): ", len(self.frames))

        self.end_record()

        self._recorder_thread_done = True

        # at this point, the recorder thread is done
        # from the main loop of an outside rendering thread, the state can be queried
        # by calling self.recorder.is_recorder_thread_done()
