import time
import sys
import csv
import random
from math import ceil
import struct

from services.execution_service import ExecutionService
from services.control_service import State
from services.file_service import TripFileRecord, File


class TripPrep(ExecutionService):
    required_keys = (
        'VEHICLE_ROSTER_FILE',
    )

    optional_keys = (
        'START_TRIP_NUMBER',
        'SELECTION_FILE',
        'SELECTION_FORMAT',
        'NEW_VEHICLE_ROSTER_FILE',
        'NEW_FLAT_TRIP_FILE',
        'RENUMBER_TRIPS',
        'SELECTION_PERCENTAGE'
    )

    trip_fmt_str_flat = "{:d},{:d},{:d},{:.1f},{:d},{:d},{:d},{:d},{:d},{:d},{:.4f},{:.4f},{:d}," \
                        "{:d},{:.8f},{:.2f},{:d},{:.1f},{:d},{:.1f},{:d},{:.2f}"
    selection_file_header = "Vehicle_ID"
    TRIP_FILE_HEADER = '''vid usec dsec stime vehcls vehtype 
                                      ioc #ONode #IntDe info ribf comp Izone Evac InitPos VoT tFlag pArrTime TP IniGas 
                                      DZone waitTime'''

    def __init__(self, name='TripPrep', input_control_file='TripPrep.ctl'):
        super().__init__(name, input_control_file, TripPrep.required_keys, TripPrep.optional_keys)

        # Module-specific data fields
        self.start_id = 1
        self.input_vehicle_count = 0
        self.output_vehicle_count = 0
        self.vehicle_roster_file = None
        self.input_vehicle_roster_file = None
        self.selection_file = None
        self.selection_format = None
        self.flat_trip_file = None
        self.renumber_trips = None

        self.trips = File()
        self.trip_index = set()
        self.duplicate_trip_index = set()
        self.selections = set()         # input selections; some ids may not be present in the trip file
        self.selection_ids = []         # true selections in internal vehicle ids
        self.selection_percentage = 100.0
        self.input_format = 'BINARY'    # the input mode to build index
        self.stime_index = []
        self.trip_buffer = bytearray()

        random.seed(self.seed)

    def initialize_internal_data(self, group=1):
        """
        Initialize data for all the keys
        :return:
        """

        # Single keys only initiated once
        if group == 1:
            if self.keys['START_TRIP_NUMBER'].value:
                self.start_id = self.keys['START_TRIP_NUMBER'].value

            self.vehicle_roster_file = self.keys['NEW_VEHICLE_ROSTER_FILE'].value

            if self.keys['SELECTION_FILE'].value:
                self.selection_file = self.keys['SELECTION_FILE'].value
                self.selection_format = self.keys['SELECTION_FORMAT'].value

            if self.keys['NEW_FLAT_TRIP_FILE'].value:
                self.flat_trip_file = self.keys['NEW_FLAT_TRIP_FILE'].value

            self.renumber_trips = self.keys['RENUMBER_TRIPS'].value
            self.selection_percentage = max(min(100.0, self.keys['SELECTION_PERCENTAGE'].value), 0.1)

        suffix = "_" + str(group)
        self.input_vehicle_roster_file = self.keys['VEHICLE_ROSTER_FILE'+suffix].value

    def check_input_trips(self):
        """
        Check if all inputs are text files or binary files. Cannot mix
        :return:
        """
        text, binary = False, False
        for name, key in self.keys.items():
            if name.startswith('VEHICLE_ROSTER_FILE'):
                if key.value.endswith('.bin'):
                    binary = True
                if key.value.endswith('.dat'):
                    text = True
                if binary and text:
                    self.state = State.ERROR
                    self.logger.error('Cannot mix text and binary input roster')

        if text:
            self.input_format = 'TEXT'

    def read_text_trips(self, g):
        """
        Read in all input trip rosters
        :return:
        """
        with open(self.input_vehicle_roster_file, mode='r', buffering=super().INPUT_BUFFER) as input_roster:
            expected_number_of_trips = trip_count = 0
            for i, line in enumerate(input_roster):
                if i == 0:
                    expected_number_of_trips = int(line.strip().split()[0])
                if i > 1:
                    line = line.strip() + next(input_roster)
                    self.input_vehicle_count += 1
                    trip_count += 1
                    if trip_count % 10_000 == 0 or trip_count == expected_number_of_trips:
                        sys.stdout.write("\rNumber of Vehicles Read = {:,d} ({:.2f} %)".format(
                            trip_count, trip_count * 100.0 / expected_number_of_trips))
                    trip = TripFileRecord()
                    trip.from_string(line.split())

                    if not self.renumber_trips:
                        if trip.vehid in self.trip_index:
                            self.duplicate_trip_index.add(trip.vehid)
                        else:
                            self.trip_index.add(trip.vehid)
                            self.trips.append(trip)
                    else:
                        self.trips.append(trip)

            sys.stdout.write('\n')

        if expected_number_of_trips != trip_count:
            self.logger.warning("Number of trips read {:,d} inconsistent with the header count {:,d}"
                                .format(trip_count, expected_number_of_trips))
        self.logger.info("Number of Vehicles Read in Trip Roster {:d} = {:,d}".format(g, trip_count))

    def read_binary_trips(self, g):
        with open(self.input_vehicle_roster_file, mode='rb') as input_trip:
            input_trip_buffer = input_trip.read()
            input_file_size = sys.getsizeof(input_trip_buffer)
            input_total_trips = sys.getsizeof(input_trip_buffer) / struct.calcsize(TripFileRecord.fmt_binary)
            self.trip_buffer.extend(input_trip_buffer)
        self.logger.info("Read Trip Roster {:d}, Size = {:,d} MB, about {:,d} Trips".format(g,
             int(input_file_size / 1048576), int(input_total_trips)))

    def build_trip_index(self):
        read_size = struct.calcsize(TripFileRecord.fmt_binary)
        offset = 12
        pos, trip_count = 0, 0

        while pos < len(self.trip_buffer):
            vid = struct.unpack("=i", self.trip_buffer[pos:pos + 4])[0]
            if not self.renumber_trips:
                if vid in self.trip_index:
                    self.duplicate_trip_index.add(vid)
                else:
                    self.trip_index.add(vid)

            stime = struct.unpack("=f", self.trip_buffer[pos + offset:pos + offset + 4])[0]
            self.stime_index.append([stime, pos, vid])
            self.input_vehicle_count += 1
            if self.input_vehicle_count % 10_000 == 0:
                sys.stdout.write("\rBuilding Trip Index on Start Time for {:,d} Trips".format(self.input_vehicle_count))
            pos += read_size

        sys.stdout.write('\n')
        self.logger.info("Sorting trips based on departure time")
        self.stime_index.sort(key=lambda t: t[0])
        self.logger.info("Sorting trips based on departure time complete")

    def read_trips(self):
        for g in range(1, self.highest_group+1):
            self.initialize_internal_data(group=g)
            if self.input_format == 'BINARY':
                self.read_binary_trips(g)
            else:
                self.read_text_trips(g)

        if self.input_format == 'BINARY':
            self.build_trip_index()

        # Renumber the trips
        if self.renumber_trips:
            if self.input_format != 'BINARY':
                for i, trip in enumerate(self.trips):
                    trip.vehid = self.start_id + i
            else:
                for i, s in enumerate(self.stime_index):
                    s[2] = self.start_id + i

        else:
            for v in self.duplicate_trip_index:
                self.logger.warning("Duplicate Vehicle ID = {:d}".format(v))
            self.logger.warning("Number of Duplicate Vehicle IDs = {:,d}".format(len(self.duplicate_trip_index)))

    def read_selection_file(self):
        if self.selection_format != "COMMA_DELIMITED":
            self.logger.error('Selection file format must be COMMA_DELIMITED')
            self.state = State.ERROR
            return

        record_count = 0
        with open(self.selection_file, mode='r', buffering=super().INPUT_BUFFER) as selection_file:
            for i, line in enumerate(selection_file):
                if i == 0:
                    header = line.strip().split(',')[0]
                    if header.upper() != "VEHICLE_ID":
                        self.logger.error('Selection file header error; Expect first field "%s"' %
                                          self.selection_file_header)
                        self.state = State.ERROR
                else:
                    record_count += 1
                    vid = int(line.strip().split(',')[0])
                    self.selections.add(vid)

        self.logger.info("Read Selection file -- {:d} records".format(record_count))

    def filter_trips(self):
        # Renumber first and then filter; So if filtering on original ids desired. Set RENUMBER_TRIPS = False
        if self.selections:
            if self.input_format != 'BINARY':
                for i, trip in enumerate(self.trips):
                    if trip.vehid in self.selections:
                        self.selection_ids.append(i)
            else:
                for i, s in enumerate(self.stime_index):
                    if s[2] in self.selections:
                        self.selection_ids.append(i)
        else:
            if self.input_format != 'BINARY':
                self.selection_ids = list(range(len(self.trips)))   # indices to internal trip list
            else:
                self.selection_ids = list(range(len(self.stime_index)))

        if self.selection_percentage < 100.0:
            sample = random.sample(self.selection_ids,
                                   ceil(self.selection_percentage / 100.0 * len(self.selection_ids)))
            self.selection_ids = sorted(sample)

    def write_nested_trip_file(self):
        """
        Write the trips in Dynus-T native vehicle roster file format
        :return:
        """

        read_size = struct.calcsize(TripFileRecord.fmt_binary)
        self.output_vehicle_count = len(self.selection_ids)

        writer = None
        if self.flat_trip_file:
            f = open(file=self.flat_trip_file, mode='w', newline='', buffering=super().OUTPUT_BUFFER)
            writer = csv.writer(f)
            writer.writerow(self.TRIP_FILE_HEADER.split())

        with open(file=self.vehicle_roster_file, mode='w', buffering=super().OUTPUT_BUFFER) as output_roster:
            s = '%12d           1    # of vehicles in the file, Max # of STOPs\n' % self.output_vehicle_count
            output_roster.write(s)
            s = "        #   usec   dsec   stime vehcls vehtype ioc #ONode #IntDe info ribf    " \
                "comp   izone Evac InitPos    VoT  tFlag pArrTime TP IniGas\n"
            output_roster.write(s)
            for i, selection_id in enumerate(self.selection_ids):
                if self.input_format != 'BINARY':
                    output_roster.write(str(self.trips[selection_id]))
                    if self.flat_trip_file:
                        values = tuple(self.trips[selection_id].values)
                        record = self.trip_fmt_str_flat.format(*values)
                        writer.writerow(record.split(','))
                else:
                    trip_index = self.stime_index[selection_id]
                    t = TripFileRecord()
                    t.from_bytes(self.trip_buffer[trip_index[1]:trip_index[1] + read_size])
                    t.vehid = trip_index[2]    # commit the renumbered trip id
                    output_roster.write(str(t))
                    if self.flat_trip_file:
                        values = tuple(t.values)
                        record = self.trip_fmt_str_flat.format(*values)
                        writer.writerow(record.split(','))
                if (i + 1) % 10_000 == 0 or i + 1 == len(self.selection_ids):
                    sys.stdout.write("\rNumber of Vehicles Written = {:,d} ({:.0f} %)".format(
                        i + 1, (i + 1) * 100.0 / len(self.selection_ids)))
            sys.stdout.write('\n')

    # def write_tabular_trip_file(self):
    #     """
    #     Write the trips in csv file format
    #     :return:
    #     """
    #     expected_number_of_trips = len(self.selection_ids)
    #     with open(self.flat_trip_file, mode='w', newline='', buffering=super().OUTPUT_BUFFER) as output:
    #         writer = csv.writer(output)
    #         writer.writerow(self.TRIP_FILE_HEADER.split())
    #         for i, selection_id in enumerate(self.selection_ids):
    #             values = self.trips[selection_id].values
    #             record_1, record_2 = self.trip_fmt_str_1 % values[:-2], self.trip_fmt_str_2 % values[-2:]
    #             record = record_1 + record_2
    #             writer.writerow(record.split())
    #             if i + 1 % 10_000 == 0 or i + 1 == len(self.selection_ids):
    #                 sys.stdout.write("\rNumber of Vehicles Written = {:,d} ({:.2f} %)".format(
    #                     i+1, (i+1) * 100.0 / expected_number_of_trips))
    #         sys.stdout.write('\n')

    def execute(self):
        super().execute()
        start_time = time.time()
        if self.state == State.OK:
            self.initialize_internal_data(group=1)

        if self.state == State.OK:
            self.read_trips()

            if self.selection_file:
                self.read_selection_file()
            self.filter_trips()
            if self.vehicle_roster_file:
                self.write_nested_trip_file()

        end_time = time.time()
        execution_time = (end_time-start_time)/60.0

        self.logger.info("")
        self.logger.info("")
        if self.state == State.ERROR:
            self.logger.info("Execution completed with ERROR in %.2f minutes" % execution_time)
        else:
            self.logger.info("Number of Vehicles Processed  = {0:10,d}".format(self.input_vehicle_count))
            self.logger.info("Number of Vehicles Written    = {0:10,d}".format(self.output_vehicle_count))
            self.logger.info("Execution completed in %.2f minutes" % execution_time)
        return self.state.value


if __name__ == '__main__':
    DEBUG = 0
    if DEBUG == 1:
        import os
        execution_path = r"C:\Projects\SWIFT\SWIFT_Project_Data\Controls"
        # execution_path = r"C:\Projects\SWIFT\SWIFT_Workspace\Scenarios\S04_Full\STM\STM_A\01_DynusT\01_Controls"
        # control_file = "TripPrep_MergeTrips.ctl"
        control_file = "TripPrep_toTabularTrips.ctl"
        control_file = os.path.join(execution_path, control_file)
        _environ = os.environ.copy()
        try:
            env = {
                'SCEN_DIR': r'C:\Projects\SWIFT\SWIFT_Workspace\Scenarios\Scenario_S4_Full',
            }
            os.environ.update(env)
            exe = TripPrep(input_control_file=control_file)
            exe.execute()
        finally:
            os.environ = _environ
    else:
        from sys import argv
        exe = TripPrep(input_control_file=argv[1])
        state = exe.execute()
        sys.exit(state)
