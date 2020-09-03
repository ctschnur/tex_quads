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
        if 'pos' in kwargs:
            self.pos = kwargs.get('pos')
        else:
            self.pos = Vec3(0., 0., 0.)

        if 'color' in kwargs:
            self.color = kwargs.get('color')
        else:
            self.color = Vec4(1., 1., 1., 1.)

        super(Point, self).__init__()

class Point3d(Point):
    def __init__(self, scale=0.025, **kwargs):
        self.scale = scale
        Point.__init__(self, **kwargs)

        self.makeObject()
        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):

        scaling_forrowvecs = math_utils.math_convention_to_p3d_mat4(math_utils.getScalingMatrix4x4(self.scale, self.scale, self.scale))

        self.form_from_primitive_trafo = scaling_forrowvecs # * rotation_forrowvecs
        self.nodePath.setMat(self.form_from_primitive_trafo)

        self.setPos(self.pos)
        self.setColor(self.color)

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

        # self.nodePath.setRenderModeWireFrame(False)
        self.nodePath.setRenderModeFilled()

        # override the vertex colors of the model
        self.nodePath.setColor(self.color)

        self.nodePath.setLightOff(1)

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
        self.nodePath.setRenderModeThickness(5)

        self.setPos(self.pos)


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
        self.tip_point = np.array([1., 1., 1.])
        self.tail_point = np.array([0., 0., 0.])
        self.color = color
        self.makeObject(thickness, color)

    def makeObject(self, thickness, color):
        self.node = custom_geometry.createColoredUnitLineGeomNode(
            thickness=thickness, color_vec4=self.color)
        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setLightOff(1)


class Line1dPrimitive(LinePrimitive):
    def __init__(self, thickness=1., **kwargs):
        LinePrimitive.__init__(self, **kwargs)

        self.thickness = thickness
        self.makeObject(thickness, self.color)

    def makeObject(self, thickness, color):
        self.node = custom_geometry.createColoredUnitLineGeomNode(
            thickness=thickness,
            color_vec4=self.color)
        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setLightOff(1)

    def setTipPoint(self, tip_point):
        # the diff_vec needs to be first scaled and rotated, then translated by self.pos
        # to get a line at a position of a certain tip and tail point

        self.tip_point = tip_point
        diff_vec = tip_point - self.pos

        rotation_forrowvecs = math_utils.math_convention_to_p3d_mat4(math_utils.getMat4by4_to_rotate_xhat_to_vector(diff_vec))
        self._rotation_forrowvecs = rotation_forrowvecs

        # scaling matrix: scale the vector along xhat when it points in xhat direction
        # (to prevent skewing if the vector's line is a mesh)

        scaling_forrowvecs = math_utils.math_convention_to_p3d_mat4(math_utils.getScalingMatrix4x4(np.linalg.norm(diff_vec), 1., 1.))

        # apply the net transformation
        # first the scaling, then the rotation_forrowvecs
        # remember, the row vector stands on the left in p3d multiplication
        # so the order is reversed

        scaling_and_rotation_forrowvecs = scaling_forrowvecs * self._rotation_forrowvecs

        translation_forrowvecs = math_utils.getTranslationMatrix3d_forrowvecs(self.pos[0], self.pos[1], self.pos[2])

        self.nodePath.setMat(self.form_from_primitive_trafo * scaling_and_rotation_forrowvecs * translation_forrowvecs)

    def getTipPoint(self):
        return self.tip_point

    def getTailPoint(self):
        return self.getPos()


class Line1dSolid(Line1dPrimitive):
    initial_length = 1.
    # thickness is derived from Line1dPrimitive

    def __init__(self, thickness=2., color=Vec4(1., 1., 1., 1.), **kwargs):
        Line1dPrimitive.__init__(self, thickness=thickness, color=color)  # this also sets the position

        self._rotation_forrowvecs = Mat4()

        # at this point, the default position (tail point) and tip point are defined

        self.doInitialSetupTransformation(**kwargs)

    def doInitialSetupTransformation(self, **kwargs):
        self.length = self.initial_length
        self.form_from_primitive_trafo = self.nodePath.getMat()
        self.tip_point = None
        self.pos = np.array([0., 0., 0.])
        self.setTipPoint(Vec3(1., 0., 0.))


    def setPos(self, point_vec3):
        """ this is an alias for setting the tail point """
        self.setTailPoint(point_vec3)

    def setTailPoint(self, point_vec3):
        """ this sets the tailpoint (self.pos), keeping the tip point at it's original position """
        IndicatorPrimitive.setPos(self, point_vec3)

        # setTipPoint applies a transformation on an already existing line object, i.e.
        #   first figure out the difference betweeen the tip point (self.tip_point) and the tail point (self.pos) to get the length of the vector
        #   then take the difference vector (diff_vec)
        #   knowing the difference vector, compute the rotation matrix for the position vector diff_vec
        #   if you want to set the rotation using a matrix, then you have to set the position as well using a matrix
        #   to do that, implement the affine transformation in math_utils
        # must take into account the tailpoint
        self.setTipPoint(self.tip_point)


    def getRotation(self):
        """ forrowvecs """

        assert self._rotation_forrowvecs
        return self._rotation_forrowvecs


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


class Line1dDashed(LineDashedPrimitive):
    initial_length = 1.

    def __init__(self, thickness=2., color=Vec4(1., 1., 1., 1.), howmany_periods=5., **kwargs):
        super(Line1dDashed, self).__init__(
            thickness=thickness, color=color, howmany_periods=howmany_periods)

        self._rotation_forrowvecs = Mat4()

        self.doInitialSetupTransformation(**kwargs)

    def doInitialSetupTransformation(self, **kwargs):
        # if 'thickness' in kwargs:
        #     self.thickness = kwargs.get('thickness')

        self.length = self.initial_length
        # self.translation_to_xhat_forrowvecs = math_utils.getTranslationMatrix3d_forrowvecs(0.5, 0, 0)

        # self.form_from_primitive_trafo = scaling * self.translation_to_xhat_forrowvecs
        # self.nodePath.setMat(self.form_from_primitive_trafo)

        self.form_from_primitive_trafo = self.nodePath.getMat()

        self.setTipPoint(Vec3(1., 0., 0.))

    def getRotation(self):
        """
        forrowvecs
        """

        assert self._rotation_forrowvecs
        return self._rotation_forrowvecs

class Line2dObject(Box2dCentered):
    width = 0.025
    initial_length = 1.

    def __init__(self, **kwargs):
        super(Line2dObject, self).__init__()
        self.doInitialSetupTransformation(**kwargs)

    def doInitialSetupTransformation(self, **kwargs):
        if 'width' in kwargs:
            self.width = kwargs.get('width')

        scaling = math_utils.getScalingMatrix3d_forrowvecs(1., 1., self.width)
        self.length = self.initial_length
        self.translation_to_xhat_forrowvecs = math_utils.getTranslationMatrix3d_forrowvecs(
            0.5, 0, 0)

        self.form_from_primitive_trafo = scaling * self.translation_to_xhat_forrowvecs
        self.nodePath.setMat(self.form_from_primitive_trafo)

        # self.form_from_primitive_trafo = self.nodePath.getMat()
        self.setTipPoint(Vec3(1., 0., 0.))

    def getRotation(self):
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
            ArrowHead.scale,
            ArrowHead.scale,
            ArrowHead.scale)

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
            ArrowHead.scale,
            ArrowHead.scale,
            ArrowHead.scale)

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
    scale = .1

    def __init__(self, color=Vec4(0., 0., 0., 0.)):
        self.color=color
        super(ArrowHeadConeShaded, self).__init__()

        self.makeObject()

        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        # self.nodePath.setScale(self.scale, self.scale, self.scale)

        scaling_forrowvecs = math_utils.math_convention_to_p3d_mat4(math_utils.getScalingMatrix4x4(ArrowHead.scale, ArrowHead.scale, ArrowHead.scale))

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
    # from direct.gui.OnscreenText import OnscreenText
    #     textObject = OnscreenText(text='my text string', pos=(-0.5, 0.02), scale=0.07)

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

        # self.nodePath.setRenderModeThickness(5)


class OrientedCircle(IndicatorPrimitive):
    """ a circle with a normal vector (rotation) and a radius
    TODO: implement normal vector orientaion """

    def __init__(self,
                 origin_point=Vec3(1., 1., 1.),
                 normal_vector_vec3=Vec3(1., 1., 1.),
                 radius=1.,
                 scale=1.,
                 num_of_verts=10,
                 **kwargs):

        self.scale = scale
        self.normal_vector = normal_vector_vec3
        self.pos = origin_point
        # self.num_of_verts = num_of_verts

        IndicatorPrimitive.__init__(self, **kwargs)
        self.makeObject(num_of_verts, radius)

        self.nodePath.setMat(
            OrientedCircle.getSetupTransformation(normal_vector_vec3, origin_point, scale))

    def makeObject(self, num_of_verts, radius):
        self.node = custom_geometry.createCircle(
            color_vec4=Vec4(1., 1., 1., 1.),
            with_hole=True,
            num_of_verts=num_of_verts,
            radius=radius)

        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setLightOff(1)
        # self.nodePath.setTwoSided(True)

        # self.nodePath.setRenderModeThickness(5)

        # ---- set orientation from normal vector
        # self.nodePath.setMat()

    @staticmethod
    def getSetupTransformation(normal_vector_vec3=np.array([0., 0., 1.]),
                               origin_point=np.array([0., 0., 0.]),
                               scale=1.):
        """ return forrowvecs matrix """
        normal_vector_vec3 = np.array([normal_vector_vec3[0], normal_vector_vec3[1], normal_vector_vec3[2]])

        rotation = math_utils.getMat4by4_to_rotate_xhat_to_vector(normal_vector_vec3, a=np.array([0., 0., 1.]))
        rotation_forrowvecs = math_utils.math_convention_to_p3d_mat4(rotation)

        scaling_forrowvecs = math_utils.math_convention_to_p3d_mat4(math_utils.getScalingMatrix4x4(scale, scale, scale))

        translation_forrowvecs = math_utils.getTranslationMatrix3d_forrowvecs(origin_point[0], origin_point[1], origin_point[2])

        return scaling_forrowvecs * rotation_forrowvecs * translation_forrowvecs
        # self.nodePath.setMat()  # reverse order column first row second convention
