# call e.g. 
# $ python3 main.py -c "ww \$a\$" 
# You have to escape dollar signs if passed as arguments as of this version

import argparse
import os
import subprocess


def ImgFileFromTexExpr(expression, tex_xcolor="white"):
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
    
    with open('sample.tex','w') as f:
        f.write(latexcommands)

    # cmd = ['pdflatex', '-interaction', 'nonstopmode', 'sample.tex', '-shell-escape']
    cmd = ['pdflatex', '-interaction', 'nonstopmode', '-shell-escape', 'sample.tex']
    proc = subprocess.Popen(cmd)
    proc.communicate()

    retcode = proc.returncode
    if not retcode == 0:
        os.unlink('sample.pdf')
        raise ValueError('Error {} executing command: {}'.format(retcode, ' '.join(cmd))) 

    os.unlink('sample.tex')
    os.unlink('sample.log')


# parser = argparse.ArgumentParser()
# parser.add_argument('-c', '--content', type=str) 
# args = parser.parse_args()
ImgFileFromTexExpr("hey there ", tex_xcolor="white")
