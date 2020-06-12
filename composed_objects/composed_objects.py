from conventions import conventions
from simple_objects import custom_geometry
from local_utils import texture_utils, math_utils
from latex_objects.latex_expression_manager import LatexImageManager, LatexImage
from simple_objects.animator import Animator
from simple_objects.simple_objects import Line2dObject, ArrowHead, Point, Line1dObject

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Vec3,
    Vec4,
    TransparencyAttrib,
    AntialiasAttrib,
    NodePath,
    Mat4,
    Mat3,
    LineSegs)
from direct.interval.IntervalGlobal import Wait, Sequence
from direct.interval.LerpInterval import LerpFunc

import hashlib
import numpy as np


class ParallelLines:
    """ Draw Parallel Lines

    """

    def __init__(self):
        self.spacing = .25
        self.number_of_lines = 15

        # transform the lines
        # - stretch the unit length lines to the specified size
        # - position them in order, evenly spaced

        self.lines = [Line2dObject() for i in range(self.number_of_lines)]
        for idx, line1 in enumerate(self.lines):
            line1.nodePath.setScale(line1.nodePath, 1., 1., 1.)
            line1.nodePath.setPos(0., 0, idx * self.spacing)


class Vector:
    """Documentation for Vector
       combines an arrowhead and a line1 and applys transformations to them so that it
       it looks like a properly drawn vector
    """

    def __init__(self, tip_point=None, **kwargs):
        if 'linetype' in kwargs:
            self.linetype = kwargs.get('linetype')
        else:
            self.linetype = "1d"

        if self.linetype == "1d":
            if 'thickness1dline' in kwargs:
                self.thickness1dline = kwargs.get('thickness1dline')
            else:
                self.thickness1dline = 2.

            if 'color' in kwargs:
                self.color = kwargs.get('color')
            else:
                self.color = 2.

            self.line1 = Line1dObject(
                thickness=self.thickness1dline, color=self.color)

        elif self.linetype == "2d":
            self.line1 = Line2dObject()
        else:
            print("Error: linetype " + self.linetype + " is invalid")

        if 'color' in kwargs:
            self.color = kwargs.get('color')
        else:
            self.color = Vec4(1., 0., 0., 1.)

        self.arrowhead = ArrowHead()
        self.arrowhead.nodePath.setRenderModeWireframe()

        self.groupNode = GroupNode()
        self.groupNode.addChildNodePaths(
            [self.line1.nodePath, self.arrowhead.nodePath])

        self.setVectorTipPoint(tip_point)

    def setVectorTipPoint(self, tip_point):
        if tip_point is not None:
            self.line1.setTipPoint(tip_point)

        # join ArrowHead and Line
        self._adjustArrowHead()
        self._adjustLine()

    def _adjustArrowHead(self):
        # 0. scale arrowhead (may just be identity)
        # 1. rotation equal to the line1's rotation
        # 2. translation to the tip of the line1
        #   - translate arrowhead to the tip of the line1
        #   - translate arrowhead back to the scaled back line1's tip

        translation_to_tip_forrowvecs = math_utils.getTranslationMatrix3d_forrowvecs(
            self.line1.vec_prime[0],
            self.line1.vec_prime[1],
            self.line1.vec_prime[2])

        arrowhead_length = -np.cos(np.pi / 6.) * self.arrowhead.scale
        arrowhead_direction = self.line1.vec_prime / \
            np.linalg.norm(self.line1.vec_prime)
        b_tilde = arrowhead_length * arrowhead_direction
        translation_to_match_point_forrowvecs = math_utils.getTranslationMatrix3d_forrowvecs(
            b_tilde[0],
            b_tilde[1],
            b_tilde[2])

        translation_forrowvecs = (
            translation_to_tip_forrowvecs * translation_to_match_point_forrowvecs)

        self.arrowhead.nodePath.setMat(
            self.arrowhead.form_from_primitive_trafo * self.line1.getRotation() * translation_forrowvecs)

    def _adjustLine(self):
        # figure out the factor by which to scale back the line1
        # based on the size of the arrow tip
        l_arrow = -np.cos(np.pi / 6.) * self.arrowhead.scale
        arrowhead_direction = self.line1.vec_prime / \
            np.linalg.norm(self.line1.vec_prime)
        l_line_0 = np.linalg.norm(self.line1.vec_prime)
        c_scaling = l_line_0 / (l_line_0 - l_arrow)

        scaling_forrowvecs = math_utils.getScalingMatrix3d_forrowvecs(
            c_scaling,
            c_scaling,
            c_scaling)
        self.line1.nodePath.setMat(
            self.line1.nodePath.getMat() * scaling_forrowvecs)


class GroupNode(Animator):
    """Documentation for GroupNode

    """

    def __init__(self):
        super(GroupNode, self).__init__()
        self.nodePath = NodePath("empty")
        self.nodePath.reparentTo(render)

    def addChildNodePaths(self, NodePaths):
        for np in NodePaths:
            np.reparentTo(self.nodePath)

    def removeChildNodePaths(self, NodePaths):
        for np in NodePaths:
            np.removeNode()


class Axis:
    """ An axis is a vector with ticks
    TODO: add rendering of numbers
    TODO: prevent drawing of ticks in the axis' arrow head
    """

    def __init__(self, direction_vector, axis_length=1., ticksperunitlength=4, thickness1dline=2., color=Vec4(1., 0., 0., 1.)):
        # logical properties
        self.axis_length = axis_length
        self.direction_vector = direction_vector.normalized()
        self.ticksperunitlength = ticksperunitlength

        # building blocks
        self.axis_vector = None
        self.ticks = None

        self.thickness1dline = thickness1dline
        self.color = color

        # p3d node
        # TODO: make a class composed_object and have it automatically have a p3d
        # groupnode
        self.groupNode = GroupNode()

        # build and connect the building blocks according to logical properties
        self._build_vector()
        self._build_ticks()

        # # add everything together to a transform node
        # self.groupNode.addChildNodePaths([self.axis_vector.groupNode.nodePath,
        #                                   self.ticks_groupNode.nodePath])

    def _build_vector(self):
        tip_point = self.direction_vector * self.axis_length

        if self.axis_vector:
            self.axis_vector.setVectorTipPoint(tip_point)
        else:
            self.axis_vector = Vector(
                tip_point=tip_point, thickness1dline=self.thickness1dline, color=self.color)
            self.groupNode.addChildNodePaths(
                [self.axis_vector.groupNode.nodePath])

    def _build_ticks(self):
        # for now, always build new ticks
        if self.ticks:
            # remove all tick p3d nodes
            self.groupNode.removeChildNodePaths(
                [self.ticks_groupNode.nodePath])

        # build new set of ticks
        self.ticks = []
        howmanyticks = self.ticksperunitlength * self.axis_length
        self.ticks_groupNode = GroupNode()

        for i in np.arange(0, self.axis_length, step=1./self.ticksperunitlength):
            trafo_nodePath = NodePath("trafo_nodePath")
            trafo_nodePath.reparentTo(self.ticks_groupNode.nodePath)
            # tick_line = Line2dObject()
            tick_line = Line1dObject(thickness=self.thickness1dline)
            tick_line.nodePath.reparentTo(trafo_nodePath)

            tick_length = 0.2
            # translation = Vec3(i, 0, -0.25 * tick_length)
            tick_line.setTipPoint(Vec3(0, 0, tick_length))
            translation = Vec3(i, 0, -0.25 * tick_length)
            trafo_nodePath.setPos(
                translation[0], translation[1], translation[2])

            if float(i).is_integer() and i != 0:
                tick_line.nodePath.setColor(1, 0, 0, 1)
            if i == 0:
                tick_line.nodePath.setColor(1, 1, 1, 0.2)

            if float(i).is_integer() and i != 0:
                trafo_nodePath.setScale(.5, 1., .5)
            else:
                trafo_nodePath.setScale(.5, 1., .5)

            self.ticks.append(tick_line)

        # apply rotation to ticks group Node
        self.ticks_groupNode.nodePath.setMat(
            self.axis_vector.line1.getRotation())

        self.groupNode.addChildNodePaths([self.ticks_groupNode.nodePath])

    def setAxisLength(self, length):
        # set the logical parameter
        self.axis_length = length

        # rebuild (reuse or delete and allocate new)
        self._build_vector()
        self._build_ticks()


# class Tick:
#     """ an axis has ticks
#     """

#     def __init__(self):
#         # logical properties
#         self.thickness = 0.5 * Line2dObject.width
#         self.length = 4 * Line2dObject.width

#     def _build_line(self):


class CoordinateSystem:
    """ A coordinate system is a set of Axis objects
    """

    cartesian_axes_directions = [
        Vec3(1., 0., 0.),
        Vec3(0., 0., 1.),
        Vec3(0., 1., 0.)]

    cartesian_axes_colors = [Vec4(1., 0., 0., 1.),  # x-axis : red
                             Vec4(0., 1., 0., 1.),  # y-axis : green
                             Vec4(0., 0., 1., 1.)   # z-axis : blue
                             ]

    def __init__(self, axes=None, dimension=2):
        self.scatters = []
        self.dimension = dimension
        self.axes = []

        self.groupNode = GroupNode()

        for direction_vec, color_vec in zip(CoordinateSystem.cartesian_axes_directions[:dimension], CoordinateSystem.cartesian_axes_colors[:dimension]):
            ax = Axis(direction_vec, thickness1dline=2.5, color=color_vec)
            self.axes.append(ax)
            self.groupNode.addChildNodePaths([ax.groupNode.nodePath])

    def attachScatter(self, scatter):
        self.scatters.append(scatter)
        # make sure that axes are long enough to encompass
        # scatter

        # get max and min of scatter in x and y range
        scatters_x_max = max(
            [max([lpoint.x for lpoint in [point.nodePath.getPos() for point in scatter.points]]) for scatter in self.scatters])
        scatters_y_max = max(
            [max([lpoint.z for lpoint in [point.nodePath.getPos() for point in scatter.points]]) for scatter in self.scatters])

        # scatter_x_min = min(
        #     [lpoint.x for lpoint in [point.nodePath.getPos() for point in scatter.points]])
        # scatter_y_min = min(
        #     [lpoint.z for lpoint in [point.nodePath.getPos() for point in scatter.points]])

        # resize the axes of the coordinate system to encompass the scatter

        self.ax1.setAxisLength(scatters_x_max  # - scatter_x_min
                               )
        self.ax2.setAxisLength(scatters_y_max  # - scatter_y_min
                               )

        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT


class Scatter:
    """ a scatter is a set of points at coordinates
    """

    def __init__(self, x, y, **kwargs):
        if 'color' in kwargs:
            self.color = kwargs.get('color')
        else:
            self.color = Vec4(1, 1, 1, 1)

        self.x = x
        self.y = y

        assert(len(x) == len(y))

        if 'z' in kwargs:
            self.z = kwargs.get('z')
        else:
            self.z = np.zeros(np.shape(x))

        assert(len(self.x) == len(self.z))

        self.points = []

        # create the points
        for cur_x, cur_y, cur_z in zip(self.x, self.y, self.z):
            cur_point = Point()
            # FIXME: for 3d plots, this has to change
            cur_point.nodePath.setPos(cur_x, 0, cur_y)
            cur_point.nodePath.setColor(*self.color)

            self.points.append(cur_point)

        self.groupNode = GroupNode()
        self.groupNode.addChildNodePaths(
            [point.nodePath for point in self.points])


class Box2dOfLines:
    """ a box composed of lines
    """

    def __init__(self, x, y, width, height, **kwargs):
        if 'color' in kwargs:
            self.color = kwargs.get('color')
        else:
            self.color = Vec4(.5, .5, .5, .5)

        self.scale = 1.

        self.width = width
        self.height = height
        self.x_ll = x
        self.y_ll = y

        # -- bottom
        self.line1 = Line2dObject()
        self.line1.setTipPoint(Vec3(self.width, 0, 0))
        self.line1.nodePath.setPos(
            self.line1.nodePath.getPos() + Vec3(self.x_ll, 0, self.y_ll))
        self.line1.nodePath.setColor(self.color)

        # -- left
        self.line2 = Line2dObject()
        self.line2.setTipPoint(Vec3(0, 0., self.height))
        self.line2.nodePath.setPos(
            self.line2.nodePath.getPos() + Vec3(self.x_ll, 0, self.y_ll))
        self.line2.nodePath.setColor(self.color)

        # -- top
        self.line3 = Line2dObject()
        self.line3.setTipPoint(Vec3(self.width, 0., 0.))
        self.line3.nodePath.setPos(self.line3.nodePath.getPos(
        ) + Vec3(self.x_ll, 0, self.y_ll) + Vec3(0, 0, self.height))
        self.line3.nodePath.setColor(self.color)

        # -- right
        self.line4 = Line2dObject()
        self.line4.setTipPoint(Vec3(0, 0., self.height))
        self.line4.nodePath.setPos(self.line4.nodePath.getPos(
        ) + Vec3(self.x_ll, 0, self.y_ll) + Vec3(self.width, 0, 0))
        self.line4.nodePath.setColor(self.color)

        self.lines = [self.line1, self.line2, self.line3, self.line4]

        self.groupNode = GroupNode()
        self.groupNode.addChildNodePaths(
            [lines.nodePath for lines in self.lines])


class CoordinateSystemP3dPlain:
    def __init__(self):
        ls = LineSegs()
        ls.setThickness(1)

        # X axis
        ls.setColor(1.0, 0.0, 0.0, 1.0)
        ls.moveTo(0.0, 0.0, 0.0)
        ls.drawTo(1.0, 0.0, 0.0)

        # Y axis
        ls.setColor(0.0, 1.0, 0.0, 1.0)
        ls.moveTo(0.0,0.0,0.0)
        ls.drawTo(0.0, 1.0, 0.0)

        # Z axis
        ls.setColor(0.0, 0.0, 1.0, 1.0)
        ls.moveTo(0.0,0.0,0.0)
        ls.drawTo(0.0, 0.0, 1.0)

        geomnode = ls.create()
        nodepath = NodePath(geomnode)

        self.groupNode = GroupNode()
        self.groupNode.addChildNodePaths([nodepath])
