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

        self.input_trajectory_file = None
        self.trajectory_file = None
        self.trip_adjustment_file = None
        self.trip_purpose_field = None
        self.vehicle_type_field = None
        self.trip_adjustment_field = None

        self.trip_adjustment_map = None       # {(O, D, Purpose, VehType): Change}
        self.trip_index = None
        self.trip_count = 0
        self.trip_count_added = 0
        self.trip_count_deleted = 0

        self.start_id = None                 # If unspecified or <= largest ID, the new ID is the largest ID + 1

    def update_keys(self):
        if self.state == Codes_Execution_Status.ERROR:
            return
        pass

    def initialize_internal_data(self):

        self.input_trajectory_file = self.keys['TRAJECTORY_FILE'].value
        self.trajectory_file = self.keys['NEW_TRAJECTORY_FILE'].value
        self.trip_adjustment_file = self.keys['TRIP_ADJUSTMENT_FILE'].value
        self.trip_purpose_field = self.keys['TRIP_PURPOSE_FIELD'].value
        self.vehicle_type_field = self.keys['VEHICLE_TYPE_FIELD'].value
        self.trip_adjustment_field = self.keys['TRIP_ADJUSTMENT_FIELD'].value


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

        with open(self.trip_adjustment_file, mode='r', buffering=self.INPUT_BUFFER) as adj_file:
            for i, line in enumerate(adj_file):
                if i == 0:
                    header = tuple(line.strip().split()[:len(self.CHANGE_FILE_HEADER)])
                    if header != self.CHANGE_FILE_HEADER:
                        self.logger.error('Trip adjustment file header error; Expect "%s"' %
                                          " ".join(self.CHANGE_FILE_HEADER))
                        self.state = Codes_Execution_Status.ERROR

                    if self.state == Codes_Execution_Status.OK:
                        deletions = []
                        adj_list = []
                        invalid_adj = []  # a list of records in str
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

                        return adj_list, invalid_adj

    def read_period_map_file(self):
        """
        read the period map file
        :return: status code
        """

        pass

    def read_income_map_file(self):
        """
        read the income map file
        :return: status code
        """
        pass

    def build_trip_index(self):
        """
         Scan the trip file and build the trip index
        :return:

        Trip index (O,D,Purpose,Occupancy,VehType,Period,Income) to [Veh IDs] to support O(1) lookup
        """
        pass

    def build_vehicle_id_index(self):
        """
        Build the vehicle id index
        :return:

        For text trajectories, vehicle ID to number of character
        For binary trajectories, vehicle ID to number of bytes
        """
        pass

    def write_trajectories(self):
        """
        Write the trajectories; If adjustment is empty, do a format conversion
        :return:
        """

        pass

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