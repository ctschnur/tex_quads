from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector
from simple_objects.simple_objects import Line, Point, ArrowHead


import numpy as np

from direct.showbase.ShowBase import ShowBase
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Mat4
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

import tests.svgpathtodat.main

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

def spinning_around_independently():
    blueline = Line()
    blueline.nodePath.setColor(0, 0, 1, 1)

    gn = GroupNode()
    gn.addChildNodePaths([blueline.nodePath])

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
    ).loop(playRate=1)


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        # make self-defined camera control possible
        self.disableMouse()
        render.setAntialias(AntialiasAttrib.MAuto)
        conventions.setupOrthographicProjectionAndViewingAccordingToMyConvention()

        # earlier experiments
        # create_latex_texture_object()
        # create_line_groups()
        # draw_letter_from_path()
        # create_point_grid()
        # spinning_around_independently()

        # children = render.get_children()
        # for child in children:
        #     child.setRenderModeFilled()

        # current experiment
        # greenpoint = Point()
        # greenpoint.nodePath.setPos(1, 0, 1)
        # greenpoint.nodePath.setColor(0., 1., 0., 1.)

        # redpoint = Point()
        # redpoint.nodePath.setPos(1, 0, 0)
        # redpoint.nodePath.setColor(1., 0., 0., 1.)

        # line = Line()
        # line.nodePath.setColor(1,1,0,1)


        # vec = Vector()

        # def myMatTrafo(t, nodePath):
        #     # scaling (determine scaling matrix for xhat)
        #     vx = 1.
        #     vy = 1.
        #     vz = 1.
        #     scaling = np.array([[vx,  0,  0, 0],
        #                         [0,  vy,  0, 0],
        #                         [0,   0, vz, 0],
        #                         [0,   0,  0, 1]])
        #     scaling *= t

        #     scaling_forrowvecs = Mat4(*tuple(np.transpose(scaling).flatten()))
        #     trafo = scaling_forrowvecs

        #     nodePath.setMat(trafo)

        # seq = Sequence(
        #     Parallel(
        #         LerpHprInterval(
        #             vec.groupNode.nodePath,
        #             1.,
        #             Vec3(0, 0, 360)
        #         ),
        #         LerpPosInterval(
        #             vec.groupNode.nodePath,
        #             1.,
        #             Point3(0., 0, 1.)
        #         ),
        #         LerpScaleInterval(
        #             vec.groupNode.nodePath,
        #             1.,
        #             .2
        #         )
        #     )
        # ).start(playRate=0.5)

        # gn = vec.groupNode

       # def myfunc(t, gn):
        #     gn.nodePath.setPos(t, 0, t)

        # t_0 = 0.5
        # t_f = 1.

        # seq = Sequence(
        #     Parallel(
        #         LerpFunc(
        #             myfunc,
        #             fromData=t_0,
        #             duration=t_f,
        #             extraArgs=[vec.groupNode]
        #         )
        #     )
        # ).loop(playRate=1)

        vec2 = Vector(tip_point=Vec3(-1, 0, 1))
        vec2.groupNode.nodePath.setColor(1, 0, 0, 1)

        # Sequence(
        #     Wait(.5),
        #     Func(vec2.setVectorTipPoint, Vec3(-2, 0, -0.1)),
        #     Wait(.5),
        #     Func(vec2.setVectorTipPoint, Vec3(0, 0, -0.5)),
        #     Wait(.5)
        # ).start(playRate=.5)


        myline = Line()
        myline.nodePath.setColor(1, 0, 1, 1)

        def f1():
            myline.setTipPoint(Vec3(-2, 0, 0.1))

        def f2():
            myline.setTipPoint(Vec3(0, 0, 1.))

        def f3():
            myline.setTipPoint(Vec3(-2, 0, 0.1))

        f1()
        f2()
        f3()


        # in a Sequence, the matrix's nodes are being continually transformed
        # Sequence(
        #     Wait(.5),
        #     Func(f1),
        #     Wait(.5),
        #     Func(f2),
        #     Wait(.5),
        #     Func(f3),
        #     Wait(.5),
        # ).start(playRate=.25)

        # print logs
        childs = render.getChildren()
        print(len(childs))

app = MyApp()
app.run()
