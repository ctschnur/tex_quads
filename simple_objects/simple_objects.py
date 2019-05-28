from conventions import conventions

from simple_objects import custom_geometry

from utils import texture_utils

from simple_objects.box import Box2d, Box2dCentered

from latex_objects.latex_expression_manager import LatexImageManager, LatexImage

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Vec3,
    Vec4,
    TransparencyAttrib,
    AntialiasAttrib,
    NodePath,
    Mat4,
    Mat3)
from direct.interval.IntervalGlobal import Wait, Sequence
from direct.interval.LerpInterval import LerpFunc

import hashlib
import numpy as np

class Line(Box2dCentered):
    width = 0.05
    initial_length = 1.

    def __init__(self):
        super(Line, self).__init__()
        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        self.nodePath.setScale(1., 1., self.width)
        self.axis_spawning_preparation_trafo = self.nodePath.getMat()
        self.nodePath.setPos(0.5, 0, 0)
        self.length = self.initial_length
        # self.has_zero_length_is_circle = False
        self.initialTrafoMat = self.nodePath.getMat()
        self.nodePath.setRenderModeWireframe()
        self.setTipPoint(Vec3(1., 0., 0.))

    def setTipPoint(self, tip_point):
        self.xhat_prime = np.array([tip_point.getX(), tip_point.getY(), tip_point.getZ()])

        # rotation matrix for xhat
        xhat = np.array([1, 0, 0])
        normal = np.array([0, 1, 0])  # panda3d out of screen: yhat
        # find angle \theta (\in [-pi, pi]) between \hat{x} and \hat{x}'
        # using the arctan2 of a determinant and a dot product
        det = np.dot(normal, np.cross(xhat, self.xhat_prime))
        theta = np.arctan2(det, np.dot(xhat, self.xhat_prime))
        rotation = np.array([[np.cos(theta),  0, np.sin(theta), 0],
                            [0,               1,             0, 0],
                            [-np.sin(theta),  0, np.cos(theta), 0],
                            [0,               0,             0, 1]])
        self.rotation_forrowvecs = Mat4(*tuple(np.transpose(rotation).flatten()))

        # scaling matrix for xhat
        vx = np.linalg.norm(self.xhat_prime)  # length
        vy = 1.
        vz = 1.
        scaling = np.array([[vx,  0,  0, 0],
                            [0,  vy,  0, 0],
                            [0,   0, vz, 0],
                            [0,   0,  0, 1]])
        scaling_forrowvecs = Mat4(*tuple(np.transpose(scaling).flatten()))


        # apply the net transformation
        # first the scaling, then the rotation
        # remember, the row vector stands on the left in p3d multiplication
        # so the order is reversed
        trafo = scaling_forrowvecs * self.rotation_forrowvecs
        self.nodePath.setMat
        self.nodePath.setMat(self.initialTrafoMat * trafo)


class Point(Box2dCentered):
    scale_z = .05
    scale_x = .05

    def __init__(self):
        super(Point, self).__init__()
        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        self.nodePath.setScale(self.scale_x, 1., self.scale_z)


class ArrowHead(Box2dCentered):
    equilateral_length = Line.width * 4.
    scale = .1

    def __init__(self):
        super(ArrowHead, self).__init__()
        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        self.nodePath.setScale(self.scale, self.scale, self.scale)

    def makeObject(self):
        """it's not just a scaled quad, so it needs different Geometry"""
        self.node = custom_geometry.createColoredArrowGeomNode(
            color_vec4=Vec4(1., 1., 1., 1.), center_it=True)
        self.nodePath = render.attachNewNode(self.node)
