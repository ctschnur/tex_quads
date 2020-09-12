from conventions import conventions
from simple_objects import custom_geometry
from local_utils import texture_utils
from latex_objects.latex_expression_manager import LatexImageManager, LatexImage

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
    def initiateTranslationMovement(self, v_0, v_f, duration=0., delay=0., **kwargs):
        extraArgs = [duration,
                     v_0,
                     v_f]
        self.p3d_interval = LerpFunc(
            self.updatePosition, duration=duration, extraArgs=extraArgs)

        seq = Sequence(Wait(delay), self.p3d_interval)
        seq.start(**kwargs)
        return seq

    def initiateRotationMovement(self, h=0., p=0., r=0., duration=0., delay=0.):
        extraArgs = [duration, h, p, r]
        self.p3d_interval = LerpFunc(
            self.updateRotation, duration=duration, extraArgs=extraArgs)
        Sequence(Wait(delay), self.p3d_interval).start()

    # interval update functions
    def updatePosition(self, t, duration,
                       v_0,
                       v_f):
        # self.nodePath.setPos(v0_x + (v_x - v0_x) * (t / duration),
        #                      v0_y + (v_y - v0_y) * (t / duration),
        #                      v0_z * (v_z - v0_z) * (t / duration))

        self.nodePath.setPos(v_0 + (v_f - v_0) * (t / duration))

    def updateRotation(self, t, duration, h, p, r):
        self.nodePath.setHpr(h * (t / duration), p *
                             (t / duration), r * (t / duration))
