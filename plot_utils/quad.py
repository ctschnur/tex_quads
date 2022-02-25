from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle

from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3
from sequence.sequence import Sequence

from simple_objects.primitives import IndicatorPrimitive, Box2dCentered, ConePrimitive, Box2d

import numpy as np

from engine.tq_graphics_basics import TQGraphicsNodePath

class Quad(TQGraphicsNodePath):
    """ Just a quad in which things are displayed. Originally invented for display with
    aspect2d, but display with render is also possible. """

    bg_color = Vec4(1., 1., 1., 0.3)
    border_color = Vec4(0., 0., 0., 1.)

    def __init__(self, pos_vec3=Vec3(0., 0., 0.), width=1.0, height=1.0, **kwargs):
        """
        Args:
            pos_vec3: upper left corner in p3d coordinates in aspect2d
                      (+x is right, +z is up, y has to be 0.)
            **kwargs:
                TQGraphicsNodePath_creation_parent_node: aspect2d or render
                thickness: thickness of the lines in the quad
        """

        self.pos_vec3 = None
        self.width = None
        self.height = None

        TQGraphicsNodePath.__init__(self)

        self.set_pos_vec3(pos_vec3)


        self.border_line_top = Line1dSolid(**kwargs)
        self.border_line_top.reparentTo(self)

        self.border_line_bottom = Line1dSolid(**kwargs)
        self.border_line_bottom.reparentTo(self)

        self.border_line_left = Line1dSolid(**kwargs)
        self.border_line_left.reparentTo(self)

        self.border_line_right = Line1dSolid(**kwargs)
        self.border_line_right.reparentTo(self)


        self.b2d = Box2d()  # background box
        self.b2d.reparentTo(self)
        self.b2d.setColor(Quad.bg_color, 1)

        self.set_border_color(Quad.border_color, 1)

        self.set_width(width)
        self.set_height(height)

    def setColor(self, *args, **kwargs):
        """ """
        self.set_border_color(*args, **kwargs)
        self.b2d.setColor(*args, **kwargs)

        # return TQGraphicsNodePath.setColor(self, *args, **kwargs)

    def set_border_color(self, *args, **kwargs):
        self.border_line_top.setColor(*args, **kwargs)
        self.border_line_bottom.setColor(*args, **kwargs)
        self.border_line_left.setColor(*args, **kwargs)
        self.border_line_right.setColor(*args, **kwargs)

    def set_pos_vec3(self, pos_vec3):
        """ set position of upper left corner of the quad (in aspect2d) """
        self.pos_vec3 = pos_vec3

        if self.are_all_graphics_data_specified():
            self.update()

    def get_pos_vec3(self):
        return self.pos_vec3

    def set_width(self, width):
        """
        Args:
        - pos_vec3: upper left corner in p3d coordinates in aspect2d (+x is right, +z is up, y has to be 0.)
        """
        self.width = width

        if self.are_all_graphics_data_specified():
            self.update()

    def get_width(self):
        return width

    def set_height(self, height):
        """ height, not in pixels, but aspect2d p3d coords """
        self.height = height

        if self.are_all_graphics_data_specified():
            self.update()

    def get_height(self):
        return height

    def are_all_graphics_data_specified(self):
        return self.pos_vec3 and self.width and self.height

    def _set_corners_logical_from_width_height(self):
        self._p0 = Vec3(0., 0., 0.)
        self._p1 = Vec3(1., 0., 0.) * self.width
        self._p2 = (self.pos_vec3
                                   + Vec3(1., 0., 0.) * self.width
                                   - Vec3(0., 0., 1.) * self.height)
        self._p3 = (self.pos_vec3 -
                                  Vec3(0., 0., 1.) * self.height)

    def set_corners_graphical(self):
        self.border_line_top.setTailPoint(self._p0)
        self.border_line_top.setTipPoint(self._p1)

        self.border_line_bottom.setTailPoint(self._p3)
        self.border_line_bottom.setTipPoint(self._p2)

        self.border_line_left.setTailPoint(self._p0)
        self.border_line_left.setTipPoint(self._p3)

        self.border_line_right.setTailPoint(self._p1)
        self.border_line_right.setTipPoint(self._p2)

    def update(self):
        """ if are_all_graphics_data_specified returns True,
        calculate the corners and set the line points """

        if self.are_all_graphics_data_specified() == False:
            print("Warning: update() didn't work since not all graphics data was given")
            return None

        # calculate line positions, assuming x is to the right, y is up, z is 0

        self._set_corners_logical_from_width_height()
        self.set_corners_graphical()
        self._update_b2d()

    def _update_b2d(self):
        # update
        self.b2d.setScale(self.width, 1., self.height)
        p0 = self.getPos()
        self.b2d.setPos(Vec3(p0[0], p0[1], p0[2] - self.height))
        pass

    def remove(self):
        self.border_line_top.remove()
        self.border_line_left.remove()
        self.border_line_right.remove()
        self.border_line_bottom.remove()
