from panda3d.core import (PNMImage, Filename, Texture)
import numpy as np
from PIL import Image
from io import BytesIO

def getImageFromFile(filename="sample.png"):
    """ """
    image = PNMImage()
    image.read(Filename(filename))
    return image


def getTextureFrom2d_bw_arr():
    """ """
    img_arr_2d = np.array([[0.5, 0.3, 0.2, 0.1, 0.0],
                           [0.5, 0.3, 0.2, 0.1, 0.0],
                           [0.5, 0.3, 0.2, 0.1, 0.0],
                           [0.5, 0.3, 0.2, 0.1, 0.0],
                           [0.5, 0.3, 0.2, 0.1, 0.0],
                           [0.5, 0.3, 0.2, 0.1, 0.0]]
                          ).astype(np.float32)

    num_of_pixels_x = np.shape(img_arr_2d)[1]
    num_of_pixels_y = np.shape(img_arr_2d)[0]

    current_texture = Texture()
    current_texture.setup2dTexture(
        num_of_pixels_x, num_of_pixels_y, Texture.T_float, Texture.F_luminance)
    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
    current_texture.setRamImage(img_arr_2d)
    return current_texture, num_of_pixels_x, num_of_pixels_y

def getTextureFromMatplotlibFigure(fig,
                                   flip_over_y_axis=False,
                                   make_white_transparent=False,
                                   make_black_white=False,
                                   backgroud_opacity=0.):
    """ the matplotlib image produces a numpy array in the following form:
    array([[[255, 255, 255, 255],
        [255, 255, 255, 255],
        [255, 255, 255, 255],
        ...,
        [255, 255, 255, 255],
        [255, 255, 255, 255],
        [255, 255, 255, 255]],

       ...,

       [[255, 255, 255, 255],
        [255, 255, 255, 255],
        [255, 255, 255, 255],
        ...,
        [255, 255, 255, 255],
        [255, 255, 255, 255],
        [255, 255, 255, 255]]], dtype=uint8)
    with a np.shape() of (num_x, num_y, num_channels)
    """
    # import matplotlib.pyplot as plt # import it on demand
    # # fig, ax = plt.subplots(1)
    fig_axes = fig.get_axes()

    # make background transparent (of all axes)
    fig.patch.set_alpha(backgroud_opacity)

    for ax in fig_axes:
        ax.patch.set_alpha(0.0)

    default_color_for_borders_and_labels = "white"

    for ax, color in zip(fig_axes, [default_color_for_borders_and_labels] * len(fig_axes)):
        ax.tick_params(color=color, labelcolor=color)
        for spine in ax.spines.values():
            spine.set_edgecolor(color)

    # x = np.linspace(0., 2.*np.pi, num=50)
    # ax.plot(x, np.sin(x))

    from matplotlib.backends.backend_agg import FigureCanvasAgg
    canvas = FigureCanvasAgg(fig)
    imgIO = BytesIO()
    canvas.print_png(imgIO, # dpi=my_dpi_resolution
    )

    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
    imgIO.seek(0)
    # imgData = BytesIO(imgIO.read())
    im = Image.open(imgIO)
    img_arr_2d = np.array(im)

    if flip_over_y_axis == True:
        img_arr_2d = np.flip(img_arr_2d, 0).astype(img_arr_2d.dtype)

    if make_white_transparent == True:
        final_pixel_arr = img_arr_2d.copy()
        final_pixel_arr[np.all(final_pixel_arr == [255, 255, 255, 255], axis=2)] = (
            [255, 255, 255, 0])
        img_arr_2d = final_pixel_arr
        

    num_of_pixels_x = np.shape(img_arr_2d)[1]
    num_of_pixels_y = np.shape(img_arr_2d)[0]
    num_of_channels = np.shape(img_arr_2d)[2]

    current_texture = Texture()
    current_texture.setup2dTexture(
        num_of_pixels_x, num_of_pixels_y, Texture.T_unsigned_byte, Texture.F_rgba)
    current_texture.setRamImage(img_arr_2d)

    return current_texture, num_of_pixels_x, num_of_pixels_y


def getTextureFromImage(pnmImage):
    print("myImage.getNumChannels(): ", pnmImage.getNumChannels())
    print("myImage.getXSize(): ", pnmImage.getXSize())
    print("myImage.getYSize(): ", pnmImage.getYSize())
    print("myImage.hasAlpha(): ", pnmImage.hasAlpha())

    # assign the PNMImage to a Texture (load PNMImage to Texture, opposite of store)
    myTexture = Texture()
    myTexture.load(pnmImage)
    return myTexture
