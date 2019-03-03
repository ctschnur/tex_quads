import conventions

import custom_geometry
import texture_utils

from latex_expression_manager import LatexImageManager, LatexImage

from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Vec3, 
    Vec4,
    TransparencyAttrib, 
    AntialiasAttrib,
    NodePath,
    Mat4,
    Mat3)
from direct.interval.IntervalGlobal import Wait, Sequence
from direct.interval.LerpInterval import LerpFunc

import hashlib
import numpy as np


class Animator:
    # interval/sequence initiate functions
    def initiateTranslationMovement(self, v_x=0., v_z=0., duration=0., delay=0.):
        extraArgs = [duration, v_x, v_z]
        self.p3d_interval = LerpFunc(
            self.updatePosition, duration=duration, extraArgs=extraArgs)
        Sequence(Wait(delay), self.p3d_interval).start()

    def initiateRotationMovement(self, h=0., p=0., r=0., duration=0., delay=0.):
        extraArgs = [duration, h, p, r]
        self.p3d_interval = LerpFunc(
            self.updateRotation, duration=duration, extraArgs=extraArgs)
        Sequence(Wait(delay), self.p3d_interval).start()

    # interval update functions
    def updatePosition(self, t, duration, v_x, v_z):
        self.nodePath.setPos(v_x * (t / duration), 1., v_z * (t / duration))

    def updateRotation(self, t, duration, h, p, r):
        self.nodePath.setHpr(h * (t / duration), p *
                             (t / duration), r * (t / duration))

class Polygon2d(Animator):
    def __init__(self, point_cloud):
        Animator.__init__(self)

        self.makeObject(point_cloud)

    def makeObject(self, point_cloud):
        self.node = custom_geometry.create_colored_polygon2d_GeomNode_from_point_cloud(
            point_cloud, 
            color_vec4=Vec4(1., 1., 1., 1.))
        self.nodePath = render.attachNewNode(self.node)

class Polygon2dTestTriangles(Animator):
    def __init__(self, symbol_geometries):
        Animator.__init__(self)

        self.makeObject(symbol_geometries)

    def makeObject(self, symbol_geometries):
        self.node = custom_geometry.create_GeomNode_Simple_Polygon_with_Hole(symbol_geometries)
        # self.node = custom_geometry.create_GeomNode_Simple_Polygon_without_Hole(symbol_geometries)

        self.nodePath = render.attachNewNode(self.node)
        # self.nodePath.setRenderModeWireframe()

class Polygon2dTestLineStrips(Animator):
    def __init__(self, symbol_geometries):
        Animator.__init__(self)

        self.makeObject(symbol_geometries)

    def makeObject(self, symbol_geometries):
        self.node = custom_geometry.create_GeomNode_Simple_Polygon_with_Hole_LineStrips(symbol_geometries)

        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setRenderModeWireframe()

class Box2d(Animator):

    def __init__(self):
        Animator.__init__(self)

        self.makeObject()

    def makeObject(self):
        self.node = custom_geometry.createColoredUnitQuadGeomNode(
            color_vec4=Vec4(1., 1., 1., 1.))
        self.nodePath = render.attachNewNode(self.node)
        self.nodePath.setTwoSided(True)  # enable backface-culling for all Animators

class Box2dCentered(Box2d):

    def __init__(self):
        super(Box2dCentered, self).__init__()

    def makeObject(self):
        self.node = custom_geometry.createColoredUnitQuadGeomNode(
            color_vec4=Vec4(1., 1., 1., 1.), center_it=True)
        self.nodePath = render.attachNewNode(self.node)

class LatexTextureObject(Box2d):
    def __init__(self, tex_expression):
        Animator.__init__(self)

        self.tex_expression = tex_expression

        self.makeObject()

        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        """ initial setup transformation: a unit quad with an image in the
        background is being scaled so that the pixel height and width fits
        exactly with the screen resolution"""

        self.nodePath.setMat(
            conventions.getMat4_scale_quad_for_texture_pixels_to_match_screen_resolution() *
            conventions.getMat4_scale_unit_quad_to_image_aspect_ratio(self.myPNMImage.getXSize(), self.myPNMImage.getYSize()))

    def makeObject(self):
        """ only creates geometry (doesn't transform it) """
        self.node = custom_geometry.createTexturedUnitQuadGeomNode()
        self.nodePath = render.attachNewNode(self.node)

        def applyImageAndTexture():
            """assign the Texture() to the NodePath() that contains the Geom()
            load image with the object's hash"""
            expr_hash = hashlib.sha256(
                str(self.tex_expression).encode("utf-8")).hexdigest()

            myLatexImage = LatexImageManager.retrieveLatexImageFromHash(
                expr_hash)
            if myLatexImage is None:
                myLatexImage = LatexImage(expression_str=self.tex_expression)
                myLatexImage.compileToPNG()
                LatexImageManager.addLatexImageToCompiledSet(myLatexImage)
                LatexImageManager.addLatexImageToLoadedSet(myLatexImage)

            self.myPNMImage = myLatexImage.getPNMImage()
            self.myTexture = texture_utils.getTextureFromImage(self.myPNMImage)
            self.nodePath.setTexture(self.myTexture, 1)
            self.nodePath.setTransparency(TransparencyAttrib.MAlpha)

        applyImageAndTexture()

        
class Line(Box2dCentered):
    width = 0.05
    initial_length = 1.

    def __init__(self):
        super(Line, self).__init__()
        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        self.nodePath.setScale(1., 1., self.width)
        self.axis_spawning_preparation_trafo = self.nodePath.getMat()
        self.nodePath.setPos(0.5, 0, 0)
        self.to_xhat_trafo = self.nodePath.getMat()
        self.length = self.initial_length
        self.has_zero_length_is_circle = False

    def setTipPoint(self, tip_point):
        # where I want to move it
        self.xhat_prime = np.array([tip_point.getX(), tip_point.getY(), tip_point.getZ()])
        self.rotation_forrowvecs = Mat4()

        if self.has_zero_length_is_circle is False: 
            # in case it should become a zero length line (circle)
            if (    tip_point[0] == 0. 
                and tip_point[1] == 0. 
                and tip_point[2] == 0. ):
                # change geometry to visualize a line of length zero (let that be a small circle)
                self.node.removeAllGeoms()
                new_geom = custom_geometry.createColoredUnitCircle()
                self.node.addGeom(new_geom)

                # scale the unit circle to have a line's width
                vx = np.linalg.norm(self.width/2)
                vy = np.linalg.norm(self.width/2)
                vz = np.linalg.norm(self.width/2)
                scaling_unitcircle = np.array([[vx,  0,  0, 0],
                                               [0,  vy,  0, 0],
                                               [0,   0, vz, 0], 
                                               [0,   0,  0, 1]])

                scaling_unitcircle_forrowvecs = Mat4(*tuple(np.transpose(scaling_unitcircle).flatten()))
                self.nodePath.setMat(scaling_unitcircle_forrowvecs)

                self.has_zero_length_is_circle = True
                self.nodePath.setRenderModeWireframe()
                return
                
            else: 
                xhat = np.array([1, 0, 0])
                normal = np.array([0, 1, 0])  # yhat

                # find angle between xhat and xhat_prime with fixed normal vector (axis of rotation), range theta = [-pi, pi]
                # determinant, i.e. volume of parallelepiped
                det = np.dot(normal, np.cross(xhat, self.xhat_prime))
                dot = np.dot(xhat, self.xhat_prime)
                theta = np.arctan2(det, dot)
                rotation = np.array([[np.cos(theta),  0, np.sin(theta), 0],
                                    [0,              1,             0, 0],
                                    [-np.sin(theta), 0, np.cos(theta), 0], 
                                    [0,              0,             0, 1]])
                # scaling
                vx = np.linalg.norm(self.xhat_prime)
                vy = 1.
                vz = 1.
                scaling = np.array([[vx,  0,  0, 0],
                                    [0,  vy,  0, 0],
                                    [0,   0, vz, 0], 
                                    [0,   0,  0, 1]])

                self.rotation_forrowvecs = Mat4(*tuple(np.transpose(rotation).flatten()))
                scaling_forrowvecs = Mat4(*tuple(np.transpose(scaling).flatten()))
                # first the scaling, then the rotation, remember the row vector stands on the left
                trafo = scaling_forrowvecs * self.rotation_forrowvecs  

                self.nodePath.setMat(self.nodePath.getMat() * trafo)
                self.nodePath.setRenderModeWireframe()
                return

        print("WARNING: a line with 0 length will not be transformed back to finite length yet")


class Point(Box2dCentered):
    scale_z = .05
    scale_x = .05

    def __init__(self):
        super(Point, self).__init__()
        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        self.nodePath.setScale(self.scale_x, 1., self.scale_z)

    
class ParallelLines:
    """ Draw Parallel Lines

    """
    def __init__(self):
        self.spacing = .25
        self.number_of_lines = 15

        # transform the lines
        # - stretch the unit length lines to the specified size
        # - position them in order, evenly spaced

        self.lines = [Line() for i in range(self.number_of_lines)]
        for idx, line in enumerate(self.lines): 
            line.nodePath.setScale(line.nodePath, 1., 1., 1.)
            line.nodePath.setPos(0., 0, idx * self.spacing)

            
class ArrowHead(Box2dCentered):
    equilateral_length = Line.width * 4.
    scale = .1

    def __init__(self):
        super(ArrowHead, self).__init__()
        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        self.nodePath.setScale(self.scale, self.scale, self.scale)

    def makeObject(self):
        """it's not just a scaled quad, so it needs different Geometry"""
        self.node = custom_geometry.createColoredArrowGeomNode(
            color_vec4=Vec4(1., 1., 1., 1.), center_it=True)
        self.nodePath = render.attachNewNode(self.node)

        
class Vector:
    """Documentation for Vector
       combines an arrowhead and a line and applys transformations to them so that it 
       it looks like a properly drawn vector
    """
    def __init__(self, tip_point):
        self.line = Line()
        self.line.setTipPoint(tip_point)

        self.arrowhead = ArrowHead()

        # join ArrowHead and Line
        self._adjustArrowHead()
        self._adjustLine()
        
    def _adjustArrowHead(self): 
        # apply the same rotation as to the line
        # and then a translation to the tip of the vector

        # rotation: already computed (same as line)
        # translation
        bx = self.line.xhat_prime[0]
        by = self.line.xhat_prime[1]
        bz = self.line.xhat_prime[2]
        translation_to_xhat = np.array([[1, 0, 0, bx],
                                        [0, 1, 0, by],
                                        [0, 0, 1, bz], 
                                        [0, 0, 0,  1]])

        arrowhead_length = -np.cos(np.pi / 6.) * self.arrowhead.scale
        arrowhead_direction = self.line.xhat_prime / np.linalg.norm(self.line.xhat_prime)

        b_tilde = arrowhead_length * arrowhead_direction
        b_tilde_x = b_tilde[0]
        b_tilde_y = b_tilde[1]
        b_tilde_z = b_tilde[2]

        translation_to_match_point = np.array([[1, 0, 0, b_tilde_x],
                                                [0, 1, 0, b_tilde_y],
                                                [0, 0, 1, b_tilde_z], 
                                                [0, 0, 0,         1]])

        self.translation_to_xhat_forrowvecs = (
            Mat4(*tuple(np.transpose(translation_to_xhat).flatten())))
        self.translation_to_match_point_forrowvecs = (
            Mat4(*tuple(np.transpose(translation_to_match_point).flatten())))

        self.translation_forrowvecs = (
            self.translation_to_xhat_forrowvecs * self.translation_to_match_point_forrowvecs)

        trafo = self.line.rotation_forrowvecs * self.translation_forrowvecs

        self.arrowhead.nodePath.setMat(self.arrowhead.nodePath.getMat() * trafo)

        self.arrowhead.nodePath.setRenderModeWireframe()

    def _adjustLine(self):
        l_arrow = -np.cos(np.pi / 6.) * self.arrowhead.scale
        arrowhead_direction = self.line.xhat_prime / np.linalg.norm(self.line.xhat_prime)

        l_line_0 = np.linalg.norm(self.line.xhat_prime)

        c_scaling =  l_line_0 / (l_line_0 - l_arrow)

        # scaling
        vx = c_scaling
        vy = c_scaling
        vz = c_scaling
        scaling = np.array([[vx,  0,  0, 0],
                            [0,  vy,  0, 0],
                            [0,   0, vz, 0], 
                            [0,   0,  0, 1]])

        scaling_forrowvecs = Mat4(*tuple(np.transpose(scaling).flatten()))

        trafo = scaling_forrowvecs

        self.line.nodePath.setMat(self.line.nodePath.getMat() * trafo)

        
class GroupNode(Animator):
    """Documentation for GroupNode

    """
    def __init__(self):
        super(GroupNode, self).__init__()
        self.nodePath = NodePath("empty")
        self.nodePath.reparentTo(render)

    def addChildNodePaths(self, NodePaths):
        for np in NodePaths:
            np.reparentTo(self.nodePath)
