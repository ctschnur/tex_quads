from bunchOfImports import *

from latexDisplayConventions import *

import customGeometry
import textureUtils

from direct.interval.IntervalGlobal import *
from direct.interval.LerpInterval import *


class Animator:   # only derivatives of this class should be called
    def __init__(self):
        self.net_custom_initial_static_trafo = Mat4()

        # when applying a transformation, this is the matrix made of 
        # previous transformations due to animations 
        # where the new one is continually applied to 
        self.net_custom_anim_trafo = Mat4()  
        self.last_custom_anim_mat4 = Mat4()

        self.net_custom_matrix = Mat4()

    def makeObject(self):
        """creates geometry and doesn't transform it"""
        self.quad_node = customGeometry.createTexturedUnitQuadGeomNode()
        self.quad_nodepath = render.attachNewNode(self.quad_node)
        self.applyImageAndTexture()

    def updateCurrentTranslationMat(self, t, duration, v_x, v_z):
        self.net_custom_anim_trafo = (
            Mat4.translateMat(v_x*(t/duration), 0., v_z*(t/duration)) * 
            self.last_custom_anim_mat4 )

        self.updateNetMatrix()

    def updateNetMatrix(self):
        self.net_custom_matrix = self.last_custom_anim_mat4 * self.net_custom_anim_trafo * self.net_custom_initial_static_trafo
        self.quad_nodepath.setMat(self.net_custom_matrix)

    # --- animations
    def initiateTranslationMovement(self, v_x=0., v_z=0., duration=0., delay=0.): 
        extraArgs = [duration, v_x, v_z]
        self.p3d_interval = LerpFunc(self.updateCurrentTranslationMat, duration=duration, extraArgs=extraArgs) 
        Sequence(Wait(delay), self.p3d_interval).start()

class LatexObject(Animator): 
    def __init__(self, tex_expression):
        Animator.__init__(self)

        self.tex_expression = tex_expression
        self.makeObject() 

        # all the initial transformations
        # TODO: this should be a setter function
        self.net_custom_initial_static_trafo = self.trafo_UnitSquad_To_ImageDisplay()

        self.updateNetMatrix()

    def trafo_UnitSquad_To_ImageDisplay(self):
        """a unit quad with an image in the background is being scaled so that
        the pixel height and width fits exactly with the screen resolution"""
        
        def getMat4_scaleUnitQuadProperly(image_width_pixels, image_height_pixels):
            return (
                getMat4_scale_quad_for_texture_pixels_to_match_screen_resolution() * 
                getMat4_scale_unit_quad_to_image_aspect_ratio(image_width_pixels, image_height_pixels))

        return getMat4_scaleUnitQuadProperly(
            self.myPNMImage.getXSize(), self.myPNMImage.getYSize())

    def makeObject(self):
        """creates geometry and doesn't transform it"""
        self.quad_node = customGeometry.createTexturedUnitQuadGeomNode()
        self.quad_nodepath = render.attachNewNode(self.quad_node)

        def applyImageAndTexture():
            """assign the Texture() to the NodePath() that contains the Geom()
            load image with the object's hash"""
            expr_hash = hashlib.sha256(str(self.tex_expression).encode("utf-8")).hexdigest()
            from latexExpressionManager import LatexImageManager, LatexImage
            myLatexImage = LatexImageManager.retrieveLatexImageFromHash(expr_hash)
            if myLatexImage is None:
                myLatexImage = LatexImage(expression_str=self.tex_expression)
                myLatexImage.compileToPNG()
                LatexImageManager.addLatexImageToCompiledSet(myLatexImage)
                LatexImageManager.addLatexImageToLoadedSet(myLatexImage)

            self.myPNMImage = myLatexImage.getPNMImage() 
            self.myTexture = textureUtils.getTextureFromImage(self.myPNMImage)
            self.quad_nodepath.setTexture(self.myTexture, 1)
            self.quad_nodepath.setTransparency(TransparencyAttrib.MAlpha)

        applyImageAndTexture()


class Line(Animator): 
    thickness = 0.02
    length = 1.

    def __init__(self):
        Animator.__init__(self)

        self.makeObject() 

        # initial static transformation
        def getMat4_scaleUnitQuadForLine(thickness, length):
            quad_scalez = float(thickness)
            return Mat4(1., 0, 0, 0, 
                        0, 1., 0, 0, 
                        0, 0, quad_scalez * 1., 0, 
                        0, 0, 0, 1) 

        # TODO: this should be a setter function
        self.net_custom_initial_static_trafo = getMat4_scaleUnitQuadForLine(self.thickness, self.length)

    def makeObject(self): 
        self.quad_node = customGeometry.createColoredUnitQuadGeomNode(color_vec4=Vec4(1., 1., 1., 1.))
        self.quad_nodepath = render.attachNewNode(self.quad_node)


class ArrowHead(Animator): 
    equilateral_length = Line.thickness * 4.

    def __init__(self):
        Animator.__init__(self)

        self.makeObject() 
        
        # initial static transformation
        def getMat4_scaleUnitQuad(thickness, length):
            scale = 0.1
            return Mat4.scaleMat(scale, 0., scale)

        # TODO: this should be a setter function
        self.net_custom_initial_static_trafo = getMat4_scaleUnitQuad(Line.thickness, Line.length)

    def makeObject(self): 
        self.quad_node = customGeometry.createColoredArrowGeomNode(color_vec4=Vec4(1., 1., 1., 1.))
        self.quad_nodepath = render.attachNewNode(self.quad_node)
