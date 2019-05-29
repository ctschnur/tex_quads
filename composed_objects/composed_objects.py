from conventions import conventions
from simple_objects import custom_geometry
from utils import texture_utils, math_utils
from latex_objects.latex_expression_manager import LatexImageManager, LatexImage
from simple_objects.animator import Animator
from simple_objects.simple_objects import Line, ArrowHead

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
