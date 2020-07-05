from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain
from simple_objects.simple_objects import Line2dObject, Point, ArrowHead, Line1dObject, LineDashed1dObject, ArrowHeadCone, ArrowHeadConeShaded
from simple_objects import primitives
from local_utils import math_utils

import numpy as np

from direct.showbase.ShowBase import ShowBase, DirectObject
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

import local_tests.svgpathtodat.main

import os
import sys
import pytest
import gltf

from cameras.Orbiter import Orbiter

from plot_utils.bezier_curve import BezierCurve

# import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.task import Task
import sys, random

# Collision mask worn by all draggable objects.
dragMask = BitMask32.bit(1)
# Collision mask worn by all droppable objects.
dropMask = BitMask32.bit(1)

highlight = VBase4(.3,.3,.3,1)

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.setFrameRateMeter(True)
        render.setAntialias(AntialiasAttrib.MAuto)

        # ob = Orbiter(radius=3.)
        # cs = CoordinateSystem(ob)


        # # -- plot surface using points
        # from plot_utils.pointcloud.pointcloud import plot_xy_z
        # x = np.linspace(0., 1., num=20, endpoint=True)
        # y = np.linspace(0., 1., num=20, endpoint=True)
        # plot_xy_z(x, y, lambda x, y: x**3. + y**3.)

        # ob.set_view_to_yz_plane()

        # plot bezier curve together with points

        point_coords_arr = np.array([[0., 0., 0.],
                                     [0., 0., 1.],
                                     [0., 1., 1.],
                                     [0., 1., 0.]])

        BezierCurve(point_coords_arr)

        # # -- make draggable control points
        # objectManager = objectMangerClass()
        # mouseCollision = mouseCollisionClass()

        control_points = []
        for p in point_coords_arr:
            pt = Point(pos=Vec3(*p), thickness=10, point_type="quasi2d")
            pt.nodePath.setHpr(90, 0, 0)  # 90 degrees yaw
            # control_points.append(pt)
            # draggable = dragDropObjectClass(pt.nodePath, objectManager)
            pt.nodePath.showBounds()
            control_points.append(pt)



        base.disableMouse()
        self.setupWorld()

        myDirectObject = DirectObject.DirectObject()
        myDirectObject.accept('mouse1', self.onMouseTask)

        self.setupCollisionObjects()


        def findChildrenAndSetRenderModeRecursively(parentnode):
            children = parentnode.get_children()
            for child in children:
                findChildrenAndSetRenderModeRecursively(child)
                child.setRenderModeFilled()

        findChildrenAndSetRenderModeRecursively(render)


    def setupWorld(self):
        self.box = loader.loadModel('box')
        self.box.reparentTo(render)
        self.box.setScale(0.5)
        self.box.setPos(0., 0., 0.)
        self.box.setHpr(0., 0., 0.)
        self.box.setColor(0., 0.2, 0.8)

        self.box.setTag('MyObjectTag', '1')

        base.cam.setPos(5, 0, 0)
        base.cam.lookAt(0., 0., 0.)

        # # --- set a point light
        # from panda3d.core import PointLight
        # self.plight = PointLight('plight')
        # self.plight.setColor(Vec4(0.7, 0.7, 0.7, 1.))
        # self.plnp = render.attachNewNode(self.plight)
        # # self.set_pointlight_pos_spherical_coords()
        # self.plnp.setPos(self.box, 0., 0., 40.)
        # render.setLight(self.plnp)

    def setupCollisionObjects(self):
        # creating stuff
        self.pick_traverser = CollisionTraverser()
        self.collision_queue = CollisionHandlerQueue()
        self.pick_collision_ray = CollisionRay()  # the pick ray is apparently a 'Solid'

        # self.camera = base.cam
        # self.render = render

        # a ray is a half-inifinite straight line
        self.pick_collision_ray.setOrigin(base.cam.getPos(self.render))
        # picking in the positive y direction
        self.pick_collision_ray.setDirection(render.getRelativeVector(camera, Vec3(0, 1, 0)))

        self.pick_collision_node = CollisionNode('pick_collision_ray')
        self.pick_collision_node.addSolid(self.pick_collision_ray)  # the pick ray is actually a 3d object

        # attach the CollisionNode to the camera (not the CollisionRay)
        self.pick_collision_node_nodePath = base.cam.attachNewNode(self.pick_collision_node)

        # set a collide mask to the pick_collision_node, 2 objects that should be able to collide must have the same collide mask!
        self.pick_collision_node.setFromCollideMask(GeomNode.getDefaultCollideMask())  # set bit 20 (Default) to the ray

        # add the ray as sth. that can cause collisions, and tell it to fill up our collision queue object when traversing and detecting
        self.pick_traverser.addCollider(self.pick_collision_node_nodePath, self.collision_queue)


    def onMouseTask(self):
        if self.mouseWatcherNode.hasMouse() == False:
            return

        # get the position of the mouse, then position the ray where the mouse clicked
        mouse_pos = base.mouseWatcherNode.getMouse()

        self.pick_collision_ray.setFromLens(base.cam.node(), mouse_pos[0], mouse_pos[1])

        # now actually (manually) traverse to see if the two objects are collided (traverse the render tree (is the camera included there?))
        self.pick_traverser.traverse(render)  # this should fill up the collision queue

        if self.collision_queue.getNumEntries() > 0:
            # first, sort the entries (? which direction does it do that? to the camera?)
            entry = self.collision_queue.getEntry(0)  # get the first entry (closest I suppose)
            picked_obj = entry.getIntoNodePath()  # return the nodepath of the 'into-object' of the collision
            picked_obj_with_tag = picked_obj.findNetTag('MyObjectTag')  # get the object specifically with that tag (may be a child of the picked object)

            # check to see if indeed an object was picked, and which posiition it has
            if not picked_obj_with_tag.isEmpty():
                picked_obj_pos = entry.getSurfacePoint(render)
                # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
                print("picked object: ",
                      # picked_obj_with_tag.getTags(), " tag: ",
                      ", the object: ", picked_obj_with_tag, ", the position: ", picked_obj_pos)
app = MyApp()
app.run()
