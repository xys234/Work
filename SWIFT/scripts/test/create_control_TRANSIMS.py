import os
import h5py


def parse_matrix_table(matrix_name, vots):
    """
    Parse the matrix name "amnhoai45" for vehicle type, value of time, period, and purpose
    :param matrix_name:
    :type str
    :param vots:        a dict for vots
    :return: a tuple, vehicle_type, occupancy, purpose, value_of_time, period
    """

    matrix_name = matrix_name.lower()

    vtype = occ = purp = vot = 0
    time_period = (0, 0)
    period = ''

    if matrix_name.find("all") >= 0:
        return dict(vtype=None, occ=None, purp=None, vot=None, time_period=None, period=None)

    # VEHICLE_TYPE_CODE_1
    if matrix_name.find("da") >= 0:
        vtype = 1
    elif matrix_name.find("s2") >= 0 or matrix_name.find("a2") >= 0:
        vtype = 2
    elif matrix_name.find("s3") >= 0 or matrix_name.find("a3") >= 0:
        vtype = 3
    elif matrix_name.find("cargo") >= 0:
        vtype = 5   # HEAVYTRUCK
    elif matrix_name.find("serv") >= 0:
        vtype = 4   # MEDIUM TRUCK
    elif matrix_name.find("taxi") >= 0:
        vtype = 2   # HOV2
    elif matrix_name.find("exta") >= 0:
        vtype = 1

    # TRAVEL_MODE_CODE_1
    if vtype == 1 or vtype == 4 or vtype == 5:
        occ = 'DRIVE'
    elif vtype == 2:
        occ = 'HOV2'
    elif vtype == 3:
        occ = 'HOV3'

    if matrix_name.find("hbw") >= 0:
        purp = 1
    elif matrix_name.find("hnw") >= 0:
        purp = 2
    elif matrix_name.find("nhw") >= 0:
        purp = 3
    elif matrix_name.find("nho") >= 0:
        purp = 4
    else:
        purp = 5


    if matrix_name.find("am") >= 0:
        period = 'am'
        time_period = '6:00..9:00'
    elif matrix_name.find("md") >= 0:
        period = 'md'
        time_period = '9:00..15:00'
    elif matrix_name.find("pm") >= 0:
        period = 'pm'
        time_period = '15:00..19:00'
    else:
        period = 'ov'
        time_period = '0:00..6:00, 19:00..24:00'

    for key in vots.keys():
        if matrix_name.find(key) >= 0:
            vot = vots[key]
            break

    return dict(vtype=vtype, occ=occ, purp=purp, vot=vot, time_period=time_period, period=period)


if __name__ == '__main__':

    control_file_folder = r'Q:\TRANSIMS\ConvertTrips_Controls'

    matrix_folder = r'C:\Projects\SWIFT\SWIFT_Project_Data\Inputs\OD\2017'
    matrices_am = ["OD AM3HR HBNW Vehicles", "OD AM3HR HBW Vehicles", "OD AM3HR NHB Vehicles", "OD AM3HR Other VEHICLEs"]
    matrices_md = ["OD MD6HR HBNW Vehicles", "OD MD6HR HBW Vehicles", "OD MD6HR NHB Vehicles", "OD MD6HR Other VEHICLEs"]
    matrices_pm = ["OD PM4HR HBNW Vehicles", "OD PM4HR HBW Vehicles", "OD PM4HR NHB Vehicles", "OD PM4HR Other VEHICLEs"]
    matrices_ov = ["OD OV8HR HBNW Vehicles", "OD OV8HR HBW Vehicles", "OD OV8HR NHB Vehicles", "OD OV8HR Other VEHICLEs"]
    matrices = matrices_am + matrices_md + matrices_pm + matrices_ov

    purps = ["hnw", "hbw", "nho", "nhw"]
    periods = ["am", "md", "pm", "ov"]

    # right open; day starts at 0
    period_def = {'am': [(6, 9)], 'md': [(9,15)], 'pm': [(15,19)], 'ov': [(0, 6), (19, 24)]}

    vots = {"hbwi1da": 2, "hbwi2da": 5, "hbwi3da": 8, "hbwi4da": 12, "hbwi5da": 16, "hbwi12a2": 9,
            "hbwai3a2": 15, "hbwi45a2": 20, "hbwi12a3": 13, "hbwi3a3": 19, "hbwi45a3": 23,
            "hnwi12da": 1, "hnwi3da": 4, "hnwi45da": 11, "hnwi12a2": 3, "hnwai3a2": 10,
            "hnwi45a2": 18,"hnwi12a3": 6, "hnwi3a3": 14, "hnwi45a3": 21,
            "nhodai12": 1, "nhodai3": 4, "nhodai453": 11, "nhos2i12": 3, "nhos2i3": 10,
            "nhos2i45": 18, "nhos3i12": 6, "nhos3i3": 14, "nhos3i45": 21,
            "nhwdai1": 2, "nhwdai2": 5, "nhwdai3": 8, "nhwdai4": 12, "nhwdai5": 16, "nhws2i12": 9,
            "nhws2i3": 15, "nhws2i45": 20, "nhws3i12": 13, "nhws3i3": 19, "nhws3i45": 23,
            "Cargo": 22, "Serv": 17, "taxi": 7, "exta": 7}
    diurnal_file = r'Inputs\Interpolated_Diurnal_TRANSIMS.csv'

    PURP_MAP = {
        1: 'HBW',
        2: 'HNW',
        3: 'NHW',
        4: 'NHO',
        5: 'OTHER'
    }

    rotation_keys = {
        'TRIP_TABLE_FILE': None,
        'TRIP_TABLE_FORMAT': 'CUBE',
        'TRIP_TABLE_NAME': None,
        'TRIP_SCALING_FACTOR': '1.0',
        'TIME_DISTRIBUTION_FILE': diurnal_file,
        'TIME_DISTRIBUTION_FORMAT': 'COMMA_DELIMITED',
        'TIME_DISTRIBUTION_FIELD': 'REGION',
        'TIME_DISTRIBUTION_TYPE': 'TRIP_START',
        'TIME_PERIOD_RANGE': None,
        'TIME_SCHEDULE_CONSTRAINT': 'START',
        'TRAVELER_TYPE_CODE': None,
        'TRIP_PURPOSE_CODE': None,
        'TRAVEL_MODE_CODE': None,
        'TRIP_PRIORITY_CODE': 'HIGH',
        'RETURN_TRIP_FLAG': 'FALSE',
    }

    # input matrix folder
    input_matrix_folder = "L:\\DCS\\Projects\\_Legacy\\60563434_SWIFT\\400_Technical\\410 Transportation Modeling\\MODEL_RUNS\\STM-D_SWIFT\\Base\\SWIFT_2045_Scen_S4\\Temp_WorkDir\\TEMP_S4minusBase_min1round0"

    # period-purpose map to last key-group
    control_file_map = {}
    matrix_count = 0
    for m in matrices:
        key_group = 0
        matrix_file = os.path.join(matrix_folder, m + '.omx')
        matrix_file_out = "@MATRIX_FOLDER@\\DIFF " + m + ".MAT"
        value_trip_table_file = matrix_file_out

        start_index = 2
        if m.upper().find("OTHER") >= 0:
            start_index = 3

        h5 = h5py.File(matrix_file, 'r')
        tables = h5['/matrices/'].keys()

        purp = vot = occ = vtype = 0
        for t in tables:
            if t.find('all') > 0:
                continue
            matrix_count += 1

            info = parse_matrix_table(t, vots)
            vtype = info['vtype']
            occ = info['occ']
            purp = info['purp']
            vot = info['vot']
            time_period = info['time_period']
            period = info['period']

            mode = 'w'
            control_file_suffix = PURP_MAP[purp].upper() + '_' + period.upper()
            control_file = os.path.join(control_file_folder,
                                        "ConvertTrips_" + control_file_suffix + ".ctl")
            if control_file_suffix in control_file_map:
                control_file_map[control_file_suffix] += 1
                mode = 'a'
            else:
                control_file_map[control_file_suffix] = 1

            key_group = control_file_map[control_file_suffix]

            with open(control_file, mode=mode) as f:
                key_names = [k+'_'+str(key_group) for k in rotation_keys]

                if key_group == 1:
                    f.write('{0:40s}{1:s}\n'.format("CONTROL_KEY_FILE", "General_Keys.ctl"))
                    f.write('{0:40s}{1:s}\n'.format("CONTROL_KEY_FILE", "Network_Keys.ctl"))

                    f.write("\n")
                    f.write('{0:40s}{1:s}\n'.format("@MATRIX_FOLDER@", input_matrix_folder))

                    f.write("\n")

                    f.write('{0:40s}{1:s}\n'.format("NEW_TRIP_FILE", "Demand\\{0:s}".format('Trips_'+PURP_MAP[purp]+'_'+period.upper()+'.csv')))
                    f.write('{0:40s}{1:s}\n'.format("NEW_TRIP_FORMAT", "COMMA_DELIMITED"))
                    f.write('{0:40s}{1:s}\n'.format("NOTES_AND_NAME_FIELDS", "TRUE"))
                    f.write('{0:40s}{1:s}\n'.format("OD_OUTPUT_TYPE", "NODE"))
                    f.write('\n')

                for name, val in rotation_keys.items():
                    if val is None:

                        if name == 'TRIP_TABLE_FILE':
                            val = value_trip_table_file
                        elif name == 'TRIP_TABLE_NAME':
                            val = t[start_index:]
                        elif name == 'TIME_PERIOD_RANGE':
                            val = time_period
                        elif name == 'TRAVELER_TYPE_CODE':
                            val = vot
                        elif name == 'TRIP_PURPOSE_CODE':
                            val = purp
                        elif name == 'TRAVEL_MODE_CODE':
                            val = occ
                        f.write('{0:40s}{1:s}\n'.format(name+'_'+str(key_group), str(val)))
                        val = None
                    else:
                        f.write('{0:40s}{1:s}\n'.format(name+'_'+str(key_group), str(val)))
                f.write('\n')

    print("Processed {0:d} matrices".format(matrix_count))
