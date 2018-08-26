import svgpathtools
import sys
import numpy as np

class Polygon: 
    def __init__(self, points=np.array([])):
        self.points = points

    def addVertex(self, x, y):
        self.points = np.append(self.points, [x, y])

    def getVertices(self):
        return self.points


class OuterPolygon(Polygon):
    def __init__(self, points): 
        Polygon.__init__(self, points)


class InnerHolePolygon(Polygon):
    def __init__(self, points): 
        Polygon.__init__(self, points)

# and 8 has 1 outer polygon and 2 inner holes
# a large Theta has an outer polygon, an inner hole, and within that again an
# outer polygon
# I need to figure out if their svg paths look different (they must!)
# and then accordingly categorize them within these classes

class OuterPolygonWithInnerHolePolygons:  # e.g. an 8
    def __init__(self, outer_polygon=None, inner_hole_polygons=[]): 
        self.outer_polygon = outer_polygon
        self.inner_hole_polygons = inner_hole_polygons

    def addInnerHolePolygon(self, inner_hole_polygon):
        self.inner_hole_polygons.append(inner_hole_polygon)

    def setOuterPolygon(self, outer_polygon):
        self.outer_polygon = outer_polygon

        
def get_points_from_parsed_path_one_moveto(parsed_path):
    num_intermediate_points = 10.

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


def get_nested_polygons_from_svg_paths(svg_paths):
    nested_polygons = []

    for path in svg_paths:
        # split: without the M's in front, cut the first one off because it's ""
        pathSegs_strs = path.d().split("M")[1:]
        # with the M's in front
        pathSegs_strs = ["M " + s for s in pathSegs_strs]
        # parse the individual segment of that one path
        parsed_paths = [svgpathtools.parse_path(x) for x in pathSegs_strs]

        # categorize them into outer polygons with inner holes
        polygon_pair = OuterPolygonWithInnerHolePolygons()

        # if there's two moveto commands within a path, it has one hole
        points = get_points_from_parsed_path_one_moveto(parsed_paths[0])
        if len(parsed_paths) is 1: 
            # get the points
            outerpolygon = OuterPolygon(points)
            polygon_pair.setOuterPolygon(outerpolygon)

        elif len(parsed_paths) is 2: 
            # get the points of the outer
            outerpolygon = OuterPolygon(points)
            polygon_pair.setOuterPolygon(outerpolygon)
            # get the points of the inner
            points_inner = get_points_from_parsed_path_one_moveto(parsed_paths[1])
            innerpolygon = InnerHolePolygon(points_inner)
            polygon_pair.addInnerHolePolygon(innerpolygon)

        else: 
            print("This case of nested polygons isn't handled yet")

        return nested_polygons.append(polygon_pair)


if __name__ == "__main__": 

    file = sys.argv[1]

    # only need paths
    paths, _ = svgpathtools.svg2paths(file)

    nested_polygons = get_nested_polygons_from_svg_paths(paths)
    # now they are ready for the panda3d triangulator

    import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
    print("end")


