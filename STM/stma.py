from tasks.task_status import TaskStatus
from tasks.config import ConfigureExecution
from tasks.initialize import InitializeEnvironment
from tasks.check_local_network import CheckLocalNetwork
from tasks.convert_trips import ConvertTrips

from services.report_service import ReportService

import time
import sys


def main(base, scen, mode, local):
    logger = ReportService('default_log')

    start_time = time.time()
    # Step 1
    task_configure_execution = ConfigureExecution(base, scen, mode, local_network=local)
    status = task_configure_execution.execute()
    if status == TaskStatus.OK:
        logger = task_configure_execution.logger

    # Step 2
    task_initialize_environment = InitializeEnvironment(previous_steps=[task_configure_execution])
    status = task_initialize_environment.execute()

    #
    task_check_local_network = CheckLocalNetwork(previous_steps=[task_configure_execution, task_initialize_environment])
    status = task_check_local_network.execute()

    #
    task_convert_trips = ConvertTrips(previous_steps=[task_configure_execution, task_check_local_network])
    status = task_convert_trips.execute()

    end_time = time.time()
    execution_time = max((start_time - end_time) / 60.0, 0.0)

    if status == TaskStatus.OK:
        logger.info('STMA Completed in {:.2f} minutes'.format(execution_time))
    else:
        logger.error('STMA Completed with Error in {:.2f} minutes'.format(execution_time))
    return status.value


if __name__ == '__main__':
    DEBUG = 1
    if DEBUG:
        import os
        exec_dir = r'C:\Projects\SWIFT\SWIFT_Workspace\Software\STM_A'
        os.chdir(exec_dir)
        baseline, scenario, execution_mode, local_network = "S04_Base", "S04_Full", "FULL", "TRUE"
        status = main(baseline, scenario, execution_mode, local_network)
    else:
        from sys import argv
        baseline, scenario, execution_mode, local_network = argv[1], argv[2], argv[3], argv[4]
        # baseline, scenario, execution_mode = "S01_Base", "S01_Quick", "FULL"
        status = main(baseline, scenario, execution_mode, local_network)
        sys.exit(status.value)


