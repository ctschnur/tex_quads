from local_utils import math_utils

from simple_objects.primitives import ParametricLinePrimitive
from panda3d.core import Vec3, Mat4, Vec4

import numpy as np
import scipy.special

import glm

from direct.showbase.ShowBase import ShowBase, DirectObject

from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight

from conventions import conventions

import engine

def getCameraMouseRay(camera, mouse_pos):
    # aufpunkt of the plane -> just choose the camera position
    r0_obj = math_utils.p3d_to_np(base.cam.getPos())

    v_cam_forward = math_utils.p3d_to_np(engine.tq_graphics_basics.tq_render.getRelativeVector(camera, camera.node().getLens().getViewVector()))
    v_cam_forward = v_cam_forward / np.linalg.norm(v_cam_forward)
    # self.camera_gear.p3d_camera.node().getLens().getViewVector()

    v_cam_up = math_utils.p3d_to_np(engine.tq_graphics_basics.tq_render.getRelativeVector(camera, camera.node().getLens().getUpVector()))
    v_cam_up = v_cam_up / np.linalg.norm(v_cam_up)

    r_cam = math_utils.p3d_to_np(camera.getPos())

    e_up = math_utils.p3d_to_np(v_cam_up/np.linalg.norm(v_cam_up))

    e_cross = math_utils.p3d_to_np(np.cross(v_cam_forward/np.linalg.norm(v_cam_forward), e_up))

    # determine the middle origin of the draggable plane (where the plane intersects the camera's forward vector)
    r0_middle_origin = math_utils.LinePlaneCollision(v_cam_forward, r0_obj, v_cam_forward, r_cam)

    # p_xy_offset = conventions.getFilmCoordsFromMouseCoords(-self.mouse_position_before_dragging[0], -self.mouse_position_before_dragging[1], p_x_0=0., p_y_0=0.)

    p_x, p_y = conventions.getFilmCoordsFromMouseCoords(mouse_pos[0], mouse_pos[1]# , p_xy_offset[0], p_xy_offset[1]
    )
    # p_x, p_y = conventions.getFilmCoordsFromMouseCoords(mouse_pos[0], mouse_pos[1], 0., 0.)

    in_plane_vector = p_x * e_cross + p_y * e_up

    ray_aufpunkt = r0_middle_origin + in_plane_vector

    ray_direction = v_cam_forward



    return ray_direction, ray_aufpunkt
