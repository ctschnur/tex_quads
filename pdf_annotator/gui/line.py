import numpy as np

from engine.tq_graphics_basics import TQGraphicsNodePath

from simple_objects.primitives import IndicatorPrimitive

from simple_objects.simple_objects import LinePrimitive

# class LinePrimitive(IndicatorPrimitive):
#     """ """
#     def __init__(self, thickness=1., **kwargs):
#         """ """
#         IndicatorPrimitive.__init__(self, **kwargs)

#         # these are graphical values
#         # for more complex, e.g. recessed lines for vectors, you need another set
#         # of variables to store the logical end points
#         self.tip_point = None
#         self.tail_point = None



class Line1dPrimitive2d(LinePrimitive):
    """ """
    def __init__(self, thickness=1., **kwargs):
        """ """
        LinePrimitive.__init__(self, **kwargs)

        self.thickness = thickness
        self.makeObject(thickness, **kwargs)

        self.setTailPoint(self.tail_point)
        self.setTipPoint(self.tip_point)

    def makeObject(self, thickness, **kwargs):
        self.set_node_p3d(# custom_geometry.createColoredUnitLineGeomNode(
        #     thickness=thickness,
        #     color_vec4=kwargs.get("color")
        # )

        custom_geometry.createColoredUnitQuadGeomNode(color_vec4=Vec4(0., 0., 1., 1.), center_it=False)

        )

        self.set_p3d_nodepath(
            self.getParent_p3d().attachNewNode(self.get_node_p3d()))

        self.setLightOff(1)

    # TODO: modify these functions to enable scaling and translation transformations (quasi-2d line) on camera move

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


class Line1dSolid(Line1dPrimitive2d):
    """ """

    def __init__(self, thickness=2., **kwargs):
        self._rotation_forrowvecs = Mat4()

        # this also sets the position
        Line1dPrimitive2d.__init__(
            self, thickness=thickness, **kwargs)

        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        self.form_from_primitive_trafo = self.getMat()
