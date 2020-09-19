from conventions import conventions
from simple_objects import custom_geometry

from local_utils import math_utils
from .primitives import IndicatorPrimitive, Box2dCentered, ConePrimitive
from simple_objects.animator import Animator
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
import sys, os

class Point(IndicatorPrimitive):
    def __init__(self, **kwargs):
        if 'color' in kwargs:
            self.color = kwargs.get('color')
        else:
            self.color = Vec4(1., 1., 1., 1.)

        super(Point, self).__init__()


class Point3d(Point):
    def __init__(self, scale=0.025, **kwargs):
        self.scale = scale

        if 'pos' in kwargs:
            self.pos = kwargs.get('pos')
        else:
            self.pos = None

        Point.__init__(self, **kwargs)

        self.makeObject()
        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):

        scaling_forrowvecs = math_utils.math_convention_to_p3d_mat4(math_utils.getScalingMatrix4x4(self.scale, self.scale, self.scale))

        self.form_from_primitive_trafo = scaling_forrowvecs # * rotation_forrowvecs
        self.nodePath.setMat(self.form_from_primitive_trafo)
        self.setColor(self.color)

        self.setPos(self.pos)

    def makeObject(self):
        # load a gltf file
        from panda3d.core import Filename
        self.nodePath = loader.loadModel(
            Filename.fromOsSpecific(
                # root of project
                os.path.abspath(sys.path[0])).getFullpath()
            + "/models/small_sphere_triangulated_with_face_normals.gltf")

        self.nodePath.reparentTo(render)
        self.node = self.nodePath.node()

        self.nodePath.setRenderModeFilled()

        # override the vertex colors of the model
        self.nodePath.setColor(self.color)

        self.nodePath.setLightOff(1)


    def setPos(self, pos):
        self.pos = pos

        if self.pos is not None:
            self.nodePath.setPos(pos)
            self.nodePath.show()
        else:
            self.nodePath.hide()

    def getPos(self):
        return self.nodePath.getPos()



class PointPrimitive(Point):
    """ a pixel point (no real spatial extent for e.g. picking) """
    def __init__(self, **kwargs):
        Point.__init__(self, **kwargs)

        self.makeObject()

    def makeObject(self):
        self.node = custom_geometry.create_GeomNode_Single_Point(
            color_vec4=Vec4(1., 1., 1., 1.))

        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setLightOff(1)
        # self.nodePath.setRenderModeThickness(5)


class Point2d(Point):
    """ a (2d) quad """
    def __init__(self, **kwargs):
        Point.__init__(self, **kwargs)

    def makeObject(self):
        self.node = custom_geometry.createColoredUnitQuadGeomNode(
            color_vec4=Vec4(1., 1., 1., 1.), center_it=True)

        self.nodePath = render.attachNewNode(self.node)

        self.nodePath.setTwoSided(True)
        self.nodePath.setLightOff(1)


# ---- lines

class LinePrimitive(IndicatorPrimitive):
    def __init__(self, thickness=1., color=Vec4(1., 1., 1., 1.)):
        IndicatorPrimitive.__init__(self)

        # these are graphical values
        # for more complex, e.g. recessed lines for vectors, you need another set
        # of variables to store the logical end points
        self.tip_point = None
        self.tail_point = None

        self.color = color
        # self.makeObject(thickness, color)

    # def makeObject(self, thickness, color):
    #     self.node = custom_geometry.createColoredUnitLineGeomNode(
    #         thickness=thickness, color_vec4=self.color)
    #     self.nodePath = render.attachNewNode(self.node)
    #     self.nodePath.setLightOff(1)


class Line1dPrimitive(LinePrimitive):
    def __init__(self, thickness=1., **kwargs):
        LinePrimitive.__init__(self, **kwargs)

        self.thickness = thickness
        self.makeObject(thickness, self.color)

        self.setTailPoint(self.tail_point)
        self.setTipPoint(self.tip_point)

    def makeObject(self, thickness, color):
        self.node = custom_geometry.createColoredUnitLineGeomNode(
            thickness=thickness,
            color_vec4=self.color)
        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setLightOff(1)

    def setTipPoint(self, point):
        # the diff_vec needs to be first scaled and rotated, then translated by it's position
        # to get a line at a position of a certain tip and tail point

        self.tip_point = point

        if (self.tip_point is None or self.tail_point is None):
            # set vector status to hidden
            self.nodePath.hide()
            return
        else:
            self.nodePath.show()

        diff_vec = self.tip_point - self.tail_point

        rotation_forrowvecs = (
            math_utils.math_convention_to_p3d_mat4(
                math_utils.getMat4by4_to_rotate_xhat_to_vector(diff_vec)))

        self._rotation_forrowvecs = rotation_forrowvecs

        # scaling matrix: scale the vector along xhat when it points in xhat direction
        # (to prevent skewing if the vector's line is a mesh)

        scaling_forrowvecs = math_utils.math_convention_to_p3d_mat4(math_utils.getScalingMatrix4x4(np.linalg.norm(diff_vec), 1., 1.))

        # apply the net transformation
        # first the scaling, then the rotation_forrowvecs
        # remember, the row vector stands on the left in p3d multiplication
        # so the order is reversed

        scaling_and_rotation_forrowvecs = scaling_forrowvecs * self._rotation_forrowvecs

        translation_forrowvecs = math_utils.getTranslationMatrix3d_forrowvecs(*self.nodePath.getPos())

        self.nodePath.setMat(self.form_from_primitive_trafo * scaling_and_rotation_forrowvecs * translation_forrowvecs)

        # for some weird reason, I have to run setTailPoint again ...
        self.setTailPoint(self.tail_point, run_setTipPoint_again=False)

    def setTailPoint(self, point, run_setTipPoint_again=True):
        """ this sets the tailpoint (self.nodePath.getPos()), keeping the tip point at it's original
            position """

        self.tail_point = point

        if (self.tip_point is None or self.tail_point is None):
            self.nodePath.hide()
            return
        else:
            self.nodePath.show()

        self.nodePath.setPos(point)

        # setTipPoint applies a transformation on an already existing line object, i.e.
        #   first figure out the difference betweeen the tip point (self.tip_point) and the tail point (self.nodePath.getPos()) to get the length of the vector
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


class Line1dSolid(Line1dPrimitive):
    def __init__(self, thickness=2., color=Vec4(1., 1., 1., 1.), **kwargs):
        self._rotation_forrowvecs = Mat4()

        Line1dPrimitive.__init__(self, thickness=thickness, color=color)  # this also sets the position

        self.doInitialSetupTransformation(**kwargs)

    def doInitialSetupTransformation(self, **kwargs):
        self.form_from_primitive_trafo = self.nodePath.getMat()


class LineDashedPrimitive(Animator):
    def __init__(self, thickness=1., color=Vec4(1., 1., 1., 1.), howmany_periods=5.):
        Animator.__init__(self)
        self.thickness = thickness
        self.color = color
        self.howmany_periods = howmany_periods
        self.makeObject(thickness, color, howmany_periods)

    def makeObject(self, thickness, color, howmany_periods):
        self.node = custom_geometry.createColoredUnitDashedLineGeomNode(
            thickness=thickness, color_vec4=self.color, howmany_periods=5.)
        self.nodePath = render.attachNewNode(self.node)

        self.nodePath.setLightOff(1)

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
        self.form_from_primitive_trafo = self.nodePath.getMat()

        self.setTipPoint(Vec3(1., 0., 0.))


class Line2dObject(Box2dCentered):
    def __init__(self, **kwargs):
        super(Line2dObject, self).__init__()
        self.doInitialSetupTransformation(**kwargs)

    def doInitialSetupTransformation(self, **kwargs):
        if 'width' in kwargs:
            self.width = kwargs.get('width')
        else:
            self.width = 0.025

        scaling = math_utils.getScalingMatrix3d_forrowvecs(1., 1., self.width)

        self.length = 1.
        self.translation_to_xhat_forrowvecs = math_utils.getTranslationMatrix3d_forrowvecs(
            0.5, 0, 0)

        self.form_from_primitive_trafo = scaling * self.translation_to_xhat_forrowvecs
        self.nodePath.setMat(self.form_from_primitive_trafo)

        # self.form_from_primitive_trafo = self.nodePath.getMat()
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
        # self.nodePath.setScale(self.scale, self.scale, self.scale)

        scaling_forrowvecs = math_utils.getScalingMatrix3d_forrowvecs(
            self.scale,
            self.scale,
            self.scale)

        self.form_from_primitive_trafo = scaling_forrowvecs

    def makeObject(self):
        """
        it's not just a scaled quad, so it needs different Geometry
        """
        self.node = custom_geometry.createColoredArrowGeomNode(
            color_vec4=Vec4(1., 1., 1., 1.), center_it=True)
        self.nodePath = render.attachNewNode(self.node)

        self.nodePath.setTwoSided(True)


class ArrowHeadCone(Box2dCentered):
    scale = .1

    def __init__(self, **kwargs):
        super(ArrowHeadCone, self).__init__()
        self.doInitialSetupTransformation(**kwargs)

    def doInitialSetupTransformation(self, **kwargs):
        # self.nodePath.setScale(self.scale, self.scale, self.scale)

        scaling_forrowvecs = math_utils.getScalingMatrix3d_forrowvecs(
            self.scale,
            self.scale,
            self.scale)

        # also, rotate this one to orient itself in the x direction
        rotation_forrowvecs = math_utils.get_R_y_forrowvecs(np.pi/2.)

        self.form_from_primitive_trafo = scaling_forrowvecs * rotation_forrowvecs

        self.nodePath.setMat(self.form_from_primitive_trafo)

    def makeObject(self):
        self.node = custom_geometry.create_GeomNode_Cone(
            color_vec4=Vec4(1., 1., 1., 1.)) # the self.'node' is a geomnode
        # or more generally a PandaNode
        # typically, if the geometry isn't changed in-place,
        # only the NodePath is called at later times

        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setTwoSided(True)


class ArrowHeadConeShaded(IndicatorPrimitive):
    def __init__(self, color=Vec4(0., 0., 0., 0.), scale=1./5.):
        self.color=color
        self.scale=scale

        super(ArrowHeadConeShaded, self).__init__()

        self.makeObject()

        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        # self.nodePath.setScale(self.scale, self.scale, self.scale)

        scaling_forrowvecs = (
            math_utils.math_convention_to_p3d_mat4(math_utils.getScalingMatrix4x4(self.scale,
                                                                                  self.scale,
                                                                                  self.scale)))

        # the underlying model is already rotated in the x direction
        # rotation_forrowvecs = math_utils.get_R_y_forrowvecs(np.pi/2.)

        self.form_from_primitive_trafo = scaling_forrowvecs # * rotation_forrowvecs

        self.nodePath.setMat(self.form_from_primitive_trafo)

    def makeObject(self):
        # load a gltf file
        from panda3d.core import Filename
        self.nodePath = loader.loadModel(
            Filename.fromOsSpecific(
                os.path.abspath(sys.path[0])).getFullpath()  # root of project
            + "/models/unit_cone_triangulated_with_face_normals.gltf")
        self.nodePath.reparentTo(render)
        self.node = self.nodePath.node()

        # override the vertex colors of the model
        self.nodePath.setColor(self.color)

        self.nodePath.setRenderModeFilled(True)


class SphereModelShaded(Box2dCentered):
    def __init__(self, color=Vec4(1., 1., 1., 1.), scale=0.1):
        self.color=color
        self.scale=scale
        super(SphereModelShaded, self).__init__()
        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        scaling_forrowvecs = math_utils.getScalingMatrix3d_forrowvecs(
            self.scale,
            self.scale,
            self.scale)

        self.form_from_primitive_trafo = scaling_forrowvecs # * rotation_forrowvecs

        self.nodePath.setMat(self.form_from_primitive_trafo)

    def makeObject(self):
        # load a gltf file
        from panda3d.core import Filename
        self.nodePath = loader.loadModel(
            Filename.fromOsSpecific(
                os.path.abspath(sys.path[0])).getFullpath()  # root of project
            + "/models/small_sphere_triangulated_with_face_normals.gltf")
        self.nodePath.reparentTo(render)
        self.node = self.nodePath.node()

        # override the vertex colors of the model
        self.nodePath.setColor(self.color)

        self.nodePath.setLightOff(1)


from conventions.conventions import compute2dPosition
from panda3d.core import TextNode


class Pinned2dLabel:
    def __init__(self, refpoint3d=Point3(1., 1., 1.), text="pinned?", xshift=0., yshift=0.,
                 font="cmr12.egg"):
        self.refpoint3d = refpoint3d
        self.text = text
        self.nodeisattachedtoaspect2d = False

        self.font = font
        self.font_p3d = loader.loadFont(font)

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

    def update(self):
        pos_rel_to_cam = base.cam.get_relative_point(base.render,
                                                     self.refpoint3d)
        p2d = Point2()

        if not self.nodeisattachedtoaspect2d:
            self.textNode = TextNode('myPinned2dLabel')
            self.textNode.setText(self.text)

            # load a font
            # cmr12 = loader.loadFont('cmr12.egg')

            self.textNode.setFont(self.font_p3d)

            # set a shadow
            self.textNode.setShadow(0.05, 0.05)
            self.textNode.setShadowColor(0, 0, 0, 1)
            self.textNode_p3d_generated = self.textNode.generate()

            self.textNodePath = aspect2d.attachNewNode(self.textNode_p3d_generated)

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
        from conventions.conventions import win_aspect_ratio
        self.textNodePath.setPos((p2d[0] + self.xshift) * win_aspect_ratio, 0, p2d[1] + self.yshift)


class Fixed2dLabel:
    def __init__(self, # refpoint3d=Point3(1., 1., 1.),
                 text="fixed?", xshift=0., yshift=0.,
                 font="cmr12.egg"):
        # self.refpoint3d = refpoint3d
        self.text = text
        self.nodeisattachedtoaspect2d = False

        self.font = font
        self.font_p3d = loader.loadFont(font)

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

    def update(self):
        # pos_rel_to_cam = base.cam.get_relative_point(base.render,
        #                                              self.refpoint3d)
        # p2d = Point2()

        if not self.nodeisattachedtoaspect2d:
            self.textNode = TextNode('myFixed2dLabel')
            self.textNode.setText(self.text)

            # load a font
            # cmr12 = loader.loadFont('cmr12.egg')

            self.textNode.setFont(self.font_p3d)

            # set a shadow
            self.textNode.setShadow(0.05, 0.05)
            self.textNode.setShadowColor(0, 0, 0, 1)
            self.textNode_p3d_generated = self.textNode.generate()

            self.textNodePath = aspect2d.attachNewNode(self.textNode_p3d_generated)

            self.nodeisattachedtoaspect2d = True
            self.textNodePath.setScale(0.07)
            self.textNodePath.show()

        # place text in x, z in [-1, 1] boundaries and
        # the y coordinate gets ignored for the TextNode
        # parented by aspect2d
        from conventions.conventions import win_aspect_ratio
        self.textNodePath.setPos(# (-1. + self.xshift) * win_aspect_ratio,
                                 # 0.,
                                 # 1. + self.yshift
            (-1. + self.xshift) * win_aspect_ratio, 0., -1. + self.yshift
        )


class OrientedDisk(IndicatorPrimitive):
    """ a disk with a normal vector (rotation) and a radius
    TODO: implement normal vector orientaion """
    def __init__(self, thickness=5., **kwargs):
        IndicatorPrimitive.__init__(self, **kwargs)
        self.makeObject()

    def makeObject(self):
        self.node = custom_geometry.createColoredUnitDisk(
            color_vec4=Vec4(1., 1., 1., 1.))

        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setLightOff(1)
        self.nodePath.setTwoSided(True)


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
        self.makeObject(num_of_verts, radius, with_hole=with_hole, thickness=thickness)

        self.nodePath.setMat(
            OrientedCircle.getSetupTransformation(normal_vector, origin_point, scale))

    def makeObject(self, num_of_verts, radius, with_hole, thickness):

        self.node = custom_geometry.createCircle(
            color_vec4=Vec4(1., 1., 1., 1.),
            with_hole=with_hole,
            num_of_verts=num_of_verts,
            radius=radius)

        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setLightOff(1)
        self.nodePath.setRenderModeThickness(thickness)

        # self.nodePath.setTwoSided(True)

        # ---- set orientation from normal vector
        # self.nodePath.setMat()

    def setPos(self, origin_point):
        self.origin_point = origin_point

        self.nodePath.setMat(
            OrientedCircle.getSetupTransformation(self.normal_vector,
                                                  self.origin_point,
                                                  self.scale))

    @staticmethod
    def getSetupTransformation(normal_vector=np.array([0., 0., 1.]),
                               origin_point=np.array([0., 0., 0.]),
                               scale=1.):
        """ return forrowvecs matrix """
        normal_vector = np.array([normal_vector[0], normal_vector[1], normal_vector[2]])

        rotation = math_utils.getMat4by4_to_rotate_xhat_to_vector(normal_vector, a=np.array([0., 0., 1.]))
        rotation_forrowvecs = math_utils.math_convention_to_p3d_mat4(rotation)

        scaling_forrowvecs = math_utils.math_convention_to_p3d_mat4(math_utils.getScalingMatrix4x4(scale, scale, scale))

        translation_forrowvecs = math_utils.getTranslationMatrix3d_forrowvecs(origin_point[0], origin_point[1], origin_point[2])

        return scaling_forrowvecs * rotation_forrowvecs * translation_forrowvecs
        # self.nodePath.setMat()  # reverse order column first row second convention
