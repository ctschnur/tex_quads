from interactive_tools.picking import CollisionPicker, PickableObjectManager
from interactive_tools.dragging_and_dropping_objects import DragAndDropObjectsManager
from interactive_tools.pickables import PickablePoint, PickablePointDragger

from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle

from composed_objects.composed_objects import Point3dCursor

from local_utils import math_utils

from simple_objects.simple_objects import Line1dSolid, PointPrimitive
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

from simple_objects.text import Pinned2dLabel

from interactive_tools import cameraray

from functools import partial

from plot_utils.edgemousetools import EdgeHoverer, EdgeMouseClicker

from direct.interval.IntervalGlobal import Wait, Sequence, Func
from direct.interval.LerpInterval import LerpFunc

from plot_utils.edgeplayer import EdgePlayer

class EdgePlayerRecorderSpawner:
    """ when recording, you first record and then, after recording, transform the recorder into a player
    Every time an EdgeRecorder is created, it is given an instance of an EdgePlayerRecorderSpawner. This object will then spawn an EdgePlayer, once
    the finish() function of the recorder is called. From then on, the EdgePlayerRecorderSpawner (in memory)
    - creates an edgeplayer from the edgerecorder and displays it
    - removes (removes all nodes from engine.tq_graphics_basics.tq_render, and unregisters the DirectObjects (events)) the edgerecorder

    (future: - attaches the edgeplayer to the graph where it's been spawned from)
    """
    def __init__(self# , camera_gear, edge_recorder=None
    ):
        """ """
        # self.camera_gear = camera_gear

        # if edge_recorder is None:
        #     self.edge_recorder = EdgeRecorder(self.camera_gear)

        # self.edge_recorder = None
        self.edge_player = None

    # def create_EdgePlayer_delete_EdgeRecorder(self):
    #     self.edge_player = EdgePlayer(self.camera_gear)

    def set_edge_player(self, edge_player : EdgePlayer):
        """ if this transformer already has an EdgePlayer, remove that one first,
            before reassigning a new edge_player """

        assert edge_player is not self.edge_player

        if self.edge_player is None:
            self.edge_player = edge_player
        else:
            self.edge_player.remove()


    @staticmethod
    def set_EdgePlayers_state_from_EdgeRecorder(edge_player : EdgePlayer,
                                                edge_recorder, # : EdgeRecorder
                                                s_a_finished

    ):
        """ This will transform an `EdgeRecorder` to an `EdgePlayer` and remove
            the `EdgeRecorder`.
        Args:
            - edge_player: instance of an EdgePlayer, which gets transformed inside this function
            """
        # edge_player = EdgePlayer(camera_gear)

        # mapping of the states
        if edge_recorder.state.is_stopped_at_beginning():
            print("Error: a stopped_at_beginning EdgeRecorder has not recorded anything, thus can't be converted into an EdgePlayer")
            exit(1)

        elif edge_recorder.state.is_recording() or edge_player.state.is_paused():
            print("Error: end the recording first, before converting to an EdgePlayer")
            exit(1)

        elif edge_recorder.state.is_recording_finished():
            print("Recording is finished, converting to EdgePlayer -> stopped_at_end")

            # transfer logical stuff
            edge_player.v_dir = edge_recorder.v_dir

            edge_player.set_duration(s_a_finished * edge_recorder.s_dur)

            print("duration of the recorded: ", edge_player.get_duration())

            edge_player.set_v1(edge_recorder.get_v1())  # this will update v2 appropriately



            # set state:
            edge_player.set_stopped_at_beginning()  # default, maybe change that?

            edge_recorder.remove()  # deletes backend-specific graphics and event handlers

            del edge_recorder  # remove the recorder fom scope

        else:
            print("Error: set_EdgePlayer_state: case not handled")
            exit(1)
