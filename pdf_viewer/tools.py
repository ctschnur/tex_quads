from panda3d.core import Vec3, Vec4

from composed_objects.composed_objects import GroupNode

from plot_utils.pdf_renderer import PDFPageTextureObject, PopplerPDFRenderer

import numpy as np

from engine.tq_graphics_basics import TQGraphicsNodePath

from cameras.panner2d import Panner2d

from plot_utils.quad import Quad

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

    upper_scroll_margin = 1.

    margins_quad_pos_0 = Vec3(0., 1., 0.)

    filmsize_x_0 = 1.
    filmsize_y_0 = 1.

    drawing_mode_1_width = 15.  # in this drawing mode, you have huge margins in wich to draw and put derivations
    # TODO: make a drawing mode 2, where you exit those margins, this makes navigation a bit more messy, but you have
    # infinite margins

    drawing_mode_1_top_margin = 2.
    drawing_mode_1_bottom_margin = 2.


    def __init__(self, pdf_panner2d, pdf_filepath, *args, **kwargs):
        TQGraphicsNodePath.__init__(self, *args, **kwargs)

        # logical variables
        self.pdf_filepath = pdf_filepath
        self.pptos = []
        self.y_pages_distance = PDFViewer.y_pages_distance_0

        # derived
        self.pdf_panner2d = pdf_panner2d  # something like Panner2d
        self.ppr = PopplerPDFRenderer(self.pdf_filepath)

        # direct objects
        base.accept('1', self.return_to_middle_view)
        base.accept('space', self.scroll_spacebar_down)
        base.accept('shift-space', self.scroll_spacebar_up)

        base.accept('control-0', self.return_to_middle_view)


        # quad visualizing large margins for visual orientation
        self.margins_quad = Quad(thickness=10.)
        self.margins_quad.reparentTo(self)

        # plot
        self.render_pages()

        self.return_to_middle_view()

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
        filmsize_x, filmsize_y = self.pdf_panner2d.get_filmsize_with_window_active()
        self.pdf_panner2d.x[1]

        old_pos = self.pdf_panner2d.x[1]
        pos_step_try = direction_sign * (filmsize_y - PDFViewer.spacebar_scroll_overlap)
        new_pos = np.clip(old_pos + pos_step_try, -self.get_total_view_height(), -PDFViewer.upper_scroll_margin)  # clip(val, min, max)

        actual_pos_step = new_pos - old_pos

        # clip to not run off
        self.pdf_panner2d.x[1] += actual_pos_step
        self.pdf_panner2d.p_previous_offset[1] -= actual_pos_step

        self.pdf_panner2d.update_camera_state()
        self.pdf_panner2d.set_lookat_after_updated_camera_pos()
        self.pdf_panner2d.update_film_size_from_view_distance()

    def return_to_middle_view(self):
        """ scroll so that the pdf is centered again """
        assert len(self.pptos) > 0

        first_page_width = self.pptos[0].get_size()[0]

        filmsize_x, filmsize_y = self.pdf_panner2d.get_filmsize_with_window_active()

        x_val = first_page_width/2.
        self.pdf_panner2d.x[0] = x_val
        self.pdf_panner2d.p_previous_offset[0] = -x_val

        self.pdf_panner2d.update_camera_state()
        self.pdf_panner2d.set_lookat_after_updated_camera_pos()
        self.pdf_panner2d.update_film_size_from_view_distance()

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

        self.render_background_graphics()

    def render_background_graphics(self):
        width = PDFViewer.drawing_mode_1_width
        height = self.get_total_view_height() + PDFViewer.drawing_mode_1_top_margin + PDFViewer.drawing_mode_1_bottom_margin

        self.margins_quad.set_height(height)
        self.margins_quad.set_width(width)

        # self.margins_quad.setPos(PDFViewer.margins_quad_pos_0)
        self.margins_quad.setColor(Vec4(1., 0., 0., 0.3), 1)
        self.margins_quad.b2d.setColor(Vec4(1., 1., 1., 0.9), 1)

        first_page_width = self.pptos[0].get_size()[0]

        self.margins_quad.setPos(-width/2. + first_page_width/2., PDFViewer.margins_quad_pos_0[1], PDFViewer.drawing_mode_1_top_margin)

    def calculate_mean_width(self):
        x_sizes = []
        for i, ppto in enumerate(self.pptos):
            x_size, y_size = ppto.get_size()
            x_sizes.append(x_size)

        return np.sum(x_sizes)/len(x_sizes)

    # def calculate_drawing_mode_1_width(self):
    #     x_sizes = []
    #     for i, ppto in enumerate(self.pptos):
    #         x_size, y_size = ppto.get_size()
    #         x_sizes.append(x_size)

    #     return np.max(x_sizes)
