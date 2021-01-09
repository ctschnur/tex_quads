
from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain, Point3dCursor, CrossHair3d
from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle, Fixed2dLabel
from simple_objects import primitives
from local_utils import math_utils

import numpy as np
import math

from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

import local_tests.svgpathtodat.main

import os
import sys
import pytest
# import gltf

from cameras.Orbiter import Orbiter

from direct.task import Task

from plot_utils.bezier_curve import BezierCurve, DraggableBezierCurve, SelectableBezierCurve

from panda3d.core import CollisionTraverser, CollisionHandlerQueue, CollisionRay, CollisionNode, GeomNode, BitMask32, VBase4

from plot_utils.graph import Graph, DraggableGraph, GraphHoverer

from simple_objects.primitives import IndicatorPrimitive, Box2dCentered, ConePrimitive

from sequence.sequence import Sequence

from plot_utils.quad import Quad

from plot_utils.symbols.waiting_symbol import WaitingSymbol

from plot_utils.ui_thread_logger import UIThreadLogger, ProcessingBox, UIThreadLoggerElement

from plot_utils.ui_thread_logger import UIThreadLogger, uiThreadLogger

import plot_utils.ui_thread_logger

from statemachine.statemachine import EdgePlayerStateMachine



class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.setFrameRateMeter(True)
        render.setAntialias(AntialiasAttrib.MAuto)

        shade_of_gray = 0.3
        base.setBackgroundColor(shade_of_gray, shade_of_gray, shade_of_gray)

        ob = Orbiter(base.cam, radius=3.)
        # ob.set_view_to_xy_plane()
        cs = CoordinateSystem(ob)

        # self.render_edge_player(ob)

        base.accept("d", lambda: exec("import ipdb; ipdb.set_trace()"))
        # base.acceptOnce("e", lambda: print("hi"))

        # esm = EdgePlayerStateMachine(taskMgr, directobject=base)
        # # esm.transition_into(esm.state1)
        # esm.transition_into(esm.wait_for_loading, next_state_args=("myaudio.wav",))


        # esm = EdgePlayerStateMachine("/home/chris/Desktop/playbacktest.wav",
        #                              taskMgr)

        # esm.transition_into(esm.state_load)


        # # --------- playbackersm
        # pbdo = DirectObject.DirectObject()
        # from playback.playback import PlaybackerSM
        # pbsm = PlaybackerSM("/home/chris/Desktop/playbacktest.wav", taskMgr, directobject=pbdo)
        # pbsm.transition_into(pbsm.state_load_wav)
        # # ---------

        # --------- graphickersm
        from playback.audiofunctions import get_wave_file_duration
        durat = get_wave_file_duration("/home/chris/Desktop/playbacktest.wav")

        gcdo = DirectObject.DirectObject()
        from plot_utils.graphickersm import GraphickerSM
        gcsm = GraphickerSM(durat, taskMgr, directobject=gcdo)

        gcsm.transition_into(gcsm.state_load_graphics)
        # ---------


        # base.accept("mouse1", lambda: exec("import ipdb; ipdb.set_trace()"))

        # self.thread_loggers_demo()

    def render_edge_player(self, camera_gear):
        """ Render the edge player """
        from plot_utils.edgeplayer import EdgePlayer
        ep = EdgePlayer(
            camera_gear, wave_file_path="/home/chris/Desktop/playbacktest.wav")

    def thread_loggers_demo(self):
        # uiThreadLogger
        plot_utils.ui_thread_logger.uiThreadLogger = UIThreadLogger()

        ob = Orbiter(base.cam, radius=3.)
        ob.set_view_to_xy_plane()
        cs = CoordinateSystem(ob)

        import time
        initial_time = time.time()

        def my_is_alive_function(time_offset):
            cond = initial_time + time_offset > time.time()
            # print(initial_time, time.time(), cond)
            return cond

        plot_utils.ui_thread_logger.uiThreadLogger.append_new_parallel_task(
            "my desc 1", lambda: my_is_alive_function(1.))
        plot_utils.ui_thread_logger.uiThreadLogger.append_new_parallel_task(
            "my desc 2", lambda: my_is_alive_function(2.))
        plot_utils.ui_thread_logger.uiThreadLogger.append_new_parallel_task(
            "my desc 3", lambda: my_is_alive_function(3.))

        from plot_utils.edgeplayerrecorderspawner import EdgePlayerRecorderSpawner
        from plot_utils.edgerecorder import EdgeRecorder

        # in the event of ending a recording, this will store a handle to the EdgePlayer
        eprs = EdgePlayerRecorderSpawner()
        # this will get removed from scope once the recording is done
        er = EdgeRecorder(ob, eprs)

    def draw_vectors_demo(self):
        l = Line1dSolid()

        l.setTipPoint(Vec3(2.0, 0.1, 0.))
        l.setTailPoint(Vec3(1.0, 0.1, 0.))

        l2 = Line1dSolid()

        l2.setTipPoint(Vec3(0.5, 0.2, 0.))
        l2.setTailPoint(Vec3(0.0, 0.2, 0.))

        # a = Vector(tail_point_logical=Vec3(1., .7, 0.), tip_point_logical=Vec3(-0.5, -0.5, 0.0))

        a = Vector()

        # a.groupNode.hide()

        a.setTipPoint(Vec3(1., 0., 0.)  # , param=True
                      )
        a.setTailPoint(Vec3(0.5, 0., 0.)  # , param=True
                       )

        a2 = Vector(color=Vec4(0., 1., 0., 1.))

        a2.setTailPoint(Vec3(1., 1.0, 0.)  # , param=True
                        )
        a2.setTipPoint(Vec3(0.5, 0.5, 0.)  # , param=True
                       )

        l3 = Line1dSolid()

        l3.setTipPoint(Vec3(0.5, 0.5, 0.))
        l3.setTailPoint(Vec3(0.0, 0.5, 0.))

        l4 = Line1dSolid()

        l4.setTipPoint(Vec3(1., 1., 0.))
        l4.setTailPoint(Vec3(0.0, 1., 0.))


app = MyApp()
app.run()
