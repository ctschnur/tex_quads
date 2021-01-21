import direct.directbase.DirectStart
from panda3d.core import *
import engine

base.disableMouse() # disable default mouse controls

# Load the scene.
environ = loader.loadModel('environment')
environ.setScale(0.1)
environ.setZ(-5)
environ.reparentTo(engine.tq_graphics_basics.tq_render)

# model for the camera to orbit along
model = loader.loadModel('smiley')
model.reparentTo(engine.tq_graphics_basics.tq_render)

# dummy node for camera
parentnode = engine.tq_graphics_basics.tq_render.attachNewNode('camparent')
parentnode.reparentTo(model) # inherit transforms
parentnode.setEffect(CompassEffect.make(engine.tq_graphics_basics.tq_render)) # NOT inherit rotation

keyMap = {"a":0, "d":0, "w":0, "s":0}

#Records the state of the arrow keys
def setKey(key, value):
   keyMap[key] = value

# the camera
base.camera.reparentTo(parentnode)
base.camera.lookAt(parentnode)
base.camera.setY(-10) # camera distance from model

def cameraMovement(task):
   if (keyMap["a"]!=0):
      parentnode.setH(parentnode.getH()-200 * globalClock.getDt())
   if (keyMap["d"]!=0):
      parentnode.setH(parentnode.getH()+200 * globalClock.getDt())
   if (keyMap["w"]!=0):
      parentnode.setP(parentnode.getP()-200 * globalClock.getDt())
   if (keyMap["s"]!=0):
      parentnode.setP(parentnode.getP()+200 * globalClock.getDt())

   return task.cont


taskMgr.add(cameraMovement, 'cameraMovement')

# camera zooming
base.accept('wheel_up', lambda : base.camera.setY(base.cam.getY()+200 * globalClock.getDt()))
base.accept('wheel_down', lambda : base.camera.setY(base.cam.getY()-200 * globalClock.getDt()))

# camera rotation
base.accept('a', setKey, ["a",1])
base.accept('a-up', setKey, ["a",0])
base.accept('d', setKey, ["d",1])
base.accept('d-up', setKey, ["d",0])
base.accept('w', setKey, ["w",1])
base.accept('w-up', setKey, ["w",0])
base.accept('s', setKey, ["s",1])
base.accept('s-up', setKey, ["s",0])



# ---------
# import direct.directbase.DirectStart
# from panda3d.core import *

# base.disableMouse() # disable default mouse controls

# # hide mouse cursor, comment these 3 lines to see the cursor
# props = WindowProperties()
# props.setCursorHidden(True)
# base.win.requestProperties(props)

# # a scene
# environ = loader.loadModel('environment')
# environ.setScale(0.1)
# environ.setZ(-5)
# environ.reparentTo(engine.tq_graphics_basics.tq_render)

# # model for the camera to orbit along
# model = loader.loadModel('smiley')
# model.reparentTo(engine.tq_graphics_basics.tq_render)

# # dummy node for camera, we will rotate the dummy node fro camera rotation
# parentnode = engine.tq_graphics_basics.tq_render.attachNewNode('camparent')
# parentnode.reparentTo(model) # inherit transforms
# parentnode.setEffect(CompassEffect.make(engine.tq_graphics_basics.tq_render)) # NOT inherit rotation

# # the camera
# base.camera.reparentTo(parentnode)
# base.camera.lookAt(parentnode)
# base.camera.setY(-10) # camera distance from model

# # camera zooming
# base.accept('wheel_up', lambda : base.camera.setY(base.camera.getY()+200 * globalClock.getDt()))
# base.accept('wheel_down', lambda : base.camera.setY(base.camera.getY()-200 * globalClock.getDt()))


# # global vars for camera rotation
# heading = 0
# pitch = 0

# # camera rotation task
# def thirdPersonCameraTask(task):
#    global heading
#    global pitch

#    md = base.win.getPointer(0)

#    x = md.getX()
#    y = md.getY()

#    if base.win.movePointer(0, 300, 300):
#       heading = heading - (x - 300) * 0.5
#       pitch = pitch - (y - 300) * 0.5

#    parentnode.setHpr(heading, pitch,0)

#    return task.cont

# taskMgr.add(thirdPersonCameraTask, 'thirdPersonCameraTask')


# run()
