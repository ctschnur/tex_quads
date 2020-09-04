from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain
from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle
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
# import gltf

from cameras.Orbiter import Orbiter

from direct.task import Task

from plot_utils.bezier_curve import BezierCurve, DraggableBezierCurve, SelectableBezierCurve

from panda3d.core import CollisionTraverser, CollisionHandlerQueue, CollisionRay, CollisionNode, GeomNode, BitMask32, VBase4

from plot_utils.graph import Graph, DraggableGraph, GraphHoverer


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.setFrameRateMeter(True)
        render.setAntialias(AntialiasAttrib.MAuto)

        ob = Orbiter(base.cam, radius=3.)
        cs = CoordinateSystem(ob)

        # ob.set_view_to_yz_plane()
        ob.set_view_to_xy_plane()

        from simple_objects.simple_objects import Pinned2dLabel


        import matplotlib.pyplot as plt
        import networkx as nx

        hd = "H" + chr(252) + "sker D" + chr(252)
        mh = "Mot" + chr(246) + "rhead"
        mc = "M" + chr(246) + "tley Cr" + chr(252) + "e"
        st = "Sp" + chr(305) + "n" + chr(776) + "al Tap"
        q = "Queensr" + chr(255) + "che"
        boc = "Blue " + chr(214) + "yster Cult"
        dt = "Deatht" + chr(246) + "ngue"

        G = nx.Graph()
        G.add_edge(hd, mh)
        G.add_edge(mc, st)
        G.add_edge(boc, mc)
        G.add_edge(boc, dt)
        G.add_edge(st, dt)
        G.add_edge(q, st)
        G.add_edge(dt, mh)
        G.add_edge(st, mh)

        dg = DraggableGraph(ob)
        gh = GraphHoverer(dg, ob)

        print("hi")


app = MyApp()
app.run()
