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
# import gltf

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
        # f2l.setPos2d(pos_x=1., pos_y=1.)
        f2l.setPos(Vec3(0., 0., 0.))
        print(f2l.getPos())


        f2d = Frame2d(cg)
        f2d.attach_to_render()

        x = np.linspace(0., 1, num=50)
        # y = np.sinc(x)

        # f2d.set_xlim(-3., 3.)

        f2d.set_figsize(0.9, 0.75)

        # f2d.plot(x, 0.0*x,
        #              color="yellow", )

        f2d.plot(x, 0.0*x,
                     color="yellow", )


        # f2d.clear_plot()
        # f2d.plot(x, np.sin(x**3.), color="orange")


        # f2d.clear_plot()
        # f2d.plot(x, math_utils.random_polynomial(x), color="red")

        # f2d.clear_plot()
        # f2d.plot(x, np.cos(x**3.), color="red")

        # f2d.clear_plot()
        # f2d.plot(x, np.cos(x**3.), color="red")

        colors = ["red", "blue", "green"]


        # math_utils.random_polynomial_normalized(x)
        def update_random_polynomial():
            """ """
            f2d.clear_plot()
            f2d.plot(x, math_utils.random_polynomial_normalized(x),
                     color=colors[int(np.abs(np.random.rand()*3-0.001))])
            # f2d.plot(x, np.cos(x),
            #          color=colors[int(np.abs(np.random.rand()*3-0.001))])
            # f2d.plot(x, 0.01*x,
            #          color=colors[int(np.abs(np.random.rand()*3-0.001))])

        base.accept("r", update_random_polynomial)



        # f2d.set_figsize(0.9, 0.9)

        # f2d.setScale(1., 0., 0.9)

        # f2d.set_figsize(0.9, 0.1)

        # f2d.quad.set_width(0.2)

        # toggle clipping planes
        base.accept("c", lambda f2d=f2d: f2d.toggle_clipping_planes())

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

        a = Vector()
        a.setTipPoint(Vec3(1., 1., 1.))
        a.setTailPoint(Vec3(0.3, 0.3, 0.3))
        a.reparentTo_p3d(render)
        a.setColor(Vec4(0., 1., 1., 1.), 1)


        # q = Quad(width=1.25, height=0.95)
        # q.set_width(0.5)
        # q.reparentTo_p3d(render)

        cg.set_view_to_xz_plane()


        # self.accept("r", self.OnRec)


    def OnRec(self):
        """ """
        self.movie(namePrefix = 'movie', duration = 1.0, fps = 30, format = 'png', sd = 4, source = None)


app = MyApp()
app.run()
base.movie(namePrefix='frame', duration=407, fps=24, format='png')
