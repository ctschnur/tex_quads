from simple_objects.simple_objects import Line2dObject, PointPrimitive, Point3d, Point2d, ArrowHead, Line1dSolid, Line1dDashed, ArrowHeadCone, ArrowHeadConeShaded, OrientedDisk, OrientedCircle, Fixed2dLabel

from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Point2, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight, Vec3
from sequence.sequence import Sequence

import queue

from plot_utils.quad import Quad

import numpy as np

import time


from sequence.sequence import Sequence

from plot_utils.quad import Quad

from plot_utils.symbols.waiting_symbol import WaitingSymbol

from simple_objects.simple_objects import Fixed2dLabel

import engine
from engine.tq_graphics_basics import TQGraphicsNodePath


class ProcessingBox(TQGraphicsNodePath):
    """ an individual box with text, position, loading symbol, elapsed time since start e"""

    def __init__(self, is_done_function, description):
        self.description = description

        self.x_pos_left_border = None
        self.y_pos_top_box = None

        self.is_done_function = is_done_function

        self.time_initial = time.time_ns()

        self.task_obj_update = None

        self.waiting_symbol = None

        self.text = None

        self.elapsed_time_text = None

        self.quad = None

        self.task_obj_update = None

        self.task_obj_update = taskMgr.add(self.update_task, 'update_task')

        self.height = None

        self.width = None

        if self.height is None:
            self.height = 0.2

        if self.width is None:
            self.width = 0.9

        TQGraphicsNodePath.__init__(self)

        pass

    def set_xy_pos(self, x_pos_left_border, y_pos_top_box):
        """ """
        self.x_pos_left_border = x_pos_left_border
        self.y_pos_top_box = y_pos_top_box


    def update(self):
        if self.is_done_function() == False:
            if self.x_pos_left_border is None:
                self.x_pos_left_border = -1.0

            x_pos_waiting_symbol = self.x_pos_left_border + 0.1

            x_pos_text = x_pos_waiting_symbol + 0.2

            if self.y_pos_top_box is None:
                self.y_pos_top_box = 0.

            y_pos_waiting_symbol = self.y_pos_top_box - 0.05

            y_pos_text = self.y_pos_top_box - 0.125

            x_pos_elapsed_time = x_pos_text + 0.4
            y_pos_elapsed_time = y_pos_text

            quad_thickness = 2.0

            if self.waiting_symbol is None:
                self.waiting_symbol = WaitingSymbol(self.is_done_function, Vec3(x_pos_waiting_symbol, 0., y_pos_waiting_symbol), size=0.1)
                self.waiting_symbol.reparentTo(self)
            else:
                self.waiting_symbol.set_position(Vec3(x_pos_waiting_symbol, 0., y_pos_waiting_symbol))

            if self.text is None:
                self.text = Fixed2dLabel(text=self.description, font="fonts/arial.egg", x=x_pos_text, y=y_pos_text)
                self.text.reparentTo(self)
            else:
                self.text.setPos(x_pos_text, y_pos_text)

            if self.elapsed_time_text is None:
                self.elapsed_time_text = Fixed2dLabel(text="elapsed time", font="fonts/arial.egg", x=x_pos_elapsed_time, y=y_pos_elapsed_time)
                self.elapsed_time_text.reparentTo(self)
            else:
                self.elapsed_time_text.setPos(x_pos_elapsed_time, y_pos_elapsed_time)

            elapsed_time = (time.time_ns() - self.time_initial) / 1.0e9
            self.elapsed_time_text.setText("{0:.0f} s".format(elapsed_time))

            if self.quad is None:
                self.quad = Quad(thickness=quad_thickness, TQGraphicsNodePath_creation_parent_node=engine.tq_graphics_basics.tq_aspect2d)
                self.quad.reparentTo(self)

                self.quad.set_pos_vec3(Vec3(self.x_pos_left_border, 0., self.y_pos_top_box))

                self.quad.set_height(self.height)
                self.quad.set_width(self.width)
            else:
                self.quad.set_pos_vec3(Vec3(self.x_pos_left_border, 0., self.y_pos_top_box))

            return True  # call task.cont

        return False  # call task.done

    def update_task(self, task):
        """ This updates it's position, checks if the task is done, and if it is, removes the Processing Box """

        ret = self.update()
        if ret == True:
            return task.cont

        self.remove()
        return task.done

    def _is_done(self):
        """ check the is_done_function """
        return self.is_done_function()

    def get_height(self):
        return self.height

    def get_width(self):
        return self.width

    def remove(self):
        taskMgr.remove(self.task_obj_update)

        if self.waiting_symbol:
            self.waiting_symbol.remove()

        if self.text:
            self.text.remove()

        if self.elapsed_time_text:
            self.elapsed_time_text.remove()

        if self.quad:
            self.quad.remove()


class UIThreadLoggerElement(TQGraphicsNodePath):
    """ holds description, is_alive_func for a single parallel task,
    encapsulates also the ProcessingBox """

    def __init__(self, description, is_alive_func):
        """ when launching a thread, this logger can be called with
        Args:
            description: a description of the task that the thread is doing
            is_alive_func: if return value turns from True to False,
                           kill the log """
        self.description = description
        self.is_alive_func = is_alive_func

        TQGraphicsNodePath.__init__(self)

        self.processing_box = ProcessingBox(lambda: not is_alive_func(), description)
        self.processing_box.reparentTo(self)


# global uiThreadLogger
uiThreadLogger = None

class UIThreadLogger(TQGraphicsNodePath):
    """ A visual queue/cue of which threads are processing in parallel and what they are doing
    (e.g. loading or recording an audio file in the background) """

    def __init__(self):
        """
        """
        self.log_list = []

        self.task_obj_update = None

        self.task_obj_update = taskMgr.add(self.update, 'update')

        TQGraphicsNodePath.__init__(self)



    def append_new_parallel_task(self, description, is_alive_func):
        """ when launching a thread, this logger can be called with
        Args:
            description: a description of the task that the thread is doing
            is_alive_func: if return value turns from True to False,
                           kill the log """
        # pb = ProcessingBox(my_done_function)
        _ = UIThreadLoggerElement(description, is_alive_func)
        _.reparentTo(self)
        self.log_list.append(_)

    def update(self, task):
        """ updates the visual queue:
        - check if any of the queue's UIThreadLoggerElements is_alive_func returns false
        - calculates and applies the positions to the boxes in the queue """

        from conventions.conventions import win_aspect_ratio

        x_start_pos = -1.0 * win_aspect_ratio + 0.05
        y_start_pos = -0.75
        y_spacing = 0.05

        copy_log_list = self.log_list.copy()

        reduced_copy_log_list = list(filter(lambda el: el.is_alive_func(), copy_log_list))

        self.log_list = reduced_copy_log_list

        # x_accumulated = x_start_pos
        y_accumulated = y_start_pos

        for i, uitle in enumerate(self.log_list):
            # uitle = UIThreadLoggerElement()

            # x_accumulated += y_spacigng + uitle.processing_box.get_height()

            uitle.processing_box.set_xy_pos(x_start_pos, y_accumulated)
            y_accumulated += y_spacing + uitle.processing_box.get_height()

        return task.cont

    def remove(self):
        taskMgr.remove(self.task_obj_update)
        pass


    # def get_pos_of_next_processing_box(self):
    #     """ when processing boxes are added or are sliding down
    #     as some end, this function is used to set the """
