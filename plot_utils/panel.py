from engine.tq_graphics_basics import TQGraphicsNodePath

from local_utils import math_utils

import numpy as np

class PanelGraphics(TQGraphicsNodePath):
    def __init__(self, *args, **kwargs):
        TQGraphicsNodePath.__init__(self, *args, **kwargs)

class PanelGeometry:
    """ only the panel geometry and helper functions """
    def __init__(self, r0, n1, n2, l1, l2, *args, **kwargs):
        """
            args:
                r0: position of plane
                n1: normal vector 1
                n2: normal vector 2
                l1: length 1
                l2: length 2
            TODO: alternatively introduce up_vector, normal vector and l1, l2 """

        self.set_panel_geometry(r0, n1, n2, l1, l2)

    def set_panel_geometry(self, r0, n1, n2, l1, l2):
        self.r0 = r0

        assert math_utils.equal_up_to_epsilon(np.linalg.norm(n1), 1., epsilon=0.0001)
        self.n1 = n1

        math_utils.equal_up_to_epsilon(np.linalg.norm(n2), 1., epsilon=0.0001)
        self.n2 = n2

        assert l1 > 0
        self.l1 = l1

        assert l2 > 0
        self.l2 = l2

    def get_plane_normal_vector(self):
        return np.cross(self.n1, self.n2)

    def __repr__(self):
        return "(r0: %s, n1: %s, n2: %s, l1: %f, l2: %f)" % (str(self.r0), str(self.n1), str(self.n2), self.l1, self.l2)
