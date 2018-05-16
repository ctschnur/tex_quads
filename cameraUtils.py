from bunchOfImports import *

def setupOrthographicProjectionAndViewingAccordingToMyConvention():
    # setup orthographic projection, make camera fixed and look at origin.
    # In this script, the convention is to have the z axis (z axis is up in
    # p3d) centered horizontally, pointing up, and the 3d world coordinate
    # space origin centered in the middle of the window, the window only
    # shows a range of $z \in [-1, +1]$

    # the main camera can be accessed by base.cam or base.camera
    # You can even get the Matrix associated with that camera
    # I'm not sure what the difference between Lens Matrices and Camera
    # Matrices are
    # mat = base.cam.getMat()
    # print("cam.getMat(): ", mat) 

    # The camera already comes with a Lens(), but I want to set my own
    # make custom orthographic Lens() (the camera is just a Node)
    # orthographic: setting the projection matrix
    lens = OrthographicLens()

    # The total height ($z \in [-1, +1]$) is here fixed to be 2.
    # setting the view matrix as a function of the p3d window's 
    # aspect ratio
    lens_view_height_in_world_coords = 2.
    lens_view_width_in_world_coords = (
            lens_view_height_in_world_coords * (winsizex/winsizey))
    print(
        lens_view_width_in_world_coords,
        lens_view_height_in_world_coords)
    # setFilmSize specifies the size of the Lens box
    # I call it a *viewing box* if the projection matrix produces 
    # orthogonal projection, and *viewing frustum* if the projection
    # matrix includes perspective)
    lens.setFilmSize(lens_view_width_in_world_coords, lens_view_height_in_world_coords)
    
    # you can also check for the properties of your lens/camera
    print("orthographic: ", lens.isOrthographic())
    # finally, set the just created Lens() to your main camera
    base.cam.node().setLens(lens)

    # Make sure that what you want to display is within the Lenses box
    # (beware of near and far planes) 
    # Since it's orthogonal projection, letting the camera's position
    # vary doesn't do anything to the displayed content (except maybe
    # hiding it beyond the near/far planes) 
    base.cam.setPos(0, -1, 0)  # this manipulates the viewing matrix
