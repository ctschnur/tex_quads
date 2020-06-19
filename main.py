from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Pollygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain
from simple_objects.simple_objects import Line2dObject, Point, ArrowHead, Line1dObject, LineDashed1dObject, ArrowHeadCone
# , ArrowHeadCone
from simple_objects import box
from local_utils import math_utils

import numpy as np

from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

import local_tests.svgpathtodat.main

import os, sys
import pytest
import gltf

from cameras.Orbiter import Orbiter

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.setFrameRateMeter(True)

        # make self-defined camera control possible
        # base.disableMouse()
        render.setAntialias(AntialiasAttrib.MAuto)

        # render.set_two_sided(True)
        conventions.setupOrthographicProjectionAndViewingAccordingToMyConvention()

        ob = Orbiter()

        cs = CoordinateSystem()

        scat = Scatter([1, 2], [1, 2])

        import ctsutils.euler_angles as cse
        from ctsutils.euler_angles import get_R_x, get_R_y, get_R_z
        import numpy as np

        theta = 0.3

        alpha_beta_gammas = [
            tuple(np.array([3.*np.pi/2.-theta, np.pi/2., np.pi/2.])),
            tuple(np.array([np.pi/2.-theta, np.pi/2., 0.])),
            tuple(np.array([np.pi/2.-theta, 0., 0.]))]

        zxz_total = cse.get_zxz_rot(*alpha_beta_gammas[2])

        x_c_hat = np.matmul(
            zxz_total,
            np.transpose(np.array([1., 0., 0.])))

        y_c_hat = np.matmul(
            zxz_total,
            np.transpose(np.array([0., 1., 0.])))

        z_c_hat = np.matmul(
            zxz_total,
            np.transpose(np.array([0., 0., 1.])))

        v1 = Vector(tip_point=Vec3(*tuple(x_c_hat)),
                    thickness1dline=10.,
                    color=Vec4(1.,0.,0,0.25),
                    linestyle="--")

        v2 = Vector(tip_point=Vec3(*tuple(y_c_hat)),
                    thickness1dline=10.,
                    color=Vec4(0.,1.,0,0.25),
                    linestyle="--")

        v3 = Vector(tip_point=Vec3(*tuple(z_c_hat)),
                    thickness1dline=10.,
                    color=Vec4(0.,0.,1.,0.25),
                    linestyle="--")

        print("// cut ")
        print("triple x_c_hat=" + str(tuple(np.round(x_c_hat, 3))) + ";")
        print("triple y_c_hat=" + str(tuple(np.round(y_c_hat, 3))) + ";")
        print("triple z_c_hat=" + str(tuple(np.round(z_c_hat, 3))) + ";")

        from simple_objects.custom_geometry import create_GeomNode_Cone, createColoredUnitCircle

        def findChildrenAndSetRenderModeRecursively(parentnode):
            children = parentnode.get_children()
            for child in children:
                findChildrenAndSetRenderModeRecursively(child)
                child.setRenderModeFilled()

        findChildrenAndSetRenderModeRecursively(render)

        # base.cam.setPos(5, 5, 2.5)  # this manipulates the viewing matrix
        # base.cam.lookAt(Vec3(0,0,0))  # this manipulates the viewing matrix


app = MyApp()
app.run()
