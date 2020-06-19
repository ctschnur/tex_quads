import os
import sys
import panda3d.core as p3d
from direct.showbase.ShowBase import ShowBase
import pytest
import gltf


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

        base.cam.setPos(0, -30, 5)

        from panda3d.core import DirectionalLight
        dlight = DirectionalLight('dlight')
        dlnp = render.attachNewNode(dlight)
        dlnp.setHpr(30, -60, 0)
        render.setLight(dlnp)

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

        # load a gltf file
        from panda3d.core import Filename
        self.model = loader.loadModel(
            Filename.fromOsSpecific(
                os.path.abspath(sys.path[0])).getFullpath()  # root of project
            + "/models/cube_solo.gltf")
        base.textureOff()

        # self.model = (self.loader.loadModel("models/test"))
        self.model.reparentTo(self.render)
        self.model.setPos(0, 0, 3)
        self.model.setScale(0.5, 0.5, 0.5)

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
