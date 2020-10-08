import pyaudio
import wave
import sys
import os

CHUNK = 1024

wave_file_path = (
    os.path.join(os.getcwd(),
                 "local_tests/playing_back_audio/"
                 "test.wav"))

if not os.path.isfile(wave_file_path):
    print("not os.path.isfile(wave_file_path), ", wave_file_path)
    os._exit(1)

wf = wave.open(wave_file_path, 'rb')

p = pyaudio.PyAudio()

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=wf.getnchannels(),
                rate=wf.getframerate(),
                output=True)

while True:
    data = wf.readframes(CHUNK)

    if not (len(data) > 0):
        break

    stream.write(data)

# # read data
# data = wf.readframes(CHUNK)

# # play stream (3)
# while len(data) > 0:
#     stream.write(data)
#     data = wf.readframes(CHUNK)

# stop stream (4)
stream.stop_stream()
stream.close()

# close PyAudio (5)
p.terminate()
