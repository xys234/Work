"""

Initialize STM-A Quick Network, Plans, and Trips

"""

from tasks.task_status import TaskStatus
from tasks.task import Task

import os
import subprocess


class InitInternals(Task):
    family = 'Traffic_Predictor'

    def __init__(self, previous_steps, step_id='00'):
        super().__init__(previous_steps, step_id=step_id)
        self.logger = None

        self.base = None
        self.scen = None
        self.mode = None
        self.swift_dir = None
        self.stma_software_dir = None
        self.base_dir = None
        self.scen_dir = None
        self.local_network = None
        self.common_dir = None
        self.threads = 1

    def prepare(self):
        configure_execution = self.previous_steps[0]
        if configure_execution.state == TaskStatus.OK:
            self.swift_dir = configure_execution.swift_dir
            self.base = configure_execution.base
            self.scen = configure_execution.scen
            self.mode = configure_execution.mode
            self.base_dir = configure_execution.base_dir
            self.scen_dir = configure_execution.scen_dir
            self.logger = configure_execution.logger
            self.local_network = configure_execution.local_network
            self.common_dir = configure_execution.common_dir
            self.stma_software_dir = configure_execution.stma_software_dir
            self.threads = configure_execution.threads
        super().prepare()
        return self.state

    def require(self):
        if self.state == TaskStatus.OK:

            self.logger.info('Number of Threads  = {:d}'.format(self.threads))

            trajectory_dir = self.scen_dir
            if self.mode == 'QUICK':
                trajectory_dir = self.base_dir
            trajectory_file = os.path.join(trajectory_dir, r'STM/STM_A/01_DynusT/03_Model', 'vehtrajectory.itf')
            if not os.path.isfile(trajectory_file):
                self.state = TaskStatus.FAIL
                self.logger.info('{:s} Mode. Required Trajectory File {:s} Not Found'.format(self.mode,
                                                                                             trajectory_file))
            else:
                self.logger.info('{:s} Mode. Required Trajectory File {:s} Found'.format(self.mode, trajectory_file))
        return self.state

    def convert_network_and_plans(self):
        if self.state != TaskStatus.OK:
            return

        control_template_dir = os.path.join(self.common_dir, 'STM/STM_A/Control_Template')
        control_file = os.path.join(control_template_dir, 'DynusTPrep.ctl')
        executable = os.path.join(self.stma_software_dir, 'DynusTPrep.exe')
        _environ = dict(os.environ)

        plan, trip = 'FINAL_Plans', 'FINAL_Trips'
        if self.mode == 'QUICK':
            trajectory_dir = self.base_dir
            plan, trip = 'Plans', 'Trips'
        else:
            trajectory_dir = self.scen_dir

        env = {
            'SCEN_DIR': self.scen_dir,
            'COMMONDATA': self.common_dir,
            'SCEN': trajectory_dir,
            'NUMBER_THREADS': str(self.threads),
            'PLAN': plan,
            'TRIP': trip
        }
        env = {**env, **_environ}
        processes = [subprocess.Popen(args=[executable, '-k', '-n', control_file], env=env)]
        exitcodes = [p.wait() for p in processes]

        for exitcode in exitcodes:
            if exitcode == 1:
                self.state = TaskStatus.FAIL
                self.logger.error('Conversion to Internal Data Failed')

        os.environ.update(_environ)

    def run(self):
        """

        :return:
        """
        # self.convert_network_and_plans()

    def complete(self):
        pass

    def execute(self):
        self.prepare()

        self.logger.info('')
        self.logger.info(
            'TASK {:s}_{:s}_{:s}: STATUS = START'.format(self.family, self.step_id, self.__class__.__name__))
        self.logger.info('')

        self.require()
        self.run()
        self.complete()

        message = 'TASK {:s}_{:s}_{:s}: STATUS = {:15s}'.format(
            self.family, self.step_id, self.__class__.__name__, str(self.state))

        self.logger.info('')
        self.logger.info('')
        self.logger.info(message)
        self.logger.info('')
        self.logger.info('')
        return self.state
