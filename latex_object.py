import conventions

import custom_geometry
import texture_utils

from latex_expression_manager import LatexImageManager, LatexImage

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Vec4,
    TransparencyAttrib)
from direct.interval.IntervalGlobal import Wait, Sequence
from direct.interval.LerpInterval import LerpFunc

import hashlib


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
        self.nodePath.setRenderModeWireframe()

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
    scale_z = .02
    scale_x = 1.

    def __init__(self):
        Box2d.__init__(self)

        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        self.nodePath.setScale(self.scale_x, 1., self.scale_z)


class ArrowHead(Box2d):
    equilateral_length = Line.scale_z * 4.
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
    length = 1.

    def __init__(self):
        self.numberLine = Line()
        self.numberLine.nodePath.setPos(0., 0., -0.5 * self.numberLine.scale_z)
        # numberLine.initiateScalingMovement(s_x=.5, duration=1.)

        self.arrow = ArrowHead()
        self.arrow.nodePath.setPos(
            self.length, 0., -0.5 * self.arrow.equilateral_length)
        # self.arrow.initiateTranslationMovement(v_x=self.length, duration=1., delay=0.)
