"""

Test sorting trips

"""

import random
import timeit
import time
from internals.sorted_collection import SortedCollection
import sys
from services.file_service import TripFileRecord
import struct
import os
import itertools


class Trip:

    __slots__ = ('values',)

    fmt_binary = "=iiifiiiiiiffiiffififif"
    fmt_string = "{:>9d}{:>7d}{:>7d}{:>8.1f}{:>6d}{:>6d}{:>6d}{:>6d}{:>6d}{:>6d}{:>8.4f}{:>8.4f}{:>6d}" \
                 "{:>6d}{:>12.8f}{:>8.2f}{:>5d}{:>7.1f}{:>5d}{:>5.1f}\n{:>12d}{:>7.2f}\n"

    def __init__(self):
        self.values = [0 for _ in range(len(Trip.fmt_binary)-1)]

    def update(self, vals):
        for i, v in enumerate(vals):
            self.values[i] = v

    def from_bytes(self, values):
        self.update(struct.unpack(self.fmt_binary, values))

    def to_bytes(self):
        return struct.pack(self.fmt_binary, *self.values)

    def __str__(self):
        return self.fmt_string.format(*self.values)

    @property
    def vehid(self):
        return self.values[0]

    @vehid.setter
    def vehid(self, v):
        self.values[0] = v

    @property
    def stime(self):
        return self.values[3]


class Trip2:

    fmt_binary = "=iiifiiiiiiffiiffififif"
    fmt_string = "{:>9d}{:>7d}{:>7d}{:>8.1f}{:>6d}{:>6d}{:>6d}{:>6d}{:>6d}{:>6d}{:>8.4f}{:>8.4f}{:>6d}" \
                 "{:>6d}{:>12.8f}{:>8.2f}{:>5d}{:>7.1f}{:>5d}{:>5.1f}\n{:>12d}{:>7.2f}\n"

    def __init__(self):
        self.values = [0 for _ in range(len(Trip.fmt_binary)-1)]

    def update(self, vals):
        for i, v in enumerate(vals):
            self.values[i] = v

    def from_bytes(self, values):
        self.update(struct.unpack(self.fmt_binary, values))

    def to_bytes(self):
        return struct.pack(self.fmt_binary, *self.values)


# print(sys.getsizeof(Trip()), sys.getsizeof(Trip2()))

SEED = 47
random.seed(SEED)

# sizes = [100, 1000, 1_000_000, 10_000_000, 30_000_000]
sizes = [100, 1000, 1_000_000, 10_000_000]
# times = [0] * len(sizes)

output_trip_file = r'D:\Work\Vehicle_mid.bin'

size = 10_000_000
# with open(output_trip_file, mode='wb') as output_vehicle:
#
#     stimes = [random.uniform(0, 24) for _ in range(size)]
#     trips = [TripFileRecord() for i, t in zip(range(size), stimes)]
#     start_time = time.time()
#     # trips = sorted(trips, key=lambda trip: trip.stime)
#     trips.sort(key=lambda t: t.stime)
#     execution_time = time.time() - start_time
#     print('{:10d} trips run time = {:.0f} seconds'.format(len(trips), execution_time))
#     for trip in trips:
#         output_vehicle.write(trip.to_bytes())

# start_time = time.time()
# trip_file = []
# with open(output_trip_file, mode='rb') as input_vehicle:
#     trip_count = 0
#     eof = False
#     while not eof:
#         data = input_vehicle.read(struct.calcsize(TripFileRecord.fmt_binary))
#         if not data:
#             eof = True
#         else:
#             trip_count += 1
#             trip = Trip()
#             trip.from_bytes(data)
#             trip_file.append(trip)
#             if trip_count % 10_000 == 0:
#                 sys.stdout.write("\rNumber of Vehicles Read = {:,d}".format(trip_count))
# sort_start = time.time()
# trip_file.sort(key=lambda t: t.stime)
# sort_time = time.time() - sort_start
# print('Sorting run time = {:.0f} seconds'.format(sort_time))
# execution_time = time.time() - start_time
# print('{:10d} trips run time = {:.0f} seconds'.format(len(trip_file), execution_time))

# Sorting run time = 4 seconds, 10000000 trips run time = 81 seconds


# Test reading in all binary trip files and build indices based on (stime, pos)

def build_start_time_index(trips):
    """

    :param trips: a bytearray for all trips
    :return: a list of tuple (start_time, pos) in ascending order
    """
    stime_index = []
    read_size = struct.calcsize(Trip.fmt_binary)
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
    read_size = struct.calcsize(Trip.fmt_binary)
    with open(outfile, mode='w', buffering=10_000_000) as output_vehicle:
        s = '%12d           1    # of vehicles in the file, Max # of STOPs\n' % len(stime_index)
        output_vehicle.write(s)
        s = "        #   usec   dsec   stime vehcls vehtype ioc #ONode #IntDe info ribf    " \
            "comp   izone Evac InitPos    VoT  tFlag pArrTime TP IniGas\n"
        output_vehicle.write(s)
        for i, trip_index in enumerate(stime_index):
            t = Trip()
            t.from_bytes(all_trips[trip_index[1]:trip_index[1]+read_size])
            t.vehid = i + 1   # rename
            output_vehicle.write(str(t))
            sys.stdout.write("\rWriting Vehicle Roster = {:,d} Trips".format(i+1))


TRIP_FILE_DIR = r'C:\Projects\SWIFT\SWIFT_Workspace\Scenarios\Scenario_S4_Full\STM\STM_A\01_DynusT\02_Demand'
# trip_files = ('Vehicles_OTHER_AM.bin', 'Vehicles_OTHER_MD.bin')
# purposes = ('HBW', 'HBNW', 'NHO', 'NHW', 'OTHER')
purposes = ('OTHER',)
# purposes = ('HBNW', 'OTHER')
periods = ('AM',)

trip_files = ['_'.join(('Vehicles', purpose, period))+'.bin' for purpose, period in itertools.product(purposes, periods)]
output_trip_file = os.path.join(TRIP_FILE_DIR, 'Vehicle_by_index.dat')

start_time = time.time()
all_trips = bytearray()
for trip_file in trip_files:
    trip_file = os.path.join(TRIP_FILE_DIR, trip_file)
    with open(trip_file, mode='rb') as input_trip:
        all_trips.extend(input_trip.read())

print('All trips size = {:,.0f} MB'.format(sys.getsizeof(all_trips)/1048576.0))
sindex = build_start_time_index(all_trips)
write_trip_file(sindex, all_trips, output_trip_file)
execution_time = time.time() - start_time
print('{:10d} trips run time = {:.0f} seconds'.format(len(sindex), execution_time))

