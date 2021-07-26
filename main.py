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
from simple_objects.primitives import IndicatorPrimitive, Box2dCentered, ConePrimitive
from sequence.sequence import Sequence, WavSequence
from plot_utils.quad import Quad

from plot_utils.symbols.waiting_symbol import WaitingSymbol
from plot_utils.ui_thread_logger import UIThreadLogger, ProcessingBox, UIThreadLoggerElement
from plot_utils.ui_thread_logger import UIThreadLogger, uiThreadLogger
import plot_utils.ui_thread_logger

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

class F2dUpdater:
    """ """
    def __init__(self, next_color_func, xy_datas, f2d):
        """ """
        self.ctr = 0
        self.next_color_func = next_color_func
        self.xy_datas = xy_datas
        self.f2d = f2d

    def add_plot(self):
        """ """
        self.f2d.plot(self.xy_datas[self.ctr][0],
                      self.xy_datas[self.ctr][1],
                      color=self.next_color_func())
        self.ctr += 1
        self.ctr = self.ctr % len(self.xy_datas)

        print("self.ctr:", self.ctr)

class FramesUpdater:
    """ """
    def __init__(self, f2d, tf_in_s, fps):
        """ accepts a Frame2d """

        self.idx_frame_old = 0

        self.f2d = f2d

        self.frame_xs = np.linspace(0, 1., num=100)
        self.frames = []

        self.tf_in_s = tf_in_s  # e.g. 3
        self.fps = fps  # e.g. 25

        self.ti = 0
        self.tf = self.tf_in_s * self.fps
        for t in range(self.ti, self.tf):
            self.frames.append([
                self.frame_xs, (0.5 * (1+t/self.tf)) *
                (np.sin(self.frame_xs*t) +
                 np.cos(np.sqrt(self.frame_xs*t/self.tf)*self.tf))])

        self.frame_ctr = 0

    def get_next_frame(self):
        """ """
        _frame = self.frames[self.frame_ctr]
        self.frame_ctr += 1
        return _frame

    def render_frame(self, a):
        """ 0 < a < 1 """
        idx_frame = int(a*self.tf)
        x, y = self.frames[idx_frame]
        self.f2d.clear_plot()
        self.f2d.plot(x, y)

class StreamFramesFromRecorder:
    """ stream the frames from the recorder to a Frame2d """
    def __init__(self, f2d):
        self.f2d = f2d
        self.recorder = Recorder_for_live_updating()
        self.recorder.do_record(
            lambda: True,
            lambda: False,
            lambda: False)

        self.factor = 1.0e-1 * 0.2

        self.f2d.set_ylim(-0.25, 2.)
        self.f2d.set_xlim(0., 22028. * self.factor)

        taskMgr.add(self.update_task, 'foo')

    def update_task(self, task):
        if self.recorder.is_recorder_thread_done() == True:
            return task.done
        elif (self.recorder.is_recorder_thread_done() == False):
            self.render_last_frame()
            return task.cont
        elif (self.recorder.is_recorder_thread_done() is None):
            return task.cont

    def render_last_frame(self):
        y = self.recorder.grab_last_frames(num=5)

        if y is not None:
            y = np.fromstring(np.ravel(y), dtype=np.int32)
            y = np.abs(scipy.fft(y))
            freqs = fftpack.fftfreq(len(y), (1./Recorder_for_live_updating.RATE))

            x = freqs

            y = y[:int(len(y) * self.factor)]
            x = x[:int(len(x) * self.factor)]

            y /= (1e11 * 0.5)

            self.f2d.clear_plot()
            self.f2d.plot(x, y)

class StreamFramesFromRecorderTimeDomain:
    """ stream the frames from the recorder to a Frame2d """
    def __init__(self, f2d):
        self.f2d = f2d
        self.recorder = Recorder_for_live_updating()
        self.recorder.do_record(
            lambda: True,
            lambda: False,
            lambda: False)

        max_ampl = 1.0
        self.f2d.set_ylim(-max_ampl, max_ampl)
        self.f2d.set_xlim(0., 1.)

        taskMgr.add(self.update_task, 'foo2')

    def update_task(self, task):
        if self.recorder.is_recorder_thread_done() == True:
            return task.done
        elif (self.recorder.is_recorder_thread_done() == False):
            self.render_last_frame()
            return task.cont
        elif (self.recorder.is_recorder_thread_done() is None):
            return task.cont

    def render_last_frame(self):
        """ 0 < a < 1 """
        y = self.recorder.grab_last_frames(num=1)

        if y is not None:
            y = np.fromstring(np.ravel(y), dtype=np.int32)
            sample_down_indices = np.linspace(0, len(y), num=100).astype(int)[:-1]

            y = y[sample_down_indices]
            y = y * 1.5e-9 * 5

            t = np.linspace(0., 1., num=len(y)) # ?
            x = t

            self.f2d.clear_plot()
            self.f2d.plot(x, y)

from engine.tq_graphics_basics import TQGraphicsNodePath
import engine.tq_graphics_basics

from interactive_tools.dragging_and_dropping_objects import DragAndDropObjectsManager
from interactive_tools.pickables import PickablePoint, PickablePointDragger
from interactive_tools.pickable_object_dragger import PickableObjectDragger

class DraggableFrame(TQGraphicsNodePath):
    """ """
    def __init__(self, camera_gear, **kwargs):
        """ """
        TQGraphicsNodePath.__init__(self, **kwargs)

        self.camera_gear = camera_gear
        self.point3d = Point3d()

        self.quad = Quad(thickness=1.5)
        self.quad.set_height(0.25)
        self.quad.set_width(0.25)

        self.quad.reparentTo(self)
        self.point3d.reparentTo(self)
        self.point3d.setPos(Vec3(0., 0., 0.))

        # -------------------------------------

        self.pom = PickableObjectManager()
        self.pom.tag(self.point3d.get_p3d_nodepath())

        self.dadom = DragAndDropObjectsManager()

        self.pt_dragger = PickableObjectDragger(self.point3d, self.camera_gear)
        self.pt_dragger.add_on_state_change_function(self.move_frame_when_dragged)

        self.dadom.add_dragger(self.pt_dragger)

        self.collisionPicker = CollisionPicker(
            camera_gear, engine.tq_graphics_basics.tq_render,
            base.mouseWatcherNode, self.dadom)

        # -- add a mouse task to check for picking
        self.p3d_direct_object = DirectObject.DirectObject()
        self.p3d_direct_object.accept(
            'mouse1', self.collisionPicker.onMouseTask)

    def move_frame_when_dragged(self):
        new_handle_pos = self.point3d.getPos()
        self.quad.setPos(new_handle_pos)

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        engine.tq_graphics_basics.init_engine(render, aspect2d, loader)

        base.setFrameRateMeter(True)
        engine.tq_graphics_basics.tq_render.setAntialias(AntialiasAttrib.MAuto)

        shade_of_gray = 0.2
        base.setBackgroundColor(shade_of_gray, shade_of_gray, shade_of_gray)

        # cg = cameras.plain_camera_gear.PlainCameraGear(base.cam)
        # cg.setPos(Vec3(0., -1., 0.))

        cg = cameras.Orbiter.Orbiter(base.cam, radius=3.)
        self.cg = cg

        # rmplf = RotatingMatplotlibFigure()
        # rmplf.attach_to_aspect2d()

        # csp2 = CoordinateSystemP3dPlain()
        # csp2.attach_to_render()
        # csp2.setPos(Vec3(0., 0., 0.))

        base.accept("d", lambda: exec("import ipdb; ipdb.set_trace()"))
        # dep = DraggableEdgePlayer("/home/chris/Desktop/playbacktest2.wav", cg, taskMgr)
        # ------------

        from plot_utils.frame2d import Frame2d, Ticks
        # ---------------------------

        f2d3 = Frame2d(camera_gear=cg,
                       update_labels_orientation=True,
                       # update_labels_orientation=False,  # TODO: make BasicText work in Frame2d, i.e. orient text in aspect2d correctly
                       with_ticks=True,
                       attach_to_space="render",
                       # attach_directly=True
                       )

        # f2d3.attach_to_render()
        # f2d3.attach_to_aspect2d()

        # f2d3.set_figsize(*np.array([1., 0.5])*1)
        # f2d3.setPos(-1.25, 0., -0.125 + -0.5 + 0.5 + 0.25)

        # f2d3.setPos(-16/9 + space, 0., -1 + space)
        # f2d3.update_alignment()
        # f2d3.plot(y)

        # ------------
        from playback.audiofunctions import get_wave_file_duration, get_wave_file_number_of_frames, CHUNK
        import wave
        import pyaudio

        self.wave_file_path = "/home/chris/Desktop/playbacktest2.wav"
        # self.wav_sequence = WavSequence(self.wave_file_path)
        # self.wav_sequence.start_load_thread()

        self.wf = wave.open(self.wave_file_path, 'rb')
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
                                  channels=self.wf.getnchannels(),
                                  rate=self.wf.getframerate(),
                                  output=True)

        data = self.wf.readframes(
            CHUNK * get_wave_file_number_of_frames(self.wave_file_path))

        y = np.fromstring(np.ravel(data), dtype=np.int32)
        t_f = get_wave_file_duration(self.wave_file_path)
        t = np.linspace(0., 1., num=len(y)) * t_f

        t_scale_factor = 0.05
        strip_width = 0.25
        space = 0.125
        f2d3.set_figsize(*np.array([t_f * t_scale_factor, strip_width]))
        f2d3.setPos(0., 0, 0.)

        # numof_steps = 50
        # step = int((len(y)-1)/50)
        # y = y[0:step:len(y)-1]
        # t = t[0:step:len(t)-1]

        step = int((len(y)-1)/25)
        # y = np.abs(y[0:-1:step])
        y = np.abs(y[0:-1:step])
        t = t[0:-1:step]

        y = y.astype(float)
        t = t.astype(float)

        # t = np.linspace(0, 3*np.pi, num=25)
        # y = np.sin(t)

        y = y/max(y)
        # y2 = -y

        t = t/max(t)

        # y = y/np.abs(max(y))

        space = 0.05

        color="orange"

        # fig, ax = plt.subplots(1)

        for i, (ti, yi) in enumerate(zip(t, y)):
            if np.abs(yi) < 1e-8:
                f2d3.plot([ti, ti], [-space, +space], color=color)
            else:
                f2d3.plot([ti, ti], [0, yi], color=color)

        # t = np.linspace(0., 2*3.14) * 1
        # y = np.sin(t)

        # # print("t_f", t_f)

        # print(np.shape(y), np.shape(t))
        # # ----------

        print("-----------------")
        print("t, y: ", t, y)
        print("type(t), type(y): ", type(t), type(y))
        print("np.shape(t), np.shape(y): ", np.shape(t), np.shape(y))
        print("-----------------")

        # f2d3.plot(t, y, color="orange")
        # f2d3.plot(t, -y, color="green")

        f2d3.set_xlim(min(t), max(t))
        f2d3.set_ylim(-max(y), max(y))


        # ------------

        from simple_objects.text import BasicText, Basic2dText

        # bt = BasicText(text="basic text")
        # bt.attach_to_aspect2d()
        # bt.attach_to_render()
        # ------------

        # bt = Basic2dText(text="basic text")
        # bt.attach_to_aspect2d()

        # f2d3.set_xlim(min(t), max(t))
        # f2d3.set_ylim(min(y), max(y))

        # f2d3.update_alignment()

        # f2d3.set_ylim(-1, 1.)
        # sffr = StreamFramesFromRecorder(f2d3)

        # while self.wav_sequence.load_thread_finished_p() is False:
        #     print("waiting")

        # # ------------

        # f2l = Fixed2dLabel(text=str(1))
        # f2l.attach_to_aspect2d()
        # f2l.setPos(Vec3(0., 0., 0.))

        # # ------------

        # print(f2l.getPos())

        # ----------- BEGIN FRAME2d experiments --------

        # f2d = Frame2d(cg, update_labels_orientation=False, with_ticks=True)
        # f2d.attach_to_render()

        # f2d.set_figsize(*np.array([1., 0.5])*1)

        # f2d.set_xlim(0., 1.)
        # f2d.set_ylim(-1., 1.)

        # x = np.linspace(0, 1, num=100)
        # f2d.plot(x, np.sin(10*x), color="orange")
        # f2d.plot(x, 2.*np.sin(5*x), color="blue")
        # f2d.plot(x, np.array([2.5]*len(x)), color="white")

        # f2d.update_alignment()

        # # ----------- END FRAME2d experiments --------

        # colors = ["red", "blue", "green"]

        # xy_datas = [[x, 2*x],
        #             [x, 3*x],
        #             [x, x**2],
        #             [x, (x+1)**3 + 2],
        #             [x, -(x+1)**3 + 2],
        #             [x, np.exp(x)]]

        # # ---------------------------

        # f2dUpdater = F2dUpdater(
        #     pucc.get_next_mpl_color,
        #     xy_datas,
        #     f2d
        # )

        # base.accept("r", f2dUpdater.add_plot)

        # # ----------

        # time_in_s = 1000
        # fps = 60

        # fu = FramesUpdater(f2d, time_in_s, fps)

        # sf_seq = Sequence()
        # sf_seq.set_sequence_params(
        #     duration=time_in_s,  # in seconds ?
        #     extraArgs=[],
        #     update_function=fu.render_frame,
        #     on_finish_function=fu.say_finished)

        # sf_seq.start()

        # # ---------------------------

        # f2d3 = Frame2d(cg, update_labels_orientation=False, with_ticks=False)
        # # f2d3.attach_to_render()
        # f2d3.attach_to_aspect2d()

        # # f2d3.set_figsize(*np.array([1., 0.5])*1)
        # # f2d3.setPos(-1.25, 0., -0.125 + -0.5 + 0.5 + 0.25)

        # space = 0.125
        # f2d3.set_figsize(*np.array([1., 0.5])*0.5)
        # f2d3.setPos(-1+space, 0, -1+space)

        # # f2d3.setPos(-16/9 + space, 0., -1 + space)

        # # f2d3.

        # f2d3.update_alignment()

        # sffr = StreamFramesFromRecorder(f2d3)

        # # ---------------------------

        # ---- second frame

        # f2d2 = Frame2d(cg, update_labels_orientation=False, with_ticks=True)
        # f2d2.attach_to_render()

        # f2d2.set_figsize(*np.array([1., 0.5]))
        # f2d2.setPos(-1.25, 0., -0.125 -0.5)

        # f2d2.update_alignment()

        # sffr2 = StreamFramesFromRecorderTimeDomain(f2d2)

        # sffr.render_last_frame,

        # --------------

        # self.anim_seq = Sequence()

    #     self.anim_seq.set_sequence_params(
    #         duration=self.duration,
    #         extraArgs=[],
    #         update_function=self.update,
    #         on_finish_function=self.restart_animation)

    #     self.anim_seq.start()

    # def restart_animation(self):
    #     self.anim_seq.set_t(0.)
    #     self.anim_seq.resume()

        # f2d.set_figsize(0.9, 0.9)
        # f2d.setScale(1., 0., 0.9)
        # f2d.set_figsize(0.9, 0.1)
        # f2d.quad.set_width(0.2)

        # toggle clipping planes
        # base.accept("c", lambda f2d=f2d: f2d.toggle_clipping_planes())

        # l = Line1dSolid(thickness=2.0, color=Vec4(0., 1., 0., 1.))
        # l.setColor(Vec4(0., 1., 1., 1.), 1)

        # l.setTipPoint(Vec3(1., 1., 1.))
        # l.setTailPoint(Vec3(0.5, 0.5, 0.5))
        # l.reparentTo_p3d(render)

        # def update_sequence(a, f2d, initial_width, initial_height):
        #     """ """
        #     f2d.clear_plot()
        #     f2d.plot(x + a, np.sin(x + a))

        # s = Sequence(
        #     duration=5.,
        #     extraArgs=[f2d, f2d.width, f2d.height],
        #     update_function=update_sequence,
        #     on_finish_function=lambda: None
        # )
        # s.start()

        # a = Vector()
        # a.setTipPoint(Vec3(1., 1., 1.))
        # a.setTailPoint(Vec3(0.3, 0.3, 0.3))
        # a.reparentTo_p3d(render)
        # a.setColor(Vec4(0., 1., 1., 1.), 1)

        # # height:  0.0335018546320498 , width:  0.2910444438457489
        # height:  0.0670037092640996 , width:  0.17515186220407486

        # q = Quad(width=0.17515186220407486, height=0.0670037092640996, color=(1,0,1,1))
        # q.setPos(0, 0, -0.25)
        # q.reparentTo_p3d(render)

        # q2 = Quad(width=0.149, height=0.034, color=(1,0,1,1))
        # q2.setPos(0, 0, -0.5)
        # q2.reparentTo_p3d(render)

        cg.set_view_to_xz_plane()

        # self.accept("r", self.OnRec)


        # -------

        # from interactive_tools.sketching import SketcherDraggable
        # sktr = SketcherDraggable(cg)

        # # dp_handle = DraggablePoint(cg)
        # # dp_handle.setPos(Vec3(0, 0, 0))

        # quad = Quad(thickness=1.5)
        # quad.setPos(Vec3(0., 0., 0.5))
        # quad.set_height(0.5)
        # quad.set_width(0.5)
        # # quad.set_h(0.5)

        # quad.attach_to_render()

        # # -------

        # df = DraggableFrame(cg)
        # df.setPos(Vec3(0., 0., 0.6))
        # df.attach_to_render()

    def OnRec(self):
        """ """
        self.movie(namePrefix = 'movie', duration = 1.0, fps = 30,
                   format = 'png', sd = 4, source = None)


app = MyApp()
app.run()
base.movie(namePrefix='frame', duration=407, fps=24, format='png')
