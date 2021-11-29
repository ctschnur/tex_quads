from simple_objects import custom_geometry
from simple_objects.primitives import IndicatorPrimitive
from local_utils import texture_utils
from latex_objects.latex_expression_manager import LatexImageManager, LatexImage
from conventions import conventions
from engine.tq_graphics_basics import TQGraphicsNodePath

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
from poppler import load_from_file, PageRenderer  # python-poppler

from PIL import Image, ImageTk



SCREEN_SIZE_IN_PIXELS_X = 1920
SCREEN_SIZE_IN_PIXELS_Y = 1080

INCHES_TO_CM_FACTOR = 2.54

SCREEN_DIAMETER_IN_INCHES = 14
SCREEN_DIAMETER_IN_CM = INCHES_TO_CM_FACTOR * SCREEN_DIAMETER_IN_INCHES

alpha = np.arctan(SCREEN_SIZE_IN_PIXELS_Y/SCREEN_SIZE_IN_PIXELS_X)

SCREEN_SIZE_IN_CM_X = SCREEN_DIAMETER_IN_CM * np.cos(alpha)
SCREEN_SIZE_IN_CM_Y = SCREEN_DIAMETER_IN_CM * np.sin(alpha)

DPI = SCREEN_SIZE_IN_PIXELS_X / (SCREEN_SIZE_IN_CM_X / INCHES_TO_CM_FACTOR)

print("alpha:", alpha * 360./(2. * np.pi), "SCREEN_SIZE_IN_CM_X:", SCREEN_SIZE_IN_CM_X, "SCREEN_SIZE_IN_CM_Y:", SCREEN_SIZE_IN_CM_Y, "DPI:", DPI)

def get_page_dims_from_page_in_cm(poppler_page):
    return poppler_page.page_rect().width/72 * INCHES_TO_CM_FACTOR, poppler_page.page_rect().height/72 * INCHES_TO_CM_FACTOR

def cm_to_pixels_for_render(l_in_cm):
    return int(l_in_cm / INCHES_TO_CM_FACTOR * DPI)

class PopplerPDFRenderer:
    """ """
    def __init__(self, pdf_filepath, *args, **kwargs):
        self.pdf_filepath = pdf_filepath
        # self.pdf_filepath = "sample.pdf"

        self.pdf_document = load_from_file(self.pdf_filepath)
        self.renderer = PageRenderer()

        # pil_image.save("img1.png")

        # print("image.width: ", image.width, "image.height: ", image.height)
        # tk_image = ImageTk.PhotoImage(pil_image)

        pass

    def getPILImage(self, page=0):
        """ get a pdf page as a PNMImage """
        pdf_page = self.pdf_document.create_page(page)

        w_in_cm, h_in_cm = get_page_dims_from_page_in_cm(pdf_page)
        w_in_pixels_for_render = cm_to_pixels_for_render(w_in_cm)
        h_in_pixels_for_render = cm_to_pixels_for_render(h_in_cm)

        image = self.renderer.render_page(pdf_page, xres=DPI, yres=DPI, w=w_in_pixels_for_render, h=h_in_pixels_for_render)

        pil_image = Image.frombytes(
            "RGBA",
            (image.width, image.height),
            image.data,
            "raw",
            str(image.format),
            )

        return pil_image


class PDFPageTextureObject(IndicatorPrimitive):
    """ a poppler pdf page """
    def __init__(self, pdf_page, pdf_renderer, *args, **kwargs):
        """
        pdf_page : number starting from 0
        pdf_renderer : instance of PopplerPDFRenderer
        """

        TQGraphicsNodePath.__init__(self, **kwargs)

        self.pdf_page = pdf_page
        self.pdf_renderer = pdf_renderer

        self.makeObject()

        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        """ initial setup transformation: a unit quad with an image in the
        background is being scaled so that the pixel height and width fits
        exactly with the screen resolution"""

        self.setMat(
            conventions.getMat4_scale_quad_for_texture_pixels_to_match_screen_resolution_forrowvecs() *
            conventions.getMat4_scale_unit_quad_to_image_aspect_ratio_forrowvecs(self.myPILImage.width, self.myPILImage.height))

    def makeObject(self):
        """ only creates geometry (doesn't transform it) """
        self.set_node_p3d(custom_geometry.createTexturedUnitQuadGeomNode())
        # self.set_p3d_nodepath(self.getParent_p3d().attachNewNode_p3d(self.p3d_node))
        self.set_p3d_nodepath(self.getParent_p3d().attachNewNode(self.get_node_p3d()))

        # -- apply image and texture --
        # self.myPNMImage = myLatexImage.getPNMImage()
        # self.myTexture = texture_utils.getTextureFromImage(self.myPNMImage)

        self.myPILImage = self.pdf_renderer.getPILImage(page=self.pdf_page)

        self.myTexture, self.num_of_pixels_x, self.num_of_pixels_y = (
            texture_utils.getTextureFromPILImage(self.myPILImage, flip_over_y_axis=True)
        )

        self.setTexture(self.myTexture, 1)

        self.setTwoSided(True)
        self.setLightOff(1)
        # self.setTransparency(True)

        self.setTransparency(TransparencyAttrib.MAlpha)
