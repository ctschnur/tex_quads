from direct.showbase.ShowBase import ShowBase, DirectObject

from simple_objects.primitives import ParametricLinePrimitive
from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk

from composed_objects.composed_objects import Point3dCursor

from panda3d.core import Vec3, Mat4, Vec4

import numpy as np

from plot_utils.edgemousetools import EdgeHoverer, EdgeMouseClicker

from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval
from local_utils import math_utils

class EdgeGeneral:
    """ superclass for EdgePlayer and EdgeRecorder
        it contains some basic commonalities, like
        - a cursor
        - the logical v1 and v_dir
        - the line """

    def __init__(self):
        self.v1 = Vec3(-.5, -.5, 0.)
        self.v_dir = Vec3(1., 1., 0.)/np.linalg.norm(Vec3(1., 1., 0.))

        self.v_c = self.v1  # cursor; initially at stopped_at_beginning state

        self.p_c = Point3dCursor(Vec3(0., 0., 0.))

        self.line = Line1dSolid()
        self.line.setTipPoint(self.v1)
        self.line.setTailPoint(self.get_v2())
