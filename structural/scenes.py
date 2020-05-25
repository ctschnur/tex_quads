from local_utils import math_utils

import numpy as np

from direct.showbase.ShowBase import ShowBase
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Mat4, Vec4
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval


class Scene2d:
    def __init__(self, x_lowerleft, y_lowerleft, box_height=1.0, box_width=2.0, **kwargs):
        if 'color' in kwargs:
            self.color = kwargs.get('color')
        else:
            self.color = Vec4(.5, .5, .5, 1)

        self.x_lowerleft = x_lowerleft
        self.y_lowerleft = y_lowerleft

        self.box_height = box_height
        self.box_width = box_width

        self.scale = 1.

        # draw the box
        for cur_x, cur_y, cur_z in zip(self.x_lowerleft, self.y_lowerleft, self.z):
            cur_point = Point()
            cur_point.nodePath.setPos(cur_x, 0, cur_y)
            cur_point.nodePath.setColor(*self.color)
            self.set_bbox.append(cur_point)

        self.groupNode = GroupNode()
        self.groupNode.addChildNodePaths(
            [point.nodePath for point in self.set_bbox])
