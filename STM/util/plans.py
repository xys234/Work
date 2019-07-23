"""

A set of utilities to manipulate TRANSIMS plan file


"""


import csv
import math
import sys


class Time:

    __slots__ = ('hours', 'minutes', 'seconds')

    def __init__(self, s=None):
        self.hours, self.minutes, self.seconds = 0, 0, 0
        if s:
            self.from_string(s)

    def __str__(self):
        return self.to_string()

    def to_string(self, hours=None, minutes=None, seconds=None):
        if hours is None:
            hours = self.hours
        if minutes is None:
            minutes = self.minutes
        if seconds is None:
            seconds = self.seconds
        return ":".join([str(t).zfill(2) for t in (hours, minutes, round(seconds))])

    def from_string(self, s):
        """
        Convert a time string like h:mm:ss or hh:mm:ss to individual time components
        :param s:
        :return: Time
        """

        parts = s.split(':')
        if len(parts) == 2:
            self.hours, self.minutes = int(parts[0]), int(parts[1])
        else:
            self.hours, self.minutes, self.seconds = tuple([int(c) for c in parts])

    def __add__(self, other):
        """
        Add seconds to the simulation clock
        :param other: a scalar
        :return:
        """
        total_seconds = self.hours * 3600 + self.minutes * 60 + self.seconds + other
        self.hours = math.floor(total_seconds / 3600)

        total_seconds -= self.hours * 3600
        self.minutes = math.floor(total_seconds / 60)

        total_seconds -= self.minutes * 60
        self.seconds = total_seconds
        return self

    def to_interval(self):
        """
        round to the neatest 15 min. interval
        :return:
        """

        interval = math.floor(self.minutes / 15) * 15
        return self.to_string(minutes=interval, seconds=0)


class Skim:

    __slots__ = ('values',)

    def __init__(self, values):
        self.values = values

    @property
    def hhold(self):
        return int(self.values[0])

    @property
    def depart(self):
        return Time(self.values[19])

    @property
    def drive(self):
        return float(self.values[23])

    @property
    def length(self):
        return float(self.values[27])

    @property
    def legs(self):
        return int(self.values[-1])


class Leg:
    __slots__ = ('values',)

    def __init__(self, values):
        """
        :param values: a list of strings
        """
        self.values = values

    @property
    def mode(self):
        return self.values[0].strip()

    @property
    def type(self):
        return self.values[1].strip()

    @property
    def leg(self):
        return int(self.values[2])

    @property
    def time(self):
        return float(self.values[3])

    @property
    def length(self):
        return float(self.values[4])


def process_plans_csv(input_plans, output_trajectories):

    header = "HHOLD,LEG,LINK,TIMESTAMP,INTERVAL,TRAVEL_TIME,LENGTH,CUMULATIVE_LENGTH"

    with open(input_plans, mode='r', buffering=20_000_000) as f:
        with open(output_trajectories, mode='w', buffering=10_000_000, newline='') as r:
            writer = csv.writer(r, quoting=csv.QUOTE_NONE)
            writer.writerow(header.split(','))

            next(f)
            next(f)
            total_households, nested, legs_read, drive_legs, cumulative_distance = 0, False, 0, 0, 0

            for line in f:
                data = line.split(',')
                # hhold, depart, drive, length, legs = 0, None, 0, 0, 0
                if not nested:
                    skim = Skim(data)
                    hhold, depart, drive, length, legs = \
                        skim.hhold, skim.depart, skim.drive, skim.length, skim.legs
                    nested = True
                    total_households += 1
                    sys.stdout.write("\rProcessing HHOLD = {:d}".format(hhold))
                else:
                    legs_read += 1
                    leg = Leg(data)
                    if leg.mode == 'DRIVE' and leg.type.find('LINK') >= 0:
                        drive_legs += 1
                        depart += leg.time
                        cumulative_distance += leg.length
                        record = (str(int(hhold)),
                                  str(int(drive_legs)), str(leg.leg), str(depart), depart.to_interval(),
                                  "{:.1f}".format(leg.time), "{:.1f}".format(leg.length),
                                  "{:.1f}".format(cumulative_distance))
                        writer.writerow(record)
                if legs_read == legs:
                    nested = False
                    drive_legs = 0
                    legs_read = 0

            sys.stdout.write("\n")
            print("Total Number of Households Processed = {:d}".format(total_households))

if __name__ == '__main__':
    import os
    execution_dir = r'L:\DCS\Projects\_Legacy\60563434_SWIFT\400_Technical\SWIFT_Workspace\Scenarios\Scenario_2045_S12_Alpha\STM\STM_A\02_TrafficPredictor\03_Demand'
    # plans = os.path.join(execution_dir, 'test.csv')
    plans = os.path.join(execution_dir, 'FINAL_Plans_Link_53.csv')
    output = os.path.join(execution_dir, 'test_Legs.csv')

    process_plans_csv(plans, output)


