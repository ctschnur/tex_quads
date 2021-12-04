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

from composed_objects.composed_objects import CrossHair3d

from interactive_tools.event_managers import DragDropEventManager

from local_utils import math_utils

import engine

from engine.tq_graphics_basics import TQGraphicsNodePath
import engine.tq_graphics_basics


class OrbiterVisualAids(TQGraphicsNodePath):
    """ A set of graphics that helps the orbiter """

    def __init__(self, orbiter):
        """
        Args:
            orbiter : the orbiter object that gets these visual aids """
        self.orbiter = orbiter

        TQGraphicsNodePath.__init__(self)

        # self.crosshair = None
        self.crosshair = CrossHair3d(self.orbiter, lines_length=0.25)
        self.crosshair.reparentTo(self)

    def on(self):
        """ show them """
        if not self.crosshair:
            self.crosshair = CrossHair3d(self.orbiter)
            self.crosshair.reparentTo(self)

    def update(self):
        """ """
        if self.crosshair:
            self.crosshair.update()

    def remove(self):
        """ """
        if self.crosshair:
            self.crosshair.remove()
            self.crosshair = None


class OrbiterOrtho:
    """ """
    # when flipping over, the eye vector and z-vector are multiplied by -1.
    # but still, to prevent graphics glitches in the situation where
    # the lookat vector and view vector are perfectly aligned ("theta = 0"),
    # theta_epsilon provides a small but visually unnoticeable offset
    # theta_epsilon = 1.0e-10
    theta_epsilon = 1.0e-5
    phi_0 = 0.
    theta_0 = np.pi/3.
    r0 = 1.
    orbit_center_0 = np.array([0., 0., 0.])


    def __init__(self, camera, r_init=2., enable_visual_aids=True):
        base.disableMouse()

        self._orbit_center = None
        self.set_orbit_center(OrbiterOrtho.orbit_center_0, not_just_init=False)

        self.before_aspect_ratio_changed_at_init = True  # ?

        self.radius_init = r_init
        self.radius = r_init
        self.phi = OrbiterOrtho.phi_0
        self.theta = OrbiterOrtho.theta_0

        # camera stuff
        self.camera = camera
        # # init the camera pos
        x, y, z = self.get_cam_coords(correct_for_camera_setting=True, fixed_phi=self.phi, fixed_theta=self.theta, fixed_r=self.radius)
        self.camera.setPos(x, y, z)  # TODO: is this really necessary in addition to the setViewMatrix ?

        # --- hooks for camera movement
        self.camera_move_hooks = []  # store function objects

        # --- hooks for window resize
        self.window_resize_hooks = []  # store function objects

        # --- set the lens
        self.lens = OrthographicLens()
        self.lens.setNearFar(-500., 500.)
        self.camera.node().setLens(self.lens)

        # --- initial setting of the position
        self.update_camera_pos(# recalculate_film_size=True
        )

        self.set_view_matrix_after_updated_camera_pos()

        # --- event handling to reorient the camera
        from panda3d.core import ModifierButtons
        base.mouseWatcherNode.setModifierButtons(ModifierButtons())

        from direct.showbase.ShowBase import DirectObject

        # changing phi
        base.accept('wheel_down', self.handle_wheel_down)

        base.accept('wheel_up', self.handle_wheel_up)

        # changing theta
        base.accept('control-wheel_down',
                    self.handle_control_wheel_down)

        base.accept('control-wheel_up', self.handle_control_wheel_up)

        # 'changing r' (although that's not what directly changes the 'zoom' in an ortho lens)
        base.accept('shift-wheel_up', self.handle_zoom_plus)

        base.accept('shift-wheel_down', self.handle_zoom_minus)

        # polling for zoom is better than events
        self.plus_button = KeyboardButton.ascii_key('+')
        self.minus_button = KeyboardButton.ascii_key('-')
        # taskMgr.add(self.poll_zoom_plus_minus, 'Zoom')

        # blender-like usage of 1, 3, 7 keys to align views with axes
        # base.accept('1', self.set_view_to_xz_plane)
        base.accept('3', self.set_view_to_yz_plane)
        base.accept('7', self.set_view_to_xy_plane)

        base.accept('1', self.set_view_to_xz_plane_and_reset_zoom)

        # base.accept('wheel_up', self.handle_wheel_up)

        # --- fix a point light to the side of the camera
        from panda3d.core import PointLight
        self.plight = PointLight('plight')
        self.pl_nodepath = engine.tq_graphics_basics.tq_render.attachNewNode_p3d(
            self.plight)
        self.set_pointlight_pos_spherical_coords()
        engine.tq_graphics_basics.tq_render.setLight(self.pl_nodepath)

        # -- set faint ambient white lighting
        from panda3d.core import AmbientLight
        self.alight = AmbientLight('alight')
        self.alnp = engine.tq_graphics_basics.tq_render.attachNewNode_p3d(
            self.alight)
        self.alight.setColor(Vec4(0.25, 0.25, 0.25, 1))
        engine.tq_graphics_basics.tq_render.setLight(self.alnp)

        self.visual_aids = OrbiterVisualAids(self)
        self.visual_aids.attach_to_render()

        if enable_visual_aids == True:
            self.visual_aids.on()
        else:
            self.visual_aids.off()

        # TODO: append a drag drop event manager here
        base.accept('shift-mouse1', self.handle_shift_mouse1  # , extraArgs=[ob]
                    )

        # p3d throws an aspectRatiochanged event after calling MyApp.run()
        # This variable controls which aspect ratio to take (initial aspect ratio (hard-coded or in configuration file)
        # or asking for it from the window manager)

        self.set_film_size_from_window_dimensions(
            called_from_orbiter_init=True)

        base.accept("aspectRatioChanged", self.run_window_resize_hooks)
        self.add_window_resize_hook(self.set_film_size_from_window_dimensions)
        self.add_window_resize_hook(self.scale_aspect2d_from_window_dimensions)

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
            p_x_0=0., p_y_0=0.)

        self.ddem.add_on_state_change_function(OrbiterOrtho.set_new_panning_orbit_center_from_dragged_mouse,
                                               args=(self, p_xy_offset, self.get_orbit_center()))
        self.ddem.init_dragging()

    @staticmethod
    def set_new_panning_orbit_center_from_dragged_mouse(camera_gear, p_xy_offset, original_orbit_center):
        """ There is a new mouse position, now
        Args:
            camera_gear: camera gear with camera member variable
            p_xy_offset: the origin point (lies in the camera plane) to which the change point (calculated from the mouse displacement) is being added to """

        v_cam_forward = math_utils.p3d_to_np(engine.tq_graphics_basics.tq_render.getRelativeVector(
            camera_gear.camera, camera_gear.camera.node().getLens().getViewVector()))
        v_cam_forward = v_cam_forward / np.linalg.norm(v_cam_forward)
        # print("--- > View Vector", camera_gear.camera.node().getLens().getViewVector())

        v_cam_up = math_utils.p3d_to_np(engine.tq_graphics_basics.tq_render.getRelativeVector(
            camera_gear.camera, camera_gear.camera.node().getLens().getUpVector()))
        v_cam_up = v_cam_up / np.linalg.norm(v_cam_up)

        r_cam = math_utils.p3d_to_np(camera_gear.camera.getPos())

        e_up = math_utils.p3d_to_np(v_cam_up/np.linalg.norm(v_cam_up))

        e_cross = math_utils.p3d_to_np(
            np.cross(v_cam_forward/np.linalg.norm(v_cam_forward), e_up))

        # determine the middle origin of the draggable plane (where the plane intersects the camera's forward vector)
        # r0_middle_origin = math_utils.LinePlaneCollision(v_cam_forward, r0_obj, v_cam_forward, r_cam)

        # print("r0_obj", r0_obj)
        # print("v_cam_forward", v_cam_forward)
        # print("v_cam_up", v_cam_up)
        # print("r_cam", r_cam)
        # print("e_up", e_up)
        # print("e_cross", e_cross)
        # print("r0_middle_origin", r0_middle_origin)

        # -- calculate the bijection between mouse coordinates m_x, m_y and plane coordinates p_x, p_y

        mouse_pos = base.mouseWatcherNode.getMouse()  # between -1 and 1 in both x and y
        # filmsize = self.camera.node().getLens().getFilmSize()  # the actual width of the film size

        # print("p_xy_offset: ", p_xy_offset)

        p_x, p_y = conventions.getFilmCoordsFromMouseCoords(
            mouse_pos[0], mouse_pos[1], p_xy_offset[0], p_xy_offset[1])
        # p_x, p_y = conventions.getFilmCoordsFromMouseCoords(mouse_pos[0], mouse_pos[1], 0., 0.)

        drag_vec = p_x * e_cross + p_y * e_up

        # print("px: ", p_x, ", py: ", p_y)
        # print("drag_vec: ", drag_vec)

        # camera_new_pos = camera_original_pos + drag_vec
        new_orbit_center = original_orbit_center + (-drag_vec)

        # print("original orbit center: ", original_orbit_center)
        # print("new orbit center: ", new_orbit_center)
        # print("current orbit center: ", camera_gear.get_orbit_center())
        camera_gear.set_orbit_center(
            math_utils.indexable_vec3_to_p3d_Vec3(new_orbit_center))
        # print("updated orbit center: ", camera_gear.get_orbit_center())

    def toggle_visual_aids(self, p):
        """
        Args:
            p: True or False to enalbe or disable visual aids """
        if p == True:
            if self.visual_aids is not None:
                self.visual_aids = OrbiterVisualAids(self)
                self.visual_aids.on()
        else:
            self.visual_aids.off()
            self.visual_aids = None

    def poll_zoom_plus_minus(self, task):

        is_down = base.mouseWatcherNode.is_button_down

        if is_down(self.plus_button):
            self.handle_zoom_plus()

        if is_down(self.minus_button):
            self.handle_zoom_minus()

        return task.cont

    def on_other_side_p(self):
        return self.theta % (2. * np.pi) > np.pi

    def correct_cam_spherical_coords(self, fixed_phi, fixed_theta, fixed_r, correct_for_camera_setting):
        # print("theta = ", self.theta, ", ",
        #       "phi = ", self.phi, ", ",
        #       "r = ", self.radius)

        # prevent over-the-top flipping
        # self.theta = self.theta % np.pi

        # keep r positive
        if self.radius < 0:
            self.radius = 0.001

        # # keep phi in the range [0, 2*pi]
        # if self.phi > 2.*np.pi:
        #     self.phi = self.phi % 2.*np.pi
        # elif self.phi < 0.:
        #     self.phi = self.phi + 2.*np.pi
        # elif self.phi > 2.*np.pi:
        #     self.phi = self.phi - 2.*np.pi

        theta = None
        phi = None
        r = None

        if fixed_theta:
            theta = fixed_theta
        else:
            theta = self.theta

        if correct_for_camera_setting == True:
            if theta % np.pi < OrbiterOrtho.theta_epsilon:
                theta = theta + OrbiterOrtho.theta_epsilon

        if fixed_phi:
            phi = fixed_phi
        else:
            phi = self.phi

        if fixed_r:
            r = fixed_r
        else:
            r = self.radius

        return theta, phi, r

    def get_cam_spherical_coords_only(self, theta, phi, r):
        return r * np.array([np.sin(theta) * np.cos(phi),
                             np.sin(theta) * np.sin(phi),
                             np.cos(theta)])

    def get_cam_coords(self, offset_theta=0., offset_phi=0., fixed_phi=None, fixed_theta=None, fixed_r=None, correct_for_camera_setting=False):
        """ """
        # get corrected quantities
        theta_c, phi_c, r_c = self.correct_cam_spherical_coords(fixed_phi, fixed_theta, fixed_r, correct_for_camera_setting)

        orbit_center = self.get_orbit_center()
        spherical_coords_only = self.get_cam_spherical_coords_only(theta_c + offset_theta, phi_c + offset_phi, r_c)

        return orbit_center + spherical_coords_only

    def set_orbit_center(self, orbit_center, not_just_init=True):
        """
        Args:
           orbit_center: Vec3 for the new orbit center """

        # print(type(orbit_center))
        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
        if orbit_center is not None:
            self._orbit_center = orbit_center

        if not_just_init == True:
            if self.visual_aids:
                self.visual_aids.update()

            self.update_camera_pos()
            self.set_pointlight_pos_spherical_coords()

    def get_orbit_center(self, numpy=True):
        """ 
        args:
            numpy: return in numpy or in p3d format """
        if self._orbit_center is not None:
            if numpy == True:
                return math_utils.p3d_to_np(self._orbit_center)
            else:
                # otherwise it should be Vec3
                return self._orbit_center
        else:
            print("self._orbit_center is None")
            exit(1)

    def get_eye_vector_1(self):
        """ """
        if self.on_other_side_p() == True:
            # in the case where -z is up, to provide visual consistency when flipping over
            return Vec3(-1., 0., 0.)
        else:
            return Vec3(1., 0., 0.)  # in the case where z is up

    def get_up_vector_1(self):
        """ """
        if self.on_other_side_p() == True:
            return Vec3(0., 0., -1)  # -z is up
        else:
            return Vec3(0., 0., 1.)  # z is up

    def update_camera_pos(self, fixed_phi=None, fixed_theta=None, fixed_r=None, # recalculate_film_size=True
                          on_init=False
    ):
        """ based on this class' internal variables """
        print("update_camera_pos")
        x, y, z = self.get_cam_coords(correct_for_camera_setting=True, fixed_phi=fixed_phi, fixed_theta=fixed_theta, fixed_r=fixed_r)
        self.camera.setPos(x, y, z)  # TODO: is this really necessary in addition to the setViewMatrix ?

        # eye_vector = self.get_eye_vector_1()
        # up_vector = self.get_up_vector_1()
        # self.camera.node().getLens().setViewMat(
        #     Mat4(eye_vector[0], 0, 0, 0, 0, 1, 0, 0, 0, 0, up_vector[2], 0, 0, 0, 0, 1))

        self.set_view_matrix_after_updated_camera_pos()

        self.set_film_size_from_window_dimensions()
        # self.camera.lookAt(self.get_orbit_center())

        self.run_camera_move_hooks()

    def set_view_matrix_after_updated_camera_pos(self):
        """ this arcball camera's eye and up vectors change upon
            change of spherical coordinates and offset change """


        # TOOD: work out what's right with the old and what's wrong with the new method
        # by inspecting the viewing matrix (for the old method also before and after an additional lookAt)

        # --- new method

        # eye = self.get_cam_pos()
        # print("eye: ", eye)

        # at = self.get_orbit_center()
        # print("at: ", at)

        # up = -math_utils.get_e_theta(self.theta, self.phi)
        # print("up: ", up)

        # vm = math_utils.get_lookat_view_matrix(eye, at, up)

        # vm_forrowvecs = math_utils.to_forrowvecs(vm)
        # vm_forrowvecs_tuple = np.ravel(vm_forrowvecs)

        # print("vm_forrowvecs: ", vm_forrowvecs)

        # self.camera.node().getLens().setViewMat(Mat4(*vm_forrowvecs_tuple))


        # --- old method

        eye_vector = self.get_eye_vector_1()
        # eye_vector = self.get_cam_pos()
        up_vector = self.get_up_vector_1()
        self.camera.node().getLens().setViewMat(
            Mat4(eye_vector[0], 0, 0, 0, 0, 1, 0, 0, 0, 0, up_vector[2], 0, 0, 0, 0, 1))

        self.camera.lookAt(Vec3(*self.get_orbit_center()))

    def set_view_to_xz_plane_and_reset_zoom(self):
        self.radius = self.radius_init
        self.set_view_to_xz_plane()

    def set_pointlight_pos_spherical_coords(self):
        x, y, z = self.get_cam_coords(offset_phi=np.pi/2.)
        self.pl_nodepath.setPos(x, y, z)
        # self.pl_nodepath.lookAt(self.get_orbit_center())

    def handle_wheel_up(self):
        self.phi = self.phi + 0.05
        self.update_camera_pos()
        self.set_pointlight_pos_spherical_coords()

    def handle_wheel_down(self):
        self.phi = self.phi - 0.05
        self.update_camera_pos()
        self.set_pointlight_pos_spherical_coords()

    def set_view_to_xy_plane(self):
        """ set view to the xy plane """
        self.phi = -np.pi/2.
        self.theta = 0.  # np.pi/2.
        # self.theta = OrbiterOrtho.theta_epsilon
        self.update_camera_pos()
        self.set_pointlight_pos_spherical_coords()

    def set_view_to_yz_plane(self):
        self.phi = 0.
        self.theta = np.pi/2.
        self.update_camera_pos()
        self.set_pointlight_pos_spherical_coords()

    def set_view_to_xz_plane(self):
        self.phi = -np.pi/2.
        self.theta = np.pi/2
        # self.theta = OrbiterOrtho.theta_epsilon
        self.update_camera_pos()
        self.set_pointlight_pos_spherical_coords()

    def handle_control_wheel_down(self):
        self.theta = self.theta - 0.05
        self.update_camera_pos()
        self.set_pointlight_pos_spherical_coords()

    def handle_control_wheel_up(self):
        # print("previous theta: \t", self.theta)
        self.theta = self.theta + 0.05
        # print("after setting theta: \t", self.theta)
        self.update_camera_pos()
        self.set_pointlight_pos_spherical_coords()
        # print("aftera updating theta: \t", self.theta)

    def handle_zoom_plus(self):
        print("zooming in")
        # to give an effective zoom effect in orthographic projection
        # the films size is adjusted and mapped (in update_camera_pos())
        # to self\.r + r_0
        self.radius = self.radius - 0.05
        self.update_camera_pos()
        self.set_pointlight_pos_spherical_coords()

    def handle_zoom_minus(self):
        print("zooming out")
        # to give an effective zoom effect in orthographic projection
        # the films size is adjusted and mapped (in update_camera_pos())
        # to self\.r + r_0
        self.radius = self.radius + 0.05
        # print("r: ", self.radius)
        self.update_camera_pos()
        self.set_pointlight_pos_spherical_coords()

    def add_camera_move_hook(self, func):
        """ func is the function to run when the camera moves;
        if it depends on parameters, they can be set upon adding
        the hook by just using a lambda function """
        self.camera_move_hooks.append(func)

    def remove_camera_move_hook(self, func):
        """ remove the hook """
        self.camera_move_hooks.remove(func)

    def run_camera_move_hooks(self):
        for c_hook in self.camera_move_hooks:
            # run the function
            c_hook()

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

    def set_film_size_from_window_dimensions(self, called_from_orbiter_init=False):
        """ """
        print("set_film_size_from_window_dimensions called, self.radius=", self.radius)

        aspect_ratio = None
        if self.before_aspect_ratio_changed_at_init == True or called_from_orbiter_init == True:
            aspect_ratio = conventions.winsizex_0/conventions.winsizey_0

            if called_from_orbiter_init == False:
                self.before_aspect_ratio_changed_at_init = False
        else:
            aspect_ratio = engine.tq_graphics_basics.get_window_aspect_ratio()
            # print("aspect ratio : ", aspect_ratio)
            # print(engine.tq_graphics_basics.get_window_size_x(),
            #       engine.tq_graphics_basics.get_window_size_y())
            # self.set_orthographic_zoom(None, 2. * aspect_ratio)
            scale_factor = 1./(conventions.winsizey_0/2.)

            scale_factor *= self.convert_r_to_filmsize_offset_scale_factor()

            filmsize_x = engine.tq_graphics_basics.get_window_size_x()*scale_factor
            filmsize_y = engine.tq_graphics_basics.get_window_size_y()*scale_factor

            print("filmsize_x, filmsize_y: ", filmsize_x, filmsize_y)

            print("not at init")
            self.lens.setFilmSize(filmsize_x, filmsize_y)
            self.lens.setNearFar(-500., 500.)

            # if base.mouseWatcherNode.hasMouse():
            #     print("get_coords_2d_for_mouse_zoom: ", self.get_coords_2d_for_mouse_zoom())

    def convert_r_to_filmsize_offset_scale_factor(self):
        return self.radius/OrbiterOrtho.r0

    def scale_aspect2d_from_window_dimensions(self):
        """ when window dimensions change by resizing the window, I want the aspect2d viewport to scale with it, so that
            e.g. fonts attached to it stay the same size w.r.t the screen """

        # engine.tq_graphics_basics.tq_aspect2d.
        # print("getMat p3d native format: \n", aspect2d.getMat())
        # print("getMat from_forrowvecs: \n",
        #       math_utils.from_forrowvecs(aspect2d.getMat()))

        T, R, S = math_utils.decompose_affine_trafo_4x4(
            math_utils.from_forrowvecs(aspect2d.getMat()))
        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

        # S = np.array([[0.5497, 0.,     0.,     0.],
        #               [0.,     1.,     0.,     0.],
        #               [0.,     0.,     1.,     0.],
        #               [0.,     0.,     0.,     1.]])

        # aspect2d.setMat(math_utils.to_forrowvecs(T.dot(R).dot(S)))


        # render2d.setPos

        # scale = 1./(engine.tq_graphics_basics.get_window_size_y()/conventions.winsizey_0)
        # aspect2d.setScale(scale,
        #                   1.,
        #                   scale)

        aspect2d.setScale(conventions.winsizex_0/engine.tq_graphics_basics.get_window_size_x() * 1./(conventions.winsizex_0/conventions.winsizey_0),
                          1.,
                          conventions.winsizey_0/engine.tq_graphics_basics.get_window_size_y())

        aspect2d.setPos(-1 + conventions.winsizex_0/engine.tq_graphics_basics.get_window_size_x() * 1./(conventions.winsizex_0/conventions.winsizey_0),
                        0.,
                        1 - conventions.winsizey_0/engine.tq_graphics_basics.get_window_size_y())

        # print("window sizes: ", engine.tq_graphics_basics.get_window_size_x(),
        #       engine.tq_graphics_basics.get_window_size_y())

        # aspect2d.setScale(1., 1., 1.)
        # aspect2d.setScale(1./400, 1, 1./300)

    def get_cam_forward_vector_normalized(self):
        v_cam_forward = math_utils.p3d_to_np(
            engine.tq_graphics_basics.tq_render.getRelativeVector(
            self.camera, self.camera.node().getLens().getViewVector()))

        return v_cam_forward / np.linalg.norm(v_cam_forward)

    def get_cam_up_vector_normalized(self):
        v_cam_up = math_utils.p3d_to_np(engine.tq_graphics_basics.tq_render.getRelativeVector(self.camera, self.camera.node().getLens().getUpVector()))
        return v_cam_up / np.linalg.norm(v_cam_up)

    def get_cam_pos(self):
        return math_utils.p3d_to_np(self.camera.getPos())

    def get_e_x_prime(self):
        return math_utils.p3d_to_np(np.cross(self.get_cam_forward_vector_normalized(), self.get_cam_up_vector_normalized()))

    def get_e_y_prime(self):
        return self.get_cam_up_vector_normalized()

    # --- for zooming orthographically

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
        print("Ortho Lens Film: ", "width: ", width, ", height: ", height)
        # setFilmSize specifies the size of the Lens box
        # I call it a *viewing box* if the projection matrix produces
        # orthogonal projection, and *viewing frustum* if the projection
        # matrix includes perspective)
        self.lens.setFilmSize(width, height)

        print("-------- self.lens.setFilmSize(width, height): ", width, height)

        self.width = width
        self.height = height

    def getOrthoLensRange(self):
        """ when calling mouse_pos = self.base.mouseWatcherNode.getMouse(),
        then mouse_pos is a 2d point in the range (-1, 1), (-1, 1).
        To get the position relative to the film size (for my custom orthogonal
        lens), """
        return self.width, self.height

    def get_coords_2d_for_mouse_zoom(self):
        """ mouse_pos as returned from base.mouseWatcherNode.getMouse()
            # planeNormal, planePoint, rayDirection, rayPoint
            """
        mouse_pos = base.mouseWatcherNode.getMouse()
        print("mouse_pos: ", mouse_pos[0], mouse_pos[1])
        mouse_p_x, mouse_p_y = conventions.getFilmCoordsFromMouseCoords(mouse_pos[0], mouse_pos[1]  # , self.p_xy_at_init_drag[0], self.p_xy_at_init_drag[1]
        )
        # print("self.p_xy_at_init_drag: ", self.p_xy_at_init_drag)
        print("mouse_p_x, mouse_p_y: ", mouse_p_x, mouse_p_y)

        cam_pos = self.get_cam_pos()
        # print("cam_pos: ", cam_pos)
        r0_shoot = (cam_pos +  # camera position
                    self.get_e_x_prime() * mouse_p_x + self.get_e_y_prime() * mouse_p_y  # camera plane
                    )

        # print("self.get_e_y_prime(): ", self.get_e_y_prime())
        # print("self.get_e_x_prime(): ", self.get_e_x_prime())

        # print("r0_shoot: ", r0_shoot)
        print("self.get_cam_up_vector_normalized(): ", self.get_cam_up_vector_normalized())

        # planeNormal, planePoint, rayDirection, rayPoint
        r = math_utils.LinePlaneCollision(self.get_cam_forward_vector_normalized(), self.get_cam_pos(), self.get_cam_forward_vector_normalized(), r0_shoot)

        # print("self.get_cam_forward_vector_normalized():, ", self.get_cam_forward_vector_normalized())
        # print("r: ", r)

        in_plane_vec = r - self.get_cam_pos()

        x1 = np.dot(self.get_e_x_prime(), in_plane_vec)
        x2 = np.dot(self.get_e_y_prime(), in_plane_vec)

        # print("x1, x2: ", x1, x2)
        return np.array([x1, x2])
