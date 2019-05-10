"""

Analyze converted trajectories (b03 file)


"""


import struct
import sys
import csv
import os

fmt3 = '<lBBBxHHHxxLLffffqHxxxxxx'
fsize3 = struct.calcsize(fmt3)

FLAT_TRAJECTORY_HEADER = [f.strip() for f in
  "vid, tag, uclass, vtyp, origz, destz, nodes, node0, node1, start, end, delay, dist, totveh, purpose".split(',')]


def process(trajectory_file, flat_trajectory_file):
    base_vmt = []
    base_vid = []

    with open(trajectory_file, mode='rb') as input_trajectory, \
            open(flat_trajectory_file, mode='w', newline='', buffering=10_000_000) as output_trajectory:

        writer = csv.writer(output_trajectory)
        writer.writerow(FLAT_TRAJECTORY_HEADER)

        # read first record
        data = input_trajectory.read(fsize3)
        fields = struct.unpack(fmt3, data)
        expected_vehicles = fields[13]
        vehicles_read, total_exits, total_incomplete = 0, 0, 0

        for i in range(expected_vehicles):

            data = input_trajectory.read(fsize3)
            fields = struct.unpack(fmt3, data)
            tag = fields[1]
            vehicles_read += 1

            if tag == 1:
                total_incomplete += 1
            else:
                total_exits += 1
            writer.writerow(fields)
            if vehicles_read % 10000 == 0 or vehicles_read == expected_vehicles:
                sys.stdout.write("\rNumber of Vehicles Written = {:,d} ({:.0f} %)".format(
                    total_exits, total_exits * 100.0 / expected_vehicles))

        sys.stdout.write("\n")
        print("Total Vehicles Read       = {:,d}".format(vehicles_read))
        print("Total Vehicles Exited     = {:,d}".format(total_exits))
        print("Total Vehicles Incomplete = {:,d}".format(total_incomplete))


if __name__ == "__main__":
    execution_dir = r'C:\Projects\SWIFT\SWIFT_Workspace\Scenarios\Scenario_S0\STM\STM_A\01_DynusT\03_Model'
    input_trajectory_file = os.path.join(execution_dir, 'VehTrajectory.b03')
    output_trajectory_file = os.path.join(execution_dir, 'Vehicle_Skim.csv')
    process(input_trajectory_file, output_trajectory_file)
