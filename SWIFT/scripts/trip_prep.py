import time
from services.sys_defs import *
from services.execution_service import Execution_Service


class TripPrep(Execution_Service):
    required_keys = (
        'VEHICLE_ROSTER_FILE',
        'NEW_VEHICLE_ROSTER_FILE'
    )

    acceptable_keys = (
        'START_TRIP_NUMBER',
    )

    def __init__(self, name='TripPrep', control_file='TripPrep.ctl'):
        super().__init__(name, control_file, TripPrep.required_keys, TripPrep.acceptable_keys)

        # Module-specific data fields
        self.start_id = 1
        self.vehicle_count = 0
        self.vehicle_roster_file = None
        self.input_vehicle_roster_file = None

    def update_keys(self):
        if self.state == Codes_Execution_Status.ERROR:
            return
        if self.project_dir is not None:
            self.keys['NEW_VEHICLE_ROSTER_FILE'].value = \
                os.path.join(self.project_dir, self.keys['NEW_VEHICLE_ROSTER_FILE'].value)
            for i in range(1, self.highest_group+1):
                suffix = "_" + str(i)
                self.keys['VEHICLE_ROSTER_FILE'+suffix].value = \
                    os.path.join(self.project_dir, self.keys['VEHICLE_ROSTER_FILE'+suffix].value)

    def initialize_internal_data(self, group=1):
        if self.keys['START_TRIP_NUMBER'].value:
            self.start_id = self.keys['START_TRIP_NUMBER'].value

        # regular keys
        if group == 1:
            self.vehicle_roster_file = self.keys['NEW_VEHICLE_ROSTER_FILE'].value

        # group keys
        suffix = "_" + str(group)
        self.input_vehicle_roster_file = self.keys['VEHICLE_ROSTER_FILE' + suffix].value

    def merge_vehicle_roster_file(self):
        mode = 'w'
        if self.vehicle_count > 0:
            mode = 'a'
        with open(self.vehicle_roster_file, mode=mode, buffering=super().OUTPUT_BUFFER) as new_veh_roster:
            with open(self.input_vehicle_roster_file, mode='r', buffering=super().INPUT_BUFFER) as input_veh_roster:
                for i, line in enumerate(input_veh_roster):
                    line = line.strip().split()
                    if i % 2 == 0:
                        self.vehicle_count += 1
                        vid = self.start_id + self.vehicle_count - 1
                        data = (vid, *line[1:])
                        record = '%9d%7s%7s%9s%6s%6s%6s%6s%6s%6s%12s%12s%6s%6s%20s%10s%5s%8s%5s%6s\n' % (data)
                        new_veh_roster.write(record)
                    else:
                        record = '%12s%9s\n' % (tuple(line))
                        new_veh_roster.write(record)

    def execute(self):
        super().execute()

        start_time = time.time()
        if self.state == Codes_Execution_Status.OK:
            self.update_keys()
            self.print_keys()

            for i in range(self.highest_group):
                if self.state == Codes_Execution_Status.OK:
                    processing_start_time = time.time()
                    self.initialize_internal_data(i + 1)
                    self.merge_vehicle_roster_file()
                    processing_end_time = time.time()
                    self.logger.info('Processed vehicle file %s in %.2f minutes' %
                                     (self.input_vehicle_roster_file, (processing_end_time-processing_start_time)/60.0))
        end_time = time.time()
        execution_time = (end_time-start_time)/60.0

        self.logger.info("")
        self.logger.info("")
        if self.state == Codes_Execution_Status.ERROR:
            self.logger.info("Execution completed with ERROR in %.2f minutes" % execution_time)
        else:
            self.logger.info("Total vehicles processed               = {0:d}".format(self.vehicle_count))
            self.logger.info("Execution completed in %.2f minutes" % execution_time)


if __name__ == '__main__':

    DEBUG = 0
    if DEBUG == 1:
        import os
        execution_path = r"C:\Projects\Repo\Work\SWIFT\scripts\test\cases"
        control_file = "TripPrep_MergeTrips.ctl"
        control_file = os.path.join(execution_path, control_file)
        exe = TripPrep(control_file=control_file)
        exe.execute()
    else:
        from sys import argv
        exe = TripPrep(control_file=argv[1])
        exe.execute()