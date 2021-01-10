import direct.interval.IntervalGlobal
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

import playback.audiofunctions
import threading
import wave
import pyaudio


class SequenceState:
    """ a state of a sequence (it can be playing or paused, essentially)
    and has a duration and a playing parameter `a` between 0 and 1 """
    def __init__(self):
        self.a = None  # this parameter should be set from wihin the update_function
        self.duration = None
        pass

    def calc_t(self):
        """ """
        return self.a * self.duration

    def set_t(self, t):
        """ """
        assert t <= self.duration
        self.a = float(t) / float(self.duration)

    def get_t(self):
        """ """
        # assert 1. <= self.a
        if self.a > 1.:
            print("WARNING: self.a > 1.: ", self.a)
        t = self.a * self.duration
        # assert t <= self.duration
        if not (t <= self.duration):
            print("WARNING: not (t <= self.duration): t: ", t,
                  ", self.duration: ", self.duration)
        
        return self.a * self.duration

class Sequence:
    """ wrapper around p3d sequences with basic start/stop/setting
    duration and playing parameter (between 0 and 1) functionality """
    def __init__(self, **kwargs):
        """ update the p3d sequence to have a specific duration, extraArgs, and update function
        The sequence will be (at first) only created and not restarted.

        Since a sequence's duration is determined on start time
        Args:
            **kwargs: passthrough kwargs: see docstring of set_sequence_params """

        self.extraArgs = None
        self.update_function = None
        self.on_finish_function = None

        self.p3d_sequence = None
        self.p3d_interval = None

        self.state = SequenceState()

        self.set_sequence_params(**kwargs)

    def update_sequence_graphics(self):
        """ whatever the state of the sequence is, run the function to update the graphics """

        if self.p3d_sequence:  # it had been created, such that we had enough parameters
            a = self.get_t() # FIXME? a is between 0 and 1, right? t should be different!
            self.state.a = a
            self.p3d_sequence.set_t(self.state.calc_t())

    def set_sequence_params(self, **kwargs):
        """ update the p3d sequence to have a specific duration, extraArgs, and update function.
        This does not call the graphics update function afterwards automatically.
        The sequence will be (at first) only created and not restarted.

        Since a sequence's duration is determined on start time
        kwars:
        - duration: duration of the p3d sequence in seconds
        - extraArgs: extra arguments that the sequence update function receives
        - update_function: function with signature: (a : parameter in interval between 0 (beginning) and 1 (end), )
        - on_finish_function """

        create_lerp_and_seq = True

        if 'duration' in kwargs:
            self.state.duration = kwargs.get('duration')
        elif self.state.duration is None:
            print("Warning: LerpFunc will not be created yet, self.duration is None")
            create_lerp_and_seq = False

        if 'extraArgs' in kwargs:
            self.extraArgs = kwargs.get('extraArgs')
        elif self.extraArgs is None:
            print("Warning: LerpFunc will not be created yet, self.extraArgs is None")
            create_lerp_and_seq = False

        if 'update_function' in kwargs:
            self.update_function = kwargs.get('update_function')
        elif self.update_function is None:
            print("Warning: LerpFunc will not be created yet, self.update_function is None")
            create_lerp_and_seq = False

        if 'on_finish_function' in kwargs:
            self.on_finish_function = kwargs.get('on_finish_function')
        elif self.on_finish_function is None:
            # print("Warning: LerpFunc will not be created yet, self.on_finish_function is None")
            self.on_finish_function = lambda: None
            # create_lerp_and_seq = False


        if self.p3d_sequence:
            self.p3d_sequence.pause()  # remove it from the interval manager
            del self.p3d_sequence  # remove the reference

        if create_lerp_and_seq == True:
            self.p3d_interval = LerpFunc(
                self.update_function,
                duration=self.state.duration,
                extraArgs=self.extraArgs)

            self.p3d_sequence = direct.interval.IntervalGlobal.Sequence(
                self.p3d_interval,
                direct.interval.IntervalGlobal.Func(self.on_finish_function))

        return self  # in order to

    def remove(self):
        """ unregister the sequence """
        self._finish_up_resouces_from_inside_play_loop()

    def get_t(self):
        return self.p3d_sequence.get_t()

    def set_t(self, t):
        self.p3d_sequence.set_t(t)

    def pause(self):
        self.p3d_sequence.pause()

    def resume(self):
        self.p3d_sequence.resume()

    def start(self):
        self.p3d_sequence.start()

    def finish(self):
        self.p3d_sequence.finish()



class WavSequence:
    """ wrapper around wave and pyaudio functionality for playing a wav file """
    def __init__(self, wave_file_path, **kwargs):
        """ update the p3d sequence to have a specific duration, update_function_extra_args, and update function
        The sequence will be (at first) only created and not restarted.

        Since a sequence's duration is determined on start time
        Args:
            **kwargs: passthrough kwargs: see docstring of set_sequence_params """

        self.wave_file_path = wave_file_path

        self.update_function_extra_args = None
        self.update_function_kwargs = None

        self.update_function = None
        self.on_finish_function = None

        self.defer_loading = None

        self.wf = None
        # TODO: check rb vs r changes the meaning of self.wf.setpos(...)
        self.p = None
        self.stream = None
        self.load_thread = None  # threading.Thread(target=self.load, daemon=True)
        self.play_thread = None  # threading.Thread(target=self.play, args=(time,), daemon=True)

        self.playing_p = False
        self.break_play_loop_p = True

        self.state = SequenceState()

        self.set_sequence_params(**kwargs)

    def update_sequence_audio(self):
        """ whatever the state of the sequence is, run the function to update the """

        if self.wf:  # it had been created, such that we had enough parameters
            a = self.get_t()
            self.state.a = a
            self.wf.setpos(self.get_framenumber_from_time(self.state.calc_t()))

    def set_sequence_params(self, **kwargs):
        """ update the p3d sequence to have a specific duration, update_function_extra_args, and update function.
        This does not call the graphics update function afterwards automatically.
        The sequence will be (at first) only created and not restarted.

        Since a sequence's duration is determined on start time
        kwars:
        - duration: duration of the p3d sequence in seconds
        - update_function_extra_args: extra arguments that the sequence update function receives
        - update_function: function with signature: (a : parameter in interval between 0 (beginning) and 1 (end), )
        - on_finish_function
        - defer_loading: if True, don't call self.start_load_thread() after init, but wait and call it manually afterwards. """

        create_thread_wf_stream = True

        if 'duration' in kwargs:
            self.state.duration = kwargs.get('duration')
        elif self.state.duration is None:
            self.state.duration = playback.audiofunctions.get_wave_file_duration(
                self.wave_file_path)
            # create_thread_wf_stream = True

        if 'update_function_extra_args' in kwargs:
            self.update_function_extra_args = kwargs.get('update_function_extra_args')
        # elif self.update_function_extra_args is None:
        #     # print("Warning: LerpFunc will not be created yet, self.update_function_extra_args is None")
        #     # create_thread_wf_stream = False

        # if 'update_function_kwargs' in kwargs:
        #     self.update_function_extra_args = kwargs.get('update_function_kwargs')
        # elif self.update_function_extra_args is None:
        #     self.update_function_kwargs = dict({})

        if 'update_function' in kwargs:
            self.update_function = kwargs.get('update_function')
        elif self.update_function is None:
            self.update_function = self.default_play_loop_function

        if 'on_finish_function' in kwargs:
            self.on_finish_function = kwargs.get('on_finish_function')
        elif self.on_finish_function is None:
            self.on_finish_function = lambda: None
            # FIXME: call this sequence with this transition function: self.transition_into(self.state_stopped_at_end)

        if 'defer_loading' in kwargs:
            self.defer_loading = kwargs.get('defer_loading')
        elif self.defer_loading is None:
            self.defer_loading = False

        if self.wf:
            self.wf.stop_stream()
            del self.wf  # remove the reference

        if create_thread_wf_stream == True:
            if self.defer_loading == False:
                self.start_load_thread()

        return self  # in order to

    def _load(self):
        """ """
        self.wf = wave.open(self.wave_file_path, 'rb')
        # TODO: check rb vs r changes the meaning of self.wf.setpos(...)

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
                                  channels=self.wf.getnchannels(),
                                  rate=self.wf.getframerate(),
                                  output=True)

    def default_play_loop_function(self, *args):
        """ named in analogy to p3d sequences update functions """
        # try:
        #     if change_time_to is not None:
        #         self.wf.setpos(self.get_framenumber_from_time(change_time_to))
        # except wave.Error:
        #     print("Bad position for start_frame")
        #     os._exit()

        while True:
            if self.playing_p == True:

                self.playing_p == True

                data = self.wf.readframes(playback.audiofunctions.CHUNK)
                # self.play_session_num_frames += int(len(data)/PlaybackerSM.CHUNK)

                framenumber = self.wf.tell()
                self.set_t(self.get_time_from_framenumber(framenumber))
                
                print("TIME from FRAMENUBNMER: ",
                      self.get_time_from_framenumber(framenumber))

                if len(data) > 0:
                    # write to sound device
                    self.stream.write(data)
                else:
                    # no data left
                    self.finish()

            if self.break_play_loop_p == True:
                self.finish()
                break

            # else:

            #     # self.transition_into(self.state_stopped_at_end)
            #     # this transition happens from inside the thread! But then the thread finishes

    def remove(self):
        """ unregister the sequence """
        if self.wf:
            self.wf.close()
            self.wf = None

        self.wf = None # remove the reference
        self.p3d_interval = None

    def get_t(self):
        """ """
        t_from_state = self.state.get_t()
        print("from inside get_t: ", t_from_state)
        t = t_from_state

        if self.wf:
            assert self.wf
            t_wf = float(self.wf.tell()) / float(self.wf.getframerate())
            t = t_wf
            print("COMPARISON: t_from_state: ", t_from_state, ", t_wf: ", t_wf)

        print("time returned:", t)

        return t

    def set_t(self, t):
        """ """
        if t > 50.:
            import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
            
        self.state.set_t(t)

        if self.wf:
            self.wf.setpos(self.get_framenumber_from_time(t))
        else:
            print("WARNING: self.wf: ", self.wf)

    def pause(self):
        """ """
        # stream stopped would not be a pause state
        # the pause state is an idle while loop not writing to the soundcard
        assert self.wf and self.p and self.play_thread.is_alive() == True  # and self.stream.is_active() == True
        self.playing_p = False
        self.break_play_loop_p = False
        print("pause: setting playing_p to ", self.playing_p)

    def resume(self):
        assert self.wf and self.p and self.play_thread.is_alive() == True  # and self.stream.is_active() == True
        self.playing_p = True
        self.break_play_loop_p = False

    def start_load_thread(self):
        """ loading at the end of init """
        self.load_thread = threading.Thread(target=self._load, daemon=True)
        self.load_thread.start()
        print("- > starting load thread")

    def load_thread_finished_p(self):
        """ """
        # TODO: put this into the playbackersm as a on bool event
        res = None
        if self.load_thread is not None:
            res = self.load_thread.is_alive()

        return res
        # upon load_thread is not alive any more

    def start(self, block_to_join_threads=False, start_paused=False):
        """ the sequence needs to be loaded first before it's played using 'start'.
        it can be made sure that it's loaded by waiting for wavseq.load_thread.is_alive() == False in
        an outside state machine and then transitioning """
        if self.load_thread.is_alive() == True:
            # wait for load thread to join
            if block_to_join_threads == True:
                import time
                start = time.time()
                print("WARNING: blocking to join the audio load thread with the main thread")
                self.load_thread.join()
                end = time.time()
                print("WARNING: blocked for {:.3f}".format(end-start), "seconds to join the audio load thread with the main thread")
            else:
                print("ERR: audio sequence load thread not yet finished")
                assert False

        if start_paused == True:
            self.playing_p = False
        else:
            self.playing_p = True

        self.break_play_loop_p = False

        if self.play_thread is None or self.play_thread.is_alive() == False:
            self.play_thread = threading.Thread(target=self.default_play_loop_function,
                                                args=(self.update_function_extra_args,),
                                                daemon=True)
            
            self.set_t(0.)

            if self.stream is not None and self.stream.is_active() == False:
                self.stream.start_stream()

            self.play_thread.start()

            print("- > starting play thread")

        return False

    def finish(self):
        """ this function sets variables which are queried in the play loop,
        run _finish_up_resouces_from_inside_play_loop and end the thread """

        self.set_t(self.state.duration)

        print("set_t in finish: ", self.state.duration)
        print("get_t immediately afterwards: ", self.get_t())
        
        self.playing_p = False
        self.break_play_loop_p = True
        
        self._finish_up_resouces_from_inside_play_loop()
        self.on_finish_function()

    def _finish_up_resouces_from_inside_play_loop(self):
        """ """
        if self.stream is not None and self.stream.is_active() == True:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if self.wf is not None:
            self.wf.close()
            self.wf = None

        if self.p is not None:
            self.p.terminate()
            self.p = None

    def get_framenumber_from_time(self, time):
        """ """
        start_frame = int(time * self.wf.getframerate())
        assert time <= self.state.duration
        return start_frame

    def get_time_from_framenumber(self, framenumber):
        """ """
        time = float(framenumber) / float(self.wf.getframerate())
        # start_frame = int(time * self.wf.getframerate())
        assert time <= self.state.duration
        return time
