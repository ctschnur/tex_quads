
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

        # uiThreadLogger
        plot_utils.ui_thread_logger.uiThreadLogger = UIThreadLogger()

        ob = Orbiter(base.cam, radius=3.)
        cs = CoordinateSystem(ob)

        cs.attachScatter

        # ax = Axis(Vec3(1., 0., 0.), thickness1dline=5, color=Vec4(1., 1., 1., 1.))

        # csplain = CoordinateSystemP3dPlain()

        # ob.set_view_to_yz_plane()
        # ob.set_view_to_xy_plane()

        # from simple_objects.simple_objects import Pinned2dLabel

        # q = Quad(thickness=3.0, nodePath_creation_parent_node=aspect2d)

        # q.set_pos_vec3(Vec3(0., 0., 0.))
        # q.set_height(0.2)
        # q.set_width(0.2)

        # import time
        # initial_time = time.time()

        # def my_done_function():
        #     return initial_time + 5. < time.time()

        # ws = WaitingSymbol(my_done_function, Vec3(-.5, 0., 0.), size=0.1)

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

        # from plot_utils.ui_thread_logger import ProcessingBox
        # pb = ProcessingBox(my_done_function)
        # a = Sequence(duration=50., extraArgs=[pb], update_while_moving_function=lambda a, pb: pb.set_xy_pos(a, 0.)).start()

        # uitle = UIThreadLoggerElement("my desk", lambda: not my_done_function())

        # fl = Fixed2dLabel(text="MYTEXT", font="fonts/arial.egg",
        #                   x=0.,
        #                   y=0.5,
        #                   nodePath_creation_parent_node=aspect2d)

        # import matplotlib.pyplot as plt
        # import networkx as nx

        # hd = "H" + chr(252) + "sker D" + chr(252)
        # mh = "Mot" + chr(246) + "rhead"
        # mc = "M" + chr(246) + "tley Cr" + chr(252) + "e"
        # st = "Sp" + chr(305) + "n" + chr(776) + "al Tap"
        # q = "Queensr" + chr(255) + "che"
        # boc = "Blue " + chr(214) + "yster Cult"
        # dt = "Deatht" + chr(246) + "ngue"

        # G = nx.Graph()
        # G.add_edge(hd, mh)
        # G.add_edge(mc, st)
        # G.add_edge(boc, mc)
        # G.add_edge(boc, dt)
        # G.add_edge(st, dt)
        # G.add_edge(q, st)
        # G.add_edge(dt, mh)
        # G.add_edge(st, mh)

        # dg = DraggableGraph(ob)
        # gh = GraphHoverer(dg, ob)

        # gh = GraphHoverer()

        # f2dl = Fixed2dLabel(text="play", font="fonts/arial.egg", xshift=0.1,
        #                     yshift=0.1, nodePath_creation_parent_node=aspect2d)

        # self.line = Line1dSolid(nodePath_creation_parent_node=aspect2d)
        # self.line.setTailPoint(Vec3(1., 0., 1.))
        # self.line.setTipPoint(Vec3(0.5, 0., 0.))

        # cp = CursorPlayer()

        # from plot_utils.edgeplayer import EdgePlayer

        # ep = EdgePlayer(ob)

        # --- loading symbol: line turning inside a quad

        # a simple edgerecorder, starting at an arbitrary point and ending on demand

        # do = DirectObject.DirectObject()
        # do.accept('d', lambda : ep.set_v1(Vec3(np.random.rand(),
        #                                        np.random.rand(),
        #                                        0.)))

        from plot_utils.edgeplayerrecorderspawner import EdgePlayerRecorderSpawner
        from plot_utils.edgerecorder import EdgeRecorder

        # in the event of ending a recording, this will store a handle to the EdgePlayer
        eprs = EdgePlayerRecorderSpawner()
        # this will get removed from scope once the recording is done
        er = EdgeRecorder(ob, eprs)

        #         import time
        # initial_time = time.time()

        # def my_is_alive_function(time_offset):
        #     cond = initial_time + time_offset > time.time()
        #     # print(initial_time, time.time(), cond)
        #     return cond

        # uiThreadLogger.append_new_parallel_task("my desc 1", lambda: my_is_alive_function(1.))
        # uiThreadLogger.append_new_parallel_task("my desc 2", lambda: my_is_alive_function(2.))

        # from plot_utils.edgehoverer import EdgeHoverer

        # self.line = Line1dSolid()

        # self.line.setTailPoint(Vec3(1., 1., 0.))
        # self.line.setTipPoint(Vec3(0.5, 0.5, 0.))

        # self.line.setTailPoint(Vec3(1., 1., 0.))
        # self.line.setTipPoint(Vec3(0.5, 0.5, 0.))

        # self.myvec = Vector()
        # self.myvec.setTailPoint(Vec3(1., 1., 0.))
        # self.myvec.setTipPoint(Vec3(1.5, 1.5, 0.))

        # self.line.setTipPoint(Vec3(0.5, 0.5, 0.))
        # self.line.setTailPoint(Vec3(1., 1., 0.))

        # oc = OrientedCircle(
        #     origin_point=Vec3(0., 0., 0.),
        #     normal_vector=Vec3(0., 0., 1.),
        #     radius=0.1,
        #     num_of_verts=30,
        #     with_hole=False)

        # cursor = Point3dCursor(Vec3(1., 0., 0.))

        # point1_vec3 = Vec3(1., 1., 0.)
        # point2_vec3 = Vec3(2., 2., 0.)
        # myvec = Vector(# tail_point_logical=point1_vec3, tip_point_logical=point2_vec3
        # )
        # myvec.setTailPoint(point1_vec3)
        # myvec.setTipPoint(point2_vec3)

        # the vector class has an artifact

        # self.draw_vectors_demo()

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
