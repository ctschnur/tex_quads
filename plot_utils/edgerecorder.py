from interactive_tools.dragging_and_dropping import PickableObjectManager, PickablePoint, Dragger, PickablePoint, CollisionPicker, DragAndDropObjectsManager

from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle

from composed_objects.composed_objects import Point3dCursor

from local_utils import math_utils

from simple_objects.simple_objects import Line1dSolid, PointPrimitive, Fixed2dLabel
from composed_objects.composed_objects import Vector

from simple_objects.custom_geometry import create_Triangle_Mesh_From_Vertices_and_Indices, createCircle, createColoredUnitQuadGeomNode

from simple_objects.primitives import ParametricLinePrimitive
from panda3d.core import Vec3, Mat4, Vec4

import numpy as np
import scipy.special

import glm

from direct.showbase.ShowBase import ShowBase, DirectObject

from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight

import networkx as nx

from simple_objects.simple_objects import Pinned2dLabel

from interactive_tools import cameraray

from functools import partial

from plot_utils.edgehoverer import EdgeHoverer, EdgeMouseClicker

from plot_utils.edgeplayer import EdgePlayer

from plot_utils.edgeplayerrecorderspawner import EdgePlayerRecorderSpawner

from sequence.sequence import Sequence

from recording.recorder import Recorder

# TODO: write a SequenceRepeater class to automatically continue a finite sequence (provided by p3d) when it has ended


class EdgeRecorderState:
    """ When you record an edge, the states are
        1. recording (extending the edge at it's furthest point)
        2. paused (not recording right now, but not recording finished)
        (~3. stopped at end (actually not a state, at that point it has been transformed to a edgeplayer)~)

    This class is just for checking and changing the state.
    TODO: A class derived from EdgeRecorderState will call it's functions and
    add the specific sequence commands after executing the state change functions. """

    def __init__(self):
        # TODO: set predefined initial state
        self.set_stopped_at_beginning()

        self.recording_finished = False

    def set_recording(self):
        """ continue recording from a paused state """
        self.recording = True
        self.paused = False
        self.stopped_at_beginning = False
        self.recording_finished = False

    def is_recording(self):
        return (self.recording == True and self.paused == False and self.stopped_at_beginning == False and self.recording_finished == False)

    def set_paused(self):
        self.recording = False
        self.paused = True
        self.stopped_at_beginning = False
        self.recording_finished = False

    def is_paused(self):
        return (self.recording == False and self.paused == True and self.stopped_at_beginning == False and self.recording_finished == False)

    def set_stopped_at_beginning(self):
        """ """
        self.s_a = 0.
        self.recording = False
        self.paused = False
        self.stopped_at_beginning = True
        self.recording_finished = False

    def is_stopped_at_beginning(self):
        """ """
        return (self.recording == False and self.paused == False and self.stopped_at_beginning == True and self.recording_finished == False)

    def set_recording_finished(self):
        """ this the (for now inescapable) end state of the lifecycle of a recording.
            If it's finished, you can just kill it
            The recorder technically doesn't even have to enter this state before the recorder is killed """

        # things don't need to be defined any more
        self.s_a = None
        self.recording = None
        self.paused = None
        self.stopped_at_beginning = None
        self.recording_finished = True

    def is_recording_finished(self):
        """ """
        return (self.recording is None and self.paused is None and self.stopped_at_beginning is None and self.recording_finished == True)

    def print_states(self):
        """ debugging """
        print("--- States: ---")
        print("is_stopped_at_beginning(): ", self.is_stopped_at_beginning(), ", ",
              "is_recording(): ", self.is_recording(), ", ",
              "is_paused(): ", self.is_paused(), ", ",
              "is_recording_finished(): ", self.is_recording_finished())
        print("s_a: ", self.s_a, ", ",
              "stopped_at_beginning: ", self.stopped_at_beginning, ", ",
              "recording: ", self.recording, ", ",
              "paused: ", self.paused, ", ",
              "recording_finished: ", self.recording_finished)


class EdgeRecorder:
    """ Adds the graphics and the p3d sequence operations to the logic of EdgeRecorderState
    """

    stopped_at_beginning_primary_color = ((.75, .25, 0., 1.), 1)
    stopped_at_beginning_cursor_color = ((.75, .25, 0., 1.), 1)
    stopped_at_beginning_line_color = ((.75, .25, 0., 1.), 1)

    recording_primary_color = ((.5, .5, 0., 1.), 1)
    recording_cursor_color = ((.5, .5, 0., 1.), 1)
    recording_line_color = ((.5, .5, 0., 1.), 1)

    paused_primary_color = ((0., .5, .5, 1.), 1)
    paused_cursor_color = ((0., .5, .5, 1.), 1)
    paused_line_color = ((0., .5, .5, 1.), 1)

    s_l = 50.  # length of a template sequence
    # (of a finite sequence, todo: chain a series of finite sequences while recording)

    s_dur = s_l / EdgePlayer.lps_rate  # the duration of a template sequence

    time_ind = 0.5

    def __init__(self, camera_gear, edge_player_recorder_spawner=None):

        self.camera_gear = camera_gear
        self.edge_player_recorder_spawner = edge_player_recorder_spawner

        self.state = EdgeRecorderState()

        # -- do geometry logic
        # make the line small, but pick initial direction

        # -- do graphics stuff
        tail_init_point = Vec3(0., 0., 0.)
        self.p_c = Point3dCursor(tail_init_point)

        self.line = Line1dSolid()
        tip_init_point = tail_init_point + Vec3(2., 2., 2.)

        self.line.setTipPoint(tip_init_point)
        self.line.setTailPoint(tail_init_point)

        # actions: record, pause, kill

        # setup the spacebar to continue/start recording or pausing
        self.space_direct_object = DirectObject.DirectObject()
        self.space_direct_object.accept('space', self.react_to_spacebar)

        self.set_recording_direct_object = DirectObject.DirectObject()
        self.set_recording_direct_object.accept(
            'r', self.react_to_r)

        # -- do p3d sequence stuff
        # ---- initialize the sequence

        self.v1 = Vec3(0.5, 0.5, 0.)
        self.v_dir = Vec3(1., 1., 0.)/np.linalg.norm(Vec3(1., 1., 0.))

        self.extraArgs = [
            math_utils.p3d_to_np(self.v1), math_utils.p3d_to_np(self.v_dir),
            self.p_c, self.line
        ]

        self.init_recorder_label()

        self.cursor_sequence = Sequence()
        self.cursor_sequence.set_sequence_params(
            duration=EdgeRecorder.s_dur,
            extraArgs=self.extraArgs,
            update_while_moving_function=self.update_while_moving_function,
            on_finish_function=self.on_finish_cursor_sequence)

        # --- additional ui stuff ---
        # -- init hover and click actions

        # self.edge_hoverer = EdgeHoverer(self, self.camera_gear)
        # self.edge_mouse_clicker = EdgeMouseClicker(self)

        # make a pinned label saying Rec. in thick red letters

        # --- set initial state ----

        self.set_stopped_at_beginning()

        self.recorder = Recorder()

    def init_recorder_label(self):
        """ Pin this `Rec.` label to the position of the recorder cursor """

        self.recorder_label = Pinned2dLabel(
            refpoint3d=Point3(0., 0., 0.), text="Rec.",
            xshift=0.02, yshift=0.02, font="fonts/arial.egg")

        self.camera_gear.add_camera_move_hook(self.recorder_label.update)

        self.recorder_label.setColor(Vec4(1., 0., 0., 1.))  # red

        # self.recorder_label.textNode.setTransform(
        #     math_utils.math_convention_to_p3d_mat4(math_utils.getScalingMatrix4x4(0.5, 0.5, 0.5)))

    def update_while_moving_function(self,
                                     s_a,
                                     v1, v_dir,
                                     p_c, line):
        # logical, given:
        # for the current sequence:
        # s_a: parameter between 0 and 1 for the time between the sequence's current start and end points
        # s_l: fixed length of what length a sequence should have (choose a reasonable length, corresponding to a time of maybe 10 seconds, after that, start a new (always finite) sequence)
        # s_dur: fixed duration of the sequence
        # EdgeRecorder.time_ind=1 (s), (time corresponding to the length of the hint line at start of recording),
        # v1 (branch point),
        # v_dir (direction of branching),
        # lps_rate (length per second rate of the player/recorder)

        # graphical: p1, p2, p_c, line

        # asked (logical):
        # the length of the line at the covered_time (line always just keeps increasing in size, not separate segments). Time in seconds is extracted from s_a (given)

        self.state.s_a = s_a  # update s_a

        covered_time = s_a * (EdgeRecorder.s_l/EdgePlayer.lps_rate)
        covered_length = EdgeRecorder.s_l * s_a

        len_ind = EdgeRecorder.time_ind * EdgePlayer.lps_rate
        s_a_ind = EdgeRecorder.time_ind * EdgePlayer.lps_rate / EdgeRecorder.s_l

        if s_a <= s_a_ind:
            line.setTipPoint(math_utils.np_to_p3d_Vec3(len_ind * v_dir + v1))
        elif s_a > s_a_ind:
            line.setTipPoint(math_utils.np_to_p3d_Vec3(
                covered_length * v_dir + v1))
        else:
            print("invalid value of s_a: ", s_a)
            exit(1)

        line.setTailPoint(math_utils.np_to_p3d_Vec3(v1))

        # set cursor point:
        cursor_pos = math_utils.np_to_p3d_Vec3(covered_length * v_dir + v1)
        p_c.setPos(cursor_pos)

        # update the label position (which should be pinned to the (self.p_c), which gets set one line above)

        self.recorder_label.setPos(*tuple(cursor_pos))
        # self.recorder_label.update()

    def react_to_r(self):
        """ starts or finishes a recording (does't pause or resume, that's what spacebar does) """
        print("before r")
        self.state.print_states()

        if self.state.is_recording() or self.state.is_paused():
            self.set_recording_finished()
        elif self.state.is_stopped_at_beginning():
            self.set_recording()
        else:
            print("Error: not (recording or paused), nor stopped at beginning")
            exit(1)

        print("after r")
        self.state.print_states()

    def react_to_spacebar(self):
        """ spacebar will:
        - pause if it's recording
        - resume recording if it's paused
        """

        print("before spacebar")
        self.state.print_states()

        if self.state.is_recording():
            self.set_paused()
        elif self.state.is_paused():
            self.set_recording()
        else:
            print("spacebar doesn't do anything here!")

        print("after spacebar")
        self.state.print_states()

    def on_finish_cursor_sequence(self):
        self.set_recording_finished()

    def set_stopped_at_beginning(self):
        self.state.set_stopped_at_beginning()
        # -- do p3d sequence stuff
        # p3d only really has a finish() function, not a 'stopped at start'

        self.cursor_sequence.start()
        self.cursor_sequence.set_t(0)
        self.cursor_sequence.pause()

        # -- do graphics stuff

        self.set_primary_color(self.stopped_at_beginning_primary_color)

    def set_recording_finished(self,  # already_at_end=False
                               ):

        s_a_finished = self.state.s_a
        self.state.set_recording_finished()

        print("set_recording_finished")

        # add a task into the render loop for joining the rendering and audio threads,
        # as soon as the audio thread is done

        print("adding the task rendering_while_waiting_for_audio_thread_task")

        taskMgr.add(self.rendering_while_waiting_for_audio_thread_task,
                    'rendering_while_waiting_for_audio_thread_task',
                    extraArgs=[s_a_finished],
                    appendTask=True)


    def rendering_while_waiting_for_audio_thread_task(self, s_a_finished, task):
        # make a p3d task to check for the audio recorder
        # only after the file has been registered, an EdgePlayer should be created

        print("rendering_while_waiting_for_audio_thread_task")
        print("self.recorder.is_recorder_thread_done(): ",
              self.recorder.is_recorder_thread_done())

        if self.recorder.is_recorder_thread_done() is None:
            print("ERR: self.recorder.is_recorder_thread_done() is None",
                  "this task (rendering_while_waiting_for_audio_thread_task)",
                  "should not even be registered in that situation!")
            exit(1)
            # return task.cont

        if self.recorder.is_recorder_thread_done() == True:
            print("wanting to join threads: audio thread is done",
                  "your audio file should be at",
                  self.recorder.output_filename)

            # -- spawn the EdgePlayer
            ep = EdgePlayer(self.camera_gear)
            EdgePlayerRecorderSpawner.set_EdgePlayers_state_from_EdgeRecorder(
                ep, self, s_a_finished)

            self.state.print_states()

            # assign the EdgePlayer instance to the EdgePlayerRecorderSpawner
            if self.edge_player_recorder_spawner is not None:
                self.edge_player_recorder_spawner.set_edge_player(ep)
            else:
                print("self.edge_player_recorder_spawner is None, ",
                      "not transforming to an EdgePlayer")

            return task.done
        elif self.recorder.is_recorder_thread_done() == False:
            print("wanting to join threads: recorder thread not yet done")
            return task.cont
        else:
            exit(1)

    def set_recording(self,  # a_to_start_from=None,
                      after_finish=False):

        tmp_is_stopped_at_beginning = self.state.is_stopped_at_beginning()
        tmp_is_paused = self.state.is_paused()

        self.state.set_recording()

        if tmp_is_stopped_at_beginning:
            # start a recording
            self.cursor_sequence.start()

            # start the recording thread
            self.recorder.do_record(
                self.state.is_recording,
                self.state.is_paused,
                self.state.is_recording_finished)
            # in set_recording_finished, register a task to check if
            # the self.recorder thread is done or still alive

        elif tmp_is_paused:
            # assuming that the handle to the recorder was not destroyed on set_paused()
            # otherwise, a recalculation and restart of the sequence would be required
            self.cursor_sequence.resume()
            print("resuming the recording")
        else:
            print("ERROR set_recording(): this state should not occur. ")
            self.state.print_states()
            exit(1)

        self.set_primary_color(self.recording_primary_color)

    def set_paused(self  # , a_to_set_paused_at=None
                   ):
        self.state.set_paused()

        print("set_paused")
        self.cursor_sequence.pause()
        self.set_primary_color(self.paused_primary_color)

    def set_primary_color(self, primary_color, cursor_color_special=None,
                          line_color_special=None,
                          change_logical_primary_color=True):
        """ A part of the cursor and the line get by default
            the primary color. Optionally, they can be changed individually.

        Args:
            change_logical_primary_color:
               if False, the logical primary_color is not modified, if True, it is.
               This is good for e.g. on-hover short and temporary modifications of the
               primary color. """

        if change_logical_primary_color is True:
            self.primary_color = primary_color

        cursor_color = None
        line_color = None

        if cursor_color_special:
            cursor_color = cursor_color_special
        else:
            cursor_color = primary_color

        if line_color_special:
            line_color = line_color_special
        else:
            line_color = primary_color

        self.p_c.setColor(cursor_color)
        self.line.setColor(line_color)

    def get_primary_color(self):
        return self.primary_color

    def get_state_snapshot(self):
        """ get a snapshot of a state (FIXME?: incomplete information, i.e. not a deep copy of
            the parent class `EdgeRecorderState` of the `EdgeRecorder`) """
        state_snapshot = {
            "state.is_stopped_at_beginning": self.state.is_stopped_at_beginning(),
            "state.is_recording": self.state.is_recording(),
            "state.is_paused": self.state.is_paused(),
            "a": self.state.s_a
        }
        return state_snapshot

    def set_state_from_state_snapshot(self, state_snapshot):
        """ state taken from get_state_snapshot """

        a = state_snapshot["a"]

        if state_snapshot["is_stopped_at_beginning"]:
            self.set_stopped_at_beginning()
        elif state_snapshot["is_stopped_at_end"]:
            self.set_recording_finished()
        elif state_snapshot["is_recording"]:
            self.set_recording(a_to_start_from=a)
        elif state_snapshot["is_paused"]:
            self.set_paused(a_to_set_paused_at=a)
        else:
            print("snapshot matches no valid state, could not be restored!")
            exit(1)

    def remove(self):
        """ removes all
        - sequences
        - p3d nodes (detaches them from render)
        - p3d events (directobjects)
            their references. """

        print("removing EdgeRecorder")

        self.cursor_sequence.pause()  # remove it from the interval manager
        del self.cursor_sequence  # remove the reference

        self.line.nodePath.removeNode()
        # self.p1.nodePath.removeNode()
        # self.p2.nodePath.removeNode()
        self.p_c.remove()

        self.space_direct_object.ignoreAll()
        self.space_direct_object.removeAllTasks()

        self.set_recording_direct_object.ignoreAll()
        self.set_recording_direct_object.removeAllTasks()

        self.recorder_label.remove()
        self.camera_gear.remove_camera_move_hook(self.recorder_label.update)

        # taskMgr.remove(self.rendering_while_waiting_for_audio_thread_task)

    def set_v1(self, v1):
        """ set the starting point of the edge
        Args:
        - v1: p3d Vec3 """
        self.v1 = v1

        self.line.setTipPoint(self.v1)
        self.line.setTailPoint(self.get_v2())

        # call update_while_moving_function manually
        self.update_while_moving_function(
            self.state.s_a, *tuple(self.extraArgs))

    def get_v1(self):
        return self.v1

    def get_v2(self, s_a=None):
        if s_a is None:
            s_a = self.state.s_a

        covered_time = s_a * (EdgeRecorder.s_l/EdgePlayer.lps_rate)
        return self.v1 + self.v_dir * EdgePlayer.lps_rate * covered_time
