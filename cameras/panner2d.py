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
    view_distance_0 = view_distance_max/2.
    view_distance_steps = 20
    view_distance_step_size = (view_distance_max)/view_distance_steps
    view_distance_min = view_distance_step_size

    panner_zoom_0 = 1.  # percentage, 0 to 1
    offset_0 = np.array([0., 0.])

    x_h_0 = 0.
    x_v_0 = 0.

    n1 = np.array([1., 0., 0.]) # x right: horizontal coordinate: x_h
    n2 = np.array([0., 0., 1.]) # z up: vertical coordinate: x_v

    y_offset_vector = np.array([0., 1., 0.])

    r0 = y_offset_vector + x_h_0 * n1 + x_v_0 * n2  # initial position of the window upper right corner

    near_0 = -100.
    far_0 = +100.

    plane_normal = np.cross(n1, n2)

    def set_cam_coords(self, x_h, x_v):
        self.camera.setPos(self.get_cam_coords(fixed_x_h=x_h, fixed_x_v=x_v))

    def get_cam_coords(self, at_init=False, fixed_x_h=None, fixed_x_v=None):
        x_h = None
        x_v = None

        if fixed_x_h is not None:
            x_h = fixed_x_h
        else:
            x_h = self.x_h

        if fixed_x_v is not None:
            x_v = fixed_x_v
        else:
            x_v = self.x_v

        cam_coords = None

        if at_init == True:
            cam_coords = tuple(self.y_offset_vector + Panner2d.x_h_0 * self.n1 + Panner2d.x_v_0 * self.n2)
        else:
            cam_coords = tuple(self.y_offset_vector + x_h * self.n1 + x_v * self.n2)

        # print("x_h: ", x_h)
        # print("x_v: ", x_v)
        # print("self.n1: ", self.n1)

        # print("cam_coords: ", cam_coords)
        # print("x_h * self.n1 + x_v * self.n2: ", x_h * self.n1 + x_v * self.n2)

        return cam_coords

    def lookat_after_updated_camera_pos(self):
        """ the lookat point is in the center of the window """
        x, y, z = self.get_cam_coords(# at_init=True
        )
        r0_shoot = Vec3(x, y, z)

        # # args: planeNormal, planePoint, rayDirection, rayPoint
        # lookat_vec = math_utils.LinePlaneCollision(Panner2d.plane_normal, Panner2d.r0, -Panner2d.plane_normal, r0_shoot)

        # print("r0_shoot - Panner2d.plane_normal: ", r0_shoot - Panner2d.plane_normal)

        # print("r0_shoot: ", r0_shoot)
        # print("r0_shoot: ", r0_shoot)

        self.p3d_camera.look_at(Vec3(*(r0_shoot - Panner2d.plane_normal)))

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
        self.x_h = self.x_h_0
        self.x_v = self.x_v_0

        x, y, z = self.get_cam_coords(at_init=True)
        self.p3d_camera.setPos(x, y, z)

        # --- hooks for camera movement
        self.p3d_camera_move_hooks = []  # store function objects

        self.p_x_previous_offset = 0.
        self.p_y_previous_offset = 0.

        # --- set the lens
        self.lens = OrthographicLens()
        self.lens.setNearFar(Panner2d.near_0, Panner2d.far_0)
        self.p3d_camera.node().setLens(self.lens)

        # --- initial setting of the position
        self.update_camera_pos(# recalculate_film_size=True
        )
        self.lookat_after_updated_camera_pos()

        # --- event handling to reorient the camera
        from panda3d.core import ModifierButtons
        base.mouseWatcherNode.setModifierButtons(ModifierButtons())

        from direct.showbase.ShowBase import DirectObject

        # changing zoom
        base.accept('control-wheel_down', self.handle_zoom_minus)
        base.accept('control-wheel_up', self.handle_zoom_plus)

        # changing shift in horizontal direction
        base.accept('shift-wheel_up', self.handle_control_wheel_up)
        base.accept('shift-wheel_down', self.handle_control_wheel_down)

        # changing shift in vertical direction
        base.accept('wheel_up', self.handle_wheel_up)
        base.accept('wheel_down', self.handle_wheel_down)

        # # polling for zoom is better than events
        # self.plus_button = KeyboardButton.ascii_key('+')
        # self.minus_button = KeyboardButton.ascii_key('-')
        # # taskMgr.add(self.poll_zoom_plus_minus, 'Zoom')

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

        self.update_from_window_dimensions(called_from_init=True)

        # -- window resize
        self.window_resize_hooks = []  # store function objects

        base.accept("aspectRatioChanged", self.run_window_resize_hooks)

        self.add_window_resize_hook(self.update_from_window_dimensions)
        self.add_window_resize_hook(self.scale_aspect2d_from_window_dimensions)

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

        print("self.p_x_0, self.p_y_0: ", self.p_x_0, self.p_y_0)

        p_x, p_y = conventions.getFilmCoordsFromMouseCoords(
            mouse_pos[0], mouse_pos[1], p_xy_offset[0], p_xy_offset[1])

        drag_vec = p_x * e_cross + p_y * e_up

        print(drag_vec)

        new_orbit_center = original_orbit_center + (-drag_vec)

        # self.set_corner_to_coords(math_utils.indexable_vec3_to_p3d_Vec3(new_orbit_center))

        print("self.get_cam_coords: ", self.get_cam_coords())

        self.x_h = -p_x
        self.x_v = -p_y

        self.p_x_previous_offset = p_x
        self.p_y_previous_offset = p_y


        self.set_corner_to_coords(math_utils.indexable_vec3_to_p3d_Vec3(new_orbit_center))

    # def poll_zoom_plus_minus(self, task):
    #     is_down = base.mouseWatcherNode.is_button_down

    #     if is_down(self.plus_button):
    #         self.handle_zoom_plus()

    #     if is_down(self.minus_button):
    #         self.handle_zoom_minus()

    #     return task.cont

    # def get_coords_from_mouse_pos(self):
    #     """ """
    #     # x1_p, x2_p = 0., 0.
    #     # if not base.mouseWatcherNode.hasMouse():
    #     #     return np.array([x1_p, x2_p])

    #     x1_n, x2_n = self.get_zoom_step_plane_coords()

    #     # offset_coords = np.array([x1_n - x1_p, x2_n - x2_p])
    #     offset_coords = np.array([x1_n, x2_n])
    #     return offset_coords


    def handle_wheel_up(self):
        print("handle_wheel_up: self.x_v: ", self.x_v)
        self.x_v += 0.1
        self.p_y_previous_offset -= 0.1

        self.update_camera_pos()
        self.lookat_after_updated_camera_pos()

    def handle_wheel_down(self):
        print("handle_wheel_down: self.x_v: ", self.x_v)
        self.x_v -= 0.1
        self.p_y_previous_offset += 0.1

        self.update_camera_pos()
        self.lookat_after_updated_camera_pos()


    def handle_control_wheel_down(self):
        self.x_h += 0.1
        self.p_x_previous_offset -= 0.1

        self.update_camera_pos()
        self.lookat_after_updated_camera_pos()

    def handle_control_wheel_up(self):
        self.x_h -= 0.1
        self.p_x_previous_offset += 0.1

        self.update_camera_pos()
        self.lookat_after_updated_camera_pos()


    def handle_zoom_plus(self):
        self.view_distance = np.clip(self.view_distance - self.view_distance_step_size, self.view_distance_min, self.view_distance_max)
        # print("self.view_distance:", self.view_distance)
        self.update_camera_pos()
        self.lookat_after_updated_camera_pos()

    def handle_zoom_minus(self):
        self.view_distance = np.clip(self.view_distance + self.view_distance_step_size, self.view_distance_min, self.view_distance_max)

        self.update_camera_pos()
        self.lookat_after_updated_camera_pos()


    # def add_camera_move_hook(self, func):
    #     self.p3d_camera_move_hooks.append(func)

    # def remove_camera_move_hook(self, func):
    #     """ remove the hook """
    #     self.p3d_camera_move_hooks.remove(func)

    # def run_camera_move_hooks(self):
    #     for c_hook in self.p3d_camera_move_hooks:
    #         # run the function
    #         c_hook()


    def update_from_window_dimensions(self, called_from_init=False):
        """ """
        # print("update_from_window_dimensions called, self.view_distance=", self.view_distance)

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
            # self.set_orthographic_zoom(None, 2. * aspect_ratio)
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

    def get_coords_2d_of_mouse_for_zoom(self):
        """ get the 2d coordinates of the plane """
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
        p_xy_offset = conventions.getFilmCoordsFromMouseCoords(
            -mouse_position_before_dragging[0],
            -mouse_position_before_dragging[1],
            p_x_0=self.p_x_previous_offset, p_y_0=self.p_y_previous_offset)

        self.p_x_0 = p_xy_offset[0]
        self.p_y_0 = p_xy_offset[1]

        self.ddem.add_on_state_change_function(
            Panner2d.set_new_position_from_dragged_mouse,
            args=(self, p_xy_offset, self.get_coords_3d_of_corner()))

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
        # print("update_camera_pos")

        x, y, z = self.get_cam_coords()
        self.p3d_camera.setPos(x, y, z)

        self.lookat_after_updated_camera_pos()
        self.update_from_window_dimensions()
        # self.run_camera_move_hooks()

    def set_orthographic_zoom(self, width, height):
        """ an orthographic lens' `zoom`
            is controlled by the film size
        args:
            width:  width of the orthographic lens in world coordinates
            height:  height ---------------- '' ------------------------
        """

        if width is None and height:
            width = height * engine.tq_graphics_basics.get_window_aspect_ratio()
        elif height is None:
            print("ERR: height is None")
            exit(1)

        width = height * engine.tq_graphics_basics.get_window_aspect_ratio()
        # print("Ortho Lens Film: ", "width: ", width, ", height: ", height)

        self.lens.setFilmSize(width, height)

        # print("-------- self.lens.setFilmSize(width, height): ", width, height)

        self.width = width
        self.height = height

    # def set_view_to_xz_plane_and_reset_zoom(self):
    #     self.view_distance = self.view_distance
    #     self.set_view_to_xz_plane()

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
