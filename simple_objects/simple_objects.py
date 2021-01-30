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


class Point(IndicatorPrimitive):
    def __init__(self, **kwargs):
        if 'color' in kwargs:
            self.color = kwargs.get('color')
        else:
            self.color = Vec4(1., 1., 1., 1.)

        IndicatorPrimitive.__init__(self, **kwargs)


class Point3d(Point):
    point3d_normal_scale = 0.025

    def __init__(self, scale=1., **kwargs):
        """
        Args:
            scale: the scale in multiples of  """
        self.scale = scale
        self.scale_ist = Point3d.point3d_normal_scale * self.scale

        if 'pos' in kwargs:
            self.pos = kwargs.get('pos')
        else:
            self.pos = None

        Point.__init__(self, **kwargs)

        self.makeObject()
        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):

        scaling_forrowvecs = math_utils.math_convention_to_p3d_mat4(
            math_utils.getScalingMatrix4x4(self.scale_ist, self.scale_ist, self.scale_ist))

        self.form_from_primitive_trafo = scaling_forrowvecs  # * rotation_forrowvecs
        self.setMat(self.form_from_primitive_trafo)
        self.setColor(self.color)

        self.setPos(self.pos)

    def makeObject(self):
        # load a gltf file
        from panda3d.core import Filename
        self.set_p3d_nodepath(engine.tq_graphics_basics.tq_loader.loadModel(
            Filename.fromOsSpecific(
                # root of project
                os.path.abspath(sys.path[0])).getFullpath()
            + "/models/small_sphere_triangulated_with_face_normals.gltf"))

        self.reparentTo(engine.tq_graphics_basics.tq_render)
        self.set_node_p3d(self.get_node_p3d())

        self.setRenderModeFilled()

        # override the vertex colors of the model
        self.setColor(self.color)

        self.setLightOff(1)

    def setPos(self, pos):
        """
        Args:
            pos: a p3d 3-component vector """
        self.pos = pos

        if self.pos is not None:
            super().setPos(pos)
            self.show()
        else:
            self.hide()


class PointPrimitive(Point):
    """ a pixel point (no real spatial extent for e.g. picking) """

    def __init__(self, **kwargs):
        Point.__init__(self, **kwargs)

        self.makeObject()

    def makeObject(self):
        self.set_node_p3d(custom_geometry.create_GeomNode_Single_Point(
            color_vec4=Vec4(1., 1., 1., 1.)))
        self.set_p3d_nodepath(
            self.getParent_p3d().attachNewNode(self.get_node_p3d()))

        self.setLightOff(1)
        # self.setRenderModeThickness(5)


class Point2d(Point):
    """ a (2d) quad """

    def __init__(self, **kwargs):
        Point.__init__(self, **kwargs)

    def makeObject(self):
        self.set_node_p3d(custom_geometry.createColoredUnitQuadGeomNode(
            color_vec4=Vec4(1., 1., 1., 1.), center_it=True))

        self.set_p3d_nodepath(
            self.getParent_p3d().attachNewNode(self.get_node_p3d()))

        self.setTwoSided(True)
        self.setLightOff(1)


# ---- lines

class LinePrimitive(IndicatorPrimitive):
    def __init__(self, thickness=1., color=Vec4(1., 1., 1., 1.), **kwargs):
        IndicatorPrimitive.__init__(self, **kwargs)

        # these are graphical values
        # for more complex, e.g. recessed lines for vectors, you need another set
        # of variables to store the logical end points
        self.tip_point = None
        self.tail_point = None

        self.color = color
        # self.makeObject(thickness, color)

    # def makeObject(self, thickness, color):
    #     self.set_node_p3d(custom_geometry.createColoredUnitLineGeomNode(
    #         thickness=thickness, color_vec4=self.color))
    #     self.set_p3d_nodepath(engine.tq_graphics_basics.tq_render.attachNewNode_p3d(self.get_node_p3d())
    #     self.setLightOff(1))


class Line1dPrimitive(LinePrimitive):
    def __init__(self, thickness=1., **kwargs):
        LinePrimitive.__init__(self, **kwargs)

        self.thickness = thickness
        self.makeObject(thickness, self.color)

        self.setTailPoint(self.tail_point)
        self.setTipPoint(self.tip_point)

    def makeObject(self, thickness, color):
        self.set_node_p3d(custom_geometry.createColoredUnitLineGeomNode(
            thickness=thickness,
            color_vec4=self.color))

        self.set_p3d_nodepath(
            self.getParent_p3d().attachNewNode(self.get_node_p3d()))

        self.setLightOff(1)

    def setTipPoint(self, point):
        # the diff_vec needs to be first scaled and rotated, then translated by it's position
        # to get a line at a position of a certain tip and tail point

        self.tip_point = point

        if (self.tip_point is None or self.tail_point is None or self.tip_point == self.tail_point):
            # set vector status to hidden
            self.hide()
            print("Warning: setTipPoint exception: transformation skipped")
            return
        else:
            self.show()

        diff_vec = self.tip_point - self.tail_point

        rotation_forrowvecs = (
            math_utils.math_convention_to_p3d_mat4(
                math_utils.getMat4by4_to_rotate_xhat_to_vector(diff_vec)))

        self._rotation_forrowvecs = rotation_forrowvecs

        # scaling matrix: scale the vector along xhat when it points in xhat direction
        # (to prevent skewing if the vector's line is a mesh)

        scaling_forrowvecs = math_utils.math_convention_to_p3d_mat4(
            math_utils.getScalingMatrix4x4(np.linalg.norm(diff_vec), 1., 1.))

        # apply the net transformation
        # first the scaling, then the rotation_forrowvecs
        # remember, the row vector stands on the left in p3d multiplication
        # so the order is reversed

        scaling_and_rotation_forrowvecs = scaling_forrowvecs * self._rotation_forrowvecs

        translation_forrowvecs = math_utils.getTranslationMatrix4x4_forrowvecs(
            *self.getPos())

        self.setMat(self.form_from_primitive_trafo *
                    scaling_and_rotation_forrowvecs * translation_forrowvecs)

        # for some weird reason, I have to run setTailPoint again ...
        self.setTailPoint(self.tail_point, run_setTipPoint_again=False)

    def setTailPoint(self, point, run_setTipPoint_again=True):
        """ this sets the tailpoint (self.getPos()), keeping the tip point at it's original
            position """

        self.tail_point = point

        if (self.tip_point is None or self.tail_point is None):
            self.hide()
            return
        else:
            self.show()

        self.setPos(point)

        # setTipPoint applies a transformation on an already existing line object, i.e.
        #   first figure out the difference betweeen the tip point (self.tip_point) and the tail point (self.getPos()) to get the length of the vector
        #   then take the difference vector (diff_vec)
        #   knowing the difference vector, compute the rotation matrix for the position vector diff_vec
        #   if you want to set the rotation using a matrix, then you have to set the position as well using a matrix
        #   to do that, implement the affine transformation in math_utils
        # must take into account the tailpoint

        if run_setTipPoint_again is True:
            # print("tip_point rerun after setTailPoint: ", self.tip_point)
            self.setTipPoint(self.tip_point)

    def getRotation_forrowvecs(self):
        """ forrowvecs """

        assert self._rotation_forrowvecs
        return self._rotation_forrowvecs

    def getTipPoint(self):
        return self.tip_point

    def getTailPoint(self):
        return self.tail_point

    def remove(self):
        """ remove the NodePath """
        self.removeNode()


class Line1dSolid(Line1dPrimitive):
    """ """

    def __init__(self, thickness=2., color=Vec4(1., 1., 1., 1.), **kwargs):
        self._rotation_forrowvecs = Mat4()

        # this also sets the position
        Line1dPrimitive.__init__(
            self, thickness=thickness, color=color, **kwargs)

        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        self.form_from_primitive_trafo = self.getMat()


class LineDashedPrimitive(TQGraphicsNodePath):
    def __init__(self, thickness=1., color=Vec4(1., 1., 1., 1.), howmany_periods=5., **kwargs):
        TQGraphicsNodePath.__init__(self, **kwargs)
        self.thickness = thickness
        self.color = color
        self.howmany_periods = howmany_periods
        self.makeObject(thickness, color, howmany_periods)

    def makeObject(self, thickness, color, howmany_periods):
        self.set_node_p3d(custom_geometry.createColoredUnitDashedLineGeomNode(
            thickness=thickness, color_vec4=self.color, howmany_periods=5.))
        self.set_p3d_nodepath(
            self.getParent_p3d().attachNewNode(self.get_node_p3d()))

        self.setLightOff(1)

    def getRotation_forrowvecs(self):
        """
        forrowvecs
        """

        assert self._rotation_forrowvecs
        return self._rotation_forrowvecs


class Line1dDashed(LineDashedPrimitive):
    def __init__(self, thickness=2., color=Vec4(1., 1., 1., 1.), howmany_periods=5., **kwargs):
        super(Line1dDashed, self).__init__(
            thickness=thickness, color=color, howmany_periods=howmany_periods)

        self._rotation_forrowvecs = Mat4()

        self.doInitialSetupTransformation(**kwargs)

    def doInitialSetupTransformation(self, **kwargs):
        self.form_from_primitive_trafo = self.getMat()

        self.setTipPoint(Vec3(1., 0., 0.))


class Line2dObject(Box2dCentered):
    def __init__(self, **kwargs):
        Box2dCentered.__init__(self, **kwargs)
        self.makeObject()
        self.doInitialSetupTransformation(**kwargs)

    def doInitialSetupTransformation(self, **kwargs):
        if 'width' in kwargs:
            self.width = kwargs.get('width')
        else:
            self.width = 0.025

        scaling = math_utils.getScalingMatrix3d_forrowvecs(1., 1., self.width)

        self.length = 1.
        self.translation_to_xhat_forrowvecs = math_utils.getTranslationMatrix4x4_forrowvecs(
            0.5, 0, 0)

        self.form_from_primitive_trafo = scaling * self.translation_to_xhat_forrowvecs
        self.setMat(self.form_from_primitive_trafo)

        # self.form_from_primitive_trafo = self.getMat()
        self.setTipPoint(Vec3(1., 0., 0.))

    def getRotation_forrowvecs(self):
        """
        forrowvecs
        """
        assert self._rotation_forrowvecs
        return self._rotation_forrowvecs


class ArrowHead(Box2dCentered):
    scale = .1

    def __init__(self):
        super(ArrowHead, self).__init__()
        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        # self.setScale(self.scale, self.scale, self.scale)

        scaling_forrowvecs = math_utils.getScalingMatrix3d_forrowvecs(
            self.scale,
            self.scale,
            self.scale)

        self.form_from_primitive_trafo = scaling_forrowvecs

    def makeObject(self):
        """
        it's not just a scaled quad, so it needs different Geometry
        """
        self.set_node_p3d(custom_geometry.createColoredArrowGeomNode(
            color_vec4=Vec4(1., 1., 1., 1.), center_it=True))
        self.set_p3d_nodepath(
            self.getParent_p3d().attachNewNode(self.get_node_p3d()))

        self.setTwoSided(True)


class ArrowHeadCone(Box2dCentered):
    scale = .1

    def __init__(self, **kwargs):
        Box2dCentered.__init__(self, **kwargs)
        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        scaling_forrowvecs = math_utils.getScalingMatrix3d_forrowvecs(
            self.scale,
            self.scale,
            self.scale)

        # also, rotate this one to orient itself in the x direction
        rotation_forrowvecs = math_utils.get_R_y_forrowvecs(np.pi/2.)

        self.form_from_primitive_trafo = scaling_forrowvecs * rotation_forrowvecs

        self.setMat(self.form_from_primitive_trafo)

    def makeObject(self):
        self.set_node_p3d(custom_geometry.create_GeomNode_Cone(
            color_vec4=Vec4(1., 1., 1., 1.)))
        # the self.'node' is a geomnode
        # or more generally a PandaNode
        # typically, if the geometry isn't changed in-place,
        # only the NodePath is called at later times

        self.set_p3d_nodepath(
            self.getParent_p3d().attachNewNode(self.get_node_p3d()))
        self.setTwoSided(True)


class ArrowHeadConeShaded(IndicatorPrimitive):
    """ """

    def __init__(self, color=Vec4(0., 0., 0., 0.), scale=1./5., **kwargs):
        """ """
        self.color = color
        self.scale = scale

        super(ArrowHeadConeShaded, self).__init__(**kwargs)

        self.makeObject()

        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        # self.setScale(self.scale, self.scale, self.scale)

        scaling_forrowvecs = (
            math_utils.math_convention_to_p3d_mat4(math_utils.getScalingMatrix4x4(self.scale,
                                                                                  self.scale,
                                                                                  self.scale)))

        # the underlying model is already rotated in the x direction
        # rotation_forrowvecs = math_utils.get_R_y_forrowvecs(np.pi/2.)

        self.form_from_primitive_trafo = scaling_forrowvecs  # * rotation_forrowvecs

        self.setMat(self.form_from_primitive_trafo)

    def makeObject(self):
        # load a gltf file
        from panda3d.core import Filename
        self.set_p3d_nodepath(engine.tq_graphics_basics.tq_loader.loadModel(
            Filename.fromOsSpecific(
                os.path.abspath(sys.path[0])).getFullpath()  # root of project
            + "/models/unit_cone_triangulated_with_face_normals.gltf"))

        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
        # print("self.getParent_p3d(): ", self.getParent_p3d())
        # self.reparentTo(self.getParent_p3d())

        # override the vertex colors of the model
        self.setColor(self.color)

        self.setRenderModeFilled(True)


class SphereModelShaded(Box2dCentered):
    def __init__(self, color=Vec4(1., 1., 1., 1.), scale=0.1):
        self.color = color
        self.scale = scale
        super(SphereModelShaded, self).__init__()
        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        scaling_forrowvecs = math_utils.getScalingMatrix3d_forrowvecs(
            self.scale,
            self.scale,
            self.scale)

        self.form_from_primitive_trafo = scaling_forrowvecs  # * rotation_forrowvecs

        self.setMat(self.form_from_primitive_trafo)

    def makeObject(self):
        # load a gltf file
        from panda3d.core import Filename
        self.set_p3d_nodepath(engine.tq_graphics_basics.tq_loader.loadModel(
            Filename.fromOsSpecific(
                os.path.abspath(sys.path[0])).getFullpath()  # root of project
            + "/models/small_sphere_triangulated_with_face_normals.gltf"))
        self.reparentTo(engine.tq_graphics_basics.tq_render)
        self.set_node_p3d(self.get_node_p3d())

        # override the vertex colors of the model
        self.setColor(self.color)

        self.setLightOff(1)


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
        self.refpoint3d = Point3(x, y, z)
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


class OrientedDisk(IndicatorPrimitive):
    """ a disk with a normal vector (rotation) and a radius
    TODO: implement normal vector orientaion """

    def __init__(self, thickness=5., **kwargs):
        IndicatorPrimitive.__init__(self, **kwargs)
        self.makeObject()

    def makeObject(self):
        self.set_node_p3d(custom_geometry.createColoredUnitDisk(
            color_vec4=Vec4(1., 1., 1., 1.)))

        self.set_p3d_nodepath(
            self.getParent_p3d().attachNewNode(self.get_node_p3d()))
        self.setLightOff(1)
        self.setTwoSided(True)


class OrientedCircle(IndicatorPrimitive):
    """ a circle with a normal vector (rotation) and a radius
    TODO: implement normal vector orientaion """

    def __init__(self,
                 origin_point=Vec3(1., 1., 1.),
                 normal_vector=Vec3(1., 1., 1.),
                 radius=1.,
                 scale=1.,
                 num_of_verts=10,
                 with_hole=False,
                 thickness=1.,
                 **kwargs):

        self.origin_point = origin_point
        self.normal_vector = normal_vector
        self.scale = scale

        IndicatorPrimitive.__init__(self, **kwargs)
        self.makeObject(num_of_verts, radius,
                        with_hole=with_hole, thickness=thickness)

        self.setMat(
            OrientedCircle.getSetupTransformation(normal_vector, origin_point, scale))

    def makeObject(self, num_of_verts, radius, with_hole, thickness):

        self.set_node_p3d(custom_geometry.createCircle(
            color_vec4=Vec4(1., 1., 1., 1.),
            with_hole=with_hole,
            num_of_verts=num_of_verts,
            radius=radius))

        self.set_p3d_nodepath(
            self.getParent_p3d().attachNewNode(self.get_node_p3d()))
        self.setLightOff(1)
        self.setRenderModeThickness(thickness)

        # self.setTwoSided(True)

        # ---- set orientation from normal vector
        # self.setMat()

    def setPos(self, origin_point):
        self.origin_point = origin_point

        self.setMat(
            OrientedCircle.getSetupTransformation(self.normal_vector,
                                                  self.origin_point,
                                                  self.scale))

    @staticmethod
    def getSetupTransformation(normal_vector=np.array([0., 0., 1.]),
                               origin_point=np.array([0., 0., 0.]),
                               scale=1.):
        """ return forrowvecs matrix """
        normal_vector = np.array(
            [normal_vector[0], normal_vector[1], normal_vector[2]])

        rotation = math_utils.getMat4by4_to_rotate_xhat_to_vector(
            normal_vector, a=np.array([0., 0., 1.]))
        rotation_forrowvecs = math_utils.math_convention_to_p3d_mat4(rotation)

        scaling_forrowvecs = math_utils.math_convention_to_p3d_mat4(
            math_utils.getScalingMatrix4x4(scale, scale, scale))

        translation_forrowvecs = math_utils.getTranslationMatrix4x4_forrowvecs(
            origin_point[0], origin_point[1], origin_point[2])

        return scaling_forrowvecs * rotation_forrowvecs * translation_forrowvecs
        # self.setMat()  # reverse order column first row second convention


# class TextureOf2dImageData(TQGraphicsNodePath):
#     """ """
#     def __init__(self, mpl_fig, **kwargs):
#         """ get a 2d textured quad from a matplotlib figure object """
#         TQGraphicsNodePath.__init__(self, **kwargs)

#         self.tex_expression = tex_expression

#         self.makeObject()

#         self.doInitialSetupTransformation()

#     def doInitialSetupTransformation(self):
#         """ initial setup transformation: a unit quad with an image in the
#         background is being scaled so that the pixel height and width fits
#         exactly with the screen resolution"""

#         self.setMat(
#             conventions.getMat4_scale_quad_for_texture_pixels_to_match_screen_resolution() *
#             conventions.getMat4_scale_unit_quad_to_image_aspect_ratio(self.myPNMImage.getXSize(), self.myPNMImage.getYSize()))

#     def makeObject(self):
#         """ only creates geometry (doesn't transform it) """
#         self.set_node_p3d(custom_geometry.createTexturedUnitQuadGeomNode())
#         self.set_p3d_nodepath(self.getParent_p3d().attachNewNode_p3d(self.p3d_node))

#         def applyImageAndTexture():
#             """assign the Texture() to the NodePath() that contains the Geom()
#             load image with the object's hash"""
#             expr_hash = hashlib.sha256(
#                 str(self.tex_expression).encode("utf-8")).hexdigest()

#             myLatexImage = LatexImageManager.retrieveLatexImageFromHash(
#                 expr_hash)
#             if myLatexImage is None:
#                 myLatexImage = LatexImage(expression_str=self.tex_expression)
#                 myLatexImage.compileToPNG()
#                 LatexImageManager.addLatexImageToCompiledSet(myLatexImage)
#                 LatexImageManager.addLatexImageToLoadedSet(myLatexImage)

#             self.myPNMImage = myLatexImage.getPNMImage()
#             self.myTexture = texture_utils.getTextureFromImage(self.myPNMImage)
#             self.setTexture(self.myTexture, 1)
#             self.setTransparency(TransparencyAttrib.MAlpha)

#         applyImageAndTexture()


class TextureOf2dImageData(TQGraphicsNodePath):
    """ """

    def __init__(self, np_2d_arr=None, scaling=1.0, **kwargs):
        """ get a textured quad from a 2d array of pixel data """
        # self.np_2d_arr = np_2d_arr
        self.myTexture = None
        self.num_of_pixels_x = None
        self.num_of_pixels_y = None
        self.scaling = scaling

        TQGraphicsNodePath.__init__(self, **kwargs)

        self.makeObject()

        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        """ initial setup transformation: a unit quad with an image in the
        background is being scaled so that the pixel height and width fits
        exactly with the screen resolution"""

        self.setMat_normal(
            conventions.getMat4_scale_unit_quad_to_image_aspect_ratio(self.num_of_pixels_x, self.num_of_pixels_y).dot(
                conventions.getMat4_scale_quad_for_texture_pixels_to_match_screen_resolution()
            ).dot(math_utils.getScalingMatrix4x4(self.scaling, self.scaling, self.scaling)))

    def makeObject(self):
        """ only creates geometry (doesn't transform it) """
        self.set_node_p3d(custom_geometry.createTexturedUnitQuadGeomNode())
        self.set_p3d_nodepath(
            self.getParent_p3d().attachNewNode(self.get_node_p3d()))

        self.myTexture, self.num_of_pixels_x, self.num_of_pixels_y = texture_utils.getTextureFrom2d_bw_arr()
        self.myTexture.setMagfilter(SamplerState.FT_nearest)
        self.myTexture.setMinfilter(SamplerState.FT_nearest)
        self.setTexture(self.myTexture, 1)

        # self.setTransparency(TransparencyAttrib.MAlpha)

        self.setTwoSided(True)
        self.setLightOff(True)


class BasicText(# IndicatorPrimitive
):
    """ a text label attached to aspect2d,  """

    def __init__(self,
                 text="Basic text",
                 font=None):

        # IndicatorPrimitive.__init__(self)

        # self.height = 0.5               # in units of one panda unit

        self.pointsize = 11

        def get_height_p3d_from_pointsize(pt):
            """ let 1 p3d units be 100/pt_to_height_p3d_scale pt """
            pt_to_height_p3d_scale = 0.6
            return pt_to_height_p3d_scale * float(pt)/(100.)

        def get_font_bmp_pixels_from_height(height):
            """ 10 pixels from height of 0.1
                the aspect2d viewport goes in the up direction from -1 to 1 -> range of 2
            """
            pixels_per_p3d_length_unit = engine.tq_graphics_basics.get_window_size_y()/2.0
            return pixels_per_p3d_length_unit * height  # how many pixels

        self.text = text

        self.font = None
        if font is not None:
            self.font = font
        else:
            # self.font = "fonts/arial.egg"
            self.font = "fonts/arial.ttf"

        self.textNode = TextNode('foo')
        self.textNode.setText(self.text)
        self._font_p3d = loader.loadFont(self.font)

        self.pixels_per_unit = get_font_bmp_pixels_from_height(get_height_p3d_from_pointsize(self.pointsize))
        self._font_p3d.setPixelsPerUnit(self.pixels_per_unit)

        # self._font_p3d.setPointSize(64)
        # self._font_p3d.setSpaceAdvance(2)
        # self._font_p3d.setRenderMode(TextFont.RMPolygon)  # render font as polygons instead of bitmap

        self._font_p3d.setPointSize(self.pointsize)
        # self._font_p3d.setPixelsPerUnit(15)
        # self._font_p3d.setScaleFactor(1)
        # self._font_p3d.setTextureMargin(2)
        # self._font_p3d.setMinfilter(Texture.FTNearest)
        # self._font_p3d.setMagfilter(Texture.FTNearest)

        self.textNode.setFont(self._font_p3d)

        # self.textNode.setShadow(0.05, 0.05)
        # self.textNode.setShadowColor(0, 0, 0, 1)
        # self.set_p3d_nodepath(NodePath(self.textNode.generate()))

        self.text_p3d_nodepath = NodePath(self.textNode.generate())
        self.text_p3d_nodepath.reparentTo(aspect2d)
        self.text_p3d_nodepath.setPos(Vec3(0., 0., 0.))

        def get_scale_matrix_initial_to_font_size():
            """ """
            initial_height = self.textNode.getHeight()
            print("initial_height", initial_height)
            scale_factor_to_height_1 = 1./initial_height

            pixels_per_p3d_length_unit = engine.tq_graphics_basics.get_window_size_y()/2.0

            scale_height_1_to_pixels = 1./pixels_per_p3d_length_unit
            # print(scale_height_1_to_pixels * self.pixels_per_unit * 2.0)

            scale = scale_height_1_to_pixels * self.pixels_per_unit
            self.text_p3d_nodepath.setScale(scale, 1., scale)

        get_scale_matrix_initial_to_font_size()

    #     # self.do_trafo()

    # # def do_trafo(self):
    # #     """ """
    # #     text_size_base_scale = 0.07
    # #     self.setMat_normal(math_utils.getScalingMatrix4x4(text_size_base_scale, 1., text_size_base_scale).dot(
    # #         math_utils.getTranslationMatrix4x4(self.pos_x, 0., self.pos_y)
    # #     ))
