from recording.recorder import Recorder
from recording.recorder_for_live_updating import Recorder_for_live_updating

import scipy
from scipy import fftpack

import numpy as np

class StreamFramesFromRecorder:
    """ stream the frames from the recorder to a Frame2d """
    def __init__(self, f2d):
        self.f2d = f2d
        self.recorder = Recorder_for_live_updating()
        self.recorder.do_record(
            lambda: True,
            lambda: False,
            lambda: False)

        self.factor = 1.0e-1 * 0.2

        self.f2d.set_ylim(-0.25, 2.)
        self.f2d.set_xlim(0., 22028. * self.factor)

        taskMgr.add(self.update_task, 'foo')

    def update_task(self, task):
        if self.recorder.is_recorder_thread_done() == True:
            return task.done
        elif (self.recorder.is_recorder_thread_done() == False):
            self.render_last_frame()
            return task.cont
        elif (self.recorder.is_recorder_thread_done() is None):
            return task.cont

    def render_last_frame(self):
        y = self.recorder.grab_last_frames(num=5)

        if y is not None:
            y = np.fromstring(np.ravel(y), dtype=np.int32)
            y = np.abs(scipy.fft(y))
            freqs = fftpack.fftfreq(len(y), (1./Recorder_for_live_updating.RATE))

            x = freqs

            y = y[:int(len(y) * self.factor)]
            x = x[:int(len(x) * self.factor)]

            y /= (1e11 * 0.5)

            self.f2d.clear_plot()
            self.f2d.plot(x, y)

class StreamFramesFromRecorderTimeDomain:
    """ stream the frames from the recorder to a Frame2d """
    def __init__(self, f2d):
        self.f2d = f2d
        self.recorder = Recorder_for_live_updating()
        self.recorder.do_record(
            lambda: True,
            lambda: False,
            lambda: False)

        max_ampl = 1.0
        self.f2d.set_ylim(-max_ampl, max_ampl)
        self.f2d.set_xlim(0., 1.)

        taskMgr.add(self.update_task, 'foo2')

    def update_task(self, task):
        if self.recorder.is_recorder_thread_done() == True:
            return task.done
        elif (self.recorder.is_recorder_thread_done() == False):
            self.render_last_frame()
            return task.cont
        elif (self.recorder.is_recorder_thread_done() is None):
            return task.cont

    def render_last_frame(self):
        """ 0 < a < 1 """
        y = self.recorder.grab_last_frames(num=1)

        if y is not None:
            y = np.fromstring(np.ravel(y), dtype=np.int32)
            sample_down_indices = np.linspace(0, len(y), num=100).astype(int)[:-1]

            y = y[sample_down_indices]
            y = y * 1.5e-9 * 5

            t = np.linspace(0., 1., num=len(y)) # ?
            x = t

            self.f2d.clear_plot()
            self.f2d.plot(x, y)


# ----------- usage -------------
# f2d3 = Frame2d(camera_gear=cg, attach_to_space="render", update_labels_orientation=True)
# f2d3.set_figsize(0.8, 0.5)

# sffr = StreamFramesFromRecorder(f2d3)
