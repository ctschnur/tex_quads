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
        render.setAntialias(AntialiasAttrib.MAuto)

        # render.set_two_sided(True)
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

        plot_xy_z(x, y, lambda x, y: x**3. + y**3.)

        plot_xy_z(x, y, lambda x, y: x + y)

        plot_xy_z(x, y, lambda x, y: 0)

        # Scatter([0.6], [0], z=[0.])
        # Scatter([0], [0.6], z=[0.])
        Scatter([0], [0], z=[0.6])

        import ctsutils.euler_angles as cse
        from ctsutils.euler_angles import get_R_x, get_R_y, get_R_z
        import numpy as np

        theta = 0.3

        alpha_beta_gammas = [
            tuple(np.array([3.*np.pi/2.-theta, np.pi/2., np.pi/2.])),
            tuple(np.array([np.pi/2.-theta, np.pi/2., 0.])),
            tuple(np.array([np.pi/2.-theta, 0., 0.])),
            tuple(np.array([3*np.pi/2., -np.pi/2, np.pi/2])/3.)]

        zxz_total = cse.get_zxz_rot(*alpha_beta_gammas[3])

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

        # from simple_objects.custom_geometry import create_GeomNode_Cone, createColoredUnitCircle

        from simple_objects.simple_objects import Pinned2dLabel

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
            children = parentnode.get_children()
            for child in children:
                findChildrenAndSetRenderModeRecursively(child)
                child.setRenderModeFilled()

        findChildrenAndSetRenderModeRecursively(render)

        # base.cam.setPos(5, 5, 2.5)  # this manipulates the viewing matrix
        # base.cam.lookAt(Vec3(0,0,0))  # this manipulates the viewing matrix


app = MyApp()
app.run()
