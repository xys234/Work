from services.sys_defs import *
from services.execution_service import Execution_Service


class NetworkPrep(Execution_Service):
    required_keys = (
        'NETWORK_FILE',
        'SCENARIO_PARAMETER_FILE',
    )

    acceptable_keys = (

    )

    def __init__(self, name='NetworkPrep', input_control_file='NetworkPrep.ctl'):
        super().__init__(name, input_control_file, NetworkPrep.required_keys, NetworkPrep.acceptable_keys)


if __name__ == '__main__':

    DEBUG = 0
    if DEBUG == 1:
        import os
        execution_path = r"C:\Projects\SWIFT\SWIFT_Project_Data\Controls"
        control_file = "TripPrep_toTabularTrips.ctl"
        control_file = os.path.join(execution_path, control_file)
        exe = NetworkPrep(input_control_file=control_file)
        exe.execute()
    else:
        from sys import argv
        exe = NetworkPrep(input_control_file=argv[1])
        exe.execute()