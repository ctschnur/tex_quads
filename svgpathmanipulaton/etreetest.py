# Then, flatten it
import xml.etree.ElementTree as ET
import copy
import re

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

                print(x, y)
                # print(use.attrib['x'])

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

tree.write("output.svg")


# eventually concatenate all strings and write them to file in between
# <svg> tags, without groups, without uses without symbols
