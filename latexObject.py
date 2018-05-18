from bunchOfImports import *

from latexDisplayConventions import *

import customGeometry
import textureUtils

class LatexObject: 

    def __init__(self, tex_expression, renderit=True):
        self.tex_expression = tex_expression
        self.renderit = renderit
        self.customTransform = Mat4(1., 0., 0., 0., 
                                    0., 1., 0., 0., 
                                    0., 0., 1., 0., 
                                    0., 0., 0., 1.)
        self.makeNewLatexObject()
        
        self.translate()

    def translate(self, v_x=0., v_y=0., v_z=0.):
        self.customTransform = (Mat4.translateMat(v_x, v_y, v_z) * 
                                self.customTransform)
        self._apply_net_trafo_to_nodepath()

    def _apply_net_trafo_to_nodepath(self):
        self.quad_nodepath.setMat(self.customTransform * self.standardTransform)

    def makeNewGeometry(self):
        # procedurally create a Geom() (here: a textured quad made up of 2
        # triangles) and make a GeomNode() from it
        self.quad_node = customGeometry.createTexturedUnitQuadGeomNode()

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

    def makeNewLatexObject(self, renderit=True):
        
        self.makeNewGeometry()

        # the concept of a NodePath() only makes sense only the node is attached 
        # to a scenegraph, so do it:
        self.quad_nodepath = render.attachNewNode(self.quad_node)

        # if you don't want to render it, hide it, after attachNewNode, you
        # don't need to manually show() it
        if renderit is False:
            self.hide()

        self.getImageAndApplyTexture()

        # Whatever is your texture, it now has been applied to a unit square.
        # If all you want to do is show an image, it is probably stretched/squished
        # to fit in the unit square
        # There are two solutions to this problem: 
        # 1. You can scale the unit square by applying a custom model matrix
        #    onto your unit square geometry. p3d provides utility functions for
        #    that (e.g. nodepath.setSx/y/z(float)), but I prefer to construct 
        #    my own matrix and then give it to p3d
        # 2. You could apply a transform on your texture's (u,v) coordinates
        #    that can result in the same output as in (1.). And you would have
        #    to dig through the p3d manual and reference yourself, 
        #    because I'm using (1.)

        self.standardTransform = getMat4_scaleUnitQuadProperly(self.myPNMImage.getXSize(), self.myPNMImage.getYSize())

        self._apply_net_trafo_to_nodepath()

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
