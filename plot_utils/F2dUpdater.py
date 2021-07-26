class F2dUpdater:
    """ """
    def __init__(self, next_color_func, xy_datas, f2d):
        """ """
        self.ctr = 0
        self.next_color_func = next_color_func
        self.xy_datas = xy_datas
        self.f2d = f2d

    def add_plot(self):
        """ """
        self.f2d.plot(self.xy_datas[self.ctr][0],
                      self.xy_datas[self.ctr][1],
                      color=self.next_color_func())
        self.ctr += 1
        self.ctr = self.ctr % len(self.xy_datas)

        print("self.ctr:", self.ctr)


class FramesUpdater:
    """ """
    def __init__(self, f2d, tf_in_s, fps):
        """ accepts a Frame2d """

        self.idx_frame_old = 0

        self.f2d = f2d

        self.frame_xs = np.linspace(0, 1., num=100)
        self.frames = []

        self.tf_in_s = tf_in_s  # e.g. 3
        self.fps = fps  # e.g. 25

        self.ti = 0
        self.tf = self.tf_in_s * self.fps
        for t in range(self.ti, self.tf):
            self.frames.append([
                self.frame_xs, (0.5 * (1+t/self.tf)) *
                (np.sin(self.frame_xs*t) +
                 np.cos(np.sqrt(self.frame_xs*t/self.tf)*self.tf))])

        self.frame_ctr = 0

    def get_next_frame(self):
        """ """
        _frame = self.frames[self.frame_ctr]
        self.frame_ctr += 1
        return _frame

    def render_frame(self, a):
        """ 0 < a < 1 """
        idx_frame = int(a*self.tf)
        x, y = self.frames[idx_frame]
        self.f2d.clear_plot()
        self.f2d.plot(x, y)
