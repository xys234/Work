from services.report_service import ReportService
from services.control_service import State
from tasks.config import ConfigureExecution

import os


class InitializeEnvironment(object):

    STMA_FOLDER_STRUCT = {
        '01_DynusT': tuple(),
        '02_TrafficPredictor': ('01_Controls', '02_Network', '03_Demand', '04_Results'),
        '02_Performance_Summarizer': ('01_Controls', '02_Network', '03_Demand', '04_Results'),
        '04_KPI_PreProcessor': ('01_Controls', '02_Results')

    }

    def __init__(self, step_number=2):

        self.state = State.OK
        self.step_number = step_number
        self.logger = None

        self.base = None
        self.scen = None
        self.mode = None
        self.swift_dir = None
        self.stma_software_dir = None
        self.base_dir = None
        self.scen_dir = None

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

    def require(self, configure_execution):
        if not isinstance(configure_execution, ConfigureExecution):
            self.state = State.ERROR
        else:
            if configure_execution.state == State.OK:
                self.base = configure_execution.base
                self.scen = configure_execution.scen
                self.mode = configure_execution.mode
                self.swift_dir = configure_execution.swift_dir
                self.stma_software_dir = configure_execution.stma_software_dir
                self.base_dir = configure_execution.base_dir
                self.scen_dir = configure_execution.scen_dir
                self.logger = configure_execution.logger
            else:
                self.state = State.ERROR

    def run(self):
        """
        Initialize exeuction
        :param base: baseline name
        :param scen: scenario name
        :param mode: execution mode
        :return:
        """

        if self.state == State.ERROR:
            return

        self.logger.info('STEP {:d} - {:20s} START'.format(self.step_number, self.__class__.__name__))

        stm_dir = os.path.join(self.scen_dir, 'STM')
        if not self.check_dir(stm_dir):
            self.state = State.ERROR
            return

        stma_dir = os.path.join(stm_dir, 'STM_A')
        if not self.check_dir(stma_dir):
            self.state = State.ERROR
            return

        for topfolder, subfolder in self.STMA_FOLDER_STRUCT.items():
            folder = os.path.join(stma_dir, topfolder)
            self.check_dir(folder, self.scen_dir)

            if topfolder == '01_DynusT':
                if not self.check_dir(os.path.join(folder, self.scen), self.scen_dir):
                    self.state = State.ERROR
                    return
            else:
                for s in subfolder:
                    if not self.check_dir(os.path.join(folder, s), self.scen_dir):
                        self.state = State.ERROR
                        return

    def complete(self):
        if self.state == State.OK:
            self.logger.info('STEP {:d} - {:20s} STATUS = COMPLETE'.format(self.step_number, self.__class__.__name__))
        else:
            self.logger.info('STEP {:d} - {:20s} STATUS =   FAILED'.format(self.step_number, self.__class__.__name__))

    def execute(self, configure_execution):
        self.require(configure_execution)
        self.run()
        self.complete()
        return self.state


