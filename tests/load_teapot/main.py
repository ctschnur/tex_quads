from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from direct.actor.Actor import Actor

from direct.interval.IntervalGlobal import Sequence
from panda3d.core import Point3

class MyApp(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)

        self.disableMouse()

        # # teapot
        self.scene = self.loader.loadModel("models/teapot")
        self.scene.reparentTo(self.render)

        self.camera.setPos(0, -20, 4)
 
app = MyApp()
app.run()
