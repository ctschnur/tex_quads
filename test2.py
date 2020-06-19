from conventions import conventions
import os, sys
import panda3d.core as p3d
from direct.showbase.ShowBase import ShowBase
import pytest
import gltf

from panda3d.core import Vec4

from cameras.Orbiter import Orbiter

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        gltf.patch_loader(base.loader)

        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
        # my_model_path = modelpath()
        # print("MODEL PATH: ", my_model_path)

        # self.scene = (self.loader.loadModel("models/environment"))
        # self.scene.reparentTo(self.render)
        # self.scene.setScale(0.25, 0.25, 0.25)
        # self.scene.setPos(-8, 42, 0)

        conventions.setupOrthographicProjectionAndViewingAccordingToMyConvention()

        from composed_objects.composed_objects import ParallelLines, GroupNode, Vector, CoordinateSystem, Scatter, Axis, Box2dOfLines, CoordinateSystemP3dPlain
        cs = CoordinateSystem()

        ob = Orbiter()

        # # ambient light
        # from panda3d.core import AmbientLight
        # alight = AmbientLight('alight')
        # alnp = render.attachNewNode(alight)
        # # alnp.setPos(0, -30, 5)
        # alight.setColor((0.2, 0.2, 0.2, 1))
        # render.setLight(alnp)

        # # point light
        # from panda3d.core import PointLight
        # plight = PointLight('plight')
        # plnp = render.attachNewNode(plight)
        # # dlnp.setHpr(30, -60, 0)
        # plnp.setPos(0, -30, 5)
        # render.setLight(plnp)

        # # load an egg file model
        # from panda3d.core import Filename
        # loader.loadModel(
        #     Filename.fromOsSpecific(
        #         os.path.abspath(sys.path[0])).getFullpath() # root of project
        #     + "/models/mymodel.egg")
        # model.reparentTo(render)
        # base.textureOff()

        # # load the panda (standard included) model, which has vertex normals
        # # to test toggling of flat/smooth shading
        # model = loader.loadModel('panda')
        # model.reparentTo(render)
        # base.textureOff()

        # # load a gltf file
        # from panda3d.core import Filename
        # self.model = loader.loadModel(
        #     Filename.fromOsSpecific(
        #         os.path.abspath(sys.path[0])).getFullpath()  # root of project
        #     + "/models/cube_solo.gltf")
        # base.textureOff()

        # # load a gltf file
        # from panda3d.core import Filename
        # self.model = loader.loadModel(
        #     Filename.fromOsSpecific(
        #         os.path.abspath(sys.path[0])).getFullpath()  # root of project
        #     + "/models/unit_cone_triangulated_with_face_normals.gltf")
        # self.model.reparentTo(self.render)

        # self.model.setColor(Vec4(1, 0, 0, 1))


        # # toggling between smooth and flat shading (for panda model)
        # type = 1
        # def changeShading():
        #         global type

        #         if type == 1:
        #                 model.node().setAttrib(ShadeModelAttrib.make(ShadeModelAttrib.MFlat))
        #                 type = 0
        #         else:
        #                 model.node().setAttrib(ShadeModelAttrib.make(ShadeModelAttrib.MSmooth))
        #                 type = 1

        # base.accept('enter', changeShading)


app = MyApp()
app.run()
