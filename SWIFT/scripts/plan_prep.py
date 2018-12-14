import time
import random
import struct
import sys
import os

from services.sys_defs import *
from services.execution_service import Execution_Service


class PlanPrep(Execution_Service):

    CHANGE_FILE_HEADER = ('ORIGIN','DESTINATION','PURPOSE','OCCUPANCY','VEHTYPE','PERIOD','INCOME','CHANGE')
    PERIOD_MAP_FILE_HEADER = ('PERIOD', 'START', 'END')
    INCOME_MAP_FILE_HEADER = ('INCOME', 'LOW', 'HIGH')

    HEADER_PACKING_FMT = "=ibhhbiiiiffibbfbfhff"

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

    )

    file_keys = (
        'TRAJECTORY_FILE',
        'NEW_TRAJECTORY_FILE',
        'VEHICLE_ROSTER_FILE',
        'TRIP_ADJUSTMENT_FILE',
        'PERIOD_MAP_FILE',
        'INCOME_MAP_FILE',
        'ZONE_MAP_FILE',
        'NEW_VEHICLE_MAP_FILE'
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

        self.trip_adjustment_map = None             # {(O, D, Purpose, Occupancy, VehType, Period, Income): Change}
        self.trip_index = None                      # {(O, D, Purpose, Occupancy, VehType, Period, Income): [vid]}
        self.vehicle_trajectory_index = None        # {vid: (pos, record_length)}
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
        if self.project_dir is not None:
            for k in self.file_keys:
                if KEY_DB[k].group_type == Key_Group_Types.GROUP:
                    for g in range(1, self.highest_group+1):
                        if self.keys[k+"_"+str(g)].value:
                            self.keys[k+"_"+str(g)].value = os.path.join(self.project_dir, self.keys[k+"_"+str(g)].value)
                else:
                    if self.keys[k].value:
                        self.keys[k].value = os.path.join(self.project_dir, self.keys[k].value)

    def initialize_internal_data(self):
        self.input_trajectory_file = self.keys['TRAJECTORY_FILE'].value
        self.input_trajectory_format = self.keys['TRAJECTORY_FORMAT'].value
        self.new_trajectory_file = self.keys['NEW_TRAJECTORY_FILE'].value
        self.new_trajectory_format = self.keys['NEW_TRAJECTORY_FORMAT'].value
        self.trip_adjustment_file = self.keys['TRIP_ADJUSTMENT_FILE'].value
        self.vehicle_roster_file = self.keys['VEHICLE_ROSTER_FILE_'+str(self.highest_group)].value

        self.period_map_file = self.keys['PERIOD_MAP_FILE'].value
        self.vot_map_file = self.keys['INCOME_MAP_FILE'].value
        self.zone_map_file = self.keys['ZONE_MAP_FILE'].value

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

        For binary trajectories, vehicle ID to position as number of bytes and record length. For now,
        the program will only process binary trajectories.
        The program will only build indices into trips that exited the network (Tag=2).
        The indices look like {Vid: (starting_bytes, record_length)}

        TODO: For text trajectories, vehicle IDs to position as number of character and record length

        """
        if self.input_trajectory_format != "BINARY":
            self.state = Codes_Execution_Status.ERROR
            self.logger.error("Input trajectory file must be binary for trip adjustment")
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
                            self.vehicle_trajectory_index[vid] = (pos, record_length)
                            pos += record_length
                            input_trajectories.seek(pos)
                            record_length = 0
                            sys.stdout.write("\rNumber of Vehicles Read = {:,d}".format(veh_count))
            sys.stdout.write("\n")
            self.logger.info("Number of Vehicles Read = {:,d}".format(veh_count))


    def write_trajectories(self):
        """
        Write the trajectories with adjustment
        :return:
        """

        pass

    @staticmethod
    def parse_nested_sequences(byte_record, numnodes, time_records=True, read_toll=True):
        """
        Parse the byte sequence for nested trajectory information
        :param byte_record:
        :param numnodes:
        :param time_records:
        :param read_toll:
        :return: tuples of nodes, cumulative times, link times, delays, and tolls if any

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
                pos = end_pos

                # link time
                size_seq = struct.unpack("i", byte_record[pos:pos+4])[0]
                pos += 4
                fmt = str(size_seq) + 'f'
                end_pos = pos + 4 * size_seq
                times = struct.unpack(fmt, byte_record[pos:end_pos])
                pos = end_pos

                # delay
                size_seq = struct.unpack("i", byte_record[pos:pos+4])[0]
                pos += 4
                fmt = str(size_seq) + 'f'
                end_pos = pos + 4 * size_seq
                delays = struct.unpack(fmt, byte_record[pos:end_pos])
                pos = end_pos

                if read_toll > 0:
                    fmt = str(size_seq) + 'f'
                    end_pos = pos + 4 * numnodes
                    tolls = struct.unpack(fmt, byte_record[pos:end_pos])
            return nodes, cumu_times, times, delays, tolls
        else:
            raise TypeError("Input must be bytes")

    @staticmethod
    def calc_read_size(numnodes, tag, toll):
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

    def convert_trajectories(self):
        """
        Convert text to/from binary vehicle trajectories
        :return:
        """

        veh_count = 0
        with open(file=self.input_trajectory_file, mode='rb') as input_trajectories:
            with open(file=self.new_trajectory_file, mode='w', buffering=super().OUTPUT_BUFFER) as output_trajectories:
                eof = False
                while not eof:
                    data = input_trajectories.read(struct.calcsize(self.HEADER_PACKING_FMT))
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
                            record = "Veh #{0:9d} Tag={1:2d} OrigZ={2:5d} DestZ={3:5d} Class={4:2d} Tck/HOV={5:2d} UstmN={6:7d} " \
                                     "DownN={7:7d} DestN={8:7d} STime={9:8.2f} Total Travel Time={10:8.2f} # of Nodes={11:4d} " \
                                     "VehType{12:2d} EVAC{13:2d} VOT{14:8.2f} tFlag{15:2d} PrefArrTime{16:7.1f} " \
                                     "TripPur{17:4d} IniGas{18:5.1f} " \
                                     "Toll{19:6.1f}\n".format(*data)
                            output_trajectories.write(record)
                            veh_count += 1
                            sys.stdout.write("\rNumber of Vehicles Read = {:,d}".format(veh_count))
                            # Processed the nested data
                            tag, numnodes, toll = data[1], data[11], data[19]
                            bytes_to_read, flag_for_time_records = self.calc_read_size(numnodes, tag, toll)

                            bytes_record = input_trajectories.read(bytes_to_read)
                            nodes, cumulative_times, times, delays, tolls = \
                                self.parse_nested_sequences(bytes_record, numnodes, flag_for_time_records, toll > 0)

                            # node sequence
                            template = "{:8d}"*numnodes+"\n"
                            record = template.format(*nodes)
                            output_trajectories.write(record)

                            if flag_for_time_records:
                                if tag == 1:
                                    numnodes -= 1
                                # cumulative time
                                template = "{:8.2f}"*numnodes+"\n"
                                record = template.format(*cumulative_times)
                                output_trajectories.write(record)

                                # link time
                                template = "{:8.2f}"*numnodes+"\n"
                                record = template.format(*times)
                                output_trajectories.write(record)

                                # delay
                                template = "{:8.2f}"*numnodes+"\n"
                                record = template.format(*delays)
                                output_trajectories.write(record)

                                if toll > 0:
                                    template = "{:8.2f}" * numnodes + "\n"
                                    record = template.format(*tolls)
                                    output_trajectories.write(record)
                        # if veh_count == 13:
                        #     eof = True
        self.logger.info("Number of Vehicles Read = {:d}".format(veh_count))
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
            else:
                self.build_vehicle_id_index()

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


if __name__ == '__main__':

    DEBUG = 1
    if DEBUG == 1:
        import os
        execution_path = r"C:\Projects\Repo\Work\SWIFT\scripts\test\cases"
        control_file = "PlanPrep_Test_Trajectory_Index.ctl"
        control_file = os.path.join(execution_path, control_file)
        exe = PlanPrep(control_file=control_file)
        exe.execute()
    else:
        from sys import argv
        exe = PlanPrep(control_file=argv[1])
        exe.execute()