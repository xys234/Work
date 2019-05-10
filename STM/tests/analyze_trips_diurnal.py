from services.file_service import TripFileRecord
import os
import sys
import struct
import itertools
import time


def summarize_diurnal_distribution(text_vehicle_roster, output_diurnal_file):
    """
    Read text trip rosters and create a diurnal summary
    :param
    diurnal_bins are a list of tuples
    :return:
    """

    summary = {}
    with open(text_vehicle_roster, mode='r', buffering=20_000_000) as input_roster:
        expected_number_of_trips = trip_count = 0
        for i, line in enumerate(input_roster):
            if i == 0:
                expected_number_of_trips = int(line.strip().split()[0])
            if i > 1:
                line = line.strip() + next(input_roster)
                trip_count += 1
                if trip_count % 10_000 == 0 or trip_count == expected_number_of_trips:
                    sys.stdout.write("\rNumber of Vehicles Read = {:,d} ({:.2f} %)".format(
                        trip_count, trip_count * 100.0 / expected_number_of_trips))
                bin_index = int(float(line.split()[3])*10)
                if bin_index in summary:
                    summary[bin_index] += 1
                else:
                    summary[bin_index] = 1

        sys.stdout.write('\n')

    with open(output_diurnal_file, mode='w', buffering=20_000_000) as output_diurnal:
        output_diurnal.write('Start,Trips\n')
        for s, trip in summary.items():
            output_diurnal.write('{:.1f}, {:d}\n'.format(s/10.0, trip))


def get_diurnal_bins(diurnal_file):
    """

    :param diurnal_file: a csv file for diurnal distribution between 0 and 24
    :return: a list of tuples

    """

    hours, probs = [], []
    with open(diurnal_file, mode='r') as f:
        next(f)
        for line in f:
            hour, prob = line.strip().split(',')
            hours.append(float(hour.strip()))
            probs.append(float(prob.strip()))
    return {int(l*10): (l, u) for l, u in zip(hours[:-1], hours[1:])}


def build_start_time_index(trips):
    """

    :param trips: a bytearray for all trips
    :return: a list of tuple (start_time, pos) in ascending order
    """
    stime_index = []
    read_size = struct.calcsize(TripFileRecord.fmt_binary)
    offset = 12
    pos, trip_count = 0, 0

    while pos < len(trips):
        vid = struct.unpack("=i", trips[pos:pos+4])[0]
        stime = struct.unpack("=f", trips[pos+offset:pos+offset+4])[0]
        stime_index.append((stime, pos))
        trip_count += 1
        sys.stdout.write("\rBuilding Trip Index on Start Time = {:,d} Trips".format(trip_count))
        # sys.stdout.write("\rBuilding Trip Index on Vehicle = {:,d} Trips".format(vid))
        # print("Building Trip Index on Start Time = {:,d} Trips".format(trip_count))
        pos += read_size
    stime_index.sort(key=lambda t: t[0])
    return stime_index


def write_trip_file(stime_index, all_trips, outfile):
    read_size = struct.calcsize(TripFileRecord.fmt_binary)
    with open(outfile, mode='w', buffering=10_000_000) as output_vehicle:
        s = '%12d           1    # of vehicles in the file, Max # of STOPs\n' % len(stime_index)
        output_vehicle.write(s)
        s = "        #   usec   dsec   stime vehcls vehtype ioc #ONode #IntDe info ribf    " \
            "comp   izone Evac InitPos    VoT  tFlag pArrTime TP IniGas\n"
        output_vehicle.write(s)
        for i, trip_index in enumerate(stime_index):
            t = TripFileRecord()
            t.from_bytes(all_trips[trip_index[1]:trip_index[1]+read_size])
            t.vehid = i + 1   # rename
            output_vehicle.write(str(t))
            sys.stdout.write("\rWriting Vehicle Roster = {:,d} Trips".format(i+1))


if __name__ == '__main__':
    start_time = time.time()
    diurnal_file = r'L:\DCS\Projects\_Legacy\60563434_SWIFT\400_Technical\SWIFT_Workspace\CommonData\STM\STM_A\Shared_Inputs\Diurnal_Full.csv'
    vehicle_roster_file = r'L:\DCS\Projects\_Legacy\60563434_SWIFT\400_Technical\Houston_8_County_DTA_CalibValid\_dst\HGAC_45_fr\vehicle.dat'
    output_diurnal_file = r'C:\Projects\SWIFT_Project_Data\Outputs\HGAC_45_fr_diurnal.csv'

    diurnal_bins = get_diurnal_bins(diurnal_file)
    summarize_diurnal_distribution(vehicle_roster_file, output_diurnal_file)
    execution_time = time.time() - start_time
    print('Process complete in {:.0f} seconds'.format(execution_time))

# TRIP_FILE_DIR = r'C:\Projects\SWIFT\SWIFT_Workspace\Scenarios\Scenario_S4_Full\STM\STM_A\01_DynusT\02_Demand'
# trip_files = ('Vehicles_OTHER_AM.bin', 'Vehicles_OTHER_MD.bin')
# purposes = ('HBW', 'HBNW', 'NHO', 'NHW', 'OTHER')
# purposes = ('HBW', )
# purposes = ('OTHER',)
# purposes = ('HBNW', 'OTHER')
# periods = ('MD',)

# trip_files = ['_'.join(('Vehicles', purpose, period))+'.bin' for purpose, period in itertools.product(purposes, periods)]
# output_trip_file = os.path.join(TRIP_FILE_DIR, 'Vehicles_HBW_MD.dat')
#
# start_time = time.time()
# all_trips = bytearray()
# for trip_file in trip_files:
#     trip_file = os.path.join(TRIP_FILE_DIR, trip_file)
#     with open(trip_file, mode='rb') as input_trip:
#         all_trips.extend(input_trip.read())
#
# print('All trips size = {:,.0f} MB'.format(sys.getsizeof(all_trips)/1048576.0))
# sindex = build_start_time_index(all_trips)
# write_trip_file(sindex, all_trips, output_trip_file)
# execution_time = time.time() - start_time
# print('{:10d} trips run time = {:.0f} seconds'.format(len(sindex), execution_time))