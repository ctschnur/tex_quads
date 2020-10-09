from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle, Fixed2dLabel

from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3
from sequence.sequence import Sequence

from plot_utils.quad import Quad

import numpy as np


class WaitingSymbol:
    """ An animation that runs as long as done_function returns False. """

    def __init__(self, done_function, position, size=0.2, frequency=1):
        """
        Args:
            done_function: function which controls when the waiting symbol
                           animation should be stopped (when True)
            position: Vec3 of the upper left hand corner in p3d coordinates """

        # -- logical
        self.done_function = done_function

        self.position = position
        self.size = size
        self.frequency = frequency
        self.duration = 1.

        self.a = None

        # -- supporting graphics
        self.quad = Quad(thickness=3.0, nodePath_creation_parent_node=aspect2d)
        self.quad.set_pos_vec3(self.position)
        self.quad.set_height(self.size)
        self.quad.set_width(self.size)

        self.line = Line1dSolid(
            thickness=3.0, nodePath_creation_parent_node=aspect2d)

        self.anim_seq = Sequence()

        self.anim_seq.set_sequence_params(
            duration=self.duration,
            extraArgs=[],
            update_while_moving_function=self.update,
            on_finish_function=self.restart_animation)

        self.anim_seq.start()

    def restart_animation(self):
        self.anim_seq.set_t(0.)
        self.anim_seq.resume()

    def _get_center(self):
        return Vec3(self.position[0] + 0.5 * self.size, 0., self.position[2] - 0.5 * self.size)

    def set_position(self, vec3_pos):
        self.position = vec3_pos
        self.update(self.a)

    def update(self, a):
        """ a is in between 0 and 1 """

        self.a = a

        if self.done_function() == True:
            self.remove()
            return
        elif self.done_function() != False:
            raise ValueError("self.done_function() should return Boolean")

        t = a * self.duration
        omega = 2 * np.pi * self.frequency
        theta = omega * t

        r = self.size * 0.4
        p1 = self._get_center()
        p2 = p1 + Vec3(r * np.cos(theta),
                       0.,
                       r * np.sin(theta))

        self.line.setTailPoint(p1)
        self.line.setTipPoint(p2)

        self.quad.set_pos_vec3(self.position)

    def remove(self):
        """ release all resources """
        self.anim_seq.remove()
        self.line.remove()
        self.quad.remove()
