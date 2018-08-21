from direct.showbase.ShowBase import ShowBase

from panda3d.core import (
    Mat4,
    PandaSystem,
    OrthographicLens,
    loadPrcFileData)
print("Panda version:", PandaSystem.getVersionString())


svgcleaner_path = 'tests/svgpathmanipulaton/svgcleaner/svgcleaner'

# p3d window
winsizex = 480
winsizey = 272
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


def getMat4_scale_unit_quad_to_image_aspect_ratio(image_width_pixels, image_height_pixels):
    # the height stays constant (height of 1 in world coords)
    quad_scalex = float(image_width_pixels)
    quad_scalez = float(image_height_pixels)
    return Mat4(quad_scalex * 1., 0, 0, 0, 
                0, 1, 0, 0, 
                0, 0, quad_scalez * 1., 0, 
                0, 0, 0, 1)

def getMat4_scale_quad_for_texture_pixels_to_match_screen_resolution():
    # a single unit takes an amount of pixels of the p3d window
    # by convention here, the height of what the initial fixed camera 
    # displays is exactly 2, i.e. the distance d((0,0,-1), (0,0,1))
    pixel_per_unit = winsizey/2.
    # scale = (winsizey/screen_res_height)
    return Mat4(1./pixel_per_unit, 0, 0, 0, 
                0, 1, 0, 0, 
                0, 0, 1./pixel_per_unit, 0, 
                0, 0, 0, 1)

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
