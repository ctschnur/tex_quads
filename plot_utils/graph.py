from interactive_tools.dragging_and_dropping import PickableObjectManager, PickablePoint, Dragger, PickablePoint, CollisionPicker, DragAndDropObjectsManager

from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle

from composed_objects.composed_objects import Point3dCursor

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

from plot_utils.edgehoverer import EdgeHoverer, EdgeMouseClicker


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

        self.init_time_label()

    def mouseMoverTask(self, task):
        self.render_hints()
        return task.cont

    def onPress(self):
        self.render_hints()
        print("onPress")

    def render_hints(self):
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

            # points of shortest edge_length
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

                # only count this edge if the vector of shortest edge_length lies in-between the
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
                # -    the line segment of shortest edge_length touches the edge's line within the
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
                    edge.setColor(((1., 1., 1., 1.), 1))
                    if edge is closestedge:
                        edge.setColor(((1., 0., 0., 1.), 1))
            else:
                # hide the connection line
                self.shortest_distance_line.nodePath.hide()

                # make all the same color
                for edge in self.draggablegraph.graph_edges:
                    edge.setColor(((1., 1., 1., 1.), 1))

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

    def init_time_label(self):
        """ show a text label at the position of the cursor:
            - set an event to trigger updating of the text on-hover
            - check if the active edge has changed """

        # init the textNode (there is one text node)
        pos_rel_to_world_x = Point3(1., 0., 0.)

        self.time_label = Pinned2dLabel(refpoint3d=pos_rel_to_world_x, text="mytext",
                                        xshift=0.02, yshift=0.02, font="fonts/arial.egg")

        self.time_label.textNode.setTransform(
            math_utils.math_convention_to_p3d_mat4(math_utils.getScalingMatrix4x4(0.5, 0.5, 0.5)))






from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval


class EdgePlayerState:
    """ You have an edge, and the states are
        1. stopped at beginning
        2. playing
        3. paused
        4. stopped at end
    This class is just for checking and changing the state.
    TODO: A class derived from EdgePlayerState will call it's functions and
    add the specific sequence commands after executing the state change functions. """
    def __init__(self):
        # TODO: set predefined initial state
        self.set_stopped_at_beginning()


    def set_stopped_at_beginning(self):
        self.a = 0.
        self.stopped = True
        self.paused = False  # undefined

    def is_stopped_at_beginning(self):
        return (self.a == 0. and self.stopped == True
                # self.paused = False  # undefined
        )


    def set_stopped_at_end(self):
        self.a = 1.
        self.stopped = True
        self.paused = False  # undefined

    def is_stopped_at_end(self):
        return (self.a == 1. and self.stopped == True
                # self.paused = False  # undefined
        )


    def set_playing(self, a_to_start_from=None):
        if a_to_start_from is None:
            a_to_start_from = self.a

        assert (a_to_start_from >= 0. and a_to_start_from <= 1.)
        self.a = a_to_start_from

        self.stopped = False
        self.paused = False

    def is_playing(self):
        return (self.a >= 0. and self.a <= 1. and self.stopped == False and self.paused == False)


    def set_paused(self, a_to_set_paused_at=None):
        if a_to_set_paused_at is None:
            a_to_set_paused_at = self.a

        assert (a_to_set_paused_at >= 0. and a_to_set_paused_at <= 1.)
        self.a = a_to_set_paused_at

        self.stopped = False  # in a stopped state, you can't pause
        self.paused = True


    def is_paused(self):
        return (self.a >= 0. and self.a <= 1. and self.stopped == False and self.paused == True)

    def __repr__(self):
        # return '{name:'+self.name+', age:'+str(self.age)+ '}'
        return "{a: " + str(self.a) + ", stopped: " + str(self.stopped) + ", paused: " + str(self.paused) + " }"



class EdgePlayer(EdgePlayerState):
    """ Adds the graphics and the p3d sequence operations to the logic of EdgePlayerState """

    stopped_at_beginning_primary_color = ((1., 0., 0., 1.), 1)
    stopped_at_beginning_cursor_color = ((1., 0., 0., 1.), 1)
    stopped_at_beginning_line_color = ((1., 0., 0., 1.), 1)  # this is only set, if the line (edge) is 'engaged' (at a node, multiple edges diverge)

    stopped_at_end_primary_color = ((1., .5, 0., 1.), 1)
    stopped_at_end_cursor_color = ((1., .5, 0., 1.), 1)
    stopped_at_end_line_color = ((1., .5, 0., 1.), 1)  # this is only set, if the line (edge) is 'engaged' (at a node, multiple edges diverge)

    playing_primary_color = ((.5, .5, 0., 1.), 1)
    playing_cursor_color = ((.5, .5, 0., 1.), 1)
    playing_line_color = ((.5, .5, 0., 1.), 1)  # this is only set, if the line (edge) is 'engaged' (at a node, multiple edges diverge)

    paused_primary_color = ((0., .5, .5, 1.), 1)
    paused_cursor_color = ((0., .5, .5, 1.), 1)
    paused_line_color = ((0., .5, .5, 1.), 1)  # this is only set, if the line (edge) is 'engaged' (at a node, multiple edges diverge)

    def __init__(self, camera_gear):
        # -- do geometry logic
        self.v1 = Vec3(-.5, -.5, 0.)
        self.v2 = Vec3(-1.5, -1.5, 0.)
        self.v_c = self.v1  # cursor; initially at stopped_at_beginning state
        self.duration = 10.  # a relatively high number
        self.set_short_step = 2.  # in seconds
        # self.a = 0.  # a parameter between 0 and 1   # already gets initialized in the EdgePlayerState
        self.delay = 0.

        # -- do graphics stuff
        self.p1 = Point3d(scale=0.01, pos=self.v1)
        self.p2 = Point3d(scale=0.01, pos=self.v2)

        # self.p_c = Point3d(scale=0.0125, pos=self.v1)

        self.p_c = Point3dCursor(Vec3(0., 0., 0.))

        self.line = Line1dSolid()
        self.line.setTipPoint(self.v1)
        self.line.setTailPoint(self.v2)

        # self.line = Vector()
        # self.line.setTailPoint(self.v1)
        # self.line.setTipPoint(self.v2)

        self.primary_color = None
        self.set_primary_color(self.stopped_at_beginning_primary_color)  # initially

        # setup the spacebar
        self.space_direct_object = DirectObject.DirectObject()
        self.space_direct_object.accept('space', self.react_to_spacebar)

        # setup keys for jumping to beginning/end
        self.set_stopped_at_beginning_direct_object = DirectObject.DirectObject()
        self.set_stopped_at_beginning_direct_object.accept('a', self.react_to_a)

        self.set_stopped_at_end_direct_object = DirectObject.DirectObject()
        self.set_stopped_at_end_direct_object.accept('e', self.react_to_e)

        self.set_short_forward_direct_object = DirectObject.DirectObject()
        self.set_short_forward_direct_object.accept('arrow_right', self.react_to_arrow_right)

        self.set_short_backward_direct_object = DirectObject.DirectObject()
        self.set_short_backward_direct_object.accept('arrow_left', self.react_to_arrow_left)

        self.extraArgs = [# a, # duration,
            self.v1, self.v2, self.v_c, # p1, p2,
            self.p_c]

        # -- do p3d sequence stuff
        # ---- initialize the sequence
        self.p3d_interval = LerpFunc(
            self.update_position_func, duration=self.duration, extraArgs=self.extraArgs)
        self.p3d_cursor_sequence = Sequence(Wait(self.delay), self.p3d_interval,
                                            Func(self.on_finish_cursor_sequence))


        # -- init hover and click actions
        self.camera_gear = camera_gear

        self.edge_hoverer = EdgeHoverer(self, self.camera_gear)

        self.edge_mouse_clicker = EdgeMouseClicker(self)

        EdgePlayerState.__init__(self)


    def update_position_func(self,
                         a, # duration,
                         v1, v2, v_c, # p1, p2,
                         p_c):
        self.a = a
        # assumption: t is a parameter between 0 and self.duration
        v21 = v2 - v1
        # a = t# /self.duration
        v_c = v1 + v21 * a
        # p_c.nodePath.setPos(v_c)
        p_c.setPos(v_c)
        print(# "t = ", t,
              # "; duration = ", duration,
              " a = ", a)


    def react_to_a(self):
        """ unconditionally jump to the beginning and stop """
        self.set_stopped_at_beginning()

    def react_to_e(self):
        """ unconditionally jump to the beginning and stop """
        self.set_stopped_at_end()


    def react_to_spacebar(self):
        """ spacebar will either:
        - start playing from beginning if it's stopped at the beginning
        - start playing from beginning of the next edge if it's stopped at the end (print 'start at next edge')
        - pause if it's playing
        - play if it's paused
        """

        print("before spacebar")
        print("is_stopped_at_beginning(): ", self.is_stopped_at_beginning(), ", ",
              "is_stopped_at_end(): ", self.is_stopped_at_end(), ", ",
              "is_playing(): ", self.is_playing(), ", ",
              "is_paused(): ", self.is_paused())
        print(self)

        if self.is_stopped_at_beginning():
            self.set_playing(a_to_start_from=0.)
        elif self.is_stopped_at_end():
            self.set_playing(a_to_start_from=0., after_finish=True)
            print("start at next edge (if no next edge, start from beginning of last edge)")
        elif self.is_playing():
            self.set_paused()
        elif self.is_paused():
            self.set_playing()
        else:
            print("situation matches no state!")

        print("after spacebar")
        print("is_stopped_at_beginning(): ", self.is_stopped_at_beginning(), ", ",
              "is_stopped_at_end(): ", self.is_stopped_at_end(), ", ",
              "is_playing(): ", self.is_playing(), ", ",
              "is_paused(): ", self.is_paused())
        print(self)


    def react_to_arrow_right(self):
        """ arrow_right will either:
        - if calculated time is smaller than duration: advance to a time and change nothing
        - if calculated time is greater than duration: finish() the sequence and set stopped state
        """

        print("before arrow right")
        # print("is_stopped_at_beginning(): ", self.is_stopped_at_beginning(), ", ",
        #       "is_stopped_at_end(): ", self.is_stopped_at_end(), ", ",
        #       "is_playing(): ", self.is_playing(), ", ",
        #       "is_paused(): ", self.is_paused())
        print(self)

        self.a = self.p3d_cursor_sequence.get_t()/self.duration

        print("self.a: ", self.a,
              "; self.p3d_cursor_sequence.get_t(): ", self.p3d_cursor_sequence.get_t())

        calculated_time = self.a * self.duration + self.set_short_step

        new_a = calculated_time/self.duration
        print("new_a: ", new_a)

        print("; calculated_time: ", calculated_time,
              "; self.a: ", self.a,
              "; self.duration: ", self.duration,
              "; self.set_short_step", self.set_short_step)

        if self.is_stopped_at_beginning():
            # self.set_playing(a_to_start_from=0.)
            self.set_paused(a_to_set_paused_at=new_a)
        elif self.is_stopped_at_end():
            # self.set_playing(a_to_start_from=0., after_finish=True)
            print("do nothing, only consider next edge, if there is one")
        elif self.is_playing():
            print("self.is_playing(): ", self.is_playing())
            if calculated_time < self.duration:
                print("calculated_time < self.duration: ", calculated_time < self.duration)
                self.set_playing(a_to_start_from=new_a)
            else:
                self.set_stopped_at_end()
        elif self.is_paused():
            print("self.is_paused(): ", self.is_paused())
            if calculated_time < self.duration:
                print("calculated_time < self.duration", calculated_time < self.duration)
                # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
                self.set_paused(a_to_set_paused_at=new_a)
            else:
                self.set_stopped_at_end()
        else:
            print("situation matches no state!")

        print("after arrow right")
        # print("is_stopped_at_beginning(): ", self.is_stopped_at_beginning(), ", ",
        #       "is_stopped_at_end(): ", self.is_stopped_at_end(), ", ",
        #       "is_playing(): ", self.is_playing(), ", ",
        #       "is_paused(): ", self.is_paused())
        print(self)



    def react_to_arrow_left(self):
        """ arrow_right will either:
        - if calculated time is smaller than duration: advance to a time and change nothing
        - if calculated time is greater than duration: finish() the sequence and set stopped state
        """

        print("before arrow left")
        # print("is_stopped_at_beginning(): ", self.is_stopped_at_beginning(), ", ",
        #       "is_stopped_at_end(): ", self.is_stopped_at_end(), ", ",
        #       "is_playing(): ", self.is_playing(), ", ",
        #       "is_paused(): ", self.is_paused())
        print(self)

        self.a = self.p3d_cursor_sequence.get_t()/self.duration

        print("self.a: ", self.a,
              "; self.p3d_cursor_sequence.get_t(): ", self.p3d_cursor_sequence.get_t())

        calculated_time = self.a * self.duration - self.set_short_step

        if calculated_time < 0.001:  # clamp it so that you can't skip the node
            # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
            calculated_time = 0.001
            # setting it to exactly 0.0 seems to not work properly (? with the p3d sequence)
        # elif calculated_time < self.set_short_step

        new_a = calculated_time/self.duration
        print("new_a: ", new_a)

        print("; calculated_time: ", calculated_time,
              "; self.a: ", self.a,
              "; self.duration: ", self.duration,
              "; self.set_short_step", self.set_short_step)

        if self.is_stopped_at_beginning():
            # self.set_playing(a_to_start_from=0.)
            # self.set_paused(a_to_set_paused_at=new_a)
            print("stopped at beginning: stepping back only if something precedes")
        elif self.is_stopped_at_end():
            self.set_paused(a_to_set_paused_at=new_a# , after_finish=True
            )
        elif self.is_playing():
            print("self.is_playing(): ", self.is_playing())
            self.set_playing(a_to_start_from=new_a)
        elif self.is_paused():
            print("self.is_paused(): ", self.is_paused())
            self.set_paused(a_to_set_paused_at=new_a)
        else:
            print("situation matches no state!")

        print("after arrow left")
        # print("is_stopped_at_beginning(): ", self.is_stopped_at_beginning(), ", ",
        #       "is_stopped_at_end(): ", self.is_stopped_at_end(), ", ",
        #       "is_playing(): ", self.is_playing(), ", ",
        #       "is_paused(): ", self.is_paused())
        print(self)


    def on_finish_cursor_sequence(self):
        self.set_stopped_at_end()


    def set_stopped_at_beginning(self):
        EdgePlayerState.set_stopped_at_beginning(self)
        # -- do p3d sequence stuff
        # p3d only really has a finish() function, not a 'stopped at start'
        self.p3d_cursor_sequence.pause()
        self.p3d_cursor_sequence.set_t(self.a * self.duration)

        # -- do graphics stuff

        self.set_primary_color(self.stopped_at_beginning_primary_color)


    def set_stopped_at_end(self, # already_at_end=False
    ):
        EdgePlayerState.set_stopped_at_end(self)

        # if already_at_end is False:

        print("stopped at end ", self)

        self.p3d_cursor_sequence.finish()

        # setting pause() is undefined behaviour, if it's already finished.
        # self.p3d_cursor_sequence.pause()
        # self.p3d_cursor_sequence.setT(self.a)
        # print("stopped at end point 2: ", self)
        # else:
        #     print("already_at_end = ", already_at_end, " no need to set T again. ")  # right?

        self.set_primary_color(self.stopped_at_end_primary_color)


    def set_playing(self, a_to_start_from=None, after_finish=False):
        EdgePlayerState.set_playing(self, a_to_start_from=a_to_start_from)

        if a_to_start_from:
            self.p3d_cursor_sequence.set_t(a_to_start_from * self.duration)
            print("a_to_start_from: ", a_to_start_from)

        if after_finish is True:
            # it needs to be restarted at a=0. Usually this is called after the interval has finished once, to restart the Sequence
            print("attempting to restart the sequence after finish", self)
            self.p3d_cursor_sequence.start()
            print("after restart: ", self)
        else:
            # merely resume, since it is already started (standard state)
            self.p3d_cursor_sequence.resume()


        self.set_primary_color(self.playing_primary_color)


    def set_paused(self, a_to_set_paused_at=None):
        EdgePlayerState.set_paused(self, a_to_set_paused_at=a_to_set_paused_at)

        if a_to_set_paused_at:
            self.p3d_cursor_sequence.set_t(a_to_set_paused_at * self.duration)
            print("a_to_set_paused_at: ", a_to_set_paused_at)

        self.p3d_cursor_sequence.pause()

        self.set_primary_color(self.paused_primary_color)


    def set_primary_color(self, primary_color, cursor_color_special=None, line_color_special=None,
                          change_logical_primary_color=True):
        """ A part of the cursor and the line get by default
            the primary color. Optionally, they can be changed individually.

        Args:
            change_logical_primary_color:
               if False, the logical primary_color is not modified, if True, it is.
               This is good for e.g. on-hover short and temporary modifications of the
               primary color. """

        if change_logical_primary_color is True:
            self.primary_color = primary_color

        cursor_color = None
        line_color = None

        if cursor_color_special:
            cursor_color = cursor_color_special
        else:
            cursor_color = primary_color

        if line_color_special:
            line_color = line_color_special
        else:
            line_color = primary_color


        self.p_c.setColor(cursor_color)
        self.line.setColor(line_color)


    def get_primary_color(self):
        return self.primary_color

    def get_state_snapshot(self):
        """ get a snapshot of a state (FIXME?: incomplete information, i.e. not a deep copy of
            the parent class `EdgePlayerState` of the `EdgePlayer`) """
        state_snapshot = {
            "is_stopped_at_beginning": self.is_stopped_at_beginning(),
            "is_stopped_at_end": self.is_stopped_at_end(),
            "is_playing": self.is_playing(),
            "is_paused": self.is_paused(),
            "a": self.a
        }
        return state_snapshot

    def set_state_from_state_snapshot(self, state_snapshot):
        """ state taken from get_state_snapshot """

        a = state_snapshot["a"]

        if state_snapshot["is_stopped_at_beginning"]:
            self.set_stopped_at_beginning()
        elif state_snapshot["is_stopped_at_end"]:
            self.set_stopped_at_end()
        elif state_snapshot["is_playing"]:
            self.set_playing(a_to_start_from=a)
        elif state_snapshot["is_paused"]:
            self.set_paused(a_to_set_paused_at=a)
        else:
            print("snapshot matches no valid state, could not be restored!")
            exit(1)

    # def set_state_from_state_snapshot_to_playing_or_paused(self, state_snapshot):


