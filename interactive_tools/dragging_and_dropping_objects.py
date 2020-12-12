from conventions import conventions

from local_utils import math_utils

from simple_objects.simple_objects import Line2dObject, PointPrimitive, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, Point3d

from panda3d.core import NodePath, Vec3, Point3, Point2, Mat4, Vec4

from direct.task import Task

from panda3d.core import CollisionTraverser, CollisionHandlerQueue, CollisionRay, CollisionNode, GeomNode, BitMask32

import numpy as np

import sys

class DragAndDropObjectsManager:
    """ Stores all dragger objects.
    Picking works using the nodepath. Thus, we need to store somewhere
    all pickable objects, and then search their nodepaths to get to the one
    that was picked.
    Each drag and drop object has to have an individual tag,
    at creation, use this class to generate a new individual tag for it.
    Once it's picked for dragging, the dragAndDropObjectsManager of the context
    is searched for the picked nodepath """

    def __init__( self ):
        self.objectIdCounter = 0
        self.draggers = []

    def add_dragger(self, dragger):
        self.draggers.append(dragger)
        print("dragger ", dragger, " added to ", self)

    def clear_draggable_objects(self):
        self.draggers = []

    def get_dragger_from_nodePath(self, nodePath):
        """ Go through draggers and query their nodepaths to search
        the object with nodePath.
        Needed e.g. after picking, which gets you back only the lower-level nodePath,
        not the dragger or directly the pickableobject """

        for c_drg in self.draggers:
            if c_drg.get_nodepath_handle_for_dragger() == nodePath:
                return c_drg
        return None
