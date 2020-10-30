
from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain, Point3dCursor
from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle, Fixed2dLabel
from simple_objects import primitives
from local_utils import math_utils

import numpy as np

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


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.setFrameRateMeter(True)
        render.setAntialias(AntialiasAttrib.MAuto)

        # ob = Orbiter(base.cam, radius=3.)
        # ob.set_view_to_xy_plane()

        # cs = CoordinateSystem(ob)

        self.draw_twobody_system()
        
    def draw_twobody_system(self):
        ob = Orbiter(base.cam, radius=3.)
        ob.set_view_to_xy_plane()

        cs = CoordinateSystem(ob)

        from plot_utils.twobodysystem.calc import get_pos_as_func_of_time

        stop_time = 50.0
        num_points = 10000

        p1_color = (0., 0., 1., 1.)
        p2_color = (1., 1., 0., 1.)

        def render_twobodysystem(a, m, p1: Point3d, p2: Point3d):
            """
            Args:
                a: param between 0 and 1 -> time
                m: list of [t, x1_vec, x2_vec]
                p1, p2: graphical points 1 and 2 """

            t = np.array(m[0])
            x1_vec = m[1]
            x2_vec = m[2]

            duration = max(t)
            assert duration == stop_time
            # display one out of the discrete positions, the closest one to the time in the sequence
            i_to_display = np.where(t <= a * duration)[0][-1]

            # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
            p1.setPos(math_utils.np_to_p3d_Vec3(
                np.append(x1_vec[i_to_display], 0.)))
            p2.setPos(math_utils.np_to_p3d_Vec3(
                np.append(x2_vec[i_to_display], 0.)))

            p_new1 = Point3d(scale=0.25)
            p_new1.setPos(math_utils.np_to_p3d_Vec3(
                np.append(x1_vec[i_to_display], 0.)))
            p_new1.setColor(p1_color)

            p_new2 = Point3d(scale=0.25)
            p_new2.setPos(math_utils.np_to_p3d_Vec3(
                np.append(x2_vec[i_to_display], 0.)))
            p_new2.setColor(p2_color)

            pass

        def get_radius_from_mass_3d_sphere(mass):
            """ assume incompressibility
            Args:
                mass: a positive number
            Returns: radius """
            rho = 1.
            return (3. * mass / (4. * rho * np.pi))**(1./3.)

        # two bodies: two points
        m1 = 1
        m2 = 2

        p1 = Point3d(scale=get_radius_from_mass_3d_sphere(m1))
        p1.setColor(p1_color)
        p1.setPos(Vec3(1., 0., 0.))

        p2 = Point3d(scale=get_radius_from_mass_3d_sphere(m2))
        p2.setPos(Vec3(0.5, 0., 0.))
        p2.setColor(p2_color)

        myseq = Sequence(duration=stop_time,
                         extraArgs=[
                             # the solution vector including the times
                             get_pos_as_func_of_time(
                                 stoptime=stop_time, numpoints=num_points,
                                 m1=m1, m2=m2, nc1=1, nc2=-1,
                                 v1=(0.2, -0.2), v2=(0., 0.4), x1=(-0.5, 0.), x2=(+0.5, 0.)),
                             p1,
                             p2
                         ],
                         update_while_moving_function=render_twobodysystem)
        myseq.start()

    def thread_loggers_demo():
        # uiThreadLogger
        plot_utils.ui_thread_logger.uiThreadLogger = UIThreadLogger()

        ob = Orbiter(base.cam, radius=3.)
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
