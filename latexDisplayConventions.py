from bunchOfImports import *

def getMat4_ScaleWidthOfUnitSquareToMatchAspectRatio(image_width_pixels, image_height_pixels):
    # the height stays constant (height of 1 in world coords)
    quad_scalex = (float(image_width_pixels)/float(image_height_pixels))
    return Mat4(quad_scalex * 1., 0, 0, 0, 
                0, 1, 0, 0, 
                0, 0, 1., 0, 
                0, 0, 0, 1)

def getMat4_MatchScreenResolution():
    scale = (winsizey/screen_res_height)
    return Mat4(scale * 1., 0, 0, 0, 
                0, 1, 0, 0, 
                0, 0, scale * 1., 0, 
                0, 0, 0, 1)

def getMat4_LatexQuadTrafo(image_width_pixels, image_height_pixels):
    aspect_ratio_width_scale_mat4 = getMat4_ScaleWidthOfUnitSquareToMatchAspectRatio(image_width_pixels, image_height_pixels)
    true_resolution_scale_mat4 = getMat4_MatchScreenResolution()
    return true_resolution_scale_mat4 * aspect_ratio_width_scale_mat4
