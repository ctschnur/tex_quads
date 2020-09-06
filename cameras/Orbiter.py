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

class OrbiterLens:
    """ an Orbiter instance has an OrbiterLens to zoom
        with orthographic projection (then, the lens has to
        be modified, i.e. the FilmSize) """
    def __init__(self,
                 # lookat_position=Vec3(0,0,0),
                 # camera_position=Vec3(5, 5, 2)
    ):
        self.lens = OrthographicLens()

        self.setOrthoLensRange(None, 5.)  # only initially!
        # ^ the point is to change this interactively

        self.lens.setNearFar(0.001, 50.)

        # you can also check for the properties of your lens/camera
        print("OrbiterLens: orthographic: ", self.lens.isOrthographic())
        # finally, set the just created Lens() to your main camera
        base.cam.node().setLens(self.lens)

        # Make sure that what you want to display is within the Lenses box
        # (beware of near and far planes)
        # Since it's orthogonal projection, letting the camera's position
        # vary doesn't do anything to the displayed content (except maybe
        # hiding it beyond the near/far planes)

        # base.cam.setPos(camera_position[0], camera_position[1], camera_position[2])  # this manipulates the viewing matrix

        # base.cam.lookAt(self.orbit_center)  # this manipulates the viewing matrix

        # self.set_camera_pos_spherical_coords()

    def setOrthoLensRange(self, width, height):
        """ an orthographic lens' `zoom`
            is controlled by the film size
        Parameters:
        width  -- width of the orthographic lens in world coordinates
        height -- height ---------------- '' ------------------------
        """

        if width is None and height:
            width = height * (conventions.winsizex/conventions.winsizey)
        elif height is None:
            print("ERR: height is None")
            exit(1)

        width = height * (conventions.winsizex/conventions.winsizey)
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
    def __init__(self, camera, radius=2.):
        base.disableMouse()
        self.orbit_center = Vec3(0., 0., 0.)
        self.r = radius
        self.phi = 0.
        self.theta = np.pi/3.


        # camera stuff
        self.camera = camera

        # --- hooks for camera movement
        self.camera_move_hooks = []  # store function objects

        # --- set the lens
        self.orbiterLens = OrbiterLens()

        # --- initial setting of the position
        self.set_camera_pos_spherical_coords()

        # --- event handling to reorient the camera
        from panda3d.core import ModifierButtons
        base.mouseWatcherNode.setModifierButtons(ModifierButtons())

        from direct.showbase.ShowBase import DirectObject

        # changing phi
        myDirectObject = DirectObject.DirectObject()
        myDirectObject.accept('wheel_down', self.handle_wheel_down)

        myDirectObject = DirectObject.DirectObject()
        myDirectObject.accept('wheel_up', self.handle_wheel_up)

        # changing theta
        myDirectObject = DirectObject.DirectObject()
        myDirectObject.accept('control-wheel_down', self.handle_control_wheel_down)

        myDirectObject = DirectObject.DirectObject()
        myDirectObject.accept('control-wheel_up', self.handle_control_wheel_up)

        # 'changing r' (although that's not what directly changes the 'zoom' in an ortho lens)
        myDirectObject = DirectObject.DirectObject()
        myDirectObject.accept('shift-wheel_up', self.handle_zoom_plus)

        myDirectObject = DirectObject.DirectObject()
        myDirectObject.accept('shift-wheel_down', self.handle_zoom_minus)

        # polling for zoom is better than events
        self.plus_button = KeyboardButton.ascii_key('+')
        self.minus_button = KeyboardButton.ascii_key('-')
        # taskMgr.add(self.poll_zoom_plus_minus, 'Zoom')


        # pressing 1, 3, 7 makes you look straight at the origin from y, x, z axis
        myDirectObject = DirectObject.DirectObject()
        myDirectObject.accept('1', self.set_view_to_xy_plane)

        myDirectObject = DirectObject.DirectObject()
        myDirectObject.accept('3', self.set_view_to_yz_plane)

        myDirectObject = DirectObject.DirectObject()
        myDirectObject.accept('7', self.set_view_to_xz_plane)

        # myDirectObject = DirectObject.DirectObject()
        # myDirectObject.accept('wheel_up', self.handle_wheel_up)


        # --- fix a point light to the side of the camera
        from panda3d.core import PointLight
        self.plight = PointLight('plight')
        self.pl_nodePath = render.attachNewNode(self.plight)
        self.set_pointlight_pos_spherical_coords()
        render.setLight(self.pl_nodePath)

        # -- set faint ambient white lighting
        from panda3d.core import AmbientLight
        self.alight = AmbientLight('alight')
        self.alnp = render.attachNewNode(self.alight)
        self.alight.setColor((0.35, 0.35, 0.35, 1))
        render.setLight(self.alnp)

    def poll_zoom_plus_minus(self, task):

        is_down = base.mouseWatcherNode.is_button_down

        if is_down(self.plus_button):
            self.handle_zoom_plus()

        if is_down(self.minus_button):
            self.handle_zoom_minus()

        return task.cont

    def get_spherical_coords(self, offset_r=0., offset_theta=0., offset_phi=0.,
                             prevent_overtop_flipping=False,
                             fixed_phi=None, fixed_theta=None, fixed_r=None):
        # print("theta = ", self.theta, ", ",
        #       "phi = ", self.phi, ", ",
        #       "r = ", self.r)

        # prevent over-the-top flipping
        # self.theta = self.theta % np.pi

        if prevent_overtop_flipping:  # useful for the camera
            if self.theta > np.pi:
                self.theta = np.pi - 0.0001
            if self.theta < 0.:
                self.theta = 0. + 0.0001


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

        theta = None
        phi = None
        r = None

        if fixed_theta:
            theta = fixed_theta
        else:
            theta = self.theta

        if fixed_phi:
            phi = fixed_phi
        else:
            phi = self.phi

        if fixed_r:
            r = fixed_r
        else:
            r = self.r

        x = (self.orbit_center[0] +
             self.r * np.sin(theta + offset_theta) * np.cos(phi + offset_phi))
        y = (self.orbit_center[1] +
             self.r * np.sin(theta + offset_theta) * np.sin(phi + offset_phi))
        z = (self.orbit_center[2] +
             self.r * np.cos(theta + offset_theta))

        return x, y, z

    def set_camera_pos_spherical_coords(self):
        x, y, z = self.get_spherical_coords(prevent_overtop_flipping=True)
        base.cam.setPos(x, y, z)
        self.orbiterLens.setOrthoLensRange(None, self.r + 0.1)
        base.cam.lookAt(self.orbit_center)
        self.run_camera_move_hooks()


    def set_pointlight_pos_spherical_coords(self):
        x, y, z = self.get_spherical_coords(offset_phi=np.pi/2.)
        self.pl_nodePath.setPos(x, y, z)
        self.pl_nodePath.lookAt(self.orbit_center)

    def handle_wheel_up(self):
        self.phi = self.phi + 0.1
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

    def handle_wheel_down(self):
        self.phi = self.phi - 0.1
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

        # from pandac.PandaModules import KeyboardButton
        # upArrowIsPressed = base.mouseWatcherNode.isButtonDown(KeyboardButton.up())
        # wIsPressed = base.mouseWatcherNode.isButtonDown(KeyboardButton.asciiKey("w"))

        # print("wIsPressed: ", wIsPressed)

    def set_view_to_xy_plane(self):
        self.phi = np.pi/2.
        self.theta = 0.  # np.pi/2.
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

    def set_view_to_yz_plane(self):
        self.phi = 0.
        self.theta = np.pi/2.
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

    def set_view_to_xz_plane(self):
        self.phi = -np.pi/2.
        self.theta = 0.
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

    def handle_control_wheel_down(self):
        self.theta = self.theta - 0.1
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

    def handle_control_wheel_up(self):
        self.theta = self.theta + 0.1
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

    def handle_zoom_plus(self):
        # print("plus pressed")
        # to give an effective zoom effect in orthographic projection
        # the films size is adjusted and mapped (in set_camera_pos_spherical_coords())
        # to self\.r + r_0
        self.r = self.r - 0.1
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

    def handle_zoom_minus(self):
        # print("minus pressed")
        # to give an effective zoom effect in orthographic projection
        # the films size is adjusted and mapped (in set_camera_pos_spherical_coords())
        # to self\.r + r_0
        self.r = self.r + 0.1
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

    def add_camera_move_hook(self, func):
        """ func is the function to run when the camera moves;
        if it depends on parameters, they can be set upon adding
        the hook by just using a lambda function """
        self.camera_move_hooks.append(func)

    def run_camera_move_hooks(self):

        for c_hook in self.camera_move_hooks:
            # run the function
            c_hook()
