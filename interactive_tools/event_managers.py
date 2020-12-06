from conventions import conventions

from local_utils import math_utils

from panda3d.core import Vec3, Point3, Point2, Mat4, Vec4

from direct.task import Task

from panda3d.core import CollisionTraverser, CollisionHandlerQueue, CollisionRay, CollisionNode, GeomNode, BitMask32

import numpy as np

import sys

class DragDropEventManager:
    """ it bundles the relevant information about a dragging event's state """
    def __init__(self, camera_gear):
        self.camera_gear = camera_gear

        self.mouse_position_before_dragging = None

        self.counter = None  # debugging

        self.last_frame_mouse_drag_pos = None  # to query each frame if the position (state) of the dragged object has indeed changed
        self.state_changed = None  # true or false,
        # i.e. if you want to register events on the drag (e.g. updating of the geometry of a bezier curve),
        # for the events to be run, this state variable has to be checked first

        self.on_state_change_functions_with_args = []  # store functions to be called on state change

    def init_dragging(self):
        """ save original mouse position at start of dragging """
        mouse_pos = base.mouseWatcherNode.getMouse()  # between -1 and 1 in both x and y
        # filmsize = base.cam.node().getLens().getFilmSize()  # the actual width of the film size

        self.mouse_position_before_dragging = mouse_pos

        # ---- calculate (solely camera and object needed and the recorded mouse position before dragging) the self.p_xy_offset
        self.p_xy_offset = conventions.getFilmSizeCoordinates(-self.mouse_position_before_dragging[0], -self.mouse_position_before_dragging[1], p_x_0=0., p_y_0=0.)

        print("mouse_position_before_dragging: ", self.mouse_position_before_dragging)
        print("p_xy_offset: ", self.p_xy_offset)

        # -- setup a task that updates the position

        # ---- dragging
        base.accept("escape", sys.exit)
        # base.accept('mouse1', self.onPress)
        base.accept('mouse1-up', self.end_dragging)

        # create an individual task for an individual dragger object
        self.dragging_mouse_move_task = taskMgr.add(self.update_dragging_task, 'update_dragging_task')

        self.counter = 0

        self.update_dragging_default_func()

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
        self.update_dragging_default_func()  # this changed state (or not)

        # execute the functions that were given to
        for fwa in self.on_state_change_functions_with_args:
            fwa[0](*fwa[1])

        return task.cont

    def update_dragging_default_func(self):
        print("counter: ", self.counter)
        self.counter += 1

        # v_cam_forward = math_utils.p3d_to_np(render.getRelativeVector(self.camera_gear.camera, self.camera_gear.camera.node().getLens().getViewVector()))
        # v_cam_forward = v_cam_forward / np.linalg.norm(v_cam_forward)
        # # self.camera_gear.camera.node().getLens().getViewVector()

        # v_cam_up = math_utils.p3d_to_np(render.getRelativeVector(self.camera_gear.camera, self.camera_gear.camera.node().getLens().getUpVector()))
        # v_cam_up = v_cam_up / np.linalg.norm(v_cam_up)

        # r_cam = math_utils.p3d_to_np(self.camera_gear.camera.getPos())

        # e_up = math_utils.p3d_to_np(v_cam_up/np.linalg.norm(v_cam_up))

        # e_cross = math_utils.p3d_to_np(np.cross(v_cam_forward/np.linalg.norm(v_cam_forward), e_up))

        # # determine the middle origin of the draggable plane (where the plane intersects the camera's forward vector)
        # # r0_middle_origin = math_utils.LinePlaneCollision(v_cam_forward, r0_obj, v_cam_forward, r_cam)

        # # print("r0_obj", r0_obj)
        # # print("v_cam_forward", v_cam_forward)
        # # print("v_cam_up", v_cam_up)
        # # print("r_cam", r_cam)
        # # print("e_up", e_up)
        # # print("e_cross", e_cross)
        # # print("r0_middle_origin", r0_middle_origin)

        # # -- calculate the bijection between mouse coordinates m_x, m_y and plane coordinates p_x, p_y

        # mouse_pos = base.mouseWatcherNode.getMouse()  # between -1 and 1 in both x and y
        # # filmsize = base.cam.node().getLens().getFilmSize()  # the actual width of the film size

        # self.this_frame_mouse_drag_pos = mouse_pos

        # # print("p_xy_offset: ", self.p_xy_offset)

        # p_x, p_y = conventions.getFilmSizeCoordinates(mouse_pos[0], mouse_pos[1], self.p_xy_offset[0], self.p_xy_offset[1])
        # # p_x, p_y = conventions.getFilmSizeCoordinates(mouse_pos[0], mouse_pos[1], 0., 0.)

        # drag_vec = p_x * e_cross + p_y * e_up

        # print("px: ", p_x, ", py: ", p_y)
        # print("drag_vec: ", drag_vec)


    def end_dragging(self):
        self.position_before_dragging = None
        self.mouse_position_before_dragging = None
        taskMgr.remove(self.dragging_mouse_move_task)
