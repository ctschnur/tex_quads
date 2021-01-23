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


class IndicatorPrimitive(TQGraphicsNodePath):
    """ """
    def __init__(self, **kwargs):
        TQGraphicsNodePath.__init__(self, **kwargs)

    # a makeobject is pointless to define here, since it will get overridden anyway
    # for a specific object

    def setColor(self, color):
        """
        Args:
            color: rgba tuple """
        self.color = color
        super().setColor(*self.color)


class Box2dCentered(IndicatorPrimitive):
    def __init__(self, **kwargs):
        IndicatorPrimitive.__init__(self, **kwargs)

    def makeObject(self):
        self.set_node_p3d(custom_geometry.createColoredUnitQuadGeomNode(
            color_vec4=Vec4(1., 1., 1., 1.), center_it=True))
        self.set_p3d_nodepath(self.getParent_p3d().attachNewNode(self.get_node_p3d()))


class SegmentedLinePrimitive(TQGraphicsNodePath):
    """ a segmented line, for example to trace out the path of sth., or plot a curve """

    def __init__(self, coords=None, thickness=1., color=Vec4(1., 1., 1., 1.), **kwargs):
        TQGraphicsNodePath.__init__(self, **kwargs)

        self.coords = coords
        self.thickness = thickness
        self.color = color

        self.set_p3d_nodepath(None)

        self.updateObject()

    def updateObject(self):
        from simple_objects.custom_geometry import createColoredSegmentedLineGeomNode

        # destroy old object
        if self.nodepath is not None:
            self.removeNode()

        # create new object
        if self.coords and self.thickness and self.color:
            self.set_node_p3d(createColoredSegmentedLineGeomNode(
                self.coords,
                thickness=self.thickness,
                color=self.color))

            self.set_p3d_nodepath(self.getParent_p3d().attachNewNode(self.get_node_p3d()))

        # lighting
        if self.nodepath is not None:
            self.setLightOff(1)

    def setCoords(self, coords):
        """ after the object has been created, this method can be used to update the path, i.e. destroy the nodepath and remake the object """
        self.coords = coords
        self.updateObject()

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
        TQGraphicsNodePath.__init__(self, **kwargs)
        self.thickness = thickness
        self.color = color
        self.howmany_points = howmany_points
        self.func = func
        self.makeObject(func, param_interv, thickness, color, howmany_points)

    def makeObject(self, func, param_interv, thickness, color, howmany_points):
        # draw a parametric curve
        from simple_objects.custom_geometry import createColoredParametricCurveGeomNode
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
