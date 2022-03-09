from conventions import conventions

from simple_objects import custom_geometry
from local_utils import texture_utils
from engine.tq_graphics_basics import TQGraphicsNodePath

from latex_objects.latex_expression_manager import LatexImageManager, LatexImage

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Vec3,
    Vec4,
    TransparencyAttrib,
    AntialiasAttrib,
    NodePath,
    Mat4,
    Mat3)
from direct.interval.IntervalGlobal import Wait, Sequence
from direct.interval.LerpInterval import LerpFunc

import hashlib
import numpy as np

from simple_objects.custom_geometry import createColoredParametricDashedCurveGeomNode
from simple_objects.custom_geometry import createColoredSegmentedLineGeomNode
from simple_objects.custom_geometry import createColoredParametricCurveGeomNode

from local_utils import math_utils

from simple_objects.custom_geometry import createRoundedStrokeSegment2d, createColoredUnitQuadGeomNode, createColoredUnitDisk

class IndicatorPrimitive(TQGraphicsNodePath):
    """ """
    def __init__(self, **kwargs):
        """ """
        TQGraphicsNodePath.__init__(self, **kwargs)

        # a makeobject is pointless to define here, since it will get overridden anyway
        # for a specific object

    # def setColor(self, color):
    #     """
    #     Args:
    #         color: rgba tuple """
    #     self.color = color
    #     super().setColor(*self.color)


class Box2dCentered(IndicatorPrimitive):
    def __init__(self, **kwargs):
        IndicatorPrimitive.__init__(self, **kwargs)

    def makeObject(self):
        self.set_node_p3d(custom_geometry.createColoredUnitQuadGeomNode(
            color_vec4=Vec4(1., 1., 1., 1.), center_it=True))
        self.set_p3d_nodepath(self.getParent_p3d().attachNewNode(self.get_node_p3d()))


class Box2d(IndicatorPrimitive):
    def __init__(self, center_it=False, **kwargs):
        IndicatorPrimitive.__init__(self, **kwargs)
        self._center_it = center_it
        self.makeObject()

    def makeObject(self):
        self.set_node_p3d(custom_geometry.createColoredUnitQuadGeomNode(
            color_vec4=Vec4(0., 0., 1., 1.), center_it=self._center_it))
        self.set_p3d_nodepath(self.getParent_p3d().attachNewNode(self.get_node_p3d()))

        # np = render.attachNewNode(gn)
        self.setTwoSided(True)
        self.setLightOff(1)
        self.setTransparency(True)


class SegmentedLinePrimitive(TQGraphicsNodePath):
    """ a segmented line, for example to trace out the path of sth., or plot a curve """

    def __init__(self, coords=None, thickness=1., color=Vec4(1., 1., 1., 1.), **kwargs):
        TQGraphicsNodePath.__init__(self, **kwargs)

        self.coords = coords
        self.thickness = thickness
        self.color = color

        # self.set_p3d_nodepath(None)

        self.updateObject()

    # def set_parent_node_to_reattach_upon_removal()

    def updateObject(self):
        # destroy old object
        if self.get_p3d_nodepath() is not None:
            self.removeNode()

        # create new object
        if self.coords and self.thickness and self.color:
            self.set_node_p3d(createColoredSegmentedLineGeomNode(
                self.coords,
                thickness=self.thickness,
                color=self.color))

            self.set_p3d_nodepath(self.getParent_p3d().attachNewNode(self.get_node_p3d()))

        # lighting
        if self.get_node_p3d() is not None:
            self.setLightOff(1)

    def setCoords(self, coords):
        """ after the object has been created, this method can be used to update the path, i.e. destroy the nodepath and remake the object """
        self.coords = coords
        self.updateObject()

    def getCoords_np(self):
        """ """
        return np.array([math_utils.p3d_to_np(coord) for coord in self.coords])

    def extendCoords(self, coords_to_add):
        """ adds coords to the previous coords which are already in memory.
            useful if you want to e.g. just trace out (log) a path and don't care about all previous points.
        Args:
            coords_to_add: list of 3d np.array coordinates """
        if coords_to_add is None:
            return

        if self.coords is None:
            self.coords = []

        self.coords.extend(coords_to_add)
        self.updateObject()


class ParametricLinePrimitive(TQGraphicsNodePath):
    def __init__(self, func, param_interv=np.array([0, 1]),
                 thickness=1., color=Vec4(1., 1., 1., 1.), howmany_points=50, **kwargs):
        """ """
        TQGraphicsNodePath.__init__(self, **kwargs)

        self.thickness = thickness
        self.color = color
        self.howmany_points = howmany_points
        self.func = func
        self.param_interv = param_interv
        self.func = func
        self.thickness = thickness
        self.makeObject(func, param_interv, thickness, color, howmany_points)

    def makeObject(self, func, param_interv, thickness, color, howmany_points):
        # draw a parametric curve
        self.set_node_p3d(createColoredParametricCurveGeomNode(
            func=func,
            param_interv=param_interv, thickness=thickness, color=color, howmany_points=howmany_points))
        self.set_p3d_nodepath(self.getParent_p3d().attachNewNode(self.get_node_p3d()))
        self.setLightOff(1)


class ParametricDashedLinePrimitive(TQGraphicsNodePath):
    def __init__(self,
                 func,
                 param_interv=np.array([0,
                                        1]),
                 thickness=1.,
                 color=Vec4(1., 1., 1., 1.),
                 howmany_points=50, **kwargs):
        TQGraphicsNodePath.__init__(self, **kwargs)
        self.makeObject(
            func,
            param_interv,
            thickness,
            color,
            howmany_points,
        )

    def makeObject(self, func, param_interv, thickness, color, howmany_points):
        self.set_node_p3d(createColoredParametricDashedCurveGeomNode(
            func=func,
            param_interv=param_interv,
            thickness=thickness,
            color=color,
            howmany_points=howmany_points))

        self.set_p3d_nodepath(self.getParent_p3d().attachNewNode(self.get_node_p3d()))
        self.setLightOff(1)


class ConePrimitive(TQGraphicsNodePath):
    def __init__(self):
        super(ConePrimitive, self).__init__()

    def makeObject(self):
        self.set_node_p3d(custom_geometry.create_GeomNode_Cone(
            color_vec4=Vec4(1., 1., 1., 1.)))

        self.set_p3d_nodepath(self.getParent_p3d().attachNewNode(self.get_node_p3d()))
        self.setTwoSided(True)


class Stroke2d(TQGraphicsNodePath):
    """ a stroke is a collection of stroke segments """
    epsilon_0 = 0.01
    radius_0 = 0.01
    def __init__(self, *args, **kwargs):
        TQGraphicsNodePath.__init__(self, *args, **kwargs)
        self.stroke_segments = []
        self.last_added_point = None  # np array

    def append_stroke_segment(self, stroke_segment_p3d_np):
        self.stroke_segments.append(stroke_segment_p3d_np)
        stroke_segment_p3d_np.reparentTo(self.get_p3d_nodepath())

    def append_point(self, point):
        """
        Args: point: 2d tuple (*, *) """
        append_point_p = None
        if self.last_added_point is not None:
            if math_utils.vectors_equal_up_to_epsilon(np.array(self.last_added_point), np.array(point), epsilon_per_component=Stroke2d.epsilon_0):
                append_point_p = False
            else:
                append_point_p = True
        else:
            self.last_added_point = np.array([point[0], point[1]])
            append_point_p = True

        if append_point_p == True:
            rss = createRoundedStrokeSegment2d(p1=(self.last_added_point[0], self.last_added_point[1]),
                                               p2=(point[0], point[1]),
                                               radius=Stroke2d.radius_0)
            self.append_stroke_segment(rss)

            self.last_added_point = np.array([point[0], point[1]])

        else:
            print("WARNING: point not added")
