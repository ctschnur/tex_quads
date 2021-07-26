import pyaudio
import wave
import sys
import os

import contextlib

CHUNK = 1024  # number of bytes in a buffer (a buffer is 'one frame')

def get_wave_file_duration(filepath):
    """ get the duration of a .wav file """
    # filepath = "/home/chris/Desktop/playbacktest.wav"
    with contextlib.closing(wave.open(filepath, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames/float(rate)
        # print(duration)
        return duration

def get_wave_file_number_of_frames(filepath):
    """ get the duration of a .wav file """
    # filepath = "/home/chris/Desktop/playbacktest.wav"
    with contextlib.closing(wave.open(filepath, 'r')) as f:
        frames = f.getnframes()
        return frames
