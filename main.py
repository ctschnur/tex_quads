import engine
from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain, Point3dCursor, CrossHair3d
from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle, Fixed2dLabel, TextureOf2dImageData, TextureOfMatplotlibFigure
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

import threading

from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt

def generate_polynomial(x, coeffs, shifts):
    """ """
    my_sum = 0.
    for i, coeff in enumerate(coeffs):
        my_sum += coeffs[i] * (x + shifts[i])**float(i)

    return my_sum

def random_polynomial(x):
    """ """
    num_of_coeffs = int(np.random.rand() * 10.) + 1
    coeffs = np.random.rand(num_of_coeffs) * np.sign(0.5 - np.random.rand(num_of_coeffs))
    shifts = np.random.rand(num_of_coeffs) * np.sign(0.5 - np.random.rand(num_of_coeffs))
    print(len(coeffs), len(shifts))
    return generate_polynomial(x, coeffs, shifts)

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        engine.tq_graphics_basics.init_engine(render, aspect2d, loader)

        base.setFrameRateMeter(True)
        engine.tq_graphics_basics.tq_render.setAntialias(AntialiasAttrib.MAuto)

        shade_of_gray = 0.
        base.setBackgroundColor(shade_of_gray, shade_of_gray, shade_of_gray)

        # self.thread_loggers_demo()

        ob = cameras.Orbiter.Orbiter(base.cam, radius=3.)

        # mto = TextureOf2dImageData(scaling=10.)
        # mto.attach_to_render()

        # mto = TextureOf2dImageData(scaling=10.)
        # mto.attach_to_render()

        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(5, 5))
        # ax = fig.add_axes([0.2, 0.2, 0.7, 0.7])
        # x = np.linspace(0, np.pi * 2., 50)
        # ax.plot(x, np.sin(x))

        # fig.tight_layout()
        tmplf = TextureOfMatplotlibFigure(fig, scaling=1.0, backgroud_opacity=0.0)
        tmplf.attach_to_aspect2d()
        width, height = tmplf.get_dimensions_from_calc()
        from conventions.conventions import win_aspect_ratio
        tmplf.setPos(Vec3(1.0 * win_aspect_ratio - width, 0., -1.))

        # # ax.plot(x, np.cos(x))
        # # tmplf.update_figure_texture()
        # ob.set_view_to_xz_plane()

        # x1, x2 = -2., 2.
        # y1, y2 = -2., 2.

        # x = np.linspace(x1, x2, 1000)
        # # fig, ax = plt.subplots(1)

        # ax.set_xlim(x1, x2)
        # ax.set_ylim(y1, y2)

        self.angle = 0.

        self.ax = fig.add_subplot(111, projection='3d')

        import time
        # initial_time = time.time()
        # angle = 0.

        def my_is_alive_function(time_offset, initial_time=None):
            cond = initial_time + time_offset > time.time()
            # print(initial_time, time.time(), cond)
            return cond

        plot_utils.ui_thread_logger.uiThreadLogger = UIThreadLogger()
        plot_utils.ui_thread_logger.uiThreadLogger.attach_to_aspect2d()
        # plot_utils.ui_thread_logger.uiThreadLogger.setPos(Vec3(0., 0., 0.))

        def add_plot_thread_wrapped():
            """ """
            td = threading.Thread(target=self.add_plot, daemon=True)
            td.start()

            def wait_for_thread_to_finish_task(task):
                """ """
                if td.is_alive():
                    return task.cont

                self.ax.w_xaxis.line.set_color("white")
                self.ax.w_yaxis.line.set_color("white")
                self.ax.w_zaxis.line.set_color("white")

                tmplf.update_figure_texture(update_full=True, # tight_layout=True
                )
                # base.acceptOnce("c", add_plot_thread_wrapped)

                # time.sleep(0.2)
                # Wait(0.001)
                add_plot_thread_wrapped()

                return task.done

            taskMgr.add(wait_for_thread_to_finish_task, 'foo')

            # plot_utils.ui_thread_logger.uiThreadLogger.append_new_parallel_task(
            #     "plotting", lambda: td.is_alive())

        # base.acceptOnce("c", add_plot_thread_wrapped)

        add_plot_thread_wrapped()

        # plot_utils.ui_thread_logger.uiThreadLogger.append_new_parallel_task(
        #         "plotting", lambda initial_time=time.time(): (
        #             my_is_alive_function(2., initial_time=initial_time)))


        cs = CoordinateSystem(ob)
        cs.attach_to_render()
        cs.setPos(Vec3(0., 0., 0.))

        # cs2 = CoordinateSystem(ob)
        # cs2.attach_to_render()

        # # cs2.setPos(Vec3(1., 1., 1.))

        # cs2.setMat(math_utils.get_R_y_forrowvecs(0.2) * math_utils.get_R_z_forrowvecs(0.2) * math_utils.get_R_x_forrowvecs(0.2) * math_utils.getTranslationMatrix3d_forrowvecs(1., 1., 1.))

        # # self.render_edge_player(ob)

        base.accept("d", lambda: exec("import ipdb; ipdb.set_trace()"))

        # # esm = EdgePlayerSM("/home/chris/Desktop/playbacktest2.wav", ob, taskMgr)
        # # esm.transition_into(esm.state_load)
        # # esm.gcsm.edge_graphics.set_v2_override(Vec3(1., 0., 0.))

        # # dp = DraggablePoint(ob)
        # # dp.setPos(Vec3(1., 0., 0.))
        # # print(dp.getPos())

        # dep = DraggableEdgePlayer("/home/chris/Desktop/playbacktest2.wav", ob, taskMgr) #

        # from plot_utils.frame2d import Frame2d

        # f2d = Frame2d()
        # # f2d.attach_to_aspect2d()
        # f2d.attach_to_render()

        # # dp1 = DraggablePoint(ob)
        # # dp1.attach_to_render()
        # # dp1.setPos(Vec3(1., 0., 0.))
        # # print(dp1.getPos())

        # # dp2 = DraggablePoint(ob)
        # # dp2.setPos(Vec3(2., 0., 0.))
        # # print(dp2.getPos())

        # # ob.set_view_to_xy_plane()

    def add_plot(self):
        """ """
        self.ax.cla()

        # make the panes transparent
        self.ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        self.ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        self.ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))

        # self.ax.plot(x, random_polynomial(x))

        # fig = plt.figure()
        # ax = fig.add_subplot(111, projection='3d')

        # Grab some test data.
        X, Y, Z = axes3d.get_test_data(0.05)

        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = 10 * np.outer(np.cos(u), np.sin(v))
        y = 10 * np.outer(np.sin(u), np.sin(v))
        z = 10 * np.outer(np.ones(np.size(u)), np.cos(v))

        # Plot the surface

        # Plot a basic wireframe.
        self.ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10)
        self.angle += 0.75 * 1.
        self.ax.view_init(30, self.angle)

    def render_edge_player(self, camera_gear):
        """ Render the edge player """
        from plot_utils.edgeplayer import EdgePlayer
        ep = EdgePlayer(
            camera_gear, wave_file_path="/home/chris/Desktop/playbacktest.wav")

    def thread_loggers_demo(self):
        # uiThreadLogger
        plot_utils.ui_thread_logger.uiThreadLogger = UIThreadLogger()
        plot_utils.ui_thread_logger.uiThreadLogger.attach_to_aspect2d()

        plot_utils.ui_thread_logger.uiThreadLogger.setPos(Vec3(0., 0., 0.))


        ob = cameras.Orbiter.Orbiter(base.cam, radius=3.)
        ob.set_view_to_xy_plane()
        cs = CoordinateSystem(ob)
        cs.attach_to_render()

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

        # from plot_utils.edgeplayerrecorderspawner import EdgePlayerRecorderSpawner
        # from plot_utils.edgerecorder import EdgeRecorder

        # # in the event of ending a recording, this will store a handle to the EdgePlayer
        # eprs = EdgePlayerRecorderSpawner()
        # # this will get removed from scope once the recording is done
        # er = EdgeRecorder(ob, eprs)

    def draw_vectors_demo(self):
        l = Line1dSolid()

        l.setTipPoint(Vec3(2.0, 0.1, 0.))
        l.setTailPoint(Vec3(1.0, 0.1, 0.))

        l2 = Line1dSolid()

        l2.setTipPoint(Vec3(0.5, 0.2, 0.))
        l2.setTailPoint(Vec3(0.0, 0.2, 0.))

        # a = Vector(tail_point_logical=Vec3(1., .7, 0.), tip_point_logical=Vec3(-0.5, -0.5, 0.0))

        a = Vector()

        # a.group_node.hide()

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
