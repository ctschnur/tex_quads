from conventions import conventions
from simple_objects import custom_geometry
from local_utils import math_utils
from .primitives import IndicatorPrimitive, Box2dCentered, LinePrimitive, LineDashedPrimitive, ConePrimitive
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

class Point(Box2dCentered):
    scale_z = .05
    scale_x = .05

    def __init__(self, point_type="primitive"):
        self.point_type = point_type

        super(Point, self).__init__()
        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        if self.point_type != "primitive":
            self.nodePath.setScale(self.scale_x, 1., self.scale_z)

    def makeObject(self):
        if self.point_type == "primitive":
            self.node = custom_geometry.create_GeomNode_Single_Point(
                color_vec4=Vec4(1., 1., 1., 1.))
        else:
            self.node = custom_geometry.createColoredUnitQuadGeomNode(
                color_vec4=Vec4(1., 1., 1., 1.), center_it=True)
            self.nodePath.setTwoSided(True)

        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setLightOff(1)

        if self.point_type == "primitive":
            self.nodePath.setRenderModeThickness(5)


class Line1dObject(LinePrimitive):
    initial_length = 1.

    # thickness is derived from LinePrimitive

    def __init__(self, thickness=2., color=Vec4(1., 1., 1., 1.), **kwargs):
        super(Line1dObject, self).__init__(thickness=thickness, color=color)

        self._rotation_forrowvecs = Mat4()

        self.doInitialSetupTransformation(**kwargs)

    def doInitialSetupTransformation(self, **kwargs):
        # if 'thickness' in kwargs:
        #     self.thickness = kwargs.get('thickness')

        # scaling = math_utils.getScalingMatrix3d_forrowvecs(1., 1., 1.)
        self.length = self.initial_length
        # self.translation_to_xhat_forrowvecs = math_utils.getTranslationMatrix3d_forrowvecs(0.5, 0, 0)

        # self.form_from_primitive_trafo = scaling * self.translation_to_xhat_forrowvecs
        # self.nodePath.setMat(self.form_from_primitive_trafo)

        self.form_from_primitive_trafo = self.nodePath.getMat()
        # self.nodePath.setRenderModeWireframe()

        self.setTipPoint(Vec3(1., 0., 0.))

    def setTipPoint(self, tip_point):
        # --- Rodriguez rotation formula ---
        # apply rodriguez formula to rotate the geometrie's given
        # xhat = [1, 0, 0] vector to the destination vector v

        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
        a = np.array([1., 0., 0.], dtype=np.float)
        self.vec_prime = np.array(
            [tip_point.getX(), tip_point.getY(), tip_point.getZ()], dtype=np.float)
        b = self.vec_prime

        theta = np.arccos(
            np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

        R = None
        epsilon = 0.0000001
        if theta < epsilon:  # edge case: parallel
            # in this case, you can't divide by zero to get the rotation axis x
            R = np.identity(3, dtype=np.float)
        elif np.pi - theta < epsilon:  # edge case: antiparallel
            # find a vector orthogonal to a,
            # for this, e.g. first find the component of least magnitude
            # of a, then calculate the cross product of the
            # corresponding standard
            # unit vector with a, which cannot be zero in magnitude

            i = min(np.where(a == np.min(a))[0])

            # chop up identity matrix to get the standard unit vector
            e_i = np.identity(3)[i]

            x = np.cross(a, e_i) / np.linalg.norm(np.cross(a, e_i))

            A = np.array([
                [0.,    -x[2],  x[1]],
                [x[2],  0.,    -x[0]],
                [-x[1], x[0],   0.]
            ], dtype=np.float)

            R = (np.identity(3, dtype=np.float) + np.sin(theta) * A
             + (1. - np.cos(theta)) * np.matmul(A, A))
        else:
            x = np.cross(a, b) / np.linalg.norm(np.cross(a, b))

            A = np.array([
                [0.,    -x[2],  x[1]],
                [x[2],  0.,    -x[0]],
                [-x[1], x[0],   0.]
            ], dtype=np.float)

            R = (np.identity(3, dtype=np.float) + np.sin(theta) * A
             + (1. - np.cos(theta)) * np.matmul(A, A))

        R_4by4 = np.array(
            [
                [R[0][0], R[0][1], R[0][2], 0.],
                [R[1][0], R[1][1], R[1][2], 0.],
                [R[2][0], R[2][1], R[2][2], 0.],
                [0., 0., 0., 1.]
            ]
        )

        rotation = Mat4(*tuple(np.transpose(R_4by4).flatten()))

        self._rotation_forrowvecs = rotation

        # scaling matrix: scale the vector along xhat when it points in xhat direction
        # (to prevent skewing if the vector's line is a mesh)
        vx = np.linalg.norm(self.vec_prime)  # length
        vy = 1.
        vz = 1.
        scaling = np.array([[vx,  0,  0, 0],
                            [0,  vy,  0, 0],
                            [0,   0, vz, 0],
                            [0,   0,  0, 1]], dtype=np.float)
        scaling_forrowvecs = Mat4(*tuple(np.transpose(scaling).flatten()))

        # apply the net transformation
        # first the scaling, then the rotation
        # remember, the row vector stands on the left in p3d multiplication
        # so the order is reversed
        trafo = scaling_forrowvecs * self._rotation_forrowvecs

        # if tip_point != Vec3(1., 0., 0.):
        #     import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

        self.nodePath.setMat(self.form_from_primitive_trafo * trafo)

    def getRotation(self):
        """
        forrowvecs
        """

        assert self._rotation_forrowvecs
        return self._rotation_forrowvecs


class LineDashed1dObject(LineDashedPrimitive):
    initial_length = 1.

    # thickness is derived from LinePrimitive

    def __init__(self, thickness=2., color=Vec4(1., 1., 1., 1.), howmany_periods=5., **kwargs):
        super(LineDashed1dObject, self).__init__(
            thickness=thickness, color=color, howmany_periods=howmany_periods)

        self._rotation_forrowvecs = Mat4()

        self.doInitialSetupTransformation(**kwargs)

    def doInitialSetupTransformation(self, **kwargs):
        # if 'thickness' in kwargs:
        #     self.thickness = kwargs.get('thickness')

        # scaling = math_utils.getScalingMatrix3d_forrowvecs(1., 1., 1.)
        self.length = self.initial_length
        # self.translation_to_xhat_forrowvecs = math_utils.getTranslationMatrix3d_forrowvecs(0.5, 0, 0)

        # self.form_from_primitive_trafo = scaling * self.translation_to_xhat_forrowvecs
        # self.nodePath.setMat(self.form_from_primitive_trafo)

        self.form_from_primitive_trafo = self.nodePath.getMat()
        # self.nodePath.setRenderModeWireframe()

        self.setTipPoint(Vec3(1., 0., 0.))

    def setTipPoint(self, tip_point):
        # --- Rodriguez rotation formula ---
        # apply rodriguez formula to rotate the geometrie's given
        # xhat = [1, 0, 0] vector to the destination vector v

        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
        a = np.array([1., 0., 0.], dtype=np.float)
        self.vec_prime = np.array(
            [tip_point.getX(), tip_point.getY(), tip_point.getZ()], dtype=np.float)
        b = self.vec_prime

        theta = np.arccos(
            np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

        R = None
        epsilon = 0.0000001
        if theta < epsilon:  # edge case: parallel
            # in this case, you can't divide by zero to get the rotation axis x
            R = np.identity(3, dtype=np.float)
        elif np.pi - theta < epsilon:  # edge case: antiparallel
            # find a vector orthogonal to a,
            # for this, e.g. first find the component of least magnitude
            # of a, then calculate the cross product of the
            # corresponding standard
            # unit vector with a, which cannot be zero in magnitude

            i = min(np.where(a == np.min(a))[0])

            # chop up identity matrix to get the standard unit vector
            e_i = np.identity(3)[i]

            x = np.cross(a, e_i) / np.linalg.norm(np.cross(a, e_i))

            A = np.array([
                [0.,    -x[2],  x[1]],
                [x[2],  0.,    -x[0]],
                [-x[1], x[0],   0.]
            ], dtype=np.float)

            R = (np.identity(3, dtype=np.float) + np.sin(theta) * A
             + (1. - np.cos(theta)) * np.matmul(A, A))
        else:
            x = np.cross(a, b) / np.linalg.norm(np.cross(a, b))

            A = np.array([
                [0.,    -x[2],  x[1]],
                [x[2],  0.,    -x[0]],
                [-x[1], x[0],   0.]
            ], dtype=np.float)

            R = (np.identity(3, dtype=np.float) + np.sin(theta) * A
             + (1. - np.cos(theta)) * np.matmul(A, A))

        R_4by4 = np.array(
            [
                [R[0][0], R[0][1], R[0][2], 0.],
                [R[1][0], R[1][1], R[1][2], 0.],
                [R[2][0], R[2][1], R[2][2], 0.],
                [0., 0., 0., 1.]
            ]
        )

        rotation = Mat4(*tuple(np.transpose(R_4by4).flatten()))

        self._rotation_forrowvecs = rotation

        # scaling matrix: scale the vector along xhat when it points in xhat direction
        # (to prevent skewing if the vector's line is a mesh)
        vx = np.linalg.norm(self.vec_prime)  # length
        vy = 1.
        vz = 1.
        scaling = np.array([[vx,  0,  0, 0],
                            [0,  vy,  0, 0],
                            [0,   0, vz, 0],
                            [0,   0,  0, 1]], dtype=np.float)
        scaling_forrowvecs = Mat4(*tuple(np.transpose(scaling).flatten()))

        # apply the net transformation
        # first the scaling, then the rotation
        # remember, the row vector stands on the left in p3d multiplication
        # so the order is reversed
        trafo = scaling_forrowvecs * self._rotation_forrowvecs

        # if tip_point != Vec3(1., 0., 0.):
        #     import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

        self.nodePath.setMat(self.form_from_primitive_trafo * trafo)

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
        self.nodePath.setRenderModeWireframe()
        self.setTipPoint(Vec3(1., 0., 0.))

    def setTipPoint(self, tip_point):
        self.vec_prime = np.array(
            [tip_point.getX(), tip_point.getY(), tip_point.getZ()])

        # rotation matrix for xhat
        xhat = np.array([1, 0, 0])
        normal = np.array([0, 1, 0])  # panda3d out of screen: yhat
        # find angle \theta (\in [-pi, pi]) between \hat{x} and \hat{x}'
        # using the arctan2 of a determinant and a dot product
        det = np.dot(normal, np.cross(xhat, self.vec_prime))
        theta = np.arctan2(det, np.dot(xhat, self.vec_prime))
        rotation = np.array([[np.cos(theta),  0, np.sin(theta), 0],
                             [0,               1,             0, 0],
                             [-np.sin(theta),  0, np.cos(theta), 0],
                             [0,               0,             0, 1]])
        self._rotation_forrowvecs = Mat4(
            *tuple(np.transpose(rotation).flatten()))

        # scaling matrix for xhat
        vx = np.linalg.norm(self.vec_prime)  # length
        vy = 1.
        vz = 1.
        scaling = np.array([[vx,  0,  0, 0],
                            [0,  vy,  0, 0],
                            [0,   0, vz, 0],
                            [0,   0,  0, 1]])
        scaling_forrowvecs = Mat4(*tuple(np.transpose(scaling).flatten()))

        # apply the net transformation
        # first the scaling, then the rotation
        # remember, the row vector stands on the left in p3d multiplication
        # so the order is reversed
        trafo = scaling_forrowvecs * self._rotation_forrowvecs
        self.nodePath.setMat(self.form_from_primitive_trafo * trafo)

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


class ArrowHeadConeShaded(Box2dCentered):
    scale = .1

    def __init__(self, color=Vec4(0., 0., 0., 0.)):
        self.color=color
        super(ArrowHeadConeShaded, self).__init__()
        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        # self.nodePath.setScale(self.scale, self.scale, self.scale)

        scaling_forrowvecs = math_utils.getScalingMatrix3d_forrowvecs(
            ArrowHead.scale,
            ArrowHead.scale,
            ArrowHead.scale)

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


from conventions.conventions import compute2dPosition
from panda3d.core import TextNode

class Pinned2dLabel:
    # from direct.gui.OnscreenText import OnscreenText
    #     textObject = OnscreenText(text='my text string', pos=(-0.5, 0.02), scale=0.07)

    def __init__(self, refpoint3d=Point3(1., 1., 1.), text="pinned?", xshift=0., yshift=0.):
        self.refpoint3d = refpoint3d
        self.text = text
        self.nodeisattachedtoaspect2d = False

        self.xshift = xshift
        self.yshift = yshift

        self.update()

    def update(self):
        pos_rel_to_cam = base.cam.get_relative_point(base.render, self.refpoint3d)
        p2d = Point2()

        if not self.nodeisattachedtoaspect2d:
            self.textNode = TextNode('myPinned2dLabel')
            self.textNode.setText(self.text)

            # load a font
            cmr12 = loader.loadFont('cmr12.egg')
            self.textNode.setFont(cmr12)

            # set a shadow
            self.textNode.setShadow(0.05, 0.05)
            self.textNode.setShadowColor(0, 0, 0, 1)

            self.textNodePath = aspect2d.attachNewNode(self.textNode)
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
        self.textNodePath.setPos((p2d[0] + self.xshift) * win_aspect_ratio, 0, p2d[1]+ self.yshift)
