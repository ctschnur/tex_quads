from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Pollygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain
from simple_objects.simple_objects import Line2dObject, Point, ArrowHead, Line1dObject, LineDashed1dObject, ArrowHeadCone, ArrowHeadConeShaded
# , ArrowHeadCone
from simple_objects import box
from local_utils import math_utils

import numpy as np

from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

import local_tests.svgpathtodat.main

import os
import sys
import pytest
import gltf

from cameras.Orbiter import Orbiter

from direct.task import Task


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.setFrameRateMeter(True)
        render.setAntialias(AntialiasAttrib.MAuto)

        ob = Orbiter(radius=3.)
        cs = CoordinateSystem(ob)

        # -- plot surface using points
        from plot_utils.pointcloud.pointcloud import plot_xy_z
        x = np.linspace(0., 1., num=20, endpoint=True)
        y = np.linspace(0., 1., num=20, endpoint=True)
        # plot_xy_z(x, y, lambda x, y: x**3. + y**3.)

        # plot_xy_z(x, y, lambda x, y: 0)

        # from simple_objects.box import ParametricLinePrimitive
        # plp = ParametricLinePrimitive(lambda t: np.array([np.sin(t*(2.*np.pi)*2.),
        #                                                   np.cos(t*(2.*np.pi)*2.),
        #                                                   t]))

        # -- Plot a bloch sphere
        from simple_objects.box import ParametricLinePrimitive
        plp = ParametricLinePrimitive(lambda t: np.array([np.sin(t*(2.*np.pi)*1.),
                                                          np.cos(
                                                              t*(2.*np.pi)*1.),
                                                          0]))
        plp2 = ParametricLinePrimitive(lambda t: np.array([0,
                                                           np.sin(
                                                               t*(2.*np.pi)*1.),
                                                           np.cos(t*(2.*np.pi)*1.)]))

        # plp2 = ParametricLinePrimitive(lambda t: np.array([
        #             np.sin(t*(2.*np.pi)*1.),
        #             0,
        #             np.cos(t*(2.*np.pi)*1.)]))

        from simple_objects.custom_geometry import createColoredParametricDashedCurveGeomNode

        gn = createColoredParametricDashedCurveGeomNode(
                func=(lambda t: np.array([t, t, t])),
                param_interv=np.array([0, 1]),
                thickness=5.,
                color=Vec4(1., 1., 1., 1.),
                howmany_points=50,
                howmany_periods=50)

        nodePath = render.attachNewNode(gn)
        nodePath.setLightOff(1)

        def findChildrenAndSetRenderModeRecursively(parentnode):
            children = parentnode.get_children()
            for child in children:
                findChildrenAndSetRenderModeRecursively(child)
                child.setRenderModeFilled()

        findChildrenAndSetRenderModeRecursively(render)


app = MyApp()
app.run()
