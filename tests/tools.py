import subprocess

def test_c(c_file):
    subprocess.check_output(["cc", "-o", c_file+".exe", c_file])
    subprocess.call([c_file+".exe"])