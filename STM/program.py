import os
import sys
from services.control_service import ControlService

if __name__ == '__main__':

    DEBUG = 1
    if DEBUG == 1:
        execution_path = os.getcwd()
        control_file = "test_Control_Service_1.ctl"
        control_file = os.path.join(execution_path, control_file)
        exe = ControlService(control_file=control_file)
        state = exe.execute()
        exit(state)
    else:
        from sys import argv
        exe = ControlService(control_file=argv[1])
        state = exe.execute()
        exit(state)