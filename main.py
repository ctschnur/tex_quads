import engine
from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3, PlaneNode, Plane, LPlanef
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain, Point3dCursor, CrossHair3d
from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle, TextureOf2dImageData

from simple_objects.text import Fixed2dLabel

from simple_objects import primitives
from local_utils import math_utils

import numpy as np
import math
import local_tests.svgpathtodat.main

import os
import sys
import pytest

import cameras.Orbiter
import cameras.plain_camera_gear
from direct.task import Task
from plot_utils.bezier_curve import BezierCurve, DraggableBezierCurve, SelectableBezierCurve
from panda3d.core import CollisionTraverser, CollisionHandlerQueue, CollisionRay, CollisionNode, GeomNode, BitMask32, VBase4
from plot_utils.graph import Graph, DraggableGraph, GraphHoverer
from simple_objects.primitives import IndicatorPrimitive, Box2dCentered, ConePrimitive, Box2d
from sequence.sequence import Sequence, WavSequence
from plot_utils.quad import Quad

from plot_utils.symbols.waiting_symbol import WaitingSymbol
from plot_utils.ui_thread_logger import UIThreadLogger, ProcessingBox, UIThreadLoggerElement
from plot_utils.ui_thread_logger import UIThreadLogger, uiThreadLogger
import plot_utils.ui_thread_logger

from plot_utils.DraggableFrame import DraggableFrame, DRFrame

from statemachine.edgeplayer import EdgePlayerSM
from interactive_tools.draggables import DraggablePoint, DraggableEdgePlayer

from engine.tq_graphics_basics import TQGraphicsNodePath
import engine.tq_graphics_basics
from simple_objects.mpl_integration import RotatingMatplotlibFigure

import plot_utils.colors.colors as pucc

from recording.recorder import Recorder
from recording.recorder_for_live_updating import Recorder_for_live_updating

import scipy
from scipy import fftpack

from interactive_tools.picking import CollisionPicker, PickableObjectManager

from engine.tq_graphics_basics import TQGraphicsNodePath
import engine.tq_graphics_basics

from interactive_tools.dragging_and_dropping_objects import DragAndDropObjectsManager
from interactive_tools.pickables import PickablePoint, PickablePointDragger
from interactive_tools.pickable_object_dragger import PickableObjectDragger

from playback.audiofunctions import get_wave_file_duration, get_wave_file_number_of_frames, CHUNK
import wave
import pyaudio

from plot_utils.frame2d import Frame2d, Ticks
from simple_objects.text import BasicText, Basic2dText

from plot_utils.StreamFrames import StreamFramesFromRecorder


def plot_audio_file_profile(camera_gear):
    """ """
    f2d3 = Frame2d(attach_to_space="aspect2d")
    # f2d3 = Frame2d(attach_to_space="render", camera_gear=camera_gear, update_labels_orientation=True
    # )

    wave_file_path = "/home/chris/Desktop/playbacktest2.wav"
    wf = wave.open(wave_file_path, 'rb')
    p = pyaudio.PyAudio()
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                              channels=wf.getnchannels(),
                              rate=wf.getframerate(),
                              output=True)
    data = wf.readframes(
        CHUNK * get_wave_file_number_of_frames(wave_file_path))

    y = np.fromstring(np.ravel(data), dtype=np.int32)
    t_f = get_wave_file_duration(wave_file_path)
    t = np.linspace(0., 1., num=len(y)) * t_f

    t_scale_factor = 0.05
    strip_width = 0.25
    space = 0.125
    f2d3.set_figsize(*np.array([t_f * t_scale_factor, strip_width]))
    f2d3.setPos(0., 0, 0.)

    step = int((len(y)-1)/25)
    y = np.abs(y[0:-1:step])
    t = t[0:-1:step]

    y = y.astype(float)
    t = t.astype(float)

    y = y/max(y)
    t = t/max(t)

    space = 0.05

    color="orange"

    for i, (ti, yi) in enumerate(zip(t, y)):
        if np.abs(yi) < 1e-8:
            f2d3.plot([ti, ti], [-space, +space], color=color)
        else:
            f2d3.plot([ti, ti], [0, yi], color=color)

    f2d3.set_xlim(min(t), max(t))
    f2d3.set_ylim(-max(y), max(y))


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        engine.tq_graphics_basics.init_engine(render, aspect2d, loader)

        base.setFrameRateMeter(True)
        engine.tq_graphics_basics.tq_render.setAntialias(AntialiasAttrib.MAuto)

        shade_of_gray = 0.2
        base.setBackgroundColor(shade_of_gray, shade_of_gray, shade_of_gray)

        cg = cameras.Orbiter.Orbiter(base.cam, radius=3.)

        # base.accept("d", lambda: exec("import ipdb; ipdb.set_trace()"))
        # dep = DraggableEdgePlayer("/home/chris/Desktop/playbacktest2.wav", cg, taskMgr)

        # f2d3 = Frame2d(camera_gear=cg, attach_to_space="render", update_labels_orientation=True)
        # # f2d3.set_figsize(0.8, 0.5)
        # sffr = StreamFramesFromRecorder(f2d3)

        # plot_audio_file_profile(cg)

        # a = Vector()
        # a.setTipPoint(Vec3(1., 1., 1.))
        # a.setTailPoint(Vec3(0.3, 0.3, 0.3))
        # a.reparentTo_p3d(render)
        # a.setColor(Vec4(0., 1., 1., 1.), 1)

        cg.set_view_to_xz_plane()

        # df = DraggableFrame(cg)
        # df.setPos(Vec3(0., 0., 0.6))
        # df.attach_to_render()

        # df = DraggableFrame(cg)
        # df.setPos(Vec3(0., 0., 0.6))
        # df.attach_to_render()

        # df = DraggableFrame(cg, height=0.2, width=0.7)
        # df.setPos(Vec3(-0.8, 0., 0.7))
        # df.setColor(Vec4(0., 1., 0., 1.), 1)
        # df.attach_to_render()

        # quad = Quad(height=0.5, width=0.7, thickness=5.)
        # quad.setColor(Vec4(0., 1., 0., 1.), 1)
        # quad.reparentTo_p3d(render)

        # line = Line1dSolid(thickness=5.)
        # line.setColor(1.0, 1.0, 0., 1.)
        # line.setTailPoint(Vec3(0.25, 0., 0.))
        # line.setTipPoint(Vec3(0.75, 0., 0.))
        # line.reparentTo_p3d(render)
        # line.setColor(Vec4(0., 1., 1., 1.), 1)
        # line.setPos(Vec3(-0.8, 0., 0.7))

        df = DRFrame(cg, height=0.2, width=0.7)
        df.attach_to_render()
        # df.setPos(Vec3(0.1, 0., 0.))

        # df.setColor(Vec4(0., 1., 1., 1.), 1)

        # self.vecp0 = Vector()
        # # self.vecp0.setTipPoint(Vec3(-1., 0., 1.))
        # self.vecp0.setTipPoint(Vec3(0., 0., 0.))
        # self.vecp0.setTailPoint(Vec3(0., 0., 0.))
        # self.vecp0.reparentTo(engine.tq_graphics_basics.tq_render)
        # self.vecp0.setColor(Vec4(0., 0., 0., 1.), 1)


        # -----------

        # b2d1 = Box2d()
        # b2d1.attach_to_render()
        # b2d1.setColor(Vec4(1., 1., 1., 0.1), 1)

        # b2d2 = Box2d()
        # b2d2.attach_to_render()
        # b2d2.setPos(b2d2.getPos() - Vec3(0., 1., 0.))
        # b2d2.setColor(Vec4(1., 0., 1., 0.1), 1)

        # b2d2.setScale(0.2, 1.0, 1.)

app = MyApp()
app.run()
base.movie(namePrefix='frame', duration=407, fps=24, format='png')
