import engine
from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3, PlaneNode, Plane, LPlanef, OrthographicLens, MatrixLens
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain, Point3dCursor, CrossHair3d, GroupNode
from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle, TextureOf2dImageData, OrientedDisk

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

from cameras.Orbiter import OrbiterOrtho
from cameras.panner2d import Panner2d

from direct.task import Task
from plot_utils.bezier_curve import BezierCurve, DraggableBezierCurve, SelectableBezierCurve
from panda3d.core import CollisionTraverser, CollisionHandlerQueue, CollisionRay, CollisionNode, GeomNode, BitMask32, VBase4
from plot_utils.graph import Graph, DraggableGraph, GraphHoverer
from simple_objects.primitives import IndicatorPrimitive, Box2dCentered, ConePrimitive, Box2d, Stroke2d
from sequence.sequence import Sequence, WavSequence
from plot_utils.quad import Quad

from plot_utils.symbols.waiting_symbol import WaitingSymbol
from plot_utils.ui_thread_logger import UIThreadLogger, ProcessingBox, UIThreadLoggerElement
from plot_utils.ui_thread_logger import UIThreadLogger, uiThreadLogger
import plot_utils.ui_thread_logger

from plot_utils.DraggableFrame import DraggableFrame
from plot_utils.DraggableResizableFrame import DraggableResizableFrame
from plot_utils.DraggableResizableDrawableOnFrame import DraggableResizableDrawableOnFrame

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

from plot_utils.colors.colors import get_color

from plot_utils.pdf_renderer import PDFPageTextureObject, PopplerPDFRenderer

from pdf_viewer.tools import PDFViewer, PDFPanner2d

from pdf_annotator.tools import PDFAnnotator

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        engine.tq_graphics_basics.init_engine(render, aspect2d, loader)

        base.setFrameRateMeter(True)
        engine.tq_graphics_basics.tq_render.setAntialias(AntialiasAttrib.MAuto)

        shade_of_gray = 0.2
        base.setBackgroundColor(shade_of_gray, shade_of_gray, shade_of_gray)

        cg = cameras.Orbiter.OrbiterOrtho(base.cam, r_init=2.)
        # cg.set_view_to_yz_plane()
        cg.set_view_to_xz_plane()

        cs = CoordinateSystemP3dPlain()
        cs.attach_to_render()

        # fdp2d = FreehandDrawingPath2d()
        # fdp2d.attach_to_render()

        # -------- create custom geometry --------------

        # groupnode_pos = Vec3(0., 0., 0.)
        # p1 = Vec3(0., 0., 0.)
        # p2 = Vec3(2., 0., 0.)
        # diff_vec = p2 - p1
        # disk_num_of_verts = 20
        # color_vec4=Vec4(1., 1., 1., 1.)
        # radius = 0.1

        # rss = createRoundedStrokeSegment2d()
        # rss.reparentTo(render)

        # s2d = Stroke2d()
        # s2d.attach_to_render()

        # rss1 = createRoundedStrokeSegment2d()
        # s2d.append_stroke_segment(rss1)

        # rss2 = createRoundedStrokeSegment2d(p1=(0., 0.), p2=(2., 3.))
        # s2d.append_stroke_segment(rss2)

        s2d2 = Stroke2d()
        s2d2.attach_to_render()
        s2d2.append_point((0., 0.))

        s2d2.append_point((1., 0.))

        s2d2.append_point((1., 1.))

        s2d2.append_point((1., 1.))

        # rss2 = createRoundedStrokeSegment2d()
        # rss1.reparentTo(render

        cg_pdf_panner2d = PDFPanner2d(base.cam)

        drawing_frame = DraggableResizableDrawableOnFrame(cg_pdf_panner2d, height=0.2, width=0.7, quad_border_thickness=10.)
        # drawing_frame.reparentTo(self)

        drawing_frame.attach_to_render()
        # drawing_frame.setPos(Vec3(-1., -0.5, 1.))
        drawing_frame.bg_quad.setColor(Vec4(1., 1., 1., 0.2), 1)
        # drawing_frame.bg_quad.set_border_color(Vec4(1., 0., 0., 1.0), 1)
        drawing_frame.setPos(Vec3(-1., -0.5, 1.))

app = MyApp()

app.run()
# base.movie(namePrefix='frame', duration=407, fps=24, format='png')
