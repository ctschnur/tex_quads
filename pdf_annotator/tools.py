from panda3d.core import Vec3, Vec4

from composed_objects.composed_objects import GroupNode

from plot_utils.pdf_renderer import PDFPageTextureObject, PopplerPDFRenderer

import numpy as np

from engine.tq_graphics_basics import TQGraphicsNodePath

from cameras.panner2d import Panner2d

from plot_utils.quad import Quad

from pdf_viewer.tools import PDFViewer, PDFPanner2d

from plot_utils.DraggableResizableDrawableOnFrame import DraggableResizableDrawableOnFrame

class PDFAnnotator(PDFViewer):
    """ includes the p3d_camera and rendering functionality for annotating a pdf """
    left_margin_width = 2.5
    right_margin_width = 2.5

    def __init__(self, pdf_panner2d, pdf_filepath, *args, **kwargs):

        self.drawing_frames = []

        PDFViewer.__init__(self, pdf_panner2d, pdf_filepath, *args, **kwargs)

        # self.pptos = []

    # def get_page_width(self, page_num):
    #     x_size, y_size = self.pptos[page_num].get_size()
    #     return x_size

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

            self.pptos.append(ppto)

            drawing_frame = DraggableResizableDrawableOnFrame(self.pdf_panner2d, height=0.2, width=0.7, quad_border_thickness=10.)
            # drawing_frame.reparentTo(self)

            drawing_frame.attach_to_render()
            # drawing_frame.setPos(Vec3(-1., -0.5, 1.))
            drawing_frame.bg_quad.setColor(Vec4(1., 1., 1., 0.0), 1)
            drawing_frame.bg_quad.set_border_color(Vec4(1., 0., 0., 1.0), 1)
            drawing_frame.setPos(Vec3(-1., -0.5, 1.))

            ppto.setPos(Vec3(x, 0., y))
            drawing_frame.setPos(Vec3(x-self.left_margin_width, 0., y+y_size))
            drawing_frame.set_height(y_size)
            drawing_frame.set_width(x_size + self.left_margin_width + self.right_margin_width)

            self.drawing_frames.append(drawing_frame)



        self.render_background_graphics()
