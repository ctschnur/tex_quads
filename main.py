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

class Orbiter:
    def __init__(self):
        base.disableMouse()
        self.orbit_center = Vec3(0., 0., 0.)
        self.r = 2.
        self.phi = 0.
        self.theta = np.pi/3.

        self.set_camera_pos_spherical_coords()

        from panda3d.core import ModifierButtons
        base.mouseWatcherNode.setModifierButtons(ModifierButtons())

        from direct.showbase.ShowBase import DirectObject
        # event handling

        # changing phi
        myDirectObject = DirectObject.DirectObject()
        myDirectObject.accept('wheel_down', self.handle_wheel_down)

        myDirectObject = DirectObject.DirectObject()
        myDirectObject.accept('wheel_up', self.handle_wheel_up)

        # changing theta
        myDirectObject = DirectObject.DirectObject()
        myDirectObject.accept('control-wheel_down', self.handle_control_wheel_down)

        myDirectObject = DirectObject.DirectObject()
        myDirectObject.accept('control-wheel_up', self.handle_control_wheel_up)

    def set_camera_pos_spherical_coords(self):
        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
        print("theta = ", self.theta, ", " "phi = ", self.phi)

        # prevent over-the-top flipping
        # self.theta = self.theta % np.pi
        if self.theta > np.pi:
            self.theta = np.pi - 0.0001
        if self.theta < 0.:
            self.theta = 0. + 0.0001

        # # keep phi in the range [0, 2*pi]
        if self.phi < 0. or self.phi > 2.*np.pi:
            self.phi = self.phi % 2.*np.pi

        if self.phi < 0.:
            self.phi = self.phi + 2.*np.pi
        elif self.phi > 2.*np.pi:
            self.phi = self.phi - 2.*np.pi

        x = self.orbit_center[0] + self.r * np.sin(self.theta) * np.cos(self.phi)
        y = self.orbit_center[1] + self.r * np.sin(self.theta) * np.sin(self.phi)
        z = self.orbit_center[2] + self.r * np.cos(self.theta)

        base.cam.setPos(x, y, z)
        base.cam.lookAt(self.orbit_center)

    def handle_wheel_up(self):
        self.phi = self.phi + 0.1
        self.set_camera_pos_spherical_coords()

    def handle_wheel_down(self):
        self.phi = self.phi - 0.1
        self.set_camera_pos_spherical_coords()

        # from pandac.PandaModules import KeyboardButton
        # upArrowIsPressed = base.mouseWatcherNode.isButtonDown(KeyboardButton.up())
        # wIsPressed = base.mouseWatcherNode.isButtonDown(KeyboardButton.asciiKey("w"))

        # print("wIsPressed: ", wIsPressed)

    def handle_control_wheel_down(self):
        self.theta = self.theta - 0.1
        self.set_camera_pos_spherical_coords()

    def handle_control_wheel_up(self):
        self.theta = self.theta + 0.1
        self.set_camera_pos_spherical_coords()


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
