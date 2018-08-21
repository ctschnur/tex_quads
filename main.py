import conventions
from direct.showbase.ShowBase import ShowBase
from latex_object import LatexTextureObject, Axis, Polygon2d

class MyApp(ShowBase):
 
    def __init__(self):
        ShowBase.__init__(self)

        # make self-defined camera control possible
        self.disableMouse()  

        conventions.setupOrthographicProjectionAndViewingAccordingToMyConvention()

        # create some LatexObjects

        myLatexObject = LatexTextureObject("Obj 1")
        myLatexObject.initiateTranslationMovement(v_x=1.5, v_z=0., duration=1., delay=0.)
        myLatexObject2 = LatexTextureObject(r"$a \cdot b  - \frac{c}{d}$")
        myLatexObject2.initiateTranslationMovement(v_x=1.5, v_z=0., duration=1., delay=0.)

        axis = Axis()

        polygon2d = Polygon2d([
            [0.0, 0.0],
            [0.2, 1.2],
            [0.4, 1.5],
            [-0.9, 0.2]])

        childs = render.getChildren()
        print(len(childs))
        # for c_child in childs: 
        #     c_child.showBounds()


app = MyApp()
app.run()
