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
        myLatexObject.initiateTranslationMovement(v_x=1.5, v_z=0., duration=1., delay=0.)
        myLatexObject2 = LatexObject(r"$a \cdot b  - \frac{c}{d}$")
        myLatexObject2.initiateTranslationMovement(v_x=1.5, v_z=0., duration=1., delay=0.)

        # numberLine = Line()
        # numberLine.initiateTranslationMovement(v_x=0., v_z=0., duration=1., delay=0.)
        # numberLine.initiateRotationMovement(r=20., duration=1.)
        # numberLine.initiateScalingMovement(s_x=.5, duration=1.)
        
        # numberLine = Line()
        # numberLine.initiateTranslationMovement(v_x=-1., v_z=0., duration=1., delay=0.)

        # Arrow = ArrowHead()
        # Arrow.initiateTranslationMovement(v_x=1., v_z=0., duration=1., delay=0.)

        axis = Axis()
        
        # childs = render.getChildren()
        # for c_child in childs: 
        #     c_child.showBounds()

app = MyApp()
app.run()
