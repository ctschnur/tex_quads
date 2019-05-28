import conventions

import custom_geometry
import texture_utils

from latex_expression_manager import LatexImageManager, LatexImage

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


class Animator:
    # interval/sequence initiate functions
    def initiateTranslationMovement(self, v_x=0., v_z=0., duration=0., delay=0.):
        extraArgs = [duration, v_x, v_z]
        self.p3d_interval = LerpFunc(
            self.updatePosition, duration=duration, extraArgs=extraArgs)
        Sequence(Wait(delay), self.p3d_interval).start()

    def initiateRotationMovement(self, h=0., p=0., r=0., duration=0., delay=0.):
        extraArgs = [duration, h, p, r]
        self.p3d_interval = LerpFunc(
            self.updateRotation, duration=duration, extraArgs=extraArgs)
        Sequence(Wait(delay), self.p3d_interval).start()

    # interval update functions
    def updatePosition(self, t, duration, v_x, v_z):
        self.nodePath.setPos(v_x * (t / duration), 1., v_z * (t / duration))

    def updateRotation(self, t, duration, h, p, r):
        self.nodePath.setHpr(h * (t / duration), p *
                             (t / duration), r * (t / duration))
