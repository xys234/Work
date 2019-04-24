from tasks.task_status import TaskStatus
from tasks.task import Task
from tasks.config import ConfigureExecution

import os
import subprocess
import itertools


class ConvertTrips(Task):

    family = 'DynusT'
    step_id = '02'

    # PURPOSE = ('HBW', 'HNW', 'NHO', 'NHW', 'OTHER')
    PURPOSE = ('OTHER',)
    PERIOD = ('AM', 'MD', 'PM', 'OV')
    PERIOD_LEN = {
        'AM': '3HR',
        'MD': '6HR',
        'PM': '4HR',
        'OV': '8HR'
    }

    def __init__(self, previous_steps):
        super().__init__(previous_steps=previous_steps)

        self.base = None
        self.scen = None
        self.mode = None
        self.swift_dir = None
        self.stma_software_dir = None
        self.base_dir = None
        self.scen_dir = None
        self.common_dir = None
        self.logger = None

    def prepare(self):
        super().prepare()

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
            self.common_dir = configure_execution.common_dir
            self.logger = configure_execution.logger

    def require(self):

        # Check input matrices
        for purpose, period in itertools.product(self.PURPOSE, self.PERIOD):
            period_len = self.PERIOD_LEN[period]
            matrix = ' '.join(['OD', period+period_len, purpose, 'Vehicles.OMX'])
            matrix = os.path.join(self.scen_dir, 'STM/STM_D', matrix)
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
            env = {**env, **_environ}
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

        self.convert_trips()
        self.merge_trips()

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
