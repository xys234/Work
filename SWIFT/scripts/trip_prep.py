import time
import sys
import csv
from services.sys_defs import *
from services.execution_service import Execution_Service
from services.data_service import Trip


class TripPrep(Execution_Service):
    required_keys = (
        'VEHICLE_ROSTER_FILE',
    )

    acceptable_keys = (
        'START_TRIP_NUMBER',
        'SELECTION_FILE',
        'SELECTION_FORMAT',
        'NEW_VEHICLE_ROSTER_FILE',
        'NEW_FLAT_TRIP_FILE'
    )

    trip_fmt_str_1 = '%9d%7s%7s%9s%6s%6s%6s%6s%6s%6s%12s%12s%6s%6s%20s%10s%5s%8s%5s%6s\n'
    trip_fmt_str_2 = '%12s%9s\n'
    selection_file_header = "Vehicle_ID"
    TRIP_FILE_HEADER = '''vid usec dsec stime vehcls vehtype 
                                      ioc #ONode #IntDe info ribf comp Izone Evac InitPos VoT tFlag pArrTime TP IniGas 
                                      DZone waitTime'''

    def __init__(self, name='TripPrep', input_control_file='TripPrep.ctl'):
        super().__init__(name, input_control_file, TripPrep.required_keys, TripPrep.acceptable_keys)

        # Module-specific data fields
        self.start_id = 1
        self.input_vehicle_count = 0
        self.output_vehicle_count = 0
        self.vehicle_roster_file = None
        self.input_vehicle_roster_file = None
        self.selection_file = None
        self.selection_format = None
        self.flat_trip_file = None

        self.trips = []
        self.selections = set()         # input selections; some ids may not be present in the trip file
        self.selection_ids = []         # true selections

    def initialize_internal_data(self, group=1):
        """
        Initialize data for all the keys
        :return:
        """

        # regular keys
        if group == 1:
            if self.keys['START_TRIP_NUMBER'].value:
                self.start_id = self.keys['START_TRIP_NUMBER'].value
            self.vehicle_roster_file = self.keys['NEW_VEHICLE_ROSTER_FILE'].value
            if self.keys['SELECTION_FILE'].value:
                self.selection_file = self.keys['SELECTION_FILE'].value
                self.selection_format = self.keys['SELECTION_FORMAT'].value
            if self.keys['NEW_FLAT_TRIP_FILE'].value:
                self.flat_trip_file = self.keys['NEW_FLAT_TRIP_FILE'].value

        suffix = "_" + str(group)
        self.input_vehicle_roster_file = self.keys['VEHICLE_ROSTER_FILE'+suffix].value

    def read_trips(self):
        """
        Read in all input trip rosters
        :return:
        """
        for g in range(1, self.highest_group+1):
            self.initialize_internal_data(group=g)
            with open(self.input_vehicle_roster_file, mode='r', buffering=super().INPUT_BUFFER) as input_roster:
                expected_number_of_trips = trip_count = 0
                for i, line in enumerate(input_roster):
                    if i == 0:
                        expected_number_of_trips = int(line.strip().split()[0])
                    if i > 1:
                        line = line.strip() + next(input_roster)
                        self.input_vehicle_count += 1
                        trip_count += 1
                        sys.stdout.write("\rNumber of Vehicles Read = {:,d} ({:.2f} %)".format(
                            trip_count, trip_count*100.0/expected_number_of_trips))
                        self.trips.append(Trip(line))
            if expected_number_of_trips != trip_count:
                self.logger.warning("Number of trips read {:,d} inconsistent with the header count {:,d}"
                                    .format(trip_count, expected_number_of_trips))
            self.logger.info("Number of Vehicles Read in Trip Roster {:d} = {:,d}".format(g, trip_count))

    def merge_vehicle_roster_file(self):
        mode = 'w'
        if self.output_vehicle_count > 0:
            mode = 'a'
        with open(self.vehicle_roster_file, mode=mode, buffering=super().OUTPUT_BUFFER) as new_veh_roster:
            with open(self.input_vehicle_roster_file, mode='r', buffering=super().INPUT_BUFFER) as input_veh_roster:
                for i, line in enumerate(input_veh_roster):
                    line = line.strip().split()
                    if i % 2 == 0:
                        self.input_vehicle_count += 1
                        self.output_vehicle_count += 1
                        vid = self.start_id + self.output_vehicle_count - 1
                        data = (vid, *line[1:])
                        record = self.trip_fmt_str_1 % data
                    else:
                        record = self.trip_fmt_str_2 % (tuple(line))
                    new_veh_roster.write(record)

    def read_selection_file(self):
        if self.selection_format != "COMMA_DELIMITED":
            self.logger.error('Selection file needs to be COMMA_DELIMITED')
            self.state = Codes_Execution_Status.ERROR
            return

        record_count = 0
        with open(self.selection_file, mode='r', buffering=super().INPUT_BUFFER) as selection_file:
            for i, line in enumerate(selection_file):
                if i == 0:
                    header = line.strip().split(',')[0]
                    if header.upper() != "VEHICLE_ID":
                        self.logger.error('Selection file header error; Expect first field "%s"' %
                                          self.selection_file_header)
                        self.state = Codes_Execution_Status.ERROR
                else:
                    record_count += 1
                    vid = int(line.strip().split(',')[0])
                    self.selections.add(vid)

        self.logger.info("Read Selection file -- {:d} records".format(record_count))

    def filter_trips(self):
        if self.selections:
            for i, trip in enumerate(self.trips):
                if trip.vid in self.selections:
                    self.selection_ids.append(i)
        else:
            self.selection_ids = [trip.vid for trip in self.trips]

    def write_nested_trip_file(self):
        """
        Write the trips in Dynus-T native vehicle roster file format
        :return:
        """

        self.output_vehicle_count = len(self.selection_ids)
        with open(file=self.vehicle_roster_file, mode='w', buffering=super().OUTPUT_BUFFER) as output_roster:
            s = '%12d           1    # of vehicles in the file, Max # of STOPs\n' % self.output_vehicle_count
            output_roster.write(s)
            s = "        #   usec   dsec   stime vehcls vehtype ioc #ONode #IntDe info ribf    " \
                "comp   izone Evac InitPos    VoT  tFlag pArrTime TP IniGas\n"
            output_roster.write(s)
            for selection_id in self.selection_ids:
                record_1, record_2 = self.trips[selection_id].to_string()
                output_roster.write(record_1)
                output_roster.write(record_2)

    def write_tabular_trip_file(self):
        """
        Write the trips in csv file format
        :return:
        """
        expected_number_of_trips = len(self.selection_ids)
        with open(self.flat_trip_file, mode='w', newline='', buffering=super().OUTPUT_BUFFER) as output:
            writer = csv.writer(output)
            writer.writerow(self.TRIP_FILE_HEADER.split())
            for i, selection_id in enumerate(self.selection_ids):
                record_1, record_2 = self.trips[selection_id].to_string()
                record = record_1 + record_2
                writer.writerow(record.split())
                sys.stdout.write("\rNumber of Vehicles Written = {:,d} ({:.2f} %)".format(
                    i+1, (i+1) * 100.0 / expected_number_of_trips))

    def execute(self):
        super().execute()
        start_time = time.time()
        if self.state == Codes_Execution_Status.OK:
            self.print_keys()
            self.initialize_internal_data(group=1)

        if self.state == Codes_Execution_Status.OK:
            self.read_trips()

            if self.selection_file:
                self.read_selection_file()
            self.filter_trips()
            if self.vehicle_roster_file:
                self.write_nested_trip_file()
            if self.flat_trip_file:
                self.write_tabular_trip_file()

        end_time = time.time()
        execution_time = (end_time-start_time)/60.0

        self.logger.info("")
        self.logger.info("")
        if self.state == Codes_Execution_Status.ERROR:
            self.logger.info("Execution completed with ERROR in %.2f minutes" % execution_time)
        else:
            self.logger.info("Number of vehicles processed  = {0:10,d}".format(self.input_vehicle_count))
            self.logger.info("Number of vehicles written    = {0:10,d}".format(self.output_vehicle_count))
            self.logger.info("Execution completed in %.2f minutes" % execution_time)


if __name__ == '__main__':

    DEBUG = 0
    if DEBUG == 1:
        import os
        execution_path = r"C:\Projects\SWIFT\SWIFT_Project_Data\Controls"
        # control_file = "TripPrep_SelectTrips.ctl"
        control_file = "TripPrep_toTabularTrips.ctl"
        control_file = os.path.join(execution_path, control_file)
        exe = TripPrep(input_control_file=control_file)
        exe.execute()
    else:
        from sys import argv
        exe = TripPrep(input_control_file=argv[1])
        exe.execute()