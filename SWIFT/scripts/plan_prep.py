import time
import random
import struct
import sys
import os
import re
from itertools import product

from services.sys_defs import *
from services.execution_service import Execution_Service


class PlanPrep(Execution_Service):

    CHANGE_FILE_HEADER = ('ORIGIN', 'DESTINATION', 'PURPOSE', 'OCCUPANCY', 'VEHTYPE', 'PERIOD', 'INCOME', 'CHANGE')
    PERIOD_MAP_FILE_HEADER = ('PERIOD', 'START', 'END')
    INCOME_MAP_FILE_HEADER = ('INCOME', 'LOW', 'HIGH')
    ZONE_MAP_FILE_HEADER = ('ZONE', 'EQUIV_ZONE', )

    HEADER_PACKING_FMT = "=ibhhbiiiiffibbfbfhff"
    HEADER_TEMPLATE = \
        "Veh #{0:9d} Tag={1:2d} OrigZ={2:5d} " \
        "DestZ={3:5d} Class={4:2d} Tck/HOV={5:2d} UstmN={6:7d} " \
        "DownN={7:7d} DestN={8:7d} STime={9:8.2f} Total Travel Time={10:8.2f} # of Nodes={11:4d} " \
        "VehType{12:2d} EVAC{13:2d} VOT{14:8.2f} tFlag{15:2d} PrefArrTime{16:7.1f} " \
        "TripPur{17:4d} IniGas{18:5.1f} " \
        "Toll{19:6.1f}\n"
    FIELD_ID_VID = 0
    FIELD_ID_TAG = 1
    FIELD_NUMBER_OF_NODES = 11
    FIELD_TOLL = 19

    selection_file_header = "Vehicle_ID"

    required_keys = (
        'TRAJECTORY_FILE',
        'TRAJECTORY_FORMAT',
        'NEW_TRAJECTORY_FILE',
        'NEW_TRAJECTORY_FORMAT',

    )
    acceptable_keys = (
        'TRIP_ADJUSTMENT_FILE',
        'ZONE_MAP_FILE',
        'VEHICLE_ROSTER_FILE',
        'PERIOD_MAP_FILE',
        'INCOME_MAP_FILE',
        'NEW_VEHICLE_MAP_FILE',         # New ID -> Old ID
        'NEW_PROBLEM_FILE',
        'SELECTION_FILE',
        'SELECTION_FORMAT',
    )

    file_keys = (
        'TRAJECTORY_FILE',
        'NEW_TRAJECTORY_FILE',
        'VEHICLE_ROSTER_FILE',
        'TRIP_ADJUSTMENT_FILE',
        'PERIOD_MAP_FILE',
        'INCOME_MAP_FILE',
        'ZONE_MAP_FILE',
        'NEW_VEHICLE_MAP_FILE',
        'NEW_PROBLEM_FILE',
        'SELECTION_FILE',
    )

    def __init__(self, name='PlanPrep', control_file='PlanPrep.ctl'):
        super().__init__(name, control_file, PlanPrep.required_keys, PlanPrep.acceptable_keys)

        self.vehicle_roster_file = None
        self.input_trajectory_file = None
        self.input_trajectory_format = None
        self.new_trajectory_file = None
        self.new_trajectory_format = None
        self.trip_adjustment_file = None
        self.period_map_file = None
        self.vot_map_file = None
        self.zone_map_file = None
        self.problem_file = None
        self.selection_file = None
        self.selection_format = None

        self.trip_adjustment_map = {}             # {(O, D, Purpose, Occupancy, VehType, Period, Income): Change}
        self.trip_index = {}                        # {(O, D, Purpose, Occupancy, VehType, Period, Income): [vid]}
        self.vehicle_trajectory_index = {}        # {vid: (pos, record_length, tag)}
        self.trip_count = 0
        self.count_paths_added = 0
        self.count_paths_deleted = 0
        self.count_paths_written = 0
        self.count_adjustments = 0
        self.adj_list = []
        self.invalid_adj = []
        self.zone_map = {}

        self.period_map = {}
        self.vot_map_to_level = {}
        self.vot_map_to_range = {}
        self.selections = set()

        self.start_id = 0                       # the new ID is the largest ID + 1

    def update_keys(self):
        if self.state == Codes_Execution_Status.ERROR:
            return
        if self.project_dir is not None:
            for k in self.file_keys:
                if KEY_DB[k].group_type == Key_Group_Types.GROUP:
                    for g in range(1, self.highest_group+1):
                        if self.keys[k+"_"+str(g)].value:
                            self.keys[k+"_"+str(g)].value = \
                                os.path.join(self.project_dir, self.keys[k+"_"+str(g)].value)
                else:
                    if self.keys[k].value:
                        self.keys[k].value = os.path.join(self.project_dir, self.keys[k].value)

    def initialize_internal_data(self):
        self.input_trajectory_file = self.keys['TRAJECTORY_FILE'].value
        self.input_trajectory_format = self.keys['TRAJECTORY_FORMAT'].value.upper()
        self.new_trajectory_file = self.keys['NEW_TRAJECTORY_FILE'].value
        self.new_trajectory_format = self.keys['NEW_TRAJECTORY_FORMAT'].value.upper()
        self.trip_adjustment_file = self.keys['TRIP_ADJUSTMENT_FILE'].value
        self.vehicle_roster_file = self.keys['VEHICLE_ROSTER_FILE_'+str(self.highest_group)].value

        self.period_map_file = self.keys['PERIOD_MAP_FILE'].value
        self.vot_map_file = self.keys['INCOME_MAP_FILE'].value
        self.zone_map_file = self.keys['ZONE_MAP_FILE'].value
        self.selection_file = self.keys['SELECTION_FILE'].value
        self.selection_format = self.keys['SELECTION_FORMAT'].value
        self.problem_file = self.keys['NEW_PROBLEM_FILE'].value

        # Check key logic
        if self.new_trajectory_format != 'BINARY':
            self.new_trajectory_format = 'TEXT'

        if self.trip_adjustment_file:
            if self.period_map_file is None:
                self.state = Codes_Execution_Status.ERROR
                self.logger.error("Period map file is required for trajectory adjustment")
            if self.vot_map_file is None:
                self.state = Codes_Execution_Status.ERROR
                self.logger.error("Income map file is required for trajectory adjustment")
            if self.vehicle_roster_file is None:
                self.state = Codes_Execution_Status.ERROR
                self.logger.error("Input vehicle roster file is required for trajectory adjustment")
            if self.problem_file is None:
                self.state = Codes_Execution_Status.ERROR
                self.logger.error("Problem file is required for trajectory adjustment")

        if self.selection_file:
            if self.new_trajectory_format != 'BINARY':
                self.new_trajectory_format = 'BINARY'
                self.logger.warning("Trajectory filtering needs binary output")

    def read_trip_adjustment_file(self):
        """
        read the trip adjustment file; Build the adjustment list
        :return: status code

        The fields are in the following exact order and names.
        ORIGIN	DESTINATION	PURPOSE	OCCUPANCY	VEHTYPE	PERIOD	INCOME	CHANGE NOTES OTHER_FIELDS
        Any fields after "CHANGE" is ignored.

        The adjustment process
        Additions are the first block followed by the deletions.
        New_ID    Old_ID
        10001     25
        10002     88
        ......
        -67       -67
        """

        number_of_fields = len(self.CHANGE_FILE_HEADER)
        with open(self.trip_adjustment_file, mode='r', buffering=self.INPUT_BUFFER) as adj_file:
            for i, line in enumerate(adj_file):
                if i == 0:
                    header = tuple(line.strip().split(',')[:number_of_fields])
                    if header != self.CHANGE_FILE_HEADER:
                        self.logger.error('Trip adjustment file header error; Expect "%s" separated by commas' %
                                          " ".join(self.CHANGE_FILE_HEADER))
                        self.state = Codes_Execution_Status.ERROR

                if i > 0 and self.state == Codes_Execution_Status.OK:
                    self.count_adjustments += 1
                    data = list(map(int, line.strip().split(',')[:number_of_fields]))
                    key, operation = tuple(data[:number_of_fields-1]), data[number_of_fields-1]
                    if key in self.trip_adjustment_map:
                        self.trip_adjustment_map[key] += operation
                    else:
                        self.trip_adjustment_map[key] = operation
                    sys.stdout.write("\rNumber of Adjustment instructions Read = {:,d}".format(self.count_adjustments))
            sys.stdout.write("\n")

        deletions = []
        for key, operation in self.trip_adjustment_map.items():
            matched_key = None
            if key not in self.trip_index:

                # zone equivalence mapping is activated only for additions
                if self.zone_map and operation > 0:
                    equivalent_key = self.find_equivalent_zone_pairs(key)
                    if equivalent_key != key:
                        matched_key = equivalent_key
                    else:
                        self.invalid_adj.append(key + (operation, 1))  # no matching trip
                else:
                    self.invalid_adj.append(key+(operation, 1))
            else:
                matched_key = key

            if matched_key:
                if operation > 0:
                    candidates = self.trip_index[matched_key]
                    candidates = [candidate for candidate in candidates
                                  if self.vehicle_trajectory_index[candidate][2] == 2]  # only complete paths
                    if len(candidates) == 0:
                        self.invalid_adj.append(matched_key+(operation, 2))
                    else:
                        chosen = random.choices(candidates, k=operation)
                        for v in chosen:
                            self.adj_list.append((self.start_id, v))
                            self.start_id += 1
                else:
                    deletions.append((matched_key, operation))

        # Process deletions
        for k, operation in deletions:
            candidates = self.trip_index[k]
            number_of_paths = len(candidates)
            candidates = [candidate for candidate in candidates
                          if self.vehicle_trajectory_index[candidate][2] == 2]  # only complete paths
            number_of_complete_paths = len(candidates)
            if number_of_complete_paths == 0 and number_of_paths > 0:
                self.invalid_adj.append(k + (operation, 2))  # only complete paths
            else:
                if abs(operation) > number_of_complete_paths:
                    for c in candidates:
                        self.adj_list.append((-c, -c))
                    self.invalid_adj.append(k+(abs(operation)-number_of_complete_paths, 3))
                else:
                    chosen = random.sample(candidates, k=abs(operation))
                    for c in chosen:
                        self.adj_list.append((-c, -c))

    def read_period_map_file(self):
        """
        read the period map file
        :return: status code
        """

        row_count = 0
        with open(self.period_map_file, mode='r', buffering=super().INPUT_BUFFER) as period_map_file:
            for i, line in enumerate(period_map_file):
                if i == 0:
                    header = tuple(line.strip().split(',')[:len(self.PERIOD_MAP_FILE_HEADER)])
                    if header != self.PERIOD_MAP_FILE_HEADER:
                        self.logger.error('Period map file header error; Expect "%s" separated by commas' %
                                          " ".join(self.PERIOD_MAP_FILE_HEADER))
                        self.state = Codes_Execution_Status.ERROR

                elif self.state == Codes_Execution_Status.OK:
                    row_count += 1
                    period, pstart, pend = tuple(map(int, line.strip().split(',')[:len(self.PERIOD_MAP_FILE_HEADER)]))
                    if self.period_map is None or period not in self.period_map:
                        self.period_map[period] = [(pstart, pend)]
                    else:
                        self.period_map[period].append((pstart, pend))
        self.logger.info("Read period map file -- %d records" % row_count)

    def to_period(self, departure_time):
        """
        Convert a departure time to a period index
        :param departure_time:
        :return: an integer period index
        """

        for period, ranges in self.period_map.items():
            for r in ranges:
                if r[0] <= departure_time < r[1]:
                    return period

    def read_income_map_file(self):
        """
        read the income map file
        :return: status code

        The income maps include a dict that maps income ranges to income levels and another mapping levels to ranges

        """

        row_count = 0
        with open(self.vot_map_file, mode='r', buffering=super().INPUT_BUFFER) as vot_map_file:
            for i, line in enumerate(vot_map_file):
                if i == 0:
                    header = tuple(line.strip().split(',')[:len(self.INCOME_MAP_FILE_HEADER)])
                    if header != self.INCOME_MAP_FILE_HEADER:
                        self.logger.error('Income map file header error; Expect "%s" separated by commas' %
                                          " ".join(self.INCOME_MAP_FILE_HEADER))
                        self.state = Codes_Execution_Status.ERROR

                elif self.state == Codes_Execution_Status.OK:
                    row_count += 1
                    level, low, high = tuple(map(float, line.strip().split(',')[:len(self.INCOME_MAP_FILE_HEADER)]))
                    self.vot_map_to_level[(low, high)] = int(level)
                    self.vot_map_to_range[int(level)] = low, high

        self.logger.info("Read income map file -- %d records" % row_count)

    def read_zone_map_file(self):
        """
        Read in the zone mapping file; The mapping is one-directional.
        :return:

        zone -> [equivalent zones]

        """

        row_count = 0
        with open(self.zone_map_file, mode='r', buffering=super().INPUT_BUFFER) as zone_map_file:
            for i, line in enumerate(zone_map_file):
                if i == 0:
                    header = tuple(line.strip().split(',')[:len(self.ZONE_MAP_FILE_HEADER)])
                    if header != self.ZONE_MAP_FILE_HEADER:
                        self.logger.error('Period map file header error; Expect "%s" separated by commas' %
                                          " ".join(self.ZONE_MAP_FILE_HEADER))
                        self.state = Codes_Execution_Status.ERROR

                elif self.state == Codes_Execution_Status.OK:
                    row_count += 1
                    zone, equiv_zone = tuple(map(int, line.strip().split(',')[:len(self.ZONE_MAP_FILE_HEADER)]))
                    if self.zone_map is None or zone not in self.zone_map:
                        self.zone_map[zone] = [equiv_zone]
                    else:
                        self.zone_map[zone].append(equiv_zone)
        self.logger.info("Read zone map file -- %d records" % row_count)

    def to_vot_level(self, vot):
        """
        Convert a VoT to an integer income level
        :param vot: A value of time in float
        :return:

        Do a linear search through the vot_map_to_level; Find the first suitable interval
        Could use BST but there are usually only a handful of VoTs
        """

        for vot_range in self.vot_map_to_level.keys():
            if vot_range[0] <= vot < vot_range[1]:
                return self.vot_map_to_level[vot_range]

    def build_trip_index(self):
        """
         Scan the trip file and build the trip index
        :return:

        Trip index (O,D,Purpose,Occupancy,VehType,Period,Income) to [Veh IDs] to support fast lookup
        """

        with open(self.vehicle_roster_file, mode='r', buffering=super().INPUT_BUFFER) as input_trip:
            header = next(input_trip)
            trips_stored = int(header.strip().split()[0])
            next(input_trip)  # skip the vehicle roster header
            for line in input_trip:
                data = line + next(input_trip)
                data = data.strip().split()

                departure_time = float(data[3])
                period = self.to_period(departure_time)
                vot = float(data[15])
                income = self.to_vot_level(vot)

                vid, o, d, purp, occ, vehtype = \
                    int(data[0]), int(data[12]), int(data[20]), int(data[18]), int(data[6]), int(data[5])
                key = (o, d, purp, occ, vehtype, period, income)
                if key not in self.trip_index:
                    self.trip_index[key] = [vid]
                else:
                    self.trip_index[key].append(vid)
                if vid + 1 > self.start_id:
                    self.start_id = vid + 1
                self.trip_count += 1
        if self.trip_count != trips_stored:
            self.logger.warning("Number of trips read inconsistent with the header count %d" % trips_stored)

    def build_vehicle_trajectories_index(self):
        """
        Build the vehicle id index
        :return:

        For binary trajectories, vehicle ID to position as number of bytes and record length. For now,
        the program will only process binary trajectories.
        The program will only build indices into trips that exited the network (Tag=2).
        The indices look like {Vid: (starting_bytes, record_length)}

        """
        if self.input_trajectory_format != "BINARY":
            self.state = Codes_Execution_Status.ERROR
            self.logger.error("Input trajectory file must be binary for binary indexing")
        else:
            self.vehicle_trajectory_index = {}
            veh_count = 0
            with open(file=self.input_trajectory_file, mode='rb') as input_trajectories:
                eof = False
                pos, record_length = 0, 0
                while not eof:
                    read_size = struct.calcsize(self.HEADER_PACKING_FMT)
                    record_length += read_size
                    data = input_trajectories.read(read_size)
                    if not data:
                        eof = True
                    else:
                        try:
                            data = struct.unpack(self.HEADER_PACKING_FMT, data)
                        except struct.error:
                            self.state = Codes_Execution_Status.ERROR
                            self.logger.error("Error in reading binary trajectory file")
                            eof = True
                        if self.state == Codes_Execution_Status.OK:
                            veh_count += 1
                            vid, tag, numnodes, toll = data[0], data[1], data[11], data[19]
                            nested_record_size, _ = self.calc_read_size(numnodes, tag, toll)
                            record_length += nested_record_size
                            self.vehicle_trajectory_index[vid] = (pos, record_length, tag)
                            pos += record_length
                            input_trajectories.seek(pos)
                            record_length = 0
                            sys.stdout.write("\rNumber of Vehicle Trajectories Read = {:,d}".format(veh_count))
            sys.stdout.write("\n")

    def build_vehicle_trajectories_index_text(self):
        """
        Build an index into text trajectory file
        :return:
        """

        if self.input_trajectory_format != "TEXT":
            self.state = Codes_Execution_Status.ERROR
            self.logger.error("Input trajectories must be in TEXT format for text indexing")

        if self.state == Codes_Execution_Status.OK:
            veh_count = 0
            with open(self.input_trajectory_file, mode='r') as trajectory_text_file:
                start_pos = eol_chars = 0
                for line in trajectory_text_file:
                    if line.startswith("Veh #"):
                        veh_count += 1
                        header_length = len(line) - 1       # minus the eol character

                        items = re.findall("[0-9.0-9]+", line.strip())
                        vid = int(items[self.FIELD_ID_VID])
                        tag = int(items[self.FIELD_ID_TAG])
                        number_of_nodes = int(items[self.FIELD_NUMBER_OF_NODES])
                        toll = float(items[self.FIELD_TOLL])

                        if tag == number_of_nodes == 1:
                            eol_chars = 4           # two lines: header + node sequence
                        else:
                            eol_chars = 10
                            if toll > 0:
                                eol_chars += 2

                        record_length, _ = self.calc_read_size(number_of_nodes, tag, toll, binary=False)
                        self.vehicle_trajectory_index[vid] = (start_pos,
                                                              int(header_length+record_length+eol_chars/2), tag)
                        start_pos += int(header_length+record_length+eol_chars)
                        sys.stdout.write("\rNumber of Vehicles Read = {:,d}".format(veh_count))
            sys.stdout.write("Number of Vehicles Read = {:,d}".format(veh_count))

    def adjust_trajectories(self):
        """
        Write the trajectories with adjustment
        :return:
        """

        problem_types = {
            1: 'NO_MATCHING_TRIP',
            2: 'NO_COMPLETE_PATH',
            3: 'UNFULFILLED_DELETION',
        }

        if self.input_trajectory_format != "BINARY" or self.new_trajectory_format != "BINARY":
            self.state = Codes_Execution_Status.ERROR
            self.logger.error("Input and output trajectory files must be binary for trajectory adjustment")
        if self.state == Codes_Execution_Status.OK:
            duplicated_ids = set()         # The old vehicle ids to be duplicated
            deleted_ids = set()         # The old vehicle ids to be duplicated
            with open(self.new_trajectory_file, mode='wb', buffering=super().OUTPUT_BUFFER) as output_trajectories:
                with open(self.input_trajectory_file, mode='rb') as input_trajectories:
                    for new_id, old_id in self.adj_list:
                        if new_id > 0:
                            # always read since the new record depends on the old record
                            pos, record_length, _ = self.vehicle_trajectory_index[old_id]
                            input_trajectories.seek(pos)
                            record = input_trajectories.read(record_length)
                            if old_id not in duplicated_ids:
                                output_trajectories.write(record)
                                self.count_paths_written += 1
                                duplicated_ids.add(old_id)

                            # assemble the new trajectory
                            vid, tag, number_of_nodes, toll, header, nodes, cumu_times, times, delays, tolls = \
                                self.parse_record(record, binary=True)
                            nodes_fmt, floats_fmt, tolls_fmt = self.get_packing_fmt(number_of_nodes)
                            new_header = (new_id, *header[1:])
                            new_record = struct.pack(self.HEADER_PACKING_FMT, *new_header) + \
                                struct.pack(nodes_fmt, *(number_of_nodes, *nodes)) + \
                                struct.pack(floats_fmt, *(number_of_nodes, *cumu_times)) + \
                                struct.pack(floats_fmt, *(number_of_nodes, *times)) + \
                                struct.pack(floats_fmt, *(number_of_nodes, *delays))

                            if toll > 0:
                                new_record += struct.pack(tolls_fmt, *tolls)
                            output_trajectories.write(new_record)
                            self.count_paths_added += 1
                            self.count_paths_written += 1
                        elif new_id < 0:
                            if -old_id not in deleted_ids:
                                self.count_paths_deleted += 1
                                deleted_ids.add(-old_id)

                    for vid, (pos, record_length, _) in self.vehicle_trajectory_index.items():
                        if vid not in duplicated_ids and vid not in deleted_ids:
                            input_trajectories.seek(pos)
                            record = input_trajectories.read(record_length)
                            output_trajectories.write(record)
                            self.count_paths_written += 1

            # Write out invalid adjustments
            with open(self.problem_file, mode='w', buffering=super().OUTPUT_BUFFER) as problem_file:
                header = ",".join(self.CHANGE_FILE_HEADER + ("PROBLEM",)) + "\n"
                problem_file.write(header)
                if len(self.invalid_adj) > 0:
                    for r in self.invalid_adj:
                        r = (*r[:-1], problem_types[r[-1]])
                        record = ",".join(map(str, r)) + "\n"
                        problem_file.write(record)

    @staticmethod
    def get_packing_fmt(number_of_nodes):
        """
        Get packing format strings for parts in a completed trajectory
        :param number_of_nodes:
        :return: a tuple of packing format strings
        """
        template = "=i"             # leading sequence size
        template_toll = "="         # no leading sequence size

        nodes_fmt = template + "i"*number_of_nodes
        floats_fmt = template + "f"*number_of_nodes
        tolls_fmt = template_toll + "f"*number_of_nodes

        return nodes_fmt, floats_fmt, tolls_fmt

    def parse_record(self, record, binary=True):
        """
        Return the vid, tag, number_of_nodes, toll along with header and nested sequences in tuples of numerical data
        :param record:
        :param binary:
        :return:

        for binary input, the header and nested sequences only have numbers but no leading field (sequence size) or
        field name such as "Veh #"

        """

        if binary:
            header_length = struct.calcsize(self.HEADER_PACKING_FMT)
            header = record[:header_length]
            header = struct.unpack(self.HEADER_PACKING_FMT, header)
            vid, tag, number_of_nodes, toll = header[0], header[1], header[11], header[19]
            time_record = True
            if tag == number_of_nodes == 1:
                time_record = False
            nodes, cumu_times, times, delays, tolls = \
                self.parse_nested_sequences(record[header_length:], number_of_nodes, time_record, toll > 0)
        else:
            header_length = 257
            header, nested_sequence = record[:header_length], record[header_length:]

            items = re.findall("[0-9.0-9]+", header.strip())
            vid = int(items[self.FIELD_ID_VID])
            tag = int(items[self.FIELD_ID_TAG])
            number_of_nodes = int(items[self.FIELD_NUMBER_OF_NODES])
            toll = float(items[self.FIELD_TOLL])

            time_records = True
            if number_of_nodes == tag == 1:
                time_records = False
            nodes, cumu_times, times, delays, tolls = \
                self.parse_nested_sequences_text(nested_sequence, time_records, toll > 0)

        return vid, tag, number_of_nodes, toll, header, nodes, cumu_times, times, delays, tolls

    @staticmethod
    def parse_nested_sequences(byte_record, numnodes, time_records=True, read_toll=True):
        """
        Parse the byte sequence for nested trajectory information
        :param byte_record:
        :param numnodes:
        :param time_records:
        :param read_toll:
        :return: tuples of nodes, tuples of cumulative times, tuples of link times, tuples of delays, and
        tuples of tolls if any

        """

        pos = 0
        nodes, cumu_times, times, delays, tolls = None, None, None, None, None
        if isinstance(byte_record, bytes):
            size_seq = struct.unpack("i", byte_record[pos:pos+4])[0]
            pos += 4
            fmt = str(size_seq) + 'i'
            end_pos = pos+4*numnodes
            nodes = struct.unpack(fmt, byte_record[pos:end_pos])
            pos = end_pos

            if time_records:
                # cumulative time
                size_seq = struct.unpack("i", byte_record[pos:pos+4])[0]
                pos += 4
                fmt = str(size_seq) + 'f'
                end_pos = pos + 4 * size_seq
                cumu_times = struct.unpack(fmt, byte_record[pos:end_pos])
                cumu_times = tuple([round(i, 2) for i in cumu_times])
                pos = end_pos

                # link time
                size_seq = struct.unpack("i", byte_record[pos:pos+4])[0]
                pos += 4
                fmt = str(size_seq) + 'f'
                end_pos = pos + 4 * size_seq
                times = struct.unpack(fmt, byte_record[pos:end_pos])
                times = tuple([round(i, 2) for i in times])
                pos = end_pos

                # delay
                size_seq = struct.unpack("i", byte_record[pos:pos+4])[0]
                pos += 4
                fmt = str(size_seq) + 'f'
                end_pos = pos + 4 * size_seq
                delays = struct.unpack(fmt, byte_record[pos:end_pos])
                delays = tuple([round(i, 2) for i in delays])
                pos = end_pos

                if read_toll > 0:
                    fmt = str(size_seq) + 'f'
                    end_pos = pos + 4 * numnodes
                    tolls = struct.unpack(fmt, byte_record[pos:end_pos])
                    tolls = tuple([round(i, 2) for i in tolls])
            return nodes, cumu_times, times, delays, tolls
        else:
            raise TypeError("Input must be bytes")

    @staticmethod
    def parse_nested_sequences_text(record, time_records=True, read_toll=True):
        """
        Parse the text sequence for nested trajectory information
        :param record: the lines of text for nested sequences ONLY. Header is not included
        :param time_records:
        :param read_toll:
        :return: tuples of nodes, tuples of cumulative times, tuples of link times, tuples of delays, and
        tuples of tolls if any
        """

        nodes, cumu_times, times, delays, tolls = None, None, None, None, None
        if isinstance(record, str):
            items = record.strip().split("\n")
            nodes = tuple(map(int, items[0].strip().split()))
            if time_records:
                cumu_times = tuple(map(float, items[1].strip().split()))
                times = tuple(map(float, items[2].strip().split()))
                delays = tuple(map(float, items[3].strip().split()))
            if read_toll:
                tolls = tuple(map(float, items[4].strip().split()))
        return nodes, cumu_times, times, delays, tolls

    @staticmethod
    def calc_read_size(numnodes, tag, toll, binary=True):
        if binary:
            bytes_to_read = 4 + 4 * numnodes  # node sequence always the same
            flag_for_time_records = True
            if numnodes == tag == 1:
                flag_for_time_records = False
            if flag_for_time_records:
                if tag == 2:
                    bytes_to_read += 3 * (4 + 4 * numnodes)
                elif tag == 1:
                    bytes_to_read += 3 * (4 + 4 * (numnodes - 1))
            if toll > 0:
                if tag == 2:
                    bytes_to_read += 4 * numnodes
                elif tag == 1:
                    bytes_to_read += 4 * (numnodes - 1)
            return bytes_to_read, flag_for_time_records
        else:
            # text record length
            record_length = 8 * numnodes    # each field takes up 8 characters
            flag_for_time_records = True
            if numnodes == tag == 1:
                flag_for_time_records = False
            if flag_for_time_records:
                if tag == 2:
                    record_length += 3 * (8 * numnodes)
                elif tag == 1:
                    record_length += 3 * (8 * (numnodes-1))
            if toll > 0:
                if tag == 2:
                    record_length += 8 * numnodes
                elif tag == 1:
                    record_length += 8 * (numnodes-1)
            return record_length, flag_for_time_records

    def find_equivalent_zone_pairs(self, trip_key):
        """
        Find the first matched equivalence zone pair; Match origin zone, then destination zone, and then both
        :param trip_key: a tuple of trip_index
        :return: a tuple of (equiv_origin, equiv_destination)
        """

        origin, destination = trip_key[0], trip_key[1]
        if origin in self.zone_map:
            equivalent_zones = self.zone_map[origin]
            for zone in equivalent_zones:
                if (zone, destination, *trip_key[2:]) in self.trip_index:
                    return (zone, destination, *trip_key[2:])

        if destination in self.zone_map:
            equivalent_zones = self.zone_map[destination]
            for zone in equivalent_zones:
                if (origin, zone, *trip_key[2:]) in self.trip_index:
                    return (origin, zone, *trip_key[2:])

        if origin in self.zone_map and destination in self.zone_map:
            equivalent_zones_origin = self.zone_map[origin]
            equivalent_zones_destination = self.zone_map[destination]
            candidates = [(p[0], p[1]) for p in
                          product(equivalent_zones_origin, equivalent_zones_destination) if p[0] != p[1]]
            for candidate in candidates:
                if candidate+trip_key[2:] in self.trip_index:
                    return candidate+trip_key[2:]
        return trip_key

    def convert_trajectories(self):
        """
        Convert text to/from binary vehicle trajectories
        :return:
        """

        self.build_vehicle_trajectories_index()
        with open(file=self.input_trajectory_file, mode='rb', buffering=super().INPUT_BUFFER) as input_trajectories:
            with open(file=self.new_trajectory_file, mode='w', buffering=super().OUTPUT_BUFFER) as output_trajectories:
                for vid, (pos, record_length, _) in self.vehicle_trajectory_index.items():
                    input_trajectories.seek(pos)
                    data = input_trajectories.read(record_length)
                    vid, tag, number_of_nodes, toll, header, nodes, cumu_times, times, delays, tolls = \
                        self.parse_record(data, binary=True)
                    output_trajectories.write(self.HEADER_TEMPLATE.format(*header))
                    self.count_paths_written += 1

                    # node sequence
                    template = "{:8d}"*number_of_nodes+"\n"
                    record = template.format(*nodes)
                    output_trajectories.write(record)

                    # cumulative time
                    if tag == 1:
                        number_of_nodes -= 1
                    if cumu_times:
                        template = "{:8.2f}"*number_of_nodes+"\n"
                        record = template.format(*cumu_times)
                        output_trajectories.write(record)

                    if times:
                        template = "{:8.2f}"*number_of_nodes+"\n"
                        record = template.format(*times)
                        output_trajectories.write(record)

                    if delays:
                        template = "{:8.2f}"*number_of_nodes+"\n"
                        record = template.format(*delays)
                        output_trajectories.write(record)

                    if tolls:
                        template = "{:8.2f}" * number_of_nodes + "\n"
                        record = template.format(*tolls)
                        output_trajectories.write(record)
        sys.stdout.write("\n")

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

    def filter_trajectories(self):
        """
        Filter the input trajectories by vehicle IDs.
        :return:
        """

        with open(self.new_trajectory_file, mode='wb', buffering=super().OUTPUT_BUFFER) as output_trajectories:
            with open(self.input_trajectory_file, mode='rb') as input_trajectories:
                for i, vid in enumerate(self.selections):
                    pos, record_length, _ = self.vehicle_trajectory_index[vid]
                    input_trajectories.seek(pos)
                    record = input_trajectories.read(record_length)
                    output_trajectories.write(record)
                    self.count_paths_written += 1
                    sys.stdout.write("\rNumber of Trajectories Written = {:,d}".format(i+1))
        sys.stdout.write("\n")

    def execute(self):
        super().execute()

        start_time = time.time()
        if self.state == Codes_Execution_Status.OK:
            self.update_keys()
            self.print_keys()

        if self.state == Codes_Execution_Status.OK:
            self.initialize_internal_data()

        if self.state == Codes_Execution_Status.OK:

            # Format Conversion only
            if self.trip_adjustment_file is None:
                if self.input_trajectory_format == 'BINARY' and self.new_trajectory_format == 'TEXT':
                    self.convert_trajectories()
                    self.logger.info(
                        "Total Number of Trajectories Read            = {0:,d}".format(
                            len(self.vehicle_trajectory_index)))
                    self.logger.info("Total Number of Trajectories Written         = {0:,d}".format(
                        self.count_paths_written))
                if self.selection_file:
                    self.build_vehicle_trajectories_index()
                    self.logger.info(
                        "Total Number of Trajectories Read            = {0:,d}".format(
                            len(self.vehicle_trajectory_index)))
                    self.read_selection_file()
                    self.filter_trajectories()
                    self.logger.info("Total Number of Trajectories Written         = {0:,d}".format(
                        self.count_paths_written))
            else:
                if self.selection_file:
                    self.logger.warning("Selection is ignored when adjustment file is provided")
                self.read_period_map_file()
                if self.state == Codes_Execution_Status.OK:
                    self.read_income_map_file()
                if self.state == Codes_Execution_Status.OK and self.zone_map_file:
                    self.read_zone_map_file()
                if self.state == Codes_Execution_Status.OK:
                    self.build_trip_index()
                    self.logger.info("Total Number of Trips read                   = {0:,d}".format(self.trip_count))
                    self.build_vehicle_trajectories_index()
                    self.logger.info(
                        "Total Number of Trajectories Read            = {0:,d}".format(
                            len(self.vehicle_trajectory_index)))
                    self.read_trip_adjustment_file()
                    self.logger.info("Total Number of Adjustment Instructions Read = {0:,d}".format(
                        self.count_adjustments))
                    self.adjust_trajectories()
                    self.logger.info("Total Number of Trajectories Duplicated      = {0:,d}".format(
                        self.count_paths_added))
                    self.logger.info("Total Number of Trajectories Deleted         = {0:,d}".format(
                        self.count_paths_deleted))
                    self.logger.info("Total Number of Trajectories Written         = {0:,d}".format(
                        self.count_paths_written))
                    self.logger.info("Number of problems                           = {0:,d}".format(
                        len(self.invalid_adj)))

        end_time = time.time()
        execution_time = (end_time - start_time) / 60.0

        self.logger.info("")
        self.logger.info("")
        if self.state == Codes_Execution_Status.ERROR:
            self.logger.info("Execution completed with ERROR in %.2f minutes" % execution_time)
        else:
            self.logger.info("Execution completed in %.2f minutes" % execution_time)


if __name__ == '__main__':

    DEBUG = 0
    if DEBUG == 1:
        import os

        execution_path = r"C:\Projects\SWIFT\SWIFT_Project_Data\Controls"
        # control_file = "PlanPrep_SelectTrajectories.ctl"
        # control_file = "PlanPrep_toTextTrajectories.ctl"
        control_file = "PlanPrep_AdjustTrajectories.ctl"
        control_file = os.path.join(execution_path, control_file)
        exe = PlanPrep(control_file=control_file)
        exe.execute()
    else:
        from sys import argv
        exe = PlanPrep(control_file=argv[1])
        exe.execute()