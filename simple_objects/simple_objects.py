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
    """ """
    def __init__(self, thickness=1., **kwargs):
        """ """
        IndicatorPrimitive.__init__(self, **kwargs)

        # these are graphical values
        # for more complex, e.g. recessed lines for vectors, you need another set
        # of variables to store the logical end points
        self.tip_point = None
        self.tail_point = None


class Line1dPrimitive(LinePrimitive):
    """ """
    def __init__(self, thickness=1., **kwargs):
        """ """
        LinePrimitive.__init__(self, **kwargs)

        self.thickness = thickness
        self.makeObject(thickness, **kwargs)

        self.setTailPoint(self.tail_point)
        self.setTipPoint(self.tip_point)

    def makeObject(self, thickness, **kwargs):
        self.set_node_p3d(custom_geometry.createColoredUnitLineGeomNode(
            thickness=thickness,
            color_vec4=kwargs.get("color")
        ))

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
            # print("Warning: setTipPoint exception: transformation skipped")
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

        if (self.tip_point is None or self.tail_point is None or self.tip_point == self.tail_point):
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

    def __init__(self, thickness=2., **kwargs):
        self._rotation_forrowvecs = Mat4()

        # this also sets the position
        Line1dPrimitive.__init__(
            self, thickness=thickness, **kwargs)

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

# class PathSegment:
#     """ a 2d path segment, with two circles and """
#     def __init__(self, p1, p2, thickness):

class OrientedDisk(IndicatorPrimitive):
    """ a disk with a normal vector (rotation) and a radius """

    def __init__(self, thickness=5., target_normal_vector=Vec3(1., 0., 0.), initial_scaling=1., num_of_verts=10, **kwargs):
        IndicatorPrimitive.__init__(self, **kwargs)

        self.from_geometry_generator_normal_vector = None  # as generated from geometry routine, see makeObject
        self.initial_scaling = initial_scaling
        self.target_normal_vector = target_normal_vector  # target normal vector
        self.num_of_verts = num_of_verts
        self.additional_trafo_nodepath = TQGraphicsNodePath()
        self.makeObject()
        self.doInitialSetupTransformation()

    def makeObject(self):
        node_p3d, _normal_vector_info = custom_geometry.createColoredUnitDisk(color_vec4=Vec4(1., 1., 1., 1.), num_of_verts=self.num_of_verts)
        self.from_geometry_generator_normal_vector = _normal_vector_info
        self.set_node_p3d(node_p3d)

        # nodepath order: original parent -> additional_trafo nodepath (setup transformations) -> actual OrientedDisk nodepath (it's own transformations)

        self.additional_trafo_nodepath.reparentTo_p3d(self.getParent_p3d())
        self.set_p3d_nodepath(
            self.additional_trafo_nodepath.attachNewNode_p3d(self.get_node_p3d()))

        self.setLightOff(1)
        self.setTwoSided(True)

    def get_additional_trafo_mat(self):
        """ """
        return math_utils.getMat4by4_to_rotate_xhat_to_vector(
            self.target_normal_vector, a=self.from_geometry_generator_normal_vector).dot(math_utils.getScalingMatrix4x4(self.initial_scaling, self.initial_scaling, self.initial_scaling))

    def doInitialSetupTransformation(self):
        """ initial setup transformation: a unit quad with an image in the
        background is being scaled so that the pixel height and width fits
        exactly with the screen resolution"""

        # make a new transformation node between it's current parent and itself and
        # give it a transform
        self.additional_trafo_nodepath.setMat_normal(self.get_additional_trafo_mat())

        # TODO : CHECK WHY THIS IS NOT EVEN APPLIED
        print("----SETTING additional trafo: \n", self.additional_trafo_nodepath.getMat())

    def reparentTo(self, *args, **kwargs):
        """ """
        return self.additional_trafo_nodepath.reparentTo(*args, **kwargs)

# class OrientedDisk(IndicatorPrimitive):
#     """ a disk with a normal vector (rotation) and a radius """

#     def __init__(self, thickness=5., target_normal_vector=Vec3(1., 0., 0.), initial_scaling=1., num_of_verts=10, **kwargs):
#         IndicatorPrimitive.__init__(self, **kwargs)

#         self.from_geometry_generator_normal_vector = None  # as generated from geometry routine, see makeObject
#         self.initial_scaling = initial_scaling
#         self.target_normal_vector = target_normal_vector  # target normal vector
#         self.num_of_verts = num_of_verts
#         self.additional_trafo_nodepath = TQGraphicsNodePath()
#         self.makeObject()
#         self.doInitialSetupTransformation()

#     def makeObject(self):
#         node_p3d, _normal_vector_info = custom_geometry.createColoredUnitDisk(color_vec4=Vec4(1., 1., 1., 1.), num_of_verts=self.num_of_verts)
#         self.from_geometry_generator_normal_vector = _normal_vector_info
#         self.set_node_p3d(node_p3d)

#         # nodepath order: original parent -> additional_trafo nodepath (setup transformations) -> actual OrientedDisk nodepath (it's own transformations)
#         self.additional_trafo_nodepath.reparentTo_p3d(self.getParent_p3d())
#         self.set_p3d_nodepath(
#             self.additional_trafo_nodepath.attachNewNode_p3d(self.get_node_p3d()))

#         self.setLightOff(1)
#         self.setTwoSided(True)

#     def get_additional_trafo_mat(self):
#         """ """
#         return math_utils.getMat4by4_to_rotate_xhat_to_vector(
#             self.target_normal_vector, a=self.from_geometry_generator_normal_vector).dot(math_utils.getScalingMatrix4x4(self.initial_scaling, self.initial_scaling, self.initial_scaling))

#     def doInitialSetupTransformation(self):
#         """ initial setup transformation: a unit quad with an image in the
#         background is being scaled so that the pixel height and width fits
#         exactly with the screen resolution"""

#         # make a new transformation node between it's current parent and itself and
#         # give it a transform
#         self.additional_trafo_nodepath.setMat_normal(self.get_additional_trafo_mat()
#             # math_utils.getTranslationMatrix4x4(1.0, 0., 0.)
#         )

#         # TODO : CHECK WHY THIS IS NOT EVEN APPLIED
#         print("----SETTING additional trafo: \n", self.additional_trafo_nodepath.getMat())

#     def reparentTo(self, *args, **kwargs):
#         """ """
#         return self.additional_trafo_nodepath.reparentTo(*args, **kwargs)


class OrientedCircle(IndicatorPrimitive):
    """ a disk with a normal vector (rotation) and a radius """

    def __init__(self, thickness=5., target_normal_vector=Vec3(1., 0., 0.), initial_scaling=1., num_of_verts=10, **kwargs):
        IndicatorPrimitive.__init__(self, **kwargs)

        self.from_geometry_generator_normal_vector = None  # as generated from geometry routine, see makeObject
        self.initial_scaling = initial_scaling
        self.target_normal_vector = target_normal_vector  # target normal vector
        self.num_of_verts = num_of_verts
        self.additional_trafo_nodepath = TQGraphicsNodePath()
        self.makeObject()
        self.doInitialSetupTransformation()

    def makeObject(self):
        node_p3d = custom_geometry.createCircle(color_vec4=Vec4(1., 1., 1., 1.), with_hole=False, num_of_verts=self.num_of_verts, radius=1.)
        self.from_geometry_generator_normal_vector = Vec3(0., 0., 1.)
        self.set_node_p3d(node_p3d)

        # nodepath order: original parent -> additional_trafo nodepath (setup transformations) -> actual OrientedCircle nodepath (it's own transformations)
        self.additional_trafo_nodepath.reparentTo_p3d(self.getParent_p3d())
        self.set_p3d_nodepath(
            self.additional_trafo_nodepath.attachNewNode_p3d(self.get_node_p3d()))

        self.setLightOff(1)
        self.setTwoSided(True)

    def get_additional_trafo_mat(self):
        """ """
        return math_utils.getMat4by4_to_rotate_xhat_to_vector(
            self.target_normal_vector, a=self.from_geometry_generator_normal_vector).dot(math_utils.getScalingMatrix4x4(self.initial_scaling, self.initial_scaling, self.initial_scaling))

    def doInitialSetupTransformation(self):
        """ initial setup transformation: a unit quad with an image in the
        background is being scaled so that the pixel height and width fits
        exactly with the screen resolution"""

        # make a new transformation node between it's current parent and itself and
        # give it a transform
        self.additional_trafo_nodepath.setMat_normal(self.get_additional_trafo_mat()
            # math_utils.getTranslationMatrix4x4(1.0, 0., 0.)
        )

        # TODO : CHECK WHY THIS IS NOT EVEN APPLIED
        print("----SETTING additional trafo: \n", self.additional_trafo_nodepath.getMat())

    def reparentTo(self, *args, **kwargs):
        """ """
        return self.additional_trafo_nodepath.reparentTo(*args, **kwargs)


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


class Point3dCursor(TQGraphicsNodePath):
    """ a white Point3d with a
    black and a white circle aroud it for accentuation """

    def __init__(self, camera_gear, scale=0.05):
        """ """
        self.camera_gear = camera_gear # needed for re-orientation towards the camera whenever it's updated or the camera moves

        self.scale_total = scale
        self.rel_scale_point_center = 0.4
        self.rel_scale_circle_outer_first = 0.6
        self.rel_scale_circle_outer_second = 0.9
        # self.rel_scale_circle_outer_third = 1.2
        self.num_of_verts = 20

        self.color_point_center = Vec4(1., 1., 1., 1.)
        self.color_circle_outer_first = Vec4(0., 0., 0., 1.)
        self.color_circle_outer_second = Vec4(1., 1., 1., 1.)
        # self.color_circle_outer_third = Vec4(0., 0., 0., 1.)

        self._initial_normal_vector = Vec3(1., 0., 0.)

        TQGraphicsNodePath.__init__(self)

        self.point_center = Point3d(
            scale=self.scale_total * self.rel_scale_point_center)
        self.point_center.reparentTo(self)

        self.circle_outer_first = OrientedCircle(
            target_normal_vector=self._initial_normal_vector,
            initial_scaling=self.scale_total * self.rel_scale_circle_outer_first,
            num_of_verts=self.num_of_verts,
            thickness=3.)
        self.circle_outer_first.reparentTo(self)

        self.circle_outer_second = OrientedCircle(
            target_normal_vector=self._initial_normal_vector,
            initial_scaling=self.scale_total * self.rel_scale_circle_outer_second,
            num_of_verts=self.num_of_verts,
            thickness=3.)
        self.circle_outer_second.reparentTo(self)

        # the closest to root node of the cursor saves the translation (along the edgeplayer) (i.e. here the additional_trafo_nodepath)
        # the edgeplayer node itself actually only has a rotation, which it sets to
        # always reorient towards the camera. If I didn't separate the two (translation and rotation)
        # into two separate nodes, I would need to declare additional functions for TQGraphicsNodePath to
        # set and get Rotation, Position and Scaling components of the Model Matrix independently of each other
        # (which I guess can be done, since a Model Matrix actually be decomposed)

        self.additional_trafo_nodepath = TQGraphicsNodePath()
        self.additional_trafo_nodepath.reparentTo_p3d(self.getParent_p3d())
        super().reparentTo(self.additional_trafo_nodepath)

        self.camera_gear.add_camera_move_hook(self._adjust)

        self._adjust()

    def _adjust(self):
        self.point_center.setColor(self.color_point_center)
        self.circle_outer_first.setColor(self.color_circle_outer_first)
        self.circle_outer_second.setColor(self.color_circle_outer_second)

        self._adjust_rotation_to_camera()

    def _adjust_rotation_to_camera(self):
        """ """
        # -- get the forward vector of the camera in the coordinate system of the cursor
        v_cam_forward = math_utils.p3d_to_np(engine.tq_graphics_basics.tq_render.getRelativeVector(
            self.camera_gear.p3d_camera, self.camera_gear.p3d_camera.node().getLens().getViewVector()))
        v_cam_forward = v_cam_forward / np.linalg.norm(v_cam_forward)

        # now set the rotation to point into the direction of v_cam_forward
        rot_mat_to_apply = math_utils.getMat4by4_to_rotate_xhat_to_vector(v_cam_forward,
                                                                          a=self._initial_normal_vector)
        self.setMat(math_utils.to_forrowvecs(rot_mat_to_apply))

    def setPos(self, *args, **kwargs):
        """ """
        return self.additional_trafo_nodepath.setPos(*args, **kwargs)

    def reparentTo(self, *args, **kwargs):
        """ """
        return self.additional_trafo_nodepath.reparentTo(*args, **kwargs)
