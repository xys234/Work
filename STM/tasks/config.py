from services.report_service import ReportService
from services.control_service import State

from tasks.task_status import TaskStatus
from tasks.task import Task

import os
import sys
import configparser


class ConfigureExecution(Task):

    family = 'Setup'
    step_id = '01'

    def __init__(self, base, scen, mode, local_network='FALSE'):
        super().__init__()
        self.base = base
        self.scen = scen
        self.mode = mode
        self.local_network = local_network

        if local_network.upper() == 'TRUE':
            self.local_network = True
        else:
            self.local_network = False

        self.config_file = None

        self.swift_dir = None
        self.stma_software_dir = None
        self.dynastuio_executable = None
        self.dynust_executable_name = None
        self.common_dir = None

        self.base_dir = None
        self.scen_dir = None

        self.config = None
        self.logger = None

    def check_dir(self, d, root_dir=None):
        if not os.path.exists(d):
            os.mkdir(d)
            if not os.path.exists(d):
                if root_dir is not None:
                    self.logger.error('{:60s} Failed to Create'.format(os.path.relpath(d, root_dir)))
                else:
                    self.logger.error('{:60s} Failed to Create'.format(d))
                return False
            else:
                if root_dir is not None:
                    self.logger.info('{:60s} Created'.format(os.path.relpath(d, root_dir)))
                else:
                    self.logger.info('{:60s} Created'.format(d))
                return True
        else:
            if root_dir is not None:
                self.logger.info('{:60s} Checked'.format(os.path.relpath(d, root_dir)))
            else:
                self.logger.info('{:60s} Checked'.format(d))
            return True

    def require(self):

        current_dir = os.getcwd()
        self.config_file = os.path.join(current_dir, '../../STMA_config.cfg')
        if not os.path.exists(self.config_file):
            self.state = State.ERROR
            sys.stderr('STM-A Configuration File {:s} Not Found - STM-A Failed'.format(self.config_file))
            return self.state

    def run(self):

        if self.state == TaskStatus.OK:

            parser = configparser.ConfigParser()
            parser.read(self.config_file)
            self.swift_dir = parser['SYSTEM']['SWIFT_Directory']
            self.stma_software_dir = parser['SYSTEM']['STMA_Software_Directory']
            self.dynastuio_executable = parser['SYSTEM']['DynuStudio_Executable']
            self.dynust_executable_name = parser['SYSTEM']['DynusT_Executable_Name']
            self.common_dir = os.path.join(self.swift_dir, 'CommonData')

            self.scen_dir = os.path.join(self.swift_dir, 'Scenarios', self.scen)
            self.logger = ReportService(os.path.join(self.scen_dir, self.scen + '_STM_A.log')).get_logger()
            if not self.check_dir(self.scen_dir):
                self.logger.error('Scenario {:s} Not Found at'.format(self.scen_dir))
                self.state = State.ERROR
                return self.state

            self.base_dir = os.path.join(self.swift_dir, 'Scenarios', self.base)
            if not os.path.exists(self.base_dir):
                self.logger.error('Baseline {:s} Not Found at'.format(self.base_dir))
                self.state = State.ERROR
                return self.state

            if self.mode.upper() == 'FULL':
                self.mode = "FULL"
            else:
                self.mode = 'QUICK'

            self.logger.info('Scenario {:s} Execution Starts'.format(self.scen))

            self.logger.info('')
            self.logger.info('TASK {:s}_{:s}_{:s}: START'.format(self.family, self.step_id, self.__class__.__name__))
            self.logger.info('')

            self.logger.info('Scenario Name      = {:s}'.format(self.scen))
            self.logger.info('Baseline Name      = {:s}'.format(self.base))
            self.logger.info('Execution Mode     = {:s}'.format(self.mode))
            self.logger.info('Use Local Network  = {:}'.format(self.local_network))
            self.logger.info('Configuration File = {:s}'.format(self.config_file))

    def complete(self):
        message = 'TASK {:s}_{:s}_{:s}: STATUS = {:15s}'.format(
            self.family, self.step_id, self.__class__.__name__, str(self.state))
        self.logger.info('')
        self.logger.info('')
        self.logger.info(message)
        self.logger.info('')
        self.logger.info('')

    def execute(self):
        self.require()
        self.run()
        self.complete()
        return self.state

