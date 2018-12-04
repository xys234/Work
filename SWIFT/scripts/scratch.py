import os
import textwrap

# seeking position considers return as 2 chars
# read position considers return as 1 char
# todo: Read in the adjustment file; Scan the trip file;


def build_trip_index(trip_file):
    """
    Scan the trip file and build the trip index (O,D,Purpose,Occupancy,VehType) to [Veh IDs]
    :param trip_file:
    :return:
    """

    with open(trip_file, mode='r') as input_trip:
        next(input_trip)
        next(input_trip)  # skip the vehicle roster header
        for line in input_trip:
            data = line + next(input)
            data = data.split()





def build_vehicle_id_index(veh_trajectory_file):
    veh_id_pos_index = {}
    prev_pos, pos, veh_count, offset, prev_line = 0, 0, 0, 0, 0
    with open(veh_trajectory_file, mode='r', buffering=10_000_000) as veh_file:
        for i, line in enumerate(veh_file):
            if line.startswith("Veh #"):
                if veh_count == 0:
                    prev_pos = pos
                else:
                    offset = pos - prev_pos - (i-prev_line)
                    veh_id_pos_index[veh_id] = (prev_pos, offset)
                    prev_pos = pos
                prev_line = i
                veh_count += 1
                veh_id = int(line[:15].split()[2])
            pos += len(line)+1
            if i > 20:
                break
    return veh_id_pos_index


def write_trajectories(veh_trajectory_file, vehicle_id_index, adj_list, output):
    """

    :param veh_trajectory_file:
    :param vehicle_id_index:
    :param adj_list: a list of vehicle ids. Negative id means deletion
    :type list
    :return:
    """
    VEHICLE_ID_FIELD_LENGTH =14
    VEHICLE_FIELD_HEADER = "Veh #"
    start_new_id = 10_000
    ids = set()
    with open(veh_trajectory_file, mode='r') as input:
        with open(output, mode='w') as out:
            for v in adj_list:
                if v > 0:
                    start_pos, offset = vehicle_id_index[v]
                    input.seek(start_pos)
                    record = input.read(offset)
                    if v not in ids:
                        ids.add(v)
                        # add the original trajectory
                        out.write(record)
                    new_veh_id_field = VEHICLE_FIELD_HEADER + str(start_new_id).rjust(9)
                    record = new_veh_id_field + record[VEHICLE_ID_FIELD_LENGTH:]
                    out.write(record)
                    start_new_id += 1


def wrap_list(lst, items_per_line=5):
    lines = []
    for i in range(0, len(lst), items_per_line):
        chunk = lst[i:i + items_per_line]
        line = ", ".join("{!r}".format(x) for x in chunk)
        lines.append(line)
    return "" + ",\n ".join(lines) + ""


if __name__ == '__main__':

    data_dir = r'C:\Projects\Repo\Work\SWIFT\data\Dynus_T'
    veh_trajectory_file = 'VehTrajectory.dat'
    # veh_trajectory_file = 'input.dat'
    out_file = 'test.dat'
    veh_trajectory_file = os.path.join(data_dir, veh_trajectory_file)
    out_file = os.path.join(data_dir, out_file)

    # with open(veh_trajectory_file, mode='r') as f:
    #     pos = 0
    #     for i, line in enumerate(f):
    #         pos += len(line)
    #         print("Line {0:d} = {1:d} chars".format(i+1, len(line)+1))
    #         if i > 10:
    #             break
    #
    with open(veh_trajectory_file, mode='r') as f:
        with open(out_file, mode='w') as out:
            f.seek(532)
            data = f.read(357)
            out.write(data)

    veh_id_pos_index = build_vehicle_id_index(veh_trajectory_file)
    adj_list = [
        160, 160, -519, 403
    ]
    write_trajectories(veh_trajectory_file, veh_id_pos_index, adj_list, out_file)

