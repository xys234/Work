"""

Make DynusT Run

"""

from tasks.task_status import TaskStatus
from tasks.task import Task

import os
import subprocess
import shutil


class FullPredict(Task):
    family = 'DynusT'

    REQUIRED_LIBRARY = (
        'libifcoremd.dll',
        'libifportmd.dll',
        'libiomp5md.dll',
        'libmmd.dll',
        'svml_dispmd.dll',
        'pdbx.dll',
        'pdbx.dll',
        'miva2017.exe',
    )

    COMPLETE_RUN_MARKER = {
        'SummaryStat.dat'
        'VehTrajectory.itf'
    }

    def __init__(self, previous_steps, step_id='00'):
        super().__init__(previous_steps)
        self.logger = None
        self.step_id = step_id

        self.base = None
        self.scen = None
        self.mode = None
        self.swift_dir = None
        self.stma_software_dir = None
        self.dynust_dir = None
        self.dynastuio_executable = None
        self.dynust_executable_name = None
        self.base_dir = None
        self.scen_dir = None
        self.local_network = None
        self.common_dir = None
        self.threads = 1

        # Task specific variables
        self.run_completed = True

    def prepare(self):
        configure_execution = self.previous_steps[0]
        if configure_execution.state == TaskStatus.OK:
            self.swift_dir = configure_execution.swift_dir
            self.dynust_dir = configure_execution.dynust_dir
            self.dynastuio_executable = configure_execution.dynastudio_executable
            self.dynust_executable_name = configure_execution.dynust_executable_name
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
        """

        :return:
        """

        # Check if DynusT run has already been made
        model_dir = os.path.join(self.scen_dir, r'STM\STM_A\01_DynusT\03_Model')
        for f in self.COMPLETE_RUN_MARKER:
            if not os.path.isfile(os.path.join(model_dir, f)):
                self.run_completed = False
            else:
                self.logger.info('DynusT Output {:s} Found'.format(f))

        if self.run_completed:
            self.logger.info('DynusT Run Completed and are NOT re-run')
        else:
            # Check and Copy DynusT Executables
            if not os.path.exists(self.dynust_dir):
                self.state = TaskStatus.FAIL
                self.logger.error('Required DynusT Installation Not Found'.format(self.dynust_dir))
            else:
                dest = os.path.join(self.scen_dir, r'STM\STM_A\01_DynusT\03_Model')
                for e in self.REQUIRED_LIBRARY + (self.dynust_executable_name,):
                    check_file = os.path.join(self.dynust_dir, r'_exe\DynusT', e)
                    if not os.path.isfile(check_file):
                        shutil.copy2(check_file, os.path.join(dest, e))
                        self.logger.error('Required DynusT File {:s} Found'.format(check_file))
                    else:
                        self.state = TaskStatus.FAIL
                        self.logger.error('Required DynusT File {:s} Not Found'.format(check_file))

                # Check the vehicle roster
                check_file = os.path.join(self.scen_dir, r'STM\STM_A\01_DynusT\03_Model', 'vehicle.dat')
                if not os.path.isfile(check_file):
                    self.state = TaskStatus.FAIL
                    self.logger.error('Required DynusT Vehicle Roster {:s} Not Found'.format(check_file))

    def run_full_assignment(self):
        if self.state != TaskStatus.OK:
            return

        executable = self.dynastuio_executable
        username = os.environ['USERNAME']
        model_dir = os.path.join(self.scen_dir, r'STM\STM_A\01_DynusT\03_Model')

        process = subprocess.Popen(args=[executable, username, '0000', self.dynust_executable_name], cwd=model_dir)
        exitcode = process.wait()

        if not os.path.isfile(os.path.join(model_dir, 'executing')):
            self.info('DynusT Run Finished')
            self.run_completed = True

    def run(self):
        self.run_full_assignment()

    def complete(self):

        # Check if DynusT run is successfully made
        model_dir = os.path.join(self.scen_dir, r'STM\STM_A\01_DynusT\03_Model')

        for f in self.COMPLETE_RUN_MARKER:
            if not os.path.isfile(os.path.join(model_dir, f)):
                self.run_completed = False

        if self.run_completed:
            self.logger.info('Full Prediction Using DynusT Completed')
        else:
            self.logger.info('Full Prediction Using DynusT Failed')

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
