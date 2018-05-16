from bunchOfImports import *
from customGeometry import *
from textureUtils import *
from cameraUtils import *
from latexDisplayConventions import *

class MyApp(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)

        # make self-defined camera control possible
        self.disableMouse()  

        setupOrthographicProjectionAndViewingAccordingToMyConvention()

        # procedurally create a Geom() (here: a textured quad made up of 2
        # triangles) and make a GeomNode() from it
        quad_node = createTexturedUnitQuadGeomNode()

        # the concept of a NodePath() only makes sense only the node is attached 
        # to a scenegraph, so do it:
        quad_nodepath = render.attachNewNode(quad_node)

        # PNMImage() is p3d's own image loading and handling utility class
        myPNMImage = getImageFromFile()
        # Texture() is p3d's own texture class that interacts well with the
        # PNMImage() class
        myTexture = getTextureFromImage(myPNMImage)

        # assign the Texture() to the NodePath() that contains the Geom()
        # only on the nodepath you can assign textures with setTexture()
        # priority 1 could also be 0 here, since nothing is inherited
        quad_nodepath.setTexture(myTexture, 1)
        quad_nodepath.setTransparency(TransparencyAttrib.MAlpha)

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

        quad_nodepath.setMat(getMat4_LatexQuadTrafo(myPNMImage.getXSize(), myPNMImage.getYSize()))

app = MyApp()
app.run()
