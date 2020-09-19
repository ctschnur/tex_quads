from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain, Point3dCursor
from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle, Fixed2dLabel
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
from plot_utils.graphplayer import GraphPlayer


from simple_objects.simple_objects import Pinned2dLabel

from interactive_tools import cameraray


class EdgeHoverer:
    """ give it a line, it will register the necessary hover event and on each
        mouse shift recalculate the new situation,
        i.e. either show a connecting line or not. """

    def __init__(self, edge_player, cameragear):
        # register event for onmousemove
        self.edge_player = edge_player
        self.cameragear = cameragear
        # self.mouse = mouse

        taskMgr.add(self.mouseMoverTask, 'mouseMoverTask')
        # base.accept('mouse1', self.onPress)

        self.hoverindicatorpoint = Point3d()

        # self.c1point = Point3d()
        # self.c2point = Point3d()

        self.shortest_distance_line = Line1dSolid(thickness=5, color=Vec4(1., 0., 1., 0.5))

        self.init_time_label()

    def mouseMoverTask(self, task):
        self.render_hints()
        return task.cont

    # def onPress(self):
    #     self.render_hints()
    #     print("onPress")

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


            # self.edge_player.line = None
            d_min = float('inf')

                        # for edge in self.draggablegraph.graph_edges:


            # -- check if this line qualifies to render a hover cursor
            # # find closest line (infinite straight)
            # r2 = edge.getTailPoint()
            r2 = self.edge_player.v1
            edge_p1 = r2
            # edge_p2 = edge.getTipPoint()
            edge_p2 = self.edge_player.v2

            e2 = edge_p2 - edge_p1  # direction vector for edge infinite straight line

            d = np.abs(math_utils.shortestDistanceBetweenTwoStraightInfiniteLines(r1, r2, e1, e2))
            c1, c2 = math_utils.getPointsOfShortestDistanceBetweenTwoStraightInfiniteLines(
                r1, r2, e1, e2)

            # only count this edge if the vector of shortest edge_length lies in-between the
            # start and end points of the line
            # if d is not None:
            # if d_min is None:
            #     d_min = d
            # if self.edge_player.line is None:
            #     self.edge_player.line = edge
            # if c1_min is None:
            # c1_min = c1
            # if c2_min is None:
            # c2_min = c2

            # conditions for closest edge
            # -    d < d_min
            # -    the line segment of shortest edge_length touches the edge's line within the
            #      two node points of the edge:
            #

            Line1dSolid.setTipPoint
            if (  # d < d_min and
                math_utils.isPointBetweenTwoPoints(edge_p1, edge_p2, c1)):

                self.shortest_distance_line.setTipPoint(math_utils.np_to_p3d_Vec3(c1))
                self.shortest_distance_line.setTailPoint(math_utils.np_to_p3d_Vec3(c2))
                self.shortest_distance_line.nodePath.show()

                # -- set the time label
                # ---- set the position of the label to the position of the mouse cursor,
                #      but a bit higher
                self.time_label.textNodePath.show()
                self.time_label.setPos(*(ray_aufpunkt + ray_direction * 1.))

                # figure out the parameter t
                t = (
                    np.linalg.norm(
                        self.edge_player.line.getTailPoint() - math_utils.np_to_p3d_Vec3(c2)) /
                    np.linalg.norm(
                        self.edge_player.line.getTailPoint() - self.edge_player.line.getTipPoint()))

                # print("t = np.linalg.norm(self.edge_player.line.getTailPoint() - math_utils.np_to_p3d_Vec3(c2))/np.linalg.norm(self.edge_player.line.getTailPoint() - self.edge_player.line.getTipPoint())")
                # print(t, "np.linalg.norm(", self.edge_player.line.getTailPoint(), " - ", math_utils.np_to_p3d_Vec3(c2), ")/, np.linalg.norm(", self.edge_player.line.getTailPoint(), " - ", self.edge_player.line.getTipPoint(), ")")

                self.time_label.setText("t = {0:.2f}".format(t))
                self.time_label.update()
                self.time_label.textNodePath.setScale(0.04)

                # -- color edges

                # on hover, change the color to be
                # darker than otherwise
                primary_color = self.edge_player.get_primary_color()

                darkening_factor = 0.5
                new_rgb_v3 = np.array([
                    primary_color[0][0],
                    primary_color[0][1],
                    primary_color[0][2]]) * darkening_factor
                new_color = ((new_rgb_v3[0], new_rgb_v3[1], new_rgb_v3[2], 1.), 1)

                # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

                # when hovered-over
                self.edge_player.set_primary_color(new_color,
                                                   change_logical_primary_color=False)

                print("### COLOR: ", self.edge_player.line.nodePath.getColor())
                # lighten up the color that they have a bit
            else:
                self.shortest_distance_line.setColor(((1., 1., 1., 1.), 1))  # when not hovered-over

                self.edge_player.set_primary_color(self.edge_player.get_primary_color())

                # self.edge_player.p1.setColor(((1., 1., 1., 1.), 1))  # when not hovered-over
                # self.edge_player.p1.setColor(((1., 1., 1., 1.), 1))  # when not hovered-over

                self.shortest_distance_line.nodePath.hide()
                self.time_label.textNodePath.hide()

            self.hoverindicatorpoint.nodePath.setPos(
                math_utils.np_to_p3d_Vec3(ray_aufpunkt + ray_direction * 1.))

            # -- color point
            # ---- find closest point,
            # within a certain radius

            d_min_point = None
            closestpoint = None

            playerline_limiting_points = [self.edge_player.p1, self.edge_player.p2]

            for point in playerline_limiting_points:
                d = np.linalg.norm(
                    math_utils.p3d_to_np(point.getPos())
                    - math_utils.p3d_to_np(ray_aufpunkt))

                if d_min_point is not None:
                    if d < d_min_point:
                        d_min_point = d
                        closestpoint = point
                else:
                    d_min_point = d
                    closestpoint = point

            # ---- color in point
            for point in playerline_limiting_points:
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
