from panda3d.core import Vec3

from composed_objects.composed_objects import GNodeClass

from plot_utils.pdf_renderer import PDFPageTextureObject, PopplerPDFRenderer

import numpy as np

from engine.tq_graphics_basics import TQGraphicsNodePath

from cameras.panner2d import Panner2d


class PDFPanner2d(Panner2d):
    """ own camera gear class """
    def __init__(self, *args, **kwargs):
        Panner2d.__init__(self, *args, **kwargs)

class PDFViewer(TQGraphicsNodePath):
    """ includes the p3d_camera and rendering functionality for viewing a pdf """

    y_pages_distance_0 = 0.1
    x_left_offset = 0.1
    y_top_offset = 0.1

    spacebar_scroll_overlap = 0.1

    upper_scroll_margin = 0.4

    def __init__(self, p3d_camera, pdf_filepath, *args, **kwargs):
        TQGraphicsNodePath.__init__(self, *args, **kwargs)

        # logical variables
        self.pdf_filepath = pdf_filepath
        self.pptos = []
        self.y_pages_distance = PDFViewer.y_pages_distance_0

        # derived
        self.pdf_panner2d = PDFPanner2d(base.cam)  # something like Panner2d
        self.ppr = PopplerPDFRenderer(self.pdf_filepath)

        # direct objects
        base.accept('1', self.set_initial_view)
        base.accept('space', self.scroll_spacebar_down)
        base.accept('shift-space', self.scroll_spacebar_up)

        # base.accept('-', self.zoom_general_control_minus)
        # base.accept('+', self.zoom_general_control_plus)

        base.accept('control-0', self.set_initial_view)


        # plot
        self.render_pages()

        # viewing
        self.set_initial_view()


    def zoom_general_control_minus(self):
        self.zoom_general(-1.)

    def zoom_general_control_plus(self):
        self.zoom_general(+1.)

    def zoom_general(self, direction_sign):
        """
        args:
            direction_sign: -1: scroll down, +1: scroll up """

        # print("zoom_general")

        # filmsize_x, filmsize_y = self.pdf_panner2d.get_filmsize()

        # print("filmsize_x, filmsize_y: ", filmsize_x, filmsize_y)

        # filmsize_x_new = (1. + direction_sign * 0.1) * filmsize_x
        # filmsize_y_new = (1. + direction_sign * 0.1) * filmsize_y

        # print("filmsize_x_new, filmsize_y_new: ", filmsize_x_new, filmsize_y_new)

        # self.pdf_panner2d.set_filmsize(filmsize_x_new, filmsize_y_new)
        # # self.pdf_panner2d.update_three()

        # self.pdf_panner2d.update_camera_pos()
        # self.pdf_panner2d.set_lookat_after_updated_camera_pos()




    def scroll_spacebar_down(self):
        self.scroll_spacebar(-1.)

    def scroll_spacebar_up(self):
        self.scroll_spacebar(+1.)

    def get_total_view_height(self):
        _sum = len(self.pptos) * self.y_pages_distance
        for ppto in self.pptos:
            if ppto is self.pptos[-1]:
                x_sizef, y_sizef = self.pptos[-1].get_size()
                _sum += y_sizef
                continue

            x_size, y_size = ppto.get_size()
            _sum += y_size

        return _sum

    def scroll_spacebar(self, direction_sign):
        """
        args:
            direction_sign: -1: scroll down, +1: scroll up """
        filmsize_x, filmsize_y = self.pdf_panner2d.get_filmsize()
        self.pdf_panner2d.x[1] += direction_sign * (filmsize_y - PDFViewer.spacebar_scroll_overlap)

        # clip to not run off
        self.pdf_panner2d.x[1] = np.clip(self.pdf_panner2d.x[1], -self.get_total_view_height(), -PDFViewer.upper_scroll_margin)  # clip(val, min, max)
        self.pdf_panner2d.update_three()

    def set_initial_view(self):
        """ go to first page, set position and zoom """
        # mean_width = self.calculate_mean_width()
        # print("calculate_mean_width:", mean_width)

        assert len(self.pptos) > 0

        x_size0, y_size0 = self.pptos[0].get_size()

        # if the pdf is rendered with the top left corner of the fist page at the origin

        # shift the view such that the origin sits at the upper left corner

        filmsize_x, filmsize_y = self.pdf_panner2d.get_filmsize()
        print("filmsize_x, filmsize_y: ", filmsize_x, filmsize_y)

        self.pdf_panner2d.x[0] = filmsize_x/2. - PDFViewer.x_left_offset
        self.pdf_panner2d.x[1] = - filmsize_y/2. + PDFViewer.y_top_offset

        self.pdf_panner2d.update_three()

    def get_page_width(self, page_num):
        x_size, y_size = self.pptos[page_num].get_size()
        return x_size

    def render_pages(self):
        for i in range(self.ppr.get_number_of_pages()):
            ppto = PDFPageTextureObject(i, self.ppr)
            ppto.reparentTo(self)

            pos_3d = ppto.getPos()
            x0 = pos_3d[0]
            y0 = pos_3d[2]  # since z is up in p3d and y is up in the 2d pdf convention here

            x_size, y_size = ppto.get_size()

            y = y0
            x = x0

            if i > 0:
                y -= self.y_pages_distance
            y -= (i + 1.) * y_size

            ppto.setPos(Vec3(x, 0., y))
            self.pptos.append(ppto)

    def calculate_mean_width(self):
        x_sizes = []
        for i, ppto in enumerate(self.pptos):
            x_size, y_size = ppto.get_size()
            x_sizes.append(x_size)

        return np.sum(x_sizes)/len(x_sizes)
