from panda3d.core import TextNode, TextFont, AntialiasAttrib, Texture
from panda3d.core import SamplerState
from conventions.conventions import compute2dPosition
from conventions import conventions
from simple_objects import custom_geometry

from local_utils import math_utils, texture_utils
from simple_objects.primitives import IndicatorPrimitive, Box2dCentered, ConePrimitive

from engine.tq_graphics_basics import TQGraphicsNodePath
import engine.tq_graphics_basics

from latex_objects.latex_expression_manager import LatexImageManager, LatexImage

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Vec3,
    Vec4,
    TransparencyAttrib,
    AntialiasAttrib,
    NodePath,
    Mat4,
    Mat3,
    Point3,
    Point2)
from direct.interval.IntervalGlobal import Wait, Sequence
from direct.interval.LerpInterval import LerpFunc

import hashlib
import numpy as np
import sys
import os

import threading
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from simple_objects.custom_geometry import createCircle

class Pinned2dLabel(IndicatorPrimitive):
    """ """

    def __init__(self, refpoint3d=Point3(1., 1., 1.), text="pinned?", xshift=0., yshift=0.,
                 font="cmr12.egg", color=(1., 1., 1., 1.)):
        """ """
        IndicatorPrimitive.__init__(self)

        self.refpoint3d = refpoint3d
        self.text = text
        self.color = color
        self.nodeisattachedtoaspect2d = False

        self.font = font
        self._font_p3d = loader.loadFont(font)

        self.xshift = xshift
        self.yshift = yshift

        self.update()

    def setPos(self, x, y, z):
        """ essentially sets the 3d position of the pinned label """
        self.refpoint3d = Point3(x + 2, y, z)
        self.update()

    def setText(self, text):
        """ sets the text and updates the pinned label """
        self.text = text
        self.textNode.setText(self.text)
        self.textNodePath.removeNode()
        self.nodeisattachedtoaspect2d = False
        self.update()

    def setColor(self, color):
        """ set the text color

            Args: color is a Vec4(., ., ., .) """

        self.color = color

        self.textNodePath.removeNode()
        self.nodeisattachedtoaspect2d = False
        self.update()

    def update(self):
        """ """
        pos_rel_to_cam = base.cam.get_relative_point(engine.tq_graphics_basics.tq_render.get_p3d_nodepath(),
                                                     self.refpoint3d)
        p2d = Point2()

        if not self.nodeisattachedtoaspect2d:
            self.textNode = TextNode('myPinned2dLabel')
            self.textNode.setText(self.text)
            self.textNode.setTextColor(self.color)

            # load a font
            # cmr12 = loader.loadFont('cmr12.egg')

            self.textNode.setFont(self._font_p3d)

            # set a shadow
            self.textNode.setShadow(0.05, 0.05)
            self.textNode.setShadowColor(0, 0, 0, 1)
            self.textNode_p3d_generated = self.textNode.generate()

            self.textNodePath = aspect2d.attachNewNode(
                self.textNode_p3d_generated)

            self.nodeisattachedtoaspect2d = True
            self.textNodePath.setScale(0.07)

        if not base.cam.node().getLens().project(pos_rel_to_cam, p2d):
            # outside lense camera
            # just don't render it then.
            self.textNodePath.hide()
        else:
            self.textNodePath.show()
            # print("Error: project did not work")
            # exit(1)

        # place text in x, z in [-1, 1] boundaries and
        # the y coordinate gets ignored for the TextNode
        # parented by aspect2d
        self.textNodePath.setPos(
            (p2d[0] + self.xshift) * engine.tq_graphics_basics.get_window_aspect_ratio(), 0, p2d[1] + self.yshift)

    def remove(self):
        """ removes all p3d nodes """
        self.textNodePath.removeNode()


class Fixed2dLabel(IndicatorPrimitive):
    """ a text label attached to aspect2d,  """

    def __init__(self,
                 text="fixed?",
                 font="cmr12.egg"):
        """
        Args:
            x: x position in GUI-xy-plane
            y: y position in GUI-xy-plane
            z: 'z' (actually y) position when attaching to aspect2d """

        IndicatorPrimitive.__init__(self)

        self.text = text
        self.font = font
        self._font_p3d = loader.loadFont(font)
        self.textNode = None    # this thing gets updated in a weird way

        self.pos_x = 0.
        self.pos_y = 0.

        self.update()

    def setPos2d(self, pos_x=None, pos_y=None):
        """ """
        if pos_x is not None:
            self.pos_x = pos_x

        if pos_y is not None:
            self.pos_y = pos_y

        self.update()

    def setPos(self, pos_vec3):
        """ """
        self.pos_x = pos_vec3[0]
        self.pos_y = pos_vec3[2]

        super().setPos(pos_vec3)

        self.update()

    def setText(self, text):
        """ sets the text and updates the pinned label """
        self.text = text
        self.textNode.setText(self.text)
        self.update()

    def update(self):
        """ """
        # TODO: continue with ticks
        self.removeNode()

        if self.textNode is None:
            self.textNode = TextNode('myFixed2dLabel')

        self.textNode.setText(self.text)
        self.textNode.setFont(self._font_p3d)

        # set a shadow
        self.textNode.setShadow(0.05, 0.05)
        self.textNode.setShadowColor(0, 0, 0, 1)

        self.set_p3d_nodepath(NodePath(self.textNode.generate()))

        self.do_trafo()

    def do_trafo(self):
        """ """
        text_size_base_scale = 0.07
        self.setMat_normal(math_utils.getScalingMatrix4x4(text_size_base_scale, 1., text_size_base_scale).dot(
            math_utils.getTranslationMatrix4x4(self.pos_x, 0., self.pos_y)
        ))


class Text(IndicatorPrimitive):
    def __init__(self, **kwargs):
        IndicatorPrimitive.__init__(self)

        self.pointsize = None
        if "pointsize" in kwargs:
            self.pointsize = kwargs.get("pointsize")
        elif self.pointsize is None:
            self.pointsize = 10

        self.text = None
        if "text" in kwargs:
            self.text = kwargs.get("text")
        elif self.text is None:
            self.text = "Basic text"

        self.font = None
        if "font" in kwargs:
            self.font = kwargs.get("font")
        elif self.font is None:
            self.font = "fonts/arial.ttf"

        self.alignment = None
        if "alignment" in kwargs:
            self.alignment = kwargs.get("alignment")
        elif self.alignment is None:
            self.alignment = "left"

    def _set_text_static_graphics_1(self):
        self.textNode = TextNode('foo')
        self.textNode.setText(self.text)
        self._font_p3d = loader.loadFont(self.font)

        self.pixels_per_unit = engine.tq_graphics_basics.get_font_bmp_pixels_from_height(
            engine.tq_graphics_basics.get_pts_to_p3d_units(self.pointsize))

        self._font_p3d.setPixelsPerUnit(self.pixels_per_unit)
        self._font_p3d.setPointSize(self.pointsize)
        self.textNode.setFont(self._font_p3d)

        self.textNode.setShadow(0.05, 0.05)
        self.textNode.setShadowColor(0, 0, 0, 1)

    def _set_text_static_graphics_2(self):
        self.set_node_p3d(self.textNode)
        self.set_p3d_nodepath(NodePath(self.textNode.generate()))

        self._font_p3d.clear()

        self.setLightOff(1)
        self.setTwoSided(True)
        self.set_render_above_all(True)

        scale = self._get_scale()
        self.setScale(scale, 1., scale)

    def _get_scale(self):
        # --- get_scale_matrix_initial_to_font_size
        initial_height = self.textNode.getHeight()
        scale_factor_to_height_1 = 1./initial_height
        pixels_per_p3d_length_unit = engine.tq_graphics_basics.get_window_size_y()/2.0
        scale_height_1_to_pixels = 1./pixels_per_p3d_length_unit
        return scale_height_1_to_pixels * self.pixels_per_unit

    def _reparentTo_additional_trafo_nodepath(self):
        self.additional_trafo_nodepath = TQGraphicsNodePath()
        self.additional_trafo_nodepath.reparentTo_p3d(self.getParent_p3d())
        super().reparentTo(self.additional_trafo_nodepath)


    def _update_textnode_alignment(self):
        if self.alignment == "right":
            self.textNode.setAlign(TextNode.ARight)
        elif self.alignment == "left":
            self.textNode.setAlign(TextNode.ALeft)
        elif self.alignment == "center":
            self.textNode.setAlign(TextNode.ACenter)

    def get_size(self):
        height = engine.tq_graphics_basics.get_pts_to_p3d_units(self.pointsize)
        width = (self.textNode.getWidth()/self.textNode.getHeight()) * height
        return height, width



class BasicText(Text):
    """ a text label attached to aspect2d,  """

    def __init__(self, **kwargs):
        Text.__init__(self, **kwargs)

        self._set_text_static_graphics_1()
        self._update_textnode_alignment()
        self._set_text_static_graphics_2()
        self._reparentTo_additional_trafo_nodepath()


class Basic2dText(BasicText):
    """ Upright text means not rotated, i.e. BasicText retransformed to be upright """
    def __init__(self, # camera_gear,
                 rotate_angle_2d=0,
                 **kwargs):
        BasicText.__init__(self, **kwargs)

        self.rotate_angle_2d = rotate_angle_2d

        # self.camera_gear = camera_gear

        # heading, pitch, roll = self.camera_gear.p3d_camera.getHpr()

        # print("render, heading, pitch, roll: ", render, heading, pitch, roll)

        # self.setHpr(render, heading, pitch + 90, roll)


    def attach_to_aspect2d(self):
        super().attach_to_aspect2d()
        # rotate it here, after attaching it

        # h, p, r = self.getHpr()
        # self.setHpr(h, p, r-90)

        # h, p, r = self.additional_trafo_nodepath.getHpr()
        # self.additional_trafo_nodepath.setHpr(h, p, r-90)

        # h, p, r = aspect2d.getHpr()
        # self.setHpr(h, p, r+self.rotate_angle_2d)
        pass


class BasicOrientedText(Text):
    """ a text label attached to aspect2d,  """

    def __init__(self,
                 camera_gear,
                 update_orientation_on_camera_rotate=True,
                 **kwargs):

        self.camera_gear = camera_gear # needed for re-orientation towards the camera whenever it's updated or the camera moves
        self._initial_normal_vector = Vec3(0., 1., 0.)

        Text.__init__(self, **kwargs)

        self._set_text_static_graphics_1()
        self._update_textnode_alignment()
        self._set_text_static_graphics_2()
        self._reparentTo_additional_trafo_nodepath()

        if update_orientation_on_camera_rotate == True:
            self.camera_gear.add_camera_move_hook(self.face_camera)
        # self.face_camera()

    def face_camera(self):
        """ """
        x, y, z, up_vector, eye_vector = self.camera_gear.get_spherical_coords(
            get_up_vector=True, get_eye_vector=True, correct_for_camera_setting=True)

        heading, pitch, roll = self.camera_gear.p3d_camera.getHpr()
        # roll += 90.
        # pitch += 90.
        if up_vector == Vec3(0, 0, -1) and eye_vector == Vec3(-1, 0, 0):
            self.setHpr(render, heading, pitch, roll + 180.)
        else:
            self.setHpr(render, heading, pitch, roll)

    def setPos(self, *args, **kwargs):
        """ """
        res = self.additional_trafo_nodepath.setPos(*args, **kwargs)
        return res

    def reparentTo(self, *args, **kwargs):
        """ """
        res = self.additional_trafo_nodepath.reparentTo(*args, **kwargs)
        return res

    def removeNode(self):
        """ """
        self.camera_gear.remove_camera_move_hook(self.adjust_rotation_to_camera)
        super().removeNode()
        return self.additional_trafo_nodepath.removeNode()
