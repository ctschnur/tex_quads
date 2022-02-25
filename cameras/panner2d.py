from conventions import conventions

import numpy as np

from direct.showbase.ShowBase import ShowBase, DirectObject, KeyboardButton
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval
from direct.task import Task

from panda3d.core import (
    Mat4,
    Vec3,
    Vec4,
    PandaSystem,
    OrthographicLens,
    loadPrcFileData,
    AmbientLight,
    Point3)

from interactive_tools.event_managers import DragDropEventManager

from local_utils import math_utils

import engine

from engine.tq_graphics_basics import TQGraphicsNodePath
import engine.tq_graphics_basics

from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain, Point3dCursor, CrossHair3d

from panda3d.core import ModifierButtons
from direct.showbase.ShowBase import DirectObject

from cameras.camera_gear import CameraGear


class Panner2d(CameraGear):
    """ """

    # TODO: 1 to 1 mapping from self.view_distance to filmsize, using aspect_ratio
    # filmsize_x = 2 * aspect_ratio * self.view_distance  (~ 2 * 16/9 * 1.)
    view_distance_max = 10.
    view_distance_0 = 2.
    view_distance_step_size = 0.1
    view_distance_min = 0.1

    # these two are always set together, with opposite signs
    x0 = np.array([0., 0.])
    p_previous_offset_0 = np.array([0., 0.])  # for shifting with shift+mouse

    n1 = np.array([1., 0., 0.]) # x right: horizontal coordinate: x_1
    n2 = np.array([0., 0., 1.]) # z up: vertical coordinate: x_2

    cam_pos_y_offset_vector = np.array([0., 1., 0.])

    r0 = cam_pos_y_offset_vector + x0[0] * n1 + x0[1] * n2

    near_0 = -100.
    far_0 = +100.

    plane_normal = np.cross(n1, n2)

    def __init__(self, p3d_camera, enable_visual_aids=True):
        """ """
        CameraGear.__init__(self)

        base.disableMouse()

        self._coords_3d_of_corner = None

        self.view_distance = Panner2d.view_distance_0

        # camera stuff
        self.p3d_camera = p3d_camera

        # init the camera pos
        self.x = Panner2d.x0
        self.p_previous_offset = Panner2d.p_previous_offset_0

        x, y, z = self.get_cam_coords(at_init=True)
        self.p3d_camera.setPos(x, y, z)

        self.lookat = self.get_lookat_vector(at_init=True)

        # --- hooks for camera movement
        self.p3d_camera_move_hooks = []  # store function objects

        self.p_previous_offset = np.array([0., 0.])

        self.set_corner_to_coords(Panner2d.r0, at_init=True)

        # --- set the lens
        self.lens = OrthographicLens()
        self.lens.setNearFar(Panner2d.near_0, Panner2d.far_0)
        self.p3d_camera.node().setLens(self.lens)

        # --- event handling to reorient the camera
        base.mouseWatcherNode.setModifierButtons(ModifierButtons())

        # changing zoom
        base.accept('control-wheel_down', self.handle_zoom_minus_with_mouse)
        base.accept('control-wheel_up', self.handle_zoom_plus_with_mouse)

        base.accept('control--', self.handle_zoom_minus_general)
        base.accept('control-+', self.handle_zoom_plus_general)
        base.accept('control---repeat', self.handle_zoom_minus_general)
        base.accept('control-+-repeat', self.handle_zoom_plus_general)

        # changing shift in horizontal direction
        base.accept('shift-wheel_up', self.handle_control_wheel_up)
        base.accept('shift-wheel_down', self.handle_control_wheel_down)

        # changing shift in vertical direction
        base.accept('wheel_up', self.handle_wheel_up)
        base.accept('wheel_down', self.handle_wheel_down)

        base.accept('shift-mouse1', self.handle_shift_mouse1)

        # -- window resize
        base.accept("aspectRatioChanged", self.run_window_resize_hooks)

        self.add_window_resize_hook(self.update_film_size_from_view_distance)
        self.add_window_resize_hook(self.scale_aspect2d_from_window_dimensions)

        # self.update_film_size_from_view_distance()

    # @staticmethod
    # def set_new_position_from_dragged_mouse(self, p_xy_offset, original_orbit_center):
    #     """ There is a new mouse position, now
    #     Args:
    #         p_xy_offset: the origin point (lies in the camera plane) to which the change point (calculated from the mouse displacement) is being added to """

    #     v_cam_forward = math_utils.p3d_to_np(engine.tq_graphics_basics.tq_render.getRelativeVector(
    #         self.p3d_camera, self.p3d_camera.node().getLens().getViewVector()))
    #     v_cam_forward = v_cam_forward / np.linalg.norm(v_cam_forward)
    #     # print("--- > View Vector", self.p3d_camera.node().getLens().getViewVector())

    #     v_cam_up = math_utils.p3d_to_np(engine.tq_graphics_basics.tq_render.getRelativeVector(
    #         self.p3d_camera, self.p3d_camera.node().getLens().getUpVector()))
    #     v_cam_up = v_cam_up / np.linalg.norm(v_cam_up)

    #     r_cam = math_utils.p3d_to_np(self.p3d_camera.getPos())

    #     e_up = math_utils.p3d_to_np(v_cam_up/np.linalg.norm(v_cam_up))

    #     e_cross = math_utils.p3d_to_np(
    #         np.cross(v_cam_forward/np.linalg.norm(v_cam_forward), e_up))

    #     # -- calculate the bijection between mouse coordinates m_x, m_y and plane coordinates p_x, p_y
    #     mouse_pos = base.mouseWatcherNode.getMouse()  # between -1 and 1 in both x and y
    #     p = conventions.getFilmCoordsFromMouseCoords(
    #         mouse_pos[0], mouse_pos[1], p_xy_offset[0], p_xy_offset[1])

    #     drag_vec = p[0] * e_cross + p[1] * e_up
    #     print(drag_vec)

    #     new_orbit_center = original_orbit_center + (-drag_vec)
    #     print("self.get_cam_coords: ", self.get_cam_coords())

    #     self.x = -p
    #     self.p_previous_offset = p


    def set_new_position_from_dragged_mouse(self, p_xy_offset, original_orbit_center):
        """ There is a new mouse position, now
        Args:
            p_xy_offset: the origin point (lies in the camera plane) to which the change point (calculated from the mouse displacement) is being added to """

        v_cam_forward = math_utils.p3d_to_np(engine.tq_graphics_basics.tq_render.getRelativeVector(
            self.p3d_camera, self.p3d_camera.node().getLens().getViewVector()))
        v_cam_forward = v_cam_forward / np.linalg.norm(v_cam_forward)
        # print("--- > View Vector", self.p3d_camera.node().getLens().getViewVector())

        v_cam_up = math_utils.p3d_to_np(engine.tq_graphics_basics.tq_render.getRelativeVector(
            self.p3d_camera, self.p3d_camera.node().getLens().getUpVector()))
        v_cam_up = v_cam_up / np.linalg.norm(v_cam_up)

        r_cam = math_utils.p3d_to_np(self.p3d_camera.getPos())

        e_up = math_utils.p3d_to_np(v_cam_up/np.linalg.norm(v_cam_up))

        e_cross = math_utils.p3d_to_np(
            np.cross(v_cam_forward/np.linalg.norm(v_cam_forward), e_up))

        # -- calculate the bijection between mouse coordinates m_x, m_y and plane coordinates p_x, p_y

        mouse_pos = base.mouseWatcherNode.getMouse()  # between -1 and 1 in both x and y

        p = conventions.getFilmCoordsFromMouseCoords(
            mouse_pos[0], mouse_pos[1], p_xy_offset[0], p_xy_offset[1])

        drag_vec = p[0] * e_cross + p[1] * e_up

        print(drag_vec)
        # print("p: ", p)

        new_orbit_center = original_orbit_center + (-drag_vec)

        # self.set_corner_to_coords(math_utils.indexable_vec3_to_p3d_Vec3(new_orbit_center))

        print("self.get_cam_coords: ", self.get_cam_coords())

        self.x = -np.array(p)
        self.p_previous_offset = np.array(p)

        self.set_corner_to_coords(math_utils.indexable_vec3_to_p3d_Vec3(new_orbit_center))

    def handle_wheel_up(self):
        # print("handle_wheel_up: self.x[1]: ", self.x[1])
        self.x[1] += 0.1
        self.p_previous_offset[1] -= 0.1

        self.update_camera_state()
        self.set_lookat_after_updated_camera_pos()

    def handle_wheel_down(self):
        # print("handle_wheel_down: self.x[1]: ", self.x[1])
        self.x[1] -= 0.1
        self.p_previous_offset[1] += 0.1

        self.update_camera_state()
        self.set_lookat_after_updated_camera_pos()


    def handle_control_wheel_down(self):
        self.x[0] += 0.1
        self.p_previous_offset[0] -= 0.1

        self.update_camera_state()
        self.set_lookat_after_updated_camera_pos()

    def handle_control_wheel_up(self):
        self.x[0] -= 0.1
        self.p_previous_offset[0] += 0.1

        self.update_camera_state()
        self.set_lookat_after_updated_camera_pos()

    @staticmethod
    def get_film_size_logical(aspect_ratio, view_distance):
        filmsize_x = 2. * aspect_ratio * view_distance  # (~ 2 * 16/9 * 1.)
        filmsize_y = 2. * 1.           * view_distance
        return filmsize_x, filmsize_y

    def update_film_size_from_view_distance(self):
        """ for setting the film size by a 1 to 1 mapping to view_distance """
        # filmsize_x, filmsize_y = self.get_filmsize_with_window_active()

        # winsizex = engine.tq_graphics_basics.get_window_size_x()
        # winsizey = engine.tq_graphics_basics.get_window_size_y()

        aspect_ratio = engine.tq_graphics_basics.get_window_aspect_ratio()  # x/y

        filmsize_x, filmsize_y = Panner2d.get_film_size_logical(aspect_ratio, self.view_distance)

        # print("filmsize_x, filmsize_y: ", filmsize_x, filmsize_y)

        self.lens.setFilmSize(filmsize_x, filmsize_y)
        self.lens.setNearFar(Panner2d.near_0, Panner2d.far_0)

    def get_filmsize_with_window_active(self, view_distance=None):
        """ after the window has been initialized and a default film size has been set """
        if view_distance is None:
            view_distance = self.view_distance

        aspect_ratio = engine.tq_graphics_basics.get_window_aspect_ratio()

        filmsize_x, filmsize_y = Panner2d.get_film_size_logical(aspect_ratio, view_distance)

        return filmsize_x, filmsize_y

    def scale_aspect2d_from_window_dimensions(self):
        """ when window dimensions change by resizing the window, I want the aspect2d viewport to scale with it, so that
            e.g. fonts attached to it stay the same size w.r.t the screen """
        T, R, S = math_utils.decompose_affine_trafo_4x4(math_utils.from_forrowvecs(aspect2d.getMat()))

        winsizex = engine.tq_graphics_basics.get_window_size_x()
        winsizey = engine.tq_graphics_basics.get_window_size_y()

        aspect_ratio = conventions.winsizex_0/conventions.winsizey_0

        aspect2d.setScale(conventions.winsizex_0/winsizex * 1./aspect_ratio,
                          1.,
                          conventions.winsizey_0/winsizey)

        # shift position of origin of aspect2d
        aspect2d.setPos(-1 + conventions.winsizex_0/winsizex * 1./aspect_ratio,
                        0.,
                        1 - conventions.winsizey_0/winsizey)

    # --------------------------------------------------------------------------------
    # --- getters and setters --------------------------------------------------------

    def get_coords_3d_of_corner(self, numpy=True):
        """
        args:
            numpy: return in numpy or in p3d format """
        if self._coords_3d_of_corner is not None:
            if numpy == True:
                return math_utils.p3d_to_np(self._coords_3d_of_corner)
            else:
                # otherwise it should be Vec3
                return self._coords_3d_of_corner
        else:
            print("self._coords_3d_of_corner is None")
            exit(1)

    def set_corner_to_coords(self, coords_3d_of_corner, at_init=False):
        """ """
        if coords_3d_of_corner is not None:
            self._coords_3d_of_corner = coords_3d_of_corner

        if at_init == True:
            return

        self.update_camera_state()

    def get_coords_2d_from_mouse_pos_for_zoom(self, mouse_pos=None, get_r=False):
        """ get the 2d coordinates of the panner plane from the mouse collision """
        if mouse_pos is None:
            mouse_pos = base.mouseWatcherNode.getMouse()

        # print("mouse_pos: ", mouse_pos[0], mouse_pos[1])

        mouse_p_x, mouse_p_y = conventions.getFilmCoordsFromMouseCoords(mouse_pos[0], mouse_pos[1])
        # print("mouse_p_x, mouse_p_y: ", mouse_p_x, mouse_p_y)

        cam_pos = self.get_cam_pos()
        r0_shoot = (cam_pos +  # camera position
                    self.get_e_x_prime() * mouse_p_x + self.get_e_y_prime() * mouse_p_y  # camera plane
                    )

        # args: planeNormal, planePoint, rayDirection, rayPoint
        r = math_utils.LinePlaneCollision(self.get_cam_forward_vector_normalized(), self.get_cam_pos(), self.get_cam_forward_vector_normalized(), r0_shoot)

        in_plane_vec = r - self.get_cam_pos()

        x1 = np.dot(self.get_e_x_prime(), in_plane_vec)
        x2 = np.dot(self.get_e_y_prime(), in_plane_vec)

        # print("x1, x2: ", x1, x2)

        if get_r == True:
            return np.array([x1, x2]), r

        return np.array([x1, x2])


    # ---- math getters -------

    def get_cam_forward_vector_normalized(self):
        v_cam_forward = math_utils.p3d_to_np(
            engine.tq_graphics_basics.tq_render.getRelativeVector(
            self.p3d_camera, self.p3d_camera.node().getLens().getViewVector()))

        return v_cam_forward / np.linalg.norm(v_cam_forward)

    def get_cam_up_vector_normalized(self):
        v_cam_up = math_utils.p3d_to_np(engine.tq_graphics_basics.tq_render.getRelativeVector(self.p3d_camera, self.p3d_camera.node().getLens().getUpVector()))
        return v_cam_up / np.linalg.norm(v_cam_up)

    def get_cam_pos(self):
        return math_utils.p3d_to_np(self.p3d_camera.getPos())

    def get_e_x_prime(self):
        return math_utils.p3d_to_np(np.cross(self.get_cam_forward_vector_normalized(), self.get_cam_up_vector_normalized()))

    def get_e_y_prime(self):
        return self.get_cam_up_vector_normalized()


    # ------- event handlers --------
    def handle_shift_mouse1(self):
        """ """
        print("handle_shift_mouse1")
        self.ddem = DragDropEventManager()

        # ---- calculate (solely camera and object needed and the recorded mouse position before dragging) the self.p_xy_at_init_drag
        # between -1 and 1 in both x and y

        mouse_position_before_dragging = base.mouseWatcherNode.getMouse()
        _p_xy_offset = conventions.getFilmCoordsFromMouseCoords(
            -mouse_position_before_dragging[0],
            -mouse_position_before_dragging[1],
            p_x_0=self.p_previous_offset[0],
            p_y_0=self.p_previous_offset[1])

        self.p_previous_offset = np.array(_p_xy_offset)

        self.ddem.add_on_state_change_function(
            Panner2d.set_new_position_from_dragged_mouse,
            args=(self, _p_xy_offset, self.get_coords_3d_of_corner()))

        self.ddem.init_dragging()

    # -- updating camera --

    def update_camera_state(self, view_distance=None, on_init=False):
        """ based on this class' internal variables """
        self.p3d_camera.setPos(*self.get_cam_coords())
        self.run_camera_move_hooks()

    def get_cam_coords(self, at_init=False, fixed_x_1=None, fixed_x_2=None):
        """ gets the camera coordinates in 3d, based on the x_1 and x_2 of the plane """
        x_1 = None
        x_2 = None

        if fixed_x_1 is not None:
            x_1 = fixed_x_1
        else:
            x_1 = self.x[0]

        if fixed_x_2 is not None:
            x_2 = fixed_x_2
        else:
            x_2 = self.x[1]

        cam_coords = None

        if at_init == True:
            cam_coords = tuple(
                Panner2d.cam_pos_y_offset_vector + self.get_in_plane_point_from_2d_coords(Panner2d.x0[0], Panner2d.x0[1]))
        else:
            cam_coords = tuple(
                Panner2d.cam_pos_y_offset_vector + self.get_in_plane_point_from_2d_coords(x_1, x_2))

        return np.array(cam_coords)

    def get_lookat_vector(self, at_init=False):
        return Vec3(*(self.get_cam_coords(at_init=at_init) + Panner2d.cam_pos_y_offset_vector))

    def set_lookat_after_updated_camera_pos(self, lookat=None):
        """ the lookat point is in the center of the window """
        _lookat = None
        if lookat is None:
            _lookat = self.get_lookat_vector()
        else:
            _lookat = lookat

        self.lookat = math_utils.p3d_to_np(_lookat)
        self.p3d_camera.look_at(Vec3(*self.lookat))

        assert math_utils.vectors_parallel_or_antiparallel_p(Panner2d.plane_normal, self.get_cam_forward_vector_normalized())

    def get_in_plane_point_from_2d_coords(self, x1, x2):
        return x1 * self.n1 + x2 * self.n2

    def zoom_to_2d_coords_of_mouse_task_and_doit(self):
        self.zoom_to_2d_coords_of_mouse(sign=-1., doit=True)

    def zoom_to_2d_coords_of_mouse(self, sign=1., doit=False):
        x = self.get_coords_2d_from_mouse_pos_for_zoom()
        self.zoom_to_2d_coords(x[0], x[1], sign=sign, doit=doit)

    def zoom_to_2d_coords(self, x1, x2, sign=1., doit=False):
        """
        args:
            x1, x2: coords in the plane of the panner
            sign: positive: zoom in (+)
                  negative: zoom out (-)
        """

        # print("p: ", math_utils.vectors_equal_up_to_epsilon(
        #     self.get_cam_coords(), math_utils.p3d_to_np(self.p3d_camera.getPos())))

        view_distance_step = -1. * sign * Panner2d.view_distance_step_size  # zoom in: negative

        old_view_distance = self.view_distance
        new_view_distance = np.clip(old_view_distance + view_distance_step,
                                    Panner2d.view_distance_min,
                                    Panner2d.view_distance_max)

        x_displacement = 0.
        y_displacement = 0.

        if old_view_distance != new_view_distance:
            displacements_scale_factor = -1. * view_distance_step / old_view_distance
            x_displacement = x1 * displacements_scale_factor
            y_displacement = x2 * displacements_scale_factor

        # print("zoom_to_2d_coords: ")
        # print("self.view_distance", self.view_distance, "old_view_distance", old_view_distance, "new_view_distance", new_view_distance, "view_distance_step", view_distance_step)

        if doit == True:
            self.x[0] += x_displacement
            self.x[1] += y_displacement
            self.p_previous_offset[0] -= x_displacement
            self.p_previous_offset[1] -= y_displacement
            self.view_distance = new_view_distance

        self.update_camera_state()
        self.set_lookat_after_updated_camera_pos()
        self.update_film_size_from_view_distance()

    def handle_zoom_plus_with_mouse(self):
        self.zoom_to_2d_coords_of_mouse(sign=1., doit=True)

    def handle_zoom_minus_with_mouse(self):
        self.zoom_to_2d_coords_of_mouse(sign=-1., doit=True)

    def handle_zoom_plus_general(self):
        # if base.mouseWatcherNode.hasMouse():
        #     self.handle_zoom_plus_with_mouse()
        # else:
        self.zoom_to_2d_coords(0., 0., sign=+1., doit=True)

    def handle_zoom_minus_general(self):
        # if base.mouseWatcherNode.hasMouse():
        #     self.handle_zoom_minus_with_mouse()
        # else:
        self.zoom_to_2d_coords(0., 0., sign=-1., doit=True)
