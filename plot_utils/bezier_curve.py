from interactive_tools.dragging_and_dropping import PickableObjectManager, PickablePoint, Dragger, PickablePoint, CollisionPicker, DragAndDropObjectsManager

from simple_objects.simple_objects import Line1dObject

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
        self.l1 = Line1dObject(thickness=1., color=Vec4(1,0,1,1))
        self.l2 = Line1dObject(thickness=1., color=Vec4(1,0,1,1))
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
