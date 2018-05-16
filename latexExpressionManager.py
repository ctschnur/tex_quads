from bunchOfImports import *
import textureUtils

import os
import subprocess
import hashlib
import glob

LATEX_SUBFOLDER = "latex_compiled"

class LatexImageManager: 
    # this class should for now only have a single instance
    # static variables (1st level)

    # the m_set's are populated with the LatexImage objects themselves

    # *accessible* means that image and hash can be retrieved somehow
    m_set_to_be_compiled = set()

    m_set_compiled = set()

    # aka the hash and image data is loaded
    m_set_loaded = set()

    subfolder = LATEX_SUBFOLDER

    @staticmethod
    def loadAllCompiledImages():
        # go through self.subfolder and create PNMImages
        png_filename_list = glob.glob('./*.png')
        for c_filename in png_filename_list: 
            # first check if image is already loaded
            # get the hash
            hash_from_filename = os.path.splitext(os.path.basename(c_filename))[0]
            # search the m_set_loaded for it, if it's not in there, load it
            already_loaded = False
            for c_loaded_latexImage in LatexImageManager.m_set_loaded:
                if c_loaded_latexImage.shaHash is hash_from_filename:
                    already_loaded = True
                    continue

            if already_loaded is False: 
                LatexImageManager.m_set_loaded.insert(c_latexImage)
                c_latexImage = LatexImage(subfolder=self.subfolder, shaHash=hash_from_filename) 
                pnm_image = textureUtils.getImageFromFile(filename=c_filename)

            # no matter what, 
            # we add it also to compiled (since the png exists)
            # and also to accessible (since png filename contains hash and
            # png exists)
            LatexImageManager.m_set_compiled.insert(c_latexImage)

    def addToBeCompiled(latexImage):
        # maybe this can happen asynchronoulsy in the future?
        # until then, it would be useful to have a catalogue at the start
        # of all latex expressions that are then computed right at the start
        # but maybe, that's also not the best strategy
        # first check if it's really not compiled (by hash)
        for c_compiled_latexImage in LatexImageManager.m_set_compiled:
            if latexImage.shaHash is c_compiled_latexImage.shaHash: 
                break

        # if it goes through until here, compile it 
        latexImage.compileToPNG()
        LatexImageManager.m_set_compiled.insert(latexImage)


class LatexImage:
    # a LatexImage can in theory be incomplete. 
    # it doesn't necessarily need an expression_str, if it's just loaded 
    # by a hash (created from an expression_str) from disk
    def __init__(self, 
            expression_str=None, 
            shaHash=None, 
            tex_xcolor="white", 
            subfolder=LATEX_SUBFOLDER, 
            p3d_PNMImage=None):
        # hash
        self.name_hash = hashlib.sha256(str(expression_str).encode("utf-8")).hexdigest()

        # latex expression
        # You have to escape dollar signs if passed as arguments as of this version
        self.expression_str = expression_str
        
        # image file
        self.subfolder = subfolder
        self.fullfilepath_without_extentsion = os.getcwd() + "/" + self.name_hash
        self.p3d_PNMImage = p3d_PNMImage

        # misc 
        self.tex_xcolor = tex_xcolor  # isn't actually used as of now

    def compileToPNG(self, load_p3d_PNMImage=True):
        latexcommands = (r'''
        \documentclass[convert={density=300,outext=.png},preview]{standalone}
        \usepackage{xcolor}
        \color{white}
        \begin{document}
        \color{white}
        ''' + expression_str + 
        r'''
        \end{document}
        ''')

        print("compiling ", self.fullfilepath_without_extentsion)

        with open(self.fullfilepath_without_extentsion + '.tex','w') as f:
            f.write(latexcommands)

        cmd = ['pdflatex', '-interaction', 'nonstopmode', '-shell-escape', "\"" + self.name_hash + '.tex' + "\""]
        proc = subprocess.Popen(cmd)
        proc.communicate()

        # deal with success/failure
        retcode = proc.returncode
        if not retcode == 0:
            os.unlink(self.name_hash + '.pdf')
            raise ValueError('Error {} executing command: {}'.format(retcode, ' '.join(cmd))) 

        # delete all auxiliary files
        os.unlink(self.fullfilepath_without_extentsion + '.tex')
        os.unlink(self.fullfilepath_without_extentsion + '.log')
        os.unlink(self.fullfilepath_without_extentsion + '.aux')

        # LatexImage can also be in a state where the image is not loaded
        # but for now, it always also loads the pnmImage from disk
        if load_p3d_PNMImage is True:
            self.p3d_PNMImage = textureUtils.getImageFromFile(filename=self.fullfilepath_without_extentsion + ".png")

