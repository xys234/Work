import time, os

from services.sys_defs import *
from services.execution_service import Execution_Service


class PlanPrep(Execution_Service):
    required_keys = (
        'TRAJECTORY_FILE',
        'NEW_TRAJECTORY_FILE',
        'TRIP_ADJUSTMENT_FILE',
        'TRIP_PURPOSE_FIELD',
        'VEHICLE_TYPE_FIELD',
        'TRIP_ADJUSTMENT_FIELD',
    )
    acceptable_keys = (
        'NEW_VEHICLE_MAP_FILE',         # New ID -> Old ID
        'NEW_VEHICLE_MAP_FILE'

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
        self.trip_map = None
        self.trip_count = 0
        self.trip_count_added = 0
        self.trip_count_deleted = 0


    def update_keys(self):
        if self.state == Codes_Execution_Status.ERROR:
            return
        pass

    def initialize_internal_data(self, group=1):

        self.input_trajectory_file = self.keys['TRAJECTORY_FILE'].value
        self.trajectory_file = self.keys['NEW_TRAJECTORY_FILE'].value
        self.trip_adjustment_file = self.keys['TRIP_ADJUSTMENT_FILE'].value
        self.trip_purpose_field = self.keys['TRIP_PURPOSE_FIELD'].value
        self.vehicle_type_field = self.keys['VEHICLE_TYPE_FIELD'].value
        self.trip_adjustment_field = self.keys['TRIP_ADJUSTMENT_FIELD'].value

        purpose_ind = 0
        vehtype_ind = 0
        trip_adj_ind = 0

        with open(self.trip_adjustment_file, mode='r', buffering=self.INPUT_BUFFER) as adj_file:
            for i, line in enumerate(adj_file):
                if i == 0:
                    purpose_ind, vehtype_ind, trip_adj_ind = \
                        line.index(self.trip_purpose_field),\
                        line.index(self.vehicle_type_field),\
                        line.index(self.trip_adjustment_field)

        # read in the trip adjustment file


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