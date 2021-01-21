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

import numpy as np


class TQGraphicsNodePath:
    """ Anything that fundamentally is a only a graphics object in this engine should have these properties. """

    def __init__(self, **kwargs):
        self.TQGraphicsNodePath_creation_parent_node = None

        if 'TQGraphicsNodePath_creation_parent_node' in kwargs:
            self.TQGraphicsNodePath_creation_parent_node = kwargs.get(
                'TQGraphicsNodePath_creation_parent_node')
        else:
            self.TQGraphicsNodePath_creation_parent_node = render

        self.set_parent_node_for_nodepath_creation(
            self.TQGraphicsNodePath_creation_parent_node)

        if 'p3d_nodepath' in kwargs:
            p3d_nodepath = kwargs.get(
                'p3d_nodepath')
            self.set_p3d_nodepath(p3d_nodepath)

    @staticmethod
    def from_p3d_nodepath(p3d_nodepath, **tq_graphics_nodepath_kwargs):
        """ factory """
        go = TQGraphicsNodePath(**tq_graphics_nodepath_kwargs)
        go.set_p3d_nodepath(p3d_nodepath)
        return go

    def set_parent_node_for_nodepath_creation(
            self, TQGraphicsNodePath_creation_parent_node):
        """ when calling attachNewNode, a new node pat is generated.
        E.g.: To attach a line to render (3d world) is different than attaching
        it to aspect2d (2d GUI plane), since the aspect2d children are not directly
        affected by camera movements
        Args:
        - TQGraphicsNodePath_creation_parent_node : the NodePath to attach the TQGraphicsNodePath to
                                          (e.g. render or aspect2d in p3d)
        """

        # self.set_parent_node_for_nodepath_creation(self.TQGraphicsNodePath_creation_parent_node)
        self.TQGraphicsNodePath_creation_parent_node = TQGraphicsNodePath_creation_parent_node

    def set_p3d_nodepath(self, p3d_nodepath):
        """ """
        self.p3d_nodepath = p3d_nodepath

    def get_parent_node_for_nodepath_creation(self):
        return self.TQGraphicsNodePath_creation_parent_node

    def set_render_above_all(self, p):
        """ set render order to be such that it renders normally (false), or above all (true)
        Args:
            p: True or False to enable or disable the 'above all' rendering mode """

        try:
            if p == True:
                self.p3d_nodepath.setBin("fixed", 0)
                self.p3d_nodepath.setDepthTest(False)
                self.p3d_nodepath.setDepthWrite(False)
            else:
                self.p3d_nodepath.setBin("default", 0)
                self.p3d_nodepath.setDepthTest(True)
                self.p3d_nodepath.setDepthWrite(True)
        except NameError:       # if p3d_nodepath is not yet defined
            print("NameError in set_render_above_all()")

    def remove(self):
        """ """
        self.p3d_nodepath.removeNode()

    def setPos(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setPos(*args, **kwargs)

    def getPos(self):
        """ """
        return self.p3d_nodepath.getPos()

    def setMat(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setMat(*args, **kwargs)

    def getMat(self):
        """ """
        return self.p3d_nodepath.getMat()

    def setTexture(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setTexture(*args, **kwargs)

    def setColor(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setColor(*args, **kwargs)

    def setTwoSided(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setTwoSided(*args, **kwargs)

    def setRenderModeWireframe(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setRenderModeWireframe(*args, **kwargs)

    def reparentTo(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.reparentTo(*args, **kwargs)

    def node(self):
        """ """
        return self.p3d_nodepath.node()

    def setRenderModeFilled(self):
        """ """
        return self.p3d_nodepath.setRenderModeFilled()

    def setLightOff(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setLightOff(*args, **kwargs)

    def show(self):
        """ """
        return self.p3d_nodepath.show()

    def hide(self):
        """ """
        return self.p3d_nodepath.hide()

    def setRenderModeThickness(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setRenderModeThickness(*args, **kwargs)

    def removeNode(self):
        """ """
        return self.p3d_nodepath.removeNode()

    def setHpr(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setHpr(*args, **kwargs)

    def showBounds(self):
        """ """
        return self.p3d_nodepath.showBounds()

    def setCollideMask(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setCollideMask(*args, **kwargs)

    def getParent(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.getParent(*args, **kwargs)

    def wrtReparentTo(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.wrtReparentTo(*args, **kwargs)

    def setBin(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setBin(*args, **kwargs)

    def setDepthTest(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setDepthTest(*args, **kwargs)

    def setDepthWrite(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setDepthWrite(*args, **kwargs)

    def get_children(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.get_children(*args, **kwargs)

    def attachNewNode(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.attachNewNode(*args, **kwargs)

    def lookAt(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.lookAt(*args, **kwargs)

    def setLight(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setLight(*args, **kwargs)

    def setAntialias(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setAntialias(*args, **kwargs)


class TQLoader:
    """ """
    def __init__(self, p3d_loader):
        """ """
        self.p3d_loader = p3d_loader
        pass

    def loadModel(self, *args, **kwargs):
        """ wrapper for p3d's loader.loadModel(...) """
        return self.p3d_loader.loadModel(*args, **kwargs)


tq_render = None
tq_aspect2d = None
tq_loader = None

def prepare_engine(p3d_render, p3d_aspect2d, loader):
    """ """
    global tq_render
    global tq_aspect2d
    global tq_loader
    tq_render = TQGraphicsNodePath.from_p3d_nodepath(render)
    tq_aspect2d = TQGraphicsNodePath.from_p3d_nodepath(aspect2d)
    tq_loader = TQLoader(loader)
