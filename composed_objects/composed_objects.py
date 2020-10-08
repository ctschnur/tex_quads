from conventions import conventions
from simple_objects import custom_geometry
from local_utils import texture_utils, math_utils
from latex_objects.latex_expression_manager import LatexImageManager, LatexImage
from engine.graphics_object import GraphicsObject
from simple_objects.simple_objects import Line2dObject, ArrowHead, Point, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedCircle

from simple_objects.simple_objects import Point3d

from p3d_tools import p3d_tools

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Vec3,
    Point3,
    Vec4,
    TransparencyAttrib,
    AntialiasAttrib,
    NodePath,
    Mat4,
    Mat3,
    LineSegs)
from direct.interval.IntervalGlobal import Wait, Sequence
from direct.interval.LerpInterval import LerpFunc

import hashlib
import numpy as np

class GroupNode(GraphicsObject):
    """ Documentation for GroupNode
    """

    def __init__(self):
        super(GroupNode, self).__init__()
        self.nodePath = NodePath("empty")
        self.nodePath.reparentTo(render)

    def addChildNodePaths(self, NodePaths):
        for np in NodePaths:
            np.reparentTo(self.nodePath)

    def removeChildNodePaths(self, NodePaths):
        for np in NodePaths:
            np.removeNode()

    def hide(self):
        """ hide every child node in the group node """
        children = self.nodePath.get_children()

        for child in children:
            child.hide()

    def show(self):
        """ hide every child node in the group node """
        children = self.nodePath.get_children()
        for child in children:
            child.show()

    def get_children(self):
        return self.nodePath.get_children()


class ParallelLines:
    """ Draw Parallel Lines

    """

    def __init__(self):
        self.spacing = .25
        self.number_of_lines = 15

        # transform the lines
        # - stretch the unit length lines to the specified size
        # - position them in order, evenly spaced

        self.lines = [Line2dObject() for i in range(self.number_of_lines)]
        for idx, line1 in enumerate(self.lines):
            line1.nodePath.setScale(line1.nodePath, 1., 1., 1.)
            line1.nodePath.setPos(0., 0, idx * self.spacing)


class Point3dCursor():
    """ a white Point3d with a
    black and a white circle aroud it for accentuation """

    def __init__(self, origin_point, scale=0.05):
        """ """
        self.origin_point = origin_point

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

        self.point_center = Point3d(
            scale=self.scale_total * self.rel_scale_point_center)
        self.circle_outer_first = OrientedCircle(
            normal_vector=Vec3(0., 0., 1.),
            scale=self.scale_total * self.rel_scale_circle_outer_first,
            num_of_verts=self.num_of_verts,
            thickness=3.)
        self.circle_outer_second = OrientedCircle(
            normal_vector=Vec3(0., 0., 1.),
            scale=self.scale_total * self.rel_scale_circle_outer_second,
            num_of_verts=self.num_of_verts,
            thickness=3.)
        # self.circle_outer_third = OrientedCircle(
        #     normal_vector=Vec3(0., 0., 1.),
        #     scale=self.scale_total * self.rel_scale_circle_outer_third,
        #     num_of_verts=self.num_of_verts,
        #     thickness=3.)

        self._adjust()

    def _adjust(self):
        # TODO: reorient towards the camera
        # TODO: keep it the same size w.r.t. the camera (on zooming)
        self.point_center.setPos(self.origin_point)
        self.point_center.setColor(self.color_point_center)

        self.circle_outer_first.setPos(self.origin_point)
        self.circle_outer_first.setColor(self.color_circle_outer_first)

        self.circle_outer_second.setPos(self.origin_point)
        self.circle_outer_second.setColor(self.color_circle_outer_second)

        # self.circle_outer_third.setPos(self.origin_point)
        # # self.circle_outer_third.setColor(self.color_circle_outer_third)

    def setPos(self, position):
        self.origin_point = position
        self._adjust()

    def getPos(self):
        return self.origin_point

    def setColor(self, primary_color, color_point_center=False):
        if color_point_center == True:
            self.color_point_center = primary_color

        self.color_circle_outer_second = primary_color
        self._adjust()

    def setColor_point_center(self, color):
        self.color_point_center = color
        self._adjust()

    def hide(self):
        self.point_center.nodePath.hide()
        self.circle_outer_first.nodePath.hide()
        self.circle_outer_second.nodePath.hide()

    def show(self):
        self.point_center.nodePath.show()
        self.circle_outer_first.nodePath.show()
        self.circle_outer_second.nodePath.show()

    def remove(self):
        self.point_center.nodePath.removeNode()
        self.circle_outer_first.nodePath.removeNode()
        self.circle_outer_second.nodePath.removeNode()



class Vector:
    """Documentation for Vector
       combines an arrowhead and a line1 and applys transformations to them so that it
       it looks like a properly drawn vector
    """

    def __init__(self, tail_point_logical=None, tip_point_logical=None,
                 arrowhead_scale=1./15.,
                 **kwargs):

        if 'linetype' in kwargs:
            self.linetype = kwargs.get('linetype')
        else:
            self.linetype = "1d"

        if 'color' in kwargs:
            self.color = kwargs.get('color')
        else:
            self.color = Vec4(1., 0., 0., 1.)

        if self.linetype == "1d":
            if 'thickness1dline' in kwargs:
                self.thickness1dline = kwargs.get('thickness1dline')
            else:
                self.thickness1dline = 2.

            if 'linestyle' in kwargs:
                self.linestyle = kwargs.get('linestyle')
            else:
                self.linestyle = "-"

            if self.linestyle == "--":
                howmany_periods = 5.
                if 'howmany_periods' in kwargs:
                    howmany_periods = kwargs.get('howmany_periods')

                self.line1 = Line1dDashed(
                    thickness=self.thickness1dline,
                    color=self.color,
                    howmany_periods=howmany_periods)
            else:
                self.line1 = Line1dSolid(
                    thickness=self.thickness1dline, color=self.color)
        elif self.linetype == "2d":
            self.line1 = Line2dObject()
        else:
            print("Error: linetype " + self.linetype + " is invalid")


        if 'arrowheadstyle' in kwargs:
            self.arrowheadstyle = kwargs.get('arrowheadstyle')
            if self.arrowheadstyle == "ArrowHeadCone":
                self.arrowhead = ArrowHeadCone()
            elif self.arrowheadstyle == "ArrowHeadConeShaded":
                self.arrowhead = ArrowHeadConeShaded(color=self.color)
            elif self.arrowheadstyle == "ArrowHead":
                self.arrowhead = ArrowHead()
        else:
            self.arrowhead = ArrowHeadConeShaded(color=self.color, scale=arrowhead_scale)

        self.groupNode = GroupNode()
        self.groupNode.addChildNodePaths(
            [self.line1.nodePath, self.arrowhead.nodePath])

        self.tip_point_logical = tip_point_logical
        self.tail_point_logical = tail_point_logical

        self.setTipPoint(self.tip_point_logical)
        self.setTailPoint(self.tail_point_logical)

        self.setColor(self.color)

    def setColor(self, color):
        """ set this color to all panda nodes """
        children = self.groupNode.get_children()
        for child in children:
            child.setColor(*color)

    def getTipPoint(self):
        return self.tip_point_logical

    def getTailPoint(self):
        return self.tail_point_logical

    def setTipPoint(self, point, param=False, adjust=True):
        """ the group node might have an additional non-zero position:
            -> setPos of the groupnode determines the origin of the primed coorinate system, i.e. the tail of the vector, which is at it's origin
            -> the tip point is either specified in the primed coordinate system (primed=True). This already works and can be used to plot vector fields
            -> if the vector tip point however is meant to be a coordinate in the unprimed system, then:
               - the specified tip point has to be transformed by (groupnode.getMat)^-1 (on updating the vector, -> on the cpu) to undo the effect of the groupnode transformation,
                 and then the transformed tip point is used (this causes self.tip_point_logical to be different than the relative position of the tip point wrt the primed system)
               - as the arrowhead's orientation is wrt the primed system, it should still be ok.
        """

        self.tip_point_logical = point

        if (self.tip_point_logical is None or self.tail_point_logical is None):
            adjust = False
            self.groupNode.hide()

            if self.tip_point_logical is not None:
                self.line1.setTipPoint(self.tip_point_logical)

        else:
            self.groupNode.show()
            self.line1.setTipPoint(self.tip_point_logical)
            self.line1.setTailPoint(self.tail_point_logical)

        if adjust is True:


            # join ArrowHead and Line
            self._adjustArrowHead()
            self._adjustLine()

    def setTailPoint(self, point, param=False, adjust=True):
        """ This sets the position of the local coordinate system that is the vector.
            If there is already a tip point, set the tail point and then set the tip point again """

        self.tail_point_logical = point

        if (self.tip_point_logical is None or self.tail_point_logical is None):
            adjust = False
            self.groupNode.hide()

            if self.tail_point_logical is not None:
                self.line1.setTailPoint(self.tail_point_logical)
        else:
            self.groupNode.show()
            self.line1.setTipPoint(self.tip_point_logical)
            self.line1.setTailPoint(self.tail_point_logical)

        if adjust is True:


            # join ArrowHead and Line
            self._adjustArrowHead()
            self._adjustLine()

    def _adjustArrowHead(self):
        # 0. scale arrowhead (may just be identity)
        # 1. rotation equal to the line1's rotation
        # 2. translation to the tip of the line1
        #   - translate arrowhead to the tip of the line1
        #   - translate arrowhead back to the scaled back line1's tip

        assert self.line1.nodePath.getPos() == self.line1.tail_point
        assert self.line1.nodePath.getPos() == self.tail_point_logical

        translation_to_tip_forrowvecs = math_utils.getTranslationMatrix3d_forrowvecs(
            self.tip_point_logical[0],
            self.tip_point_logical[1],
            self.tip_point_logical[2])

        # arrowhead_length = -np.cos(np.pi / 6.) * self.arrowhead.scale
        arrowhead_length = self.arrowhead.scale
        arrowhead_direction = self._get_direction()

        b_tilde = - math_utils.multiply_scalar_with_vec3(arrowhead_length, arrowhead_direction)

        translation_to_match_point_forrowvecs = math_utils.getTranslationMatrix3d_forrowvecs(
            b_tilde[0], b_tilde[1], b_tilde[2])

        # translation_forrowvecs = (
        #     # translation_to_tip_forrowvecs * translation_to_match_point_forrowvecs
        #     Mat4()
        # )

        self.arrowhead.nodePath.setMat(
            self.arrowhead.form_from_primitive_trafo *  # for me, this is just the scaling
            self.line1.getRotation_forrowvecs() *
            translation_to_tip_forrowvecs *
            translation_to_match_point_forrowvecs
        )

    def _get_length_logical(self):
        vec_length_logical = np.linalg.norm(
            math_utils.p3d_to_np(self.tail_point_logical - self.tip_point_logical))
        return vec_length_logical

    def _get_direction(self):
        return (
            math_utils.multiply_scalar_with_vec3(
                1./np.linalg.norm(self.tip_point_logical - self.tail_point_logical),
                self.tip_point_logical - self.tail_point_logical))

    def _adjustLine(self):
        # figure out the factor by which to scale back the line1
        # based on the size of the arrow tip
        # l_arrow = -np.cos(np.pi / 6.) * self.arrowhead.scale
        # arrowhead_direction = self._get_direction()

        l_arrowhead = self.arrowhead.scale  # this could be made more general in the ArrowHead class
        l_line_0 = self._get_length_logical()
        c_scaling =  (l_line_0 - l_arrowhead) / l_line_0



        assert c_scaling <= 1.

        scaling_forrowvecs = math_utils.math_convention_to_p3d_mat4(
            math_utils.getScalingMatrix4x4(c_scaling, c_scaling, c_scaling))

        # you apply the scaling with the tail of the vector sitting in the origin, i.e.
        # 0. save it's original tail position
        # 1. translate it to the origin
        # 2. apply the scaling
        # 3. translate it back to it's original position

        assert self.line1.nodePath.getPos() == self.line1.tail_point
        assert self.line1.nodePath.getPos() == self.tail_point_logical

        self.line1.nodePath.setMat(
            (self.line1.nodePath.getMat() *
             math_utils.getTranslationMatrix3d_forrowvecs(-self.tail_point_logical[0],
                                                          -self.tail_point_logical[1],
                                                          -self.tail_point_logical[2]) *
             scaling_forrowvecs *
             math_utils.getTranslationMatrix3d_forrowvecs(self.tail_point_logical[0],
                                                          self.tail_point_logical[1],
                                                          self.tail_point_logical[2])
             ))



class Axis:
    """ An axis is a vector with ticks
    TODO: add rendering of numbers
    TODO: prevent drawing of ticks in the axis' arrow head
    """

    def __init__(self, direction_vector, axis_length=1.,
                 ticksperunitlength=4, thickness1dline=2., color=Vec4(1., 0., 0., 1.)):
        # logical properties
        self.axis_length = axis_length
        self.direction_vector = direction_vector.normalized()
        self.ticksperunitlength = ticksperunitlength

        # building blocks
        self.axis_vector = None
        self.ticks = None

        self.thickness1dline = thickness1dline
        self.color = color

        # p3d node
        # TODO: make a class composed_object and have it automatically have a p3d
        # groupnode
        self.groupNode = GroupNode()

        # build and connect the building blocks according to logical properties
        self._build_vector()
        # self._build_ticks()

        # # add everything together to a transform node
        # self.groupNode.addChildNodePaths([self.axis_vector.groupNode.nodePath,
        #                                   self.ticks_groupNode.nodePath])

    def _build_vector(self):
        tip_point_logical = self.direction_vector * self.axis_length

        if self.axis_vector:
            self.axis_vector.setTipPoint(tip_point_logical)
        else:
            self.axis_vector = Vector(thickness1dline=self.thickness1dline, color=self.color)

            self.axis_vector.setTailPoint(Vec3(0., 0., 0.))
            self.axis_vector.setTipPoint(tip_point_logical)

            self.groupNode.addChildNodePaths(
                [self.axis_vector.groupNode.nodePath])

    def _build_ticks(self):
        # for now, always build new ticks
        if self.ticks:
            # remove all tick p3d nodes
            self.groupNode.removeChildNodePaths(
                [self.ticks_groupNode.nodePath])

        # build new set of ticks
        self.ticks = []
        howmanyticks = self.ticksperunitlength * self.axis_length
        self.ticks_groupNode = GroupNode()

        for i in np.arange(0, self.axis_length, step=1./self.ticksperunitlength):
            trafo_nodePath = NodePath("trafo_nodePath")
            trafo_nodePath.reparentTo(self.ticks_groupNode.nodePath)
            # tick_line = Line2dObject()
            tick_line = Line1dSolid(thickness=self.thickness1dline)
            tick_line.nodePath.reparentTo(trafo_nodePath)

            tick_length = 0.2
            # translation = Vec3(i, 0, -0.25 * tick_length)
            tick_line.setTipPoint(Vec3(0, 0, tick_length))
            translation = Vec3(i, 0, -0.25 * tick_length)
            trafo_nodePath.setPos(
                translation[0], translation[1], translation[2])

            if float(i).is_integer() and i != 0:
                tick_line.nodePath.setColor(1, 0, 0, 1)
            if i == 0:
                tick_line.nodePath.setColor(1, 1, 1, 0.2)

            if float(i).is_integer() and i != 0:
                trafo_nodePath.setScale(.5, 1., .5)
            else:
                trafo_nodePath.setScale(.5, 1., .5)

            self.ticks.append(tick_line)

        # apply rotation to ticks group Node
        self.ticks_groupNode.nodePath.setMat(
            self.axis_vector.line1.getRotation_forrowvecs())

        self.groupNode.addChildNodePaths([self.ticks_groupNode.nodePath])

    def setAxisLength(self, length):
        # set the logical parameter
        self.axis_length = length

        # rebuild (reuse or delete and allocate new)
        self._build_vector()
        self._build_ticks()


class CoordinateSystem:
    """ A coordinate system is a set of Axis objects
    """

    cartesian_axes_directions = [
        Vec3(1., 0., 0.),
        Vec3(0., 1., 0.),
        Vec3(0., 0., 1.)]

    cartesian_axes_colors = [Vec4(1., 0., 0., 1.),  # x-axis : red
                             Vec4(0., 1., 0., 1.),  # y-axis : green
                             Vec4(0., 0., 1., 1.)   # z-axis : blue
                             ]

    def __init__(self, camera, axes=None, dimension=3):
        """
        Parameters:
        camera -- e.g. an Orbiter object, to attach 2d labels properly to the
                  3d geometry
        """
        self.scatters = []
        self.dimension = dimension
        self.axes = []
        self.camera = camera

        self.groupNode = GroupNode()

        for direction_vec, color_vec in zip(CoordinateSystem.cartesian_axes_directions[:dimension], CoordinateSystem.cartesian_axes_colors[:dimension]):
            ax = Axis(direction_vec, thickness1dline=5, color=color_vec)
            self.axes.append(ax)
            self.groupNode.addChildNodePaths([ax.groupNode.nodePath])

        self.attach_axes_labels()

    def attachScatter(self, scatter):
        self.scatters.append(scatter)
        # make sure that axes are long enough to encompass
        # scatter

        # get max and min of scatter in x and y range
        scatters_x_max = max(
            [max([lpoint.x for lpoint in [point.nodePath.getPos() for point in scatter.points]]) for scatter in self.scatters])
        scatters_y_max = max(
            [max([lpoint.z for lpoint in [point.nodePath.getPos() for point in scatter.points]]) for scatter in self.scatters])

        # scatter_x_min = min(
        #     [lpoint.x for lpoint in [point.nodePath.getPos() for point in scatter.points]])
        # scatter_y_min = min(
        #     [lpoint.z for lpoint in [point.nodePath.getPos() for point in scatter.points]])

        # resize the axes of the coordinate system to encompass the scatter

        self.ax1.setAxisLength(scatters_x_max  # - scatter_x_min
                               )
        self.ax2.setAxisLength(scatters_y_max  # - scatter_y_min
                               )

    def attach_axes_labels(self):
        from simple_objects.simple_objects import Pinned2dLabel
        import cameras

        if isinstance(self.camera, cameras.Orbiter.Orbiter):
            pos_rel_to_world_x = Point3(1., 0., 0.)
            myPinnedLabelx = Pinned2dLabel(
                refpoint3d=pos_rel_to_world_x, text="x", xshift=0.02, yshift=0.02)
            self.camera.add_camera_move_hook(myPinnedLabelx.update)

            pos_rel_to_world_y = Point3(0., 1., 0.)
            myPinnedLabely = Pinned2dLabel(
                refpoint3d=pos_rel_to_world_y, text="y", xshift=0.02, yshift=0.02)
            self.camera.add_camera_move_hook(myPinnedLabely.update)

            pos_rel_to_world_z = Point3(0., 0., 1.)
            myPinnedLabelz = Pinned2dLabel(
                refpoint3d=pos_rel_to_world_z, text="z", xshift=0.02, yshift=0.02)
            self.camera.add_camera_move_hook(myPinnedLabelz.update)
        else:
            print(
                "ERR: no other camera yet implemented for attaching lablels to CoordinateSystem")


class Scatter:
    """ a scatter is a set of points at coordinates
    """

    def __init__(self, x, y, **kwargs):
        if 'color' in kwargs:
            self.color = kwargs.get('color')
        else:
            self.color = Vec4(1, 1, 1, 1)

        self.x = x
        self.y = y

        assert(len(x) == len(y))

        if 'z' in kwargs:
            self.z = kwargs.get('z')
        else:
            self.z = np.zeros(np.shape(x))

        assert(len(self.x) == len(self.z))

        self.points = []

        # create the points
        for cur_x, cur_y, cur_z in zip(self.x, self.y, self.z):
            cur_point = Point3d()
            # FIXME: for 3d plots, this has to change
            cur_point.nodePath.setPos(cur_x, cur_y, cur_z)
            cur_point.nodePath.setColor(*self.color)

            self.points.append(cur_point)

        self.groupNode = GroupNode()
        self.groupNode.addChildNodePaths(
            [point.nodePath for point in self.points])


class Box2dOfLines:
    """ a box composed of lines
    """

    def __init__(self, x, y, width, height, **kwargs):
        if 'color' in kwargs:
            self.color = kwargs.get('color')
        else:
            self.color = Vec4(.5, .5, .5, .5)

        self.scale = 1.

        self.width = width
        self.height = height
        self.x_ll = x
        self.y_ll = y

        # -- bottom
        self.line1 = Line2dObject()
        self.line1.setTipPoint(Vec3(self.width, 0, 0))
        self.line1.nodePath.setPos(
            self.line1.nodePath.getPos() + Vec3(self.x_ll, 0, self.y_ll))
        self.line1.nodePath.setColor(self.color)

        # -- left
        self.line2 = Line2dObject()
        self.line2.setTipPoint(Vec3(0, 0., self.height))
        self.line2.nodePath.setPos(
            self.line2.nodePath.getPos() + Vec3(self.x_ll, 0, self.y_ll))
        self.line2.nodePath.setColor(self.color)

        # -- top
        self.line3 = Line2dObject()
        self.line3.setTipPoint(Vec3(self.width, 0., 0.))
        self.line3.nodePath.setPos(self.line3.nodePath.getPos(
        ) + Vec3(self.x_ll, 0, self.y_ll) + Vec3(0, 0, self.height))
        self.line3.nodePath.setColor(self.color)

        # -- right
        self.line4 = Line2dObject()
        self.line4.setTipPoint(Vec3(0, 0., self.height))
        self.line4.nodePath.setPos(self.line4.nodePath.getPos(
        ) + Vec3(self.x_ll, 0, self.y_ll) + Vec3(self.width, 0, 0))
        self.line4.nodePath.setColor(self.color)

        self.lines = [self.line1, self.line2, self.line3, self.line4]

        self.groupNode = GroupNode()
        self.groupNode.addChildNodePaths(
            [lines.nodePath for lines in self.lines])


class CoordinateSystemP3dPlain:
    def __init__(self):
        ls = LineSegs()
        ls.setThickness(1)

        # X axis
        ls.setColor(1.0, 0.0, 0.0, 1.0)
        ls.moveTo(0.0, 0.0, 0.0)
        ls.drawTo(1.0, 0.0, 0.0)

        # Y axis
        ls.setColor(0.0, 1.0, 0.0, 1.0)
        ls.moveTo(0.0, 0.0, 0.0)
        ls.drawTo(0.0, 1.0, 0.0)

        # Z axis
        ls.setColor(0.0, 0.0, 1.0, 1.0)
        ls.moveTo(0.0, 0.0, 0.0)
        ls.drawTo(0.0, 0.0, 1.0)

        geomnode = ls.create()
        nodepath = NodePath(geomnode)

        self.groupNode = GroupNode()
        self.groupNode.addChildNodePaths([nodepath])
