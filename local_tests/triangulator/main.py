import sys
sys.path.append("..")

import svgpathtodat.main as svgpathtodat

from panda3d.core import Triangulator, LPoint2d
import numpy as np


def triangulate_outer_polygon_with_hole_polygons(outerPolygonWithInnerHolePolygons):

    # TODO: this needs to be all changed, and support for holes needs to be
    # integrated
    tr = Triangulator()

    for vertex in outerPolygonWithInnerHolePolygons.outer_polygon.getVertices(): 
        vi = tr.addVertex(vertex[0], vertex[1])
        tr.addPolygonVertex(vi)

    for inner_hole_polygon in outerPolygonWithInnerHolePolygons.inner_hole_polygons: 
        tr.beginHole()  # finish the last hole, and add to the next
        for vertex in inner_hole_polygon.getVertices():
            vi = tr.addVertex(vertex[0], vertex[1])
            tr.addHoleVertex(vi)
 
    # tr.beginHole()  # finish the last hole?
    tr.triangulate()

    # --- BEGIN getting the triangles vertices and indices ----

    def get_vertices_and_indices_from_p3d_triangulated_object(tr):

        # first linear array of triangle points
        triangles_indices = np.array([])
        num_triangles = tr.getNumTriangles()
        for i in range(num_triangles): 
            triangle = np.array([])
            # 2d vertices
            triangle = np.append(triangle, tr.getTriangleV0(i))
            triangle = np.append(triangle, tr.getTriangleV1(i))
            triangles_indices = np.append(triangles_indices, triangle)

        # reshape it
        triangles_indices = np.reshape(triangles_indices, (-1, 2))
        triangles_indices = np.array(triangles_indices, np.int32)

        # print(tr.isLeftWinding())
        # print(tr.getNumTriangles())
        # print(tr.getNumVertices())

        # return all vertices and indices needed to create a GeomPrimitive

        vertices = tr.getVertices()
        return vertices, triangles_indices

    return get_vertices_and_indices_from_p3d_triangulated_object(tr)


if __name__ == "__main__": 

    polygon1_points = (
        np.array([(0, 1), (-1, 0), (0, -1), (1, 0)], dtype=np.float64))



    outerPolygon = svgpathtodat.OuterPolygon(polygon1_points)

    outerPolygonWithInnerHolePolygons = (
        svgpathtodat.OuterPolygonWithInnerHolePolygons(
            outer_polygon=outerPolygon))

    vertices, triangle_indices = triangulate_outer_polygon_with_hole_polygons(
        outerPolygonWithInnerHolePolygons)
    


    print("end")
    
