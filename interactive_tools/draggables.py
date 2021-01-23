from conventions import conventions
from local_utils import math_utils

import numpy as np

from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3

from direct.task import Task

from interactive_tools.picking import CollisionPicker, PickableObjectManager
from interactive_tools.dragging_and_dropping_objects import DragAndDropObjectsManager
from interactive_tools.pickables import PickablePoint, PickablePointDragger

from statemachine.edgeplayer import EdgePlayerSM

from plot_utils.edgegraphics import EdgeGraphicsDraggable
from plot_utils.graphickersm import GraphickerSM
import engine


class DraggablePoint(PickablePoint):
    """ abstraction of all utilities to create a draggable point """

    def __init__(self, camera_gear):
        """ """
        self.camera_gear = camera_gear
        self.pom = PickableObjectManager()

        PickablePoint.__init__(self, self.pom)

        self.pt_dragger = PickablePointDragger(self, self.camera_gear.camera)
        # self.pt_dragger.add_on_state_change_function(sayhi)

        self.dadom = DragAndDropObjectsManager()
        self.dadom.add_dragger(self.pt_dragger)

        self.collisionPicker = CollisionPicker(
            camera_gear, engine.tq_graphics_basics.tq_render, base.mouseWatcherNode, self.dadom)

        # -- add a mouse task to check for picking
        self.p3d_direct_object = DirectObject.DirectObject()
        self.p3d_direct_object.accept(
            'mouse1', self.collisionPicker.onMouseTask)

        # base.accept('mouse1', self.collisionPicker.onMouseTask)

        # self.add_on_state_change_function(self.sayhi)

    def add_on_state_change_function(self, func, args=()):
        """ """
        self.pt_dragger.add_on_state_change_function(func, args=args)

    # def sayhi(self):
    #     """ """
    #     print("HELLO")


class DraggableEdgePlayer(EdgePlayerSM):
    """ """

    def __init__(self, wave_file_path, camera_gear, taskmgr, *sm_args, **sm_kwargs):
        """ """

        dp1_v1 = Vec3(0.5, 0.5, 0.)
        dp2_v2_override = Vec3(1.5, 1.5, 0.)

        self.camera_gear = camera_gear

        self.edge_graphics_draggable = EdgeGraphicsDraggable(
            lambda: GraphickerSM.lps_rate,
            lambda: self.get_duration(),
            self.camera_gear)
        self.edge_graphics_draggable.attach_to_render()

        EdgePlayerSM.__init__(self, wave_file_path, self.camera_gear, taskmgr,
                              *sm_args, edge_graphics=self.edge_graphics_draggable,
                              **sm_kwargs)

        self.transition_into(self.state_load)

        self.edge_graphics_draggable.set_v1(dp1_v1, update_graphics=False)
        self.gcsm.edge_graphics.set_v2_override(dp2_v2_override)

        dp_arr = [self.edge_graphics_draggable.dp1,
                  self.edge_graphics_draggable.dp2]

        for dp in dp_arr:
            dp.add_on_state_change_function(
                self.update_the_line_and_draggable_points,
                args=(self.edge_graphics_draggable,
                      self.edge_graphics_draggable.dp1,
                      self.edge_graphics_draggable.dp2))

    def update_the_line_and_draggable_points(self, edge_graphics_draggable, dp1, dp2,
                                             ):
        """ """
        cursor_pos = (
            self.edge_graphics_draggable.cursor_sequence.get_t()/
            self.edge_graphics_draggable.get_duration_func())

        # print(self.edge_graphics_draggable.cursor_sequence.get_t())

        edge_graphics_draggable.set_cursor_position(cursor_pos)
        edge_graphics_draggable.set_v1(dp1.getPos(), update_graphics=False)
        edge_graphics_draggable.set_v2_override(dp2.getPos())

        edge_graphics_draggable.update_line()
