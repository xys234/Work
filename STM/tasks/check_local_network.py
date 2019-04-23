from tasks.task_status import TaskStatus
from tasks.task import Task
from tasks.config import ConfigureExecution

import os
import shutil


class CheckLocalNetwork(Task):

    family = 'DynusT'
    step_id = '01'

    REQUIRED_NETWORK_FILES = (
        'system.dat',
        'movement.dat',
        'superzone.dat',
        'TAZ_mapping.dat',
        'vms.dat',
        'control.dat',
        'linkname.dat',
        'linkxy.dat',
        'indexlink.dat',
        'network.dat',
        'destination.dat',
        'xy.dat',
        'origin.dat',
        'CongestionPricingConfig.dat',
        'Incident.dat',
        'Ramp.dat',
        'TrafficFlowModel.dat',
        'WorkZone.dat',
        'Epoch.dat',
        'output_option.dat',
        'parameter.dat',
        'scenario.dat',
        'userclass.dat',
        'GradeLengthPCE.dat',
        'YieldCap.dat',
        'StopCap4Way.dat',
        'StopCap2Way.dat',
        'LeftCap.dat',
    )

    def __init__(self, previous_steps):
        super().__init__(previous_steps)
        self.logger = None

        self.base = None
        self.scen = None
        self.mode = None
        self.swift_dir = None
        self.stma_software_dir = None
        self.base_dir = None
        self.scen_dir = None
        self.local_network = None

    def require(self):
        """
        Check the baseline network files.
        :return:
        """
        super().require()
        if self.state == TaskStatus.OK:
            configure_execution = None
            for s in self.previous_steps:
                if isinstance(s, ConfigureExecution):
                    configure_execution = s

            self.base = configure_execution.base
            self.scen = configure_execution.scen
            self.mode = configure_execution.mode
            self.swift_dir = configure_execution.swift_dir
            self.stma_software_dir = configure_execution.stma_software_dir
            self.base_dir = configure_execution.base_dir
            self.scen_dir = configure_execution.scen_dir
            self.logger = configure_execution.logger
            self.local_network = configure_execution.local_network

        return self.state

    def run(self):

        self.logger.info('')
        self.logger.info(
            'TASK {:s}_{:s}_{:s}: STATUS = START'.format(self.family, self.step_id, self.__class__.__name__))
        self.logger.info('')

        if not self.local_network:
            sources = [os.path.join(self.base_dir, r'STM\STM_A\01_DynusT', self.base, f)
                             for f in self.REQUIRED_NETWORK_FILES]
            copies = [os.path.join(self.scen_dir, r'STM\STM_A\01_DynusT', self.scen, f)
                             for f in self.REQUIRED_NETWORK_FILES]
            for s, c in zip(sources, copies):
                if not os.path.isfile(s):
                    self.state = TaskStatus.FAIL
                    self.logger.error("Base Network File {:s} Not Found".format(s))
                else:
                    shutil.copy2(s, c)

        required_network_files = [os.path.join(self.scen_dir, r'STM\STM_A\01_DynusT', self.scen, f)
                                  for f in self.REQUIRED_NETWORK_FILES]
        for f in required_network_files:
            print_path = os.path.relpath(f, os.path.join(self.scen_dir, r'STM\STM_A\01_DynusT', self.scen))
            if not os.path.isfile(f):
                self.logger.error('Required Network File {:s} Not Found'.format(print_path))
                self.state = TaskStatus.FAIL
            else:
                self.logger.info('Required Network File {:s} Checked'.format(print_path))

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
