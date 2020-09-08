from interactive_tools.dragging_and_dropping import PickableObjectManager, PickablePoint, Dragger, PickablePoint, CollisionPicker, DragAndDropObjectsManager

from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle

from local_utils import math_utils

from simple_objects.simple_objects import Line1dSolid, PointPrimitive, Fixed2dLabel
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

from simple_objects.simple_objects import Pinned2dLabel

from interactive_tools import cameraray

from functools import partial


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
            p = Point3d(
                pos=Vec3(coord[0], coord[1], 0.),
                scale=0.025)
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


class GraphEdge(Vector):
    """ when dragging a graph node, the graph edge also needs to update, so you need to know it's associated logical graph nodes """
    def __init__(self, nx_graph, nx_graph_edge, point1_vec3, point2_vec3):
        self.nx_graph = nx_graph
        self.nx_graph_edge = nx_graph_edge

        # plot a line between point1 and point2
        Vector.__init__(self, tail_point_logical=point1_vec3, tip_point_logical=point2_vec3)
        # self.setTailPoint(point1_vec3)
        # self.setTipPoint(point2_vec3)


class DraggableGraph(Graph):
    def __init__(self, camera_gear):
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
        self.collisionPicker = CollisionPicker(
            self.camera_gear, render, base.mouseWatcherNode, base, self.dragAndDropObjectsManager)

        # -- add a mouse task to check for picking
        self.p3d_direct_object = DirectObject.DirectObject()
        self.p3d_direct_object.accept('mouse1', self.collisionPicker.onMouseTask)

        self.plot()

        self.updateAfterPointCoordsChanged()

        # # -- add the update dragging tasks for each of the PickablePoints' draggers
        # for pp in self.graph_points:
        #     dragger = self.dragAndDropObjectsManager.get_dragger_from_nodePath(pp.nodePath):
        #     dragger.add_on_state_change_function(self.updateAfterPointCoordsChanged)

        # TODO: improve the design by letting DraggableGraph inherit from DragAndDropObjectsManager,
        # it can be easily thought of as holding the dragger objects themselves


    def plot(self):
        # ---- go through the nodes
        for nx_node in (list) (self.logical_graph):
            auto_coord = self.pos[nx_node]  # the coordinate which is automatically generated, i.e. by a layout algorithm

            pt = GraphPickablePoint(self.logical_graph,
                                    nx_node,
                                    self.pickableObjectManager,
                                    pos=Vec3(auto_coord[0], auto_coord[1], 0.))

            pt.nodePath.setScale(*(0.9*np.array([0.02, 0.02, 0.02])))

            pt_dragger = Dragger(pt, self.camera_gear)
            pt_dragger.add_on_state_change_function(sayhi)

            # use 'optional parameters' to store the current value (at 'save time', vs at call time) (elisp is much better at that)
            mylambda = lambda pt=pt: self.updateAfterPointCoordsChanged(dragged_graphpickablepoint=pt)

            pt_dragger.add_on_state_change_function(mylambda)  # will this actually work?

            self.dragAndDropObjectsManager.add_dragger(pt_dragger)

            pt.nodePath.setHpr(90, 0, 0)  # 90 degrees yaw
            # pt.nodePath.showBounds()

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

            # what is happening here is that the
            for ge in self.graph_edges:
                mycond = any([edges_equal_undirected(ge.nx_graph_edge, conn_edge) for conn_edge in connected_edges])
                if mycond:
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

        self.hoverindicatorpoint = Point3d()

        # self.c1point = Point3d()

        # self.c2point = Point3d()

        self.shortest_distance_line = Line1dSolid(thickness=5, color=Vec4(1., 0., 1., 0.5))

        self.initTimeLabel()


    def mouseMoverTask(self, task):
        self.renderHints()
        return task.cont

    def onPress(self):
        self.renderHints()
        print("onPress")

    def renderHints(self):
        """ render various on-hover things:
            - cursors
            - time labels """
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()

            ray_direction, ray_aufpunkt = cameraray.getCameraMouseRay(
                self.cameragear.camera, base.mouseWatcherNode.getMouse())
            r1 = ray_aufpunkt
            e1 = ray_direction


            closestedge = None
            d_min = float('inf')

            # points of shortest distance
            c1_min = None
            c2_min = None

            for edge in self.draggablegraph.graph_edges:
                # find closest line (infinite straight)
                r2 = edge.getTailPoint()
                edge_p1 = r2
                edge_p2 = edge.getTipPoint()

                e2 = edge_p2 - edge_p1  # direction vector for edge infinite straight line

                d = np.abs(math_utils.shortestDistanceBetweenTwoStraightInfiniteLines(r1, r2, e1, e2))
                c1, c2 = math_utils.getPointsOfShortestDistanceBetweenTwoStraightInfiniteLines(
                    r1, r2, e1, e2)

                # only count this edge if the vector of shortest distance lies in-between the
                # start and end points of the line
                # if d is not None:
                # if d_min is None:
                #     d_min = d
                # if closestedge is None:
                #     closestedge = edge
                if c1_min is None:
                    c1_min = c1
                if c2_min is None:
                    c2_min = c2

                # conditions for closest edge
                # -    d < d_min
                # -    the line segment of shortest distance touches the edge's line within the
                #      two node points of the edge:
                #

                if d < d_min and math_utils.isPointBetweenTwoPoints(edge_p1, edge_p2, c1):
                    d_min = d
                    closestedge = edge

                    c1_min = c1
                    c2_min = c2

                    self.shortest_distance_line.setTipPoint(math_utils.np_to_p3d_Vec3(c1))
                    self.shortest_distance_line.setTailPoint(math_utils.np_to_p3d_Vec3(c2))
                    self.shortest_distance_line.nodePath.show()

                    # -- set the time label
                    # ---- set the position of the label to the position of the mouse cursor, but a bit higher
                    if closestedge is not None:
                        self.time_label.textNodePath.show()
                        self.time_label.setPos(*(ray_aufpunkt + ray_direction * 1.))

                        # figure out the parameter t
                        t = np.linalg.norm(closestedge.getTailPoint() - math_utils.np_to_p3d_Vec3(c2))/np.linalg.norm(closestedge.getTailPoint() - closestedge.getTipPoint())

                        # print("t = np.linalg.norm(closestedge.getTailPoint() - math_utils.np_to_p3d_Vec3(c2))/np.linalg.norm(closestedge.getTailPoint() - closestedge.getTipPoint())")
                        # print(t, "np.linalg.norm(", closestedge.getTailPoint(), " - ", math_utils.np_to_p3d_Vec3(c2), ")/, np.linalg.norm(", closestedge.getTailPoint(), " - ", closestedge.getTipPoint(), ")")

                        self.time_label.setText("t = {0:.2f}".format(t))
                        self.time_label.update()
                        self.time_label.textNodePath.setScale(0.04)

                    else:
                        self.time_label.textNodePath.hide()

            # -- color edges
            if closestedge is not None:
                for edge in self.draggablegraph.graph_edges:
                    # color all
                    edge.setColor((1., 1., 1., 1.), 1)
                    if edge is closestedge:
                        edge.setColor((1., 0., 0., 1.), 1)
            else:
                # hide the connection line
                self.shortest_distance_line.nodePath.hide()

                # make all the same color
                for edge in self.draggablegraph.graph_edges:
                    edge.setColor((1., 1., 1., 1.), 1)

            self.hoverindicatorpoint.nodePath.setPos(math_utils.np_to_p3d_Vec3(
                ray_aufpunkt + ray_direction * 1.))

            # -- color point
            # ---- find closest point,
            # within a certain radius (FIXME: automatically calculate that radius based on the
            # sorroundings)

            d_min_point = None
            closestpoint = None
            for point in self.draggablegraph.graph_points:
                d = np.linalg.norm(math_utils.p3d_to_np(point.getPos())
                                   - math_utils.p3d_to_np(ray_aufpunkt))
                if d_min_point is not None:
                    if d < d_min_point:
                        d_min_point = d
                        closestpoint = point
                else:
                    d_min_point = d
                    closestpoint = point

            # ---- color in point
            for point in self.draggablegraph.graph_points:
                point.nodePath.setColor((1., 0., 1., 1.), 1)

                if point is closestpoint:
                    point.nodePath.setColor((1., 0., 0., 1.), 1)
                else:
                    point.nodePath.setColor((1., 1., 1., 1.), 1)

    def initTimeLabel(self):
        """ show a text label at the position of the cursor:
            - set an event to trigger updating of the text on-hover
            - check if the active edge has changed """

        # init the textNode (there is one text node)
        pos_rel_to_world_x = Point3(1., 0., 0.)

        self.time_label = Pinned2dLabel(refpoint3d=pos_rel_to_world_x, text="mytext",
                                        xshift=0.02, yshift=0.02, font="fonts/arial.egg")

        self.time_label.textNode.setTransform(
            math_utils.math_convention_to_p3d_mat4(math_utils.getScalingMatrix4x4(0.5, 0.5, 0.5)))


class GraphPlayer:
    """
        - Plot a play/pause text and toggle it with space
        - give it a graph and call playfrom(edge, t between 0 and 1).
        - Show a cursor (thicker, smaller)
    """

    def __init__(self, draggablegraph, cameragear):
        self.play_p = True  # play is true, pause is false

        # register event for onmousemove
        self.draggablegraph = draggablegraph
        self.cameragear = cameragear
        # self.mouse = mouse

        # taskMgr.add(self.mouseMoverTask, 'mouseMoverTask')
        # base.accept('mouse1', self.onPress)

        # self.hoverindicatorpoint = Point3d()

        # self.shortest_distance_line = Line1dSolid(thickness=5, color=Vec4(1., 0., 1., 0.5))

        self.initPlayPauseLabel()

    def toggle_play_pause(self, val=None):
        """ toggle or set the play/pause state, val=True for play, False for pause """

        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
        if val is None:
            val = self.play_p

        if val is True:
            self.play_p = False
            self.play_pause_label.setText("pause")
        elif val is False:
            self.play_p = True
            self.play_pause_label.setText("play")
        else:
            print("Error: play_p has invalid value")

        # self.time_label.setText("t = {0:.2f}".format(t))

    def initPlayPauseLabel(self):
        """ show a text label at the side of the screen
            - set an event to trigger play/pause of the text on pressing p
        """
        # init the textNode (there is one text node)
        self.play_pause_label = (
            Fixed2dLabel(text="play", font="fonts/arial.egg", xshift=0.1, yshift=0.1))

        # self.play_pause_label.textNode.setTransform(
        #     math_utils.math_convention_to_p3d_mat4(math_utils.getScalingMatrix4x4(0.5, 0.5, 0.5)))

        # register space key to toggle play/pause
        myDirectObject = DirectObject.DirectObject()
        myDirectObject.accept('space', self.toggle_play_pause)

    # def mouseMoverTask(self, task):
    #     self.renderHints()
    #     return task.cont

    # def onPress(self):
    #     self.renderHints()
    #     print("onPress")

    def renderCursor(self):
        """ render:
            - cursor of current time (disk perpendicular to edge)
            - current time label """

        r1 = ray_aufpunkt
        e1 = ray_direction

        closestedge = None
        d_min = float('inf')

        # points of shortest distance
        c1_min = None
        c2_min = None

        for edge in self.draggablegraph.graph_edges:
            # find closest line (infinite straight)
            r2 = edge.getTailPoint()
            edge_p1 = r2
            edge_p2 = edge.getTipPoint()

            e2 = edge_p2 - edge_p1  # direction vector for edge infinite straight line

            d = np.abs(math_utils.shortestDistanceBetweenTwoStraightInfiniteLines(r1, r2, e1, e2))
            c1, c2 = math_utils.getPointsOfShortestDistanceBetweenTwoStraightInfiniteLines(
                r1, r2, e1, e2)

            # only count this edge if the vector of shortest distance lies in-between the
            # start and end points of the line
            # if d is not None:
            # if d_min is None:
            #     d_min = d
            # if closestedge is None:
            #     closestedge = edge
            if c1_min is None:
                c1_min = c1
            if c2_min is None:
                c2_min = c2

            # conditions for closest edge
            # -    d < d_min
            # -    the line segment of shortest distance touches the edge's line within the
            #      two node points of the edge:
            #

            if d < d_min and math_utils.isPointBetweenTwoPoints(edge_p1, edge_p2, c1):
                d_min = d
                closestedge = edge

                c1_min = c1
                c2_min = c2

                self.shortest_distance_line.setTipPoint(math_utils.np_to_p3d_Vec3(c1))
                self.shortest_distance_line.setTailPoint(math_utils.np_to_p3d_Vec3(c2))
                self.shortest_distance_line.nodePath.show()

                # -- set the time label
                # ---- set the position of the label to the position of the mouse cursor, but a bit higher
                if closestedge is not None:
                    self.time_label.textNodePath.show()
                    self.time_label.setPos(*(ray_aufpunkt + ray_direction * 1.))

                    # figure out the parameter t
                    t = np.linalg.norm(closestedge.getTailPoint() - math_utils.np_to_p3d_Vec3(c2))/np.linalg.norm(closestedge.getTailPoint() - closestedge.getTipPoint())

                    # print("t = np.linalg.norm(closestedge.getTailPoint() - math_utils.np_to_p3d_Vec3(c2))/np.linalg.norm(closestedge.getTailPoint() - closestedge.getTipPoint())")
                    # print(t, "np.linalg.norm(", closestedge.getTailPoint(), " - ", math_utils.np_to_p3d_Vec3(c2), ")/, np.linalg.norm(", closestedge.getTailPoint(), " - ", closestedge.getTipPoint(), ")")

                    self.time_label.setText("t = {0:.2f}".format(t))
                    self.time_label.update()
                    self.time_label.textNodePath.setScale(0.04)

                else:
                    self.time_label.textNodePath.hide()

        # -- color edges
        if closestedge is not None:
            for edge in self.draggablegraph.graph_edges:
                # color all
                edge.setColor((1., 1., 1., 1.), 1)
                if edge is closestedge:
                    edge.setColor((1., 0., 0., 1.), 1)
        else:
            # hide the connection line
            self.shortest_distance_line.nodePath.hide()

            # make all the same color
            for edge in self.draggablegraph.graph_edges:
                edge.setColor((1., 1., 1., 1.), 1)

        self.hoverindicatorpoint.nodePath.setPos(math_utils.np_to_p3d_Vec3(
            ray_aufpunkt + ray_direction * 1.))

        # -- color point
        # ---- find closest point,
        # within a certain radius (FIXME: automatically calculate that radius based on the
        # sorroundings)

        d_min_point = None
        closestpoint = None
        for point in self.draggablegraph.graph_points:
            d = np.linalg.norm(math_utils.p3d_to_np(point.getPos())
                               - math_utils.p3d_to_np(ray_aufpunkt))
            if d_min_point is not None:
                if d < d_min_point:
                    d_min_point = d
                    closestpoint = point
            else:
                d_min_point = d
                closestpoint = point

        # ---- color in point
        for point in self.draggablegraph.graph_points:
            point.nodePath.setColor((1., 0., 1., 1.), 1)

            if point is closestpoint:
                point.nodePath.setColor((1., 0., 0., 1.), 1)
            else:
                point.nodePath.setColor((1., 1., 1., 1.), 1)

    def initTimeLabel(self):
        """ show a text label at the position of the cursor:
            - set an event to trigger updating of the text on-hover
            - check if the active edge has changed """

        # init the textNode (there is one text node)
        pos_rel_to_world_x = Point3(1., 0., 0.)

        self.time_label = Pinned2dLabel(refpoint3d=pos_rel_to_world_x, text="mytext",
                                        xshift=0.02, yshift=0.02, font="fonts/arial.egg")

        self.time_label.textNode.setTransform(
            math_utils.math_convention_to_p3d_mat4(math_utils.getScalingMatrix4x4(0.5, 0.5, 0.5)))
