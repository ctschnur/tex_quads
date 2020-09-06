# Read SVG into a list of path objects and list of dictionaries of attributes
import numpy as np
from svgpathtools import Path, CubicBezier, svg2paths, wsvg, disvg, svg2paths2, parse_path, bpoints2bezier

from pathlib import PurePath

import os
import subprocess

import xml.etree.ElementTree as ET
import copy
import re

def simplify_svg(filename_in, filename_out):
    # First, simplify the svg using svgcleaner
    svgcleaner_path = PurePath(
        PurePath(str(__file__)).parent /
        PurePath("svgcleaner/svgcleaner"))



    cmd = [
        str(svgcleaner_path),
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

def simplified_svg_custom_cleanup(filename_in, filename_out):
    SVG_XLINK_NS = "{http://www.w3.org/1999/xlink}"
    SVG_NS = "{http://www.w3.org/2000/svg}"

    tree = ET.parse(str(filename_in))
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

    tree.write(str(filename_out))

def read_flattened_svg(filename_in): 
    paths, attributes = svg2paths(str(filename_in))

    # now you can extract the path coordinates (complex plane) with 
    # e.g. paths[0][0].control1.imag (for a CubicBezier 
    # type path segment)

    point_clouds = []
    num_intermediate_points = 10.

    for path in paths: 
        xs = []
        ys = []
        print("---------------------------")
        print(path)

        for segment in path: 
            xs.append(segment.start.real)
            ys.append(segment.start.imag)
            if type(segment) is CubicBezier: 
                for i in np.arange(1., num_intermediate_points):  # This probably needs adjustment
                    point = segment.point(i/num_intermediate_points)
                    xs.append(point.real)
                    ys.append(point.imag)

            xs.append(segment.end.real)
            ys.append(segment.end.imag)
        
        point_clouds.append(np.transpose([np.array(xs), np.array(ys)]))
    
    point_clouds = np.array(point_clouds)
    # disvg(paths, attributes=attributes)
    return point_clouds


def get_point_clouds_from_svg(svg_filename):

    simplified_svg_path = (
        PurePath(
            str(PurePath(svg_filename).stem) + 
            str(PurePath("_simplified_")) + 
            str(PurePath(svg_filename).suffix)))

    simplify_svg(svg_filename, 
                 simplified_svg_path)

    custom_cleaned_up_svg_path = (
        PurePath(
            str(PurePath(simplified_svg_path).stem) + 
            str(PurePath("_customcleaned_")) + 
            str(PurePath(simplified_svg_path).suffix)))

    simplified_svg_custom_cleanup(
        simplified_svg_path, custom_cleaned_up_svg_path)

    return read_flattened_svg(custom_cleaned_up_svg_path)


if __name__ == "__main__":
    get_point_clouds_from_svg("main.svg")

