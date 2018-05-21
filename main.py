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

        myLatexObject = LatexObject("Obj 1")
        myLatexObject.initiateTranslationMovement(v_x=-1., delta_t=1.0, delay=0.5)
        myLatexObject2 = LatexObject(r"$a \cdot b  - \frac{c}{d}$")
        myLatexObject2.initiateTranslationMovement(v_x=1., delta_t=1.0)

app = MyApp()
app.run()
