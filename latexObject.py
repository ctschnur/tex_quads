from bunchOfImports import *

from latexDisplayConventions import *

import customGeometry
import textureUtils

from direct.interval.IntervalGlobal import *
from direct.interval.LerpInterval import *


class Animator:   # only derivatives of this class should be called
    def __init__(self):
        self.renderit = True
        self.customTransform = Mat4()
        self.net_trafo_at_t0_mat4 = Mat4()
        self.standardTransform = Mat4()  # each subclass has a specific transform (Line, LatexObject, ...)

    def initiateTranslationMovement(self, v_x=0., v_z=0., delta_t=0., delay=0.): 
        extraArgs = [ 
                v_x,
                v_z,
                delta_t
            ]
        self.interval = LerpFunc(self.translate_update_matrix, duration=1.0, blendType="easeInOut", extraArgs=extraArgs) 
        Sequence(Wait(delay), self.interval).start()

    def translate_update_matrix(self, t, v_x, v_z, delta_t):
        self.customTransform = (Mat4.translateMat(v_x*(t/delta_t), 0., v_z*(t/delta_t)) * 
                                self.net_trafo_at_t0_mat4)
        self._apply_net_trafo_to_nodepath()

    def _apply_net_trafo_to_nodepath(self):
        self.quad_nodepath.setMat(self.customTransform * self.standardTransform)

    def render(self): 
        # after each detaching from the scenegraph, if you want to attach the
        # node again, you have to redo all the things that can only be operated on a
        # the corresponding nodepath. A nodepath that has a texture and 
        # transformation applied to it can't be detached and reattached to 
        # the render scenegraph while keeping the applied texture and 
        # transformation information 
        # That's why we only hide() the nodepath, to make it invisible to all
        # cameras and show() it if necessary
        self.renderit = True
        self.quad_nodepath.show()

    def hide(self):
        self.renderit = False
        self.quad_nodepath.hide()


class LatexObject(Animator): 
    def __init__(self, tex_expression):
        Animator.__init__(self)

        self.tex_expression = tex_expression
        self.makeObject()

    def getImageAndApplyTexture(self):
        # TODO: check if latex image is compiled and loaded, and if so retrieve it and not
        # load it anew
        # get expression hash
        expr_hash = hashlib.sha256(str(self.tex_expression).encode("utf-8")).hexdigest()
        # load image with that hash
        from latexExpressionManager import LatexImageManager, LatexImage
        myLatexImage = LatexImageManager.retrieveLatexImageFromHash(expr_hash)
        if myLatexImage is None:  # it wasn't compiled yet, so do it
            myLatexImage = LatexImage(expression_str=self.tex_expression)
            myLatexImage.compileToPNG()
            LatexImageManager.addLatexImageToCompiledSet(myLatexImage)
            LatexImageManager.addLatexImageToLoadedSet(myLatexImage)

        self.myPNMImage = myLatexImage.getPNMImage()
        
        # PNMImage() is p3d's own image loading and handling utility class
        # self.myPNMImage = textureUtils.getImageFromFile()  # default: sample.png
        # Texture() is p3d's own texture class that interacts well with the
        # PNMImage() class
        self.myTexture = textureUtils.getTextureFromImage(self.myPNMImage)

        # assign the Texture() to the NodePath() that contains the Geom()
        # only on the nodepath you can assign textures with setTexture()
        # priority 1 could also be 0 here, since nothing is inherited
        self.quad_nodepath.setTexture(self.myTexture, 1)
        self.quad_nodepath.setTransparency(TransparencyAttrib.MAlpha)

    def makeObject(self):
        
        self.quad_node = customGeometry.createTexturedUnitQuadGeomNode()
        # the concept of a NodePath() only makes sense only the node is attached 
        # to a scenegraph, so do it:
        self.quad_nodepath = render.attachNewNode(self.quad_node)
        # specifically for this type of data:
        self.getImageAndApplyTexture()

        # Whatever is your texture, it now has been applied to a unit square.
        # If all you want to do is show an image, it is probably stretched/squished
        # into the unit square.
        # There are two solutions to this problem: 
        # 1. You can scale the unit square by applying a custom model matrix
        #    onto your unit square geometry. p3d provides utility functions for
        #    that (e.g. nodepath.setSx/y/z(float)), but I prefer to construct 
        #    my own matrix and then give it to p3d
        # 2. You could apply a transform on your textures (u,v) coordinates

        self.standardTransform = LatexObject.getMat4_scaleUnitQuadProperly(self.myPNMImage.getXSize(), self.myPNMImage.getYSize())

        self._apply_net_trafo_to_nodepath()

    @staticmethod
    def getMat4_scaleUnitQuadProperly(image_width_pixels, image_height_pixels):
        return (
            getMat4_scale_quad_for_texture_pixels_to_match_screen_resolution() * 
            getMat4_scale_unit_quad_to_image_aspect_ratio(image_width_pixels, image_height_pixels))

class Line(Animator): 
    thickness = 0.02
    length = 1.
    position = Vec3(0., 0., 0.) 

    def __init__(self):
        Animator.__init__(self)

        self.makeObject()
 
    def makeObject(self): 
        self.quad_node = customGeometry.createColoredUnitQuadGeomNode(color_vec4=Vec4(1., 1., 1., 1.))
        # the concept of a NodePath() makes sense only if the node is attached 
        # to a scenegraph, so do it:
        self.quad_nodepath = render.attachNewNode(self.quad_node)

        self.standardTransform = Line.getMat4_scaleUnitQuadForLine(self.thickness, self.length, self.position)

        self._apply_net_trafo_to_nodepath()

    @staticmethod
    def getMat4_scaleUnitQuadForLine(thickness, length, position):
        # scale height down
        # quad_scalex = float(length)
        quad_scalez = float(thickness)
        return Mat4(1., 0, 0, 0, 
                    0, 1., 0, 0, 
                    0, 0, quad_scalez * 1., 0, 
                    0, 0, 0, 1) 


class ArrowForLine(Animator): 
    eqilateral_length = Line.thickness * 4.
    position = Vec3(0., 0., 0.) 

    def __init__(self):
        Animator.__init__(self)

        self.makeObject()
 
    def makeObject(self): 
        self.quad_node = customGeometry.createColoredArrowGeomNode(color_vec4=Vec4(1., 1., 1., 1.))
        # the concept of a NodePath() makes sense only if the node is attached 
        # to a scenegraph, so do it:
        self.quad_nodepath = render.attachNewNode(self.quad_node)

        self.standardTransform = ArrowForLine.getMat4_scaleGeometry(self.eqilateral_length, self.position)

        self._apply_net_trafo_to_nodepath()

    @staticmethod
    def getMat4_scaleGeometry(equilateral_length, position):
        # scale height down
        # quad_scalex = float(length)
        scale = float(equilateral_length)
        return Mat4(scale, 0, 0, 0, 
                    0, 1., 0, 0, 
                    0, 0, scale* 1., 0, 
                    0, 0, 0, 1) 


