from bunchOfImports import *


class LatexObject:

    def __init__(latex_expr_str):
        return

    def compileLatexToImage():
        ImgFileFromTexExpr(expression_str, tex_xcolor="white")


import os
import subprocess

latexcommands = (r'''
\documentclass[convert={density=300,outext=.png},preview]{standalone}
\usepackage{xcolor}
\color{white}
\begin{document}
\color{white}
''' + expression + 
# r'''
# \begin{equation}
# L = 2
# \end{equation}
# Hello. This is a test.
r'''
\end{document}
''')


def ImgFileFromTexExpr(expression_str, tex_xcolor="white"):
    # You have to escape dollar signs if passed as arguments as of this version

    # give it a name (a hash generated from expression)
    name_hash = str(hash(expression_str))

    with open(name_hash + '.tex','w') as f:
        f.write(latexcommands)

    # cmd = ['pdflatex', '-interaction', 'nonstopmode', 'sample.tex', '-shell-escape']
    cmd = ['pdflatex', '-interaction', 'nonstopmode', '-shell-escape', name_hash + '.tex']
    proc = subprocess.Popen(cmd)
    proc.communicate()

    retcode = proc.returncode
    if not retcode == 0:
        os.unlink(name_hash + '.pdf')
        raise ValueError('Error {} executing command: {}'.format(retcode, ' '.join(cmd))) 

    os.unlink(name_hash + '.tex')
    os.unlink(name_hash + '.log')


