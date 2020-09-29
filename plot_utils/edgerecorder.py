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


# class EdgeRecorder:
#     """ This is just a line that grows with time, from one point in space to another, annotated with a Rec. label and a time """
#     def __init__(self, camera_gear):
#         self.p_c = Point3dCursor(Vec3(0., 0., 0.))
#         self.rec_label = Pinned2dLabel(refpoint3d=pos_rel_to_world_x, text="Rec.",
#                                         xshift=0.02, yshift=0.02, font="fonts/arial.egg")
#         self.duration

#         self.camera_gear = camera_gear


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
        self.set_recording()

    def set_recording(self):
        """ continue recording from a paused state """

        self.recording = True
        self.paused = False

    def is_recording(self):
        return (self.recording == True and self.paused == False)

    def set_paused(self):
        self.recording = False
        self.paused = True

    def is_paused(self):
        return (self.recording == False and self.paused == True)

    def __repr__(self):
        return "{recording: " + str(self.recording) + ", paused: " + str(self.paused) + " }"


class EdgeRecorder(EdgeRecorderState):
    """ Adds the graphics and the p3d sequence operations to the logic of EdgeRecorderState """

    recording_primary_color = ((.5, .5, 0., 1.), 1)
    recording_cursor_color = ((.5, .5, 0., 1.), 1)
    recording_line_color = ((.5, .5, 0., 1.), 1)

    paused_primary_color = ((0., .5, .5, 1.), 1)
    paused_cursor_color = ((0., .5, .5, 1.), 1)
    paused_line_color = ((0., .5, .5, 1.), 1)

    def __init__(self, camera_gear):
        # -- do geometry logic
        # make the line small, but pick initial direction

        self.v1_initial = Vec3(-.25, -.25, 0.)
        self.v2_initial = Vec3(+1.5, -1.5, 0.)

        self.direction = math_utils.normalize(math_utils.p3d_to_np(
            self.v2_initial) - math_utils.p3d_to_np(self.v1_initial))

        self.v1 = v1_initial
        self.v2 = v2_initial  # this will change as a function of time

        self.v_c = self.v1  # cursor; initially at beginning, idea: initially at v2_initial, then growing from when it reaches over that
        # self.duration = 0.  # this will grow with time

        self.delay = 0.

        # -- do graphics stuff
        # self.p1 = Point3d(scale=0.03, pos=self.v1)
        # self.p2 = Point3d(scale=0.03, pos=self.v2)

        # self.p_c = Point3d(scale=0.0125, pos=self.v1)
        self.p_c = Point3dCursor()

        self.line = Line1dSolid()
        self.line.setTipPoint(self.v1)
        self.line.setTailPoint(self.v2)

        # self.line = Vector()
        # self.line.setTailPoint(self.v1)
        # self.line.setTipPoint(self.v2)

        self.primary_color = None
        self.set_primary_color(self.recording_primary_color)  # initially

        # actions: record, pause, kill

        # setup the spacebar to continue/start recording or pausing
        self.space_direct_object = DirectObject.DirectObject()
        self.space_direct_object.accept('space', self.react_to_spacebar)

        # kill
        self.set_stopped_at_beginning_direct_object = DirectObject.DirectObject()
        self.set_stopped_at_beginning_direct_object.accept(
            'k', self.react_to_k)

        # -- do p3d sequence stuff
        # ---- initialize the sequence
        # self.extraArgs = [# a, # duration,
        #     self.v1_initial, self.v2_initial, self.v_c, self.direction,
        #     self.p1, self.p2, self.p_c, self.line,
        #     self.p3d_cursor_sequence_intermediate_duration]

        self.s_l = 3.  #, self.s_dur = 1.,
        self.time_ind = 0.5,
        self.vi1 = Vec3(0.5, 0.5, 0.), self.v_dir = Vec3(1., 1., 0.)/np.linalg.norm(Vec3(1., 1., 0.)),
        self.lps_rate = 0.5/1.,  # length per second
        # p1, p2,
        # self.p_c, self.line

        self.extraArgs = [
            self.s_l, # self.s_dur,
            self.time_ind,
            self.vi1, self.v_dir,
            self.lps_rate,
            # p1, p2,
            self.p_c, self.line
        ]

        s_dur = self.s_l / self.lps_rate

        self.p3d_interval = LerpFunc(
            self.update_graphics_function, duration=s_dur, extraArgs=self.extraArgs)
        self.p3d_cursor_sequence = Sequence(Wait(self.delay), self.p3d_interval,
                                            Func(self.on_finish_cursor_sequence))

        # -- init hover and click actions
        self.camera_gear = camera_gear

        self.edge_hoverer = EdgeHoverer(self, self.camera_gear)

        self.edge_mouse_clicker = EdgeMouseClicker(self)

        EdgeRecorderState.__init__(self)

    def update_graphics_function(self,
                                 s_a,
                                 s_l, # s_dur,
                                 time_ind,
                                 vi1, v_dir,
                                 lps_rate,
                                 # p1, p2,
                                 p_c, line):
        # TODO: CONTINUE going through from top down, adapting an edgeplayer to be an edgerecorder instead

        # logical, given:
        # for the current sequence:
        # s_a: parameter between 0 and 1 for the time between the sequence's current start and end points
        # s_l: fixed length of what length a sequence should have (choose a reasonable length, corresponding to a time of maybe 10 seconds, after that, start a new (always finite) sequence)
        # s_dur: fixed duration of the sequence
        # time_ind=1 (s), (time corresponding to the length of the hint line at start of recording),
        # vi1 (branch point),
        # v_dir (direction of branching),
        # lps_rate (length per second rate of the player/recorder)

        # graphical: p1, p2, p_c, line

        # asked (logical):
        # the length of the line at the covered_time (line always just keeps increasing in size, not separate segments). Time in seconds is extracted from s_a (given)
        covered_time = s_a * (s_l/lps_rate)
        covered_length = s_l * s_a

        len_ind = time_ind * lps_rate

        # minimal line length: length corresponding to time_ind
        # if covered_time <= time_ind:
        #     s_a_min = time_ind * lps_rate / s_l
        #     s_a = s_a_min

        s_a_ind = time_ind * lps_rate / s_l

        if s_a <= s_a_ind:
            line.setTipPoint(len_ind * v_dir + vi1)
        elif s_a > s_a_ind:
            line.setTipPoint(covered_length * v_dir + vi1)
        else:
            print("invalid value of s_a: ", s_a)
            exit(1)

        line.setTailPoint(vi1)

        # set cursor point:
        p_c.setPos(covered_length * v_dir + vi1)

        # # v21 = v2 - v1
        # vi21 = v2_initial - v1_initial
        # vi21_length = np.linalg.norm(math_utils.p3d_to_np(vi21))

        # line_length =
        # if line_length < vi21_length:
        #     line_length = vi21_length

        # v_c = v1 + v21 * a
        # # p_c.nodePath.setPos(v_c)
        # p_c.setPos(v_c)
        # line.setTailPoint(v1_initial)
        # line.setTipPoint(direction * math_utils.p3d_to_np(self.v2_initial) - math_utils.p3d_to_np(self.v1_initial))
        # print(# "t = ", t,
        #       # "; duration = ", duration,
        #       " a = ", a)

    def react_to_k(self):
        """ unconditionally jump to the beginning and stop """
        self.set_stopped_at_beginning()

    def react_to_e(self):
        """ unconditionally jump to the beginning and stop """
        self.set_stopped_at_end()

    def react_to_spacebar(self):
        """ spacebar will either:
        - start recording from beginning if it's stopped at the beginning
        - start recording from beginning of the next edge if it's stopped at the end (print 'start at next edge')
        - pause if it's recording
        - record if it's paused
        """

        print("before spacebar")
        print("is_stopped_at_beginning(): ", self.is_stopped_at_beginning(), ", ",
              "is_stopped_at_end(): ", self.is_stopped_at_end(), ", ",
              "is_recording(): ", self.is_recording(), ", ",
              "is_paused(): ", self.is_paused())
        print(self)

        if self.is_stopped_at_beginning():
            self.set_recording(a_to_start_from=0.)
        elif self.is_stopped_at_end():
            self.set_recording(a_to_start_from=0., after_finish=True)
            print(
                "start at next edge (if no next edge, start from beginning of last edge)")
        elif self.is_recording():
            self.set_paused()
        elif self.is_paused():
            self.set_recording()
        else:
            print("situation matches no state!")

        print("after spacebar")
        print("is_stopped_at_beginning(): ", self.is_stopped_at_beginning(), ", ",
              "is_stopped_at_end(): ", self.is_stopped_at_end(), ", ",
              "is_recording(): ", self.is_recording(), ", ",
              "is_paused(): ", self.is_paused())
        print(self)

    def on_finish_cursor_sequence(self):
        self.set_stopped_at_end()

    def set_stopped_at_beginning(self):
        EdgeRecorderState.set_stopped_at_beginning(self)
        # -- do p3d sequence stuff
        # p3d only really has a finish() function, not a 'stopped at start'
        self.p3d_cursor_sequence.pause()
        self.p3d_cursor_sequence.set_t(self.a * self.duration)

        # -- do graphics stuff

        self.set_primary_color(self.stopped_at_beginning_primary_color)

    def set_stopped_at_end(self,  # already_at_end=False
                           ):
        EdgeRecorderState.set_stopped_at_end(self)

        # if already_at_end is False:

        print("stopped at end ", self)

        self.p3d_cursor_sequence.finish()

        # setting pause() is undefined behaviour, if it's already finished.
        # self.p3d_cursor_sequence.pause()
        # self.p3d_cursor_sequence.setT(self.a)
        # print("stopped at end point 2: ", self)
        # else:
        #     print("already_at_end = ", already_at_end, " no need to set T again. ")  # right?

        self.set_primary_color(self.stopped_at_end_primary_color)

    def set_recording(self, a_to_start_from=None, after_finish=False):
        EdgeRecorderState.set_recording(self, a_to_start_from=a_to_start_from)

        if a_to_start_from:
            self.p3d_cursor_sequence.set_t(a_to_start_from * self.duration)
            print("a_to_start_from: ", a_to_start_from)

        if after_finish is True:
            # it needs to be restarted at a=0. Usually this is called after the interval has finished once, to restart the Sequence
            print("attempting to restart the sequence after finish", self)
            self.p3d_cursor_sequence.start()
            print("after restart: ", self)
        else:
            # merely resume, since it is already started (standard state)
            self.p3d_cursor_sequence.resume()

        self.set_primary_color(self.recording_primary_color)

    def set_paused(self, a_to_set_paused_at=None):
        EdgeRecorderState.set_paused(
            self, a_to_set_paused_at=a_to_set_paused_at)

        if a_to_set_paused_at:
            self.p3d_cursor_sequence.set_t(a_to_set_paused_at * self.duration)
            print("a_to_set_paused_at: ", a_to_set_paused_at)

        self.p3d_cursor_sequence.pause()

        self.set_primary_color(self.paused_primary_color)

    def set_primary_color(self, primary_color, cursor_color_special=None, line_color_special=None,
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
            "is_stopped_at_beginning": self.is_stopped_at_beginning(),
            "is_stopped_at_end": self.is_stopped_at_end(),
            "is_recording": self.is_recording(),
            "is_paused": self.is_paused(),
            "a": self.a
        }
        return state_snapshot

    def set_state_from_state_snapshot(self, state_snapshot):
        """ state taken from get_state_snapshot """

        a = state_snapshot["a"]

        if state_snapshot["is_stopped_at_beginning"]:
            self.set_stopped_at_beginning()
        elif state_snapshot["is_stopped_at_end"]:
            self.set_stopped_at_end()
        elif state_snapshot["is_recording"]:
            self.set_recording(a_to_start_from=a)
        elif state_snapshot["is_paused"]:
            self.set_paused(a_to_set_paused_at=a)
        else:
            print("snapshot matches no valid state, could not be restored!")
            exit(1)
