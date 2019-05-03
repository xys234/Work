from tasks.task_status import TaskStatus
from tasks.task import Task
from tasks.config import ConfigureExecution

import os
import shutil


class CheckNetwork(Task):

    family = 'DynusT'

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
        'Toll.dat',
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
        'demand.dat'
    )

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
        super().prepare()
        if self.state == TaskStatus.OK:
            configure_execution = self.previous_steps[0]

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

        return self.state

    def require(self):
        """
        Check the baseline network files if not using local network.
        :return:
        """
        if self.state == TaskStatus.OK:
            if not self.local_network:
                sources = [os.path.join(self.base_dir, r'STM\STM_A\01_DynusT', '03_Model', f)
                           for f in self.REQUIRED_NETWORK_FILES]
                for source in sources:
                    if source.find('demand.dat') < 0:
                        print_path = os.path.relpath(source, self.scen_dir)
                        if not os.path.isfile(source):
                            self.state = TaskStatus.FAIL
                            self.logger.error("Base Network File {:s} Not Found".format(print_path))
                        else:
                            self.logger.info("Base Network File {:s} Found".format(print_path))
        return self.state

    def run(self):
        if self.state == TaskStatus.OK:
            if not self.local_network:
                sources = [os.path.join(self.base_dir, r'STM\STM_A\01_DynusT', '03_Model', f)
                                 for f in self.REQUIRED_NETWORK_FILES]
                copies = [os.path.join(self.scen_dir, r'STM\STM_A\01_DynusT', '03_Model', f)
                                 for f in self.REQUIRED_NETWORK_FILES]
                for s, c in zip(sources, copies):
                    if s.find('demand.dat') < 0:
                        shutil.copy2(s, c)

            required_network_files = [os.path.join(self.scen_dir, r'STM\STM_A\01_DynusT', '03_Model', f)
                                      for f in self.REQUIRED_NETWORK_FILES]
            for f in required_network_files:
                if f.find('demand.dat') >= 0:
                    with open(f, 'w') as temp_demand:
                        pass
                    self.logger.info('Empty Scenario Required Network File {:s} Created'.format(f))
                else:
                    print_path = os.path.relpath(f, os.path.join(self.scen_dir, r'STM\STM_A\01_DynusT', '03_Model'))
                    if not os.path.isfile(f):
                        self.logger.error('Scenario Required Network File {:s} Not Found'.format(print_path))
                        self.state = TaskStatus.FAIL
                    else:
                        self.logger.info('Scenario Required Network File {:s} Found'.format(print_path))

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
