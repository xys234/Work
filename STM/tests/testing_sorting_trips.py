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

start_time = time.time()
trip_file = []
with open(output_trip_file, mode='rb') as input_vehicle:
    trip_count = 0
    eof = False
    while not eof:
        data = input_vehicle.read(struct.calcsize(TripFileRecord.fmt_binary))
        if not data:
            eof = True
        else:
            trip_count += 1
            trip = Trip()
            trip.from_bytes(data)
            trip_file.append(trip)
            if trip_count % 10_000 == 0:
                sys.stdout.write("\rNumber of Vehicles Read = {:,d}".format(trip_count))
sort_start = time.time()
trip_file.sort(key=lambda t: t.stime)
sort_time = time.time() - sort_start
print('Sorting run time = {:.0f} seconds'.format(sort_time))
execution_time = time.time() - start_time
print('{:10d} trips run time = {:.0f} seconds'.format(len(trip_file), execution_time))

# Sorting run time = 4 seconds, 10000000 trips run time = 81 seconds

# for size in sizes:
#     stimes = [random.uniform(0, 24) for _ in range(size)]
#     trips = SortedCollection(key=lambda trip: trip.stime)
#     start_time = time.time()
#     for i, t in zip(range(size), stimes):
#         sys.stdout.write("\rNumber of Trips Sorted = {:,d} ({:.2f} %)".format(i+1, (i+1)*100.0/size))
#         trips.insert(Trip(i, t))
#     execution_time = time.time() - start_time
#     print('{:10d} trips run time = {:.0f} seconds'.format(len(trips), execution_time))
