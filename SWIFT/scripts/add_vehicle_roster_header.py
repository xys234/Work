import os, time


def add_vehicle_roster_header(input_vehicle_file, output_vehicle_file, vehicle_count):


    with open(output_vehicle_file, mode='w', buffering=10_000_000) as output:
        s = '%12d           1    # of vehicles in the file, Max # of STOPs\n' % (vehicle_count)
        output.write(s)

        s = "        #   usec   dsec   stime vehcls vehtype ioc #ONode #IntDe info ribf    comp   izone Evac InitPos    VoT  tFlag pArrTime TP IniGas\n"
        output.write(s)
        with open(input_vehicle_file, mode='r') as input:
            for line in input:
                output.write(line)






if __name__ == '__main__':

    data_dir = r'C:\Projects\Repo\Work\SWIFT\data\Dynus_T'
    input_vehicle_roster = 'Vehicles_HNW_AM.dat'
    output_vehicle_roster = 'Vehicles_HNW_AM_with_Header.dat'
    input_vehicle_roster = os.path.join(data_dir, input_vehicle_roster)
    output_vehicle_roster = os.path.join(data_dir, output_vehicle_roster)

    start_time = time.time()
    add_vehicle_roster_header(input_vehicle_roster, output_vehicle_roster, 1583688)
    end_time = time.time()
    print("Execution time = {0:.2f} minutes".format((end_time-start_time)/60.0))