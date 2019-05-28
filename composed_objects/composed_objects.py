from conventions import conventions
from simple_objects import custom_geometry
from utils import texture_utils
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
        bx = self.line.xhat_prime[0]
        by = self.line.xhat_prime[1]
        bz = self.line.xhat_prime[2]
        translation_to_xhat = np.array(
            [[1, 0, 0, bx],
             [0, 1, 0, by],
             [0, 0, 1, bz],
             [0, 0, 0,  1]])
        self.translation_to_xhat_forrowvecs = (
            Mat4(*tuple(np.transpose(translation_to_xhat).flatten())))

        # then translate arrowhead back to the scaled back line's tip
        arrowhead_length = -np.cos(np.pi / 6.) * self.arrowhead.scale
        arrowhead_direction = self.line.xhat_prime / np.linalg.norm(self.line.xhat_prime)
        b_tilde = arrowhead_length * arrowhead_direction
        b_tilde_x = b_tilde[0]
        b_tilde_y = b_tilde[1]
        b_tilde_z = b_tilde[2]
        translation_to_match_point = np.array([[1, 0, 0, b_tilde_x],
                                               [0, 1, 0, b_tilde_y],
                                               [0, 0, 1, b_tilde_z],
                                               [0, 0, 0,         1]])
        self.translation_to_match_point_forrowvecs = (
            Mat4(*tuple(np.transpose(translation_to_match_point).flatten())))

        # compose the two translations
        self.translation_forrowvecs = (
            self.translation_to_xhat_forrowvecs * self.translation_to_match_point_forrowvecs)

        # scale the arrowhead to the line thickness
        vx = ArrowHead.scale
        vy = ArrowHead.scale
        vz = ArrowHead.scale
        scaling = np.array([[vx,  0,  0, 0],
                            [0,  vy,  0, 0],
                            [0,   0, vz, 0],
                            [0,   0,  0, 1]])
        self.scaling_forrowvecs = Mat4(*tuple(np.transpose(scaling).flatten()))

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

        # apply the scaling
        vx = c_scaling
        vy = c_scaling
        vz = c_scaling
        scaling = np.array([[vx,  0,  0, 0],
                            [0,  vy,  0, 0],
                            [0,   0, vz, 0],
                            [0,   0,  0, 1]])

        self.scaling_forrowvecs = Mat4(*tuple(np.transpose(scaling).flatten()))

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