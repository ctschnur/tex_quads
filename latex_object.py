import conventions

import custom_geometry
import texture_utils

from latex_expression_manager import LatexImageManager, LatexImage

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Vec3, 
    Vec4,
    TransparencyAttrib, 
    AntialiasAttrib,
    NodePath)
from direct.interval.IntervalGlobal import Wait, Sequence
from direct.interval.LerpInterval import LerpFunc

import hashlib
import numpy as np


class Animator:
    # interval/sequence initiate functions
    def initiateTranslationMovement(self, v_x=0., v_z=0., duration=0., delay=0.):
        extraArgs = [duration, v_x, v_z]
        self.p3d_interval = LerpFunc(
            self.updatePosition, duration=duration, extraArgs=extraArgs)
        Sequence(Wait(delay), self.p3d_interval).start()

    def initiateRotationMovement(self, h=0., p=0., r=0., duration=0., delay=0.):
        extraArgs = [duration, h, p, r]
        self.p3d_interval = LerpFunc(
            self.updateRotation, duration=duration, extraArgs=extraArgs)
        Sequence(Wait(delay), self.p3d_interval).start()

    # def initiateScalingMovement(self, s_x=0., s_z=0., duration=0., delay=0.):
    #     extraArgs = [duration, s_x, s_z]
    #     self.p3d_interval = LerpFunc(
    #         self.updatePosition, duration=duration, extraArgs=extraArgs)
    #     Sequence(Wait(delay), self.p3d_interval).start()

    # interval update functions
    def updatePosition(self, t, duration, v_x, v_z):
        self.nodePath.setPos(v_x * (t / duration), 1., v_z * (t / duration))

    def updateRotation(self, t, duration, h, p, r):
        self.nodePath.setHpr(h * (t / duration), p *
                             (t / duration), r * (t / duration))

    # def updateScaling(self, t, duration, s_x, s_z):
    #     self.nodePath.setPos(s_x*(t/duration), 1., s_z*(t/duration))


class Polygon2d(Animator):
    def __init__(self, point_cloud):
        Animator.__init__(self)

        self.makeObject(point_cloud)

    def makeObject(self, point_cloud):
        self.node = custom_geometry.create_colored_polygon2d_GeomNode_from_point_cloud(
            point_cloud, 
            color_vec4=Vec4(1., 1., 1., 1.))
        self.nodePath = render.attachNewNode(self.node)

class Polygon2dTestTriangles(Animator):
    def __init__(self, symbol_geometries):
        Animator.__init__(self)

        self.makeObject(symbol_geometries)

    def makeObject(self, symbol_geometries):
        self.node = custom_geometry.create_GeomNode_Simple_Polygon_with_Hole(symbol_geometries)
        # self.node = custom_geometry.create_GeomNode_Simple_Polygon_without_Hole(symbol_geometries)

        self.nodePath = render.attachNewNode(self.node)
        
        # self.nodePath.setRenderModeWireframe()

class Polygon2dTestLineStrips(Animator):
    def __init__(self, symbol_geometries):
        Animator.__init__(self)

        self.makeObject(symbol_geometries)

    def makeObject(self, symbol_geometries):
        self.node = custom_geometry.create_GeomNode_Simple_Polygon_with_Hole_LineStrips(symbol_geometries)

        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setRenderModeWireframe()

class Box2d(Animator):

    def __init__(self):
        Animator.__init__(self)

        self.makeObject()

    def makeObject(self):
        self.node = custom_geometry.createColoredUnitQuadGeomNode(
            color_vec4=Vec4(1., 1., 1., 1.))
        self.nodePath = render.attachNewNode(self.node)


class LatexTextureObject(Box2d):
    def __init__(self, tex_expression):
        Animator.__init__(self)

        self.tex_expression = tex_expression

        self.makeObject()

        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        """ initial setup transformation: a unit quad with an image in the
        background is being scaled so that the pixel height and width fits
        exactly with the screen resolution"""

        self.nodePath.setMat(
            conventions.getMat4_scale_quad_for_texture_pixels_to_match_screen_resolution() *
            conventions.getMat4_scale_unit_quad_to_image_aspect_ratio(self.myPNMImage.getXSize(), self.myPNMImage.getYSize()))

    def makeObject(self):
        """ only creates geometry (doesn't transform it) """
        self.node = custom_geometry.createTexturedUnitQuadGeomNode()
        self.nodePath = render.attachNewNode(self.node)

        def applyImageAndTexture():
            """assign the Texture() to the NodePath() that contains the Geom()
            load image with the object's hash"""
            expr_hash = hashlib.sha256(
                str(self.tex_expression).encode("utf-8")).hexdigest()

            myLatexImage = LatexImageManager.retrieveLatexImageFromHash(
                expr_hash)
            if myLatexImage is None:
                myLatexImage = LatexImage(expression_str=self.tex_expression)
                myLatexImage.compileToPNG()
                LatexImageManager.addLatexImageToCompiledSet(myLatexImage)
                LatexImageManager.addLatexImageToLoadedSet(myLatexImage)

            self.myPNMImage = myLatexImage.getPNMImage()
            self.myTexture = texture_utils.getTextureFromImage(self.myPNMImage)
            self.nodePath.setTexture(self.myTexture, 1)
            self.nodePath.setTransparency(TransparencyAttrib.MAlpha)

        applyImageAndTexture()


class Line(Box2d):
    width = 0.05

    def __init__(self):
        Box2d.__init__(self)
        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        self.nodePath.setScale(1., 1., self.width)
        # self.nodePath.setPos(self.nodePath, 0, 0, - 1. * 0.5)  # first, translate the box of dimensions 1x1
        self.nodePath.setPos(0, 0, - self.width * 0.5)  # then, translate it half of it's intended with up

    # def setTipPoint(self, tip_point):
    #     # since the template is already normalized in world coordinates,
    #     # I only need to scale it in the x direction and then rotate it so
    #     # it points to the intended coordinate
    #     self.tip_point = tip_point
    #     # scale it
    #     self.nodePath.setScale(self.nodePath, np.sqrt(tip_point.getX()**2. + tip_point.getY()**2. + tip_point.getZ()**2.))
    #     # angle between (1, 0, 0)^T and tip_point
    #     xhat = Vec3(1., 0., 0.)
    #     print("the angle between ",
    #           tip_point.getX(), tip_point.getY(), tip_point.getZ(),
    #           " and ",
    #           xhat.getX(), xhat.getY(), xhat.getZ(),
    #           " is ",
    #           xhat.angleDeg(tip_point))
    #           
    #     self.nodePath.setHpr(0., 0., tip_point.angleDeg(xhat))

class Point(Box2d):
    scale_z = .05
    scale_x = .05

    def __init__(self):
        Box2d.__init__(self)
        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        self.nodePath.setScale(self.scale_x, 1., self.scale_z)

    # def setTailPoint(self, tail_point):
    #     self.tail_point = tail_point
    #     self.nodePath.setPos(self.tail_point)

    def setTipPoint(self, tip_point):
        # since the template is already normalized in world coordinates,
        # I only need to scale it in the x direction and then rotate it so
        # it points to the intended coordinate
        self.tip_point = tip_point
        # scale it
        self.nodePath.setScale(self.nodePath, np.sqrt(tip_point.getX()**2. + tip_point.getY()**2. + tip_point.getZ()**2.))
        # angle between (1, 0, 0)^T and tip_point
        xhat = Vec3(1., 0., 0.)
        print("the angle between ",
              tip_point.getX(), tip_point.getY(), tip_point.getZ(),
              " and ",
              xhat.getX(), xhat.getY(), xhat.getZ(),
              " is ",
              xhat.angleDeg(tip_point))
              
        self.nodePath.setHpr(0., 0., tip_point.angleDeg(xhat))

class ParallelLines:
    """ Draw Parallel Lines

    """
    def __init__(self):
        self.spacing = .25
        self.number_of_lines = 15

        # self.numoflines = int(self.length_in_segments - 1)


        # transform the lines
        # - stretch the unit length lines to the specified size
        # - position them in order, evenly spaced

        self.lines = [Line() for i in range(self.number_of_lines)]
        for idx, line in enumerate(self.lines): 
            line.nodePath.setScale(line.nodePath, 1., 1., 1.)
            line.nodePath.setPos(0., 0, idx * self.spacing)


class ArrowHead(Box2d):
    equilateral_length = Line.width * 4.
    scale = .1

    def __init__(self):
        Box2d.__init__(self)

        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        self.nodePath.setScale(self.scale, self.scale, self.scale)

    def makeObject(self):
        """it's not just a scaled quad, so it needs different Geometry"""
        self.node = custom_geometry.createColoredArrowGeomNode(
            color_vec4=Vec4(1., 1., 1., 1.))
        self.nodePath = render.attachNewNode(self.node)


class Axis:
    def __init__(self):
        self.numberLine = Line()
        # self.arrow = ArrowHead()
        # self.arrow.nodePath.setPos(
        #     self.length, 0., -0.5 * self.arrow.equilateral_length)

class YAxis(Axis):
    """ YAxis, basically a rotated XAxis

    """
    def __init__(self):
        super(YAxis, self).__init__()
        # x(right), y(into screen), z(up)
        # self.numberLine.nodePath.setPos(0.0, 0.0, 0.0)
        # around z, around x', around y''
        self.numberLine.nodePath.setHpr(0.0, 0.0, -90.0)

class GroupNode(Animator):
    """Documentation for GroupNode

    """
    def __init__(self):
        super(GroupNode, self).__init__()
        self.nodePath = NodePath("empty")
        self.nodePath.reparentTo(render)

    def addChildNodePaths(self, NodePaths):
        for np in NodePaths:
            np.reparentTo(self.nodePath)
        
