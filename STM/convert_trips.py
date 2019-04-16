
from services.execution_service import ExecutionService
from services.control_service import State
from services.utility import bucket_rounding, to_vehicles_helper, parse_origins

import time
import h5py
import os
import numpy as np
from scipy.interpolate import interp1d
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


class DTGenerator:
    def __init__(self, x, prob, seed=0, interp=0, logger=None):
        """

        :param x:      x values for the probability density
        :param prob:   probabilities
        :param seed:   random seed
        :param interp: number of interpolation points
        :param logger: number of interpolation points
        """
        self._prob = prob
        self._x = x
        self._seed = seed
        self._interp = interp

        if len(x) != len(prob):
            if logger is not None:
                logger.error("The lengths of input distribution do not match")
            raise ValueError("The lengths of input distribution do not match")

        self._prob_interp = prob
        if interp:
            self._x_interp = np.linspace(x[0], x[-1], self._interp)
            interpolator = interp1d(self._x, self._prob, kind='cubic')
            self._prob_interp = interpolator(self._x_interp)
            self._prob_interp = self._prob_interp / sum(self._prob_interp)
        else:
            self._x_interp = self._x
        np.random.seed(self._seed)

    def _select_range(self, period=None):
        """

        :param period: period start and end times
        :type  list of tuples
        :return:
        """
        if period:
            selector = np.array([False]*len(self._x_interp))
            for p in period:
                selector = selector | ((self._x_interp >= p[0]) & (self._x_interp < p[1]))

            xs = self._x_interp[selector]
            probs = self._prob_interp[selector]
            probs = probs / np.sum(probs)
            return probs, xs
        return self._prob_interp, self._x_interp

    def dt(self, period, size=1):
        probs, xs = self._select_range(period)
        return np.random.choice(xs, p=probs, size=size)


class ConvertTrips(ExecutionService):
    required_keys = (
        'NUMBER_OF_ZONES',
        'ORIGIN_FILE',
        'NEW_VEHICLE_ROSTER_FILE',
        'TRIP_TABLE_FILE',
        'MATRIX_NAME',
        'TIME_PERIOD_RANGE',
        'DIURNAL_FILE',
        'TRIP_PURPOSE_CODE',
        'VALUE_OF_TIME',
        'VEHICLE_OCCUPANCY'
    )

    optional_keys = (
        'VEHICLE_CLASS',
        'VEHICLE_TYPE',
        'VEHICLE_GENERATION_MODE',
        'INDIFFERENCE_BAND',
        'NUMBER_OF_STOPS',
        'ENROUTE_INFO',
        'COMPLIANCE_RATE',
        'EVACUATION_FLAG',
        'ACTIVITY_DURATION',
        'ARRIVAL_TIME',
        'WAIT_TIME',
        'INITIAL_GAS'
    )

    def __init__(self, name='ConvertTrips', control_file='ConvertTrips.ctl'):
        super().__init__(name, control_file, ConvertTrips.required_keys, ConvertTrips.optional_keys)

        self.number_of_zones = None
        self.origin_file = None
        self.vehicle_roster_file = None
        self.diurnal_file = None
        self.trip_table_file = None
        self.matrix_name = None
        self.time_period_range = None
        self.trip_purpose = None
        self.value_of_time = None
        self.vehicle_occupancy = None
        self.vehicle_class = None
        self.vehicle_type = None
        self.vehicle_gen_mode = None
        self.indifference_band = None
        self.number_of_stops = None
        self.enroute_info = None
        self.compliance_rate = None
        self.evac_flag = None
        self.activity_duration = None
        self.arrival_time = None
        self.wait_time = None
        self.initial_gas = None

        self.origins = None
        self.diurnal = None
        self.dt_generator = None
        self.diurnal_points = 600 * 24

        self.vehicle_id = 1
        self.temp_vehicle = None

    def initialize_internal_data(self, group=1):
        """
        initialize all internal data structures for a control key group.
        :param group: The control group ID
        :return:

        This function needs to be program-specific

        """
        if self.state == State.ERROR:
            return
        if group == 1:
            self.number_of_zones = self.keys['NUMBER_OF_ZONES'].value
            self.origin_file = self.keys['ORIGIN_FILE'].value
            self.origins = parse_origins(self.origin_file, self.number_of_zones, self.logger)
            self.vehicle_roster_file = self.keys['NEW_VEHICLE_ROSTER_FILE'].value

        suffix = "_" + str(group)
        self.trip_table_file = self.keys['TRIP_TABLE_FILE'+suffix].value

        self.diurnal_file = self.keys['DIURNAL_FILE'+suffix].value
        self.diurnal = self.read_diurnal_file(self.diurnal_file)
        self.dt_generator = DTGenerator(x=self.diurnal[0], prob=self.diurnal[1],
                                        interp=self.diurnal_points, seed=self.seed)

        self.matrix_name        = self.keys['MATRIX_NAME'+suffix].value
        self.time_period_range  = self.keys['TIME_PERIOD_RANGE'+suffix].value
        self.trip_purpose       = self.keys['TRIP_PURPOSE_CODE'+suffix].value
        self.value_of_time      = self.keys['VALUE_OF_TIME'+suffix].value
        self.vehicle_occupancy  = self.keys['VEHICLE_OCCUPANCY'+suffix].value
        self.vehicle_class      = self.keys['VEHICLE_CLASS'+suffix].value
        self.vehicle_type       = self.keys['VEHICLE_TYPE'+suffix].value
        self.vehicle_gen_mode   = self.keys['VEHICLE_GENERATION_MODE'+suffix].value
        self.indifference_band  = self.keys['INDIFFERENCE_BAND'+suffix].value
        self.number_of_stops    = self.keys['NUMBER_OF_STOPS'+suffix].value
        self.enroute_info       = self.keys['ENROUTE_INFO'+suffix].value
        self.compliance_rate    = self.keys['COMPLIANCE_RATE'+suffix].value
        self.evac_flag          = self.keys['EVACUATION_FLAG'+suffix].value
        self.activity_duration  = self.keys['ACTIVITY_DURATION'+suffix].value
        self.arrival_time       = self.keys['ARRIVAL_TIME'+suffix].value
        self.wait_time          = self.keys['WAIT_TIME'+suffix].value
        self.initial_gas        = self.keys['INITIAL_GAS'+suffix].value

    def rounding(self):
        if self.state == State.ERROR:
            return
        if not os.path.exists(self.trip_table_file):
            self.state = State.ERROR
            self.logger.error("Failed to open trip table file %s" % self.trip_table_file)
            return
        h5 = h5py.File(self.trip_table_file, 'r')
        self.logger.info("")
        self.logger.info("Processing trip table %s" % self.trip_table_file)
        self.logger.info("Processing matrix %s" % self.matrix_name)

        od = h5['/matrices/' + self.matrix_name][:]
        total_trips = od.sum()
        self.logger.info("Total vehicles in the matrix                = {0:,.2f}".format(total_trips))
        od = bucket_rounding(od)
        total_trips = od.sum()
        self.logger.info("Total vehicles in the matrix after rounding = {0:,d}".format(total_trips))
        return od

    def read_diurnal_file(self, diurnal_file):
        """

        :param diurnal_file: a csv file for diurnal distribution between 0 and 24
        :return: two lists: hours and probs

        only two columns of data should be present
        an example diurnal file

        Hour,Share
        0,0.001
        1,0.001
        2,0.001
        3,0.002
        4,0.005
        5,0.015
        6,0.0501
        7,0.1022
        8,0.0581
        9,0.0411
        10,0.0481
        11,0.0571
        12,0.0571
        13,0.0521
        14,0.0651
        15,0.0982
        16,0.0852
        17,0.0832
        18,0.0651
        19,0.0451
        20,0.0301
        21,0.022
        22,0.01
        23,0.005
        24,0

        """

        if not os.path.exists(diurnal_file):
            self.logger.info("Diurnal file %s does not exist" % diurnal_file)
            raise FileNotFoundError("Diurnal file %s does not exist" % diurnal_file)

        hours, probs = [], []
        with open(diurnal_file, mode='r') as f:
            next(f)
            for line in f:
                hour, prob = line.strip().split(',')
                hours.append(float(hour.strip()))
                probs.append(float(prob.strip()))
        return hours, probs

    def to_vehicles(self):

        vclass = self.vehicle_class
        vtype = self.vehicle_type
        purp = self.trip_purpose
        vot = self.value_of_time
        period = self.time_period_range

        od = self.rounding()
        total_trips = od.sum()
        dt_gen = self.dt_generator.dt(period=period, size=total_trips)
        return to_vehicles_helper(od, dt_gen, period, self.origins, vtype, vclass,
                            self.vehicle_occupancy, self.vehicle_gen_mode, self.number_of_stops, self.enroute_info,
                            self.indifference_band, self.compliance_rate, self.evac_flag, self.arrival_time,
                            self.initial_gas, self.wait_time, purp, vot)

    def write_vehicles(self, vehicle_pool):
        if self.state == Codes_Execution_Status.ERROR:
            return

        vid = self.vehicle_id
        open_mode = 'a'
        if vid == 1:
            open_mode = 'w'
        with open(self.temp_vehicle, mode=open_mode, buffering=super().OUTPUT_BUFFER) as f:
            for i, vals in enumerate(vehicle_pool):
                vid = self.vehicle_id + i
                data = (vid, *vals[:-2])
                record = '%9d%7d%7d%8.1f%6d%6d%6d%6d%6d%6d%8.4f%8.4f%6d%6d%12.8f%8.2f%5d%7.1f%5d%5.1f\n' % (data)
                f.write(record)
                record = '%12d%7.2f\n' % (vals[-2:])
                f.write(record)

        self.logger.info("Total vehicles converted                    = {0:,d}".format(vid))
        self.vehicle_id = vid + 1

    def execute(self, required_keys=(), optional_keys=()):
        """

        :return:

        The function needs to be module-specific file

        """
        super().execute(required_keys, optional_keys)
        start_time = time.time()

        end_time = time.time()
        execution_time = (end_time-start_time)/60.0

        self.logger.info("")
        self.logger.info("")
        if self.state == State.ERROR:
            self.logger.info("Execution completed with ERROR in %.2f minutes" % execution_time)
        else:
            self.logger.info("Total vehicles converted               = {0:,d}".format(self.vehicle_id - 1))
            self.logger.info("Execution completed in %.2f minutes" % execution_time)
        exit(self.state)


if __name__ == '__main__':

    DEBUG = 1
    if DEBUG == 1:
        import os
        execution_path = r"C:\Projects\SWIFT\SWIFT_Project_Data\Controls"
        # control_file = "ConvertTrips_HBW_AM.ctl"
        control_file = "ConvertTrips_OTHER_AM.ctl"
        control_file = os.path.join(execution_path, control_file)
        exe = ConvertTrips(control_file=control_file)
        exe.execute()
    else:
        from sys import argv
        exe = ConvertTrips(control_file=argv[1])
        exe.execute()