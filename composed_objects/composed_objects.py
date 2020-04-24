from conventions import conventions
from simple_objects import custom_geometry
from local_utils import texture_utils, math_utils
from latex_objects.latex_expression_manager import LatexImageManager, LatexImage
from simple_objects.animator import Animator
from simple_objects.simple_objects import Line, ArrowHead, Point

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Vec3,
    Vec4,
    TransparencyAttrib,
    AntialiasAttrib,
    NodePath,
    Mat4,
    Mat3)
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

        self.lines = [Line() for i in range(self.number_of_lines)]
        for idx, line in enumerate(self.lines):
            line.nodePath.setScale(line.nodePath, 1., 1., 1.)
            line.nodePath.setPos(0., 0, idx * self.spacing)


class Vector:
    """Documentation for Vector
       combines an arrowhead and a line and applys transformations to them so that it
       it looks like a properly drawn vector
    """
    def __init__(self, tip_point=None):
        self.line = Line()
        self.arrowhead = ArrowHead()
        self.arrowhead.nodePath.setRenderModeWireframe()

        self.groupNode = GroupNode()
        self.groupNode.addChildNodePaths([self.line.nodePath, self.arrowhead.nodePath])

        self.setVectorTipPoint(tip_point)

    def setVectorTipPoint(self, tip_point):
        if tip_point is not None:
            self.line.setTipPoint(tip_point)

        # join ArrowHead and Line
        self._adjustArrowHead()
        self._adjustLine()

    def _adjustArrowHead(self):
        # apply the same rotation as to the line
        # and then a translation to the tip of the vector

        # first do a rotation: already computed (same as line)

        # two translations:
        # first translate arrowhead to the tip of the line

        self.translation_to_xhat_forrowvecs = math_utils.getTranslationMatrix3d_forrowvecs(
            self.line.xhat_prime[0],
            self.line.xhat_prime[1],
            self.line.xhat_prime[2])

        # then translate arrowhead back to the scaled back line's tip
        arrowhead_length = -np.cos(np.pi / 6.) * self.arrowhead.scale
        arrowhead_direction = self.line.xhat_prime / np.linalg.norm(self.line.xhat_prime)
        b_tilde = arrowhead_length * arrowhead_direction
        self.translation_to_match_point_forrowvecs = math_utils.getTranslationMatrix3d_forrowvecs(
            b_tilde[0],
            b_tilde[1],
            b_tilde[2])

        # compose the two translations
        self.translation_forrowvecs = (
            self.translation_to_xhat_forrowvecs * self.translation_to_match_point_forrowvecs)

        # scale the arrowhead to the line thickness
        self.scaling_forrowvecs = math_utils.getScalingMatrix3d_forrowvecs(
            ArrowHead.scale,
            ArrowHead.scale,
            ArrowHead.scale)

        # apply the scaling
        # apply the same rotation as for the line
        # and then the translation
        self.arrowhead.nodePath.setMat(
            self.scaling_forrowvecs * self.line.rotation_forrowvecs * self.translation_forrowvecs)


    def _adjustLine(self):
        # figure out the factor by which to scale back the line
        # based on the size of the arrow tip
        l_arrow = -np.cos(np.pi / 6.) * self.arrowhead.scale
        arrowhead_direction = self.line.xhat_prime / np.linalg.norm(self.line.xhat_prime)
        l_line_0 = np.linalg.norm(self.line.xhat_prime)
        c_scaling =  l_line_0 / (l_line_0 - l_arrow)

        self.scaling_forrowvecs = math_utils.getScalingMatrix3d_forrowvecs(
            c_scaling,
            c_scaling,
            c_scaling)
        self.line.nodePath.setMat(self.line.nodePath.getMat() * self.scaling_forrowvecs)


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


class Axis:
    """ An axis is a vector with ticks
    TODO: add rendering of numbers
    TODO: prevent drawing of ticks in the axis' arrow head
    """
    def __init__(self, tip_point, ticksperunitlength=4, highlightticksatunitlengths=True):
        self.axis_vector = Vector(tip_point=tip_point)
        self.ticks = []

        self.axis_length = math_utils.getNormFromP3dVector(tip_point)
        self.howmanyticks = ticksperunitlength * self.axis_length

        self.ticks_groupNode = GroupNode()

        for i in np.arange(0, self.axis_length, step=1./ticksperunitlength):
            trafo_nodePath = NodePath("trafo_nodePath")
            trafo_nodePath.reparentTo(self.ticks_groupNode.nodePath)
            tick_line = Line()
            tick_line.nodePath.reparentTo(trafo_nodePath)

            tick_length = 0.2
            # translation = Vec3(i, 0, -0.25 * tick_length)
            tick_line.setTipPoint(Vec3(0, 0, tick_length))
            translation = Vec3(i, 0, -0.25 * tick_length)
            trafo_nodePath.setPos(translation[0], translation[1], translation[2])

            if float(i).is_integer() and i != 0:
                tick_line.nodePath.setColor(1, 0, 0, 1)
            if i == 0:
                tick_line.nodePath.setColor(1, 1, 1, 0.2)

            if float(i).is_integer() and i != 0:
                trafo_nodePath.setScale(.5, 1., .5)
            else:
                trafo_nodePath.setScale(.5, 1., .5)

            self.ticks.append(tick_line)

        self._adjust_ticks()
        # xticks_transformations = [xt.nodePath.get_parent() for xt in xticks]

        # add everything together to a transform node
        self.groupNode = GroupNode()
        self.groupNode.addChildNodePaths([self.axis_vector.groupNode.nodePath,
                                          self.ticks_groupNode.nodePath])

    def _adjust_ticks(self):
        # apply rotation to ticks group Node
        self.ticks_groupNode.nodePath.setMat(self.axis_vector.line.rotation_forrowvecs)


class CoordinateSystem:
    """ A coordinate system is a set of Axis objects
    """

    def __init__(self, axes=None):
        self.ax1 = Axis(Vec3(1., 0, 0))
        self.ax2 = Axis(Vec3(0, 0, 1.))

        self.groupNode = GroupNode()
        self.groupNode.addChildNodePaths([self.ax1.groupNode.nodePath,
                                          self.ax2.groupNode.nodePath])


class Scatter:
    """ a scatter is a set of points at coordinates
    """

    def __init__(self, x, y, **kwargs):
        if 'color' in kwargs:
            self.color = kwargs.get('color')

        self.x = x
        self.y = y

        assert(len(x) == len(y))

        if 'z' in kwargs:
            self.z = kwargs.get('z')
            assert(len(self.x) == len(self.z))

        self.points = []
        # create the points
        for cur_x, cur_y, cur_z in zip(x, y, z):
            cur_point = Point()
            # FIXME: for 3d plots, this has to change
            cur_point.nodePath.setPos(x, 0, y)
            cur_point.nodePath.setColor(0., 1., 0., 1.)

            self.points.append(Point())

        self.groupNode = GroupNode()
        self.groupNode.addChildNodePaths([self.ax1.groupNode.nodePath,
                                          self.ax2.groupNode.nodePath])
