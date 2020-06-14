from conventions import conventions

from simple_objects import custom_geometry
from local_utils import texture_utils
from simple_objects.animator import Animator

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

class Box2d(Animator):

    def __init__(self):
        Animator.__init__(self)

        self.makeObject()

    def makeObject(self):
        self.node = custom_geometry.createColoredUnitQuadGeomNode(
            color_vec4=Vec4(1., 1., 1., 1.))
        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setTwoSided(True)  # enable backface-culling for all Animators


class Box2dCentered(Box2d):

    def __init__(self):
        super(Box2dCentered, self).__init__()

    def makeObject(self):
        self.node = custom_geometry.createColoredUnitQuadGeomNode(
            color_vec4=Vec4(1., 1., 1., 1.), center_it=True)
        self.nodePath = render.attachNewNode(self.node)


# ------ make a line instead of a box (what in OpenGL is called a GL_LINE)

class LinePrimitive(Animator):

    def __init__(self, thickness=1., color=Vec4(1.,1.,1.,1.)):
        Animator.__init__(self)
        self.thickness = thickness
        self.color = color
        self.makeObject(thickness, color)

    def makeObject(self, thickness, color):
        self.node = custom_geometry.createColoredUnitLineGeomNode(thickness=thickness, color_vec4=self.color)
        self.nodePath = render.attachNewNode(self.node)
        # self.nodePath.setTwoSided(True)  # no need for backface culling in the case of a GL_LINE

class LineDashedPrimitive(Animator):

    def __init__(self, thickness=1., color=Vec4(1.,1.,1.,1.), howmany_periods=5.):
        Animator.__init__(self)
        self.thickness = thickness
        self.color = color
        self.howmany_periods = howmany_periods
        self.makeObject(thickness, color, howmany_periods)

    def makeObject(self, thickness, color, howmany_periods):
        self.node = custom_geometry.createColoredUnitDashedLineGeomNode(
            thickness=thickness, color_vec4=self.color, howmany_periods=5.)
        self.nodePath = render.attachNewNode(self.node)



# class LinePrimitiveCentered(LinePrimitive):

#     def __init__(self):
#         super(LinePrimitiveCentered, self).__init__()

#     def makeObject(self):
#         self.node = custom_geometry.createColoredUnitQuadGeomNode(
#             color_vec4=Vec4(1., 1., 1., 1.), center_it=True)
#         self.nodePath = render.attachNewNode(self.node)
