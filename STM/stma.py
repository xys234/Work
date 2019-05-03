from tasks.task_status import TaskStatus
from tasks.config import ConfigureExecution
from tasks.initialize import InitializeEnvironment
from tasks.check_network import CheckNetwork
from tasks.convert_trips import ConvertTrips
from tasks.initialize_internals import InitInternals
from tasks.full_predict import FullPredict
from tasks.quick_predict import QuickPredict
from tasks.summarize import SummarizePlans
from tasks.grid import ProcessGrids
from tasks.update_network import UpdateNetwork

from services.report_service import ReportService

import time
import sys
from collections import OrderedDict


def workflow(base, scen, mode, local, config_file):
    # Common steps
    task_configure_execution = ConfigureExecution(base, scen, mode, config_file, local)
    task_initialize_environment = InitializeEnvironment(previous_steps=[task_configure_execution], step_id='01')
    task_check_network = CheckNetwork(previous_steps=[task_configure_execution, task_initialize_environment],
                                      step_id='02')
    task_modify_network = UpdateNetwork(previous_steps=[task_configure_execution, task_check_network], step_id='03')

    wf = OrderedDict(
        {
            'ConfigureExecution': task_configure_execution,
            'InitializeEnvironment': task_initialize_environment,
            'CheckNetwork': task_check_network,
            'ModifyNetwork': task_modify_network
        }
    )

    if mode.upper() == 'FULL':
        task_convert_trips = ConvertTrips(previous_steps=[task_configure_execution, task_check_network], step_id='04')
        task_full_predict = FullPredict(previous_steps=[task_configure_execution, task_convert_trips,
                                                        task_modify_network], step_id='05')
        task_init_internals = InitInternals(previous_steps=[task_configure_execution, task_full_predict], step_id='06')
        task_summarize_scenario = SummarizePlans(previous_steps=[task_configure_execution, task_init_internals],
                                                 step_id='07')
        task_grids = ProcessGrids(previous_steps=[task_configure_execution, task_summarize_scenario], step_id='08')

        wf['EstimateFullDemand'] = task_convert_trips
        wf['FullPredict'] = task_full_predict
        wf['InitializeInternals'] = task_init_internals
        wf['SummarizeScenario'] = task_summarize_scenario
        wf['KPIPreProcess'] = task_grids
    else:
        task_init_internals = InitInternals(previous_steps=[task_configure_execution, task_check_network],
                                            step_id='04')
        task_summarize_internals = SummarizePlans(previous_steps=[task_configure_execution, task_init_internals],
                                            step_id='05')
        task_quick_predict = QuickPredict(previous_steps=[task_configure_execution, task_init_internals], step_id='06')
        task_summarize_scenario = SummarizePlans(previous_steps=[task_configure_execution, task_quick_predict],
                                                 step_id='07')
        task_grids = ProcessGrids(previous_steps=[task_configure_execution, task_summarize_scenario], step_id='08')

        wf['InitializeInternals'] = task_init_internals
        wf['SummarizeInternals'] = task_summarize_internals
        wf['QuickPredict'] = task_quick_predict
        wf['SummarizeScenario'] = task_summarize_scenario
        wf['KPIPreProcess'] = task_grids

    return wf


def main(base, scen, mode, local, config_file):
    logger = ReportService('default_log')

    start_time = time.time()
    wf = workflow(base, scen, mode, local, config_file)
    steps = list(wf.keys())

    for name, step in wf.items():
        step.execute()
        if name == 'ConfigureExecution':
            logger = step.logger
            logger.info('----------------STMA WorkFlow------------------')
            for i, s in enumerate(steps):
                logger.info("Step {:d} - {:30s}".format(i+1, s))

    end_time = time.time()
    execution_time = max((end_time - start_time) / 60.0, 0.0)

    model_status = [s.state for s in wf.values()]
    model_status = {s: st for s, st in zip(steps, model_status)}

    logger.info('----------------STMA Execution Summary------------------')
    stma_status = TaskStatus.OK
    stepid = 0
    for step, status in model_status.items():
        stepid += 1
        logger.info('Step {:d} {:50s} Status = {:10s}'.format(stepid, step, str(status)))
        if status != TaskStatus.OK:
            stma_status = TaskStatus.FAIL

    if stma_status == TaskStatus.OK:
        logger.info('STMA Completed in {:.0f} minutes'.format(execution_time))
    else:
        logger.error('STMA Failed in {:.0f} minutes'.format(execution_time))
    return stma_status


if __name__ == '__main__':
    DEBUG = 0
    if DEBUG:
        import os
        exec_dir = r'C:\Projects\SWIFT\SWIFT_Workspace\Software\STM_A'
        config_file = r'C:\Projects\SWIFT\SWIFT_Workspace\CommonData\STM\STM_A\STMA_config.cfg'
        baseline, scenario, execution_mode, local_network = "Scenario_S0", "Scenario_S4_Quick", "Quick", "False"
        # baseline, scenario, execution_mode, local_network = "Scenario_S0", "Scenario_S4_Full", "Full", "False"
        status = main(baseline, scenario, execution_mode, local_network, config_file)
        sys.exit(status)
    else:
        from sys import argv
        baseline, scenario, execution_mode, local_network, config_file = argv[1], argv[2], argv[3], argv[4], argv[5]
        status = main(baseline, scenario, execution_mode, local_network, config_file)
        sys.exit(status)


