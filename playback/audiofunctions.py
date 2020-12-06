import pyaudio
import wave
import sys
import os

import contextlib


def get_wave_file_duration(filepath):
    """ get the duration of a .wav file """
    # filepath = "/home/chris/Desktop/playbacktest.wav"
    with contextlib.closing(wave.open(filepath, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames/float(rate)
        # print(duration)
        return duration
