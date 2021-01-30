from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Vec3,
    Vec4,
    TransparencyAttrib,
    AntialiasAttrib,
    NodePath,
    Mat4,
    Mat3,
    Point3,
    Point2)
from direct.interval.IntervalGlobal import Wait, Sequence
from direct.interval.LerpInterval import LerpFunc

import hashlib
import numpy as np
import sys
import os

from engine.tq_graphics_basics import TQGraphicsNodePath
import engine.tq_graphics_basics
from local_utils import math_utils, texture_utils

from conventions import conventions
from simple_objects import custom_geometry

import threading
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt

class TextureOfMatplotlibFigure(TQGraphicsNodePath):
    """ """

    def __init__(self, mpl_figure, scaling=1.0, backgroud_opacity=0.2, **kwargs):
        """ get a textured quad from a 2d array of pixel data """
        # self.np_2d_arr = np_2d_arr
        self.myTexture = None
        self.num_of_pixels_x = None
        self.num_of_pixels_y = None
        self.scaling = scaling
        self.backgroud_opacity = backgroud_opacity

        self.mpl_figure = mpl_figure

        TQGraphicsNodePath.__init__(self, **kwargs)

        self.makeObject()

        self.doInitialSetupTransformation()

    def doInitialSetupTransformation(self):
        """ initial setup transformation: a unit quad with an image in the
        background is being scaled so that the pixel height and width fits
        exactly with the screen resolution"""

        self.setMat_normal(
            self.get_scaling_matrix()
        )

    def get_scaling_matrix(self):
        """ """
        return (
            conventions.getMat4_scale_unit_quad_to_image_aspect_ratio(
                self.num_of_pixels_x, self.num_of_pixels_y)
            .dot(
                conventions.getMat4_scale_quad_for_texture_pixels_to_match_screen_resolution()
            )
            .dot(math_utils.getScalingMatrix4x4(self.scaling, self.scaling, self.scaling))
        )

    def get_dimensions_from_calc(self):
        """ return the width and height of the textured quad in p3d coordinates """
        _ = np.abs(np.diag(self.get_scaling_matrix()))
        return _[0], _[2]       # in p3d aspect2d, x is to the right, z is up

    def makeObject(self):
        """ only creates geometry (doesn't transform it) """
        self.set_node_p3d(custom_geometry.createTexturedUnitQuadGeomNode())
        self.set_p3d_nodepath(
            self.getParent_p3d().attachNewNode(self.get_node_p3d()))

        self._set_texture(update_full=True)

        self.setTransparency(TransparencyAttrib.MAlpha)

        self.setTwoSided(True)
        self.setLightOff(True)

    def _setup_figure_for_tex_quads_convention(self):
        """ """
        fig_axes = self.mpl_figure.get_axes()

        # make background transparent (of all axes)
        self.mpl_figure.patch.set_alpha(self.backgroud_opacity)

        for ax in fig_axes:
            ax.patch.set_alpha(self.backgroud_opacity)

        default_color_for_borders_and_labels = "white"

        for ax, color in zip(fig_axes,
                             [default_color_for_borders_and_labels] * len(fig_axes)):
            ax.tick_params(color=color, labelcolor=color)
            for spine in ax.spines.values():
                spine.set_edgecolor(color)

    def _generate_and_set_texture(self):
        """ """
        self.myTexture, self.num_of_pixels_x, self.num_of_pixels_y = (
            texture_utils.getTextureFromMatplotlibFigure(
                self.mpl_figure,
                flip_over_y_axis=True,
                # make_white_transparent=True
                # backgroud_opacity=self.backgroud_opacity
            ))

        # self.myTexture.setMagfilter(SamplerState.FT_nearest)
        # self.myTexture.setMinfilter(SamplerState.FT_nearest)
        self.setTexture(self.myTexture, 1)

    def _set_texture(self, update_full=False, tight_layout=False):
        """ """
        if update_full == True:
            self._setup_figure_for_tex_quads_convention()

        if tight_layout == True:
            if self.mpl_figure:
                self.mpl_figure.tight_layout()

        self._generate_and_set_texture()

    def update_figure_texture(self, update_full=False, tight_layout=False):
        """ """
        # preserve the matrices of rotation and position
        pos = self.getPos()
        rot = self.getHpr()

        self._set_texture(update_full=update_full, tight_layout=tight_layout)

        self.setPos(pos)
        self.setHpr(rot)

class RotatingMatplotlibFigure(TQGraphicsNodePath):
    """ A matplotlib figure is being continuously generated and updated, then
    loaded onto a texture while the viewing angle is changed """

    def __init__(self, fig=None):
        """ """
        TQGraphicsNodePath.__init__(self)

        self.fig = None
        if fig is not None:
            self.fig = fig
        else:
            fig = plt.figure(figsize=(5, 5))

        tmplf = TextureOfMatplotlibFigure(fig, scaling=1.0, backgroud_opacity=0.0)
        tmplf.attach_to_aspect2d()

        width, height = tmplf.get_dimensions_from_calc()
        tmplf.setPos(Vec3(1.0 * engine.tq_graphics_basics.get_window_aspect_ratio() - width, 0., -1.))

        self.angle = 0.
        self.ax = fig.add_subplot(111, projection='3d')

        def add_plot_thread_wrapped():
            """ """
            td = threading.Thread(target=self.add_plot, daemon=True)
            td.start()

            def wait_for_thread_to_finish_task(task):
                """ """
                if td.is_alive():
                    return task.cont

                self.ax.w_xaxis.line.set_color("white")
                self.ax.w_yaxis.line.set_color("white")
                self.ax.w_zaxis.line.set_color("white")

                tmplf.update_figure_texture(update_full=True, # tight_layout=True
                )
                # base.acceptOnce("c", add_plot_thread_wrapped)

                # time.sleep(0.2)
                # Wait(0.001)
                add_plot_thread_wrapped()

                return task.done

            taskMgr.add(wait_for_thread_to_finish_task, 'foo')

        add_plot_thread_wrapped()

    def add_plot(self):
        """ """
        self.ax.cla()

        # make the panes transparent
        self.ax.xaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        self.ax.yaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))
        self.ax.zaxis.set_pane_color((1.0, 1.0, 1.0, 0.0))

        # self.ax.plot(x, random_polynomial(x))

        # fig = plt.figure()
        # ax = fig.add_subplot(111, projection='3d')

        # Grab some test data.
        X, Y, Z = axes3d.get_test_data(0.05)

        u = np.linspace(0, 2 * np.pi, 100)
        v = np.linspace(0, np.pi, 100)
        x = 10 * np.outer(np.cos(u), np.sin(v))
        y = 10 * np.outer(np.sin(u), np.sin(v))
        z = 10 * np.outer(np.ones(np.size(u)), np.cos(v))

        # Plot the surface

        # Plot a basic wireframe.
        self.ax.plot_wireframe(X, Y, Z, rstride=10, cstride=10)
        self.angle += 0.75 * 1.
        self.ax.view_init(30, self.angle)
