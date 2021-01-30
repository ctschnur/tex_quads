import engine
import engine.tq_graphics_basics
from engine.tq_graphics_basics import TQGraphicsNodePath

import numpy as np
import math

from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

from plot_utils.quad import Quad

from simple_objects.primitives import ParametricLinePrimitive

import numpy as np
import scipy.special

from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, Fixed2dLabel
from local_utils import math_utils


class Tick(TQGraphicsNodePath):
    """ Line and (optionally) Label """
    def __init__(self):
        """ """
        TQGraphicsNodePath.__init__(self)

        self.line = None
        self.label = None

    def set_line(self, line):
        """ """
        self.line = line
        self.line.reparentTo(self)

    def set_label(self, label):
        """ """
        self.label = label
        self.label.reparentTo(self)

class Ticks(TQGraphicsNodePath):
    """ """
    def __init__(self, arr=np.array([0., 0.25, 0.5, 0.75, 1.])):
        """
        Args:
            arr: numbers at which to create the tick lines """
        TQGraphicsNodePath.__init__(self)

        self.arr = None

        # self.lines = []
        self.ticks = []
        self.tick_length = 0.05

        self.set_ticks_by_arr(arr)

    def remove_all_ticks(self):
        """ """
        # for line in self.lines:
        #     line.remove()
        for tick in self.ticks:
            tick.remove()

    def set_ticks_by_arr(self, arr):
        """ pass an array, generate a bunch of vertical lines """
        self.remove_all_ticks()
        self.arr = arr

        for c_num in self.arr:
            x = c_num

            line = Line1dSolid(thickness=1.0)
            line.setTipPoint(Vec3(x, 0., self.tick_length/2.))
            line.setTailPoint(Vec3(x, 0., -self.tick_length/2.))

            label = Fixed2dLabel(text=str(c_num)) # offset
            label.reparentTo(self)

            t = Tick()
            t.set_line(line)
            t.set_label(label)
            t.reparentTo(self)

            self.ticks.append(t)

            # self.lines.append(l)

class Frame2d(TQGraphicsNodePath):
    """ a 2d frame within which 2d data can be displayed, i.e. numpy x and y arrays """
    def __init__(self):
        """ """
        TQGraphicsNodePath.__init__(self)

        self.quad = None

        size = 0.5
        self.height = size
        self.width = size * 1.618

        self.pos_x = 0.2
        self.pos_y = 0.1

        x_start_pos = 1.0 * engine.tq_graphics_basics.get_window_aspect_ratio() - self.width - 0.05
        y_start_pos = -0.75
        # y_spacing = 0.05

        self.x_pos_left_border = x_start_pos
        self.y_pos_top_box = y_start_pos

        self.quad = Quad(thickness=2.0)
        self.quad.reparentTo(self)

        # self.quad.set_pos_vec3(Vec3(self.x_pos_left_border, 0., self.y_pos_top_box))
        # self.quad.set_pos_vec3(Vec3(0., 0., 0.))

        self.setMat_normal(self.get_quad_base_transform_mat())

        self.set_figsize(self.height, self.width)

        self.xmin = 0.
        self.xmax = 1.
        self.ymin = 0.
        self.ymax = 1.

        self.plp1 = None

        self.update_parametric_line(
            # lambda t: np.array([
            #         np.cos(t*(2.*np.pi)*1.),
            #         np.sin(t*(2.*np.pi)*1.),
            #     ])
            lambda x: np.array([
                    x,
                    np.sin(x),
                ])
        )

        self.x_ticks = Ticks()
        self.x_ticks.reparentTo(self)

        self.ticks_max_density = 10. # per p3d length unit
        self.ticks_min_density = 3. # per p3d length unit


        self.update_ticks()
        # self.adjust_ticks_transform()

        # self.plp1.remove()
        # point = Point3d(pos=(Vec3(1., 0., 1.)), TQGraphicsNodePath_creation_parent_node=engine.tq_graphics_basics.tq_aspect2d)

    def get_quad_base_transform_mat(self):
        """ transform to set it's position in the center and scale it's dimensions to [1,1]"""
        return math_utils.getTranslationMatrix4x4(0., 0., self.height).dot(math_utils.getTranslationMatrix4x4(self.pos_x, 0., self.pos_y))

    def update_ticks(self):
        """ make sure the density of ticks is between ticks_max_density and ticks_min_density, then adjust the ticks """
        arr = np.linspace(self.xmin, self.xmax, num=10, endpoint=True)
        self.x_ticks.set_ticks_by_arr(arr)
        self.adjust_ticks_transform()

    def adjust_ticks_transform(self):
        """ """
        self.x_ticks.setMat_normal(math_utils.getScalingMatrix4x4(self.width/(self.xmax - self.xmin), 1., 1.))

    def set_figsize(self, height, width):
        """ set the size of the figure, in p3d units """
        self.quad.set_height(self.height)
        self.quad.set_width(self.width)

    # def set_xlim(self, xmin, xmax):
    #     """ """
    #     self.quad.


    def update_parametric_line(self, func_xy_of_t=None):
        """ """
        if func_xy_of_t is not None:
            self.plp1 = ParametricLinePrimitive(
                lambda t: np.array([func_xy_of_t(t)[0], 0., func_xy_of_t(t)[1]]),
                howmany_points=100, param_interv=np.array([0, 2.0 * np.pi]))
            self.plp1.reparentTo(self)

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
