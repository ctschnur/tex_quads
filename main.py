import conventions
import tests.svgpathtodat.main

from direct.showbase.ShowBase import ShowBase
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3
import numpy as np
from latex_object import LatexTextureObject, Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips, ParallelLines, GroupNode, Line, Point, ArrowHead, Vector

def draw_letter_from_path():
    # letter from path
    symbol_geometries = tests.svgpathtodat.main.get_test_symbol_geometries()
    polygontest = Polygon2dTestTriangles(symbol_geometries)
    polygontest.initiateTranslationMovement(v_x=1., duration=1.)

def create_point_grid():
    # create point grid
    irange = range(-2, 3)
    jrange = range(-2, 3)

    for i in irange:
        for j in jrange:
            point = Point()
            point.nodePath.setPos(i, 0, j)
            # color the origin
            if i == 0 and j == 0:
                point.nodePath.setColor(0., 1., 0., 1.)
            else:
                vector = Vector(Vec3(i, 0, j))
                # gradient_color = len(irange)/(min(irange)+i+0.001)
                gradient_color = 1. - np.abs((min(irange)+i)/float(len(irange)))
                gradient_color2 = 1. - np.abs((min(jrange)+j)/float(len(jrange)))
                # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT<C-c>
                print(gradient_color)
                vector.line.nodePath.setColor(gradient_color, gradient_color2, 1., 1.)
                vector.arrowhead.nodePath.setColor(gradient_color, gradient_color2, 1., 1.)

def create_latex_texture_object():
    myLatexObject = LatexTextureObject("Obj 1")

def create_line_groups():
    # first, unaltered line train
    parallelLines = ParallelLines()
    groupNode1 = GroupNode()
    groupNode1.addChildNodePaths([line.nodePath for line in parallelLines.lines])

    # second, altered line train
    parallelLines2 = ParallelLines()
    groupNode = GroupNode()
    groupNode.addChildNodePaths([line.nodePath for line in parallelLines2.lines])

    # color it in
    for idx, np in enumerate(groupNode.nodePath.get_children()):
        greyscale_ratio = idx / len(groupNode.nodePath.get_children())
        color_value_greyscale = 1. - greyscale_ratio
        np.setColor(color_value_greyscale, color_value_greyscale, color_value_greyscale, 1.0)

    # translate it
    length_of_line_train = parallelLines2.number_of_lines * parallelLines2.spacing
    # groupNode.nodePath.setHpr(0, 0, -90)
    # groupNode.nodePath.setPos(groupNode.nodePath, -length_of_line_train/2., 0, 0.)
    groupNode.nodePath.setPos(groupNode.nodePath, -1., 0, 0.)
    groupNode.nodePath.setHpr(0, 0, -90)


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        # make self-defined camera control possible
        self.disableMouse()
        conventions.setupOrthographicProjectionAndViewingAccordingToMyConvention()

        # earlier experiments
        # create_latex_texture_object()
        # create_line_groups()
        # draw_letter_from_path()
        # create_point_grid()

        # children = render.get_children()
        # for child in children:
        #     child.setRenderModeFilled()
        render.setAntialias(AntialiasAttrib.MAuto)

        # current experiment

        greenpoint = Point()
        greenpoint.nodePath.setPos(1, 0, 1)
        greenpoint.nodePath.setColor(0., 1., 0., 1.)

        redpoint = Point()
        redpoint.nodePath.setPos(1, 0, 0)
        redpoint.nodePath.setColor(1., 0., 0., 1.)

        line = Line()
        line.setTipPoint(Vec3(1, 0, 1))

        blueline = Line()
        blueline.nodePath.setColor(0, 0, 1, 1)

        gn = GroupNode()
        gn.addChildNodePaths([blueline.nodePath])

        from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
        from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval


        def circlearound(t):
            r = 1.
            x = r * np.cos(t)
            z = r * np.sin(t)
            gn.nodePath.setPos(x, 0, z)

        seq = Sequence(
            Parallel(
                LerpFunc(
                    circlearound,
                    fromData=0,
                    toData=2*3.1415,
                    duration=1.),
                LerpHprInterval(
                    blueline.nodePath,
                    1.,
                    Vec3(0,0,360))
                )
        ).loop(playRate=.25)

        def myfunction(node, myvec):
            node.setTipPoint(myvec)

        # seq.append(Func(myfunction, blueline, Vec3(-1., 0, 1.)))
        # seq.append(Wait(.5))
        # seq.append(Func(myfunction, blueline, Vec3(-2., 0, 1.)))
        # seq.append(Wait(.5))
        # seq.append(LerpPosInterval(gn.nodePath, .5, Point3(-.5, 0., 0.)))
        # seq.append(Wait(.5))

        # print("duration: ", seq.duration)

        # def parametrization_of_rotation(t, t_f, h_f, p_f, r_f):
        #     h = h_f * (t / t_f)
        #     p = p_f * (t / t_f)
        #     r = r_f * (t / t_f)
        #     return (h, p, r)

        # def update_function(t, nodepath, t_f, h_f, p_f, r_f):
        #     h, p, r = parametrization_of_rotation(t, t_f, h_f, p_f, r_f)
        #     nodepath.setHpr(h, p, r)

        # nodepath = blueline.nodePath
        # t_0 = 0.
        # t_f = 2.  # seconds, only actual seconds if panda syncs it up correctly
        # h_f = 0.  # degrees
        # p_f = 0.  # degrees
        # r_f = 90. # degrees

        # params = [nodepath, t_f, h_f, p_f, r_f]  # constants for the parametrization
        # # create an 'Interval', i.e. an object performing the transition, scaling up time
        # p3d_interval = LerpFunc(
        #     update_function,     # pointer to function updating the nodepath's properties
        #     fromData=t_0,
        #     toData=t_f,
        #     duration=(t_f-t_0),  # duration (maybe to skip the animation, if sth. goes bad)
        #     extraArgs=params)

        # delay = 1.
        # # create a 'Sequence', i.e. a sequence of 'Intervals'
        # Sequence(Wait(delay),   # just a waiting (do nothing) type of 'Interval'
        #          p3d_interval   # my custom 'Interval'
        # ).start()  # start the animation

        # symbol_geometries = tests.svgpathtodat.main.get_test_symbol_geometries()
        # polygontest = Polygon2dTestTriangles(symbol_geometries)
        # polygontest.initiateTranslationMovement(v_x=1., duration=1.)


        # time_total = 5
        # step_size = 1
        # steps = 10
        # r = 1
        # for t in np.linspace(0, time_total, num=steps):
        #     Sequence(Wait(.5))
        #     phi = 2 * 3.1415 * t/time_total
        #     x = r * np.cos(phi)
        #     z = r * np.sin(phi)
        #     blueline.setTipPoint(Vec3(x, 0, z))

        # print logs
        childs = render.getChildren()
        print(len(childs))

app = MyApp()
app.run()
