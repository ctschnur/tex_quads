from conventions import conventions

from local_utils import math_utils

from panda3d.core import Vec3, Point3, Point2, Mat4, Vec4

from direct.task import Task

from panda3d.core import CollisionTraverser, CollisionHandlerQueue, CollisionRay, CollisionNode, GeomNode, BitMask32

import numpy as np

import sys

class DragDropEventManager:
    """ it bundles the relevant information about a dragging event's state """
    def __init__(self):
        self.mouse_position_before_dragging = None

        self.counter = None  # debugging

        self.last_frame_mouse_drag_pos = None  # to query each frame if the position (state) of the dragged object has indeed changed
        self.state_changed = None  # true or false,
        # i.e. if you want to register events on the drag (e.g. updating of the geometry of a bezier curve),
        # for the events to be run, this state variable has to be checked first

        self.on_state_change_functions_with_args = []  # store functions to be called on state change

    def _register_event(self, p3d_event_identifier_str, func):
        """ internally register an event """

        base.accept(p3d_event_identifier_str, func)

    def init_dragging(self):
        """ save original mouse position at start of dragging """
        mouse_pos = base.mouseWatcherNode.getMouse()  # between -1 and 1 in both x and y
        # filmsize = base.cam.node().getLens().getFilmSize()  # the actual width of the film size

        self.mouse_position_before_dragging = mouse_pos

        self.p_xy_at_init_drag = conventions.getFilmCoordsFromMouseCoords(-self.mouse_position_before_dragging[0], -self.mouse_position_before_dragging[1], p_x_0=0., p_y_0=0.)

        print("event_managers: mouse_position_before_dragging: ", self.mouse_position_before_dragging)
        print("event_managers: p_xy_offset: ", self.p_xy_at_init_drag)

        self._register_event("escape", sys.exit) # FIXME: why?
        self._register_event('mouse1-up', self.end_dragging)

        # create an individual task for an individual dragger object
        self.dragging_mouse_move_task = taskMgr.add(self.update_dragging_task, 'update_dragging_task')

    def add_on_state_change_function(self, func, args=()):
        """ you can pass functions (or lambda functions) to here for execution """

        self.on_state_change_functions_with_args.append((func, args))

    def remove_on_state_change_function(self, func):
        """ remove a function """

        for fwa in self.on_state_change_functions_with_args:
            if fwa[0] is func:
                self.on_state_change_functions_with_args.remove(fwa)

    def update_dragging_task(self, task):
        """ whatever needs to be done every frame while dragging """
        # execute the functions that were given to
        for fwa in self.on_state_change_functions_with_args:
            fwa[0](*fwa[1])

        return task.cont

    def end_dragging(self):
        print("end dragging")
        self.mouse_position_before_dragging = None
        taskMgr.remove(self.dragging_mouse_move_task)
