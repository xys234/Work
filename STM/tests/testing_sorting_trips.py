"""

Test sorting trips

"""

import random
import timeit
import time
from internals.sorted_collection import SortedCollection
import sys

class Trip:
    __slots__ = ('vid', 'stime', 'purp', 'mode', 'field2', 'field3', 'field4', 'field5', 'field6', 'field7', 'field8'
                 , 'field9', 'field10', 'field11', 'field12', 'field13', 'field14', 'field15', 'field16', 'field17',
                 'field18', 'field19', 'field20')

    def __init__(self, vid, stime):
        self.vid = vid
        self.stime = stime
        self.purp = 1
        self.mode = 1
        self.field2 = 1
        self.field3 = 1
        self.field4 = 1
        self.field5 = 1
        self.field6 = 1
        self.field7 = 1
        self.field8 = 1
        self.field9 = 1
        self.field10 = 1
        self.field11 = 1
        self.field12 = 1
        self.field13 = 1
        self.field14 = 1
        self.field15 = 1
        self.field16 = 1
        self.field17 = 1
        self.field18 = 1
        self.field19 = 1
        self.field20 = 1


SEED = 47
random.seed(SEED)

# sizes = [100, 1000, 1_000_000, 10_000_000, 30_000_000]
sizes = [100, 1000, 1_000_000, 10_000_000]
# times = [0] * len(sizes)

for size in sizes:
    stimes = [random.uniform(0, 24) for _ in range(size)]
    trips = [Trip(i, t) for i, t in zip(range(size), stimes)]
    start_time = time.time()
    # trips = sorted(trips, key=lambda trip: trip.stime)
    trips.sort(key=lambda trip: trip.stime)
    execution_time = time.time() - start_time
    print('{:10d} trips run time = {:.0f} seconds'.format(len(trips), execution_time))

# for size in sizes:
#     stimes = [random.uniform(0, 24) for _ in range(size)]
#     trips = SortedCollection(key=lambda trip: trip.stime)
#     start_time = time.time()
#     for i, t in zip(range(size), stimes):
#         sys.stdout.write("\rNumber of Trips Sorted = {:,d} ({:.2f} %)".format(i+1, (i+1)*100.0/size))
#         trips.insert(Trip(i, t))
#     execution_time = time.time() - start_time
#     print('{:10d} trips run time = {:.0f} seconds'.format(len(trips), execution_time))