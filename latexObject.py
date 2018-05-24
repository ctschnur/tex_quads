from bunchOfImports import *

from latexDisplayConventions import *

import customGeometry
import textureUtils

from direct.interval.IntervalGlobal import *
from direct.interval.LerpInterval import *


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
        self.nodePath.setPos(v_x*(t/duration), 1., v_z*(t/duration))
    
    def updateRotation(self, t, duration, h, p, r):
        self.nodePath.setHpr(h*(t/duration), p*(t/duration), r*(t/duration))
    
    # def updateScaling(self, t, duration, s_x, s_z):
    #     self.nodePath.setPos(s_x*(t/duration), 1., s_z*(t/duration))


class Shape2d(Animator):

    def __init__(self):
        Animator.__init__(self)

        self.makeObject()

    def makeObject(self):
        self.node = customGeometry.createColoredUnitQuadGeomNode(
            color_vec4=Vec4(1., 1., 1., 1.))
        self.nodePath = render.attachNewNode(self.node)


class LatexObject(Shape2d):
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
            getMat4_scale_quad_for_texture_pixels_to_match_screen_resolution() *
            getMat4_scale_unit_quad_to_image_aspect_ratio(self.myPNMImage.getXSize(), self.myPNMImage.getYSize()))

    def makeObject(self):
        """only creates geometry (doesn't transform it)"""
        self.node = customGeometry.createTexturedUnitQuadGeomNode()
        self.nodePath = render.attachNewNode(self.node)

        def applyImageAndTexture():
            """assign the Texture() to the NodePath() that contains the Geom()
            load image with the object's hash"""
            expr_hash = hashlib.sha256(
                str(self.tex_expression).encode("utf-8")).hexdigest()
            from latexExpressionManager import LatexImageManager, LatexImage
            myLatexImage = LatexImageManager.retrieveLatexImageFromHash(
                expr_hash)
            if myLatexImage is None:
                myLatexImage = LatexImage(expression_str=self.tex_expression)
                myLatexImage.compileToPNG()
                LatexImageManager.addLatexImageToCompiledSet(myLatexImage)
                LatexImageManager.addLatexImageToLoadedSet(myLatexImage)

            self.myPNMImage = myLatexImage.getPNMImage()
            self.myTexture = textureUtils.getTextureFromImage(self.myPNMImage)
            self.nodePath.setTexture(self.myTexture, 1)
            self.nodePath.setTransparency(TransparencyAttrib.MAlpha)

        applyImageAndTexture()


class Line(Shape2d):
    scale_z = .02
    scale_x = 1.
    
    def __init__(self):
        Shape2d.__init__(self)

        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        self.nodePath.setScale(self.scale_x, 1., self.scale_z)


class ArrowHead(Shape2d):
    equilateral_length = Line.scale_z * 4.
    scale = .1

    def __init__(self):
        Shape2d.__init__(self)

        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        self.nodePath.setScale(self.scale, self.scale, self.scale)

    def makeObject(self):
        """it's not just a scaled quad, so it needs different Geometry"""
        self.node = customGeometry.createColoredArrowGeomNode(
            color_vec4=Vec4(1., 1., 1., 1.))
        self.nodePath = render.attachNewNode(self.node)


class Axis: 
    length = 1.
    def __init__(self):
        self.numberLine = Line()
        self.numberLine.nodePath.setPos(0., 0., -0.5*self.numberLine.scale_z)
        # numberLine.initiateScalingMovement(s_x=.5, duration=1.)
        
        self.arrow = ArrowHead()
        self.arrow.nodePath.setPos(self.length, 0., -0.5*self.arrow.equilateral_length)
        # self.arrow.initiateTranslationMovement(v_x=self.length, duration=1., delay=0.)
