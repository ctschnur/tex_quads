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

from direct.task import Task

from plot_utils.bezier_curve import BezierCurve

from panda3d.core import CollisionTraverser, CollisionHandlerQueue, CollisionRay, CollisionNode, GeomNode, BitMask32, VBase4


class PickableObjectManager:
    """ Each pickable object has to have an individual tag,
    at creation, use this class to generate a new individual tag for it """

    def __init__(self):
        self.objectIdCounter = 0
        # self.objectDict = dict()

    def tag(self, nodePath,  # objectClass
            ):
        self.objectIdCounter += 1
        objectTag = str(self.objectIdCounter)
        nodePath.setTag('objectId', objectTag)
        # self.objectDict[objectTag] = objectClass

    # def get(self, objectTag):
    #     if objectTag in self.objectDict:
    #         return self.objectDict[objectTag]
    #     return None


class PickablePoint(Point):
    """ a flat point (2d box) parented by render """

    def __init__(self, pickableObjectManager, **kwargs):
        Point.__init__(self, **kwargs)

        self.nodePath.setColor(1., 0., 0., 1.)

        # give it a tag to enable picking
        pickableObjectManager.tag(self.nodePath)


    # def drag(self, mouseNp):
    #     # that should be the only thing
    #     self.model.wrtReparentTo(mouseNp)

    #     # self.box.setTag('MyObjectTag', '1')


class DraggablePoint(PickablePoint):
    """ a flat point (2d box) parented by render """

    def __init__(self, pickableObjectManager, **kwargs):
        PickablePoint.__init__(self, **kwargs)

        self.nodePath.setColor(1., 0., 0., 1.)
        pickableObjectManager.tag(self.nodePath, )


class CollisionPicker:
    """ This stores a ray, attached to a camera """

    def __init__(self, camera_gear, render, mousewatchernode, base):

        # -- things that are needed to do picking from different camera orientations
        self.camera_gear = camera_gear  # e.g. the orbiter class is a camera_gear
        self.camera = self.camera_gear.camera
        self.render = render

        self.base = base

        self.mouse_watcher_node = mousewatchernode


        # ---- dragging
        base.accept("escape", sys.exit)
        base.accept('mouse1', self.onPress)
        base.accept('mouse1-up', self.onRelease)
        self.draggedObj = None

        taskMgr.add( self.mouseMoverTask, 'mouseMoverTask' )

        # ----

        # -- things that are needed for collision detection by picking a 3d object
        self.pick_traverser = CollisionTraverser()
        self.collision_queue = CollisionHandlerQueue()

        # ---- build the CollisionRay
        # the pick ray is apparently a 'Solid'
        self.pick_collision_ray = CollisionRay()

        # -- a ray is a half-inifinite straight line
        # it is supposed to shoot out orthogonally to the view plane and hit an object
        self.pick_collision_ray.setOrigin(self.camera.getPos(self.render))

        # -- TODO: update this every time the orbiter camera position changes
        # first, transform the (0,1,0) vector into render's coordinate system
        self.pick_collision_ray.setDirection(
            render.getRelativeVector(camera, Vec3(0, 1, 0)))

        # ---- build the CollisionNode
        self.pick_collision_node = CollisionNode('pick_collision_ray')
        # the pick ray is actually a 3d object
        self.pick_collision_node.addSolid(self.pick_collision_ray)

        # attach the CollisionNode to the camera (not the CollisionRay)
        self.pick_collision_node_nodePath = self.camera.attachNewNode(
            self.pick_collision_node)

        # set a collide mask to the pick_collision_node, 2 objects that should be able to collide must have the same collide mask!
        self.pick_collision_node.setFromCollideMask(GeomNode.getDefaultCollideMask()
                                                    # DraggingInfo.dragMask
                                                    )  # set bit 20 (Default) to the ray

        # add the ray as sth. that can cause collisions, and tell it to fill up our collision queue object when traversing and detecting
        self.pick_traverser.addCollider(
            self.pick_collision_node_nodePath, self.collision_queue)

        self.pick_collision_node_nodePath.show()

    def onPress(self):
        print("pressed")
        if self.mouse_watcher_node.hasMouse() == False:
            return

        # get the position of the mouse, then position the ray where the mouse clicked
        # mouse_pos = base.mouseWatcherNode.getMouse()
        mouse_pos = self.base.mouseWatcherNode.getMouse()

        mouse_pos_adjusted_x, mouse_pos_adjusted_y = self.camera_gear.orbiterLens.getOrthoLensRange()
        # or just base.cam.getFilmSize()


        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

        self.pick_collision_ray.setFromLens(
            self.camera.node(), mouse_pos[0], mouse_pos[1]
            # mouse_pos_adjusted_x, mouse_pos_adjusted_y
        )

        # now actually (manually) traverse to see if the two objects are collided (traverse the render tree (is the camera included there?))
        # this should fill up the collision queue
        self.pick_traverser.traverse(render)

        if self.collision_queue.getNumEntries() > 0:
            # first, sort the entries (? which direction does it do that? to the camera?)
            # get the first entry (closest I suppose)
            entry = self.collision_queue.getEntry(0)
            # return the nodepath of the 'into-object' of the collision
            picked_obj = entry.getIntoNodePath()
            # get the object specifically with that tag (may be a child of the picked object)
            picked_obj_with_tag = picked_obj.findNetTag('objectId')

            # check to see if indeed an object was picked, and which posiition it has
            if not picked_obj_with_tag.isEmpty():
                picked_obj_pos = entry.getSurfacePoint(render)

                print("picked object: ",
                      # picked_obj_with_tag.getTags(), " tag: ",
                      ", the object: ", picked_obj_with_tag, ", the position: ", picked_obj_pos)
                picked_obj_with_tag.setColor(1., 1., 1., 1.)

                # TODO: attach a
                # recalculate position of
                # picked_obj_with_tag.wrtReparentTo(self.pick_collision_node_nodePath)
                # picked_obj_with_tag.setCollideMask(BitMask32.allOff())
            else:
                print("nothing picked")
        else:
            print("no collision")



    def onRelease( self ):
        print("release")
        # obj = self.collisionCheck()
        # self.draggedObj.onRelease() # self.cnp )
        # if obj is not None:
        #     self.draggedObj.onCombine( obj )


    def mouseMoverTask( self, task ):
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            # TODO:
            # project it into the view plane

            # # range of the screen in actual 3d width and height
            # # i.e. size of the visible part of the draggable plane
            # self.camera_gear.camera.node().getLens().getFilmSize()

            # print(mpos)
            self.pick_collision_node_nodePath.setPos(mpos[0], 0, mpos[1])
        return task.cont
