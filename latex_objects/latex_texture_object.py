from simple_objects import custom_geometry
from simple_objects.box import Box2d
from local_utils import texture_utils
from latex_objects.latex_expression_manager import LatexImageManager, LatexImage
from conventions import conventions
from simple_objects.animator import Animator

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
