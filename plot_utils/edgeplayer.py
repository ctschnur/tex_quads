from direct.showbase.ShowBase import ShowBase, DirectObject

from simple_objects.primitives import ParametricLinePrimitive
from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk

from composed_objects.composed_objects import Point3dCursor

from panda3d.core import Vec3, Mat4, Vec4

import numpy as np

from plot_utils.edgehoverer import EdgeHoverer, EdgeMouseClicker

from local_utils import math_utils

from sequence.sequence import Sequence

from playback.playback import Playbacker

import os

import inspect

from plot_utils.edgegraphics import EdgeGraphics

import playback.audiofunctions


class EdgePlayerState:
    """ You have an edge, and the states are
        1. stopped at beginning
        2. playing
        3. paused
        4. stopped at end
    This class is just for checking and changing the state.
    TODO: A class derived from EdgePlayerState will call it's functions and
    add the specific sequence commands after executing the state change functions. """

    def __init__(self):
        # TODO: set predefined initial state
        self.set_stopped_at_beginning()

    def set_stopped_at_beginning(self):
        self.s_a = 0.
        self.stopped = True
        self.paused = False  # undefined

    def is_stopped_at_beginning(self):
        return (self.s_a == 0. and self.stopped == True
                # self.paused = False  # undefined
                )

    def set_stopped_at_end(self):
        self.s_a = 1.
        self.stopped = True
        self.paused = False  # undefined

    def is_stopped_at_end(self):
        return (math_utils.equal_up_to_epsilon(self.s_a, 1.) and self.stopped == True
                )

    def is_playing_stopped(self):
        return self.is_stopped_at_end() or self.is_stopped_at_beginning()

    def set_playing(self, a_to_start_from=None):
        if a_to_start_from is None:
            a_to_start_from = self.s_a

        assert (a_to_start_from >= 0. and a_to_start_from <= 1.)
        self.s_a = a_to_start_from

        self.stopped = False
        self.paused = False

    def is_playing(self):
        return (self.s_a >= 0. and self.s_a <= 1. and self.stopped == False and self.paused == False)

    def set_paused(self, a_to_set_paused_at=None):
        if a_to_set_paused_at is None:
            a_to_set_paused_at = self.s_a

        assert (a_to_set_paused_at >= 0. and a_to_set_paused_at <= 1.)
        self.s_a = a_to_set_paused_at

        self.stopped = False  # in a stopped state, you can't pause
        self.paused = True

    def is_paused(self):
        return (self.s_a >= 0. and
                self.s_a <= 1. and
                self.stopped == False and
                self.paused == True)

    def print_self(self):
        print("s_a: ", str(self.s_a), ", ",
              "stopped: ", str(self.stopped), ", ",
              "paused: ", str(self.paused))


class EdgePlayer(EdgeGraphics):
    """ Adds the graphics and the p3d sequence operations to the logic of EdgePlayerState """

    stopped_at_beginning_primary_color = ((1., 0., 0., 1.), 1)
    stopped_at_beginning_cursor_color = ((1., 0., 0., 1.), 1)
    # this is only set, if the line (edge) is 'engaged' (at a node, multiple edges diverge)
    stopped_at_beginning_line_color = ((1., 0., 0., 1.), 1)

    stopped_at_end_primary_color = ((1., .5, 0., 1.), 1)
    stopped_at_end_cursor_color = ((1., .5, 0., 1.), 1)
    # this is only set, if the line (edge) is 'engaged' (at a node, multiple edges diverge)
    stopped_at_end_line_color = ((1., .5, 0., 1.), 1)

    playing_primary_color = ((.5, .5, 0., 1.), 1)
    playing_cursor_color = ((.5, .5, 0., 1.), 1)
    # this is only set, if the line (edge) is 'engaged' (at a node, multiple edges diverge)
    playing_line_color = ((.5, .5, 0., 1.), 1)

    paused_primary_color = ((0., .5, .5, 1.), 1)
    paused_cursor_color = ((0., .5, .5, 1.), 1)
    # this is only set, if the line (edge) is 'engaged' (at a node, multiple edges diverge)
    paused_line_color = ((0., .5, .5, 1.), 1)

    lps_rate = 0.25/1.  # length per second

    def __init__(self, camera_gear, wave_file_path=None):

        self.wave_file_path = wave_file_path

        # -- do geometry logic
        self.v1 = Vec3(-.5, -.5, 0.)
        self._v_dir = None
        self.set_v_dir(Vec3(1., 1., 0.)/np.linalg.norm(Vec3(1., 1., 0.)))

        self._duration = None  # a relatively high number
        self.set_duration(1., update_cursor_sequence=False)

        self.short_skipping_time_step = 2.  # interactive forward/backward skipping, in seconds

        # -- do graphics stuff
        self.p_c = Point3dCursor(self.get_v1())

        self.line = None
        self.update_line()

        self.primary_color = None
        self.set_primary_color(
            self.stopped_at_beginning_primary_color)  # initially

        # setup the spacebar
        self.space_direct_object = DirectObject.DirectObject()
        self.space_direct_object.accept('space', self.react_to_spacebar)

        # setup keys for jumping to beginning/end
        self.set_stopped_at_beginning_direct_object = DirectObject.DirectObject()
        self.set_stopped_at_beginning_direct_object.accept(
            'a', self.react_to_a)

        self.set_stopped_at_end_direct_object = DirectObject.DirectObject()
        self.set_stopped_at_end_direct_object.accept('e', self.react_to_e)

        self.set_short_forward_direct_object = DirectObject.DirectObject()
        self.set_short_forward_direct_object.accept(
            'arrow_right', self.react_to_arrow_right)

        self.set_short_backward_direct_object = DirectObject.DirectObject()
        self.set_short_backward_direct_object.accept(
            'arrow_left', self.react_to_arrow_left)

        self.extraArgs = [
            # self.lps_rate,
            # self._duration,
            # # self.v1, self._v_dir,
            # self.p_c
        ]

        # -- do sequence stuff
        # ---- initialize the sequence

        self.cursor_sequence = Sequence()
        self.cursor_sequence.set_sequence_params(
            duration=self.get_duration(),
            extraArgs=self.extraArgs,
            update_while_moving_function=self.update_while_moving_function,
            on_finish_function=self.on_finish_cursor_sequence)

        # -- init hover and click actions
        self.camera_gear = camera_gear

        self.edge_hoverer = EdgeHoverer(self, self.camera_gear)

        self.edge_mouse_clicker = EdgeMouseClicker(self)

        self.state = EdgePlayerState()

        self.playbacker = Playbacker()

        # -- audio playing capability
        # this means that the graphics is still being rendered, but no audio actions are performed
        # to debug your routines and uncouple the audio from the graphics, use switches in the
        # state change functions addressing this variable
        # initiall, self.has_audio_playing_capability = False
        # but if a wave file has been successfully loaded, set self.has_audio_playing_capability = True
        self.has_audio_playing_capability = False

        if wave_file_path is not None:
            self.set_and_load_wave_file(self.wave_file_path)

    def set_and_load_wave_file(self, wave_file_path):
        """ sets also the duration, i.e. the length of the edge,
            resets the cursor to the beginning """
        self.has_audio_playing_capability = False

        self.wave_file_path = wave_file_path

        if not os.path.isfile(self.wave_file_path):
            print("ERR: EdgePlayer: not os.path.isfile(self.wave_file_path), ",
                  self.wave_file_path)
            os._exit(1)
        else:
            self.has_audio_playing_capability = True

            # proceed to set the length of your edge
            # get the duration of the wave file

            durat = playback.audiofunctions.get_wave_file_duration(
                self.wave_file_path)
            # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

            # durat = 2.
            print("wave file exists: ", self.wave_file_path, "duration: ", durat)

            self.set_duration(durat, update_cursor_sequence=True)

    def update_line(self):
        """ set the line to the appropriate dimensions """
        if self.line is None:
            self.line = Line1dSolid()

        self.line.setTipPoint(self.get_v1())
        self.line.setTailPoint(self.get_v2())

    def update_while_moving_function(self,
                                     s_a):
        """ calculating everything that changes while
        playing """
        self.state.s_a = s_a  # update s_a

        # covered_time = s_a * (s_l/lps_rate)

        s_l = self.lps_rate * self.get_duration()

        covered_length = s_l * s_a

        # set cursor point:
        cursor_pos = math_utils.np_to_p3d_Vec3(
            covered_length * math_utils.p3d_to_np(self._v_dir) +
            math_utils.p3d_to_np(self.v1))

        self.p_c.setPos(cursor_pos)

        self.update_line()

    def set_duration(self, duration, update_cursor_sequence=True):
        """ the logical duration and the sequence's duration are being updated """
        self._duration = duration

        if update_cursor_sequence == True:
            self.cursor_sequence.set_sequence_params(duration=duration)
            # if it has an EdgePlayerState, otherwise in the update_while_moving_function
            # will fail
            if self.state:
                self.cursor_sequence.update_sequence_graphics()

    def get_duration(self):
        return self._duration

    def react_to_a(self):
        """ unconditionally jump to the beginning and stop """
        self.set_stopped_at_beginning()

    def react_to_e(self):
        """ unconditionally jump to the beginning and stop """
        self.set_stopped_at_end()

    def react_to_spacebar(self):
        """ spacebar will either:
        - start playing from beginning if it's stopped at the beginning
        - start playing from beginning of the next edge if it's stopped at the end (print 'start at next edge')
        - pause if it's playing
        - play if it's paused
        """

        print("before spacebar")
        print("is_stopped_at_beginning(): ", self.state.is_stopped_at_beginning(), ", ",
              "is_stopped_at_end(): ", self.state.is_stopped_at_end(), ", ",
              "is_playing(): ", self.state.is_playing(), ", ",
              "is_paused(): ", self.state.is_paused())
        print(self)

        if self.state.is_stopped_at_beginning():
            self.set_playing(a_to_start_from=0.)
        elif self.state.is_stopped_at_end():
            self.set_playing(a_to_start_from=0., after_finish=True)
            print(
                "start at next edge (if no next edge, start from beginning of last edge)")
        elif self.state.is_playing():
            self.set_paused()
        elif self.state.is_paused():
            self.set_playing()
        else:
            print("situation matches no state!")

        print("after spacebar")
        print("is_stopped_at_beginning(): ", self.state.is_stopped_at_beginning(), ", ",
              "is_stopped_at_end(): ", self.state.is_stopped_at_end(), ", ",
              "is_playing(): ", self.state.is_playing(), ", ",
              "is_paused(): ", self.state.is_paused())
        print(self)

    def react_to_arrow_right(self):
        """ arrow_right will either:
        - if calculated time is smaller than duration: advance to a time and change nothing
        - if calculated time is greater than duration: finish() the sequence and set stopped state
        """

        print("before arrow right")
        print(self)

        self.state.s_a = self.cursor_sequence.get_t()/self.get_duration()

        print("self.state.s_a: ", self.state.s_a,
              "; self.cursor_sequence.get_t(): ", self.cursor_sequence.get_t())

        calculated_time = (self.state.s_a * self.get_duration() +
                           self.short_skipping_time_step)

        new_a = calculated_time/self.get_duration()
        print("new_a: ", new_a)

        print("; calculated_time: ", calculated_time,
              "; self.state.s_a: ", self.state.s_a,
              "; self.get_duration(): ", self.get_duration(),
              "; self.short_skipping_time_step", self.short_skipping_time_step)

        if self.state.is_stopped_at_beginning():
            self.set_paused(a_to_set_paused_at=new_a)
        elif self.state.is_stopped_at_end():
            print("do nothing, only consider next edge, if there is one")
        elif self.state.is_playing():
            print("self.state.is_playing(): ", self.state.is_playing())
            if calculated_time < self.get_duration():
                print("calculated_time < self.get_duration(): ",
                      calculated_time < self.get_duration())
                self.set_playing(a_to_start_from=new_a)
            else:
                self.set_stopped_at_end()
        elif self.state.is_paused():
            print("self.state.is_paused(): ", self.state.is_paused())
            if calculated_time < self.get_duration():
                print("calculated_time < self.get_duration()",
                      calculated_time < self.get_duration())
                self.set_paused(a_to_set_paused_at=new_a)
            else:
                self.set_stopped_at_end()
        else:
            print("situation matches no state!")

        print("after arrow right")
        print(self)

    def react_to_arrow_left(self):
        """ arrow_right will either:
        - if calculated time is smaller than duration: advance to a time and change nothing
        - if calculated time is greater than duration: finish() the sequence and set stopped state
        """

        print("before arrow left")
        print(self)

        self.state.s_a = self.cursor_sequence.get_t()/self.get_duration()

        print("self.state.s_a: ", self.state.s_a,
              "; self.cursor_sequence.get_t(): ", self.cursor_sequence.get_t())

        calculated_time = (self.state.s_a * self.get_duration() -
                           self.short_skipping_time_step)

        if calculated_time < 0.001:  # clamp it so that you can't skip the node
            calculated_time = 0.001
            # setting it to exactly 0.0 seems to not work properly (? with the p3d sequence)
        # elif calculated_time < self.short_skipping_time_step

        new_a = calculated_time/self.get_duration()
        print("new_a: ", new_a)

        if self.state.is_stopped_at_beginning():
            print("stopped at beginning: stepping back only if something precedes")
        elif self.state.is_stopped_at_end():
            self.set_paused(a_to_set_paused_at=new_a)
        elif self.state.is_playing():
            print("self.state.is_playing(): ", self.state.is_playing())
            self.set_playing(a_to_start_from=new_a)
        elif self.state.is_paused():
            print("self.state.is_paused(): ", self.state.is_paused())
            self.set_paused(a_to_set_paused_at=new_a)
        else:
            # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
            print("situation matches no state!")

        print("after arrow left")
        print(self)

    def on_finish_cursor_sequence(self):
        self.set_stopped_at_end()

    def do_when_stopped(self):
        """ This function is called at the end of all set_stopped_... functions
        and has several tasks, e.g.:
        - terminate the audio playing thread. """

        print("adding the task rendering_while_waiting_for_audio_playback_thread_task")

        taskMgr.add(self.rendering_while_waiting_for_audio_playback_thread_task,
                    'rendering_while_waiting_for_audio_playback_thread_task',
                    extraArgs=[s_a_finished],
                    appendTask=True)

    def rendering_while_waiting_for_audio_playback_thread_task(self, s_a_finished, task):
        """ This checks if the audio thread has finished.
        TODO: If it has not properly finished, we need render a warning message. """
        # make a p3d task to check for the audio playbacker
        # only after the thread has finihsed, the graphics should be set to indicate
        # the stopped state

        print("rendering_while_waiting_for_audio_playback_thread_task")
        print("self.playbacker.is_playbacker_thread_done(): ",
              self.playbacker.is_playbacker_thread_done())

        if self.playbacker.is_playbacker_thread_done() is None:
            print("ERR: self.playbacker.is_playbacker_thread_done() is None",
                  "this task (rendering_while_waiting_for_audio_playback_thread_task)",
                  "should not even be registered in that situation!")
            exit(1)
            # return task.cont

        if self.playbacker.is_playbacker_thread_done() == True:
            print("wanting to join threads: playback audio thread is done",
                  "of your audio at",
                  self.playbacker.wave_file_path)

            return task.done
        elif self.playbacker.is_playbacker_thread_done() == False:
            print("wanting to join threads: playbacker thread not yet done")
            return task.cont
        else:
            exit(1)

    def set_stopped_at_beginning(self):
        self.state.set_stopped_at_beginning()
        # -- do p3d sequence stuff
        # p3d only really has a finish() function, not a 'stopped at start'

        self.cursor_sequence.pause()
        assert self.state.s_a == 0.

        self.cursor_sequence.set_t(self.state.s_a * self.get_duration())

        print("duration: ", self.get_duration())

        # -- do graphics stuff

        self.set_primary_color(self.stopped_at_beginning_primary_color)

    def set_stopped_at_end(self,  # already_at_end=False
                           ):
        self.state.set_stopped_at_end()

        # if already_at_end is False:
        print("stopped at end ", self)
        self.cursor_sequence.finish()
        self.set_primary_color(self.stopped_at_end_primary_color)

    def set_playing(self, a_to_start_from=None, after_finish=False):
        self.state.set_playing(a_to_start_from=a_to_start_from)

        if a_to_start_from:
            self.cursor_sequence.set_t(a_to_start_from * self.get_duration())
            print("a_to_start_from: ", a_to_start_from)

            if self.has_audio_playing_capability == True:
                # start the audio thread
                self.playbacker.do_playback(
                    self.state.is_playing,  # is_playing_query_function,
                    self.state.is_paused,  # is_paused_query_function,
                    self.state.is_playing_stopped,  # is_playing_stopped_query_function,
                    # this possibly needs to be modified,
                    # if scrolling is also a state of is_playing_stopped_query_function
                    (lambda: self.state.s_a * self.get_duration()),
                    # play_at_time_query_function,
                    self.wave_file_path)

        if after_finish is True:
            # it needs to be restarted at a=0. Usually this is called after the interval has finished once, to restart the Sequence
            print("attempting to restart the sequence after finish", self)
            self.cursor_sequence.start()
            print("after restart: ", self)
        else:
            # merely resume, since it is already started (standard state)
            self.cursor_sequence.resume()

        print("s_a: ", self.state.s_a, ", "
              "duration: ", self.get_duration())

        self.set_primary_color(self.playing_primary_color)

    def set_paused(self, a_to_set_paused_at=None):
        self.state.set_paused(a_to_set_paused_at=a_to_set_paused_at)

        if a_to_set_paused_at:
            self.cursor_sequence.set_t(
                a_to_set_paused_at * self.get_duration())
            print("a_to_set_paused_at: ", a_to_set_paused_at)

        self.cursor_sequence.pause()

        self.set_primary_color(self.paused_primary_color)

    def remove(self):
        """ removes all
        - p3d sequences
        - p3d nodes (detaches them from render)
        - p3d events (directobjects)
        their references. """

        self.cursor_sequence.pause()  # remove it from the interval manager
        del self.cursor_sequence  # remove the reference

        self.line.nodePath.removeNode()
        self.p_c.remove()

        self.space_direct_object.ignoreAll()
        self.space_direct_object.removeAllTasks()

        # setup keys for jumping to beginning/end
        self.set_stopped_at_beginning_direct_object.ignoreAll()
        self.set_stopped_at_beginning_direct_object.removeAllTasks()

        self.set_stopped_at_end_direct_object.ignoreAll()
        self.set_stopped_at_end_direct_object.removeAllTasks()

        self.set_short_forward_direct_object.ignoreAll()
        self.set_short_forward_direct_object.removeAllTasks()

        self.set_short_backward_direct_object.ignoreAll()
        self.set_short_backward_direct_object.removeAllTasks()

    def get_v2(self):
        return self.v1 + self._v_dir * EdgePlayer.lps_rate * self.get_duration()
