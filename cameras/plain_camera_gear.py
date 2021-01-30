from conventions import conventions

import numpy as np

from direct.showbase.ShowBase import ShowBase, DirectObject, KeyboardButton
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval
from direct.task import Task
from panda3d.core import ModifierButtons

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

class PlainCameraGearLens:
    """ a camera gear instance has an lense to zoom
        with orthographic projection (then, the lens has to
        be modified, i.e. the FilmSize) """

    def __init__(self,
                 camera
                 ):
        self.camera = camera
        self.lens = OrthographicLens()
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

        base.mouseWatcherNode.setModifierButtons(ModifierButtons())

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


class PlainCameraGear():
    """ """
    def __init__(self, camera):
        """ """
        base.disableMouse()

        self.camera = camera
        self.lens = PlainCameraGearLens(self.camera)

        self.set_camera_pos()

    def set_camera_pos(self):
        """ """
        self.camera.setPos(0., 0., 0.)
        self.camera.node().getLens().setViewMat(Mat4(1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1))

        # self.camera.node().getLens().setViewMat(
        #     Mat4(eye_vector[0], 0, 0, 0, 0, 1, 0, 0, 0, 0, up_vector[2], 0, 0, 0, 0, 1))

        self.lens.setOrthoLensRange(None, 2.)

        self.camera.lookAt(Vec3(0., 0., 0.))

    def setPos(self, *args, **kwargs):
        """ """
        return self.camera.setPos(*args, **kwargs)

    def get_lens(self):
        """ get my lens """
        return self.lens
