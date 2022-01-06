from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Mat4,
    Vec3,
    Vec4,
    PandaSystem,
    OrthographicLens,
    loadPrcFileData,
    AmbientLight,
    Point3)

import engine.tq_graphics_basics

import numpy as np

print("Panda version:", PandaSystem.getVersionString())

svgcleaner_path = 'tests/svgpathmanipulaton/svgcleaner/svgcleaner'

# p3d window
winsize_scale_factor_0 = 100 * 0.75
winsizex_0 = int(16. * winsize_scale_factor_0)
winsizey_0 = int(9. * winsize_scale_factor_0)

print("winsizex_0 = ", winsizex_0, ", ", "winsizey_0 = ", winsizey_0)

loadPrcFileData('', 'win-size ' + str(winsizex_0) + ' ' + str(winsizey_0))

# p3d window positon within OS gui in pixels; (0,0) is upper left of OS GUI
# puts the upper left corner of the p3d window at that position
loadPrcFileData('', 'win-origin 10 -1')


def getMat4_scale_unit_quad_to_image_aspect_ratio_forrowvecs(image_width_pixels, image_height_pixels):
    # the height stays constant (height of 1 in world coords)
    quad_scalex = float(image_width_pixels)
    quad_scalez = float(image_height_pixels)
    return Mat4(quad_scalex * 1., 0, 0, 0,
                0, 1, 0, 0,
                0, 0, quad_scalez * 1., 0,
                0, 0, 0, 1)


def getMat4_scale_unit_quad_to_image_aspect_ratio(image_width_pixels, image_height_pixels):
    # the height stays constant (height of 1 in world coords)
    quad_scalex = float(image_width_pixels)
    quad_scalez = float(image_height_pixels)
    return np.array([[quad_scalex * 1., 0, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, quad_scalez * 1., 0],
                     [0, 0, 0, 1]])

def get_pixels_per_unit():
    return engine.tq_graphics_basics.get_window_size_y()/2.


def getMat4_scale_quad_for_texture_pixels_to_match_screen_resolution_forrowvecs():
    # a single unit takes an amount of pixels of the p3d window
    # by convention here, the height of what the initial fixed camera
    # displays is exactly 2, i.e. the distance d((0,0,-1), (0,0,1))
    pixels_per_unit = get_pixels_per_unit()
    return Mat4(1./pixels_per_unit, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1./pixels_per_unit, 0,
                0, 0, 0, 1)


def getMat4_scale_quad_for_texture_pixels_to_match_screen_resolution():
    # a single unit takes an amount of pixels of the p3d window
    # by convention here, the height of what the initial fixed camera
    # displays is exactly 2, i.e. the distance d((0,0,-1), (0,0,1))
    pixels_per_unit = get_pixels_per_unit()
    return Mat4(1./pixels_per_unit, 0, 0, 0,
                0, 1, 0, 0,
                0, 0, 1./pixels_per_unit, 0,
                0, 0, 0, 1)


def setupOrthographicProjectionAndViewingAccordingToMyConvention(
        lookat_position=Vec3(0, 0, 0),
        camera_position=Vec3(5, 5, 2)):
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

    lens_view_height_in_world_coords = 5.
    lens_view_width_in_world_coords = (
        lens_view_height_in_world_coords * engine.tq_graphics_basics.get_window_aspect_ratio())

    print(
        lens_view_width_in_world_coords,
        lens_view_height_in_world_coords)
    # setFilmSize specifies the size of the Lens box
    # I call it a *viewing box* if the projection matrix produces
    # orthogonal projection, and *viewing frustum* if the projection
    # matrix includes perspective)
    lens.setFilmSize(lens_view_width_in_world_coords,
                     lens_view_height_in_world_coords)
    lens.setNearFar(0.001, 50.)

    # you can also check for the properties of your lens/camera
    print("orthographic: ", lens.isOrthographic())
    # finally, set the just created Lens() to your main camera
    base.cam.node().setLens(lens)

    # Make sure that what you want to display is within the Lenses box
    # (beware of near and far planes)
    # Since it's orthogonal projection, letting the camera's position
    # vary doesn't do anything to the displayed content (except maybe
    # hiding it beyond the near/far planes)

    # this manipulates the viewing matrix
    base.cam.setPos(camera_position[0], camera_position[1], camera_position[2])
    base.cam.lookAt(lookat_position)  # this manipulates the viewing matrix

    # -- set faint ambient white lighting
    from panda3d.core import AmbientLight
    alight = AmbientLight('alight')
    alnp = engine.tq_graphics_basics.tq_render.attachNewNode_p3d(alight)
    alight.setColor(Vec4(0.35, 0.35, 0.35, 1))
    engine.tq_graphics_basics.tq_render.setLight(alnp)


def compute2dPosition(nodepath, point=Point3(0, 0, 0)):
    """ Computes a 3-d point, relative to the indicated node, into a
    2-d point as seen by the camera.  The range of the returned value
    is based on the len's current film size and film offset, which is
    (-1 .. 1) by default. """

    # Convert the point into the camera's coordinate space
    p3d = base.cam.getRelativePoint(nodepath, point)

    # Ask the lens to project the 3-d point to 2-d.
    p2d = Point2()
    if base.camLens.project(p3d, p2d):
        # Got it!
        return p2d

    # If project() returns false, it means the point was behind the
    # lens.
    return None


def getFilmCoordsFromMouseCoords(m_x, m_y, p_x_0=0., p_y_0=0.):
    """ get actual orthogonal viewing film coordinates,
    (like those returned by getFilmSize())
    (dependent on the window's aspect ratio)
    args:
        m_x, m_y : mouse coordinates, between -1 and 1 (window edges)
        p_x_0, p_y_0 : offsets

    returns: two numbers between p_x(or y)_0 + (-1)*filmsize_x(or y) /2 and p_x(or y)_0 + filmsize_x(or y) /2 """
    filmsize = base.cam.node().getLens().getFilmSize()
    # print("filmsize: ", filmsize)

    p_x = p_x_0 + m_x * filmsize[0] / 2.
    p_y = p_y_0 + m_y * filmsize[1] / 2.

    return p_x, p_y
