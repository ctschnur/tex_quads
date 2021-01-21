import engine

import numpy as np
import math

from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

from plot_utils.quad import Quad
from conventions.conventions import win_aspect_ratio

from simple_objects.primitives import ParametricLinePrimitive

import numpy as np
import scipy.special

from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk

class Frame2d():
    """ a 2d frame within which 2d data can be displayed, i.e. numpy x and y arrays """
    def __init__(self):
        """ """
        self.quad = None

        size = 0.2
        self.height = size
        self.width = size * 1.618

        x_start_pos = 1.0 * win_aspect_ratio - self.width - 0.05
        y_start_pos = -0.75
        # y_spacing = 0.05

        self.x_pos_left_border = x_start_pos
        self.y_pos_top_box = y_start_pos

        self.quad = Quad(thickness=2.0, TQGraphicsNodePath_creation_parent_node=engine.tq_graphics_basics.tq_aspect2d)
        self.quad.set_pos_vec3(Vec3(self.x_pos_left_border, 0., self.y_pos_top_box))

        self.quad.set_height(self.height)
        self.quad.set_width(self.width)

        self.plp1 = None

        self.update_parametric_line(lambda t: np.array([
                    np.cos(t*(2.*np.pi)*1.),
                    np.sin(t*(2.*np.pi)*1.),
                ]))

        # self.plp1.remove()

        point = Point3d(pos=(Vec3(1., 0., 1.)), TQGraphicsNodePath_creation_parent_node=engine.tq_graphics_basics.tq_aspect2d)
        pass

    def update_parametric_line(self, func_xy_of_t=None):
        """ """
        if func_xy_of_t is not None:
            self.plp1 = ParametricLinePrimitive(
                lambda t: np.array([func_xy_of_t(t)[0], 0., func_xy_of_t(t)[1]]),
                howmany_points=100, TQGraphicsNodePath_creation_parent_node=engine.tq_graphics_basics.tq_aspect2d)

            self.plp1.setPos(self.quad.get_pos_vec3())
            print("hi")

            # lambda t: np.array([
            #         np.cos(t*(2.*np.pi)*1.),
            #         0,
            #         np.sin(t*(2.*np.pi)*1.),
            #     ])

        else:
            if self.plp1 is not None:
                self.plp1.remove()

    def remove():
        """ """
        self.quad.remove()
