from interactive_tools.dragging_and_dropping import PickableObjectManager, PickablePoint, Dragger, PickablePoint, CollisionPicker, DragAndDropObjectsManager

from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle

from local_utils import math_utils

from simple_objects.simple_objects import Line1dSolid, PointPrimitive
from composed_objects.composed_objects import Vector

# from interactive_tools.dragging_and_dropping import PickableObjectManager

from simple_objects.primitives import ParametricLinePrimitive
from panda3d.core import Vec3, Mat4, Vec4

import numpy as np
import scipy.special

from direct.showbase.ShowBase import ShowBase, DirectObject


def sayhi():
    print("heylo ------- ######")


class BezierCurve:
    # plot a bezier curve in the yz plane

    def __init__(self, P_arr):

        self.bez_points=P_arr

        self.beziercurve=ParametricLinePrimitive(
            lambda t:
            np.array([
                BezierCurve.calcBezierCurve(t, self.bez_points)[0],
                BezierCurve.calcBezierCurve(t, self.bez_points)[1],
                BezierCurve.calcBezierCurve(t, self.bez_points)[2]
            ]),
            param_interv=np.array([0, 1]),
            thickness=1.,
            color=Vec4(1., 1., 0., 1.))

    @staticmethod
    def calcBezierCurve(t, P_arr):
        _sum = 0
        n = len(P_arr) - 1

        assert len(P_arr) >= 2  # at least a linear bezier curve
        assert t >= 0. and t <= 1.

        for i, P_i in enumerate(P_arr):
            _sum += (scipy.special.comb(n, i)
                     * (1. - t)**(n - np.float(i))
                     * t**np.float(i)
                     * P_i)
        return _sum



class DraggableBezierCurve(BezierCurve):
    def __init__(self,
                 camera_gear,
                 P_arr=np.array([[0., 0., 0.],
                                 [0., 1., 1.],
                                 [0., 0, 1.],
                                 [1., 1., 1.]])
    ):

        BezierCurve.__init__(self, P_arr)

        self.camera_gear = camera_gear
        # self.camera_gear.set_view_to_yz_plane()

        # --- plot draggable bezier curve together with points
        # for dragging the points and updating the bezier curve,
        # the points have to stay instantiated (objects that are dragged), while the bezier curve
        # can be regenerated from the new point positions at every drag event

        # -- add picking utilities
        self.pickableObjectManager = PickableObjectManager()
        self.dragAndDropObjectsManager = DragAndDropObjectsManager()
        self.collisionPicker = CollisionPicker(self.camera_gear, render, base.mouseWatcherNode, base, self.dragAndDropObjectsManager)

        # -- add a mouse task to check for picking
        self.p3d_direct_object = DirectObject.DirectObject()
        self.p3d_direct_object.accept('mouse1', self.collisionPicker.onMouseTask)

        # -- add the PickablePoints
        self.control_points_pickable_points = []

        # ---- go through the coordinates and assign PickablePoints
        for p in self.bez_points:
            pt = PickablePoint(self.pickableObjectManager,
                               pos=Vec3(*p))

            pt_dragger = Dragger(pt, self.camera_gear)
            pt_dragger.add_on_state_change_function(sayhi)
            pt_dragger.add_on_state_change_function(self.updateCurveAfterPointCoordsChanged)

            self.dragAndDropObjectsManager.add_dragger(pt_dragger)

            pt.nodePath.setHpr(90, 0, 0)  # 90 degrees yaw
            pt.nodePath.showBounds()

            self.control_points_pickable_points.append(pt)


        # -- add a line betwen each set of 2 pickablepoints (like in inkscape)
        # ---- with only 4 pickablepoints, assign a line to the fist 2 and the last 2
        self.l1 = Line1dSolid(thickness=1., color=Vec4(1,0,1,1))
        self.l2 = Line1dSolid(thickness=1., color=Vec4(1,0,1,1))
        # l1.setPos(Vec3(0., 0., 0.))
        # l1.setTipPoint(Vec3(0., 0., 0.))

        self.updateCurveAfterPointCoordsChanged()


        # # -- add the update dragging tasks for each of the PickablePoints' draggers
        # for cppp in self.control_points_pickable_points:
        #     dragger = self.dragAndDropObjectsManager.get_dragger_from_nodePath(cppp.nodePath):
        #     dragger.add_on_state_change_function(self.updateCurveAfterPointCoordsChanged)

        # TODO: improve the design by letting DraggableBezierCurve inherit from DragAndDropObjectsManager,
        # it can be easily thought of as holding the dragger objects themselves

    def updateHandleLinesAfterPointCoordsChanged(self):
        """ update the handle lines to have tip/tail points at the positions of
        the new coordinates of the pickable points """

        self.l1.setPos(self.bez_points[0])
        self.l1.setTipPoint(self.bez_points[1])

        self.l2.setPos(self.bez_points[2])
        self.l2.setTipPoint(self.bez_points[3])


    def updateCurveAfterPointCoordsChanged(self):
        """ if a PickablePoint has been dragged, you need to update the curve
        i.e. here: fully recreate it from the coordinates of the PickablePoints """

        # delete the old curve
        self.beziercurve.nodePath.removeNode()

        # extract the new coordinates from the pickable points
        new_point_coords = []
        for cppp in self.control_points_pickable_points:
            new_point_coords.append(cppp.getPos())

        self.bez_points = new_point_coords

        self.updateHandleLinesAfterPointCoordsChanged()

        # regenerate the curve, python should drop the reference-less previous ParametricLinePrimitive soon after
        self.beziercurve=ParametricLinePrimitive(
            lambda t:
            np.array([
                BezierCurve.calcBezierCurve(t, self.bez_points)[0],
                BezierCurve.calcBezierCurve(t, self.bez_points)[1],
                BezierCurve.calcBezierCurve(t, self.bez_points)[2]
            ]),
            param_interv=np.array([0, 1]),
            thickness=1.,
            color=Vec4(1., 1., 0., 1.))


class SelectableBezierCurve(DraggableBezierCurve):
    def __init__(self, *args, **kwargs):

        self.point_primitives = []
        self.oriented_circles = []

        self.tangent_vectors = []
        self.normal_vectors = []
        self.binormal_vectors = []

        DraggableBezierCurve.__init__(self, *args, **kwargs)

        # generate a tube mesh around the curve
        self.updateTubeMesh()


    def updateTubeMesh(self):
        # -- re-calculate the points and path lengths
        points, path_lengths = math_utils.getPointsAndPathLengthsAlongPolygonalChain(
            func=(
                lambda t: np.array([
                    BezierCurve.calcBezierCurve(t, self.bez_points)[0],
                    BezierCurve.calcBezierCurve(t, self.bez_points)[1],
                    BezierCurve.calcBezierCurve(t, self.bez_points)[2]])
                # lambda t: np.array([0, t, 2.7**t])
            ),
            param_interv=np.array([0., 1.]),
            ed_subpath_length=0.2)


        # ---- clear out the ancillary objects on update
        for pp in self.point_primitives:
            pp.nodePath.removeNode()

        for oc in self.oriented_circles:
            oc.nodePath.removeNode()

        for tv in self.tangent_vectors:
            tv.nodePath.removeNode()

        for nv in self.normal_vectors:
            nv.nodePath.removeNode()

        for bv in self.binormal_vectors:
            bv.nodePath.removeNode()


        # ---- then re-generate them anew
        self.point_primitives = []
        self.oriented_circles = []

        self.tangent_vectors = []
        self.tangent_vectors_logical = []
        self.normal_vectors = []
        self.binormal_vectors = []

        view_scale = 0.2

        for i, p in enumerate(points):
            self.point_primitives.append(PointPrimitive(pos=Vec3(*tuple(p))))
            t_vec = None
            if i > 0:
                d_vec_r_of_s = points[i] - points[i-1]
                # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
                d_s = np.linalg.norm(path_lengths[i] - path_lengths[i-1])
                t_vec = math_utils.normalize(d_vec_r_of_s/d_s)
                self.oriented_circles.append(OrientedCircle(
                    origin_point=points[i],
                    normal_vector_vec3=Vec3(*tuple(t_vec))))

                tv_line = Line1dSolid(color=Vec4(1., 0., 0., 1.))
                tv_line.setTipPoint(points[i] + t_vec*view_scale)
                tv_line.setTailPoint(points[i])

                self.tangent_vectors.append(tv_line)
                self.tangent_vectors_logical.append(t_vec)

            if i > 1:  # after a change in the tangent vector, the normal vector is well-defined
                n_vec = math_utils.normalize(
                    self.tangent_vectors_logical[i-1] - self.tangent_vectors_logical[i-2])

                nv_line = Line1dSolid(color=Vec4(0., 1., 0., 1.))
                nv_line.setTipPoint(points[i] + n_vec*view_scale)
                nv_line.setTailPoint(points[i])

                self.normal_vectors.append(nv_line)

                # after tangent vector and normal vector are well-defined, the binormal is also
                b_vec = math_utils.normalize(
                    np.cross(n_vec, t_vec))

                bv_line = Line1dSolid(color=Vec4(0., 0., 1., 1.))
                bv_line.setTipPoint(points[i] + b_vec*view_scale)
                bv_line.setTailPoint(points[i])

                self.binormal_vectors.append(bv_line)


    def updateCurveAfterPointCoordsChanged(self):
        """ if a PickablePoint has been dragged, you need to update the curve
        i.e. here: fully recreate it from the coordinates of the PickablePoints """

        # delete the old curve
        self.beziercurve.nodePath.removeNode()

        # extract the new coordinates from the pickable points
        new_point_coords = []
        for cppp in self.control_points_pickable_points:
            new_point_coords.append(cppp.getPos())

        self.bez_points = new_point_coords

        self.updateHandleLinesAfterPointCoordsChanged()

        self.updateTubeMesh()

        # regenerate the curve, python should drop the reference-less previous ParametricLinePrimitive soon after
        self.beziercurve=ParametricLinePrimitive(
            lambda t:
            np.array([
                BezierCurve.calcBezierCurve(t, self.bez_points)[0],
                BezierCurve.calcBezierCurve(t, self.bez_points)[1],
                BezierCurve.calcBezierCurve(t, self.bez_points)[2]
            ]),
            param_interv=np.array([0, 1]),
            thickness=1.,
            color=Vec4(1., 1., 0., 1.))
