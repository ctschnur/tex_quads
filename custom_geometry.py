from panda3d.core import (
    GeomVertexFormat,
    GeomVertexData,
    Geom, GeomVertexWriter,
    GeomTriangles,
    GeomTrifans,
    GeomLinestrips,
    GeomNode, 
    Vec4)

from math import pi, cos

import numpy as np

import tripy_modified

def createTexturedUnitQuadGeomNode():
    # Own Geometry

    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3t2()
    vdata = GeomVertexData("textured_quad", format, Geom.UHStatic)
    vdata.setNumRows(4)

    vertexPosWriter = GeomVertexWriter(vdata, "vertex")
    vertexPosWriter.addData3f(0, 0, 0)
    vertexPosWriter.addData3f(1, 0, 0)
    vertexPosWriter.addData3f(1, 0, 1)
    vertexPosWriter.addData3f(0, 0, 1)

    # let's also add color to each vertex
    # colorWriter = GeomVertexWriter(vdata, "color")
    # colorWriter.addData4f(0,0,1,1)
    # colorWriter.addData4f(0,0,1,1)
    # colorWriter.addData4f(0,0,1,1)
    # colorWriter.addData4f(0,0,1,1)

    # let's add texture coordinates (u,v)
    texcoordWriter = GeomVertexWriter(vdata, "texcoord")
    texcoordWriter.addData2f(0, 0)
    texcoordWriter.addData2f(1, 0)
    texcoordWriter.addData2f(1, 1)
    texcoordWriter.addData2f(0, 1)

    # make primitives and assign vertices to them (primitives and primitive
    # groups can be made independently from vdata, and are later assigned
    # to vdata)
    tris = GeomTriangles(Geom.UHStatic)

    # 1st triangle
    tris.addVertices(0, 1, 3)
    tris.closePrimitive()  # the 1st primitive is finished

    # 2nd triangle
    tris.addVertices(1, 2, 3)
    tris.closePrimitive()

    # make a Geom object to hold the primitives
    quadGeom = Geom(vdata)
    quadGeom.addPrimitive(tris)

    # now put quadGeom in a GeomNode. You can now position your geometry
    # in the scene graph.
    quadGN = GeomNode("quad")
    quadGN.addGeom(quadGeom)

    return quadGN


def createColoredUnitQuadGeomNode(color_vec4=Vec4(0., 0., 1., 1.)):
    # Own Geometry

    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_quad", format, Geom.UHStatic)
    vdata.setNumRows(4)

    vertexPosWriter = GeomVertexWriter(vdata, "vertex")
    vertexPosWriter.addData3f(0, 0, 0)
    vertexPosWriter.addData3f(1, 0, 0)
    vertexPosWriter.addData3f(1, 0, 1)
    vertexPosWriter.addData3f(0, 0, 1)

    # let's also add color to each vertex
    colorWriter = GeomVertexWriter(vdata, "color")
    colorWriter.addData4f(color_vec4)
    colorWriter.addData4f(color_vec4)
    colorWriter.addData4f(color_vec4)
    colorWriter.addData4f(color_vec4)

    # make primitives and assign vertices to them (primitives and primitive
    # groups can be made independently from vdata, and are later assigned
    # to vdata)
    tris = GeomTriangles(Geom.UHStatic)

    # 1st triangle
    tris.addVertices(0, 1, 3)
    tris.closePrimitive()  # the 1st primitive is finished

    # 2nd triangle
    tris.addVertices(1, 2, 3)
    tris.closePrimitive()

    # make a Geom object to hold the primitives
    quadGeom = Geom(vdata)
    quadGeom.addPrimitive(tris)

    # now put quadGeom in a GeomNode. You can now position your geometry
    # in the scene graph.
    quadGN = GeomNode("colored_quad_node")
    quadGN.addGeom(quadGeom)

    return quadGN


def createColoredArrowGeomNode(color_vec4=Vec4(0., 0., 1., 1.)):
    # Own Geometry

    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_quad", format, Geom.UHStatic)
    vdata.setNumRows(4)

    vertexPosWriter = GeomVertexWriter(vdata, "vertex")
    vertexPosWriter.addData3f(0, 0, 0)
    vertexPosWriter.addData3f(0, 0, 1)
    vertexPosWriter.addData3f(cos(pi / 6.), 0., .5)

    # let's also add color to each vertex
    colorWriter = GeomVertexWriter(vdata, "color")
    colorWriter.addData4f(color_vec4)
    colorWriter.addData4f(color_vec4)
    colorWriter.addData4f(color_vec4)

    # make primitives and assign vertices to them (primitives and primitive
    # groups can be made independently from vdata, and are later assigned
    # to vdata)
    tris = GeomTriangles(Geom.UHStatic)

    # 1st triangle
    tris.addVertices(0, 2, 1)
    tris.closePrimitive()  # the 1st primitive is finished

    # make a Geom object to hold the primitives
    quadGeom = Geom(vdata)
    quadGeom.addPrimitive(tris)

    # now put quadGeom in a GeomNode. You can now position your geometry
    # in the scene graph.
    quadGN = GeomNode("colored_quad_node")
    quadGN.addGeom(quadGeom)

    return quadGN


def create_colored_polygon2d_GeomNode_from_point_cloud(point_cloud, color_vec4=Vec4(0., 0., 1., 1.)):
    # for triangulation (with tripy) the elements of point_cloud
    # must be 3-tuples instead of np.arrays
    triangles = tripy_modified.earclip(
        [tuple(elem) for elem in point_cloud])
    triangles = np.array(triangles)  # convert tuples to np.arrays

    # naive rendering: abusing the concept of an index buffer

    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_polygon", format, Geom.UHStatic)
    vdata.setNumRows(4)
    # make a Geom object to hold the primitives
    geom = Geom(vdata)  # give it a reference to the 
    # add position and color to each vertex
    vertex_pos_writer = GeomVertexWriter(vdata, "vertex")
    vertex_color_writer = GeomVertexWriter(vdata, "color")

    # fill vertex buffer
    for triangle in triangles: 
        vertex_pos_writer.addData3f(triangle[0][0], 0, triangle[0][1])  # z is up
        vertex_pos_writer.addData3f(triangle[1][0], 0, triangle[1][1])
        vertex_pos_writer.addData3f(triangle[2][0], 0, triangle[2][1])
        vertex_color_writer.addData4f(color_vec4)
        vertex_color_writer.addData4f(color_vec4)
        vertex_color_writer.addData4f(color_vec4)

    # create the GeomPrimitive (just one) by filling the index buffer 
    # in stages. The documentation says 'Each GeomPrimitive object actually
    # stores several different individual primitives, each of which is
    # represwended simply as a list of vertex numbers, indexing into the
    # vertices stored in the associated GeomVertexData'

    tris = GeomTriangles(Geom.UHStatic)  # derived from GeomPrimitive
    # for idx, triangle in enumerate(triangles): 
    #     tris.addVertex(idx*3 + 0)
    #     tris.addVertex(idx*3 + 1)
    #     tris.addVertex(idx*3 + 2)
    #     # close the current primitive (not the GeomPrimitive!)

    tris.add_consecutive_vertices(0, 3*len(triangles))

    tris.closePrimitive()

    geom.addPrimitive(tris)

    geom_node = GeomNode("colored_polygon_node")
    geom_node.addGeom(geom)

    return geom_node 

