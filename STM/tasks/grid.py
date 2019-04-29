"""

Make grids for KPI calculations

"""

from tasks.task_status import TaskStatus
from tasks.task import Task
from tasks.config import ConfigureExecution

import os
import subprocess


class ProcessGrids(Task):
    family = 'KPI_PreProcessor'

    def __init__(self, previous_steps, step_id='00'):
        super().__init__(previous_steps)
        self.logger = None
        self.step_id = step_id

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

    def generate_network_shapefiles(self):
        if self.state == TaskStatus.OK:
            _environ = dict(os.environ)
            control_template_dir = os.path.join(self.common_dir, 'STM/STM_A/Control_Template')
            executable = os.path.join(self.stma_software_dir, 'ArcNet.exe')
            env = {
                'SCEN_DIR': self.scen_dir,
                'COMMONDATA': self.common_dir,
                'NUMBER_THREADS': str(self.threads)
            }
            env = {**env, **_environ}
            control_file = os.path.join(control_template_dir, 'ArcNet.ctl')

            process = subprocess.Popen(args=[executable, '-k -n', control_file], env=env)
            exitcode = process.wait()
            if exitcode == 1:
                self.state = TaskStatus.FAIL
                self.logger.error('Generate Network Shapefiles Failed')
            if self.state != TaskStatus.OK:
                self.logger.info('Generate Network Shapefiles Completed')

    def generate_performance_shapefiles(self):
        if self.state == TaskStatus.OK:
            _environ = dict(os.environ)
            control_template_dir = os.path.join(self.common_dir, 'STM/STM_A/Control_Template')
            executable = os.path.join(self.stma_software_dir, 'ArcPerf.exe')
            env = {
                'SCEN_DIR': self.scen_dir,
                'COMMONDATA': self.common_dir,
                'NUMBER_THREADS': str(self.threads)
            }
            env = {**env, **_environ}
            controls = ('ArcPerf_Daily.ctl', 'ArcPerf_AM.ctl', 'ArcPerf_PM.ctl')
            controls = [os.path.join(control_template_dir, f) for f in controls]

            processes = [subprocess.Popen(args=[executable, '-k -n', control], env=env) for control in controls]
            exitcodes = [p.wait() for p in processes]

            for exitcode in exitcodes:
                if exitcode == 1:
                    self.state = TaskStatus.FAIL
                    self.logger.error('Generate Performance Shapefiles Failed')
            if self.state != TaskStatus.OK:
                self.logger.info('Generate Performance Shapefiles Completed')

            os.environ.update(_environ)

    def generate_grids(self):
        if self.state == TaskStatus.OK:
            _environ = dict(os.environ)
            control_template_dir = os.path.join(self.common_dir, 'STM/STM_A/Control_Template')
            executable = os.path.join(self.stma_software_dir, 'GridData.exe')
            env = {
                'SCEN_DIR': self.scen_dir,
                'COMMONDATA': self.common_dir,
                'NUMBER_THREADS': str(self.threads)
            }
            env = {**env, **_environ}
            controls = ['GridData'+str(i)+'.ctl' for i in range(12, 18)]
            controls = [os.path.join(control_template_dir, f) for f in controls]

            for i, control in enumerate(controls):
                process = subprocess.Popen(args=[executable, '-k -n', control], env=env)
                exitcode = process.wait()
                if exitcode == 1:
                    self.state = TaskStatus.FAIL
                    self.logger.error('Generate Grid Data Step {:d} Failed'.format(i+1))
                else:
                    self.logger.info('Generate Grid Data Step {:d} Completed'.format(i+1))

    def run(self):
        """

        :return:
        """
        # self.generate_network_shapefiles()
        # self.generate_performance_shapefiles()
        # self.generate_grids()

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