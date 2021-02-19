from pygments import highlight
from pygments.formatters import TerminalFormatter as Formatter
from pygments.lexers import get_lexer_by_name
import os
import subprocess

def test_c(c_file):
    exe = c_file+".exe"
    if os.path.exists(exe):
        os.unlink(exe)
    code = open(c_file).read()

    print(highlight(code, get_lexer_by_name("C"), Formatter()))

    subprocess.check_output(["cc", "-o", exe, c_file])
    subprocess.call([exe])