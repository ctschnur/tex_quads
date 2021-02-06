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

        # p1 = Point3d(scale=1.0)
        # p1.attach_to_render()
        # p1.setPos(Vec3(0.25, 0.5, 0.75))

        # p2 = Point3d(scale=1.0)
        # p2.attach_to_aspect2d()
        # p2.setPos(Vec3(0.25, 0., 0.75))

        # render.setScale(1., 1., 5.)

        # def onWindowEvent(window):
        #     width = base.win.getProperties().getXSize()
        #     height = base.win.getProperties().getYSize()
        #     base.cam.node().getLens().setFilmSize(width, height)
        #     base.cam.node().getLens().setFocalLength(200)

        # base.accept(base.win.getWindowEvent(), onWindowEvent)

        # plot_utils.ui_thread_logger.uiThreadLogger = UIThreadLogger()
        # plot_utils.ui_thread_logger.uiThreadLogger.attach_to_aspect2d()

        # rmplf = RotatingMatplotlibFigure()
        # rmplf.attach_to_aspect2d()

        # cs = CoordinateSystem(cg)
        # cs.attach_to_render()
        # cs.setPos(Vec3(0., 0., 0.))

        # csp = CoordinateSystemP3dPlain()
        # csp.attach_to_aspect2d()
        # csp.setPos(Vec3(0., 0., 0.))

        csp2 = CoordinateSystemP3dPlain()
        csp2.attach_to_render()
        csp2.setPos(Vec3(0., 0., 0.))

        base.accept("d", lambda: exec("import ipdb; ipdb.set_trace()"))

        # oc1 = OrientedDisk(target_normal_vector=Vec3(1., 0., 1.), initial_scaling=0.5, num_of_verts=30)
        # oc1.reparentTo(engine.tq_graphics_basics.tq_render)

        # TODO: make attach_to_render use reparentTo internally!

        # oc2 = OrientedCircle(thickness=5., target_normal_vector=Vec3(0., 1., 0.), initial_scaling=0.5, num_of_verts=30)
        # oc2.reparentTo(engine.tq_graphics_basics.tq_render)

        # p_c = Point3dCursor(cg)
        # p_c.reparentTo(engine.tq_graphics_basics.tq_render)

        # self.forward_vec = Vector()
        # self.forward_vec.attach_to_render()

        # def update_forward_vector():
        #     self.forward_vec.setTailPoint(Vec3(0., 0., 0.))
        #     v_cam_forward = math_utils.p3d_to_np(engine.tq_graphics_basics.tq_render.getRelativeVector(
        #         self.cg.camera, self.cg.camera.node().getLens().getViewVector()))
        #     v_cam_forward = v_cam_forward / np.linalg.norm(v_cam_forward)

        #     self.forward_vec.setTipPoint(Vec3(*v_cam_forward))

        # cg.add_camera_move_hook(update_forward_vector)

        # dep = DraggableEdgePlayer("/home/chris/Desktop/playbacktest2.wav", cg, taskMgr)

        from plot_utils.frame2d import Frame2d, Ticks

        # x_ticks = Ticks()
        # # x_ticks.reparentTo(self)
        # x_ticks.attach_to_render()

        from simple_objects.simple_objects import BasicText, BasicOriente2dText
        # bt = BasicText()
        # bt.reparentTo(engine.tq_graphics_basics.tq_render)
        # bt.setPos(Vec3(0., 0., 0.))

        # bot = BasicOriente2dText(cg, text="Basic Oriented Text")
        # # bot.reparentTo(engine.tq_graphics_basics.tq_render)
        # bot.attach_to_render()
        # # bot.setPos(Vec3(1., 0., 0.))

        # bot2 = BasicOriente2dText(cg, text="Basic Oriented Text")
        # # bot2.reparentTo(engine.tq_graphics_basics.tq_render)
        # bot2.attach_to_render()
        # bot2.setPos(Vec3(1., 1., 1.))

        f2l = Fixed2dLabel(text=str(1))
        f2l.attach_to_aspect2d()
        # f2l.setPos2d(pos_x=1., pos_y=1.)
        f2l.setPos(Vec3(0., 0., 0.))
        print(f2l.getPos())

        f2d = Frame2d(cg)
        # f2d.attach_to_aspect2d()
        f2d.attach_to_render()
        # f2d.reparentTo(engine.tq_graphics_basics.tq_render)



        # f2d.set_clipping_planes()

        x = np.linspace(-5., 5, num=50)
        y = np.sin(x)
        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
        f2d.plot(x, y, color="black", thickness=5.)

        f2d.plot(x, np.cos(x), color="red", thickness=5.)
        # f2d.setPos(0.2, 0., 0.2)

        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
        lims = f2d.get_lims_from_internal_data()
        print("f2d.get_lims_from_internal_data(): ", lims)

        # f2d.set_xlim(2., 5.)
        # f2d.set_ylim(-0.5, 0.7)

        # toggle clipping planes
        base.accept("c", lambda f2d=f2d: f2d.toggle_clipping_planes())

        # f2d.update_parametric_line(
        #     lambda x: np.array([
        #             x,
        #             np.sin(x),
        #         ])
        # )



        # model_nodepath = loader.loadModel("panda.egg")
        # print("type: ", model_nodepath)
        # model_nodepath.reparentTo(render)
        # # model_nodepath.setPos(Vec3(0., 2., 0.))
        # pscale = 0.05
        # model_nodepath.setScale(pscale)

        # model2_nodepath = loader.loadModel("panda.egg")
        # model2_nodepath.reparentTo(render)
        # model2_nodepath.setPos(Vec3(-0.1, 0., 0.))
        # pscale = 0.05
        # model2_nodepath.setScale(pscale)

        # # cpnp = NodePath('someModel')
        # clipping_plane_nodepath = model_nodepath.attachNewNode(PlaneNode('clip'))
        # clipping_plane_nodepath.node().setPlane(Plane(0,0,1,0))
        # clipping_plane_nodepath.node().setClipEffect(1)
        # model_nodepath.setClipPlane(clipping_plane_nodepath)
        # clipping_plane_nodepath.setPos(0., 0., 0.)


        # plane = LPlanef((0,0,0), (0,1,0), (0,0,1))
        # plane_node = PlaneNode('', plane)
        # plane_node.setClipEffect(1)
        # plane_nodepath = NodePath(plane_node)

        # plane_nodepath.reparentTo(model_nodepath)
        # model_nodepath.setClipPlane(plane_nodepath)
        # model_nodepath.setPos(0.1, 0., 0.)

        # # cpnp = NodePath('someModel')
        # pn = PlaneNode('clip')
        # pn.setPlane(Plane(0,0,1,0))
        # # clipping_plane_nodepath.setPos(0., 0., 0.)
        # model_nodepath.setClipPlane(pn)



        # cg.set_view_to_xy_plane()
        cg.set_view_to_xz_plane()


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
