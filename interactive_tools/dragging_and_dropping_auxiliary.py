from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain
from simple_objects.simple_objects import Line2dObject, PointPrimitive, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded
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
import gltf

from cameras.Orbiter import Orbiter

from direct.task import Task

from plot_utils.bezier_curve import BezierCurve

from panda3d.core import CollisionTraverser, CollisionHandlerQueue, CollisionRay, CollisionNode, GeomNode, BitMask32, VBase4

class DraggingInfo:
    """ This is added as a member instance to a DraggableObject, to keep track of it's state
    and to maybe reparent an aspect2d attached object to the mouse while
    it's being dragged. For 3d objects, this class could store the previous position
    (in 3d space) instead of the previous parent, but otherwise it's not
    really needed (yet) I think. """

    dragMask = (  # BitMask32.bit(1)
        GeomNode.getDefaultCollideMask()
    )
    # dropMask = BitMask32.bit(1)
    # highlight = VBase4(.3,.3,.3,1)

    def __init__(self, np, draggable_object_manager, **kwargs):
        self.draggable_nodePath = np

        # self.previousParent = None   # parent before dragging
        # # at drag-time, there is the possibility to reparent an object
        # # to the mouse, so it automatically transforms with the movement of the mouse
        # # but that's only useful for an object parented to aspect2d, not a 3d object

        self.draggable_nodePath.setCollideMask(dragMask)
        self.draggable_object_manager = draggable_object_manager
        self.draggable_object_manager.tag(self.draggable_nodePath, self)

    def onPress(self, # mouseNp
    ):
        # self.previousParent = self.draggable_nodePath.getParent()
        # self.draggable_nodePath.wrtReparentTo(mouseNp)

        # collision detection is not needed at drag-time
        self.draggable_nodePath.setCollideMask(BitMask32.allOff())

    def onRelease(self):
        # self.draggable_nodePath.wrtReparentTo(self.previousParent)
        self.draggable_nodePath.setCollideMask(dragMask)


class DraggingPlane:
    """ a plane perpendicular to v_lookat
    and containing r_obj """

    def __init__(self, v_lookat, r_obj):

        # the plane is in normal form with r_obj as it's origin and v_lookat as it's normal vector

        # get a parameter form computationally by following this procedure:
        # - get a vector perpendicular to the normal vector
        #   +(directly, e.g. using this prodcedure: https://math.stackexchange.com/a/413235)+ -> v_perp_to_normal
        #   - v_cam_up (Lens -> getUpVector, transformed to world coordinates)
        #   - e_up = normalize(v_cam_up_in_world_space)
        #   - e_cross = normalize(v_lookat) crossed with e_up
        # then, one can already work with dragging if v_obj is the origin of the dragging plane
