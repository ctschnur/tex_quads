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
    Vec4)

from panda3d.core import Triangulator, LPoint2d, NodePath

from math import pi, cos
import numpy as np

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


def createColoredUnitCircle(color_vec4=Vec4(0., 0., 1., 1.)):
    # Own Geometry
    # format = GeomVertexFormat.getV3c4t2()
    format = GeomVertexFormat.getV3c4()
    vdata = GeomVertexData("colored_circle", format, Geom.UHStatic)
    vdata.setNumRows(4)

    vertexPosWriter = GeomVertexWriter(vdata, "vertex")

    num_of_verts = 10

    phi = 0.
    r = 1.

    origin_point_x = 0.
    origin_point_z = 0.
    vertexPosWriter.addData3f(origin_point_x, 0, origin_point_z)

    for i in range(num_of_verts):
        phi += 2. * np.pi / num_of_verts
        x = r * np.cos(phi)
        z = r * np.sin(phi)
        vertexPosWriter.addData3f(x, 0, z)


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

    return geom_node


from panda3d.core import LineSegs

def createColoredUnitLineGeomNode(thickness=1., color_vec4=Vec4(1., 1., 1., 1.)):
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


def get_circle_vertices(num_of_verts=10, radius=0.5):
    phi = 0.
    r = radius

    origin_point_x = 0.
    origin_point_z = 0.

    verts = np.array([])
    for i in range(num_of_verts):
        phi += 2. * np.pi / num_of_verts
        x = r * np.cos(phi)
        y = r * np.sin(phi)
        z = 0

        verts = np.append(verts, np.array([x, y, z]))

    return np.reshape(verts, (-1, 3))


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
    circle_verts = get_circle_vertices(num_of_verts=num_of_circle_vertices)

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
