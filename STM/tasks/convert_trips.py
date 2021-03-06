from tasks.task_status import TaskStatus
from tasks.task import Task

import os
import subprocess
import itertools


class ConvertTrips(Task):

    family = 'DynusT'

    PURPOSE = ('HBW', 'HBNW', 'NHO', 'NHW', 'OTHER')
    # PURPOSE = ('OTHER',)
    PERIOD = ('AM', 'MD', 'PM', 'OV')
    PERIOD_LEN = {
        'AM': '3HR',
        'MD': '6HR',
        'PM': '4HR',
        'OV': '8HR'
    }

    def __init__(self, previous_steps, step_id='00'):
        super().__init__(previous_steps, step_id=step_id)

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
        self.common_dir = None
        self.local_network = None
        self.logger = None

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

        if self.state != TaskStatus.OK:
            return
        # Check input matrices
        for purpose, period in itertools.product(self.PURPOSE, self.PERIOD):
            period_len = self.PERIOD_LEN[period]
            purpose_mask = purpose
            if purpose in ('NHW', 'NHO'):
                purpose_mask = 'NHB'
            matrix = ' '.join(['OD', period+period_len, purpose_mask, 'Vehicles.OMX'])
            matrix = os.path.join(self.scen_dir, 'STM/STM_D/Outputs_SWIFT', matrix)
            if os.path.isfile(matrix):
                self.logger.info('{matrix:s} Checked'.format(matrix=matrix))
            else:
                self.logger.error('Required file {matrix:s} Not Found'.format(matrix=matrix))
                self.state = TaskStatus.FAIL

        return self.state

    def convert_trips(self):
        if self.state != TaskStatus.OK:
            return

        control_template_dir = os.path.join(self.common_dir, 'STM/STM_A/Control_Template')
        executable = os.path.join(self.stma_software_dir, 'convert_trips.exe')

        controls = {}
        _environ = dict(os.environ)
        for purpose, period in itertools.product(self.PURPOSE, self.PERIOD):
            control_file = '_'.join(('ConvertTrips', purpose, period)) + '.ctl'
            env = {
                'PURPOSE': '_'.join((purpose, period)),
                'SCEN_DIR': self.scen_dir,
                'SCEN': self.scen,
            }
            env = {**env, **_environ}           # the numpy random number generator depends on SYSTEMROOT
            controls[(purpose, period)] = (os.path.join(control_template_dir, control_file), env)

        # self.logger.info('{:s} - {:s}'.format('_'.join(k), ' '.join((executable, v[0]))))
        processes = [subprocess.Popen(args=[executable, v[0]], env=v[1]) for k, v in controls.items()]
        exitcodes = [p.wait() for p in processes]

        # restore the environment vars
        os.environ.update(_environ)

        for pp, exitcode in zip(controls.keys(), exitcodes):
            if exitcode:
                self.state = TaskStatus.FAIL
                self.logger.error('Trip Conversion for {:s} Failed'.format('_'.join(pp)))

    def merge_trips(self):
        if self.state != TaskStatus.OK:
            return

        control_template_dir = os.path.join(self.common_dir, 'STM/STM_A/Control_Template')
        control_file = os.path.join(control_template_dir, 'TripPrep_MergeTrips.ctl')
        executable = os.path.join(self.stma_software_dir, 'trip_prep.exe')

        _environ = dict(os.environ)
        env = {
            'SCEN_DIR': self.scen_dir,
            'SCEN': self.scen,
        }
        env = {**env, **_environ}
        processes = [subprocess.Popen(args=[executable, control_file], env=env)]
        exitcodes = [p.wait() for p in processes]

        for exitcode in exitcodes:
            if exitcode:
                self.state = TaskStatus.FAIL
                self.logger.error('Merge Trips Failed')

        os.environ.update(_environ)

    def run(self):
        """

        :return:
        """
        # self.convert_trips()
        # self.merge_trips()

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
