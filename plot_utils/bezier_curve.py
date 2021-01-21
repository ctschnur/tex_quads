from interactive_tools.picking import CollisionPicker, PickableObjectManager
from interactive_tools.dragging_and_dropping_objects import DragAndDropObjectsManager
from interactive_tools.pickables import PickablePoint, PickablePointDragger

from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle

from local_utils import math_utils

from simple_objects.simple_objects import Line1dSolid, PointPrimitive
from composed_objects.composed_objects import Vector

from simple_objects.custom_geometry import create_Triangle_Mesh_From_Vertices_and_Indices, createCircle, createColoredUnitQuadGeomNode

# from interactive_tools.dragging_and_dropping_objects import PickableObjectManager

from simple_objects.primitives import ParametricLinePrimitive
from panda3d.core import Vec3, Mat4, Vec4

import numpy as np
import scipy.special

import glm

from direct.showbase.ShowBase import ShowBase, DirectObject

from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight

from simple_objects.primitives import IndicatorPrimitive

import engine

def sayhi():
    print("heylo ------- ######")


class BezierCurve(IndicatorPrimitive):
    """ plot a bezier curve """
    def __init__(self, P_arr, **kwargs):
        IndicatorPrimitive.__init__(**kwargs)

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

        BezierCurve.__init__(self, P_arr, **kwargs)

        self.camera_gear = camera_gear
        # self.camera_gear.set_view_to_yz_plane()

        # --- plot draggable bezier curve together with points
        # for dragging the points and updating the bezier curve,
        # the points have to stay instantiated (objects that are dragged), while the bezier curve
        # can be regenerated from the new point positions at every drag event

        # -- add picking utilities
        self.pickableObjectManager = PickableObjectManager()
        self.dragAndDropObjectsManager = DragAndDropObjectsManager()
        self.collisionPicker = CollisionPicker(self.camera_gear, engine.tq_graphics_basics.tq_render, base.mouseWatcherNode, self.dragAndDropObjectsManager)

        # -- add a mouse task to check for picking
        self.p3d_direct_object = DirectObject.DirectObject()
        self.p3d_direct_object.accept('mouse1', self.collisionPicker.onMouseTask)

        # -- add the PickablePoints
        self.control_points_pickable_points = []

        # ---- go through the coordinates and assign PickablePoints
        for p in self.bez_points:
            pt = PickablePoint(self.pickableObjectManager,
                               pos=Vec3(*p))

            pt_dragger = PickablePointDragger(pt, self.camera_gear)
            pt_dragger.add_on_state_change_function(sayhi)
            pt_dragger.add_on_state_change_function(self.updateCurveAfterPointCoordsChanged)

            self.dragAndDropObjectsManager.add_dragger(pt_dragger)

            pt.setHpr(90, 0, 0)  # 90 degrees yaw
            pt.showBounds()

            self.control_points_pickable_points.append(pt)


        # -- add a line betwen each set of 2 pickablepoints (like in inkscape)
        # ---- with only 4 pickablepoints, assign a line to the fist 2 and the last 2
        self.l1 = Line1dSolid(thickness=1., color=Vec4(1,0,1,1))
        self.l2 = Line1dSolid(thickness=1., color=Vec4(1,0,1,1))

        self.updateCurveAfterPointCoordsChanged()


        # # -- add the update dragging tasks for each of the PickablePoints' draggers
        # for cppp in self.control_points_pickable_points:
        #     dragger = self.dragAndDropObjectsManager.get_dragger_from_tq_nodepath(cppp.nodepath):
        #     dragger.add_on_state_change_function(self.updateCurveAfterPointCoordsChanged)

        # TODO: improve the design by letting DraggableBezierCurve inherit from DragAndDropObjectsManager,
        # it can be easily thought of as holding the dragger objects themselves

    def updateHandleLinesAfterPointCoordsChanged(self):
        """ update the handle lines to have tip/tail points at the positions of
        the new coordinates of the pickable points """

        self.l1.setTailPoint(self.bez_points[0])
        self.l1.setTipPoint(self.bez_points[1])

        self.l2.setTailPoint(self.bez_points[2])
        self.l2.setTipPoint(self.bez_points[3])


    def updateCurveAfterPointCoordsChanged(self):
        """ if a PickablePoint has been dragged, you need to update the curve
        i.e. here: fully recreate it from the coordinates of the PickablePoints """

        # delete the old curve
        self.beziercurve.removeNode()

        # extract the new coordinates from the pickable points
        new_point_coords = []
        for cppp in self.control_points_pickable_points:
            new_point_coords.append(cppp.getPos())

        self.bez_points = new_point_coords

        self.updateHandleLinesAfterPointCoordsChanged()

        # regenerate the curve, python should drop the reference-less previous
        # ParametricLinePrimitive soon after
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

        self.mesh_points = []

        self.tube_mesh_nodepath = None

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
            pp.removeNode()

        for oc in self.oriented_circles:
            oc.removeNode()

        for tv in self.tangent_vectors:
            tv.removeNode()

        for nv in self.normal_vectors:
            nv.removeNode()

        for bv in self.binormal_vectors:
            bv.removeNode()

        for mp in self.mesh_points:
            mp.removeNode()


        # ---- then re-generate them anew
        self.point_primitives = []
        self.oriented_circles = []

        self.tangent_vectors = []
        self.tangent_vectors_logical = []
        self.normal_vectors = []
        self.binormal_vectors = []

        self.mesh_points = []
        self.mesh_points_logical = []  # stores the 3d vertex positions of the desired triangle mesh

        # ---- for the tube mesh

        # circles_vertices = []  # stores the 3d vertex positions of the desired triangle mesh
        triangles = []  # stores the indices to the vertices in circles_vertices
        radius = 0.1
        num_of_verts = 10
        scale = 0.2

        for i, p in enumerate(points):
            self.point_primitives.append(PointPrimitive(pos=Vec3(*tuple(p))))
            t_vec = None
            if i > 0:
                d_vec_r_of_s = points[i] - points[i-1]
                d_s = np.linalg.norm(path_lengths[i] - path_lengths[i-1])
                t_vec = math_utils.normalize(d_vec_r_of_s/d_s)

                tv_line = Line1dSolid(color=Vec4(1., 0., 0., 1.))
                tv_line.setTipPoint(points[i] + t_vec*scale)
                tv_line.setTailPoint(points[i])

                tv_line.hide()

                self.tangent_vectors.append(tv_line)
                self.tangent_vectors_logical.append(t_vec)

                # --- draw oriented circle
                oc = OrientedCircle(
                    origin_point=points[i],
                    normal_vector=Vec3(*tuple(t_vec)),
                    radius=radius)

                oc.hide()

                self.oriented_circles.append(oc)

                # --- generate vertex data for the current circle
                vd_cc = math_utils.get_circle_vertices(num_of_verts=num_of_verts, radius=radius)
                vd_cc_transformed = []
                for v in vd_cc:
                    # transform the vertices of the circles appropriately (you want one mesh)
                    trafo = math_utils.p3d_mat4_to_math_convention(
                        math_utils.getTranslationMatrix3d_forrowvecs(v[0], v[1], v[2]) *
                        OrientedCircle.getSetupTransformation(t_vec, points[i], scale=0.5))

                    # transform the coordinates
                    v = glm.vec4(*tuple(v), 1.) * glm.mat4(*tuple(np.ravel(trafo)))

                    vd_cc_transformed.append([v[0], v[1], v[2]])

                    point = Point3d(pos=np.array([v[0], v[1], v[2]]), scale=0.02)
                    point.hide()

                    self.mesh_points.append(point)

                self.mesh_points_logical.append(vd_cc_transformed)




            if i > 1:  # after a change in the tangent vector, the normal vector is well-defined
                n_vec = math_utils.normalize(
                    self.tangent_vectors_logical[i-1] - self.tangent_vectors_logical[i-2])

                nv_line = Line1dSolid(color=Vec4(0., 1., 0., 1.))
                nv_line.setTipPoint(points[i] + n_vec*scale)
                nv_line.setTailPoint(points[i])

                self.normal_vectors.append(nv_line)

                # after tangent vector and normal vector are well-defined, the binormal is also
                b_vec = math_utils.normalize(
                    np.cross(n_vec, t_vec))

                bv_line = Line1dSolid(color=Vec4(0., 0., 1., 1.))
                bv_line.setTipPoint(points[i] + b_vec*scale)
                bv_line.setTailPoint(points[i])

                self.binormal_vectors.append(bv_line)

                # you can generate vertex and index data for the current circle and a last circle

                # ---- access vertex data of the previous circle

                vd_pc = self.mesh_points_logical[i-2]

                vd_pc_idx_offset = (i-2) * num_of_verts
                vd_cc_idx_offset = (i-1) * num_of_verts

                # now build the triangles (indices) to go in between the last circle
                # and the current circle
                j = 0  # vertex index
                cur_triangles_arr = []  # stores 3-arrays of indices
                while j < len(vd_pc) - 1:
                    # sense of contour buildup: clockwise

                    # 1st triangle
                    cur_triangles_arr.append(
                        [vd_pc_idx_offset+j,
                         vd_cc_idx_offset+j,
                         vd_pc_idx_offset+j+1])

                    # opposite side triangle
                    cur_triangles_arr.append(
                        [vd_pc_idx_offset+j+1,
                         vd_cc_idx_offset+j,
                         vd_cc_idx_offset+j+1])

                    j += 1

                triangles.append(cur_triangles_arr)

        # -- plot the mesh whose points and Tristrips were created

        vertices_flat = np.ravel(self.mesh_points_logical)
        indices_flat = np.ravel(triangles)

        gn = create_Triangle_Mesh_From_Vertices_and_Indices(vertices_flat, indices_flat, color_vec4=Vec4(1., 0., 0., 1.))
        # gn = createCircle(num_of_verts=100)
        # gn = createColoredUnitQuadGeomNode(color_vec4=Vec4(0., 0., 1., 1.),
        #                                    center_it=False)

        if self.tube_mesh_nodepath:
            self.tube_mesh_nodepath.removeNode()

        self.tube_mesh_nodepath = self.get_parent_node_for_nodepath_creation().attachNewNode(gn)
        self.tube_mesh_nodepath.setRenderModeWireframe()
        self.tube_mesh_nodepath.setTwoSided(True)
        self.tube_mesh_nodepath.setLightOff(1)

    def updateCurveAfterPointCoordsChanged(self):
        """ if a PickablePoint has been dragged, you need to update the curve
        i.e. here: fully recreate it from the coordinates of the PickablePoints """

        # delete the old curve
        self.beziercurve.removeNode()

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
