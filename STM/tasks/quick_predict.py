"""

Quick-Mode Prediction

"""

from tasks.task_status import TaskStatus
from tasks.task import Task

import os
import subprocess
import itertools


class QuickPredict(Task):
    family = 'Traffic_Predictor'

    REQUIRED_NETWORK_FILES = (
        'node.csv',
        'link.csv',
        'connection.csv',
        'parking.csv',
        'zone.csv',
        'shape.csv',
    )

    PURPOSE = ('HBW', 'HBNW', 'NHO', 'NHW', 'OTHER')
    PERIOD = ('AM', 'MD', 'PM', 'OV')
    PERIOD_LEN = {
        'AM': '3HR',
        'MD': '6HR',
        'PM': '4HR',
        'OV': '8HR'
    }

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
        self.threads = None

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
            # Check network files
            for f in self.REQUIRED_NETWORK_FILES:
                if not os.path.isfile(os.path.join(self.scen_dir, r'STM/STM_A/02_TrafficPredictor/02_Network', f)):
                    self.state = TaskStatus.FAIL
                    self.logger.error('Required Internal Network File {:s} Not Found'.format(
                        os.path.join('02_TrafficPredictor/02_Network', f)))

            plan_file = os.path.join(self.scen_dir, r'STM/STM_A/02_TrafficPredictor/03_Demand', 'Plans.bin')
            if not os.path.isfile(plan_file):
                self.state = TaskStatus.FAIL
                self.logger.error('Required Internal Plans {:s} Not Found'.format(
                    os.path.join(r'STM/STM_A/02_TrafficPredictor/03_Demand', 'Plans.bin')))

            trip_file = os.path.join(self.scen_dir, r'STM/STM_A/02_TrafficPredictor/03_Demand', 'Trips.bin')
            if not os.path.isfile(trip_file):
                self.state = TaskStatus.FAIL
                self.logger.error('Required Internal Trips {:s} Not Found'.format(
                    os.path.join(r'STM/STM_A/02_TrafficPredictor/03_Demand', 'Trips.bin')))

            for purpose, period in itertools.product(self.PURPOSE, self.PERIOD):
                pp = purpose
                if purpose in ('NHO', 'NHW'):
                    pp = 'NHB'
                instruction_file = os.path.join(self.scen_dir,
                                                r'STM/STM_D/Outputs_SWIFT',
                                                ' '.join(('DIFF OD', period+self.PERIOD_LEN[period],
                                                          pp, 'Vehicles.MAT'
                                                          )))
                if not os.path.isfile(instruction_file):
                    self.state = TaskStatus.FAIL
                    self.logger.error('Required STM_D Input {:s} Not Found'.format(instruction_file))

        return self.state

    def estimate_induced_trips(self):
        """
        Run ConvertTrips on positive changes in trip matrices
        :return:
        """

        if self.state != TaskStatus.OK:
            return

        control_template_dir = os.path.join(self.common_dir, 'STM/STM_A/Control_Template')
        executable = os.path.join(self.stma_software_dir, 'ConvertTrips.exe')

        controls = {}
        _environ = dict(os.environ)
        for purpose, period in itertools.product(self.PURPOSE, self.PERIOD):
            control_file = '_'.join(('QuickPredict', purpose, period)) + '.ctl'
            env = {
                'SCEN_DIR': self.scen_dir,
                'COMMONDATA': self.common_dir,
                'NUMBER_THREADS': str(self.threads)
            }
            env = {**env, **_environ}
            controls[(purpose, period)] = (os.path.join(control_template_dir, control_file), env)

        processes = [subprocess.Popen(args=[executable, '-k -n', v[0]], env=v[1]) for k, v in controls.items()]
        exitcodes = [p.wait() for p in processes]

        # restore the environment vars
        os.environ.update(_environ)

        for pp, exitcode in zip(controls.keys(), exitcodes):
            if exitcode == 1:
                self.state = TaskStatus.FAIL
                self.logger.error('Estimate Induced Demand for {:s} Failed'.format('_'.join(pp)))
            else:
                self.logger.info('Estimate Induced Demand for {:s} Completed'.format('_'.join(pp)))

    def merge_induced_trips(self):
        if self.state == TaskStatus.OK:
            _environ = dict(os.environ)
            control_template_dir = os.path.join(self.common_dir, 'STM/STM_A/Control_Template')
            executable = os.path.join(self.stma_software_dir, 'TripPrep.exe')
            env = {
                'SCEN_DIR': self.scen_dir,
                'COMMONDATA': self.common_dir,
                'NUMBER_THREADS': str(self.threads)
            }
            env = {**env, **_environ}
            control_file = os.path.join(control_template_dir, 'QuickPredict_MergeTrips.ctl')

            process = subprocess.Popen(args=[executable, '-k -n', control_file], env=env)
            exitcode = process.wait()
            if exitcode == 1:
                self.state = TaskStatus.FAIL
                self.logger.error('Merge Induced Demand Failed')
            if self.state == TaskStatus.OK:
                self.logger.info('Merge Induced Demand Completed')

    def assign_induced_trips(self):
        if self.state == TaskStatus.OK:
            _environ = dict(os.environ)
            control_template_dir = os.path.join(self.common_dir, 'STM/STM_A/Control_Template')
            executable = os.path.join(self.stma_software_dir, 'Router.exe')
            env = {
                'SCEN_DIR': self.scen_dir,
                'COMMONDATA': self.common_dir,
                'NUMBER_THREADS': str(self.threads)
            }
            env = {**env, **_environ}
            control_file = os.path.join(control_template_dir, 'QuickPredict_Assign.ctl')

            process = subprocess.Popen(args=[executable, '-k -n', control_file], env=env)
            exitcode = process.wait()
            if exitcode == 1:
                self.state = TaskStatus.FAIL
                self.logger.error('Assign Induced Demand Failed')
            if self.state != TaskStatus.OK:
                self.logger.info('Assign Induced Demand Completed')

    def estimate_reduced_selection(self):
        if self.state != TaskStatus.OK:
            return

        control_template_dir = os.path.join(self.common_dir, 'STM/STM_A/Control_Template')
        executable = os.path.join(self.stma_software_dir, 'ConvertTrips.exe')

        controls = {}
        _environ = dict(os.environ)
        for purpose, period in itertools.product(self.PURPOSE, self.PERIOD):
            control_file = '_'.join(('QuickPredict_Reduce', purpose, period)) + '.ctl'
            env = {
                'SCEN_DIR': self.scen_dir,
                'COMMONDATA': self.common_dir,
                'NUMBER_THREADS': str(self.threads)
            }
            env = {**env, **_environ}
            controls[(purpose, period)] = (os.path.join(control_template_dir, control_file), env)

        processes = [subprocess.Popen(args=[executable, '-k -n', v[0]], env=v[1]) for k, v in controls.items()]
        exitcodes = [p.wait() for p in processes]

        # restore the environment vars
        os.environ.update(_environ)

        for pp, exitcode in zip(controls.keys(), exitcodes):
            if exitcode == 1:
                self.state = TaskStatus.FAIL
                self.logger.error('Estimate Reduced Demand for {:s} Failed'.format('_'.join(pp)))
            else:
                self.logger.info('Estimate Reduced Demand for {:s} Completed'.format('_'.join(pp)))

        if self.state == TaskStatus.OK:
            self.logger.info('Estimate Reduced Demand Completed')

    def merge_reduce_selection(self):
        if self.state == TaskStatus.OK:
            _environ = dict(os.environ)
            control_template_dir = os.path.join(self.common_dir, 'STM/STM_A/Control_Template')
            executable = os.path.join(self.stma_software_dir, 'FileFormat.exe')
            env = {
                'SCEN_DIR': self.scen_dir,
                'COMMONDATA': self.common_dir,
                'NUMBER_THREADS': str(self.threads)
            }
            env = {**env, **_environ}
            control_file = os.path.join(control_template_dir, 'FileFormat_MergeReduce.ctl')

            process = subprocess.Popen(args=[executable, '-k -n', control_file], env=env)
            exitcode = process.wait()
            if exitcode == 1:
                self.state = TaskStatus.FAIL
                self.logger.error('Merge Reduced Demand Failed')
            if self.state != TaskStatus.OK:
                self.logger.info('Merge Reduced Demand Completed')

    def merge(self):
        """
        Merge assigned induced trips to base plans and delete the reduced trips
        :return:
        """
        if self.state == TaskStatus.OK:
            _environ = dict(os.environ)
            control_template_dir = os.path.join(self.common_dir, 'STM/STM_A/Control_Template')
            executable = os.path.join(self.stma_software_dir, 'PlanPrep.exe')
            env = {
                'SCEN_DIR': self.scen_dir,
                'COMMONDATA': self.common_dir,
                'NUMBER_THREADS': str(self.threads)
            }
            env = {**env, **_environ}
            control_file = os.path.join(control_template_dir, 'QuickPredict_FinalPlans.ctl')

            process = subprocess.Popen(args=[executable, '-k -n', control_file], env=env)
            exitcode = process.wait()
            if exitcode == 1:
                self.state = TaskStatus.FAIL
                self.logger.error('Predict Final Traffic Pattern Failed')
            if self.state != TaskStatus.OK:
                self.logger.info('Predict Final Traffic Pattern Completed')

    def run(self):
        """

        :return:
        """
        self.estimate_induced_trips()
        self.merge_induced_trips()
        self.assign_induced_trips()
        self.estimate_reduced_selection()
        self.merge_reduce_selection()
        self.merge()

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
