# Read SVG into a list of path objects and list of dictionaries of attributes
import numpy as np
from svgpathtools import Path, CubicBezier, svg2paths, wsvg, disvg, svg2paths2, parse_path, bpoints2bezier

import os
import subprocess

import xml.etree.ElementTree as ET
import copy
import re

def simplify_svg(filename_in='in.svg', filename_out='out.svg'):
    # First, simplify the svg using svgcleaner
    cmd = [
        'svgcleaner/svgcleaner',
        str(filename_in),
        str(filename_out),
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
    SVG_XLINK_NS = "{http://www.w3.org/1999/xlink}"
    SVG_NS = "{http://www.w3.org/2000/svg}"

    tree = ET.parse('out.svg')
    root = tree.getroot()

    # register all namespaces
    ET.register_namespace('', "http://www.w3.org/2000/svg")  # xmlns
    ET.register_namespace('xlink', "http://www.w3.org/1999/xlink")  # xmlns:xlink

    # collect all individual <symbol>s with their id's 
    symbols = list(root.iter('{0}symbol'.format(SVG_NS)))
    # then, collect all <use>s with their id's and x and y shifts
    uses = list(root.iter('{0}use'.format(SVG_NS)))

    # for each use you found, make a copy of the <symbol>s path and apply the x
    # and y shifts to the first m svg-command.
    # then, save it as a string 
    paths = []
    for use in uses:
        # get symbol from xlink:href property
        for symbol in symbols: 
            # strip the hashtag from the front
            if (use.attrib['{0}href'.format(SVG_XLINK_NS)][1:] ==
               symbol.attrib['id']):
                # copy the paths inside the symbol 
                for path in symbol:
                    pcopy = copy.deepcopy(path)
                    d = pcopy.attrib['d']
                    pattern = re.compile(r"^m(?:\s*[-\.\d]*\s){2}(.*)")
                    d_without_m = pattern.findall(d)[0]
                    # find x 
                    pattern = re.compile(r"^m(?:\s*([-\.\d]*)){1}")
                    x = pattern.findall(d)[0]
                    # find y
                    pattern = re.compile(r"^m(?:\s*([-\.\d]*)){2}")
                    y = pattern.findall(d)[0]

                    # print(x, y)

                    # add offset to x and y, if <use> has these
                    if 'x' in use.attrib:
                        x = str(float(x) + float(use.attrib['x']))
                    if 'y' in use.attrib:
                        y = str(float(y) + float(use.attrib['y']))
                    
                    move_string = "m " + x + " " + y + " "
                    new_d = move_string + d_without_m
                    # print(d)
                    # print(new_d)
                    pcopy.attrib['d'] = new_d
                    paths.append(pcopy)

    # remove all children
    for child in list(root):
        root.remove(child)
    root.extend(paths)

    tree.write("out2.svg")

def read_flattened_svg(filename_in='out2.svg'): 
    paths, attributes, svg_attributes = svg2paths2(filename_in)

    # now you can extract the path coordinates (complex plane) with 
    # e.g. paths[0][0].control1.imag (for a CubicBezier 
    # type path segment)
    print(paths[0][0].control1.imag)

    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

    print("end")
    
    disvg(paths, attributes=attributes)


simplify_svg()
simplified_svg_custom_cleanup()
read_flattened_svg()
