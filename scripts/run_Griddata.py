import os
import subprocess
import sys


def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    return_code = popen.wait()
    out = [line for line in popen.stdout]   # <class '_io.TextIOWrapper'>
    popen.stdout.close()
    return out, return_code


out, return_code = execute(["Griddata", "-k", "-n", "Griddata.ctl"])
print(return_code)
for line in out:
    if return_code:
        if line.strip().startswith("Warning") or line.strip().startswith("Error"):
            print(line, end="")


#to-do:
### redirect the messages to a log file
### understand <class '_io.TextIOWrapper'>
### 