import engine
from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3, PlaneNode, Plane, LPlanef, OrthographicLens, MatrixLens
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain, Point3dCursor, CrossHair3d, GroupNode
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

from cameras.Orbiter import OrbiterOrtho
from cameras.panner2d import Panner2d

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


# def plot_audio_file_profile(camera_gear):
#     """ """
#     f2d3 = Frame2d(attach_to_space="aspect2d")
#     # f2d3 = Frame2d(attach_to_space="render", camera_gear=camera_gear, update_labels_orientation=True
#     # )

#     wave_file_path = "/home/chris/Desktop/playbacktest2.wav"
#     wf = wave.open(wave_file_path, 'rb')
#     p = pyaudio.PyAudio()
#     stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
#                               channels=wf.getnchannels(),
#                               rate=wf.getframerate(),
#                               output=True)
#     data = wf.readframes(
#         CHUNK * get_wave_file_number_of_frames(wave_file_path))

#     y = np.fromstring(np.ravel(data), dtype=np.int32)
#     t_f = get_wave_file_duration(wave_file_path)
#     t = np.linspace(0., 1., num=len(y)) * t_f

#     t_scale_factor = 0.05
#     strip_width = 0.25
#     space = 0.125
#     f2d3.set_figsize(*np.array([t_f * t_scale_factor, strip_width]))
#     f2d3.setPos(0., 0, 0.)

#     step = int((len(y)-1)/25)
#     y = np.abs(y[0:-1:step])
#     t = t[0:-1:step]

#     y = y.astype(float)
#     t = t.astype(float)

#     y = y/max(y)
#     t = t/max(t)

#     space = 0.05

#     color="orange"

#     for i, (ti, yi) in enumerate(zip(t, y)):
#         if np.abs(yi) < 1e-8:
#             f2d3.plot([ti, ti], [-space, +space], color=color)
#         else:
#             f2d3.plot([ti, ti], [0, yi], color=color)

#     f2d3.set_xlim(min(t), max(t))
#     f2d3.set_ylim(-max(y), max(y))


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        engine.tq_graphics_basics.init_engine(render, aspect2d, loader)

        base.setFrameRateMeter(True)
        engine.tq_graphics_basics.tq_render.setAntialias(AntialiasAttrib.MAuto)

        shade_of_gray = 0.2
        base.setBackgroundColor(shade_of_gray, shade_of_gray, shade_of_gray)

        # cg = cameras.Orbiter.OrbiterOrtho(base.cam, r_init=5.)
        # cg.set_view_to_xz_plane()

        # cg = Panner2d(base.cam)

        # self.cg = cg

        cs = CoordinateSystemP3dPlain()
        cs.attach_to_render()

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

        # df = DraggableResizableFrame(cg, height=0.2, width=0.7)
        # df.attach_to_render()

        # df.setPos(Vec3(0.1, 0., 0.))

        # df.setColor(Vec4(0., 1., 1., 1.), 1)

        self.vecp0 = Vector()
        # self.vecp0.setTipPoint(Vec3(-1., 0., 1.))
        self.vecp0.setTipPoint(Vec3(1., 0., 0.))
        self.vecp0.setTailPoint(Vec3(0., 0., 0.))
        self.vecp0.reparentTo(engine.tq_graphics_basics.tq_render)
        self.vecp0.setColor(Vec4(1., 0., 0., 0.5), 1)

        self.vecp1 = Vector()
        self.vecp1.setTipPoint(Vec3(0., 1., 0.))
        self.vecp1.setTailPoint(Vec3(0., 0., 0.))
        self.vecp1.reparentTo(engine.tq_graphics_basics.tq_render)
        self.vecp1.setColor(Vec4(0., 1., 0., 0.5), 1)

        self.vecp2 = Vector()
        self.vecp2.setTipPoint(Vec3(0., 0., 1.))
        self.vecp2.setTailPoint(Vec3(0., 0., 0.))
        self.vecp2.reparentTo(engine.tq_graphics_basics.tq_render)
        self.vecp2.setColor(Vec4(0., 0., 1., 0.5), 1)


        # -------------

        # slp = primitives.SegmentedLinePrimitive(color=get_color("yellow"), thickness=2)

        # slp.extendCoords([np.array([0., 0., 0.]), np.array([1., 1., 1.]), np.array([1., 0., 0.])])

        # slp.attach_to_render()

        # slp.extendCoords([np.array([1., 1., 0.])])

        # slp.attach_to_render()

        # -------------

        # gn = GroupNode()
        # gn.attach_to_render()

        # slp = primitives.SegmentedLinePrimitive(color=get_color("yellow"), thickness=2)

        # slp.extendCoords([np.array([0., 0., 0.]), np.array([1., 1., 1.]), np.array([1., 0., 0.])])

        # slp.reparentTo(gn)

        # slp.extendCoords([np.array([1., 1., 0.])])

        # slp.reparentTo(gn)

        # print("-----: ", engine.tq_graphics_basics.get_window_size_x())

        # # -------------

        # TODO: set Panner2d position from pdf width


        # cg_pdf_panner2d = PDFPanner2d(base.cam)

        # cg = cameras.Orbiter.OrbiterOrtho(base.cam, r_init=5.)
        # cg.set_view_to_xz_plane()

        # # ------ PDF Viewer -----------

        # cg_pdf_panner2d = PDFPanner2d(base.cam)
        # pdfv = PDFViewer(cg_pdf_panner2d, "pdfs/sample.pdf")
        # pdfv.attach_to_render()

        # # slp.reparentTo_p3d(render)

        # ddf = DraggableResizableDrawableOnFrame(cg_pdf_panner2d, height=0.2, width=0.7)
        # ddf.attach_to_render()
        # ddf.setPos(Vec3(-1., -0.5, 1.))
        # ddf.bg_quad.setColor(Vec4(1., 1., 1., 0.0), 1)
        # ddf.bg_quad.set_border_color(Vec4(1., 0., 0., 1.0), 1)

        # ------ PDF Annotator -----------

        cg_pdf_panner2d = PDFPanner2d(base.cam)
        pdfa = PDFAnnotator(cg_pdf_panner2d, "pdfs/sample.pdf")
        # pdfa = PDFAnnotator(cg_pdf_panner2d, "pdfs/Bruus-Flensberg-1.pdf")
        pdfa.attach_to_render()
        # slp.reparentTo_p3d(render)


        # ddf = DraggableResizableDrawableOnFrame(cg_pdf_panner2d, height=0.2, width=0.7)
        # ddf.attach_to_render()
        # ddf.setPos(Vec3(-1., -0.5, 1.))
        # ddf.bg_quad.setColor(Vec4(1., 1., 1., 0.0), 1)
        # ddf.bg_quad.set_border_color(Vec4(1., 0., 0., 1.0), 1)

        # TODO: Point3d: Scale it to match PDFPanner2d's scaling movements

        from pdf_annotator.gui.point3d import Point3dCGPanner
        p_ind_panner = Point3dCGPanner(cg_pdf_panner2d, scale=2.)
        p_ind_panner.setPos(Vec3(1., 0., 1.))
        p_ind_panner.setColor(Vec4(0., 0., 0., 1.))

        # # -----------

        # b2d1 = Box2d()
        # b2d1.attach_to_render()
        # b2d1.setColor(Vec4(1., 1., 1., 0.1), 1)

        # b2d2 = Box2d()
        # b2d2.attach_to_render()
        # b2d2.setPos(b2d2.getPos() - Vec3(0., 1., 0.))
        # b2d2.setColor(Vec4(1., 0., 1., 0.1), 1)

        # b2d2.setScale(0.2, 1.0, 1.)

        # self.a = Vector()
        # self.a.setTipPoint(Vec3(0., 0., 1.))
        # self.a.setTailPoint(Vec3(0., 0., 0.))
        # self.a.reparentTo_p3d(render)
        # self.a.setColor(Vec4(0., 1., 1., 1.), 1)

        # self.camera = self.cg.camera

        # base.accept('mouse1', self.onPress)
        # self.p_xy_offset = None

    # def onPress(self):
    #     mouse_pos = base.mouseWatcherNode.getMouse()

    #     mouse_position_before_dragging = base.mouseWatcherNode.getMouse()
    #     p_xy_at_init_drag = conventions.getFilmCoordsFromMouseCoords(
    #         -mouse_position_before_dragging[0],
    #         -mouse_position_before_dragging[1],
    #         p_x_0=0., p_y_0=0.)

    #     self.p_xy_at_init_drag = p_xy_at_init_drag



    #     r0_obj = math_utils.p3d_to_np(-Vec3(p_xy_at_init_drag[0], 0., p_xy_at_init_drag[1]))
    #     self.position_before_dragging = Vec3(*r0_obj)

    #     self.task_obj_update = taskMgr.add(self.update_vectors, 'update_vectors')

    #     # self.a.setTailPoint(-Vec3(*r0_obj) + self.cg.visual_aids.crosshair.getPos())

    #     print("onPress -----------------")

    # def update_vectors(self, task):
    #     """ """
    #     if base.mouseWatcherNode.hasMouse():
    #         mouse_pos = base.mouseWatcherNode.getMouse()
    #         # mouse_position_before_dragging = base.mouseWatcherNode.getMouse()
    #         # p_xy_offset = conventions.getFilmCoordsFromMouseCoords(
    #         #     -mouse_position_before_dragging[0],
    #         #     -mouse_position_before_dragging[1],
    #         #     p_x_0=0., p_y_0=0.)

    #         p_xy_offset = self.p_xy_offset


    #         r0_obj = math_utils.p3d_to_np(Vec3(0., 0., 0.))

    #         v_cam_forward = math_utils.p3d_to_np(engine.tq_graphics_basics.tq_render.getRelativeVector(self.camera, self.camera.node().getLens().getViewVector()))
    #         v_cam_forward = v_cam_forward / np.linalg.norm(v_cam_forward)
    #         # self.camera.node().getLens().getViewVector()

    #         v_cam_up = math_utils.p3d_to_np(engine.tq_graphics_basics.tq_render.getRelativeVector(self.camera, self.camera.node().getLens().getUpVector()))
    #         v_cam_up = v_cam_up / np.linalg.norm(v_cam_up)

    #         r_cam = math_utils.p3d_to_np(self.camera.getPos())

    #         e_up = math_utils.p3d_to_np(v_cam_up/np.linalg.norm(v_cam_up))

    #         e_cross = math_utils.p3d_to_np(np.cross(v_cam_forward/np.linalg.norm(v_cam_forward), e_up))

    #         # determine the middle origin of the draggable plane (where the plane intersects the camera's forward vector)
    #         r0_middle_origin = math_utils.LinePlaneCollision(v_cam_forward, r0_obj, v_cam_forward, r_cam)

    #         # print("r0_obj", r0_obj)
    #         # print("v_cam_forward", v_cam_forward)
    #         # print("v_cam_up", v_cam_up)
    #         # print("r_cam", r_cam)
    #         # print("e_up", e_up)
    #         # print("e_cross", e_cross)
    #         # print("r0_middle_origin", r0_middle_origin)

    #         # -- calculate the bijection between mouse coordinates m_x, m_y and plane coordinates p_x, p_y

    #         mouse_pos = base.mouseWatcherNode.getMouse()  # between -1 and 1 in both x and y
    #         # filmsize = base.cam.node().getLens().getFilmSize()  # the actual width of the film size

    #         # print("p_xy_offset: ", self.p_xy_at_init_drag)

    #         p_x, p_y = conventions.getFilmCoordsFromMouseCoords(mouse_pos[0], mouse_pos[1], self.p_xy_at_init_drag[0], self.p_xy_at_init_drag[1])
    #         # p_x, p_y = conventions.getFilmCoordsFromMouseCoords(mouse_pos[0], mouse_pos[1], 0., 0.)

    #         drag_vec = p_x * e_cross + p_y * e_up

    #         # print("drag_vec", drag_vec)

    #         # set the position while dragging
    #         self.this_frame_drag_pos = self.position_before_dragging + Vec3(*drag_vec)

    #         self.a.setTipPoint(self.this_frame_drag_pos)
    #         return task.cont
    #     else:
    #         return task.done

app = MyApp()
app.run()
base.movie(namePrefix='frame', duration=407, fps=24, format='png')
