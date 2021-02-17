import os
import subprocess

def test_c(c_file):
    exe = c_file+".exe"
    if os.path.exists(exe):
        os.unlink(exe)
    print(open(c_file).read())
    subprocess.check_output(["cc", "-o", exe, c_file])
    subprocess.call([exe])