import conventions
import tests.svgpathtodat.main

from direct.showbase.ShowBase import ShowBase
from panda3d.core import AntialiasAttrib
import numpy as np
from latex_object import LatexTextureObject, Axis, Polygon2d, Polygon2dTestTriangles, Polygon2dTestLineStrips


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # make self-defined camera control possible
        self.disableMouse()  

        conventions.setupOrthographicProjectionAndViewingAccordingToMyConvention()

        myLatexObject = LatexTextureObject("Obj 1")
        axis = Axis()

        symbol_geometries = tests.svgpathtodat.main.get_test_symbol_geometries()
 
        polygontest = Polygon2dTestTriangles(symbol_geometries)

        polygontest.initiateTranslationMovement(v_x=1., duration=1.)
        
        render.setAntialias(AntialiasAttrib.MAuto)

        childs = render.getChildren()
        print(len(childs))


app = MyApp()
app.run()
