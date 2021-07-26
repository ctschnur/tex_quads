from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle

from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3
from sequence.sequence import Sequence

import numpy as np

from engine.tq_graphics_basics import TQGraphicsNodePath

class Quad(TQGraphicsNodePath):
    """ Just a quad in which things are displayed. Originally invented for display with
    aspect2d, but display with render is also possible. """

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

        self.top = Line1dSolid(**kwargs)
        self.top.reparentTo(self)

        self.bottom = Line1dSolid(**kwargs)
        self.bottom.reparentTo(self)

        self.left = Line1dSolid(**kwargs)
        self.left.reparentTo(self)

        self.right = Line1dSolid(**kwargs)
        self.right.reparentTo(self)

        self.set_width(width)
        self.set_height(height)

    # def setColor(self, *args, **kwargs):
    #     """ """
    #     return super().setColor(*args, **kwargs)

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

    def update(self):
        """ if are_all_graphics_data_specified returns True,
        calculate the corners and set the line points """

        if self.are_all_graphics_data_specified() == False:
            print("Warning: update() didn't work since not all graphics data was given")
            return None

        # calculate line positions, assuming x is to the right, y is up, z is 0

        self.upper_left_corner = self.pos_vec3
        self.upper_right_corner = self.pos_vec3 + Vec3(1., 0., 0.) * self.width
        self.lower_left_corner = (self.pos_vec3 -
                                  Vec3(0., 0., 1.) * self.height)
        self.lower_right_corner = (self.pos_vec3
                                   + Vec3(1., 0., 0.) * self.width
                                   - Vec3(0., 0., 1.) * self.height)

        self.top.setTailPoint(self.upper_left_corner)
        self.top.setTipPoint(self.upper_right_corner)

        self.bottom.setTailPoint(self.lower_left_corner)
        self.bottom.setTipPoint(self.lower_right_corner)

        self.left.setTailPoint(self.upper_left_corner)
        self.left.setTipPoint(self.lower_left_corner)

        self.right.setTailPoint(self.upper_right_corner)
        self.right.setTipPoint(self.lower_right_corner)

    def remove(self):
        self.top.remove()
        self.left.remove()
        self.right.remove()
        self.bottom.remove()
