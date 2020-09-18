class GraphPlayer:
    """
        - Plot a play/pause text and toggle it with space
        - give it a graph and call playfrom(edge, t between 0 and 1).
        - Show a cursor (thicker, smaller)
    """

    def __init__(self, draggablegraph, cameragear):
        # self.play_p = False  # play is true, pause is false

        # register event for onmousemove
        self.draggablegraph = draggablegraph
        self.cameragear = cameragear
        # self.mouse = mouse

        # taskMgr.add(self.mouseMoverTask, 'mouseMoverTask')
        # base.accept('mouse1', self.onPress)

        # self.hoverindicatorpoint = Point3d()

        # self.shortest_distance_line = Line1dSolid(thickness=5, color=Vec4(1., 0., 1., 0.5))

        self.v1 = Vec3(0., 0., 0.)
        self.v2 = Vec3(2., 0., 0.)
        self.duration = 3.  # a relatively high number
        self.a = 0.  # a parameter between 0 and 1
        self.delay = 0.

        self.v_c = self.v1  # initially

        self.p1 = Point3d(scale=0.01, pos=self.v1)
        self.p2 = Point3d(scale=0.01, pos=self.v2)

        self.p_c = Point3d(scale=0.0125, pos=self.v1)
        self.p_c.setColor(((1., 0., 0., 1.), 1))

        self.l = Line1dSolid()
        self.l.setTailPoint(self.v1)
        self.l.setTipPoint(self.v2)

        self.extraArgs = [# self.duration,
                     self.v1, self.v2, self.v_c, # self.p1, self.p2,
            self.p_c]

        # self.p3d_interval = LerpFunc(
        #     GraphPlayer.update_position_func, duration=self.duration, extraArgs=self.extraArgs)
        # self.play_cursor_sequence = Sequence(Wait(self.delay), self.p3d_interval)
        self.play_cursor_sequence = None

        self.stopped_at_end = False
        self.stopped_at_beginning = True

        # self.starting_edge = list(self.draggablegraph.graph_edges)[3]
        # self.active_edge = self.starting_edge

        # self.starting_time = 0.
        # self.a = self.starting_time

        self.paused_cursor_color = ((1., 0., 0., 1.), 1)
        self.playing_cursor_color = ((0., 1., 0., 1.), 1)

        # -- init play/pause actions
        # register space key to toggle play/pause
        play_pause_toggle_direct_object = DirectObject.DirectObject()
        play_pause_toggle_direct_object.accept('space', self.toggle_play_pause)

        play_pause_toggle_direct_object = DirectObject.DirectObject()
        play_pause_toggle_direct_object.accept('arrow_left', self.set_short_forward)

        play_pause_toggle_direct_object = DirectObject.DirectObject()
        play_pause_toggle_direct_object.accept('arrow_right', self.set_right_forward)

        # init the textNode (there is one text node)
        self.play_pause_label = (
            Fixed2dLabel(text="paused", font="fonts/arial.egg", xshift=0.1, yshift=0.1))

        self.pause_cursor()
        # self.init_cursor()


    # def get_cursor_data_from_edge(self, edge, t):
    #     """ t in [0, 1] """
    #     # t = 0.0

    #     # get the coordinates of the points of the edge
    #     edge_start_point = self.active_edge.getTailPoint()
    #     edge_end_point = self.active_edge.getTipPoint()

    #     assert edge_start_point != edge_end_point

    #     # calculate position at t
    #     pos_t = edge_start_point + (edge_end_point - edge_start_point) * t

    #     direction_vec = (edge_end_point - edge_start_point)/np.linalg.norm(edge_end_point - edge_start_point)

    #     edge_length = np.linalg.norm(math_utils.p3d_to_np(edge_end_point - edge_start_point))

    #     return edge_start_point, edge_end_point, pos_t, direction_vec, edge_length


    def toggle_play_pause(self):
        """ toggle or set the play/pause state, val=True for play, False for pause """

        if self.play_p is True:
            self.play_p = False
            self.play_pause_label.setText("paused")
            self.pause_cursor()

        elif self.play_p is False:
            self.play_p = True
            self.play_pause_label.setText("playing")
            self.play_cursor()
        else:
            print("Error: play_p has invalid value")


    # def init_cursor(self):
    #     """ render:
    #         - cursor of current time (disk perpendicular to edge)
    #         - current time label """

    #     edge_start_point, edge_end_point, pos_t, direction_vec, edge_length = (
    #         self.get_cursor_data_from_edge(self.active_edge, self.a))

    #     self.p_c = OrientedCircle(
    #         origin_point=pos_t,
    #         normal_vector_vec3=Vec3(*direction_vec),
    #         radius=0.035,
    #         num_of_verts=30,
    #         with_hole=False,
    #         thickness=3.)

    #     self.p_c.setColor(self.paused_cursor_color)

        # self.play_cursor()


    def play_cursor(self):
        self.play_p = True
        if self.a == 1.0:
            self.play_cursor_sequence.finish()
            return
        # assert self.play_p is True

        # edge_start_point, edge_end_point, pos_t, direction_vec, edge_length = (
        #     self.get_cursor_data_from_edge(self.active_edge, self.a))

        self.p_c.setColor(self.playing_cursor_color)

        # start or continue the sequence
        if self.play_cursor_sequence is None:
            # create it
            self.p3d_interval = LerpFunc(
                GraphPlayer.update_position_func, duration=self.duration, extraArgs=self.extraArgs)
            self.play_cursor_sequence = Sequence(Wait(self.delay), self.p3d_interval, Func(self.finish_cursor))

            self.a = 0.
        else:
            if self.play_p is False:
                self.play_cursor_sequence.start(playRate=1.)
            else:
                self.play_cursor_sequence.resume()

            # assumption: returns value between 0 and 1
            self.a = self.play_cursor_sequence.get_t()/self.duration

            assert (self.a >= 0.0 and self.a <= 1.0)

    def pause_cursor(self):
        self.play_p = False
        if self.a == 1.0:
            self.play_cursor_sequence.finish()
            return
        # assert self.play_p is False

        self.p_c.setColor(self.paused_cursor_color)

        if self.play_cursor_sequence is None:
            # create the cursor
            self.p3d_interval = LerpFunc(
                GraphPlayer.update_position_func, duration=self.duration, extraArgs=self.extraArgs)
            self.play_cursor_sequence = Sequence(Wait(self.delay), self.p3d_interval, Func(self.finish_cursor))
            self.a = 0.
            # print("this should never occurr")
            # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
            # print("")
        else:
            self.a = self.play_cursor_sequence.get_t()/self.duration
            print("self.a: ", self.a,
                  "; self.play_cursor_sequence.get_t(): ", self.play_cursor_sequence.get_t(),
                  "; self.duration: ", self.duration)
            print("paused at self.a", self.a)
            self.play_cursor_sequence.pause()

    def finish_cursor(self):
        if self.stopped_at_end is True:
            return

        self.play_p = False
        self.pause_cursor()

        self.p_c.setColor(self.paused_cursor_color)

        self.stopped_at_end = True
        # self.a = self.play_cursor_sequence.get_t()/self.duration
        self.a = self.play_cursor_sequence.set_t(self.duration)
        # print("get_t(): ", self.a)
        print("stopped at end: ", self.a)
        # self.play_cursor_sequence.pause()
        self.play_cursor_sequence.finish()

        self.play_cursor_sequence = None


# self.stopped_at_end = False
# self.stopped_at_beginning = True

    # def init_time_label(self):
    #     """ show a text label at the position of the cursor:
    #         - set an event to trigger updating of the text on-hover
    #         - check if the active edge has changed """

    #     # init the textNode (there is one text node)
    #     pos_rel_to_world_x = Point3(1., 0., 0.)

    #     self.time_label = Pinned2dLabel(refpoint3d=pos_rel_to_world_x, text="mytext",
    #                                     xshift=0.02, yshift=0.02, font="fonts/arial.egg")

    #     self.time_label.textNode.hide()

    #     self.time_label.textNode.setTransform(
    #         math_utils.math_convention_to_p3d_mat4(math_utils.getScalingMatrix4x4(0.5, 0.5, 0.5)))

    def update_position_func(self,
                             a, # duration,
                             v1, v2, v_c, # p1, p2,
                             p_c):
            # assumption: t is a parameter between 0 and self.duration
            v21 = v2 - v1
            # a = t# /self.duration
            v_c = v1 + v21 * a
            p_c.nodePath.setPos(v_c)
            print(# "t = ", t,
                  # "; duration = ", duration,
                  "; a = ", a)

    # def mouseMoverTask(self, task):
    #     self.render_hints()
    #     return task.cont

    # def onPress(self):
    #     self.render_hints()
    #     print("onPress")
