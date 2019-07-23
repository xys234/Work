"""

Analyze converted trajectories (b03 file) and raw ITF trajectories


"""


import struct
import sys
import csv
import os

fmt3 = '<lBBBxHHHxxLLffffqHxxxxxx'
fsize3 = struct.calcsize(fmt3)

HEADER_PACKING_FMT = "=ibhhbiiiiffibbfbfhff"

# for b03 file
FLAT_TRAJECTORY_HEADER = [f.strip() for f in
  "vid, tag, uclass, vtyp, origz, destz, nodes, node0, node1, start, end, delay, dist, totveh, purpose".split(',')]

# for ITF file
FLAT_SKIM_HEADER = [f.strip() for f in
  "vid, tag, origz, destz, class, tck_hov, ustmn, downn, destn, stime, " \
  "travel_time, nodes, vehtype, evac, vot, tflag, parr, purp, gas, toll".split(',')]

HEADER_TEMPLATE = \
    "Veh #{0:9d} Tag={1:2d} OrigZ={2:5d} " \
    "DestZ={3:5d} Class={4:2d} Tck/HOV={5:2d} UstmN={6:7d} " \
    "DownN={7:7d} DestN={8:7d} STime={9:8.2f} Total Travel Time={10:8.2f} # of Nodes={11:4d} " \
    "VehType{12:2d} EVAC{13:2d} VOT{14:8.2f} tFlag{15:2d} PrefArrTime{16:7.1f} " \
    "TripPur{17:4d} IniGas{18:5.1f} " \
    "Toll{19:6.1f}\n"

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
        record_length = 8 * numnodes  # each field takes up 8 characters
        flag_for_time_records = True
        if numnodes == tag == 1:
            flag_for_time_records = False
        if flag_for_time_records:
            if tag == 2:
                record_length += 3 * (8 * numnodes)
            elif tag == 1:
                record_length += 3 * (8 * (numnodes - 1))
        if toll > 0:
            if tag == 2:
                record_length += 8 * numnodes
            elif tag == 1:
                record_length += 8 * (numnodes - 1)
        return record_length, flag_for_time_records


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
        size_seq = struct.unpack("i", byte_record[pos:pos + 4])[0]
        pos += 4
        fmt = str(size_seq) + 'i'
        end_pos = pos + 4 * numnodes
        nodes = struct.unpack(fmt, byte_record[pos:end_pos])
        pos = end_pos

        if time_records:
            # cumulative time
            size_seq = struct.unpack("i", byte_record[pos:pos + 4])[0]
            pos += 4
            fmt = str(size_seq) + 'f'
            end_pos = pos + 4 * size_seq
            cumu_times = struct.unpack(fmt, byte_record[pos:end_pos])
            cumu_times = tuple([round(i, 2) for i in cumu_times])
            pos = end_pos

            # link time
            size_seq = struct.unpack("i", byte_record[pos:pos + 4])[0]
            pos += 4
            fmt = str(size_seq) + 'f'
            end_pos = pos + 4 * size_seq
            times = struct.unpack(fmt, byte_record[pos:end_pos])
            times = tuple([round(i, 2) for i in times])
            pos = end_pos

            # delay
            size_seq = struct.unpack("i", byte_record[pos:pos + 4])[0]
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


def parse_record(record, binary=True):
    """
    Return the vid, tag, number_of_nodes, toll along with header and nested sequences in tuples of numerical data
    :param record:
    :param binary:
    :return:

    for binary input, the header and nested sequences only have numbers but no leading field (sequence size) or
    field name such as "Veh #"

    """

    if binary:
        header_length = struct.calcsize(HEADER_PACKING_FMT)
        header = record[:header_length]
        header = struct.unpack(HEADER_PACKING_FMT, header)
        vid, tag, number_of_nodes, toll = header[0], header[1], header[11], header[19]
        time_record = True
        if tag == number_of_nodes == 1:
            time_record = False
        nodes, cumu_times, times, delays, tolls = \
            parse_nested_sequences(record[header_length:], number_of_nodes, time_record, toll > 0)
        return vid, tag, number_of_nodes, toll, header, nodes, cumu_times, times, delays, tolls


def process_itf(trajectory_file, flat_skim_file):
    with open(trajectory_file, mode='rb') as input_trajectories, \
            open(flat_skim_file, mode='w', newline='', buffering=10_000_000) as output_trajectory:
        writer = csv.writer(output_trajectory)
        writer.writerow(FLAT_SKIM_HEADER)

        OK = 1
        eof = False
        veh_count = 0
        while not eof:
            read_size = struct.calcsize(HEADER_PACKING_FMT)
            data = input_trajectories.read(read_size)
            if not data:
                eof = True
            else:
                try:
                    data = struct.unpack(HEADER_PACKING_FMT, data)
                except struct.error:
                    OK = 0
                    eof = True
                if OK:
                    veh_count += 1
                    vid, tag, number_of_nodes, toll, header, nodes, cumu_times, times, delays, tolls = data
                    sys.stdout.write("\rNumber of Vehicle Trajectories Read = {:,d}".format(veh_count))
                    writer.writerow(data)
    sys.stdout.write("\n")
    print("Number of Vehicle Trajectories Read = {:,d}".format(veh_count))


def filter_trajectories(trajectory_file, maxid, text_trajectory, binary_trajectory=None):
    output_trajectory_binary = None
    if binary_trajectory:
        output_trajectory_binary = open(binary_trajectory, mode='wb', buffering=10_000_000)
    with open(trajectory_file, mode='rb') as input_trajectory, \
            open(text_trajectory, mode='w', newline='', buffering=10_000_000) as output_trajectory_text:
                OK = 1
                eof = False
                veh_count = 0
                while not eof:
                    read_size = struct.calcsize(HEADER_PACKING_FMT)
                    data = input_trajectory.read(read_size)
                    if not data:
                        eof = True
                    else:
                        try:
                            data = parse_record(data)
                        except struct.error:
                            OK = 0
                            eof = True
                        if OK:
                            veh_count += 1
                            vid, tag, numnodes, toll = data[0], data[1], data[11], data[19]
                            nested_record_size, _ = calc_read_size(numnodes, tag, toll)
                            _ = input_trajectory.read(nested_record_size)
                            sys.stdout.write("\rNumber of Vehicle Trajectories Read = {:,d}".format(veh_count))
                            writer.writerow(data)

    if binary_trajectory:
        output_trajectory_binary.close()

def process_b03(trajectory_file, flat_trajectory_file):

    with open(trajectory_file, mode='rb') as input_trajectory, \
            open(flat_trajectory_file, mode='w', newline='', buffering=10_000_000) as output_trajectory:

        writer = csv.writer(output_trajectory)
        writer.writerow(FLAT_TRAJECTORY_HEADER)

        # read first record
        data = input_trajectory.read(fsize3)
        fields = struct.unpack(fmt3, data)
        expected_vehicles = fields[13]
        vehicles_read, total_exits, total_incomplete = 0, 0, 0

        for i in range(expected_vehicles):

            data = input_trajectory.read(fsize3)
            fields = struct.unpack(fmt3, data)
            tag = fields[1]
            vehicles_read += 1

            if tag == 1:
                total_incomplete += 1
            else:
                total_exits += 1
            writer.writerow(fields)
            if vehicles_read % 10000 == 0 or vehicles_read == expected_vehicles:
                sys.stdout.write("\rNumber of Vehicles Written = {:,d} ({:.0f} %)".format(
                    total_exits, total_exits * 100.0 / expected_vehicles))

        sys.stdout.write("\n")
        print("Total Vehicles Read       = {:,d}".format(vehicles_read))
        print("Total Vehicles Exited     = {:,d}".format(total_exits))
        print("Total Vehicles Incomplete = {:,d}".format(total_incomplete))


if __name__ == "__main__":
    execution_dir = r'C:\Projects\SWIFT\SWIFT_Workspace\Scenarios\Scenario_S0\STM\STM_A\01_DynusT\03_Model'
    input_trajectory_file = os.path.join(execution_dir, 'VehTrajectory.b03')
    output_trajectory_file = os.path.join(execution_dir, 'Vehicle_Skim.csv')
    # process_b03(input_trajectory_file, output_trajectory_file)
    process_itf(input_trajectory_file, output_trajectory_file)
