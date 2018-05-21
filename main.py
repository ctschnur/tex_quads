from bunchOfImports import *
from customGeometry import *
from textureUtils import *
from cameraUtils import *
from latexDisplayConventions import *
from latexObject import *

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

        
        numberLine = Line()
        numberLine.initiateTranslationMovement(v_x=.5, v_z=.3, delta_t=3., delay=0.)
        
        Arrow = ArrowForLine()
        # Arrow.initiateTranslationMovement(v_x=.5, v_z=.3, delta_t=3., delay=0.)
        
        # childs = render.getChildren()
        # for c_child in childs: 
        #     c_child.showBounds()

app = MyApp()
app.run()
