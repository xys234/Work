
import os
import csv

def tabularize_vehicle_roster(vehicle_file, tabular_vehicle_file, with_header=True):
    VEHICLE_FILE_HEADER = '''vid usec dsec stime vehcls vehtype 
                          ioc #ONode #IntDe info ribf comp Izone Evac InitPos VoT tFlag pArrTime TP IniGas 
                          DZone waitTime'''

    select_ids = (10, 26, 205)
    selection_size = len(select_ids)

    with open(vehicle_file, mode='r') as input:
        if with_header:
            next(input)
            next(input)
        with open(tabular_vehicle_file, mode='w', newline='', buffering=10_000_000) as output:
            writer = csv.writer(output)
            writer.writerow(VEHICLE_FILE_HEADER.split())
            number_written = 0
            for i, line in enumerate(input):
                if i > 0 and i % 50_000 == 0:
                    print('Processed %d lines' % i)
                data = line + next(input)
                vid = int(data.split()[0])
                if vid in select_ids:
                    writer.writerow(data.split())
                    number_written += 1
                if selection_size == number_written:
                    break


if __name__ == '__main__':
    roster_folder = r'C:\Projects\SWIFT\SWIFT_Workspace\Scenarios\Scenario_S0\STM\STM_A\01_DynusT\03_Model'
    dynust_folder = r'C:\Projects\SWIFT\SWIFT_Project_Data\Outputs'
    roster_file_path = os.path.join(roster_folder, 'Vehicle.dat')
    tabular_vehicle_file_path = os.path.join(dynust_folder, 'Vehicles_tabularized.csv')
    tabularize_vehicle_roster(roster_file_path, tabular_vehicle_file_path, with_header=True)