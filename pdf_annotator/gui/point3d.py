from panda3d.core import Vec3, Vec4

from composed_objects.composed_objects import GroupNode

from plot_utils.pdf_renderer import PDFPageTextureObject, PopplerPDFRenderer

import numpy as np

from engine.tq_graphics_basics import TQGraphicsNodePath

from cameras.panner2d import Panner2d

from plot_utils.quad import Quad

from pdf_viewer.tools import PDFViewer, PDFPanner2d

from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d


class Point3dCGPanner(Point3d):
    """ Point3d for a Panner view"""
    def __init__(self, cg_panner2d, **kwargs):
        Point3d.__init__(self, **kwargs)

        self.cg_panner2d = cg_panner2d

        self.scale_factor = self.getScale()

        self.cg_panner2d_initial_view_distance = self.cg_panner2d.view_distance

        self.cg_panner2d.add_camera_move_hook(self._adjust)

        # self.move_ctr = 0.

        self._adjust()

    def _adjust(self):
        # self.move_ctr += 1.

        # self.cg_panner2d_scale = self.getScale()

        # print("camera move", self.move_ctr)
        # print("view_distance", self.cg_panner2d.view_distance)
        # print("self.cg_panner2d_initial_view_distance", self.cg_panner2d_initial_view_distance)

        # scale = self.getScale()

        self.setScale(self.scale_factor * self.cg_panner2d.view_distance/self.cg_panner2d_initial_view_distance)

        # self.setScale()
