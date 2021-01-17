from conventions import conventions
from local_utils import math_utils

import numpy as np

from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3

from direct.task import Task

from interactive_tools.picking import CollisionPicker, PickableObjectManager
from interactive_tools.dragging_and_dropping_objects import DragAndDropObjectsManager
from interactive_tools.pickables import PickablePoint, PickablePointDragger


class DraggablePoint(PickablePoint):
    """ abstraction of all utilities to create a draggable point """
    def __init__(self, camera_gear):
        """ """
        self.camera_gear = camera_gear
        self.pom = PickableObjectManager()

        PickablePoint.__init__(self, self.pom, pos=Vec3(0.5, 1., 0.0))

        self.pt_dragger = PickablePointDragger(self, self.camera_gear.camera)
        # self.pt_dragger.add_on_state_change_function(sayhi)

        self.dadom = DragAndDropObjectsManager()
        self.dadom.add_dragger(self.pt_dragger)

        self.collisionPicker = CollisionPicker(camera_gear, render, base.mouseWatcherNode, base, self.dadom)

        # -- add a mouse task to check for picking
        self.p3d_direct_object = DirectObject.DirectObject()
        self.p3d_direct_object.accept('mouse1', self.collisionPicker.onMouseTask)
