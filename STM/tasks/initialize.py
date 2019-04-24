from tasks.task_status import TaskStatus
from tasks.task import Task
from tasks.config import ConfigureExecution

import os


class InitializeEnvironment(Task):

    family = 'Setup'
    step_id = '02'

    STMA_FOLDER_STRUCT = {
        '01_DynusT': ('01_Controls', '03_Demand'),
        '02_TrafficPredictor': ('01_Controls', '02_Network', '03_Demand', '04_Results'),
        '03_Performance_Summarizer': ('01_Controls', '02_Network', '03_Demand', '04_Results'),
        '04_KPI_PreProcessor': ('01_Controls', '02_Results')

    }

    def __init__(self, previous_steps):
        super().__init__(previous_steps=previous_steps)

        self.logger = None

        self.swift_dir = None
        self.base = None
        self.scen = None
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

    def prepare(self):
        super().prepare()
        if self.state == TaskStatus.OK:
            configure_execution = None
            for s in self.previous_steps:
                if isinstance(s, ConfigureExecution):
                    configure_execution = s

            self.swift_dir = configure_execution.swift_dir
            self.base = configure_execution.base
            self.scen = configure_execution.scen
            self.base_dir = configure_execution.base_dir
            self.scen_dir = configure_execution.scen_dir
            self.logger = configure_execution.logger
        return self.state

    def require(self):
        pass

    def run(self):
        """
        Initialize exeuction
        :param base: baseline name
        :param scen: scenario name
        :param mode: execution mode
        :return:
        """

        if self.state != TaskStatus.OK:
            return

        stm_dir = os.path.join(self.scen_dir, 'STM')
        if not self.check_dir(stm_dir):
            self.state = TaskStatus.FAIL
            return

        stma_dir = os.path.join(stm_dir, 'STM_A')
        if not self.check_dir(stma_dir):
            self.state = TaskStatus.FAIL
            return

        for topfolder, subfolder in self.STMA_FOLDER_STRUCT.items():
            folder = os.path.join(stma_dir, topfolder)
            self.check_dir(folder, self.scen_dir)

            for s in subfolder:
                if not self.check_dir(os.path.join(folder, s), self.scen_dir):
                    self.state = TaskStatus.FAIL
                    return

            if topfolder == '01_DynusT':
                if not self.check_dir(os.path.join(folder, self.scen), self.scen_dir):
                    self.state = TaskStatus.FAIL
                    return

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


