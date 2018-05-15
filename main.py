from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase

from panda3d.core import GeomVertexFormat
from panda3d.core import GeomVertexData
from panda3d.core import Geom
from panda3d.core import GeomVertexWriter
from panda3d.core import GeomTriangles 
from panda3d.core import GeomNode

class MyApp(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)

        self.disableMouse()
        self.camera.setPos(0, -5, 0)

        # Own Geometry

        format = GeomVertexFormat.getV3c4()
        vdata = GeomVertexData("colored_quad", format, Geom.UHStatic) 
        vdata.setNumRows(4) 

        vertexPosWriter = GeomVertexWriter(vdata, "vertex") 
        vertexPosWriter.addData3f(0,0,0) 
        vertexPosWriter.addData3f(1,0,0) 
        vertexPosWriter.addData3f(1,0,1) 
        vertexPosWriter.addData3f(0,0,1) 

        # let's also add color to each vertex
        colorWriter = GeomVertexWriter(vdata, "color") 
        colorWriter.addData4f(0,0,1,1) 
        colorWriter.addData4f(0,0,1,1) 
        colorWriter.addData4f(0,0,1,1) 
        colorWriter.addData4f(0,0,1,1) 

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
        render.attachNewNode(quadGN)

app = MyApp()
app.run()
