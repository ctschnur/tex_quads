import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import itertools

mpl_tableau_colors_rgba = [mpl.colors.to_rgba("tab:" + mpl_color_name) for mpl_color_name in [
    "blue", "orange", "green", "red", "purple", "brown", "pink", "gray", "olive", "cyan"]]

mpl_color_cycle = itertools.cycle(mpl_tableau_colors_rgba)

def get_next_mpl_color():
    """ from global mpl_color_cycle, get the next color (and cycle)
    Returns:
        tuple (r, g, b, a) where r,g,b,a are numbers between 0 and 1 """
    return next(mpl_color_cycle)


def get_color(mpl_str):
    """ get color, from mpl color specification
    Args:
        mpl_str: full string of the color name
                 (https://matplotlib.org/3.3.2/gallery/color/named_colors.html#sphx-glr-gallery-color-named-colors-py)
    Returns:
        tuple (r, g, b, a) where r,g,b,a are numbers between 0 and 1 """
    return mpl.colors.to_rgba(mpl_str)
