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
    def __init__( self ):
        self.objectIdCounter = 0

    def tag( self, objectNp, # objectClass
    ):
        self.objectIdCounter += 1
        objectTag = str(self.objectIdCounter)
        objectNp.setTag('objectId', objectTag)


class DragAndDropObjectsManager:
    """ Stores all dragger objects.
    Picking works using the nodepath. Thus, we need to store somewhere
    all pickable objects, and then search their nodepaths to get to the one
    that was picked.
    Each drag and drop object has to have an individual tag,
    at creation, use this class to generate a new individual tag for it.
    Once it's picked for dragging, the dragAndDropObjectsManager of the context
    is searched for the picked nodepath """

    def __init__( self ):
        self.objectIdCounter = 0
        self.draggers = []

    def add_dragger(self, dragger):
        self.draggers.append(dragger)
        print("dragger ", dragger, " added to ", self)

    def clear_draggable_objects(self):
        self.draggers = []

    def get_dragger_from_nodePath(self, nodePath):
        """ Go through draggers and query their nodepaths to search
        the object with nodePath.
        Needed e.g. after picking, which gets you back only the lower-level nodePath,
        not the dragger or directly the pickableobject """

        for c_drg in self.draggers:
            if c_drg.nodePath == nodePath:
                return c_drg
        return None


class Dragger:
    """ a dragger object gets assigned a pickable object, and
    dragger objects are managed by DragAndDropObjetsManager.
    it bundles the relevant information about a drag's state """
    def __init__(self, pickablepoint):

        self.pickablepoint = pickablepoint
        # FIXME: figure out a better way than passing the nodePath in here
        self.nodePath = pickablepoint.nodePath

        self.position_before_dragging = None
        self.mouse_position_before_dragging = None

    def init_dragging(self):
        """ save original position """

        r0_obj = math_utils.p3d_to_np(self.nodePath.getPos())

        self.position_before_dragging = Vec3(*r0_obj)

        mouse_pos = base.mouseWatcherNode.getMouse()  # between -1 and 1 in both x and y
        # filmsize = base.cam.node().getLens().getFilmSize()  # the actual width of the film size

        self.mouse_position_before_dragging = mouse_pos

        # -- setup a task that updates the position

        # ---- dragging
        base.accept("escape", sys.exit)
        # base.accept('mouse1', self.onPress)
        base.accept('mouse1-up', self.end_dragging)

        # create an individual task for an individual dragger object
        self.dragging_mouse_move_task = taskMgr.add(self.update_dragging, 'update_dragging')

    def update_dragging(self, task):
        """ save original position,"""

        r0_obj = math_utils.p3d_to_np(self.nodePath.getPos())

        v_cam_forward = math_utils.p3d_to_np(render.getRelativeVector(self.camera_gear.camera, self.camera_gear.camera.node().getLens().getViewVector()))
        v_cam_forward = v_cam_forward / np.linalg.norm(v_cam_forward)
        # self.camera_gear.camera.node().getLens().getViewVector()

        v_cam_up = math_utils.p3d_to_np(render.getRelativeVector(self.camera_gear.camera, self.camera_gear.camera.node().getLens().getUpVector()))
        v_cam_up = v_cam_up / np.linalg.norm(v_camup)

        r_cam = math_utils.p3d_to_np(self.camera_gear.camera.getPos())

        e_up = math_utils.p3d_to_np(v_cam_up/np.linalg.norm(v_cam_up))
        # e_up = e_up / np.linalg.norm(e_up)
        e_cross = math_utils.p3d_to_np(np.cross(v_cam_forward/np.linalg.norm(v_cam_forward), e_up))

        # determine the middle origin of the draggable plane (where the plane intersects the camera's forward vector)
        r0_middle_origin = math_utils.LinePlaneCollision(v_cam_forward, r0_obj, v_cam_forward, r_cam)

        print("r0_obj", r0_obj)
        print("v_cam_forward", v_cam_forward)
        print("v_cam_up", v_cam_up)
        print("r_cam", r_cam)
        print("e_up", e_up)
        print("e_cross", e_cross)
        print("r0_middle_origin", r0_middle_origin)


        # -- calculate the bijection between mouse coordinates m_x, m_y and plane coordinates p_x, p_y
        # ---- calculate (solely camera and object needed and the recorded mouse position before dragging) the p_xy_offset
        p_xy_offset = conventions.getFilmSizeCoordinates(self.mouse_position_before_dragging[0], self.mouse_position_before_dragging[1], p_x_0=0., p_y_0=0.)

        mouse_pos = base.mouseWatcherNode.getMouse()  # between -1 and 1 in both x and y
        # filmsize = base.cam.node().getLens().getFilmSize()  # the actual width of the film size

        p_x, p_y = conventions.getFilmSizeCoordinates(mouse_pos[0], mouse_pos[1], p_xy_offset[0], p_xy_offset[1])

        drag_vec = p_x * e_cross + p_y * e_up

        print("drag_vec", drag_vec)

        # set the position while dragging
        self.nodePath.setPos(self.position_before_dragging + Vec3(*drag_vec))

        return task.cont

    def end_dragging(self):
        self.position_before_dragging = None
        self.mouse_position_before_dragging = None
        taskMgr.remove(self.dragging_mouse_move_task)


class PickablePoint(Point):
    """ a flat point (2d box) parented by render """
    def __init__(self, pickableObjectManager, **kwargs):
        Point.__init__(self, **kwargs)

        self.nodePath.setColor(1., 0., 0., 1.)
        pickableObjectManager.tag(self.nodePath)

        # self.box.setTag('MyObjectTag', '1')


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
                picked_obj_with_tag.setColor(1., 1., 1., 1.)

                # to retrieve the properties of the picked object associated with the dragging and dropping,
                # search the DragAndDropObjectsManager's array for the picked NodePath

                # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
                picked_draggable_object = self.dragAndDropObjectsManager.get_dragger_from_nodePath(picked_obj_with_tag)

                if picked_draggable_object is None:
                    print("picked_draggable_object is None, no object found in draggable object manager")
                    return
                else:
                    # set drag state of this object to True, save original position and add in the mousemoveevent a function updating it's position based on the mouse position
                    picked_draggable_object.dragger.init_dragging()



class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.setFrameRateMeter(True)
        render.setAntialias(AntialiasAttrib.MAuto)

        ob = Orbiter(base.cam, radius=3.)
        cs = CoordinateSystem(ob)

        # # -- plot surface using points
        # from plot_utils.pointcloud.pointcloud import plot_xy_z
        # x = np.linspace(0., 1., num=20, endpoint=True)
        # y = np.linspace(0., 1., num=20, endpoint=True)
        # plot_xy_z(x, y, lambda x, y: x**3. + y**3.)

        ob.set_view_to_yz_plane()

        # plot bezier curve together with points

        point_coords_arr = np.array([[0., 0., 0.],
                                     [0., 0., 1.],
                                     [0., 1., 1.],
                                     [0., 1., 0.]])

        BezierCurve(point_coords_arr)


        pickableObjectManager = PickableObjectManager()

        dragAndDropObjectsManager = DragAndDropObjectsManager()
        collisionPicker = CollisionPicker(ob, render, self.mouseWatcherNode, base, dragAndDropObjectsManager)

        myDirectObject = DirectObject.DirectObject()
        myDirectObject.accept('mouse1', collisionPicker.onMouseTask)

        control_points = []
        for p in point_coords_arr:
            pt = PickablePoint(pickableObjectManager,
                               pos=Vec3(*p), thickness=10, point_type="quasi2d")

            pt_dragger = Dragger(pt)

            dragAndDropObjectsManager.add_dragger(pt_dragger)

            pt.nodePath.setHpr(90, 0, 0)  # 90 degrees yaw
            pt.nodePath.showBounds()
            control_points.append(pt)

        def findChildrenAndSetRenderModeRecursively(parentnode):
            children = parentnode.get_children()
            for child in children:
                findChildrenAndSetRenderModeRecursively(child)
                child.setRenderModeFilled()

        findChildrenAndSetRenderModeRecursively(render)


app = MyApp()
app.run()
