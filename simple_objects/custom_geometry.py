from panda3d.core import (
    GeomVertexFormat,
    GeomVertexData,
    Geom, GeomVertexWriter,
    GeomTriangles,
    GeomTrifans,
    GeomLinestrips,
    GeomLines,
    LineSegs,
    GeomNode,
    Vec3,
    Vec4,
    GeomPoints)

from panda3d.core import Triangulator, LPoint2d, NodePath

from math import pi, cos
import numpy as np

from local_utils import math_utils

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
    quadGeomNode = GeomNode("quad")
    quadGeomNode.addGeom(quadGeom)

    return quadGeomNode


def createColoredUnitQuadGeomNode(color_vec4=Vec4(0., 0., 1., 1.), center_it=False):
    # Own Geometry

    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_quad", format, Geom.UHStatic)
    vdata.setNumRows(4)

    vertexPosWriter = GeomVertexWriter(vdata, "vertex")
    if center_it == False: 
        vertexPosWriter.addData3f(0, 0, 0)
        vertexPosWriter.addData3f(1, 0, 0)
        vertexPosWriter.addData3f(1, 0, 1)
        vertexPosWriter.addData3f(0, 0, 1)
    else:
        vertexPosWriter.addData3f(0 - 0.5, 0, 0 - 0.5)
        vertexPosWriter.addData3f(1 - 0.5, 0, 0 - 0.5)
        vertexPosWriter.addData3f(1 - 0.5, 0, 1 - 0.5)
        vertexPosWriter.addData3f(0 - 0.5, 0, 1 - 0.5)


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
    quadGeomNode = GeomNode("colored_quad_node")
    quadGeomNode.addGeom(quadGeom)

    return quadGeomNode


def createColoredArrowGeomNode(color_vec4=Vec4(0., 0., 1., 1.), center_it=False):
    # Own Geometry

    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_quad", format, Geom.UHStatic)
    vdata.setNumRows(4)

    vertexPosWriter = GeomVertexWriter(vdata, "vertex")

    if center_it is False: 
        vertexPosWriter.addData3f(           0,  0,  0)
        vertexPosWriter.addData3f(           0,  0,  1)
        vertexPosWriter.addData3f(cos(pi / 6.), 0., .5)
    else:
        vertexPosWriter.addData3f(           0,  0,  0 - 0.5)
        vertexPosWriter.addData3f(           0,  0,  1 - 0.5)
        vertexPosWriter.addData3f(cos(pi / 6.), 0., .5 - 0.5)

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

    # add the Geom object to a GeomNode
    geomNode = GeomNode("colored_arrowhead_node")
    geomNode.addGeom(quadGeom)

    return geomNode


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

def create_GeomNode_Simple_Polygon_with_Hole(symbol_geometries):

    color_vec4 = Vec4(1., 1., 1., 1.)

    outerpolygon_contour_points = 0.1 * symbol_geometries[0][0]
    inner_hole_contour_points = 0.1 * symbol_geometries[0][1]


    from itertools import groupby

    inner_hole_contour_points = [k for k,g in groupby(inner_hole_contour_points.tolist())]
    # inner_hole_contour_points.append(inner_hole_contour_points[0])
    inner_hole_contour_points = np.array(inner_hole_contour_points)[:-1]
    outerpolygon_contour_points = [k for k,g in groupby(outerpolygon_contour_points.tolist())]
    # outerpolygon_contour_points.append(outerpolygon_contour_points[0])
    outerpolygon_contour_points = np.array(outerpolygon_contour_points)[:-1]

    # remove consecutive doubles in contour 

    # outerpolygon_contour_points = inner_hole_contour_points

    # outerpolygon_contour_points = (
    #     np.array([[0, 1], [-1, 0], [0, -1], [1, 0]], dtype=np.float64))

    # inner_hole_contour_points = (
    #     0.5 * np.array([[0, 1], [-1, 0], [0, -1], [1, 0]], dtype=np.float64))

    
    tr = Triangulator()

    # very simple triangular hole
    # v1 = np.array([ 
    #     np.amax(outerpolygon_contour_points[:, 0]), 
    #     np.amax(outerpolygon_contour_points[:, 1]), 
    # ]) + np.array([-0.2, -0.15]) 
    # v2 = v1 + np.array([-0.05, -0.05])
    # v3 = v1 + np.array([0.0, -0.05])
    # inner_hole_contour_points = [v1, v2, v3]

    for vertex in outerpolygon_contour_points: 
        vi = tr.addVertex(vertex[0], vertex[1])
        tr.addPolygonVertex(vi)

    tr.beginHole()
    for vertex in inner_hole_contour_points:
        vi = tr.addVertex(vertex[0], vertex[1])
        tr.addHoleVertex(vi)


    tr.triangulate()
    
    vertices = tr.getVertices()

    indices = []
    num_triangles = tr.getNumTriangles()
    for i in range(num_triangles):
        indices.append([tr.getTriangleV0(i), tr.getTriangleV1(i), tr.getTriangleV2(i)])

    # Own Geometry

    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_polygon", format, Geom.UHStatic)
    vdata.setNumRows(4)
    
    # let's also add color to each vertex
    colorWriter = GeomVertexWriter(vdata, "color")
    vertexPosWriter = GeomVertexWriter(vdata, "vertex")

    for v in vertices: 
        vertexPosWriter.addData3f(v[0], 0, v[1])
        colorWriter.addData4f(color_vec4)

    # make primitives and assign vertices to them (primitives and primitive
    # groups can be made independently from vdata, and are later assigned
    # to vdata)
    tris = GeomTriangles(Geom.UHStatic) 

    for index_triple in indices: 
        tris.addVertices(index_triple[0], index_triple[1], index_triple[2])

    tris.closePrimitive()

    # make a Geom object to hold the primitives
    geom = Geom(vdata)  # vdata contains the vertex position/color/... buffers
    geom.addPrimitive(tris)  # tris contains the index buffer

    # now put geom in a GeomNode
    geom_node = GeomNode("colored_polygon_node")
    geom_node.addGeom(geom)

    return geom_node


def create_Triangle_Mesh_From_Vertices_and_Indices(vertices, indices,
                                                   color_vec4=Vec4(1., 1., 1., 1.)):
    """ create a mesh out of flat arrays of vertices and indices, which were prepared
    to create a mesh made of triangles. """

    # Own Geometry

    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_mesh_out_of_triangles", format, Geom.UHStatic)
    vdata.setNumRows(4)

    # let's also add color to each vertex
    colorWriter = GeomVertexWriter(vdata, "color")
    vertexPosWriter = GeomVertexWriter(vdata, "vertex")

    vertices = np.reshape(vertices, (-1, 3))
    for v in vertices:

        vertexPosWriter.addData3f(v[0], v[1], v[2])
        colorWriter.addData4f(color_vec4)

    # make primitives and assign vertices to them (primitives and primitive
    # groups can be made independently from vdata, and are later assigned
    # to vdata)
    tris = GeomTriangles(Geom.UHStatic)

    indices = np.reshape(indices, (-1, 3))
    for index_triple in indices:

        tris.addVertices(index_triple[0], index_triple[1], index_triple[2])

    tris.closePrimitive()

    # make a Geom object to hold the primitives
    geom = Geom(vdata)  # vdata contains the vertex position/color/... buffers
    geom.addPrimitive(tris)  # tris contains the index buffer

    # now put geom in a GeomNode
    geom_node = GeomNode("colored_polygon_node")
    geom_node.addGeom(geom)

    return geom_node


def create_GeomNode_Simple_Polygon_with_Hole_LineStrips(symbol_geometries):
    color_vec4 = Vec4(1., 1., 1., 1.)

    outerpolygon_contour_points = 0.1 * symbol_geometries[0][0]
    inner_hole_contour_points = 0.1 * symbol_geometries[0][1]

    # outerpolygon_contour_points = (
    #     np.array([[0, 1], [-1, 0], [0, -1], [1, 0]], dtype=np.float64))

    # inner_hole_contour_points = (
    #     0.5 * np.array([[0, 1], [-1, 0], [0, -1], [1, 0]], dtype=np.float64))


    from panda3d.core import Triangulator, LPoint2d
    
    # tr = Triangulator()

    # for vertex in outerpolygon_contour_points: 
    #     vi = tr.addVertex(vertex[0], vertex[1])
    #     tr.addPolygonVertex(vi)

    # tr.beginHole()
    # for vertex in inner_hole_contour_points:
    #     vi = tr.addVertex(vertex[0], vertex[1])
    #     tr.addHoleVertex(vi)

    # tr.triangulate()
    
    # vertices = tr.getVertices()

    # indices = []
    # num_triangles = tr.getNumTriangles()
    # for i in range(num_triangles):
    #     indices.append([tr.getTriangleV0(i), tr.getTriangleV1(i), tr.getTriangleV2(i)])

    # Own Geometry

    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_polygon", format, Geom.UHStatic)
    vdata.setNumRows(4)

    # let's also add color to each vertex
    colorWriter = GeomVertexWriter(vdata, "color")
    vertexPosWriter = GeomVertexWriter(vdata, "vertex")

    for v in outerpolygon_contour_points: 
        vertexPosWriter.addData3f(v[0], 0, v[1])
        colorWriter.addData4f(color_vec4)
    
    for v in inner_hole_contour_points: 
        vertexPosWriter.addData3f(v[0], 0, v[1])
        colorWriter.addData4f(color_vec4)

    # make primitives and assign vertices to them (primitives and primitive
    # groups can be made independently from vdata, and are later assigned
    # to vdata)
    # tris = GeomTriangles(Geom.UHStatic) 

    tris = GeomLinestrips(Geom.UHStatic)

    # for index_triple in indices: 
    #     tris.addVertices(index_triple[0], index_triple[1], index_triple[2])
    tris.add_consecutive_vertices(0, len(outerpolygon_contour_points))
    tris.closePrimitive()

    tris.add_consecutive_vertices(len(outerpolygon_contour_points), len(inner_hole_contour_points))
    tris.closePrimitive()

    # make a Geom object to hold the primitives
    polygonGeom = Geom(vdata)  # vdata contains the vertex position/color/... buffers
    polygonGeom.addPrimitive(tris)  # tris contains the index buffer

    # now put quadGeom in a GeomNode. You can now position your geometry
    # in the scene graph.
    polygonGeomNode = GeomNode("colored_polygon_node")
    polygonGeomNode.addGeom(polygonGeom)

    return polygonGeomNode


def create_GeomNode_Simple_Polygon_without_Hole(symbol_geometries):

    color_vec4 = Vec4(1., 1., 1., 1.)

    outerpolygon_contour_points = 0.1 * symbol_geometries[0][0]
    # inner_hole_contour_points = 0.1 * symbol_geometries[0][1]

    # outerpolygon_contour_points = (
    #     np.array([[0, 1], [-1, 0], [0, -1], [1, 0]], dtype=np.float64))

    # inner_hole_contour_points = (
    #     0.5 * np.array([[0, 1], [-1, 0], [0, -1], [1, 0]], dtype=np.float64))

    from panda3d.core import Triangulator, LPoint2d
    
    tr = Triangulator()

    for vertex in outerpolygon_contour_points: 
        vi = tr.addVertex(vertex[0], vertex[1])
        tr.addPolygonVertex(vi)

    # tr.beginHole()
    # for vertex in inner_hole_contour_points:
    #     vi = tr.addVertex(vertex[0], vertex[1])
    #     tr.addHoleVertex(vi)

    tr.triangulate()
    
    vertices = tr.getVertices()

    indices = []
    num_triangles = tr.getNumTriangles()
    for i in range(num_triangles):
        indices.append([tr.getTriangleV0(i), tr.getTriangleV1(i), tr.getTriangleV2(i)])

    # Own Geometry

    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_polygon", format, Geom.UHStatic)
    vdata.setNumRows(4)
    
    # let's also add color to each vertex
    colorWriter = GeomVertexWriter(vdata, "color")
    vertexPosWriter = GeomVertexWriter(vdata, "vertex")

    for v in vertices: 
        vertexPosWriter.addData3f(v[0], 0, v[1])
        colorWriter.addData4f(color_vec4)

    # make primitives and assign vertices to them (primitives and primitive
    # groups can be made independently from vdata, and are later assigned
    # to vdata)
    tris = GeomTriangles(Geom.UHStatic) 
    

    for index_triple in indices: 
        tris.addVertices(index_triple[0], index_triple[1], index_triple[2])

    tris.closePrimitive()

    # make a Geom object to hold the primitives
    polygonGeom = Geom(vdata)  # vdata contains the vertex position/color/... buffers
    polygonGeom.addPrimitive(tris)  # tris contains the index buffer

    # now put quadGeom in a GeomNode. You can now position your geometry
    # in the scene graph.
    polygonGeomNode = GeomNode("colored_polygon_node")
    polygonGeomNode.addGeom(polygonGeom)

    return polygonGeomNode


def createColoredUnitDisk(color_vec4=Vec4(0., 0., 1., 1.), num_of_verts=10):
    # Own Geometry
    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_circle", format, Geom.UHStatic)
    vdata.setNumRows(4)

    vertexPosWriter = GeomVertexWriter(vdata, "vertex")

    # num_of_verts = 10

    # phi = 0.
    r = 1.

    origin_point_x = 0.
    origin_point_z = 0.
    vertexPosWriter.addData3f(origin_point_x, 0, origin_point_z)

    circle_points = math_utils.get_circle_vertices(num_of_verts=num_of_verts, radius=r)

    _normal_vector_info = Vec3(0., 1., 0.)      # this is returned just as info about the normal vector of the generated geometry
    for p in circle_points:
        vertexPosWriter.addData3f(p[0], 0, p[1])

    # for i in range(num_of_verts):
    #     phi += 2. * np.pi / num_of_verts
    #     x = r * np.cos(phi)
    #     z = r * np.sin(phi)
    #     vertexPosWriter.addData3f(x, 0, z)

    # let's also add color to each vertex
    colorWriter = GeomVertexWriter(vdata, "color")

    colorWriter.addData4f(color_vec4)  # origin point

    for i in range(num_of_verts):
        colorWriter.addData4f(color_vec4)

    # make primitives and assign vertices to them (primitives and primitive
    # groups can be made independently from vdata, and are later assigned
    # to vdata)
    tris = GeomTrifans(Geom.UHStatic)  # the first vertex is a vertex that all triangles share

    tris.add_consecutive_vertices(0, num_of_verts+1)
    tris.addVertex(1)

    tris.closePrimitive()  # the 1st primitive is finished

    # make a Geom object to hold the primitives
    geom = Geom(vdata)
    geom.addPrimitive(tris)

    geom_node = GeomNode("colored_circle_node")
    geom_node.addGeom(geom)

    return geom_node, _normal_vector_info


from panda3d.core import LineSegs

def createColoredUnitLineGeomNode(thickness=1.,
                                  color_vec4=Vec4(1., 1., 1., 1.)):
    ls = LineSegs()
    ls.setThickness(thickness)

    ls.setColor(color_vec4)
    ls.moveTo(0.0, 0.0, 0.0)
    ls.drawTo(1.0, 0.0, 0.0)

    geomnode = ls.create()

    nodepath = NodePath(geomnode)

    # quadGeomNode = GeomNode("colored_quad_node")
    # quadGeomNode.addGeom(quadGeom)

    return geomnode


from panda3d.core import LineSegs

def createColoredUnitDashedLineGeomNode(
        thickness=5., color_vec4=Vec4(1., 1., 1., 1.),
        howmany_periods=5.):
    # thickness=5.
    # color_vec4=Vec4(1., 1., 1., 0.5)

    ls = LineSegs()
    ls.setThickness(thickness)

    ls.setColor(color_vec4)

    source_point = np.array([0.0, 0.0, 0.0])
    destination_point = np.array([1.0, 0.0, 0.0])
    difference_vector = np.array(destination_point - source_point)
    difference_normal_vector = difference_vector / np.linalg.norm(difference_vector)

    dashed_line_segments = []
    length = np.abs(np.linalg.norm(source_point - destination_point))
    # standard_segment_period = 1.0 * 1.0/5.0
    # howmany_periods = 3.  # e.g. entered by the user

    # a quarter period would draw '--'
    # a half a period then draws '--  ', which has no visible ending
    # the in-between number of periods can be 0, but at least
    # '--  -' is drawn (which is technically a dashed line)
    assert howmany_periods > 1./2.

    # the dashed line shoud start and end with a visible segment, like this:
    # --    ----    ----    --
    # thus, draw the first and last segment seperately
    # and add offset to in-between segments

    # draw first half-segment
    ls.moveTo(*tuple(source_point))
    offset_length = np.linalg.norm((difference_vector/howmany_periods)/4.)
    # offset_length = 0.
    ls.drawTo(*tuple(source_point + offset_length*difference_normal_vector))
    one_period_vector = difference_vector / howmany_periods

    # draw in-between segments
    howmany_periods_in_between = howmany_periods - 2.
    length_in_between = length - 2.*np.linalg.norm(one_period_vector)
    in_between_lengths_arr = np.linspace(0., length_in_between, int(howmany_periods_in_between)+1)

    for dis_length in in_between_lengths_arr:
        # draw a period: line segment takes half the space
        ls.moveTo(*tuple(
            source_point
            + offset_length * difference_normal_vector
            + dis_length * difference_normal_vector
            + 0.5 * one_period_vector))
        ls.drawTo(*tuple(
            source_point
            + offset_length * difference_normal_vector
            + dis_length * difference_normal_vector
            + 1.0 * one_period_vector))

    # draw last half-segment, also 1./4. a period long
    ls.moveTo(*tuple(
        source_point
        + offset_length * difference_normal_vector
        + max(in_between_lengths_arr) * difference_normal_vector
        + (1. + 0.5) * one_period_vector))
    ls.drawTo(*tuple(
        source_point
        + offset_length * difference_normal_vector
        + max(in_between_lengths_arr) * difference_normal_vector
        + (1. + 0.5 + 1./4.) * one_period_vector))

    geomnode = ls.create()
    # nodepath = NodePath(geomnode)

    return geomnode

def createColoredParametricCurveGeomNode(
        func=(lambda t: np.array([t, t, t])),
        param_interv=np.array([0, 1]),
        thickness=5., color=Vec4(1., 1., 1., 1.),
        howmany_points=50):

    ls = LineSegs()
    ls.setThickness(thickness)
    ls.setColor(color)

    t = np.linspace(param_interv[0], param_interv[1], num=howmany_points, endpoint=True)

    for i, c_t in enumerate(t):
        xyz_arr = func(c_t)
        if i > 0:
            ls.drawTo(*tuple(xyz_arr))

        ls.moveTo(*tuple(xyz_arr))

    geomnode = ls.create()
    # nodepath = NodePath(geomnode)

    return geomnode


def createColoredSegmentedLineGeomNode(coords,
        thickness=5., color=Vec4(1., 1., 1., 1.)):
    """ Plot a series of solid lines, connected to each other.
    Args:
        coords: list of 3d np.array """

    ls = LineSegs()
    ls.setThickness(thickness)
    ls.setColor(color)

    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
    ls.moveTo(*tuple(coords[0]))

    for i, coord in enumerate(coords):
        ls.drawTo(*tuple(coord))
        ls.moveTo(*tuple(coord))

    geomnode = ls.create()
    # nodepath = NodePath(geomnode)

    return geomnode


# def createColoredParametricDashedCurveGeomNode(
#         func=(lambda t: np.array([t, t, t])),
#         param_interv=np.array([0, 1]),
#         thickness=5., color=Vec4(1., 1., 1., 1.),
#         howmany_points=50,
#         howmany_periods=50):

#     # FIXME: drawing an arc as a dashed line is more complicated than I thought, especially if the dashes themselves aren't straight.

#     ls = LineSegs()
#     ls.setThickness(thickness)
#     ls.setColor(color)

#     t = np.linspace(param_interv[0], param_interv[1], num=howmany_points, endpoint=True)

#     # dash_length = 0.1  # hardcoded for now

#     # process: if 2. * (the current length) has a rest (floating point modulo) of less than

#     l_dseg = 0.1

#     p0 = None
#     p1 = None
#     l = 0.  # accumulated total length
#     l_dseg_acc = 0.  # accumulated partial length after the start of a dseg

#     for i, c_t in enumerate(t):
#         if i > 0:
#             p1 = func(c_t)
#             delta_l_vec = p1 - p0
#             p0_prime = p0

#             while True:  # do while loop, changing p0_prime and delta_l_prime

#                 delta_l_prime_vec = p0_prime - p1
#                 delta_l_prime_sign = np.sign(np.dot(delta_l_vec, delta_l_prime_vec))  # delta_l_prime_sign = +-1 : parallel/antiparallel

#                 if ((p0_prime != p1).any() and delta_l_prime_sign < 0):  # antiparallel, i.e. pp_seg has been undershot
#                     # going forward until p1 is reached

#                     delta = l_dseg - l_dseg_acc
#                     overshot = np.abs(delta) - np.linalg.norm(delta_l_prime_vec)  # if overshot is > 0, it has overshot
#                     old_overshot  # STUCK: OH MAN, it can have a whole array of overshots! that's too complicated for now. Laying it off ...
#                     if delta < 0 and np.abs(delta) <= np.linalg.norm(delta_l_prime_vec):
#                         # the dseg stops before or exactly at the end of the pp_seg
#                         l_step = np.abs(delta)
#                         l_dseg_acc += l_step  # add the length
#                         p0_prime += l_step * -delta_l_vec/np.linalg.norm(delta_l_vec)  # go forward
#                     elif delta < 0 and np.abs(delta) >= np.linalg.norm(delta_l_prime_vec):
#                         # the dseg overshoots the end of the pp_seg, i.e. goes further than p1
#                         # # so, make it go to p1 only, set p0 to p1, draw, break out of the while loop, continue the for loop

#                         l_step = np.linalg.norm(delta_l_prime_vec)
#                         l_dseg_acc = 0.  # reset, since we arrived at the end of a dseg
#                         p0_prime = p1
#                     print("hey0")

#                 elif ((p0_prime != p1).any() and delta_l_prime_sign > 0):  # parallel, i.e. pp_seg has been overshot
#                     # trim it and draw
#                     l_step = np.linalg.norm(p1 - p0_prime)
#                     # it has been overshot, so just say p0_prime = p1
#                     p0_prime = p1
#                     print("hey1")

#                 else:  # this should mean that the two vectors are equal, i.e. p0_prime hits p1 'by accident'
#                     assert (p0_prime == p1).all()
#                     l_step = 0
#                     p0_prime = p1
#                     print("hey2")

#                 l += l_step

#                 if l % (2. * l_dseg) < l_dseg:  # check if we are in a draw segment or in a non-draw segment of the dashing period "--  "
#                     # draw and move
#                     ls.drawTo(*tuple(p0_prime))
#                     ls.moveTo(*tuple(p0_prime))
#                 else:
#                     # do not draw, just move
#                     ls.moveTo(*tuple(p0_prime))

#                 if (p0_prime == p1).all():
#                     p0 = p1
#                     print("hey3")
#                     break

#         elif i == 0:  # goes in here first
#             p0 = func(c_t)
#             ls.moveTo(*tuple(p0))

#     geomnode = ls.create()
#     # nodepath = NodePath(geomnode)

#     return geomnode

# def createColoredParametricDashedCurveGeomNode(
#             func=func,
#             param_interv=param_interv, thickness=thickness, color=color, howmany_points=howmany_points,
#             howmany_periods=howmany_periods)



def create_GeomNode_Cone(color_vec4=Vec4(1., 1., 1., 1.)):
    # a cone that points into the y direction
    # and the center of it's base is at the origin

    # ---- step 1: create circle with trifans in the x-y plane and close the primitive

    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_quad", format, Geom.UHStatic)
    vdata.setNumRows(4)

    # add color to each vertex
    colorWriter = GeomVertexWriter(vdata, "color")

    # add a vertex position to each vertex
    vertexPosWriter = GeomVertexWriter(vdata, "vertex")

    # first the circle vertices
    num_of_circle_vertices = 10
    circle_verts = math_utils.get_circle_vertices(num_of_verts=num_of_circle_vertices)

    # then the origin point vertex
    vertexPosWriter.addData3f(0., 0., 0.)
    colorWriter.addData4f(color_vec4)

    for v in circle_verts:
        vertexPosWriter.addData3f(v[0], v[1], v[2])
        colorWriter.addData4f(color_vec4)

    # build the primitive (base of cone)
    tris = GeomTrifans(Geom.UHStatic) # the first vertex is a vertex that all triangles share

    tris.add_consecutive_vertices(0, num_of_circle_vertices+1)  # add all vertices

    # close up the circle (the last triangle involves the first
    # point of the circle base, i.e. point with index 1)
    tris.addVertex(1)

    tris.closePrimitive()  # this resets all the data contained in the vertexPosWriter and colorWriter

    # ---- step 2: create tip vertex and make a trifans primitive
    #      with the vertices of the cone base outer circle

    # first the tip point vertex
    vertexPosWriter.addData3f(0., 0., cos(pi / 6.))
    colorWriter.addData4f(color_vec4)

    tris.addVertex(num_of_circle_vertices+1)
    tris.add_consecutive_vertices(0, num_of_circle_vertices+1)  # add all circle vertices

    # close up the circle (the last triangle involves the first
    # point of the circle base, i.e. point with index 1)
    tris.addVertex(0)

    tris.closePrimitive()  # this resets all the data contained in the vertexPosWriter and colorWriter

    # ----- step 3: make a GeomNode out of the Geom (to which the Primitives have been added)

    # make a Geom object to hold the primitives
    geom = Geom(vdata)
    geom.addPrimitive(tris)

    geom_node = GeomNode("colored_polygon_node")
    geom_node.addGeom(geom)

    return geom_node


def create_GeomNode_Single_Point(color_vec4=Vec4(1., 1., 1., 1.)):
    # ---- step 1: create point at (0,0,0) and close the primitive

    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_point", format, Geom.UHStatic)
    vdata.setNumRows(4)

    # add color to each vertex
    colorWriter = GeomVertexWriter(vdata, "color")

    # add a vertex position to each vertex
    vertexPosWriter = GeomVertexWriter(vdata, "vertex")

    # just one origin point vertex, it gets transformed later
    # to it's intended position
    vertexPosWriter.addData3f(0., 0., 0.)
    colorWriter.addData4f(color_vec4)

    # build the primitive
    pointsprimitive = GeomPoints(Geom.UHStatic)
    pointsprimitive.addVertex(0)
    pointsprimitive.closePrimitive()  # this resets all the data contained in the vertexPosWriter and colorWriter

    # ----- step 3: make a GeomNode out of the Geom (to which the Primitives have been added)

    # make a Geom object to hold the primitives
    geom = Geom(vdata)
    geom.addPrimitive(pointsprimitive)

    geom_node = GeomNode("colored_point_node")
    geom_node.addGeom(geom)

    return geom_node


def draw_dash(ls, draw_state, # from_point,
              from_point,
              to_point):
    """
    draw_state: 1: draw and move
                0: just move (don't draw)
    """

    if draw_state == 1:
        if (from_point != to_point).any():
            ls.moveTo(*tuple(from_point))
            print("drawing from ", from_point, "to", to_point)
            ls.drawTo(*tuple(to_point))
            # ls.moveTo(*tuple(to_point))
            return to_point
    elif draw_state == 0:
        # ls.moveTo(*tuple(from_point))
        # ls.moveTo(*tuple(to_point))
        return to_point
    else:

        print("ERR in draw_dash: draw_state not defined")
        exit(1)

def bit_flip(x):
    assert x == 1 or x == 0
    return 1 - x

def createColoredParametricDashedCurveGeomNode(
        func# =(lambda t: np.array([t, t, t]))
        ,
        param_interv=np.array([0, 1]),
        thickness=1., color=Vec4(1., 1., 1., 1.),
        howmany_points=50):

    ls = LineSegs()
    ls.setThickness(thickness)
    ls.setColor(color)

    t = np.linspace(param_interv[0], param_interv[1], num=howmany_points, endpoint=True)
    points = np.array([func(ti) for ti in t])

    dash_length = 0.25  # hardcoded for now
    remaining_dash_length = dash_length

    dash_draw_state = 0  # 1: draw, 0: no draw

    # current point indices
    ip1 = 0
    ip2 = 1

    remaining_pp_length = np.linalg.norm(points[ip1] - points[ip2])

    draw_from_point = points[ip1]

    while True:
        remaining_pp_length = np.linalg.norm(points[ip2] - draw_from_point)
        if remaining_dash_length <= remaining_pp_length:
            draw_from_point = draw_dash(ls, dash_draw_state, draw_from_point, draw_from_point + remaining_dash_length * (points[ip2] - draw_from_point)/np.linalg.norm(points[ip2] - draw_from_point))
            dash_draw_state = bit_flip(dash_draw_state)
            remaining_dash_length = dash_length
        else:
            remaining_dash_length -= np.linalg.norm(points[ip2] - draw_from_point)
            draw_from_point = draw_dash(ls, dash_draw_state, draw_from_point, points[ip2])
            if ip2 < len(points) - 1:  # i.e. if it's a len(points) == 2 array, then the max index is 1
                ip1 += 1
                ip2 += 1
            else:
                break

    geomnode = ls.create()
    # nodepath = NodePath(geomnode)

    return geomnode


def createCircle(color_vec4=Vec4(1., 1., 1., 1.), with_hole=False, num_of_verts=10, radius=1.):
    # Own Geometry
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_circle", format, Geom.UHStatic)
    vdata.setNumRows(4)

    vertexPosWriter = GeomVertexWriter(vdata, "vertex")

    # generates circles in x-y plane
    circle_points = math_utils.get_circle_vertices(num_of_verts=num_of_verts, radius=radius)

    for p in circle_points:
        vertexPosWriter.addData3f(p[0], p[1], p[2])

    # let's also add color to each vertex
    colorWriter = GeomVertexWriter(vdata, "color")

    for i in range(num_of_verts):
        colorWriter.addData4f(color_vec4)

    # make primitives and assign vertices to them (primitives and primitive
    # groups can be made independently from vdata, and are later assigned
    # to vdata)
    line = GeomLinestrips(Geom.UHStatic)

    line.add_consecutive_vertices(0, num_of_verts)

    if with_hole != True:
        line.add_vertex(0)  # connect it up at the end

    line.closePrimitive()  # the 1st primitive is finished

    # make a Geom object to hold the primitives
    geom = Geom(vdata)
    geom.addPrimitive(line)

    geom_node = GeomNode("colored_circle_node")
    geom_node.addGeom(geom)

    return geom_node
