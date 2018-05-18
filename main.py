from bunchOfImports import *
from customGeometry import *
from textureUtils import *
from cameraUtils import *
from latexDisplayConventions import *
from latexObject import LatexObject

class MyApp(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)

        # make self-defined camera control possible
        self.disableMouse()  

        setupOrthographicProjectionAndViewingAccordingToMyConvention()

        # create some LatexObjects

        # for now, we only have one pre-compiled image, so the expressions
        # we provide don't actually do anything

        myLatexObject = LatexObject("myLatexObject")
        myLatexObject2 = LatexObject("myLatexObject2")
        myLatexObject2.translate(v_x=0.5, v_z=2.)

app = MyApp()
app.run()
