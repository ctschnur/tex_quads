from conventions import conventions

from simple_objects import custom_geometry
from local_utils import texture_utils

from latex_objects.latex_expression_manager import LatexImageManager, LatexImage

from engine.tq_graphics_basics import TQGraphicsNodePath


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

class Polygon2d(TQGraphicsNodePath):
    def __init__(self, point_cloud, **kwargs):
        TQGraphicsNodePath.__init__(self, **kwargs)

        self.makeObject(point_cloud)

    def makeObject(self, point_cloud):
        self.node = custom_geometry.create_colored_polygon2d_GeomNode_from_point_cloud(
            point_cloud,
            color_vec4=Vec4(1., 1., 1., 1.))
        self.set_p3d_nodepath(self.get_parent_node_for_nodepath_creation().attachNewNode(self.node))


class Polygon2dTestTriangles(TQGraphicsNodePath):
    def __init__(self, symbol_geometries, **kwargs):
        TQGraphicsNodePath.__init__(self, **kwargs)

        self.makeObject(symbol_geometries)

    def makeObject(self, symbol_geometries):
        self.node = custom_geometry.create_GeomNode_Simple_Polygon_with_Hole(symbol_geometries)
        # self.node = custom_geometry.create_GeomNode_Simple_Polygon_without_Hole(symbol_geometries)

        self.set_p3d_nodepath(self.get_parent_node_for_nodepath_creation().attachNewNode(self.node))


class Polygon2dTestLineStrips(TQGraphicsNodePath):
    def __init__(self, symbol_geometries, **kwargs):
        TQGraphicsNodePath.__init__(self, **kwargs)

        self.makeObject(symbol_geometries)

    def makeObject(self, symbol_geometries):
        self.node = custom_geometry.create_GeomNode_Simple_Polygon_with_Hole_LineStrips(symbol_geometries)

        self.set_p3d_nodepath(self.get_parent_node_for_nodepath_creation().attachNewNode(self.node))
        self.setRenderModeWireframe()
