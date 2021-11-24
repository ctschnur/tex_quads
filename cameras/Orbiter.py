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


class OrbiterLens:
    """ an Orbiter instance has an OrbiterLens to zoom
        with orthographic projection (then, the lens has to
        be modified, i.e. the FilmSize) """

    def __init__(self,
                 # lookat_position=Vec3(0,0,0),
                 # camera_position=Vec3(5, 5, 2)
                 camera
                 ):
        self.camera = camera
        self.lens = OrthographicLens()
        print("self.lens : ", self.lens)
        self.setOrthoLensRange(None, 5.)  # only initially!
        # ^ the point is to change this interactively

        self.lens.setNearFar(0.001, 50.)

        # you can also check for the properties of your lens/camera
        print("OrbiterLens: orthographic: ", self.lens.isOrthographic())
        # finally, set the just created Lens() to your main camera
        self.camera.node().setLens(self.lens)

        # Make sure that what you want to display is within the Lenses box
        # (beware of near and far planes)
        # Since it's orthogonal projection, letting the camera's position
        # vary doesn't do anything to the displayed content (except maybe
        # hiding it beyond the near/far planes)

        # self.camera.setPos(camera_position[0], camera_position[1], camera_position[2])  # this manipulates the viewing matrix

        # self.camera.lookAt(self.orbit_center)  # this manipulates the viewing matrix

        # self.set_camera_pos_spherical_coords()

    def setOrthoLensRange(self, width, height):
        """ an orthographic lens' `zoom`
            is controlled by the film size
        Parameters:
        width  -- width of the orthographic lens in world coordinates
        height -- height ---------------- '' ------------------------
        """

        if width is None and height:
            width = height * engine.tq_graphics_basics.get_window_aspect_ratio()
        elif height is None:
            print("ERR: height is None")
            exit(1)

        width = height * engine.tq_graphics_basics.get_window_aspect_ratio()
        # print("Ortho Lens Film: ", "width: ", width, ", height: ", height)
        # setFilmSize specifies the size of the Lens box
        # I call it a *viewing box* if the projection matrix produces
        # orthogonal projection, and *viewing frustum* if the projection
        # matrix includes perspective)
        self.lens.setFilmSize(width, height)

        self.width = width
        self.height = height

    def getOrthoLensRange(self):
        """ when calling mouse_pos = self.base.mouseWatcherNode.getMouse(),
        then mouse_pos is a 2d point in the range (-1, 1), (-1, 1).
        To get the position relative to the film size (for my custom orthogonal
        lens), """
        return self.width, self.height


class Orbiter:
    """ """

    # when flipping over, the eye vector and z-vector are multiplied by -1.
    # but still, to prevent graphics glitches in the situation where
    # the lookat vector and view vector are perfectly aligned ("theta = 0"),
    # theta_epsilon provides a small but visually unnoticeable offset
    # theta_epsilon = 1.0e-10
    theta_epsilon = 1.0e-5

    def __init__(self, camera, radius=2., enable_visual_aids=True):
        base.disableMouse()

        self.orbit_center = None
        self.set_orbit_center(Vec3(0., 0., 0.), not_just_init=False)

        self.before_aspect_ratio_changed_at_init = True

        self.r = radius
        self.phi = 0.
        self.theta = np.pi/3.

        # camera stuff
        self.camera = camera

        # --- hooks for camera movement
        self.camera_move_hooks = []  # store function objects

        # --- hooks for window resize
        self.window_resize_hooks = []  # store function objects

        # --- set the lens
        self.orbiterLens = OrbiterLens(camera)

        # --- initial setting of the position
        self.set_camera_pos_spherical_coords(recalculate_film_size=True)

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
        base.accept('1', self.set_view_to_xz_plane)
        base.accept('3', self.set_view_to_yz_plane)
        base.accept('7', self.set_view_to_xy_plane)

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

        self.ddem.add_on_state_change_function(Orbiter.set_new_panning_orbit_center_from_dragged_mouse,
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

    def get_spherical_coords(self, offset_r=0., offset_theta=0., offset_phi=0.,
                             fixed_phi=None, fixed_theta=None, fixed_r=None, get_up_vector=False, get_eye_vector=False, correct_for_camera_setting=False):
        """ """
        # print("theta = ", self.theta, ", ",
        #       "phi = ", self.phi, ", ",
        #       "r = ", self.r)

        # prevent over-the-top flipping
        # self.theta = self.theta % np.pi

        # keep r positive
        if self.r < 0:
            self.r = 0.001

        # # keep phi in the range [0, 2*pi]
        # if self.phi > 2.*np.pi:
        #     self.phi = self.phi % 2.*np.pi
        # elif self.phi < 0.:
        #     self.phi = self.phi + 2.*np.pi
        # elif self.phi > 2.*np.pi:
        #     self.phi = self.phi - 2.*np.pi

        on_other_side = self.theta % (2. * np.pi) > np.pi

        theta = None
        phi = None
        r = None

        if fixed_theta:
            theta = fixed_theta
        else:
            theta = self.theta

        if correct_for_camera_setting == True:
            if theta % np.pi < Orbiter.theta_epsilon:
                theta = theta + Orbiter.theta_epsilon

        if fixed_phi:
            phi = fixed_phi
        else:
            phi = self.phi

        if fixed_r:
            r = fixed_r
        else:
            r = self.r

        orbit_center = self.get_orbit_center()
        x = (orbit_center[0] +
             self.r * np.sin(theta + offset_theta) * np.cos(phi + offset_phi))
        y = (orbit_center[1] +
             self.r * np.sin(theta + offset_theta) * np.sin(phi + offset_phi))
        z = (orbit_center[2] +
             self.r * np.cos(theta + offset_theta))

        returnval = [x, y, z]

        if get_up_vector == True:
            if on_other_side == True:
                returnval.append(Vec3(0., 0., -1))  # -z is up
            else:
                returnval.append(Vec3(0., 0., 1.))  # z is up

        if get_eye_vector == True:
            if on_other_side == True:
                # in the case where -z is up, to provide visual consistency when flipping over
                returnval.append(Vec3(-1., 0., 0.))
            else:
                returnval.append(Vec3(1., 0., 0.))  # in the case where z is up

        return returnval

    def set_orbit_center(self, orbit_center, not_just_init=True):
        """
        Args:
           orbit_center: Vec3 for the new orbit center """

        # print(type(orbit_center))
        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
        if orbit_center is not None:
            self.orbit_center = orbit_center

        if not_just_init == True:
            if self.visual_aids:
                self.visual_aids.update()

            self.set_camera_pos_spherical_coords()
            self.set_pointlight_pos_spherical_coords()

    def get_orbit_center(self):
        """ """
        if self.orbit_center is not None:
            return self.orbit_center

        else:
            print("self.orbit_center is None")
            exit(1)

    def set_camera_pos_spherical_coords(self, recalculate_film_size=False):
        x, y, z, up_vector, eye_vector = self.get_spherical_coords(
            get_up_vector=True, get_eye_vector=True, correct_for_camera_setting=True)

        # if math_utils.equal_up_to_epsilon(x, 0., epsilon=) and math_utils.equal_up_to_epsilon(y, 0.):

        self.camera.setPos(x, y, z)
        # self.camera.node().getLens().setViewMat(Mat4(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))

        self.camera.node().getLens().setViewMat(
            Mat4(eye_vector[0], 0, 0, 0, 0, 1, 0, 0, 0, 0, up_vector[2], 0, 0, 0, 0, 1))

        # if self.before_aspect_ratio_changed_at_init == True:
        #     self.orbiterLens.setOrthoLensRange(None, self.get_ortho_lense_range_to_height_from_radius_contrib())
        # else:
        #     self.orbiterLens.setOrthoLensRange(None, self.get_ortho_lense_range_to_height_from_radius_contrib())

        # base the film size on the window dimensions, not on the radius of the camera around the orbit center

        if recalculate_film_size == True:
            self.set_film_size_from_window_dimensions()

        self.camera.lookAt(self.get_orbit_center())
        self.run_camera_move_hooks()

    def get_ortho_lense_range_to_height_from_radius_contrib(self):
        """ """
        return self.r + 0.1

    def set_pointlight_pos_spherical_coords(self):
        x, y, z = self.get_spherical_coords(offset_phi=np.pi/2.)
        self.pl_nodepath.setPos(x, y, z)
        self.pl_nodepath.lookAt(self.get_orbit_center())

    def handle_wheel_up(self):
        self.phi = self.phi + 0.05
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

    def handle_wheel_down(self):
        self.phi = self.phi - 0.05
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

    def set_view_to_xy_plane(self):
        """ set view to the xy plane """
        self.phi = -np.pi/2.
        self.theta = 0.  # np.pi/2.
        # self.theta = Orbiter.theta_epsilon
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

    def set_view_to_yz_plane(self):
        self.phi = 0.
        self.theta = np.pi/2.
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

    def set_view_to_xz_plane(self):
        self.phi = -np.pi/2.
        self.theta = np.pi/2
        # self.theta = Orbiter.theta_epsilon
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

    def handle_control_wheel_down(self):
        self.theta = self.theta - 0.05
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

    def handle_control_wheel_up(self):
        # print("previous theta: \t", self.theta)
        self.theta = self.theta + 0.05
        # print("after setting theta: \t", self.theta)
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()
        # print("aftera updating theta: \t", self.theta)

    def handle_zoom_plus(self):
        # print("plus pressed")
        # to give an effective zoom effect in orthographic projection
        # the films size is adjusted and mapped (in set_camera_pos_spherical_coords())
        # to self\.r + r_0
        self.r = self.r - 0.05
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

    def handle_zoom_minus(self):
        # print("minus pressed")
        # to give an effective zoom effect in orthographic projection
        # the films size is adjusted and mapped (in set_camera_pos_spherical_coords())
        # to self\.r + r_0
        self.r = self.r + 0.05
        self.set_camera_pos_spherical_coords()
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

    def get_lens(self):
        """ get my lens """
        return self.orbiterLens

    def set_film_size_from_window_dimensions(self, called_from_orbiter_init=False):
        """ """
        # print("aspect ratio changed")

        aspect_ratio = None
        if self.before_aspect_ratio_changed_at_init == True or called_from_orbiter_init == True:
            # print("self.before_aspect_ratio_changed_at_init : ",
            #       self.before_aspect_ratio_changed_at_init)
            aspect_ratio = conventions.winsizex_0/conventions.winsizey_0

            if called_from_orbiter_init == False:
                self.before_aspect_ratio_changed_at_init = False
        else:
            # print("self.before_aspect_ratio_changed_at_init : ",
            #       self.before_aspect_ratio_changed_at_init)
            aspect_ratio = engine.tq_graphics_basics.get_window_aspect_ratio()
            # print("aspect ratio : ", aspect_ratio)
            # print(engine.tq_graphics_basics.get_window_size_x(),
            #       engine.tq_graphics_basics.get_window_size_y())
            # self.lens.setOrthoLensRange(None, 2. * aspect_ratio)

            # scale_factor = 1./320. # engine.tq_graphics_basics.get_window_size_y()
            # engine.tq_graphics_basics.get_window_size_y()
            scale_factor = 1./(conventions.winsizey_0/2.)
            # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

            # offset = self.get_ortho_lense_range_to_height_from_radius_contrib()
            # offset = 0
            # print("offset: ", offset)

            filmsize_x = engine.tq_graphics_basics.get_window_size_x()*scale_factor
            filmsize_y = engine.tq_graphics_basics.get_window_size_y()*scale_factor

            # filmsize_y += float(filmsize_x) % float(self.get_ortho_lense_range_to_height_from_radius_contrib())

            self.get_lens().lens.setFilmSize(filmsize_x, filmsize_y)

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

    def get_cam_forward_normal_vector(self):
        v_cam_forward = math_utils.p3d_to_np(
            engine.tq_graphics_basics.tq_render.getRelativeVector(
            self.camera, self.camera.node().getLens().getViewVector()))

        return v_cam_forward / np.linalg.norm(v_cam_forward)

    def get_cam_up_normal_vector(self):
        v_cam_up = math_utils.p3d_to_np(engine.tq_graphics_basics.tq_render.getRelativeVector(self.camera, self.camera.node().getLens().getUpVector()))
        return v_cam_up / np.linalg.norm(v_cam_up)

    def get_cam_pos(self):
        return math_utils.p3d_to_np(self.camera.getPos())

    def get_e_x_prime(self):
        return math_utils.p3d_to_np(np.cross(self.get_cam_forward_normal_vector(), self.get_cam_up_normal_vector()))

    def get_e_y_prime(self):
        # v_cam_forward_vec = self.get_cam_forward_normal_vector()
        # v_cam_forward_normal_vec = v_cam_forward_vec/np.linalg.norm(v_cam_forward_vec)

        # print("v_cam_forward_normal_vec: ", v_cam_forward_normal_vec)

        # e_x = self.get_cam_up_normal_vector()
        # return -math_utils.p3d_to_np(np.cross(v_cam_forward_normal_vec, e_x))

        return self.get_cam_up_normal_vector()

    # def get_shoot_pos_from_mouse(self, mouse_pos_x, mouse_pos_y):
    #     """ clicking on the screen, this is the position of the point in the
    #         camera plane (orthogonal lens) where the mouse is pointing at.
    #         args:
    #             mouse_pos_x(or y): -1 (-1), to 1 (1) lower left (upper right) corner of the window """

    #     cam_pos = self.get_cam_pos()
