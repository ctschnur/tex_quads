from simple_objects.primitives import ParametricLinePrimitive

import numpy as np
import scipy.special

class BlochSphere:
    # plot a bloch sphere into the origin, with two rings to orient oneself on

    def __init__(self, P_arr  # =np.array([[0., 0., 0.],
                 #            [0., 1., 1.],
                 #            [0., 0, 1.],
                 #            [1., 1., 1.]])
                 ):
        plp1 = ParametricLinePrimitive(
            lambda t: np.array([
                0,
                np.cos(t*(2.*np.pi)*1.),
                np.sin(t*(2.*np.pi)*1.)
            ]), howmany_points=1000)

        from simple_objects.primitives import ParametricDashedLinePrimitive

        plp2 = ParametricDashedLinePrimitive(lambda t: np.array([
            np.sin(t*(2.*np.pi)*1.),
            np.cos(t*(2.*np.pi)*1.),
            0
        ]), howmany_points=1000)
