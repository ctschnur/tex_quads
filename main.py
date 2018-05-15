from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase

from panda3d.core import GeomVertexFormat
from panda3d.core import GeomVertexData
from panda3d.core import Geom, GeomVertexWriter 
from panda3d.core import GeomTriangles 
from panda3d.core import GeomNode 
from panda3d.core import PNMImage
from panda3d.core import Filename
from panda3d.core import Texture, TransparencyAttrib
from panda3d.core import PandaSystem

print "Panda version:", PandaSystem.getVersionString()

class MyApp(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)

        self.disableMouse()
        self.camera.setPos(0, -5, 0)

        # screen resolution
        screen_res_width = 1920
        screen_res_height = 1080

        # Own Geometry

        # format = GeomVertexFormat.getV3c4t2()
        format = GeomVertexFormat.getV3t2()
        vdata = GeomVertexData("textured_quad", format, Geom.UHStatic) 
        vdata.setNumRows(4) 

        vertexPosWriter = GeomVertexWriter(vdata, "vertex") 
        vertexPosWriter.addData3f(0,0,0) 
        vertexPosWriter.addData3f(1,0,0) 
        vertexPosWriter.addData3f(1,0,1) 
        vertexPosWriter.addData3f(0,0,1) 

        # let's also add color to each vertex
        # colorWriter = GeomVertexWriter(vdata, "color") 
        # colorWriter.addData4f(0,0,1,1) 
        # colorWriter.addData4f(0,0,1,1) 
        # colorWriter.addData4f(0,0,1,1) 
        # colorWriter.addData4f(0,0,1,1) 

        # let's add texture coordinates (u,v)
        texcoordWriter = GeomVertexWriter(vdata, "texcoord") 
        texcoordWriter.addData2f(0,0) 
        texcoordWriter.addData2f(1,0) 
        texcoordWriter.addData2f(1,1) 
        texcoordWriter.addData2f(0,1) 

        # make primitives and assign vertices to them (primitives and primitive
        # groups can be made independently from vdata, and are later assigned 
        # to vdata)
        tris = GeomTriangles(Geom.UHStatic) 

        # 1st triangle
        tris.addVertices(0, 1, 3) 
        tris.closePrimitive()  # the 1st primitive is finished

        # 2nd triangle
        tris.addVertices(1,2,3)
        tris.closePrimitive() 

        # make a Geom object to hold the primitives 
        quadGeom = Geom(vdata) 
        quadGeom.addPrimitive(tris) 

        # now put quadGeom in a GeomNode. You can now position your geometry 
        # in the scene graph. 
        quadGN = GeomNode("quad") 
        quadGN.addGeom(quadGeom) 
        # get nodepath by attaching to the scenegraph
        nodePath = render.attachNewNode(quadGN)

        def getImageFromFile(filename="sample.png"):
            image = PNMImage()
            image.read(Filename(filename))
            return image

        def getTextureFromImage(pnmImage):
            print("myImage.getNumChannels(): ", pnmImage.getNumChannels())
            print("myImage.getXSize(): ", pnmImage.getXSize())
            print("myImage.getYSize(): ", pnmImage.getYSize())
            print("myImage.hasAlpha(): ", pnmImage.hasAlpha())

            # assign the PNMImage to a Texture (load PNMImage to Texture, opposite of store)
            myTexture = Texture()
            myTexture.load(pnmImage)
            return myTexture

        myPNMImage = getImageFromFile()
        # myPNMImage.alphaFill(0)
        # for x in range(100):
        #     for y in range(100):
        #         print(x, y, myPNMImage.getAlpha(x, y))

        myTexture = getTextureFromImage(myPNMImage)
        # scale the unit square using matrix operations by the aspect ratio
        nodePath.setSx((myPNMImage.getXSize()/myPNMImage.getYSize()))

        # only on the nodepath you can assign textures with setTexture()
        nodePath.setTexture(myTexture, 1)  # priority 1 could also be 0 here, 
        # since nothing is inherited
        nodePath.setTransparency(TransparencyAttrib.MAlpha)


app = MyApp()
app.run()
