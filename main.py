import conventions
from tests.svgpathmanipulaton.main import get_point_clouds_from_svg, read_flattened_svg

import tripy_modified

from direct.showbase.ShowBase import ShowBase
import numpy as np
from latex_object import LatexTextureObject, Axis, Polygon2d, Polygon2dTest, Polygon2dTestLineStrips

class MyApp(ShowBase):
 def __init__(self):
        ShowBase.__init__(self)

        # make self-defined camera control possible
        self.disableMouse()  

        conventions.setupOrthographicProjectionAndViewingAccordingToMyConvention()

        # create some LatexObjects

        # myLatexObject = LatexTextureObject("Obj 1")
        # myLatexObject3 = LatexTextureObject(r"$\frac{\pi}{ 4} $")

        myLatexObject = LatexTextureObject("Obj 1")
        # myLatexObject.initiateTranslationMovement(v_x=1.5, v_z=0., duration=1., delay=0.)
        # myLatexObject2 = LatexTextureObject(r"$a \cdot b  - \frac{c}{d}$")
        # myLatexObject2.initiateTranslationMovement(v_x=1.5, v_z=0., duration=1., delay=0.)

        axis = Axis()

        # point_clouds = get_point_clouds_from_svg("tests/svgpathmanipulaton/main.svg") 
        # polygon2d2 = Polygon2d(np.array(point_clouds[0])/10.)
        # cloud = np.array([(0,1), (-1, 0), (0, -1), (1, 0)])
        # polygon2d2 = Polygon2d(cloud)

        point_clouds = get_point_clouds_from_svg("tests/svgpathmanipulaton/main.svg")
        
        import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

        # polygontest = Polygon2dTest()
        
        polygontest = Polygon2dTestLineStrips()
        
        # polygon2d2 = Polygon2d(point_clouds[0])
        # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

        childs = render.getChildren()
        print(len(childs))


app = MyApp()
app.run()
