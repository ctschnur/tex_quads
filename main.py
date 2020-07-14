from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain
from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle
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

from plot_utils.bezier_curve import BezierCurve, DraggableBezierCurve, SelectableBezierCurve

from panda3d.core import CollisionTraverser, CollisionHandlerQueue, CollisionRay, CollisionNode, GeomNode, BitMask32, VBase4


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.setFrameRateMeter(True)
        render.setAntialias(AntialiasAttrib.MAuto)

        ob = Orbiter(base.cam, radius=3.)
        cs = CoordinateSystem(ob)

        ob.set_view_to_yz_plane()

        # # -- plot surface using points
        # from plot_utils.pointcloud.pointcloud import plot_xy_z
        # x = np.linspace(0., 1., num=20, endpoint=True)
        # y = np.linspace(0., 1., num=20, endpoint=True)
        # plot_xy_z(x, y, lambda x, y: x**3. + y**3.)

        # pp = PointPrimitive(pos=Vec3(1., 1., 1.))

        # p3d = Point3d(pos=Vec3(1., 1., 1.))

        # dbc = DraggableBezierCurve(ob,
        #                            P_arr=np.array([[0.2, 0.2, 0.2],
        #                                            [0.2, 0.2, 1.2],
        #                                            [1.2, 1.2, 1.2],
        #                                            [1.2, 1.2, 0.2]]))

        # dbc = DraggableBezierCurve(ob,
        #                            P_arr=np.array([[0.2, 0.2, 0.2],
        #                                            [0.2, 0.2, 1.2],
        #                                            [1.2, 1.2, 1.2],
        #                                            [1.2, 1.2, 0.2]]))

        sbc = SelectableBezierCurve(ob,
                                    P_arr=np.array([[0.2, 0.2, 0.2],
                                                    [0.2, 0.2, 1.2],
                                                    [1.2, 1.2, 1.2],
                                                    [1.2, 1.2, 0.2]]))

        # oc = OrientedCircle()

        # p = PointPrimitive(pos=Vec3(*tuple(np.array([1., 1., 1.]))))

        # -- generate points, then circles


        # points, path_lengths = math_utils.getPointsAndPathLengthsAlongPolygonalChain(func=(lambda t: np.array([0, t, 2.7**t])), param_interv=np.array([0., 1.]), ed_subpath_length=0.2)

        # point_primitives = []
        # for p in points:
        #     point_primitives.append(PointPrimitive(pos=Vec3(*tuple(p))))

            # plot a circle


        # gn = create_GeomNode_Sphere()
        # np = NodePath(gn)
        # np.reparentTo(render)

        # def findChildrenAndSetRenderModeRecursively(parentnode):
        #     children = parentnode.get_children()
        #     for child in children:
        #         findChildrenAndSetRenderModeRecursively(child)
        #         child.setRenderModeFilled()

        # findChildrenAndSetRenderModeRecursively(render)


app = MyApp()
app.run()
