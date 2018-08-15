# Read SVG into a list of path objects and list of dictionaries of attributes
import numpy as np
from svgpathtools import Path, CubicBezier, svg2paths, wsvg, disvg, svg2paths2, parse_path, bpoints2bezier

import argparse
import os
import subprocess


def simplify_svg(filename_in='in.svg', filename_out='out.svg'):
    # First, simplify the svg using svgcleaner
    cmd = [
        'svgcleaner',
        str(filename_in),
        str(filename_out),
        'svgcleaner/svgcleaner',
        'in.svg',
        'out.svg',
        '--ungroup-groups',
        '--indent',
        '0',
        '--remove-invisible-elements',
        '--resolve-use',
        '--remove-needless-attributes',
        '--ungroup-defs',
        '--remove-unused-defs',
        '--trim-paths=false']
    proc = subprocess.Popen(cmd)
    proc.communicate()

    retcode = proc.returncode
    if not retcode == 0:
        os.unlink(str(filename_out))
        raise ValueError('Error {} executing command: {}'.format(retcode, ' '.join(cmd)))

def simplified_svg_custom_cleanup(filename_in='out.svg', filename_out='out2.svg'):
    # Then, flatten it
    # collect all individual <symbol>s with their id's 
    # then, collect all <use>s with their id's and x and y shifts
    # for each use you found, make a copy of the <symbol>s path and apply the x
    # and y shifts to the first m svg-command.
    # then, save it as a string 

    # eventually concatenate all strings and write them to file in between
    # <svg> tags, without groups, without uses without symbols


# paths, attributes, svg_attributes = svg2paths2('out.svg')
# disvg(paths, attributes=attributes)


# print(attributes)
# import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
#
#
# # print(len(paths))
# # for i in range(len(paths)):
# #     path = paths[i]
# #     path_attribs = attributes[i]
# #     print(path)
# #     try:
# #         print(path_attribs)
# #     except KeyError as e:
# #         print('I got a KeyError - reason ', str(e))
# #         print("hi")
#
# ## for some reason, there's an empty path at the beginning
# ## reassign paths to only contain all non-empty paths
# nonempty_paths = []
# nonempty_paths_attributes = []
# for idx, path in enumerate(paths):
#     # print(len(path))
#     if len(path) > 0:
#         nonempty_paths.append(path)
#         nonempty_paths_attributes.append(attributes[idx])
#
# import ipdb; ipdb.set_trace()  # noqa BREAKPOINT
#
# # cut the last thing off, it's some weird black bar
# # nonempty_paths = nonempty_paths[:-1]
# # nonempty_paths_attributes = nonempty_paths_attributes[:-1]
# paths = nonempty_paths
# attributes = nonempty_paths_attributes
# print(attributes)
# # attributes = [{} for elem in nonempty_paths]
#
# # ------ BEGIN custom created path  ----------
#
# # paths = [Path(CubicBezier(start=(10.5+80j), control1=(40+10j), control2=(65+10j), end=(95+80j)), CubicBezier(start=(95+80j), control1=(125+150j), control2=(150+150j), end=(180+80j)))]
# # attributes = [{'style': 'stroke:none'}]
#
# # ------ END custom created path  ----------
#
# # writing an svg
# print("------- writing an svg -------")
# wsvg(paths, attributes=attributes, filename='output1.svg')
