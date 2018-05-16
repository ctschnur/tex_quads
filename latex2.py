import os
import subprocess
import hashlib

def ImgFileFromTexExpr(expression_str, tex_xcolor="white"):
    latexcommands = (r'''
    \documentclass[convert={density=300,outext=.png},preview]{standalone}
    \usepackage{xcolor}
    \color{white}
    \begin{document}
    \color{white}
    ''' + expression_str + 
    # r'''
    # \begin{equation}
    # L = 2
    # \end{equation}
    # Hello. This is a test.
    r'''
    \end{document}
    ''')
    # You have to escape dollar signs if passed as arguments as of this version

    # give it a name (a hash generated from expression)
    name_hash = hashlib.sha256(str(expression_str).encode("utf-8")).hexdigest()

    # import ipdb; ipdb.set_trace()  # noqa BREAKPOINT

    print(name_hash)

    with open(name_hash + '.tex','w') as f:
        f.write(latexcommands)

    # cmd = ['pdflatex', '-interaction', 'nonstopmode', 'sample.tex', '-shell-escape']
    cmd = ['pdflatex', '-interaction', 'nonstopmode', '-shell-escape', "\"" + name_hash + '.tex' + "\""]
    proc = subprocess.Popen(cmd)
    proc.communicate()

    retcode = proc.returncode
    if not retcode == 0:
        os.unlink(name_hash + '.pdf')
        raise ValueError('Error {} executing command: {}'.format(retcode, ' '.join(cmd))) 

    os.unlink(name_hash + '.tex')
    os.unlink(name_hash + '.log')
    os.unlink(name_hash + '.aux')


while True:
    ImgFileFromTexExpr("hello world")
