from simple_objects.primitives import ParametricLinePrimitive

from panda3d.core import Vec3, Mat4, Vec4

import numpy as np
import scipy.special


class BezierCurve:
    # plot a bezier curve in the yz plane

    def __init__(self, P_arr  # =np.array([[0., 0., 0.],
                 #            [0., 1., 1.],
                 #            [0., 0, 1.],
                 #            [1., 1., 1.]])
                 ):
        self.bez_points = P_arr

        self.beziercurve = ParametricLinePrimitive(
            lambda t:
            np.array([
                BezierCurve.calcBezierCurve(t, self.bez_points)[0],
                BezierCurve.calcBezierCurve(t, self.bez_points)[1],
                BezierCurve.calcBezierCurve(t, self.bez_points)[2]
            ]),
            param_interv=np.array([0, 1]),
            thickness=1.,
            color=Vec4(1., 1., 0., 1.))

    @staticmethod
    def calcBezierCurve(t, P_arr):
        _sum = 0
        n = len(P_arr) - 1

        assert len(P_arr) >= 2  # at least a linear bezier curve
        assert t >= 0. and t <= 1.

        for i, P_i in enumerate(P_arr):
            _sum += (scipy.special.comb(n, i)
                     * (1. - t)**(n - np.float(i))
                     * t**np.float(i)
                     * P_i)
        return _sum
