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


class GraphicsObject:
    """ Anything that fundamentally is a only a graphics object in this engine should have these properties. """

    def __init__(self, **kwargs):
        self.nodePath_creation_parent_node = None

        if 'nodePath_creation_parent_node' in kwargs:
            self.nodePath_creation_parent_node = kwargs.get(
                'nodePath_creation_parent_node')
        else:
            self.nodePath_creation_parent_node = render

        self.set_parent_node_for_nodePath_creation(
            self.nodePath_creation_parent_node)

        pass

    def set_parent_node_for_nodePath_creation(self, nodePath_creation_parent_node: NodePath):
        """ when calling attachNewNode, a p3d NodePath is generated.
        E.g.: To attach a line to render (3d world) is different than attaching
        it to aspect2d (2d GUI plane), since the aspect2d children are not directly
        affected by camera movements
        Args:
        - nodePath_creation_parent_node : the NodePath to attach the GraphicsObject to
                                          (e.g. render or aspect2d in p3d)
        """

        # self.set_parent_node_for_nodePath_creation(self.nodePath_creation_parent_node)
        self.nodePath_creation_parent_node = nodePath_creation_parent_node

    def get_parent_node_for_nodePath_creation(self):
        return self.nodePath_creation_parent_node