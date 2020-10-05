import direct.interval.IntervalGlobal
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval


class SequenceState:
    """ a state of a sequence (it can be playing or paused, essentially)
    and has a duration and a playing parameter `a` between 0 and 1 """
    def __init__(self):
        self.a = None  # this parameter should be set from wihin the update_while_moving_function
        self.duration = None
        pass

class Sequence:
    """ wrapper around p3d sequences with basic start/stop/setting
    duration and playing parameter (between 0 and 1) functionality """
    def __init__(self):
        self.extraArgs = None
        self.update_while_moving_function = None
        self.on_finish_function = None

        self.p3d_cursor_sequence = None
        self.p3d_interval = None

        self.state = SequenceState()
        pass

    def set_sequence_params(self, **kwargs):
        """ update the p3d sequence to have a specific duration, extraArgs, and update function
        The sequence will be (at first) only created and not restarted.

        Since a sequence's duration is determined on start time
        kwars:
        - duration: duration of the p3d sequence in seconds
        - extraArgs: extra arguments that the sequence update function receives
        - update_while_moving_function
        - on_finish_function """

        create_lerp_and_seq = True

        if 'duration' in kwargs:
            self.duration = kwargs.get('duration')
        elif self.duration is None:
            print("Warning: LerpFunc will not be created yet, self.duration is None")
            create_lerp_and_seq = False

        if 'extraArgs' in kwargs:
            self.extraArgs = kwargs.get('extraArgs')
        elif self.extraArgs is None:
            print("Warning: LerpFunc will not be created yet, self.extraArgs is None")
            create_lerp_and_seq = False

        if 'update_while_moving_function' in kwargs:
            self.update_while_moving_function = kwargs.get('update_while_moving_function')
        elif self.update_while_moving_function is None:
            print("Warning: LerpFunc will not be created yet, self.update_while_moving_function is None")
            create_lerp_and_seq = False

        if 'on_finish_function' in kwargs:
            self.on_finish_function = kwargs.get('on_finish_function')
        elif self.on_finish_function is None:
            print("Warning: LerpFunc will not be created yet, self.on_finish_function is None")
            create_lerp_and_seq = False


        if self.p3d_cursor_sequence:
            self.p3d_cursor_sequence.pause()  # remove it from the interval manager
            del self.p3d_cursor_sequence  # remove the reference

        if create_lerp_and_seq == True:
            self.p3d_interval = LerpFunc(
                self.update_while_moving_function,
                duration=self.duration,
                extraArgs=self.extraArgs)

            self.p3d_cursor_sequence = direct.interval.IntervalGlobal.Sequence(
                self.p3d_interval,
                direct.interval.IntervalGlobal.Func(self.on_finish_function))

    def remove(self):
        """ unregister the sequence """
        self.p3d_cursor_sequence.pause()  # removes it from the interval manager

        self.p3d_cursor_sequence = None # remove the reference
        self.p3d_interval = None

    def get_t(self):
        return self.p3d_cursor_sequence.get_t()

    def set_t(self, t):
        self.p3d_cursor_sequence.set_t(t)

    def pause(self):
        self.p3d_cursor_sequence.pause()

    def resume(self):
        self.p3d_cursor_sequence.resume()

    def start(self):
        self.p3d_cursor_sequence.start()

    def finish(self):
        self.p3d_cursor_sequence.finish()
