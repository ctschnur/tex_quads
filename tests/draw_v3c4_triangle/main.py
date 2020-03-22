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

        # Define own Geometry

        # Format of the Data to render: GeomVertexFormat
        format = GeomVertexFormat.getV3c4()
        format = GeomVertexFormat.registerFormat(format)

        # Data to render: GeomVertexData
        vdata = GeomVertexData('name', format, Geom.UHStatic)

        vertex = GeomVertexWriter(vdata, 'vertex')
        color = GeomVertexWriter(vdata, 'color')

        vertex.addData3f(1, 0, 0)
        vertex.addData3f(1, 0, 1)
        vertex.addData3f(0, 0, 1)
        
        color.addData4f(1, 0, 0, 1)
        color.addData4f(1, 0, 1, 1)
        color.addData4f(0, 0, 1, 1)

        # indexing to form Primitives
        prim = GeomTriangles(Geom.UHStatic) 
        prim.addVertex(0)
        prim.addVertex(1)
        prim.addVertex(2)
        prim.closePrimitive()

        # Now attach it to the scene graph to render
        geom = Geom(vdata)
        geom.addPrimitive(prim)

        node = GeomNode('gnode')
        node.addGeom(geom)

        nodePath = render.attachNewNode(node)


app = MyApp()
app.run()
