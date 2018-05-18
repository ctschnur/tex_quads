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

    m_set_compiled = set()
    m_set_loaded = set()  # aka the hash and pnm_image are given

    subfolder = LATEX_SUBFOLDER

    @staticmethod 
    def getImageIfLoaded(expr_hash):
        for img in LatexImageManager.m_set_loaded:
            if img.sha_hash is expr_hash: 
                return img
        return None

    @staticmethod
    def loadImageIfCompiled(expr_hash):
        for img in LatexImageManager.m_set_compiled:
            if img.sha_hash is expr_hash: 
                LatexImage.assignImageFromCompiledFile()
                return img
        return None

    @staticmethod
    def retrieveLatexImageFromHash(expr_hash):

        # check first if it's loaded, if it is, return it
        image = LatexImageManager.getImageIfLoaded(expr_hash)
        if image is not None: 
            return image

        # if compiled, load it 
        image = LatexImageManager.loadImageIfCompiled(expr_hash)
        if image is not None: 
            m_set_loaded.add(image)
            return retrieveLatexImageFromHash(expr_hash)

        # if not compiled, you can't produce it from a hash
        # sometimes I have to remind myself of the KISS principle
        return None


    @staticmethod
    def addLatexImageToCompiledSet(myLatexImage): 
        # is there one with the same hash?
        for img in LatexImageManager.m_set_compiled:
            assert (img.sha_hash is not myLatexImage.sha_hash)

        LatexImageManager.m_set_compiled.add(myLatexImage)

    # -- operations on batches of images
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
                if c_loaded_latexImage.sha_hash is hash_from_filename:
                    already_loaded = True
                    continue

            if already_loaded is False: 
                LatexImageManager.m_set_loaded.add(c_latexImage)
                c_latexImage = LatexImage(subfolder=self.subfolder, sha_hash=hash_from_filename) 

            # no matter what, 
            # we add it also to compiled (since the png exists)
            # and also to accessible (since png filename contains hash and
            # png exists)
            LatexImageManager.m_set_compiled.add(c_latexImage)

class LatexImage:
    # a LatexImage can in theory be incomplete. 
    # it doesn't necessarily need an expression_str, if it's just loaded 
    # by a hash (created from an expression_str) from disk
    def __init__(self, 
            expression_str=None, 
            sha_hash=None, 
            tex_xcolor="white", 
            subfolder=LATEX_SUBFOLDER, 
            p3d_PNMImage=None):
        # hash
        self.sha_hash = hashlib.sha256(str(expression_str).encode("utf-8")).hexdigest()

        # latex expression
        # You have to escape dollar signs if passed as arguments as of this version
        self.expression_str = expression_str
        
        # image file
        self.subfolder = subfolder

        # spespecify all file paths
        import os
        self.directory = os.getcwd() + "/" + LATEX_SUBFOLDER
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)

        self.fullfilepath_without_extentsion = self.directory + "/" + self.sha_hash
        self.fullfilepath_tex_file = self.fullfilepath_without_extentsion + ".tex"
        self.fullfilepath_png_file = self.fullfilepath_without_extentsion + ".png"

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
        ''' + self.expression_str + 
        r'''
        \end{document}
        ''')

        print("compiling ", self.fullfilepath_without_extentsion)

        with open(self.fullfilepath_tex_file, 'w') as f:
            f.write(latexcommands)
        
        cmd = ['pdflatex', '-interaction', 'nonstopmode', '-shell-escape', "\"" + self.fullfilepath_tex_file + "\""]
        proc = subprocess.Popen(cmd, cwd=self.directory)
        proc.communicate()

        # deal with success/failure
        retcode = proc.returncode
        if not retcode == 0:
            os.unlink(self.sha_hash + '.pdf')
            raise ValueError('Error {} executing command: {}'.format(retcode, ' '.join(cmd))) 

        # delete all auxiliary files
        os.unlink(self.fullfilepath_without_extentsion + '.tex')
        os.unlink(self.fullfilepath_without_extentsion + '.log')
        os.unlink(self.fullfilepath_without_extentsion + '.aux')

        # LatexImage can also be in a state where the image is not loaded
        # but for now, it always also loads the pnmImage from disk
        if load_p3d_PNMImage is True:
            self.p3d_PNMImage = textureUtils.getImageFromFile(filename=self.fullfilepath_without_extentsion + ".png")

        return self.p3d_PNMImage

    def getPNMImage(self):
        assert (self.p3d_PNMImage is not None)
        return self.p3d_PNMImage
    
    def assignImageFromCompiledFile(self):
        image = PNMImage()
        image.read(Filename(str(self.sha_hash) + ".png"))
        self.p3d_PNMImage = image
