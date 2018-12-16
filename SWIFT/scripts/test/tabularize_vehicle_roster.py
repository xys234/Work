
import os
import csv

def tabularize_vehicle_roster(vehicle_file, tabular_vehicle_file, with_header=True):
    VEHICLE_FILE_HEADER = '''vid usec dsec stime vehcls vehtype 
                          ioc #ONode #IntDe info ribf comp Izone Evac InitPos VoT tFlag pArrTime TP IniGas 
                          DZone waitTime'''

    with open(vehicle_file, mode='r') as input:
        if with_header:
            next(input)
            next(input)
        with open(tabular_vehicle_file, mode='w', newline='', buffering=10_000_000) as output:
            writer = csv.writer(output)
            writer.writerow(VEHICLE_FILE_HEADER.split())
            for i, line in enumerate(input):
                if i > 0 and i % 50_000 == 0:
                    print('Processed %d lines' % i)
                data = line + next(input)
                writer.writerow(data.split())



if __name__=='__main__':
    dynust_folder = '..\data\Dynus_T'
    vehicle_file_path = os.path.join(dynust_folder, 'vehicles_deliv_17.dat')
    tabular_vehicle_file_path = os.path.join(dynust_folder, 'vehicles_deliv_17.csv')
    tabularize_vehicle_roster(vehicle_file_path, tabular_vehicle_file_path, with_header=True)