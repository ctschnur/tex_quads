from bunchOfImports import *

def createTexturedUnitQuadGeomNode():
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
    
    return quadGN
