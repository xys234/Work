import time
import struct
import sys
import re

from services.execution_service import ExecutionService
from services.control_service import State


class PlanPrep(ExecutionService):

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
        'SELECTION_FILE',
        'SELECTION_FORMAT',
    )

    file_keys = (
        'TRAJECTORY_FILE',
        'NEW_TRAJECTORY_FILE',
        'SELECTION_FILE',
    )

    def __init__(self, name='PlanPrep', control_file='PlanPrep.ctl'):
        super().__init__(name, control_file, PlanPrep.required_keys, PlanPrep.acceptable_keys)

        self.input_trajectory_file = None
        self.input_trajectory_format = None
        self.new_trajectory_file = None
        self.new_trajectory_format = None

        self.selection_file = None
        self.selection_format = None

        self.trip_adjustment_map = {}             # {(O, D, Purpose, Occupancy, VehType, Period, Income): Change}
        self.trip_index = {}                        # {(O, D, Purpose, Occupancy, VehType, Period, Income): [vid]}
        self.vehicle_trajectory_index = {}        # {vid: (pos, record_length, tag)}
        self.trip_count = 0
        self.count_paths_written = 0

        self.selections = set()

        self.start_id = 0                       # the new ID is the largest ID + 1

    def update_keys(self):
        if self.state == State.ERROR:
            return

    def initialize_internal_data(self):
        self.input_trajectory_file = self.keys['TRAJECTORY_FILE'].value
        self.input_trajectory_format = self.keys['TRAJECTORY_FORMAT'].value.upper()
        self.new_trajectory_file = self.keys['NEW_TRAJECTORY_FILE'].value
        self.new_trajectory_format = self.keys['NEW_TRAJECTORY_FORMAT'].value.upper()
        self.selection_file = self.keys['SELECTION_FILE'].value
        self.selection_format = self.keys['SELECTION_FORMAT'].value

        # Check key logic
        if self.new_trajectory_format != 'BINARY':
            self.new_trajectory_format = 'TEXT'

        if self.selection_file:
            if self.new_trajectory_format != 'BINARY':
                self.new_trajectory_format = 'BINARY'
                self.logger.warning("Trajectory filtering needs binary output")

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
            self.state = State.ERROR
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
                            self.state = State.ERROR
                            self.logger.error("Error in reading binary trajectory file")
                            eof = True
                        if self.state == State.OK:
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
            self.state = State.ERROR
            self.logger.error("Input trajectories must be in TEXT format for text indexing")

        if self.state == State.OK:
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
            sys.stdout.write("Number of Vehicles Read = {:,d}".format(veh_count))

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

    def filter_trajectories(self):
        """
        Filter the input trajectories by vehicle IDs.
        :return:
        """

        with open(self.new_trajectory_file, mode='wb', buffering=super().OUTPUT_BUFFER) as output_trajectories:
            with open(self.input_trajectory_file, mode='rb') as input_trajectories:
                for i, vid in enumerate(self.selections):
                    if vid in self.vehicle_trajectory_index:
                        pos, record_length, _ = self.vehicle_trajectory_index[vid]
                        input_trajectories.seek(pos)
                        record = input_trajectories.read(record_length)
                        output_trajectories.write(record)
                        self.count_paths_written += 1
                        sys.stdout.write("\rNumber of Trajectories Written = {:,d}".format(i+1))
                    else:
                        self.logger.warning("Trip {:d} NOT Found in Input Trajectories".format(vid))
        sys.stdout.write("\n")

    def execute(self):
        super().execute()

        start_time = time.time()
        if self.state == State.OK:
            self.initialize_internal_data()

        if self.state == State.OK:

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

        end_time = time.time()
        execution_time = (end_time - start_time) / 60.0

        self.logger.info("")
        self.logger.info("")
        if self.state == State.ERROR:
            self.logger.info("Execution completed with ERROR in %.2f minutes" % execution_time)
        else:
            self.logger.info("Execution completed in %.2f minutes" % execution_time)


if __name__ == '__main__':

    DEBUG = 1
    if DEBUG == 1:
        import os
        execution_path = r"C:\Projects\SWIFT\SWIFT_Project_Data\Controls"
        # control_file = "PlanPrep_SelectTrajectories.ctl"
        control_file = "PlanPrep_toTextTrajectories.ctl"
        # control_file = "PlanPrep_AdjustTrajectories.ctl"
        control_file = os.path.join(execution_path, control_file)
        exe = PlanPrep(control_file=control_file)
        exe.execute()
    else:
        from sys import argv
        exe = PlanPrep(control_file=argv[1])
        exe.execute()
