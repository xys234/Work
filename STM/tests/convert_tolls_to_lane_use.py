"""
This script converts DynusT tolls to TRANSIMS lane use


"""

#
# enum Use_Type {         //---- facility use restrictions ----
# 	ANY, WALK, BIKE, CAR, HOV2P, HOV3P, TRUCK, BUS, RAIL, SOV,
# 	HOV2, HOV3, HOV4, LIGHTTRUCK, HEAVYTRUCK, TAXI, RESTRICTED, NONE,
# };

from enum import Enum
import csv
from internals.sorted_collection import SortedCollection


class LaneUseType(Enum):
    APPLY = 'APPLY'
    PROHIBIT = 'PROHIBIT'


class VehicleTypeMap(Enum):
    SOV = 'SOV'
    HOV2 = 'HOV2'
    HOV3 = 'HOV3'


def minutes_to_time_string(minutes):
    """
    Convert integer minutes to time string such as 6:00..6:30, 15:00..16:20
    :param minutes:  a tuple of integer minutes
    :return:
    """

    hr, m = int(minutes / 60), minutes - int(minutes / 60) * 60
    return ":".join((str(hr), str(m).zfill(2)))


def get_cutoff_times(toll_file):
    cutoff_times = []
    with open(toll_file, mode='r') as input_toll:
        next(input_toll)
        next(input_toll)
        for line in input_toll:
            data = line.split()
            start, end = int(data[3]), int(data[4])
            cutoff_times.extend((start, end))
        cutoff_times = sorted(list(set(cutoff_times)))
        cutoff_times = [(t, st) for t, st in zip(cutoff_times, list(map(minutes_to_time_string, cutoff_times)))
                        if t <= 1440]
        cutoff_times = SortedCollection(cutoff_times, key=lambda x: x[0])
        return cutoff_times


def get_toll_header(cutoff_times):
    header = []
    for cutoff_time in cutoff_times:
        time_str = 'TOLL_'+''.join(cutoff_time[1].split(':'))
        header.append(time_str)
    return header


def get_lane_use_records(anode, bnode, link_map, start, end, cutoff_times, toll, vtype):

    filler_records = tuple([0 for _ in range(11)])

    toll_record = [0.0 for _ in cutoff_times]
    lane_use_type = LaneUseType.PROHIBIT.value
    if toll < 1000:
        lane_use_type = LaneUseType.APPLY.value
        for i, c in enumerate(cutoff_times):
            if start <= c[0] <= end:
                toll_record[i] = toll
    toll_record = tuple(toll_record)

    link_id = link_map[(anode, bnode)]
    dir, lanes, use, mintype, maxtype, mintrav, maxtrav = 0, 0, 0, 0, 0, 0, 0
    vtype = vtype.upper()
    if vtype == 'SOV':
        use = 'SOV'
        mintype, maxtype = 1, 1
    elif vtype == 'HOV2':
        use = 'HOV2'
        mintype, maxtype = 2, 2
    elif vtype == 'HOV3':
        use = 'HOV3'
        mintype, maxtype = 3, 3
    elif vtype == 'TAXI':
        use = 'TAXI'
        mintype, maxtype = 4, 4
    elif vtype == 'LIGHTTRUCK':
        use = 'LIGHTTRUCK'
        mintype, maxtype = 5, 5
    elif vtype == 'HEAVYTRUCK':
        use = 'HEAVYTRUCK'
        mintype, maxtype = 6, 6

    string_start, string_end = minutes_to_time_string(start), minutes_to_time_string(end)
    return (link_id, dir, lanes, lane_use_type, use, mintype, maxtype, mintrav, maxtrav, string_start, string_end) \
           + filler_records + toll_record


def convert_tolls_to_lane_use(link_file, toll_file, output_lane_use_file):
    """

    :param link_file: TRANSIMS link file
    :param toll_file:
    :param output_lane_use_file:
    :param vehicle_type_map: DynusT vehicle type mapped to TRANSIMS vehicle type and traveler type combination
    :return:
    """

    fmt_lane_use_file = '{:d},{:d},{:d},{:s},{:s},{:d},{:d},{:d},{:d},{:s},' \
                        '{:s},{:d},{:d},{:d},{:d},{:d},{:d},{:d},{:d},{:d},{:d},{:d},'
    header = '''LINK,DIR,LANES,TYPE,USE,MIN_TYPE,MAX_TYPE,MIN_TRAV,MAX_TRAV,START,END,LENGTH,OFFSET,TOLL,MIN_RATE,MAX_RATE,MIN_DELAY,MAX_DELAY,SPEED,SPD_FAC,CAPACITY,CAP_FAC'''.split(',')

    # def_file = [
    #     'TRANSIMS70', 'COMMA_DELIMITED', '1'
    #     'LINK', 'INTEGER', '1', '10'
    #     'DIR', 'INTEGER', '2', '1'
    #     'LANES', 'STRING', '3', '8', 'LANE_RANGE_TYPE'
    #     'TYPE', 'STRING', '4', '10', 'RESTRICTION_TYPE'
    #     'USE', 'STRING', '5', '128', 'USE_TYPE'
    #     'MIN_TYPE', 'UNSIGNED', '6', '3', 'VEHICLE_TYPE'
    #     'MAX_TYPE', 'UNSIGNED', '7', '3', 'VEHICLE_TYPE'
    #     'MIN_TRAV', 'UNSIGNED', '8', '3'
    #     'MAX_TRAV, UNSIGNED, 9, 3
    #     'START', 'TIME', '10', '16', 'HOUR_CLOCK'
    #     'END', 'TIME', '11', '16', 'HOUR_CLOCK'
    #     'LENGTH', 'DOUBLE', '12', 8.1, FEET''
    #     'OFFSET', 'DOUBLE', '13', 8.1, FEET
    #     'TOLL', 'DOUBLE', '14', 11.1, CENTS
    #     'MIN_RATE', 'DOUBLE', '15', 8.1, CENTS/MILE
    #     'MAX_RATE', 'DOUBLE', '16', 8.1, CENTS/MILE
    #     'MIN_DELAY', 'DOUBLE', '17', 8.1, SECONDS
    #     'MAX_DELAY', 'DOUBLE', '18', 8.1, SECONDS
    #     'SPEED', 'DOUBLE', '19', 5.1, MPH
    #     'SPD_FAC', 'DOUBLE', 20, 5.2
    #     'CAPACITY', 'UNSIGNED', 21, 8, VPH
    #     'CAP_FAC', 'DOUBLE', 22, 6.2
    #     'NOTES', 'STRING', 45, 128
    #             ]

    link_map = {}   # this assumes no duplicate ab nodes
    cutoff_times = []
    records = []

    with open(link_file, mode='r') as input_link:
        next(input_link)    # skip header
        for line in input_link:
            data = line.split(',')
            link_id = int(data[0])
            a, b = int(data[2]), int(data[3])
            if (a, b) in link_map:
                print('Duplicate A-B Node Found {:!r}'.format((a, b)))
            else:
                link_map[(a, b)] = link_id

    cutoff_times = get_cutoff_times(toll_file)
    fmt_lane_use_file = fmt_lane_use_file + ','.join(['{:.2f}']*(len(cutoff_times)-1))
    toll_header = get_toll_header(cutoff_times)
    header = header+toll_header+['NOTES']

    with open(toll_file, mode='r') as input_toll:
        next(input_toll)
        next(input_toll)

        for line in input_toll:
            data = line.split()
            from_id, to_id, downstream_id = int(data[0]), int(data[1]), int(data[2])
            start, end, toll_type = int(data[3]), int(data[4]), int(data[5])
            toll_sov, toll_hov2, toll_hov3, toll_taxi, toll_md, toll_hv = \
                float(data[6]), float(data[7]), float(data[8]), float(data[9]), float(data[10]), float(data[11])
            end = min(1440, end)

            # SOV
            record = get_lane_use_records(from_id, to_id, link_map, start, end, cutoff_times, toll_sov, 'SOV')
            records.append(record)
            record = get_lane_use_records(to_id, downstream_id, link_map, start, end, cutoff_times, toll_sov, 'SOV')
            records.append(record)

            # HOV2
            record = get_lane_use_records(from_id, to_id, link_map, start, end, cutoff_times, toll_hov2, 'HOV2')
            records.append(record)
            record = get_lane_use_records(to_id, downstream_id, link_map, start, end, cutoff_times, toll_hov2, 'HOV2')
            records.append(record)

            # HOV3
            record = get_lane_use_records(from_id, to_id, link_map, start, end, cutoff_times, toll_hov3, 'HOV3')
            records.append(record)
            record = get_lane_use_records(to_id, downstream_id, link_map, start, end, cutoff_times, toll_hov3, 'HOV3')
            records.append(record)

            # TAXI
            record = get_lane_use_records(from_id, to_id, link_map, start, end, cutoff_times, toll_taxi, 'TAXI')
            records.append(record)
            record = get_lane_use_records(to_id, downstream_id, link_map, start, end, cutoff_times, toll_taxi, 'TAXI')
            records.append(record)

            # LIGHTTRUCK
            record = get_lane_use_records(from_id, to_id, link_map, start, end, cutoff_times, toll_md, 'LIGHTTRUCK')
            records.append(record)
            record = get_lane_use_records(to_id, downstream_id, link_map, start, end, cutoff_times, toll_md, 'LIGHTTRUCK')
            records.append(record)

            # HEAVYTRUCK
            record = get_lane_use_records(from_id, to_id, link_map, start, end, cutoff_times, toll_hv, 'HEAVYTRUCK')
            records.append(record)
            record = get_lane_use_records(to_id, downstream_id, link_map, start, end, cutoff_times, toll_hv, 'HEAVYTRUCK')
            records.append(record)

    records.sort(key=lambda x: x[0])
    with open(output_lane_use_file, mode='w', newline='') as output_lane_use:
        writer = csv.writer(output_lane_use)
        writer.writerow(header)
        for record in records:
            string_record = fmt_lane_use_file.format(*record).split(',') + ['']
            writer.writerow(string_record)


if __name__ == '__main__':
    link_file = r'I:\SWIFT\TRANSIMS\Network\link.csv'
    toll_file = r'L:\DCS\Projects\_Legacy\60563434_SWIFT\400_Technical\SWIFT_Workspace\Scenarios\Scenario_2017\STM\STM_A\01_DynusT\03_Model\toll.dat'
    # toll_file = r'L:\DCS\Projects\_Legacy\60563434_SWIFT\400_Technical\SWIFT_Workspace\Scenarios\Scenario_2017\STM\STM_A\01_DynusT\03_Model\toll_test.dat'
    output_lane_use_file = r'I:\SWIFT\TRANSIMS\Network\laneuse.csv'
    cutoff_times = get_cutoff_times(toll_file)
    convert_tolls_to_lane_use(link_file, toll_file, output_lane_use_file)
