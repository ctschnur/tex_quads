from bunchOfImports import *

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

def getMat4_scaleUnitQuadProperly(image_width_pixels, image_height_pixels):
    return (
        getMat4_scale_quad_for_texture_pixels_to_match_screen_resolution() * 
        getMat4_scale_unit_quad_to_image_aspect_ratio(image_width_pixels, image_height_pixels))
