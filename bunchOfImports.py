from math import pi, sin, cos

from direct.showbase.ShowBase import ShowBase

from panda3d.core import GeomVertexFormat
from panda3d.core import GeomVertexData
from panda3d.core import Geom, GeomVertexWriter 
from panda3d.core import GeomTriangles 
from panda3d.core import GeomNode 
from panda3d.core import PNMImage
from panda3d.core import Filename
from panda3d.core import Texture, TransparencyAttrib
from panda3d.core import PandaSystem
from panda3d.core import Mat4, Vec3
from panda3d.core import OrthographicLens

print("Panda version:", PandaSystem.getVersionString())

from panda3d.core import loadPrcFileData 

import hashlib

# p3d window
winsizex = 480.
winsizey = 272.
loadPrcFileData('', 'win-size ' + str(winsizex) + ' ' + str(winsizey))

# utility variable
win_aspect_ratio = winsizex/winsizey

# p3d window positon within OS gui in pixels; (0,0) is upper left of OS GUI
# puts the upper left corner of the p3d window at that position
loadPrcFileData('', 'win-origin 10 -2')

# let's pretend we know the resolution (of the hardware monitor) in terms of
# pixels
screen_res_width = 1920.
screen_res_height = 1080.
