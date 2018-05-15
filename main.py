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

        # # teapot
        # self.scene = self.loader.loadModel("models/teapot")
        # self.scene.reparentTo(self.render)
        self.disableMouse()
        self.camera.setPos(0, -5, 0)

        # Own Geometry

        #in this example, we'll show how to make a square from scratch 
        #There is no "GeomQuad" class so we have to use two triangles. 

        #step 1) create GeomVertexData and add vertex information 
        format = GeomVertexFormat.getV3() 
        vdata = GeomVertexData("vertices", format, Geom.UHStatic) 
        vdata.setNumRows(4) 

        vertexWriter = GeomVertexWriter(vdata, "vertex") 
        vertexWriter.addData3f(0,0,0) 
        vertexWriter.addData3f(1,0,0) 
        vertexWriter.addData3f(1,0,1) 
        vertexWriter.addData3f(0,0,1) 

        #step 2) make primitives and assign vertices to them 
        tris=GeomTriangles(Geom.UHStatic) 

        #have to add vertices one by one since they are not in order 
        tris.addVertex(0) 
        tris.addVertex(1) 
        tris.addVertex(3) 

        #indicates that we have finished adding vertices for the first triangle. 
        tris.closePrimitive() 

        #since the coordinates are in order we can use this convenience function. 
        tris.addConsecutiveVertices(1,3) #add vertex 1, 2 and 3 
        tris.closePrimitive() 

        #step 3) make a Geom object to hold the primitives 
        squareGeom=Geom(vdata) 
        squareGeom.addPrimitive(tris) 

        #now put squareGeom in a GeomNode. You can now position your geometry in the scene graph. 
        squareGN=GeomNode("square") 
        squareGN.addGeom(squareGeom) 
        render.attachNewNode(squareGN)

app = MyApp()
app.run()
