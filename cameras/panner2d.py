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

from plot_utils.DraggableFrame import PanelGeometry

from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain, Point3dCursor, CrossHair3d


class Panner2dVisualAids(TQGraphicsNodePath):
    """ A set of graphics that helps the panner """

    def __init__(self, panner2d):
        """
        Args:
            panner2d : the panner2d object that gets these visual aids """
        self.panner2d = panner2d

        TQGraphicsNodePath.__init__(self)

        # self.crosshair = None
        # self.crosshair = CrossHair3d(self.panner2d, lines_length=0.25)
        # self.crosshair.reparentTo(self)

    def on(self):
        """ show them """
        # if not self.crosshair:
        #     self.crosshair = CrossHair3d(self.panner2d)
        #     self.crosshair.reparentTo(self)
        pass

    def update(self):
        """ """
        # if self.crosshair:
        #     self.crosshair.update()

        # self.x_vvec.setTipPoint(Vec3(1., 0., 0.))
        # self.x_vvec.setTailPoint(Vec3(0., 0., 0.))

        pass

    def remove(self):
        """ """
        # if self.crosshair:
        #     self.crosshair.remove()
        #     self.crosshair = None
        pass

class Panner2d:
    """ """
    view_distance_max = 100.
    # view_distance_0 = view_distance_max/2.
    view_distance_0 = 50.
    view_distance_steps = 10
    view_distance_step_size = (view_distance_max)/view_distance_steps
    view_distance_min = view_distance_step_size

    panner_zoom_0 = 1.  # percentage, 0 to 1
    # plane_offset_point_0 = np.array([0., 0., 0.])  # the plane where the panner is fixed to has an offset point and two orthogonal spanning vectors

    x0 = np.array([0., 0.])

    n1 = np.array([1., 0., 0.]) # x right: horizontal coordinate: x_1
    n2 = np.array([0., 0., 1.]) # z up: vertical coordinate: x_2

    cam_pos_y_offset_vector = np.array([0., 1., 0.])

    # initial position of the window upper right corner
    r0 = cam_pos_y_offset_vector + x0[0] * n1 + x0[1] * n2

    near_0 = -100.
    far_0 = +100.

    plane_normal = np.cross(n1, n2)

    sin_zoom_param_0 = np.pi/2.

    def __init__(self, p3d_camera, view_distance=None, enable_visual_aids=True):
        base.disableMouse()

        self._coords_3d_of_corner = None
        self.set_corner_to_coords(Panner2d.r0, not_just_init=False)

        self.before_aspect_ratio_changed_at_init = True  # ?

        self.view_distance = None

        if view_distance is not None:
            self.view_distance = view_distance
        else:
            self.view_distance = self.view_distance_0


        # camera stuff
        self.p3d_camera = p3d_camera

        # init the camera pos
        self.x = Panner2d.x0

        self.p_0 = np.array([0., 0.])

        # self.plane_offset_point = Panner2d.plane_offset_point_0

        x, y, z = self.get_cam_coords(at_init=True)
        self.p3d_camera.setPos(x, y, z)

        self.lookat = self.get_lookat_vector()

        self.sin_zoom_param = Panner2d.sin_zoom_param_0

        self._accumulated_from_mouse_offset = np.array([0., 0.])

        # --- hooks for camera movement
        self.p3d_camera_move_hooks = []  # store function objects

        self.p_previous_offset = np.array([0., 0.])

        # --- set the lens
        self.lens = OrthographicLens()
        self.lens.setNearFar(Panner2d.near_0, Panner2d.far_0)
        self.p3d_camera.node().setLens(self.lens)

        # --- event handling to reorient the camera
        from panda3d.core import ModifierButtons
        base.mouseWatcherNode.setModifierButtons(ModifierButtons())

        from direct.showbase.ShowBase import DirectObject

        # changing zoom
        base.accept('control-wheel_down', self.handle_zoom_minus)
        base.accept('control-wheel_up', self.handle_zoom_plus)

        # base.accept('control-wheel_up', self.handle_zoom_sin)

        # changing shift in horizontal direction
        base.accept('shift-wheel_up', self.handle_control_wheel_up)
        base.accept('shift-wheel_down', self.handle_control_wheel_down)

        # changing shift in vertical direction
        base.accept('wheel_up', self.handle_wheel_up)
        base.accept('wheel_down', self.handle_wheel_down)

        # mouse move
        # base.accept('mouse1', self.get_coords_2d_from_mouse_pos_for_zoom)
        # base.accept('mouse1', self.zoom_to_2d_coords_of_mouse_task_and_doit)

        # # polling for zoom is better than events
        # self.plus_button = KeyboardButton.ascii_key('+')
        # self.minus_button = KeyboardButton.ascii_key('-')

        # blender-like usage of 1, 3, 7 keys to align views with axes
        # base.accept('1', self.set_view_to_xz_plane)
        # base.accept('3', self.set_view_to_yz_plane)
        # base.accept('7', self.set_view_to_xy_plane)

        # base.accept('1', self.set_view_to_xz_plane_and_reset_zoom)

        self.visual_aids = Panner2dVisualAids(self)
        self.visual_aids.attach_to_render()

        if enable_visual_aids == True:
            self.visual_aids.on()
        else:
            self.visual_aids.off()

        # TODO: append a drag drop event manager here
        base.accept('shift-mouse1', self.handle_shift_mouse1)

        # p3d throws an aspectRatiochanged event after calling MyApp.run()
        # This variable controls which aspect ratio to take (initial aspect ratio (hard-coded or in configuration file)
        # or asking for it from the window manager)

        self.update_film_size_from_window_dimensions(called_from_init=True)

        # -- window resize
        self.window_resize_hooks = []  # store function objects

        base.accept("aspectRatioChanged", self.run_window_resize_hooks)

        self.add_window_resize_hook(self.update_film_size_from_window_dimensions)
        self.add_window_resize_hook(self.scale_aspect2d_from_window_dimensions)


        # self.view_distance = Panner2d.view_distance_0 # 50.
        # self.x = [2.,  4.1]

        self.view_distance = Panner2d.view_distance_0
        self.x = [0., 0.]



        # lookat
        self.x_vvec = Vector()
        self.x_vvec.setColor(Vec4(0., 0., 0., 1.), 1)
        # self.x_vvec.setTipPoint(Vec3(self.x[0], 0., self.x[1]))
        self.x_vvec.setTipPoint(Vec3(0., 0., 0.))
        self.x_vvec.setTailPoint(Vec3(0., 0., 0.))
        self.x_vvec.reparentTo(engine.tq_graphics_basics.tq_render)

        # yellow
        self.v1_vvec = Vector()
        self.v1_vvec.setColor(Vec4(1., 1., 0., 1.), 1)
        self.v1_vvec.setTipPoint(Vec3(0., 0., 0.))
        self.v1_vvec.setTailPoint(Vec3(0., 0., 0.))
        self.v1_vvec.reparentTo(engine.tq_graphics_basics.tq_render)

        # grey
        # dark grey
        self.A_vvec = Vector()
        self.A_vvec.setColor(Vec4(0.5, 0.5, 0.5, 1.), 1)
        self.A_vvec.setTipPoint(Vec3(0., 0., 0.))
        self.A_vvec.setTailPoint(Vec3(0., 0., 0.))
        self.A_vvec.reparentTo(engine.tq_graphics_basics.tq_render)

        # light grey
        self.B_vvec = Vector()
        self.B_vvec.setColor(Vec4(0.75, 0.75, 0.75, 1.), 1)
        self.B_vvec.setTipPoint(Vec3(0., 0., 0.))
        self.B_vvec.setTailPoint(Vec3(0., 0., 0.))
        self.B_vvec.reparentTo(engine.tq_graphics_basics.tq_render)


        # blue
        self.C_vvec = Vector()
        self.C_vvec.setColor(Vec4(0., 0., 1., 0.5), 1)
        self.C_vvec.setTipPoint(Vec3(0., 0., 0.))
        self.C_vvec.setTailPoint(Vec3(0., 0., 0.))
        self.C_vvec.reparentTo(engine.tq_graphics_basics.tq_render)


        # next lookat
        self.next_lookat_vvec = Vector()
        self.next_lookat_vvec.setColor(Vec4(0., 1., 0., 0.5), 1)
        self.next_lookat_vvec.setTipPoint(Vec3(0., 0., 0.))
        self.next_lookat_vvec.setTailPoint(Vec3(0., 0., 0.))
        self.next_lookat_vvec.reparentTo(engine.tq_graphics_basics.tq_render)


        self.update_camera_pos()
        self.set_lookat_after_updated_camera_pos()
        self.update_film_size_from_window_dimensions()

        # # --- initial setting of the position
        # self.update_camera_pos(# recalculate_film_size=True
        # )
        # self.update_film_size_from_window_dimensions()
        # self.set_lookat_after_updated_camera_pos()

        # taskMgr.add(self.zoom_to_2d_coords_of_mouse_task, 'zoom-updating')


    @staticmethod
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

        print("self.p_0, ", self.p_0)

        p = conventions.getFilmCoordsFromMouseCoords(
            mouse_pos[0], mouse_pos[1], p_xy_offset[0], p_xy_offset[1])

        drag_vec = p[0] * e_cross + p[1] * e_up

        print(drag_vec)
        # print("p: ", p)

        new_orbit_center = original_orbit_center + (-drag_vec)

        # self.set_corner_to_coords(math_utils.indexable_vec3_to_p3d_Vec3(new_orbit_center))

        print("self.get_cam_coords: ", self.get_cam_coords())

        self.x = -p

        self.p_previous_offset = p

        self.set_corner_to_coords(math_utils.indexable_vec3_to_p3d_Vec3(new_orbit_center))

    def handle_wheel_up(self):
        print("handle_wheel_up: self.x[1]: ", self.x[1])
        self.x[1] += 0.1
        self.p_previous_offset[1] -= 0.1

        self.update_camera_pos()
        self.set_lookat_after_updated_camera_pos()

    def handle_wheel_down(self):
        print("handle_wheel_down: self.x[1]: ", self.x[1])
        self.x[1] -= 0.1
        self.p_previous_offset[1] += 0.1

        self.update_camera_pos()
        self.set_lookat_after_updated_camera_pos()


    def handle_control_wheel_down(self):
        self.x[0] += 0.1
        self.p_previous_offset[0] -= 0.1

        self.update_camera_pos()
        self.set_lookat_after_updated_camera_pos()

    def handle_control_wheel_up(self):
        self.x[0] -= 0.1
        self.p_previous_offset[0] += 0.1

        self.update_camera_pos()
        self.set_lookat_after_updated_camera_pos()


    def update_film_size_from_window_dimensions(self, called_from_init=False):
        """ """
        # print("update_film_size_from_window_dimensions called, self.view_distance=", self.view_distance)

        aspect_ratio = None
        if self.before_aspect_ratio_changed_at_init == True or called_from_init == True:
            aspect_ratio = conventions.winsizex_0/conventions.winsizey_0

            if called_from_init == False:
                self.before_aspect_ratio_changed_at_init = False
        else:
            aspect_ratio = engine.tq_graphics_basics.get_window_aspect_ratio()
            # print("aspect ratio : ", aspect_ratio)
            # print(winsizex,
            #       winsizey)
            scale_factor = 1./(conventions.winsizey_0/2.)
            scale_factor *= self.get_filmsize_scale_factor()

            winsizex = engine.tq_graphics_basics.get_window_size_x()
            winsizey = engine.tq_graphics_basics.get_window_size_y()

            filmsize_x = winsizex*scale_factor
            filmsize_y = winsizey*scale_factor

            # print("filmsize_x, filmsize_y: ", filmsize_x, filmsize_y)

            # print("not at init")
            self.lens.setFilmSize(filmsize_x, filmsize_y)
            self.lens.setNearFar(Panner2d.near_0, Panner2d.far_0)


    def get_filmsize_scale_factor(self):
        return self.view_distance/Panner2d.view_distance_0

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

    def set_corner_to_coords(self, coords_3d_of_corner, not_just_init=True):
        """ """
        if coords_3d_of_corner is not None:
            self._coords_3d_of_corner = coords_3d_of_corner

        if not_just_init == True:
            if self.visual_aids:
                self.visual_aids.update()

            self.update_camera_pos()

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

    # def set_coords_2d_for_lookat(self):

    def get_coords_2d_from_mouse_pos_for_zoom(self, mouse_pos=None, get_r=False):
        """ get the 2d coordinates of the panner plane from the mouse collision """
        if mouse_pos is None:
            mouse_pos = base.mouseWatcherNode.getMouse()

        print("mouse_pos: ", mouse_pos[0], mouse_pos[1])

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

        print("x1, x2: ", x1, x2)

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

        self.p_0 = _p_xy_offset

        self.ddem.add_on_state_change_function(
            Panner2d.set_new_position_from_dragged_mouse,
            args=(self, _p_xy_offset, self.get_coords_3d_of_corner()))

        self.ddem.init_dragging()

    # -- window resize

    def add_window_resize_hook(self, func):
        """ func is the function to run when the window resizes;
        if it depends on parameters, they can be set upon adding
        the hook by just using a lambda function """
        self.window_resize_hooks.append(func)

    def remove_window_resize_hook(self, func):
        """ remove the hook """
        self.window_resize_hooks.remove(func)

    def run_window_resize_hooks(self):
        for c_hook in self.window_resize_hooks:
            # run the function
            c_hook()

    # -- updating camera --

    def update_camera_pos(self, view_distance=None, on_init=False):
        """ based on this class' internal variables """
        self.p3d_camera.setPos(*self.get_cam_coords())

        # self.x_vvec.setTipPoint(Vec3(self.x[0], 0., self.x[1]))

        # print("self.x: ", self.x)
        # print("self.view_distance: ", self.view_distance)

    # -- visual aids --

    def toggle_visual_aids(self, p):
        """
        Args:
            p: True or False to enalbe or disable visual aids """
        if p == True:
            if self.visual_aids is not None:
                self.visual_aids = Panner2dVisualAids(self)
                self.visual_aids.on()
        else:
            self.visual_aids.off()
            self.visual_aids = None

    # --

    # def set_cam_coords(self, x_1, x_2):
    #     self.p3d_camera.setPos(self.get_cam_coords(fixed_x_1=x_1, fixed_x_2=x_2))

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
            cam_coords = tuple(self.cam_pos_y_offset_vector
                               + self.get_in_plane_point_from_2d_coords(Panner2d.x0[0], Panner2d.x0[1])) # Panner2d.x0[0] * self.n1 + Panner2d.x0[1] * self.n2)
        else:
            cam_coords = tuple(self.cam_pos_y_offset_vector +
                               self.get_in_plane_point_from_2d_coords(x_1, x_2) # x_1 * self.n1 + x_2 * self.n2
            )

        # print("x_1: ", x_1)
        # print("x_2: ", x_2)
        # print("self.n1: ", self.n1)

        # print("cam_coords: ", cam_coords)
        # print("x_1 * self.n1 + x_2 * self.n2: ", x_1 * self.n1 + x_2 * self.n2)

        return np.array(cam_coords)

    def get_lookat_vector(self):
        return Vec3(*(self.get_cam_coords() + Panner2d.cam_pos_y_offset_vector))

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

    def handle_zoom_sin(self):
        """
        increase/decrease view distance with sin function (zoom towards lookat) """

        print("zoom sin: ")

        self.sin_zoom_param += np.pi / 50.

        print("self.sin_zoom_param:", self.sin_zoom_param)

        old_view_distance = self.view_distance
        new_view_distance = self.view_distance_step_size + self.view_distance_max * (1. + np.sin(self.sin_zoom_param))

        view_distance_step = new_view_distance - old_view_distance

        # self.view_distance = np.clip(, self.view_distance_min, self.view_distance_max)

        self.view_distance = new_view_distance

        self.update_camera_pos()
        self.update_film_size_from_window_dimensions()

        # print("self.get_coords_2d_from_mouse_pos_for_zoom(): ", self.get_coords_2d_from_mouse_pos_for_zoom())

        # from_mouse_coords_after = self.get_coords_2d_from_mouse_pos_for_zoom()

        # print("from_mouse_coords_before: ", from_mouse_coords_before)
        # print("from_mouse_coords_after: ", from_mouse_coords_after)

        # _vec = (from_mouse_coords_before - from_mouse_coords_after)
        # self._accumulated_from_mouse_offset += _vec

        # _vec = self._accumulated_from_mouse_offset[0] * Panner2d.n1 + self._accumulated_from_mouse_offset[1] * Panner2d.n2

        # self.set_lookat_after_updated_camera_pos(lookat=self.get_lookat_vector() + _vec)

        # self.p3d_camera.setPos(*(self.get_cam_coords() + _vec))

    def get_in_plane_point_from_2d_coords(self, x1, x2):
        return x1 * self.n1 + x2 * self.n2


    # def zoom_to_2d_coords_of_mouse_task(self, task):
    #     if base.mouseWatcherNode.hasMouse():
    #         self.zoom_to_2d_coords_of_mouse()

    #     return task.cont

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

        1. calculate the line between camera position and mouse plane intersection (v1)
        2. move the camera along this line such that the mouse plane intersection stays the same across the zoom calls
           given the view_distance_step, and the old_view_distance
           i) calculate horizontal and vertical displacement of the camera, and apply them (update_camera_pos)
           ii) apply the new view_distance (self.update_film_size_from_window_dimensions())
        """

        # print("self.get_cam_coords(): ", self.get_cam_coords())
        # print("math_utils.p3d_to_np(self.p3d_camera.getPos()): ", math_utils.p3d_to_np(self.p3d_camera.getPos()))

        # # assert np.all(self.get_cam_coords() == math_utils.p3d_to_np(self.p3d_camera.getPos()))
        # print("p: ", math_utils.vectors_equal_up_to_epsilon(self.get_cam_coords(),
        #                                                     math_utils.p3d_to_np(self.p3d_camera.getPos())))

        old_view_distance = self.view_distance
        new_view_distance = np.clip(old_view_distance -1.*sign* self.view_distance_step_size, self.view_distance_min, self.view_distance_max)
        view_distance_step = new_view_distance - old_view_distance  # zoom in: negative
        displacements_scale_factor = -1. * view_distance_step / old_view_distance

        x_displacement = x1 * displacements_scale_factor
        y_displacement = x2 * displacements_scale_factor

        if doit == True:
            self.x[0] += x_displacement
            self.x[1] += y_displacement
            self.view_distance = new_view_distance

        self.update_camera_pos()
        self.set_lookat_after_updated_camera_pos()
        self.update_film_size_from_window_dimensions()


    def handle_zoom_plus(self):
        self.zoom_to_2d_coords_of_mouse(sign=1., doit=True)

    def handle_zoom_minus(self):
        self.zoom_to_2d_coords_of_mouse(sign=-1., doit=True)
