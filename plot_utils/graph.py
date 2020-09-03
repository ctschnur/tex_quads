from interactive_tools.dragging_and_dropping import PickableObjectManager, PickablePoint, Dragger, PickablePoint, CollisionPicker, DragAndDropObjectsManager

from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle

from local_utils import math_utils

from simple_objects.simple_objects import Line1dSolid, PointPrimitive
from composed_objects.composed_objects import Vector

from simple_objects.custom_geometry import create_Triangle_Mesh_From_Vertices_and_Indices, createCircle, createColoredUnitQuadGeomNode

from simple_objects.primitives import ParametricLinePrimitive
from panda3d.core import Vec3, Mat4, Vec4

import numpy as np
import scipy.special

import glm

from direct.showbase.ShowBase import ShowBase, DirectObject

from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight

import networkx as nx

def sayhi():
    print("heylo ------- ######")


def edges_equal_undirected(nx_graph_edge_tuple_1, nx_graph_edge_tuple_2):
    """ even in undirected graphs, edges are represented by tuples in nx, not by sets """
    e1 = nx_graph_edge_tuple_1
    e2 = nx_graph_edge_tuple_2

    return ((e1[0] == e2[0]) and (e1[1] == e2[1])) or ((e1[0] == e2[1]) and (e1[1] == e2[0]))

class Graph:
    # a graph, logically is a set of nodes and a set of edges, which are sets of nodes
    # it can be directed, then the sets of nodes are tuples
    # here, we make a directed graph, with the fastest way back to the root

    def __init__(self# , # P_arr
    ):
        self.logical_graph = nx.Graph()
        hd = "H" + chr(252) + "sker D" + chr(252)
        mh = "Mot" + chr(246) + "rhead"
        mc = "M" + chr(246) + "tley Cr" + chr(252) + "e"
        st = "Sp" + chr(305) + "n" + chr(776) + "al Tap"
        q = "Queensr" + chr(255) + "che"
        boc = "Blue " + chr(214) + "yster Cult"
        dt = "Deatht" + chr(246) + "ngue"

        self.logical_graph.add_edge(hd, mh)
        self.logical_graph.add_edge(mc, st)
        self.logical_graph.add_edge(boc, mc)
        self.logical_graph.add_edge(boc, dt)
        self.logical_graph.add_edge(st, dt)
        self.logical_graph.add_edge(q, st)
        self.logical_graph.add_edge(dt, mh)
        self.logical_graph.add_edge(st, mh)

        # print(list(self.logical_graph.nodes()))

        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
        self.pos = nx.spring_layout(self.logical_graph)

        # get all their coordinates, and draw them

        self.coords = [*self.pos.values()]

        self.graph_points = []

        # get all the edges and draw them
        self.edges_list = [e for e in self.logical_graph.edges]

        self.graph_edges = []

        # -----------------

        # self.graph_points=P_arr

        # self.beziercurve=ParametricLinePrimitive(
        #     lambda t:
        #     np.array([
        #         Graph.calcGraph(t, self.graph_points)[0],
        #         Graph.calcGraph(t, self.graph_points)[1],
        #         Graph.calcGraph(t, self.graph_points)[2]
        #     ]),
        #     param_interv=np.array([0, 1]),
        #     thickness=1.,
        #     color=Vec4(1., 1., 0., 1.))


    def plot(self):
        # nodes
        for coord in self.coords:
            p = Point3d(pos=Vec3(
                coord[0], coord[1], 0.
            ), scale=0.025)

            self.graph_points.append(p)

        # edges
        for edge in self.edges_list:
            point1 = self.pos[edge[0]]
            point2 = self.pos[edge[1]]

            # plot a line between point1 and point2
            edgeline = Line1dSolid()
            edgeline.setTailPoint(Vec3(point1[0], point1[1], 0.))
            edgeline.setTipPoint(Vec3(point2[0], point2[1], 0.))

    # @staticmethod
    # def calcGraph(t, P_arr):
    #     _sum = 0
    #     n = len(P_arr) - 1

    #     assert len(P_arr) >= 2  # at least a linear bezier curve
    #     assert t >= 0. and t <= 1.

    #     for i, P_i in enumerate(P_arr):
    #         _sum += (scipy.special.comb(n, i)
    #                  * (1. - t)**(n - np.float(i))
    #                  * t**np.float(i)
    #                  * P_i)
    #     return _sum

class GraphPoint:
    """ when a graphical graph node is dragged, you need to know it's associated logical graph node,
    in order to update the graphics of the edges appropriately """

    def __init__(self, nx_graph, nx_graph_node):
        self.nx_graph = nx_graph
        self.nx_graph_node = nx_graph_node


class GraphPickablePoint(GraphPoint, PickablePoint):
    def __init__(self, nx_graph, nx_graph_node, pickableObjectManager, pos):
        GraphPoint.__init__(self, nx_graph, nx_graph_node)
        PickablePoint.__init__(self, pickableObjectManager, pos=pos)


class GraphEdge(Line1dSolid):
    """ when dragging a graph node, the graph edge also needs to update, so you need to know it's associated logical graph nodes """
    def __init__(self, nx_graph, nx_graph_edge, point1_vec3, point2_vec3):
        self.nx_graph = nx_graph
        self.nx_graph_edge = nx_graph_edge

        # plot a line between point1 and point2
        Line1dSolid.__init__(self)
        self.setTailPoint(point1_vec3)
        self.setTipPoint(point2_vec3)


class DraggableGraph(Graph):
    def __init__(self,
                 camera_gear):

        Graph.__init__(self)

        self.camera_gear = camera_gear
        # self.camera_gear.set_view_to_yz_plane()

        # --- plot draggable bezier curve together with points
        # for dragging the points and updating the bezier curve,
        # the points have to stay instantiated (objects that are dragged), while the bezier curve
        # can be regenerated from the new point positions at every drag event

        # -- add picking utilities
        self.pickableObjectManager = PickableObjectManager()
        self.dragAndDropObjectsManager = DragAndDropObjectsManager()
        self.collisionPicker = CollisionPicker(self.camera_gear, render, base.mouseWatcherNode, base, self.dragAndDropObjectsManager)

        # -- add a mouse task to check for picking
        self.p3d_direct_object = DirectObject.DirectObject()
        self.p3d_direct_object.accept('mouse1', self.collisionPicker.onMouseTask)


        # # -- add a line betwen each set of 2 pickablepoints (like in inkscape)
        # # ---- with only 4 pickablepoints, assign a line to the fist 2 and the last 2
        # self.l1 = Line1dSolid(thickness=1., color=Vec4(1,0,1,1))
        # self.l2 = Line1dSolid(thickness=1., color=Vec4(1,0,1,1))
        # # l1.setPos(Vec3(0., 0., 0.))
        # # l1.setTipPoint(Vec3(0., 0., 0.))

        self.plot()

        self.updateAfterPointCoordsChanged()


        # # -- add the update dragging tasks for each of the PickablePoints' draggers
        # for pp in self.graph_points:
        #     dragger = self.dragAndDropObjectsManager.get_dragger_from_nodePath(pp.nodePath):
        #     dragger.add_on_state_change_function(self.updateAfterPointCoordsChanged)

        # TODO: improve the design by letting DraggableGraph inherit from DragAndDropObjectsManager,
        # it can be easily thought of as holding the dragger objects themselves


    def plot(self):
        from functools import partial

        # # nodes
        # for coord in self.coords:
        #     p = Point3d(pos=Vec3(
        #         coord[0], coord[1], 0.
        #     ), scale=0.025)

        #     self.graph_points.append(p)

        # ---- go through the nodes
        for nx_node in (list) (self.logical_graph):
            # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

            auto_coord = self.pos[nx_node]  # the coordinate which is automatically generated, i.e. by a layout algorithm

            pt = GraphPickablePoint(self.logical_graph,
                                    nx_node,
                                    self.pickableObjectManager,
                                    pos=Vec3(auto_coord[0], auto_coord[1], 0.))

            pt_dragger = Dragger(pt, self.camera_gear)
            pt_dragger.add_on_state_change_function(sayhi)

            # use 'optional parameters' to store the current value (at 'save time', vs at call time) (elisp is much better at that)
            mylambda = lambda pt=pt: self.updateAfterPointCoordsChanged(dragged_graphpickablepoint=pt)

            pt_dragger.add_on_state_change_function(mylambda)  # will this actually work?

            self.dragAndDropObjectsManager.add_dragger(pt_dragger)

            pt.nodePath.setHpr(90, 0, 0)  # 90 degrees yaw
            pt.nodePath.showBounds()

            self.graph_points.append(pt)

        # edges
        for edge in self.edges_list:
            point1 = self.pos[edge[0]]
            point2 = self.pos[edge[1]]

            e = GraphEdge(self.logical_graph,
                          edge,
                          Vec3(point1[0], point1[1], 0.),
                          Vec3(point2[0], point2[1], 0.))

            self.graph_edges.append(e)



    def updateAfterPointCoordsChanged(self, dragged_graphpickablepoint=None):
        """ once a PickablePoint has been dragged, you need to update it's edges """

        # first of all find the dragged object (PickablePoint)
        # self.dragAndDropObjectsManager.get_dragger_from_nodePath()
        if dragged_graphpickablepoint:
            connected_edges = (list) (self.logical_graph.edges([dragged_graphpickablepoint.nx_graph_node]))

            # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
            # what is happening here is that the

            for ge in self.graph_edges:
                mycond = any([edges_equal_undirected(ge.nx_graph_edge, conn_edge) for conn_edge in connected_edges])
                if mycond:
                    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
                    # find out which node is the dragged node, number 1 or number 2

                    dp_pos = dragged_graphpickablepoint.getPos()  # new position of dragged point
                    if dragged_graphpickablepoint.nx_graph_node == ge.nx_graph_edge[0]:
                        print(dragged_graphpickablepoint.nx_graph_node, " is node 1 of ", ge.nx_graph_edge)
                        ge.setTailPoint(dp_pos)
                    else:
                        print(dragged_graphpickablepoint.nx_graph_node, " is node 2 of ", ge.nx_graph_edge)
                        ge.setTipPoint(dp_pos)

        # extract the new coordinates from the pickable points
        new_point_coords = []
        for pp in self.graph_points:
            new_point_coords.append(pp.getPos())

        self.coords = new_point_coords


from interactive_tools import cameraray

class GraphHoverer:
    """ give it a graph, it will register the necessary hover event and on each
        mouse shift recalculate the new situation, i.e. go through all lines, find the nearest one
        and plot a connecting line """

    def __init__(self, draggablegraph, cameragear):
        # register event for onmousemove
        self.draggablegraph = draggablegraph
        self.cameragear = cameragear
        # self.mouse = mouse

        taskMgr.add(self.mouseMoverTask, 'mouseMoverTask')
        base.accept('mouse1', self.onPress)

        print("graphhoverer")

        self.hoverindicatorpoint = Point3d()

    def mouseMoverTask(self, task):
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()

            ray_direction, ray_aufpunkt = cameraray.getCameraMouseRay(
                self.cameragear.camera, base.mouseWatcherNode.getMouse())
            r1 = ray_aufpunkt
            e1 = ray_direction


            closestedge = None
            d_min = None
            for edge in self.draggablegraph.graph_edges:

                # find closest line (infinite straight)
                r2 = edge.getTailPoint()
                e2 = edge.getTipPoint() - edge.getTailPoint()

                d = np.abs(math_utils.shortestDistanceBetweenTwoStraightInfiniteLines(r1, r2, e1, e2))

                if d is not None:
                    if d_min is None:
                        d_min = d

                    if d < d_min:
                        d_min = d
                        closestedge = edge

                else:
                    d_min = d
                    closestedge = edge

            print("closest edge: ", closestedge)  # TODO: maybe take the absolute value ? is it ever negative?
            print("d_min: ", d_min)

            # color edges
            for edge in self.draggablegraph.graph_edges:
                edge.nodePath.setColor((1., 0., 1., 1.), 1)

                if edge is closestedge:
                    edge.nodePath.setColor((1., 0., 0., 1.), 1)
                else:
                    edge.nodePath.setColor((1., 1., 1., 1.), 1)

            self.hoverindicatorpoint.setPos(ray_aufpunkt + ray_direction * 1.)

            # color point
            # find closest point
            d_min_point = None
            closestpoint = None
            for point in self.draggablegraph.graph_points:
                d = np.linalg.norm(math_utils.p3d_to_np(point.getPos())
                                   - math_utils.p3d_to_np(ray_aufpunkt))
                # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
                if d_min_point is not None:
                    if d < d_min_point:
                        d_min_point = d
                        closestpoint = point
                else:
                    d_min_point = d
                    closestpoint = point

            print("closest point: ", closestpoint.getPos())


            # color point
            for point in self.draggablegraph.graph_points:
                point.nodePath.setColor((1., 0., 1., 1.), 1)

                if point is closestpoint:
                    point.nodePath.setColor((1., 0., 0., 1.), 1)
                else:
                    point.nodePath.setColor((1., 1., 1., 1.), 1)



            # draw connection line of length d to the intersection with the edge

            print("onHover")

        return task.cont

    def onPress(self):
        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
        for edge in self.draggablegraph.graph_edges:
            edge.nodePath.setColor((1., 0., 1., 1.), 1)

        print("onPress")
