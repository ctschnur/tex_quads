import engine
from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3, PlaneNode, Plane, LPlanef
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain, Point3dCursor, CrossHair3d
from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle, Fixed2dLabel, TextureOf2dImageData

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

# --------

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
        self.frame_ctr = self.frame_ctr % self.tf
        _frame = self.frames[self.frame_ctr]
        print("self.frame_ctr:", self.frame_ctr)
        self.frame_ctr += 1
        return _frame

    def render_frame(self, a):
        """ 0 < a < 1 """
        idx_frame = int(a*self.tf)
        x, y = self.frames[idx_frame]
        # x, y = self.get_next_frame()

        if self.idx_frame_old != idx_frame:
            self.f2d.clear_plot()
            self.f2d.plot(x, y)

        self.idx_frame_old = idx_frame

    def say_finished(self):
        print("finished!")

# --------


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

        from plot_utils.frame2d import Frame2d, Ticks

        f2l = Fixed2dLabel(text=str(1))
        f2l.attach_to_aspect2d()
        f2l.setPos(Vec3(0., 0., 0.))

        # print(f2l.getPos())

        # ----------- BEGIN FRAME2d experiments --------

        f2d = Frame2d(cg)
        f2d.attach_to_render()

        f2d.set_figsize(1., 0.8)

        x = np.linspace(-5, 5, num=100)
        f2d.plot(x, np.sin(10*x), color="orange")
        f2d.plot(x, 2.*np.sin(5*x), color="blue")
        f2d.plot(x, np.array([2.5]*len(x)), color="white")

        # ----------- END FRAME2d experiments --------

        colors = ["red", "blue", "green"]

        xy_datas = [[x, 2*x],
                    [x, 3*x],
                    [x, -1*x**2],
                    [x, (x+1)**3 + 2],
                    [x, -(x+1)**3 + 2],
                    [x, np.exp(x)]]

        f2dUpdater = F2dUpdater(
            pucc.get_next_mpl_color,
            xy_datas,
            f2d
        )

        base.accept("r", f2dUpdater.add_plot)


        # ----------

        time_in_s = 100
        fps = 25

        fu = FramesUpdater(f2d, time_in_s, 5)

        sf_seq = Sequence()
        sf_seq.set_sequence_params(
            duration=time_in_s,  # in seconds ?
            extraArgs=[],
            update_function=fu.render_frame,
            on_finish_function=fu.say_finished)

        sf_seq.start()

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


    def OnRec(self):
        """ """
        self.movie(namePrefix = 'movie', duration = 1.0, fps = 30, format = 'png', sd = 4, source = None)


app = MyApp()
app.run()
base.movie(namePrefix='frame', duration=407, fps=24, format='png')
