from conventions import conventions

from local_utils import math_utils

from simple_objects.simple_objects import Line2dObject, PointPrimitive, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, Point3d

from panda3d.core import NodePath, Vec3, Point3, Point2, Mat4, Vec4

from direct.task import Task

from panda3d.core import CollisionTraverser, CollisionHandlerQueue, CollisionRay, CollisionNode, GeomNode, BitMask32

import numpy as np

import sys

class PickableObjectManager:
    """ Each pickable object has to have an individual tag,
    at creation, use this class to generate a new individual tag for it """

    def __init__( self ):
        self.objectIdCounter = 0

    def tag( self, objectNp, # objectClass
    ):
        self.objectIdCounter += 1
        objectTag = str(self.objectIdCounter)
        objectNp.setTag('objectId', objectTag)



class CollisionPicker:
    """ This stores a ray, attached to a camera """

    def __init__(self, camera_gear, render, mousewatchernode, base, dragAndDropObjectsManager):
        self.dragAndDropObjectsManager = dragAndDropObjectsManager

        # -- things that are needed to do picking from different camera orientations
        self.camera_gear = camera_gear  # e.g. the orbiter class is a camera_gear
        self.camera = self.camera_gear.camera
        self.render = render

        self.base = base

        self.mouse_watcher_node = mousewatchernode

        # -- things that are needed for collision detection by picking a 3d object
        self.pick_traverser = CollisionTraverser()
        self.collision_queue = CollisionHandlerQueue()

        # ---- build the CollisionRay
        self.pick_collision_ray = CollisionRay()  # the pick ray is apparently a 'Solid'

        # -- a ray is a half-inifinite straight line
        # it is supposed to shoot out orthogonally to the view plane and hit an object
        self.pick_collision_ray.setOrigin(self.camera.getPos(self.render))

        # -- TODO: update this every time the orbiter camera position changes
        # first, transform the (0,1,0) vector into render's coordinate system

        self.pick_collision_ray.setDirection(render.getRelativeVector(camera, Vec3(0, 1, 0)))

        # ---- build the CollisionNode
        self.pick_collision_node = CollisionNode('pick_collision_ray')
        self.pick_collision_node.addSolid(self.pick_collision_ray)  # the pick ray is actually a 3d object

        # attach the CollisionNode to the camera (not the CollisionRay)
        self.pick_collision_node_nodePath = self.camera.attachNewNode(self.pick_collision_node)

        # set a collide mask to the pick_collision_node, 2 objects that should be able to collide must have the same collide mask!
        self.pick_collision_node.setFromCollideMask(GeomNode.getDefaultCollideMask()
            # DragDropObject.dragMask
        )  # set bit 20 (Default) to the ray

        # add the ray as sth. that can cause collisions, and tell it to fill up our collision queue object when traversing and detecting
        self.pick_traverser.addCollider(self.pick_collision_node_nodePath, self.collision_queue)


    def onMouseTask(self):

        if self.mouse_watcher_node.hasMouse() == False:
            return

        # get the position of the mouse, then position the ray where the mouse clicked
        # mouse_pos = base.mouseWatcherNode.getMouse()

        mouse_pos = base.mouseWatcherNode.getMouse()

        self.pick_collision_ray.setFromLens(self.camera.node(), mouse_pos[0], mouse_pos[1])

        # now actually (manually) traverse to see if the two objects are collided (traverse the render tree (is the camera included there?))
        self.pick_traverser.traverse(render)  # this should fill up the collision queue

        if self.collision_queue.getNumEntries() > 0:
            # first, sort the entries (? which direction does it do that? to the camera?)
            entry = self.collision_queue.getEntry(0)  # get the first entry (closest I suppose)
            picked_obj = entry.getIntoNodePath()  # return the nodepath of the 'into-object' of the collision
            picked_obj_with_tag = picked_obj.findNetTag('objectId')  # get the object specifically with that tag (may be a child of the picked object)

            # check to see if indeed an object was picked, and which posiition it has
            if not picked_obj_with_tag.isEmpty():
                picked_obj_pos = entry.getSurfacePoint(render)

                print("picked object: ",
                      # picked_obj_with_tag.getTags(), " tag: ",
                      ", the object: ", picked_obj_with_tag, ", the position: ", picked_obj_pos)
                # picked_obj_with_tag.setColor(1., 1., 1., 1.)  # for debugging

                # to retrieve the properties of the picked object associated with the dragging and dropping,
                # search the DragAndDropObjectsManager's array for the picked NodePath


                picked_dragger = self.dragAndDropObjectsManager.get_dragger_from_nodePath(picked_obj_with_tag)

                if picked_dragger is None:
                    print("picked_dragger is None, no corresponding dragger with the picked object found in draggable object manager")
                    return
                else:
                    # set drag state of this object to True, save original position and add in the mousemoveevent a function updating it's position based on the mouse position
                    picked_dragger.init_dragging()
                    print("init dragging ----------------")
