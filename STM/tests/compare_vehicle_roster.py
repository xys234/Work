"""

Compare two vehicle roster file based on downstream node of generation link and destination zone


"""

import sys
import csv
from services.file_service import TripFileRecord, File


def read_text_trips(input_vehicle_roster_file):
    """
    Read in all input trip rosters
    :return: a dict for trip index for downstream node of generation link and destination zone
    {(downN, destZ): [tripIDs]}
    """
    input_vehicle_count = 0
    trip_index = set()
    with open(input_vehicle_roster_file, mode='r') as input_roster:
        expected_number_of_trips = trip_count = 0
        for i, line in enumerate(input_roster):
            if i == 0:
                expected_number_of_trips = int(line.strip().split()[0])
            if i > 1:
                line = line.strip() + next(input_roster)
                input_vehicle_count += 1
                trip_count += 1
                if trip_count % 10_000 == 0 or trip_count == expected_number_of_trips:
                    sys.stdout.write("\rNumber of Vehicles Read = {:,d} ({:.2f} %)".format(
                        trip_count, trip_count * 100.0 / expected_number_of_trips))
                trip = TripFileRecord()
                trip.from_string(line.split())

                vid, upstream, downstream, dzone = trip.vehid, trip.upstream, trip.downstream, trip.dzone
                if (upstream, downstream, dzone) not in trip_index:
                    trip_index.add((upstream, downstream, dzone))
        sys.stdout.write('\n')
    sys.stdout.write("Number of Vehicles Read in Trip Roster = {:,d}".format(trip_count))
    return trip_index, input_vehicle_count


def compare_trips(trip_file_1, trip_file_2, output_trip_file, flat_trip_file=None):
    """
    Compare trip1 and trip2 based on ODs and keep only trips whose ODs are in trip1
    :param trip_file_1:
    :param trip_file_2:
    :return:
    """

    trip_fmt_str_flat = "{:d},{:d},{:d},{:.1f},{:d},{:d},{:d},{:d},{:d},{:d},{:.4f},{:.4f},{:d}," \
                        "{:d},{:.8f},{:.2f},{:d},{:.1f},{:d},{:.1f},{:d},{:.2f}"
    TRIP_FILE_HEADER = '''vid usec dsec stime vehcls vehtype 
                                          ioc #ONode #IntDe info ribf comp Izone Evac InitPos VoT tFlag pArrTime TP IniGas 
                                          DZone waitTime'''

    temp_file = output_trip_file + ".tmp"
    # trip_index_1, trip_count_1 = read_text_trips(trip_file_1)
    # common_trip_count = 0
    #
    # with open(trip_file_2, mode='r') as input_roster, \
    #     open(file=temp_file, mode='w', buffering=10_000_000) as output_roster:
    #     expected_number_of_trips = trip_count = 0
    #     for i, line in enumerate(input_roster):
    #         if i == 0:
    #             expected_number_of_trips = int(line.strip().split()[0])
    #         if i > 1:
    #             line = line.strip() + next(input_roster)
    #             trip_count += 1
    #             if trip_count % 10_000 == 0 or trip_count == expected_number_of_trips:
    #                 sys.stdout.write("\rNumber of Vehicles Read in Trip File 2 = {:,d} ({:.2f} %)".format(
    #                     trip_count, trip_count * 100.0 / expected_number_of_trips))
    #             trip = TripFileRecord()
    #             trip.from_string(line.split())
    #
    #             vid, upstream, downstream, dzone = trip.vehid, trip.upstream, trip.downstream, trip.dzone
    #             if (upstream, downstream, dzone) in trip_index_1:
    #                 output_roster.write(str(trip))
    #                 common_trip_count += 1
    #
    #     sys.stdout.write('\n')
    #
    # print('Number of Upstream-Downstream-Destination Combinations in Trip File 2 AND in Trip File 1 = {:,d}'.format(
    #     common_trip_count
    # ))
    # print('Number of Upstream-Downstream-Destination Combinations in Trip File 2 NOT in Trip File 1 = {:,d}'.format(
    #     trip_count_1 - common_trip_count
    # ))

    # final output
    common_trip_count = 22_130_904
    writer, f = None, None
    if flat_trip_file:
        f = open(file=flat_trip_file, mode='w', newline='', buffering=10_000_000)
        writer = csv.writer(f)
        writer.writerow(TRIP_FILE_HEADER.split())

    trip_count = 0
    with open(output_trip_file, mode='w', buffering=10_000_000) as output_roster:
        s = '%12d           1    # of vehicles in the file, Max # of STOPs\n' % common_trip_count
        output_roster.write(s)
        s = "        #   usec   dsec   stime vehcls vehtype ioc #ONode #IntDe info ribf    " \
            "comp   izone Evac InitPos    VoT  tFlag pArrTime TP IniGas\n"
        output_roster.write(s)
        with open(temp_file, mode='r', buffering=10_000_000) as temp_roster:
            for line in temp_roster:
                line = line.strip() + next(temp_roster)
                trip_count += 1
                if trip_count % 10_000 == 0:
                    sys.stdout.write("\rNumber of Vehicles Read in Temp Roster = {:,d}".format(trip_count))

                trip = TripFileRecord()
                trip.from_string(line.split())
                output_roster.write(str(trip))
                if flat_trip_file:
                    values = tuple(trip.values)
                    record = trip_fmt_str_flat.format(*values)
                    writer.writerow(record.split(','))
    sys.stdout.write('\n')
    print("Number of Vehicles Written = {:,d}".format(trip_count))

    if f:
        f.close()


if __name__ == '__main__':
    import os
    project_directory = r'C:\Projects\SWIFT\SWIFT_Workspace\Scenarios\Scenario_S4\STM\STM_A\01_DynusT\03_Model'
    vehicle_roster_1 = os.path.join(project_directory, 'vehicle_2045_deliv.dat')
    vehicle_roster_2 = os.path.join(project_directory, 'vehicle.dat')

    output_vehicle_roster = os.path.join(project_directory, 'vehicle_common.dat')
    output_flat_roster = os.path.join(project_directory, 'vehicle_common.csv')

    compare_trips(vehicle_roster_1, vehicle_roster_2, output_vehicle_roster, output_flat_roster)

