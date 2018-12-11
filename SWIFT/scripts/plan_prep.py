import time
import os
import random

from services.sys_defs import *
from services.execution_service import Execution_Service


class PlanPrep(Execution_Service):

    CHANGE_FILE_HEADER = ('ORIGIN','DESTINATION','PURPOSE','OCCUPANCY','VEHTYPE','PERIOD','INCOME','CHANGE')
    PERIOD_MAP_FILE_HEADER = ('PERIOD', 'START', 'END')
    INCOME_MAP_FILE_HEADER = ('INCOME', 'LOW', 'HIGH')

    required_keys = (
        'TRAJECTORY_FILE',
        'TRAJECTORY_FORMAT',
        'NEW_TRAJECTORY_FILE',
        'NEW_TRAJECTORY_FORMAT',
        'VEHICLE_ROSTER_FILE',
        'TRIP_ADJUSTMENT_FILE',
        'PERIOD_FILED',
        'INCOME_FIELD',
        'PERIOD_MAP_FILE',
        'INCOME_MAP_FILE',

    )
    acceptable_keys = (
        'ZONE_MAP_FILE',
        'NEW_VEHICLE_MAP_FILE',         # New ID -> Old ID


    )

    def __init__(self, name='PlanPrep', control_file='PlanPrep.ctl'):
        super().__init__(name, control_file, PlanPrep.required_keys, PlanPrep.acceptable_keys)

        self.vehicle_roster_file = None
        self.input_trajectory_file = None
        self.trajectory_file = None
        self.trip_adjustment_file = None
        self.period_map_file = None
        self.vot_map_file = None

        self.trip_adjustment_map = None       # {(O, D, Purpose, VehType): Change}
        self.trip_index = None
        self.trip_count = 0
        self.trip_count_added = 0
        self.trip_count_deleted = 0

        self.period_map = None
        self.vot_map_to_level = None
        self.vot_map_to_range = None

        self.start_id = None                 # If unspecified or <= largest ID, the new ID is the largest ID + 1

    def update_keys(self):
        if self.state == Codes_Execution_Status.ERROR:
            return
        pass

    def initialize_internal_data(self):

        self.input_trajectory_file = self.keys['TRAJECTORY_FILE'].value
        self.trajectory_file = self.keys['NEW_TRAJECTORY_FILE'].value
        self.trip_adjustment_file = self.keys['TRIP_ADJUSTMENT_FILE'].value

        # read in the trip adjustment file

    def read_trip_adjustment_file(self):
        """
        read the trip adjustment file; Build the adjustment list
        :return: status code

        The fields are in the following exact order and names.
        ORIGIN	DESTINATION	PURPOSE	OCCUPANCY	VEHTYPE	PERIOD	INCOME	CHANGE (Notes)

        Any fields after the last field is ignored.

        Additions are the first block followed by the deletions.
        New_ID    Old_ID
        10001     25
        10002     88
        ......
        -67       -67
        """

        row_count = 0
        with open(self.trip_adjustment_file, mode='r', buffering=self.INPUT_BUFFER) as adj_file:
            for i, line in enumerate(adj_file):
                if i == 0:
                    header = tuple(line.strip().split('\t')[:len(self.CHANGE_FILE_HEADER)])
                    if header != self.CHANGE_FILE_HEADER:
                        self.logger.error('Trip adjustment file header error; Expect "%s"' %
                                          " ".join(self.CHANGE_FILE_HEADER))
                        self.state = Codes_Execution_Status.ERROR

                if self.state == Codes_Execution_Status.OK:
                    deletions = []
                    adj_list = []
                    invalid_adj = []  # a list of records in str

                    row_count += 1
                    data = list(map(int, line.strip().split()))
                    key, operation = data[:7], data[6]
                    if key not in self.trip_index:
                        invalid_adj.append(data.append("NEW_COMBINATION"))
                    else:
                        if operation > 0:
                            candidates = self.trip_index[key]
                            chosen = random.choice(candidates, k=operation)
                            for v in chosen:
                                adj_list.append((self.start_id, v))
                                self.start_id += 1
                        else:
                            deletions.append((key, operation))

                    # Process deletions
                    for deletion in deletions:
                        k, oper = deletion
                        candidates = self.trip_index[k]
                        if abs(oper) > len(candidates):
                            invalid_adj.append(list(k).extend([abs(oper) - len(candidates), "UNFILLED_DELETION"]))
                        else:
                            chosen = random.sample(candidates, k=abs(oper))
                            for c in chosen:
                                adj_list.append((-c, -c))

                    self.logger.info("Processed trip adjustment file -- %d records" % row_count)
                    return adj_list, invalid_adj

    def read_period_map_file(self):
        """
        read the period map file
        :return: status code
        """

        row_count = 0
        with open(self.period_map_file, mode='r', buffering=super().INPUT_BUFFER) as period_map_file:
            for i, line in period_map_file:
                if i == 0:
                    header = tuple(line.strip().split('\t')[:len(self.PERIOD_MAP_FILE_HEADER)])
                    if header != self.PERIOD_MAP_FILE_HEADER:
                        self.logger.error('Period map file header error; Expect "%s"' %
                                          " ".join(self.PERIOD_MAP_FILE_HEADER))
                        self.state = Codes_Execution_Status.ERROR

                if self.state == Codes_Execution_Status.OK:
                    row_count += 1
                    period, pstart, pend = tuple(map(int, line.strip.split('\t')))[:len(self.PERIOD_MAP_FILE_HEADER)]
                    if period in self.period_map:
                        self.period_map[period].append((pstart, pend))
                    else:
                        self.period_map[period] = [(pstart, pend)]
        self.logger.info("Read period map file -- %d records" % row_count)

    def to_period(self, dtime):
        """
        Convert a departure time to a period index
        :param dtime:
        :return: an integer period index
        """

        for period, ranges in self.period_map.items():
            for r in ranges:
                if r[0] <= dtime < r[1]:
                    return period

    def read_income_map_file(self):
        """
        read the income map file
        :return: status code

        The income maps include a dict that maps income ranges to income levels and another mapping levels to ranges

        """

        row_count = 0
        with open(self.vot_map_file, mode='r', buffering=super().INPUT_BUFFER) as vot_map_file:
            for i, line in vot_map_file:
                if i == 0:
                    header = tuple(line.strip().split('\t')[:len(self.INCOME_MAP_FILE_HEADER)])
                    if header != self.INCOME_MAP_FILE_HEADER:
                        self.logger.error('Income map file header error; Expect "%s"' %
                                          " ".join(self.INCOME_MAP_FILE_HEADER))
                        self.state = Codes_Execution_Status.ERROR

                if self.state == Codes_Execution_Status.OK:
                    row_count += 1
                    level, low, high = tuple(map(int, line.strip.split('\t')))[:len(self.INCOME_MAP_FILE_HEADER)]
                    self.vot_map_to_level[(low, high)] = level
                    self.vot_map_to_range[level] = low, high

        self.logger.info("Read income map file -- %d records" % row_count)

    def to_vot_level(self, vot):
        """
        Convert a VoT to an integer income level
        :param vot: A value of time
        :type float
        :return:

        Do a linear search through the vot_map_to_level; Find the first suitable interval
        Could use BST but there are usually only a handful of VoTs
        """

        for vot_range in self.vot_map_to_level.keys():
            if vot >= vot_range[0] and vot_range < vot_range[1]:
                return self.vot_map_to_level[vot_range]

    def build_trip_index(self):
        """
         Scan the trip file and build the trip index
        :return:

        Trip index (O,D,Purpose,Occupancy,VehType,Period,Income) to [Veh IDs] to support fast lookup
        """

        trip_count = 0
        with open(self.vehicle_roster_file, mode='r', buffering=super().INPUT_BUFFER) as input_trip:
            header = next(input_trip)
            trips_stored = int(header.strip().split()[0])
            next(input_trip)  # skip the vehicle roster header
            for line in input_trip:
                data = line + next(input_trip)
                data = data.strip().split()

                dtime = float(data[3])
                period = self.to_period(dtime)
                vot = float(data[15])
                income = self.to_vot_level(vot)

                vid, o, d, purp, occ, vehtype = \
                    int(data[0]), int(data[12]), int(data[20]), int(data[18]), int(data[6]), int(data[5])
                key = (o, d, purp, occ, vehtype, period, income)
                if key not in self.trip_index:
                    self.trip_index[key] = [vid]
                else:
                    self.trip_index[key].append(vid)
                trip_count += 1
        self.logger.info("Read vehicle roster file -- %d trips" % trip_count)
        if trip_count != trips_stored:
            self.logger.warning("Number of trips read inconsistent with the header count %d" % trips_stored)

    def build_vehicle_id_index(self):
        """
        Build the vehicle id index
        :return:

        For text trajectories, vehicle ID to position as number of character and record length
        For binary trajectories, vehicle ID to position as number of bytes and record length
        """
        pass

    def write_trajectories(self):
        """
        Write the trajectories with adjustment
        :return:
        """

        pass

    def convert_trajectories(self):
        """
        Convert text to/from binary vehicle trajectories
        :return:
        """





    def execute(self):
        super().execute()

        start_time = time.time()
        if self.state == Codes_Execution_Status.OK:
            self.update_keys()
            self.print_keys()

        self.initialize_internal_data()

        end_time = time.time()
        execution_time = (end_time - start_time) / 60.0

        self.logger.info("")
        self.logger.info("")
        if self.state == Codes_Execution_Status.ERROR:
            self.logger.info("Execution completed with ERROR in %.2f minutes" % execution_time)
        else:
            self.logger.info("Total trips read                  = {0:d}".format(self.trip_count))
            self.logger.info("Total trips duplicated            = {0:d}".format(self.trip_count_added))
            self.logger.info("Total trips deleted               = {0:d}".format(self.trip_count_deleted))
            self.logger.info("Execution completed in %.2f minutes" % execution_time)