import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import os
import time, h5py, numpy as np

from services.sys_defs import *
from services.execution_service import Execution_Service
from services.data_service import DTGenerator, read_diurnal_file, bucket_rounding
from services.network_service import parse_origins



class ConvertTrips(Execution_Service):
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

    acceptable_keys = (
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
        super().__init__(name, control_file, ConvertTrips.required_keys, ConvertTrips.acceptable_keys)

        # Module-specific data fields
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

    def update_keys(self):
        """
        Concatenate the project directory with individual keys
        :return:
        This function needs to be program-specific

        """

        if self.state == Codes_Execution_Status.ERROR:
            return
        if self.project_dir is not None:
            self.keys['ORIGIN_FILE'].value = os.path.join(self.project_dir, self.keys['ORIGIN_FILE'].value)
            self.keys['NEW_VEHICLE_ROSTER_FILE'].value = \
                os.path.join(self.project_dir, self.keys['NEW_VEHICLE_ROSTER_FILE'].value)
            for i in range(1, self.highest_group+1):
                suffix = "_" + str(i)
                self.keys['TRIP_TABLE_FILE'+suffix].value = \
                    os.path.join(self.project_dir, self.keys['TRIP_TABLE_FILE'+suffix].value)
                self.keys['DIURNAL_FILE'+suffix].value = \
                    os.path.join(self.project_dir, self.keys['DIURNAL_FILE'+suffix].value)


    def initialize_internal_data(self, group=1):
        """
        initialize all internal data structures for a control key group.
        :param group: The control group ID
        :return:

        This function needs to be program-specific

        """
        if self.state == Codes_Execution_Status.ERROR:
            return
        if group == 1:
            self.number_of_zones = self.keys['NUMBER_OF_ZONES'].value
            self.origin_file = self.keys['ORIGIN_FILE'].value
            self.origins = parse_origins(self.origin_file, self.number_of_zones, self.logger)
            self.vehicle_roster_file = self.keys['NEW_VEHICLE_ROSTER_FILE'].value

        suffix = "_" + str(group)
        self.trip_table_file = self.keys['TRIP_TABLE_FILE'+suffix].value

        self.diurnal_file = self.keys['DIURNAL_FILE'+suffix].value
        self.diurnal = read_diurnal_file(self.diurnal_file, self.logger)
        self.dt_generator = DTGenerator(x=self.diurnal[0], prob=self.diurnal[1],
                                        interp=self.diurnal_points, seed=self.random_seed)

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

    def to_vehicles(self):
        if self.state == Codes_Execution_Status.ERROR:
            return
        if not os.path.exists(self.trip_table_file):
            self.state = Codes_Execution_Status.ERROR
            self.logger.error("Failed to open trip table file %s" % self.trip_table_file)
            return
        h5 = h5py.File(self.trip_table_file, 'r')
        self.logger.info("")
        self.logger.info("Processing trip table %s" % self.trip_table_file)
        self.logger.info("Processing matrix %s" % self.matrix_name)

        od = h5['/matrices/' + self.matrix_name][:]
        total_trips = od.sum()
        self.logger.info("Total vehicles in the matrix                = {0:.2f}".format(total_trips))

        vclass = self.vehicle_class
        vtype = self.vehicle_type
        purp = self.trip_purpose
        vot = self.value_of_time
        period = self.time_period_range
        field_filler = 0

        od = bucket_rounding(od)
        total_trips = od.sum()
        self.logger.info("Total vehicles in the matrix after rounding = {0:d}".format(total_trips))

        dt_pool = (t for t in self.dt_generator.dt(period=period, size=total_trips))
        for i in range(od.shape[0]):
            if od[i].sum() < 1:
                continue
            for j in range(od.shape[0]):
                trip = od[i][j]
                if trip > 0:
                    orig = i + 1
                    dest = j + 1
                    for k in range(trip):
                        gen_link_choice = np.random.choice(len(self.origins[i+1]))
                        anode, bnode = self.origins[i+1][gen_link_choice][0], self.origins[i+1][gen_link_choice][1]
                        ipos = float(np.random.randint(1, 10000)) / 10000
                        dtime = next(dt_pool)
                        yield anode, bnode, dtime, vclass, vtype, self.vehicle_occupancy, \
                              self.vehicle_gen_mode, self.number_of_stops, self.enroute_info, self.indifference_band, \
                              self.compliance_rate, orig, self.evac_flag, ipos, vot, field_filler, self.arrival_time, \
                              purp, self.initial_gas, dest, self.wait_time      # 21 fields

    def write_vehicles(self, vehicle_pool):
        if self.state == Codes_Execution_Status.ERROR:
            return

        vid = self.vehicle_id
        open_mode = 'a'
        if self.vehicle_id == 1:
            open_mode = 'w'
        with open(self.vehicle_roster_file, mode=open_mode, buffering=super().OUTPUT_BUFFER) as f:
            for i, vals in enumerate(vehicle_pool):
                vid = self.vehicle_id + i
                data = (vid, *vals[:-2])
                record = '%9d%7d%7d%8.1f%6d%6d%6d%6d%6d%6d%8.4f%8.4f%6d%6d%12.8f%8.2f%5d%7.1f%5d%5.1f\n' % (data)
                f.write(record)
                record = '%12d%7.2f\n' % (vals[-2:])
                f.write(record)

        self.logger.info("Total vehicles converted                    = {0:d}".format(vid))
        self.vehicle_id = vid + 1

    def execute(self):
        """

        :return:

        The function needs to be module-specific file

        """
        super().execute()
        start_time = time.time()
        if self.state == Codes_Execution_Status.OK:
            self.update_keys()
            self.print_keys()

            for i in range(self.highest_group):
                if self.state == Codes_Execution_Status.OK:
                    matrix_conversion_start_time = time.time()
                    self.initialize_internal_data(i+1)
                    vehicle_pool = self.to_vehicles()
                    self.write_vehicles(vehicle_pool)
                    self.logger.info("Matrix Converted in %.2f minutes" % ((time.time()-matrix_conversion_start_time)/60))

        end_time = time.time()
        execution_time = (end_time-start_time)/60.0

        self.logger.info("")
        self.logger.info("")
        if self.state == Codes_Execution_Status.ERROR:
            self.logger.info("Execution completed with ERROR in %.2f minutes" % execution_time)
        else:
            self.logger.info("Total vehicles converted               = {0:d}".format(self.vehicle_id - 1))
            self.logger.info("Execution completed in %.2f minutes" % execution_time)



if __name__ == '__main__':

    DEBUG = 0
    if DEBUG == 1:
        import os
        execution_path = r"C:\Projects\Repo\Work\SWIFT\scripts\test\cases"
        control_file = "ConvertTrips_OTHER_MD.ctl"
        control_file = os.path.join(execution_path, control_file)
        exe = ConvertTrips(control_file=control_file)
        exe.execute()
    else:
        from sys import argv
        exe = ConvertTrips(control_file=argv[1])
        exe.execute()
