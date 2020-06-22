import numpy as np

from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

class Orbiter:
    def __init__(self):
        base.disableMouse()
        self.orbit_center = Vec3(0., 0., 0.)
        self.r = 2.
        self.phi = 0.
        self.theta = np.pi/3.

        # --- hooks for camera movement
        self.camera_move_hooks = []  # store function objects

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


        # # -- fix 2 point lights to the camera at opposite positions
        # --- fix a point light to the camera
        from panda3d.core import PointLight
        self.plight = PointLight('plight')
        self.plnp = render.attachNewNode(self.plight)
        self.set_pointlight_pos_spherical_coords()
        render.setLight(self.plnp)

        # # --- fix a point light to the camera
        # from panda3d.core import PointLight
        # self.plight2 = PointLight('plight2')
        # self.plnp2 = render.attachNewNode(self.plight2)
        # self.set_pointlight_pos_spherical_coords()
        # render.setLight(self.plnp2)

    def get_spherical_coords(self, offset_r=0., offset_theta=0., offset_phi=0., prevent_overtop_flipping=False, fixed_phi=None, fixed_theta=None, fixed_r=None):
        print("theta = ", self.theta, ", " "phi = ", self.phi)

        # prevent over-the-top flipping
        # self.theta = self.theta % np.pi

        if prevent_overtop_flipping:  # useful for the camera
            if self.theta > np.pi:
                self.theta = np.pi - 0.0001
            if self.theta < 0.:
                self.theta = 0. + 0.0001

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
        base.cam.lookAt(self.orbit_center)

        self.run_camera_move_hooks()


    def set_pointlight_pos_spherical_coords(self):
        x, y, z = self.get_spherical_coords(offset_phi=np.pi/2.)
        self.plnp.setPos(x, y, z)
        self.plnp.lookAt(self.orbit_center)

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

    def handle_control_wheel_down(self):
        self.theta = self.theta - 0.1
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

    def handle_control_wheel_up(self):
        self.theta = self.theta + 0.1
        self.set_camera_pos_spherical_coords()
        self.set_pointlight_pos_spherical_coords()

    def add_camera_move_hook(self, func):
        """ func is the function to run when the camera moves;
        if it depends on parameters, they can be set upon adding
        the hook by just using a lambda function """
        self.camera_move_hooks.append(func)

    def run_camera_move_hooks(self):
        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
        for c_hook in self.camera_move_hooks:
            # run the function
            c_hook()
