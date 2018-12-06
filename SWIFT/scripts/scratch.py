import os
import sys
import random

# seeking position considers return as 2 chars
# read position considers return as 1 char


def build_trip_index(trip_file):
    """
    Scan the trip file and build the trip index (O,D,Purpose,Occupancy,VehType) to [Veh IDs]
    :param trip_file:
    :return:
    """

    trip_count = 0
    trip_index = {}
    with open(trip_file, mode='r') as input_trip:
        next(input_trip)
        next(input_trip)  # skip the vehicle roster header
        for line in input_trip:
            data = line + next(input_trip)
            data = data.strip().split()
            vid, o, d, purp, occ, vehtype = int(data[0]), int(data[12]), int(data[20]), int(data[18]), int(data[6]), int(data[5])
            key = (o, d, purp, occ, vehtype)
            if key not in trip_index:
                trip_index[key] = [vid]
            else:
                trip_index[key].append(vid)
            trip_count += 1
    return trip_index, trip_count


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


def build_vehicle_adj_list(path_adjustment_file, trip_index, start_id,
                           origin_field='O',
                           dest_field='D',
                           vehtype_field='VEHTYPE',
                           purpose_field='PURPOSE',
                           occ_field='OCCUPANCY',
                           change_field='CHANGE',
                           ):
    """

    :param path_adjustment_file:
    :param trip_index:
    :param start_id:
    :param origin_field:
    :param dest_field:
    :param vehtype_field:
    :param purpose_field:
    :param occ_field:
    :param change_field:
    :return:


    Additions are the first block followed by the deletions.
    New_ID    Old_ID
    10001     25
    10002     88
    ......
    -67       -67

    """

   
    deletions = []
    adj_list = []
    invalid_adj = []        # a list of records in str
    with open(path_adjustment_file, mode='r') as input_adj:
        header = next(input_adj).strip().split()     # parse the header
        origin_field_ind = header.index(origin_field)
        dest_field_ind = header.index(dest_field)
        vehtype_field_ind = header.index(vehtype_field)
        purpose_field_ind = header.index(purpose_field)
        occ_field_ind = header.index(occ_field)
        change_field_ind = header.index(change_field)

        for line in input_adj:
            data = list(map(int, line.strip().split()))
            key, operation = (
                                    data[origin_field_ind],
                                    data[dest_field_ind],
                                    data[purpose_field_ind],
                                    data[occ_field_ind],
                                    data[vehtype_field_ind],
                                   ), data[change_field_ind]
            if key not in trip_index:
                invalid_adj.append(data.append("INVALID_COMBINATION"))
            else:
                if operation > 0:
                    candidates = trip_index[key]
                    chosen = random.choice(candidates, k=operation)
                    for v in chosen:
                        adj_list.append((start_id, v))
                        start_id += 1
                else:
                    deletions.append((key, operation))

    # Process deletions
    for deletion in deletions:
        k, oper = deletion
        candidates = trip_index[k]
        if abs(oper) > len(candidates):
            invalid_adj.append(list(k).extend([abs(oper)-len(candidates), "UNFILLED_DELETION"]))
        else:
            chosen = random.sample(candidates, k=abs(oper))
            for c in chosen:
                adj_list.append((-c, -c))

    return adj_list, invalid_adj


def write_trajectories(veh_trajectory_file, vehicle_id_index, adj_list, output):
    """

    :param veh_trajectory_file:
    :param vehicle_id_index:
    :param adj_list: a list of tuples (new_id, old_id). Negative new_id means deletion
    :return:
    """
    VEHICLE_ID_FIELD_LENGTH = 14
    VEHICLE_FIELD_HEADER = "Veh #"
    start_new_id = 10_000
    ids = set()
    with open(veh_trajectory_file, mode='r') as input_veh:
        with open(output, mode='w') as out:
            for new_id, old_id in adj_list:
                if new_id > 0:
                    start_pos, offset = vehicle_id_index[old_id]
                    input_veh.seek(start_pos)
                    record = input_veh.read(offset)
                    if old_id not in ids:
                        ids.add(old_id)
                        out.write(record)   # add the original trajectory
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
    vehicle_roster_file = 'Vehicles_HNW_AM_with_Header.dat'
    vehicle_roster_file = os.path.join(data_dir, vehicle_roster_file)


    # with open(veh_trajectory_file, mode='r') as f:
    #     pos = 0
    #     for i, line in enumerate(f):
    #         pos += len(line)
    #         print("Line {0:d} = {1:d} chars".format(i+1, len(line)+1))
    #         if i > 10:
    #             break

    # with open(veh_trajectory_file, mode='r') as f:
    #     with open(out_file, mode='w') as out:
    #         f.seek(532)
    #         data = f.read(357)
    #         out.write(data)
    #
    # veh_id_pos_index = build_vehicle_id_index(veh_trajectory_file)
    # adj_list = [
    #     160, 160, -519, 403
    # ]
    # write_trajectories(veh_trajectory_file, veh_id_pos_index, adj_list, out_file)


    trip_index, trip_count = build_trip_index(vehicle_roster_file)
    print("{0:d} Trips processed".format(trip_count))
    print(sys.getsizeof(trip_index) / 1024576.0)
