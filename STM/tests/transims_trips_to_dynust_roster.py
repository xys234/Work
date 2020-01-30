
import csv
import random
import sys
import time

from services.file_service import TripFileRecord


random.seed(73)


class TimeStamp:
    def __init__(self, s):
        self.hour = 0
        self.minute = 0
        self.second = 0

        self.from_string(s)

    def from_string(self, s):
        parts = [int(p) for p in s.split(':')]
        if len(parts) == 3:
            self.hour, self.minute, self.second = parts
        else:
            self.hour, self.minute = parts
            self.second = 0

    def to_minutes(self):
        return self.hour*60.0 + self.minute + self.second / 60.0


def read_trips(tripfile):

    usec = '9'
    dsec = '1'
    vehcls = '3'
    vehtype = '1'
    ioc = '0'
    onode = '1'
    intde = '1'
    info = '0'
    ribf = '1'
    comp = '1'
    izone = '1'
    evac = '0'
    initpos = '0'
    vot = '10'
    tflag = '1'
    parrtime = '1.0'
    tp = '1'
    initgas = '0'
    dest = '2'
    waittime = '0'

    trips = []

    with open(tripfile, mode='r') as f:
        fieldnames = next(f).split(',')
        reader = csv.DictReader(f, fieldnames=fieldnames)

        veh_count = 0
        for record in reader:
            veh_count += 1
            vid = str(record['HHOLD'])
            dt = str(TimeStamp(record['START']).to_minutes())
            initpos = str(random.random())
            s = (vid, usec, dsec, dt, vehcls, vehtype, ioc, onode, intde, info, ribf, comp, izone, evac, initpos, vot, tflag, parrtime, tp, initgas, dest, waittime)
            trip = TripFileRecord()
            trip.from_string(s)
            sys.stdout.write("\rNumber of TRANSIMS Trips Read = {:,d}".format(veh_count))
            trips.append(trip)
    sys.stdout.write("\n")
    trips.sort(key=lambda t: t.stime)
    return trips


def write_vehicles(trips, vehicle_roster_file):

    with open(vehicle_roster_file, mode='w', buffering=10_000_000) as output_veh:

        s = '%12d           1    # of vehicles in the file, Max # of STOPs\n' % (len(trips))
        output_veh.write(s)
        s = "        #   usec   dsec   stime vehcls vehtype ioc #ONode #IntDe info ribf    comp   " + \
            "izone Evac InitPos    VoT  tFlag pArrTime TP IniGas\n"
        output_veh.write(s)

        for trip in trips:
            output_veh.write(str(trip))

    sys.stdout.write("Total vehicles converted                    = {0:,d}".format(len(trips)))


if __name__ == '__main__':
    time.perf_counter()
    trip_file = r'I:\MNCPPC_TRANSIMS\TransForM_2.5_wBaseYear2015\TRANSIMS\2015\Tube\Demand\Factor2_Trips.csv'
    vehicle_roster_file = r'C:\Projects\TRANSIMS\Simulation\vehicle.dat'

    trips = read_trips(trip_file)
    write_vehicles(trips, vehicle_roster_file)
    time.perf_counter()
