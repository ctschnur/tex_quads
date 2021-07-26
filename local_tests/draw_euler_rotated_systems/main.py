from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain
from simple_objects.simple_objects import Line2dObject, PointPrimitive, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded
# , ArrowHeadCone
from simple_objects import primitives
from local_utils import math_utils

import numpy as np

from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

import local_tests.svgpathtodat.main

import os, sys
import pytest
import gltf

from cameras.Orbiter import Orbiter

from direct.task import Task

def plot_xy_z(x_set, y_set, z_func):
            points_xyz = np.empty((0, 3))  # define empty array to stack onto
            for y_ in y_set:
                for x_ in x_set:
                    points_xyz = np.append(points_xyz, np.array([[x_, y_, z_func(x_, y_)]]), axis=0)

            scat = Scatter(points_xyz[:,0], points_xyz[:,1], z=points_xyz[:,2])

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.setFrameRateMeter(True)

        # make self-defined camera control possible
        # base.disableMouse()
        engine.tq_graphics_basics.tq_render.setAntialias(AntialiasAttrib.MAuto)

        # engine.tq_graphics_basics.tq_render.set_two_sided(True)
        # conventions.setupOrthographicProjectionAndViewingAccordingToMyConvention(
        #     lookat_position=Vec3(0, 0, 0),
        #     camera_position=Vec3(5, 5, 2))

        ob = Orbiter(radius=3.)

        cs = CoordinateSystem()

        import numpy.random
        import numpy as np

        def z_f(x, y):
            return x**2. + y**2.

        # -- define the set of xy points for your (x, y) |-> z plot
        x = np.linspace(0., 1., num=20, endpoint=True)
        y = np.linspace(0., 1., num=20, endpoint=True)


        from simple_objects.text import Pinned2dLabel

        pos_rel_to_world_x = Point3(1., 0., 0.)
        myPinnedLabelx = Pinned2dLabel(refpoint3d=pos_rel_to_world_x, text="x", xshift=0.02, yshift=0.02)
        ob.add_camera_move_hook(myPinnedLabelx.update)

        pos_rel_to_world_y = Point3(0., 1., 0.)
        myPinnedLabely = Pinned2dLabel(refpoint3d=pos_rel_to_world_y, text="y", xshift=0.02, yshift=0.02)
        ob.add_camera_move_hook(myPinnedLabely.update)

        pos_rel_to_world_z = Point3(0., 0., 1.)
        myPinnedLabelz = Pinned2dLabel(refpoint3d=pos_rel_to_world_z, text="z", xshift=0.02, yshift=0.02)
        ob.add_camera_move_hook(myPinnedLabelz.update)

        def findChildrenAndSetRenderModeRecursively(parentnode):
            children = parentnode.get_children_p3d()
            for child in children:
                findChildrenAndSetRenderModeRecursively(child)
                child.setRenderModeFilled()

        findChildrenAndSetRenderModeRecursively(engine.tq_graphics_basics.tq_render)


app = MyApp()
app.run()
