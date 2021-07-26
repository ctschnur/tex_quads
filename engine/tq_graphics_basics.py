from direct.showbase.ShowBase import ShowBase

from panda3d.core import (
    Vec3,
    Vec4,
    TransparencyAttrib,
    AntialiasAttrib,
    NodePath,
    Mat4,
    Mat3,
    LVecBase4f)

from direct.interval.IntervalGlobal import Wait, Sequence
from direct.interval.LerpInterval import LerpFunc

import numpy as np

from local_utils import math_utils

import engine.tq_graphics_basics

def init_engine(p3d_render, p3d_aspect2d, loader):
    """ """
    global tq_render
    global tq_aspect2d
    global tq_loader
    tq_render = TQGraphicsNodePath.from_p3d_nodepath(render)
    tq_aspect2d = TQGraphicsNodePath.from_p3d_nodepath(aspect2d)
    tq_loader = TQLoader(loader)

    global _screen_size_x
    global _screen_size_y
    _screen_size_x = base.win.getProperties().getXSize()
    _screen_size_y = base.win.getProperties().getYSize()

    global _window_size_x
    global _window_size_y
    _window_size_x = base.pipe.getDisplayWidth()
    _window_size_y = base.pipe.getDisplayHeight()


def get_screen_size_x():
    """ """
    return base.pipe.getDisplayWidth()

def get_screen_size_y():
    """ """
    return base.pipe.getDisplayHeight()

def get_window_size_x():
    """ """
    return base.win.getProperties().getXSize()

def get_window_size_y():
    """ """
    return base.win.getProperties().getYSize()

def get_window_aspect_ratio():
    """ """
    return get_window_size_x()/get_window_size_y()

def get_pts_to_p3d_units(num_of_pt):
    """ define 1 p3d unit be 100/pt_to_height_p3d_scale num_of_pt """
    pt_to_height_p3d_scale = 0.6
    return pt_to_height_p3d_scale * float(num_of_pt)/(100.)

def get_font_bmp_pixels_from_height(height):
    """ 10 pixels from height of 0.1
        the aspect2d viewport goes in the up direction from -1 to 1 -> range of 2 """
    pixels_per_p3d_length_unit = engine.tq_graphics_basics.get_window_size_y()/2.0
    return pixels_per_p3d_length_unit * height  # how many pixels

class TQGraphicsNodePath:
    """ Anything that fundamentally is a only a graphics object in this engine should have these properties.

    Kwargs:
        TQGraphicsNodePath_creation_parent_node : this is assigned in the constructor, and after makeObject and the return of
        the p3d Nodepath, each TQGraphicsNodePath object has to call set_p3d_node """

    def __init__(self, **kwargs):
        """ """
        self.TQGraphicsNodePath_creation_parent_node = None
        self.p3d_nodepath = NodePath("empty")
        self.p3d_nodepath_changed_post_init_p = False
        self.p3d_parent_nodepath = NodePath("empty")

        self.node_p3d = None

        self.p3d_nodepath.reparentTo(self.p3d_parent_nodepath)

        self.apply_kwargs(**kwargs)

    def apply_kwargs(self, **kwargs):
        """ """
        if 'color' in kwargs:
            TQGraphicsNodePath.setColor(self, kwargs.get('color'))
        else:
            TQGraphicsNodePath.setColor(self, Vec4(1., 1., 1., 1.))


    def make_groupnode(self):
        """ this makes this TQGraphicsNodePath a pure group node (includes transformations, ...) and applies them to it's children """
        self._set_p3d_nodepath_plain_post_init(NodePath("groupnode"))

    def attach_to_render(self):
        """ """
        # assert self.p3d_nodepath
        # self.p3d_nodepath.reparentTo(render)
        assert self.p3d_nodepath
        self.reparentTo(engine.tq_graphics_basics.tq_render)

    def attach_to_aspect2d(self):
        """ """
        # assert self.p3d_nodepath
        # self.p3d_nodepath.reparentTo(aspect2d)
        assert self.p3d_nodepath
        self.reparentTo(engine.tq_graphics_basics.tq_aspect2d)

    def _set_p3d_nodepath_plain_post_init(p3d_nodepath):
        """ """
        self.p3d_nodepath = p3d_nodepath
        self.p3d_nodepath_changed_post_init_p = True

    @staticmethod
    def from_p3d_nodepath(p3d_nodepath, **tq_graphics_nodepath_kwargs):
        """ factory """
        go = TQGraphicsNodePath(**tq_graphics_nodepath_kwargs)
        go.set_p3d_nodepath(p3d_nodepath)
        return go

    def set_parent_node_for_nodepath_creation(
            self, TQGraphicsNodePath_creation_parent_node):
        """ when calling attachNewNode_p3d, a new node pat is generated.
        E.g.: To attach a line to render (3d world) is different than attaching
        it to aspect2d (2d GUI plane), since the aspect2d children are not directly
        affected by camera movements
        Args:
        - TQGraphicsNodePath_creation_parent_node : the NodePath to attach the TQGraphicsNodePath to
                                          (e.g. render or aspect2d in p3d)
        """

        # self.set_parent_node_for_nodepath_creation(self.TQGraphicsNodePath_creation_parent_node)
        self.TQGraphicsNodePath_creation_parent_node = TQGraphicsNodePath_creation_parent_node

    def set_p3d_nodepath(self, p3d_nodepath, remove_old_nodepath=True):
        """ """
        self.p3d_nodepath = p3d_nodepath

    def get_p3d_nodepath(self):
        """ """
        return self.p3d_nodepath

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

    def setScale(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setScale(*args, **kwargs)

    def getScale(self):
        """ """
        return self.p3d_nodepath.getScale()

    def setMat(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setMat(*args, **kwargs)

    def setMat_normal(self, mat4x4_normal_np):
        """ normal convention (numpy array), i.e. convert to forrowvecs convention for p3d setMat call """
        return self.p3d_nodepath.setMat(math_utils.to_forrowvecs(mat4x4_normal_np))


    def getMat(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.getMat(*args, **kwargs)

    def getMat_normal(self, *args, **kwargs):
        """ """
        return math_utils.from_forrowvecs(self.p3d_nodepath.getMat(*args, **kwargs))

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
        new_args = list(args)
        new_args[0] = new_args[0].p3d_nodepath
        return self.p3d_nodepath.reparentTo(*new_args, **kwargs)

    def reparentTo_p3d(self, *args, **kwargs):
        """ input a p3d nodepath directly """
        # new_args = list(args)
        # new_args[0] = new_args[0].p3d_nodepath
        return self.p3d_nodepath.reparentTo(*args, **kwargs)

    def get_node_p3d(self):
        """ """
        # return self.p3d_nodepath.node()
        return self.node_p3d

    def set_node_p3d(self, node_p3d):
        """ not available in p3d NodePath class """
        self.node_p3d = node_p3d

    def setRenderModeFilled(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setRenderModeFilled(*args, **kwargs)

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

    def getParent_p3d(self, *args, **kwargs):
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

    def get_children_p3d(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.get_children(*args, **kwargs)

    def attachNewNode_p3d(self, *args, **kwargs):
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

    def getRelativeVector(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.getRelativeVector(*args, **kwargs)

    def setTransparency(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setTransparency(*args, **kwargs)

    def getHpr(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.getHpr(*args, **kwargs)

    def setHpr(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.setHpr(*args, **kwargs)

    def getTightBounds(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.getTightBounds(*args, **kwargs)

    def showTightBounds(self, *args, **kwargs):
        """ """
        return self.p3d_nodepath.showTightBounds(*args, **kwargs)


class TQLoader:
    """ """
    def __init__(self, p3d_loader):
        """ """
        self.p3d_loader = p3d_loader
        pass

    def loadModel(self, *args, **kwargs):
        """ wrapper for p3d's loader.loadModel(...) """
        return self.p3d_loader.loadModel(*args, **kwargs)
