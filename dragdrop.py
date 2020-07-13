from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain
from simple_objects.simple_objects import Line2dObject, PointPrimitive, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded
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

# import direct.directbase.DirectStart
from pandac.PandaModules import *
from direct.task import Task
import sys, random

# Collision mask worn by all draggable objects.
dragMask = BitMask32.bit(1)
# Collision mask worn by all droppable objects.
dropMask = BitMask32.bit(1)

highlight = VBase4(.3,.3,.3,1)


class objectMangerClass:
  def __init__( self ):
    self.objectIdCounter = 0
    self.objectDict = dict()

  def tag( self, objectNp, objectClass ):
    self.objectIdCounter += 1
    objectTag = str(self.objectIdCounter)
    objectNp.setTag( 'objectId', objectTag )
    self.objectDict[objectTag] = objectClass

  def get( self, objectTag ):
    if objectTag in self.objectDict:
      return self.objectDict[objectTag]
    return None


class dragDropObjectClass:
  def __init__( self, np, objectManager):
    self.model = np
    self.previousParent = None
    self.model.setCollideMask(dragMask)
    self.objectManager = objectManager
    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
    self.objectManager.tag( self.model, self )

  def onPress( self, mouseNp ):
    self.previousParent = self.model.getParent()
    self.model.wrtReparentTo( mouseNp )
    self.model.setCollideMask(BitMask32.allOff())

  def onRelease( self ):
    self.model.wrtReparentTo( self.previousParent )
    self.model.setCollideMask(dragMask)

  def onCombine( self, otherObj ):
    self.model.setPos( otherObj.model.getPos() )

class mouseCollisionClass:
  def __init__(self):
    base.accept("escape", sys.exit)
    base.accept('mouse1', self.onPress)
    base.accept('mouse1-up', self.onRelease)
    self.draggedObj = None
    self.setupCollision()

    taskMgr.add( self.mouseMoverTask, 'mouseMoverTask' )

  def setupCollision( self ):
    # Initialise the collision ray that is used to detect which draggable
    # object the mouse pointer is over.
    cn = CollisionNode('')
    cn.addSolid( CollisionRay(0,-100,0, 0,1,0) )
    cn.setFromCollideMask(dragMask)
    cn.setIntoCollideMask(BitMask32.allOff())
    self.cnp = render.attachNewNode(cn)
    self.ctrav = CollisionTraverser()
    self.queue = CollisionHandlerQueue()
    self.ctrav.addCollider(self.cnp, self.queue)
    self.cnp.show()

  def mouseMoverTask( self, task ):
    if base.mouseWatcherNode.hasMouse():
      mpos = base.mouseWatcherNode.getMouse()
      self.cnp.setPos(render2d,mpos[0],0,mpos[1])
    return task.cont

  def collisionCheck( self ):
    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
    self.ctrav.traverse(render)
    self.queue.sortEntries()
    if self.queue.getNumEntries():
      np = self.queue.getEntry( self.queue.getNumEntries()-1 ).getIntoNodePath() #self.queue.getNumEntries()-1
      objectId = np.getTag( 'objectId' )
      if objectId is None:
        objectId = np.findNetTag( 'objectId' )
      if objectId is not None:
        object = self.objectManager.get( objectId )
        return object
    return None

  def onPress( self ):
    obj = self.collisionCheck()
    import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
    if obj is not None:
      self.draggedObj = obj
      obj.onPress( self.cnp )

  def onRelease( self ):
    obj = self.collisionCheck()
    self.draggedObj.onRelease() # self.cnp )
    if obj is not None:
      self.draggedObj.onCombine( obj )


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.setFrameRateMeter(True)
        render.setAntialias(AntialiasAttrib.MAuto)

        ob = Orbiter(radius=3.)
        # cs = CoordinateSystem(ob)

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

        # -- make draggable control points
        objectManager = objectMangerClass()
        mouseCollision = mouseCollisionClass()

        control_points = []
        for p in point_coords_arr:
            pt = PointPrimitive(pos=Vec3(*p), thickness=10)
            pt.nodePath.setHpr(90, 0, 0)  # 90 degrees yaw
            # control_points.append(pt)
            draggable = dragDropObjectClass(pt.nodePath, objectManager)
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


# if __name__ == '__main__':
#   cm = CardMaker('cm')
#   left,right,bottom,top = 0,2,0,-2
#   width = right - left
#   height = top - bottom
#   cm.setFrame(left,right,bottom,top)
#   node = render.attachNewNode('')
#   node.setPos(-1.2,0,0.9)
#   cards = []

#   for i in range(3):
#     for j in range(3):
#       card = node.attachNewNode(cm.generate())
#       card.setScale(.2)
#       card.setPos(i/2.0,0,-j/2.0)
#       card.setColor(random.random(),random.random(),random.random())
#       draggable = dragDropObjectClass(card)
#       cards.append(card)
