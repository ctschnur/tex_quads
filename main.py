from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain
from simple_objects.simple_objects import Line2dObject, Point, ArrowHead, Line1dObject, LineDashed1dObject, ArrowHeadCone, ArrowHeadConeShaded
from simple_objects import primitives
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
        plot_xy_z(x, y, lambda x, y: x**3. + y**3.)

        # -- Plot a bloch sphere
        from simple_objects.primitives import ParametricLinePrimitive

        plp1 = ParametricLinePrimitive(
            lambda t: np.array([
                0,
                np.cos(t*(2.*np.pi)*1.),
                np.sin(t*(2.*np.pi)*1.)
            ]), howmany_points=1000)

        from simple_objects.primitives import ParametricDashedLinePrimitive

        plp2 = ParametricDashedLinePrimitive(lambda t: np.array([
            np.sin(t*(2.*np.pi)*1.),
            np.cos(t*(2.*np.pi)*1.),
            0
        ]), howmany_points=1000)

        # plot a bezier curve in the yz plane
        import scipy.special

        def BezierCurve(t, P_arr):
            _sum = 0
            n = len(P_arr) - 1

            assert len(P_arr) >= 2  # at least a linear bezier curve
            assert t >= 0. and t <= 1.

            for i, P_i in enumerate(P_arr):
                _sum += (scipy.special.comb(n, i)
                         * (1. - t)**(n - np.float(i))
                         * t**np.float(i)
                         * P_i)
            return _sum

        bez_points = np.array([[0., 0., 0.],
                               [0., 1., 1.],  # ,
                               [0., 0, 1.],
                               [1., 1., 1.]
                               ])

        beziercurve = ParametricLinePrimitive(
            lambda t:
            np.array([
                BezierCurve(t, bez_points)[0],
                BezierCurve(t, bez_points)[1],
                BezierCurve(t, bez_points)[2]
            ]),
            param_interv=np.array([0, 1]),
            thickness=5,
            color=Vec4(1., 1., 0., 1.))

        # v1 = Vector()
        # v1.groupNode.nodePath.setColor(1, 0, 0, 1)

        # v2 = Vector()
        # v2.groupNode.nodePath.setColor(0, 1, 0, 1)

        # g = GroupNode()
        # g.addChildNodePaths([v1.groupNode.nodePath])

        # def heymyfunc(t, vec, g, twirlingvec):
        #     r = 1.
        #     x = r * np.cos(t)
        #     z = r * np.sin(t)
        #     x_fast = r * np.cos(t*2)
        #     z_fast = r * np.sin(t*2)
        #     vec.setVectorTipPoint(Vec3(-x, 0, -z)*0.5)
        #     twirlingvec.setVectorTipPoint(Vec3(x_fast, 0, z_fast)*0.2)

        #     g.nodePath.setMat(math_utils.getTranslationMatrix3d_forrowvecs(x, 0, z))
        #     twirlingvec.groupNode.nodePath.setMat(math_utils.getTranslationMatrix3d_forrowvecs(x, 0, z))

        # t_0 = 0.
        # t_f = 2*3.1415

        # seq = Sequence(
        #     Parallel(
        #         LerpFunc(
        #             heymyfunc,
        #             fromData=0,
        #             toData=t_f,
        #             duration=1,
        #             extraArgs=[v1, g, v2]
        #         )
        #     )
        # ).loop(playRate=0.2)

        # import cmath

        # def R_x(omega, t):
        #     """ rotation around the x-axis """
        #     return np.exp(-1j)

        # v3 =

        def findChildrenAndSetRenderModeRecursively(parentnode):
            children = parentnode.get_children()
            for child in children:
                findChildrenAndSetRenderModeRecursively(child)
                child.setRenderModeFilled()

        findChildrenAndSetRenderModeRecursively(render)


app = MyApp()
app.run()
