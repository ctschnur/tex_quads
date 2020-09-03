from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain
from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle
from simple_objects import primitives
from local_utils import math_utils

import numpy as np

from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

import local_tests.svgpathtodat.main

import os
import sys
import pytest
# import gltf

from cameras.Orbiter import Orbiter

from direct.task import Task

from plot_utils.bezier_curve import BezierCurve, DraggableBezierCurve, SelectableBezierCurve

from panda3d.core import CollisionTraverser, CollisionHandlerQueue, CollisionRay, CollisionNode, GeomNode, BitMask32, VBase4

from plot_utils.graph import Graph, DraggableGraph, GraphHoverer


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.setFrameRateMeter(True)
        render.setAntialias(AntialiasAttrib.MAuto)

        ob = Orbiter(base.cam, radius=3.)
        cs = CoordinateSystem(ob)

        # ob.set_view_to_yz_plane()
        ob.set_view_to_xy_plane()

        # # -- plot surface using points
        # from plot_utils.pointcloud.pointcloud import plot_xy_z
        # x = np.linspace(0., 1., num=20, endpoint=True)
        # y = np.linspace(0., 1., num=20, endpoint=True)
        # plot_xy_z(x, y, lambda x, y: x**3. + y**3.)

        # pp = PointPrimitive(pos=Vec3(1., 1., 1.))

        # p3d = Point3d(pos=Vec3(1., 1., 1.))

        # dbc = DraggableBezierCurve(ob,
        #                            P_arr=np.array([[0.2, 0.2, 0.2],
        #                                            [0.2, 0.2, 1.2],
        #                                            [1.2, 1.2, 1.2],
        #                                            [1.2, 1.2, 0.2]]))

        # dbc = DraggableBezierCurve(ob,
        #                            P_arr=np.array([[0.2, 0.2, 0.2],
        #                                            [0.2, 0.2, 1.2],
        #                                            [1.2, 1.2, 1.2],
        #                                            [1.2, 1.2, 0.2]]))

        # sbc = SelectableBezierCurve(ob,
        #                             P_arr=np.array([[0.2, 0.2, 0.2],
        #                                             [0.2, 0.2, 1.2],
        #                                             [1.2, 1.2, 1.2],
        #                                             [1.2, 1.2, 0.2]]))

        # oc = OrientedCircle()

        # p = PointPrimitive(pos=Vec3(*tuple(np.array([1., 1., 1.]))))

        # -- generate points, then circles


        # points, path_lengths = math_utils.getPointsAndPathLengthsAlongPolygonalChain(func=(lambda t: np.array([0, t, 2.7**t])), param_interv=np.array([0., 1.]), ed_subpath_length=0.2)

        # point_primitives = []
        # for p in points:
        #     point_primitives.append(PointPrimitive(pos=Vec3(*tuple(p))))

            # plot a circle


        # gn = create_GeomNode_Sphere()
        # np = NodePath(gn)
        # np.reparentTo(render)

        # def findChildrenAndSetRenderModeRecursively(parentnode):
        #     children = parentnode.get_children()
        #     for child in children:
        #         findChildrenAndSetRenderModeRecursively(child)
        #         child.setRenderModeFilled()

        # findChildrenAndSetRenderModeRecursively(render)

        # show text on-screen

        from simple_objects.simple_objects import Pinned2dLabel


        # -- implement foce-directed graph drawing example

        # 2d graph, undirected, a few nodes, networkx

        # import matplotlib.pyplot as plt
        # import networkx as nx

        # G = nx.grid_2d_graph(2, 2)  # 5x5 grid

        # # print the adjacency list
        # for line in nx.generate_adjlist(G):
        #     print(line)

        # # write edgelist to grid.edgelist
        # # nx.write_edgelist(G, path="grid.edgelist", delimiter=":")

        # # write edgelist to grid.edgelist
        # nx.write_edgelist(G, path="grid.edgelist", delimiter=":")
        # # read edgelist from grid.edgelist
        # H = nx.read_edgelist(path="grid.edgelist", delimiter=":")

        # nx.draw(H)
        # plt.show()


        import matplotlib.pyplot as plt
        import networkx as nx

        hd = "H" + chr(252) + "sker D" + chr(252)
        mh = "Mot" + chr(246) + "rhead"
        mc = "M" + chr(246) + "tley Cr" + chr(252) + "e"
        st = "Sp" + chr(305) + "n" + chr(776) + "al Tap"
        q = "Queensr" + chr(255) + "che"
        boc = "Blue " + chr(214) + "yster Cult"
        dt = "Deatht" + chr(246) + "ngue"

        G = nx.Graph()
        G.add_edge(hd, mh)
        G.add_edge(mc, st)
        G.add_edge(boc, mc)
        G.add_edge(boc, dt)
        G.add_edge(st, dt)
        G.add_edge(q, st)
        G.add_edge(dt, mh)
        G.add_edge(st, mh)

        # # write in UTF-8 encoding
        # fh = open("edgelist.utf-8", "wb")
        # nx.write_multiline_adjlist(G, fh, delimiter="\t", encoding="utf-8")

        # # read and store in UTF-8
        # fh = open("edgelist.utf-8", "rb")
        # H = nx.read_multiline_adjlist(fh, delimiter="\t", encoding="utf-8")

        # for n in G.nodes():
        #     if n not in H:
        #         print(False)

        # print(list(G.nodes()))

        # # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
        # pos = nx.spring_layout(G)

        # # now plot all
        # coords = [*pos.values()]

        # for coord in coords:
        #     p = Point3d(scale=0.025,
        #                 pos=Vec3(coord[0], coord[1], 0.))



        # # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
        # edges_list = [e for e in G.edges]

        # for edge in edges_list:
        #     point1 = pos[edge[0]]
        #     point2 = pos[edge[1]]

        #     # plot a line between point1 and point2

        #     edgeline = Line1dSolid()
        #     edgeline.setTailPoint(Vec3(point1[0], point1[1], 0.))
        #     edgeline.setTipPoint(Vec3(point2[0], point2[1], 0.))


        # nx.draw(G, pos, font_size=16, with_labels=False)
        # for p in pos:  # raise text positions
        #     pos[p][1] += 0.07
        # nx.draw_networkx_labels(G, pos)
        # plt.show()

        # g = Graph()
        # g.plot()

        dg = DraggableGraph(ob)
        gh = GraphHoverer(dg, ob)
        # dg.plot()
        print("hi")



app = MyApp()
app.run()
