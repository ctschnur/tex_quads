import conventions
import tests.svgpathtodat.main

from direct.showbase.ShowBase import ShowBase
from panda3d.core import AntialiasAttrib, NodePath, Vec3
import numpy as np
from latex_object import LatexTextureObject, Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips, ParallelLines, GroupNode, Line, Point, ArrowHead, Vector


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # make self-defined camera control possible
        self.disableMouse()  

        conventions.setupOrthographicProjectionAndViewingAccordingToMyConvention()

        # myLatexObject = LatexTextureObject("Obj 1")

        # axis2.numberLine.nodePath.setColor(0.6, 0.6, 1.0, 1.0)

        # # first, unaltered line train
        # parallelLines = ParallelLines()
        # groupNode1 = GroupNode()
        # groupNode1.addChildNodePaths([line.nodePath for line in parallelLines.lines])

        # # second, altered line train
        # parallelLines2 = ParallelLines()
        # groupNode = GroupNode()
        # groupNode.addChildNodePaths([line.nodePath for line in parallelLines2.lines])

        # # color it in
        # for idx, np in enumerate(groupNode.nodePath.get_children()):
        #     greyscale_ratio = idx / len(groupNode.nodePath.get_children())
        #     color_value_greyscale = 1. - greyscale_ratio
        #     np.setColor(color_value_greyscale, color_value_greyscale, color_value_greyscale, 1.0)

        # # translate it
        # length_of_line_train = parallelLines2.number_of_lines * parallelLines2.spacing
        # # groupNode.nodePath.setHpr(0, 0, -90)
        # # groupNode.nodePath.setPos(groupNode.nodePath, -length_of_line_train/2., 0, 0.)
        # groupNode.nodePath.setPos(groupNode.nodePath, -1., 0, 0.)
        # groupNode.nodePath.setHpr(0, 0, -90)

        # # draw vector to origin of altered line train
        # origvec = Line()
        # origvec.setTipPoint(Vec3(0.5, 0., 0.))
        # 
        # # letter from path
        # symbol_geometries = tests.svgpathtodat.main.get_test_symbol_geometries()
        # polygontest = Polygon2dTestTriangles(symbol_geometries)
        # polygontest.initiateTranslationMovement(v_x=1., duration=1.)

        # create point grid
        irange = range(-2, 3)
        jrange = range(-2, 3)

        for i in irange:
            for j in jrange:
                point = Point()
                point.nodePath.setPos(i, 100, j)
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

        line = Line()
        line.setTipPoint(Vec3(0, 0, 0))

        children = render.get_children()
        for child in children: 
            child.setRenderModeFilled()

        targetpoint = Point()
        targetpoint.nodePath.setPos(1, 0, 1)
        targetpoint.nodePath.setColor(0., 0., 0., 1.)

        point = Point()
        point.nodePath.setPos(1, 0, 0)
        point.nodePath.setColor(1., 0., 0., 1.)

        # line = Line()
        # line.setTipPoint(Vec3(1, 0, 1.5))

        # render.setAntialias(AntialiasAttrib.MAuto)

        childs = render.getChildren()
        print(len(childs))


app = MyApp()
app.run()
