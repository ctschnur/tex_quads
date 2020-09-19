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

# from plot_utils.graph import Graph, DraggableGraph, GraphHoverer
# from plot_utils.graphplayer import GraphPlayer


from simple_objects.simple_objects import Pinned2dLabel

from interactive_tools import cameraray


class EdgeHoverer:
    """ give it a line, it will register the necessary hover event and on each
        mouse shift recalculate the new situation,
        i.e. either show a connecting line or not. """

    def __init__(self, edge_player, camera_gear):
        # register event for onmousemove
        self.edge_player = edge_player
        self.camera_gear = camera_gear
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

    def get_hover_points(self):

        mouse_pos = None

        if base.mouseWatcherNode.hasMouse():
            mouse_pos = base.mouseWatcherNode.getMouse()
        else:
            return False, None, None, None, None, None, None

        ray_direction, ray_aufpunkt = cameraray.getCameraMouseRay(
            self.camera_gear.camera, mouse_pos)
        r1 = ray_aufpunkt
        e1 = ray_direction

        # -- check if this line qualifies to render a hover cursor
        r2 = self.edge_player.v1
        edge_p1 = r2
        edge_p2 = self.edge_player.v2
        e2 = edge_p2 - edge_p1  # direction vector for edge infinite straight line
        d = np.abs(math_utils.shortestDistanceBetweenTwoStraightInfiniteLines(r1, r2, e1, e2))
        c1, c2 = math_utils.getPointsOfShortestDistanceBetweenTwoStraightInfiniteLines(
            r1, r2, e1, e2)

        return True, ray_direction, ray_aufpunkt, edge_p1, edge_p2, c1, c2

    def get_a_param(self, c2):
        """
        a is between 0 and 1 and represents a time if multiplied by the duration.
        FIXME: replace getTail/TipPoints with other stuff. """
        t = 1. - (
            np.linalg.norm(
                self.edge_player.line.getTailPoint() - math_utils.np_to_p3d_Vec3(c2)) /
            np.linalg.norm(
                self.edge_player.line.getTailPoint() - self.edge_player.line.getTipPoint()))
        return t

    def render_hints(self):
        """ render various on-hover things:
            - cursors
            - time labels """

        get_hover_points_success, ray_direction, ray_aufpunkt, edge_p1, edge_p2, c1, c2 = (
            self.get_hover_points())

        if get_hover_points_success is True:
            if math_utils.isPointBetweenTwoPoints(edge_p1, edge_p2, c1):
                self.shortest_distance_line.setTipPoint(math_utils.np_to_p3d_Vec3(c1))
                self.shortest_distance_line.setTailPoint(math_utils.np_to_p3d_Vec3(c2))
                self.shortest_distance_line.nodePath.show()

                # -- set the time label
                # ---- set the position of the label to the position of the mouse cursor,
                #      but a bit higher
                self.time_label.textNodePath.show()
                self.time_label.setPos(*(ray_aufpunkt + ray_direction * 1.))

                # figure out the parameter t
                t = self.get_a_param(c2)

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

                # print("### COLOR: ", self.edge_player.line.nodePath.getColor())
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


class EdgeMouseClicker:
    """ encapsulates the resources one needs for holding down the mouse and dragging
        the cursor along a single edge. """

    def __init__(self, edge_player):
        self.edge_player = edge_player

        # -- register mouse event
        # taskMgr.add(self.mouseMoverTask, 'mouseMoverTask')
        base.accept('mouse1', self.on_press)

    def on_press(self):
        """ get the t parameter of the active edge (from the edge_hoverer)
            and set the position of the cursor to the time """
        print("on_press")

        get_hover_points_success, ray_direction, ray_aufpunkt, edge_p1, edge_p2, c1, c2 = (
            self.edge_player.edge_hoverer.get_hover_points())

        if get_hover_points_success is True:
            if math_utils.isPointBetweenTwoPoints(edge_p1, edge_p2, c1):
                a = self.edge_player.edge_hoverer.get_a_param(c2)
                print("a: ", a, "; self.edge_player.duration: ", self.edge_player.duration)

                # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

                if self.edge_player.is_stopped_at_beginning():
                    self.edge_player.set_paused(a_to_set_paused_at=a)
                elif self.edge_player.is_stopped_at_end():
                    self.edge_player.set_paused(a_to_set_paused_at=a  # , after_finish=True
                    )
                elif self.edge_player.is_playing():
                    self.edge_player.set_playing(a_to_start_from=a)
                elif self.edge_player.is_paused():
                    self.edge_player.set_paused(a_to_set_paused_at=a)
                else:
                    print("situation matches no state!")
                    exit(1)


    # def mouseMoverTask(self, task):
    #     self.render_hints()
    #     return task.cont
