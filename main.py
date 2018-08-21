import conventions
from direct.showbase.ShowBase import ShowBase
from latexObject import LatexObject, Axis

class MyApp(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)

        # make self-defined camera control possible
        self.disableMouse()  

        conventions.setupOrthographicProjectionAndViewingAccordingToMyConvention()

        # create some LatexObjects

        myLatexObject = LatexObject("Obj 1")
        myLatexObject.initiateTranslationMovement(v_x=1.5, v_z=0., duration=1., delay=0.)
        myLatexObject2 = LatexObject(r"$a \cdot b  - \frac{c}{d}$")
        myLatexObject2.initiateTranslationMovement(v_x=1.5, v_z=0., duration=1., delay=0.)

        axis = Axis()
        
app = MyApp()
app.run()
