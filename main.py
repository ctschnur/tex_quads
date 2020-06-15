from conventions import conventions
from latex_objects.latex_texture_object import LatexTextureObject
from simple_objects.polygon import Polygon2d, Polygon2dTestTriangles, Pollygon2dTestLineStrips
from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain
from simple_objects.simple_objects import Line2dObject, Point, ArrowHead, Line1dObject, LineDashed1dObject, ArrowHeadCone
# , ArrowHeadCone
from simple_objects import box
from local_utils import math_utils

import numpy as np

from direct.showbase.ShowBase import ShowBase
from panda3d.core import AntialiasAttrib, NodePath, Vec3, Point3, Mat4, Vec4, DirectionalLight, AmbientLight, PointLight
from direct.interval.IntervalGlobal import Wait, Sequence, Func, Parallel
from direct.interval.LerpInterval import LerpFunc, LerpPosInterval, LerpHprInterval, LerpScaleInterval

import local_tests.svgpathtodat.main


def draw_letter_from_path():
    # letter from path
    symbol_geometries = local_tests.svgpathtodat.main.get_test_symbol_geometries()
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
                gradient_color = 1. - \
                    np.abs((min(irange)+i)/float(len(irange)))
                gradient_color2 = 1. - \
                    np.abs((min(jrange)+j)/float(len(jrange)))
                # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT<C-c>
                print(gradient_color)
                vector.line.nodePath.setColor(
                    gradient_color, gradient_color2, 1., 1.)
                vector.arrowhead.nodePath.setColor(
                    gradient_color, gradient_color2, 1., 1.)


def create_latex_texture_object():
    myLatexObject = LatexTextureObject("Obj 1")


def create_line_groups():
    # first, unaltered line train
    parallelLines = ParallelLines()
    groupNode1 = GroupNode()
    groupNode1.addChildNodePaths(
        [line.nodePath for line in parallelLines.lines])

    # second, altered line train
    parallelLines2 = ParallelLines()
    groupNode = GroupNode()
    groupNode.addChildNodePaths(
        [line.nodePath for line in parallelLines2.lines])

    # color it in
    for idx, np in enumerate(groupNode.nodePath.get_children()):
        greyscale_ratio = idx / len(groupNode.nodePath.get_children())
        color_value_greyscale = 1. - greyscale_ratio
        np.setColor(color_value_greyscale, color_value_greyscale,
                    color_value_greyscale, 1.0)

    # translate it
    length_of_line_train = parallelLines2.number_of_lines * parallelLines2.spacing
    # groupNode.nodePath.setHpr(0, 0, -90)
    # groupNode.nodePath.setPos(groupNode.nodePath, -length_of_line_train/2., 0, 0.)
    groupNode.nodePath.setPos(groupNode.nodePath, -1., 0, 0.)
    groupNode.nodePath.setHpr(0, 0, -90)


def spinning_around_independently():
    blueline = Line2dObject()
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
                Vec3(0, 0, 360))
        )
    ).loop(playRate=1)


def miscexperiments():
    children = render.get_children()
    for child in children:
        child.setRenderModeFilled()

    # current experiment
    greenpoint = Point()
    greenpoint.nodePath.setPos(1, 0, 1)
    greenpoint.nodePath.setColor(0., 1., 0., 1.)

    redpoint = Point()
    redpoint.nodePath.setPos(1, 0, 0)
    redpoint.nodePath.setColor(1., 0., 0., 1.)

    line = Line2dObject()
    line.nodePath.setColor(1, 1, 0, 1)

    vec = Vector()

    def myMatTrafo(t, nodePath):
        # scaling (determine scaling matrix for xhat)
        vx = 1.
        vy = 1.
        vz = 1.
        scaling = np.array([[vx,  0,  0, 0],
                            [0,  vy,  0, 0],
                            [0,   0, vz, 0],
                            [0,   0,  0, 1]])
        scaling *= t

        scaling_forrowvecs = Mat4(*tuple(np.transpose(scaling).flatten()))
        trafo = scaling_forrowvecs

        nodePath.setMat(trafo)

    seq = Sequence(
        Parallel(
            LerpHprInterval(
                vec.groupNode.nodePath,
                1.,
                Vec3(0, 0, 360)
            ),
            LerpPosInterval(
                vec.groupNode.nodePath,
                1.,
                Point3(0., 0, 1.)
            ),
            LerpScaleInterval(
                vec.groupNode.nodePath,
                1.,
                .2
            )
        )
    ).start(playRate=0.6)

    gn = vec.groupNode

    def myfunc(t, gn):
        gn.nodePath.setPos(t, 0, t)

    t_0 = 0.6
    t_f = 1.

    seq = Sequence(
        Parallel(
            LerpFunc(
                myfunc,
                fromData=t_0,
                duration=t_f,
                extraArgs=[vec.groupNode]
            )
        )
    ).loop(playRate=1)


def vectoranimation(switchontwitchinglines=False):
    if switchontwitchinglines:
        vec2 = Vector()
        vec2.groupNode.nodePath.setColor(1, 0, 0, 1)

        Sequence(
            Wait(.6),
            Func(vec2.setVectorTipPoint, Vec3(-2, 0, -0.1)),
            Wait(.6),
            Func(vec2.setVectorTipPoint, Vec3(0, 0, -0.6)),
            Wait(.6)
        ).loop(playRate=.6)

        myline = Line2dObject()
        myline.nodePath.setColor(1, 0, 1, 1)
        myline.setTipPoint(Vec3(1, 0, 0.1))

        def f1():
            # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT<C-c>
            myline.setTipPoint(Vec3(-1, 0, 0))

        def f2():
            # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT<C-c>
            myline.setTipPoint(Vec3(0, 0, 1.))

        def f3():
            # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT<C-c>
            myline.setTipPoint(Vec3(-2, 0, 0.1))

        f1()
        f2()

        # print logs
        childs = render.getChildren()
        print(len(childs))

        # in a Sequence, the matrix's nodes are being continually transformed
        Sequence(
            Wait(.6),
            Func(f1),
            Wait(.6),
            Func(f2),
        ).loop(playRate=1)

    vec3 = Vector()
    vec3.groupNode.nodePath.setColor(1, 0, 0, 1)

    twvec = Vector()
    twvec.groupNode.nodePath.setColor(0, 1, 0, 1)

    g = GroupNode()
    g.addChildNodePaths([vec3.groupNode.nodePath])

    p = Point()

    def heymyfunc(t, vec, g, twirlingvec):
        r = 1.
        x = r * np.cos(t)
        z = r * np.sin(t)
        x_fast = r * np.cos(t*2)
        z_fast = r * np.sin(t*2)
        vec.setVectorTipPoint(Vec3(-x, 0, -z)*0.6)
        twirlingvec.setVectorTipPoint(Vec3(x_fast, 0, z_fast)*0.2)

        g.nodePath.setMat(
            math_utils.getTranslationMatrix3d_forrowvecs(x, 0, z))
        twirlingvec.groupNode.nodePath.setMat(
            math_utils.getTranslationMatrix3d_forrowvecs(x, 0, z))

    t_0 = 0.
    t_f = 2*3.1415

    seq = Sequence(
        Parallel(
            LerpFunc(
                heymyfunc,
                fromData=0,
                toData=t_f,
                duration=1,
                extraArgs=[vec3, g, twvec]
            )
        )
    ).loop(playRate=.25)


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        base.setFrameRateMeter(True)

        # make self-defined camera control possible
        # disableMouse()
        render.setAntialias(AntialiasAttrib.MAuto)
        # render.set_two_sided(True)
        conventions.setupOrthographicProjectionAndViewingAccordingToMyConvention()

        # earlier experiments
        # create_latex_texture_object()
        # create_line_groups()
        # draw_letter_from_path()
        # create_point_grid()
        # spinning_around_independently()
        # miscexperiments()
        # vectoranimation()

        cs = CoordinateSystem()

        # current experiment
        # greenpoint = Point()
        # greenpoint.nodePath.setPos(1, 0, 1)
        # greenpoint.nodePath.setColor(0., 1., 0., 1.)

        scat = Scatter([1, 2], [1, 2])

        # cs.attachScatter(scat)

        # line = Line2dObject()
        # line.setTipPoint(Vec3(1., 0., 0.))

        # line.setTipPoint(Vec3(1., 0., 1.))

        # ax = Axis(Vec3(1., 0., 1.), 2.)

        # cs.attachScatter(scat)

        # x = np.linspace(-1, 1, num=10)
        # y = x**2
        # scat2 = Scatter(x, y, color=Vec4(1, 0, 0, 1))
        # cs.attachScatter(scat2)

        # box2d = Box2dOfLines(0.2, 0.4, 0.5, 2.0,
        #                      color=Vec4(0.4, 0.2, 0.5, 0.5))

        # cs3dp = CoordinateSystemP3dPlain()

        # create_latex_texture_object()

        # a = box.LinePrimitive()

        # a = Line1dObject(thickness=3.0, color=Vec4(1,0,0,1))
        # a.setTipPoint(Vec3(1., 0., 0.))

        # b = Line1dObject(thickness=5.0, color=Vec4(0,1,0,1))
        # # b.setTipPoint(Vec3(0., 0., 1.))

        # b.setTipPoint(Vec3(1., 1.2, 0.5))

        import ctsutils.euler_angles as cse
        from ctsutils.euler_angles import get_R_x, get_R_y, get_R_z

        import numpy as np

        theta = 0.3

        alpha_beta_gammas = [
            tuple(np.array([3.*np.pi/2.-theta, np.pi/2., np.pi/2.])),
            tuple(np.array([np.pi/2.-theta, np.pi/2., 0.])),
            tuple(np.array([np.pi/2.-theta, 0., 0.]))]

        zxz_total = cse.get_zxz_rot(*alpha_beta_gammas[2])

        # zxz_total = cse.get_zxz_rot(3.*np.pi/2.-theta, 0.25, 0.)

        x_c_hat = np.matmul(
            zxz_total,
            np.transpose(np.array([1., 0., 0.])))

        y_c_hat = np.matmul(
            zxz_total,
            np.transpose(np.array([0., 1., 0.])))

        z_c_hat = np.matmul(
            zxz_total,
            np.transpose(np.array([0., 0., 1.])))

        v1 = Vector(tip_point=Vec3(*tuple(x_c_hat)),
                    thickness1dline=10.,
                    color=Vec4(1.,0.,0,0.25),
                    linestyle="--")

        v2 = Vector(tip_point=Vec3(*tuple(y_c_hat)),
                    thickness1dline=10.,
                    color=Vec4(0.,1.,0,0.25),
                    linestyle="--")

        v3 = Vector(tip_point=Vec3(*tuple(z_c_hat)),
                    thickness1dline=10.,
                    color=Vec4(0.,0.,1.,0.25),
                    linestyle="--")

        print("// cut ")
        print("triple x_c_hat=" + str(tuple(np.round(x_c_hat, 3))) + ";")
        print("triple y_c_hat=" + str(tuple(np.round(y_c_hat, 3))) + ";")
        print("triple z_c_hat=" + str(tuple(np.round(z_c_hat, 3))) + ";")

        # v3 = Vector(tip_point=Vec3(1., 1., 0),
        #            thickness1dline=2.5,
        #            color=Vec4(0.,0.,1.,0.25))

        # ------------------------

        # gn = GroupNode()
        # gn.addChildNodePaths([nodepath])


        # ld = LineDashedPrimitive()

        # a = LineDashed1dObject(thickness=10.0, color=Vec4(1,1,0,1), howmany_periods=10.)
        # a.setTipPoint(Vec3(1., 1., 0.))

        # v4 = Vector(tip_point=Vec3(*tuple(x_c_hat + z_c_hat)),
        #             thickness1dline=10.,
        #             color=Vec4(0.75,0.,1,0.25),
        #             linestyle="--")

        # v5 = Vector(tip_point=Vec3(*tuple(x_c_hat + z_c_hat)),
        #            thickness1dline=10.,
        #             color=Vec4(0.75,0.,1,0.25))

        from simple_objects.custom_geometry import create_GeomNode_Cone, createColoredUnitCircle

        # geomNode = create_GeomNode_Cone()
        # nodePath = render.attachNewNode(geomNode)
        # nodePath.setTwoSided(True)


        # --- setup a directional light
        # dlight = DirectionalLight('dlight')
        # dlight.setColor((1., 1., 1., 1))
        # dlnp = render.attachNewNode(dlight)
        # dlnp.setHpr(0, 45, 0)
        # render.setLight(dlnp)

        plight = PointLight('plight')
        plight.setColor((0.9, 0.9, 0.9, 1))
        plnp = render.attachNewNode(plight)
        plnp.setPos(10, 20, 0)
        render.setLight(plnp)

        # geomNode = createColoredUnitCircle()
        # nodePath = render.attachNewNode(geomNode)
        # nodePath.setTwoSided(True)

        
        # base.wireframeOn()

        ahc = ArrowHeadCone()

        # add shading
        # step 1: add a material to the nodepath
        from panda3d.core import Material
        myMaterial = Material()
        # myMaterial.setDiffuse((0.5,0.5,0.5,1.))
        # myMaterial.setShininess(5.0) #Make this material shiny
        myMaterial.setAmbient((1, 0, 0, 1)) #Make this material blue
        ahc.nodePath.setMaterial(myMaterial)
        ahc.nodePath.setMat(ahc.nodePath.getMat() * math_utils.getScalingMatrix3d_forrowvecs(4., 4., 4.))


        def findChildrenAndSetRenderModeRecursively(parentnode):
            children = parentnode.get_children()
            for child in children:
                findChildrenAndSetRenderModeRecursively(child)
                child.setRenderModeFilled()

        findChildrenAndSetRenderModeRecursively(render)


app = MyApp()
app.run()
