
from services.sys_defs import *

if __name__ == '__main__':
    from sys import argv
    import time
    print(argv[1])
    print("Testing {0:d}".format(Codes_Execution_Status.OK))
    time.sleep(10)
