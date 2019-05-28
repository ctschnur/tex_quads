import sys
sys.path.append("..")

# import triangulator.main

import svgpathtools
import sys
import numpy as np
np.set_printoptions(precision=4, threshold=5)

class IndexedTriangles:
    def __init__():
        self.vertices = []
        self.indices = []
    def __repr__(self):
        return ("vertices: " + str(len(self.vertices)) + "\n" + str(self.vertices) + "\n"
                + "indices: " + str(len(self.indices)) + "\n" + str(self.indices) + "\n")


# class Polygon: 
#     def __init__(self, contour_points=np.array([])):
#         self.indexed_geometry = IndexedTriangles()
#         self.contour_points = contour_points
# 
#     def __repr(self)__
# 
# 
# class OuterPolygon(Polygon):
#     def __init__(self, points): 
#         Polygon.__init__(self, points)
# 
# 
# class InnerHolePolygon(Polygon):
#     def __init__(self, points): 
#         Polygon.__init__(self, points)


# class OuterPolygonWithInnerHolePolygons:  # e.g. an 8
# """
# and 8 has 1 outer polygon and 2 inner holes
# a large Theta has an outer polygon, an inner hole, and within that again an
# outer polygon. I need to figure out if their svg paths look different (they must!)
# and then accordingly categorize them within these classes
# """
#     def __init__(self): 
#         self.inner_hole_polygons = []
#         self.outer_polygon = None
#         self.indexed_geometry = IndexedTriangles()
# 
#     def addInnerHolePolygon(self, inner_hole_polygon):
#         self.inner_hole_polygons.append(inner_hole_polygon)
# 
#     def setOuterPolygon(self, outer_polygon):
#         self.outer_polygon = outer_polygon

        
def get_points_continuous_path_part(parsed_path):
    num_intermediate_points = 5.

    xs = []
    ys = []
    for segment in parsed_path: 
        xs.append(segment.start.real)
        ys.append(segment.start.imag)
        if type(segment) is svgpathtools.CubicBezier: 
            for i in np.arange(1., num_intermediate_points):  # This probably needs adjustment
                point = segment.point(i/num_intermediate_points)
                xs.append(point.real)
                ys.append(point.imag)

        xs.append(segment.end.real)
        ys.append(segment.end.imag)
    
    points = np.transpose([np.array(xs), np.array(ys)])
    return points


def get_symbol_geometries(svg_paths):
    symbol_geometries = []

    for svg_path in svg_paths:
        # split svg path into it's continuous parts
        # split: without the M's in front, the first one is an empty string
        pathSegs_strs_split = svg_path.d().split("M")[1:]
        # with the M's back in front
        pathSegs_strs = ["M " + s for s in pathSegs_strs_split]

        cont_paths = [svgpathtools.parse_path(x) for x in pathSegs_strs]

        # 2 different cases are handled here for now: 0 holes, 1 hole

        if len(cont_paths) > 2: 
            print("This case of nested polygons isn't handled yet")
            exit(1)

        symbol_geometry = []

        for cp in cont_paths: 
            contour_points = get_points_continuous_path_part(cp)
            symbol_geometry.append(contour_points)

        symbol_geometries.append(symbol_geometry)

    return symbol_geometries


def get_test_symbol_geometries():
    file = None
    if len(sys.argv) is 2: 
        file = sys.argv[1]
    else: 
        file = "svgs/main_simplified__customcleaned_only_one.svg"

    # only need paths
    svg_paths, _ = svgpathtools.svg2paths(file)

    # order them into the datastructures
    symbol_geometries = get_symbol_geometries(svg_paths)
    
    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

    return symbol_geometries


if __name__ == "__main__": 

    # now they are ready for the panda3d triangulator
    # for owip in outerPolygonWithInnerHolePolygonss:
    #     import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

    #     # TODO: remove inner hole polygons, and it works, with them it
    #     # doesn't work yet.
    #     vertices, indices = triangulator.main.triangulate_outer_polygon_with_hole_polygons(owip)

    print("end")


