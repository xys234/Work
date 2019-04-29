import h5py
import os


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

    if matrix_name.find("da") >= 0:
        vtype = 1
    elif matrix_name.find("s2") >= 0 or matrix_name.find("a2") >= 0:
        vtype = 2
    elif matrix_name.find("s3") >= 0 or matrix_name.find("a3") >= 0:
        vtype = 3
    elif matrix_name.find("cargo") >= 0:
        vtype = 6
    elif matrix_name.find("serv") >= 0:
        vtype = 5
    elif matrix_name.find("taxi") >= 0:
        vtype = 4
    elif matrix_name.find("exta") >= 0:
        vtype = 1

    if vtype == 1:
        occ = 0
    elif vtype == 2 or vtype == 3 or vtype == 4:
        occ = 2
    elif vtype == 5 or vtype == 6:
        occ = 1

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
        time_period = '6..9'
    elif matrix_name.find("md") >= 0:
        period = 'md'
        time_period = '9..15'
    elif matrix_name.find("pm") >= 0:
        period = 'pm'
        time_period = '15..19'
    else:
        period = 'ov'
        time_period = '0..6, 19..24'

    for key in vots.keys():
        if matrix_name.find(key) >= 0:
            vot = vots[key]
            break

    return dict(vtype=vtype, occ=occ, purp=purp, vot=vot, time_period=time_period, period=period)


if __name__ == '__main__':

    rotation_keys = (
        'TRIP_TABLE_FILE',
        'MATRIX_NAME',
        'TIME_PERIOD_RANGE',
        'DIURNAL_FILE',
        'TRIP_PURPOSE_CODE',
        'VALUE_OF_TIME',
        'VEHICLE_OCCUPANCY',
        'VEHICLE_TYPE',
    )

    control_file_folder = r'C:\Projects\SWIFT\SWIFT_Project_Data\Controls'

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

    vots = {"hbwi1da": 9.6, "hbwi2da": 15.04, "hbwi3da": 20.48, "hbwi4da": 27.52, "hbwi5da": 37.12, "hbwi12a2": 21.56,
            "hbwai3a2": 35.84, "hbwi45a2": 56.56, "hbwi12a3": 30.8, "hbwi3a3": 51.2, "hbwi45a3": 80.8,
            "hnwi12da": 7.03, "hnwi3da": 13.44, "hnwi45da": 23.65, "hnwi12a2": 12.3, "hnwai3a2": 23.52,
            "hnwi45a2": 41.39,"hnwi12a3": 17.57, "hnwi3a3": 33.6, "hnwi45a3": 59.12,
            "nhodai12": 7.03, "nhodai3": 13.44, "nhodai453": 23.65, "nhos2i12": 12.3, "nhos2i3": 23.52,
            "nhos2i45": 41.39, "nhos3i12": 17.57, "nhos3i3": 33.6, "nhos3i45": 59.12,
            "nhwdai1": 9.6, "nhwdai2": 15.04, "nhwdai3": 20.48, "nhwdai4": 27.52, "nhwdai5": 37.12, "nhws2i12": 21.56,
            "nhws2i3": 35.84, "nhws2i45": 56.56, "nhws3i12": 30.8, "nhws3i3": 51.2, "nhws3i45": 80.8,
            "Cargo": 64.0, "Serv": 40.0, "taxi": 18.94, "exta": 18.94}
    diurnal_file = r"..\..\CommonData\STM\STM_A\Shared_Inputs\Diurnal_Full.csv"

    PURP_MAP = {
        1: 'HBW',
        2: 'HNW',
        3: 'NHW',
        4: 'NHO',
        5: 'OTHER'
    }

    # period-purpose map to last key-group
    control_file_map = {}
    matrix_count = 0
    for m in matrices:
        key_group = 0
        matrix_file = os.path.join(matrix_folder, m + '.omx')
        matrix_file_out = os.path.join(r'%SCEN_DIR%\STM\STM_D', m + '.omx')
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
                    f.write('{0:40s}{1:s}\n'.format('TITLE', 'Convert_Vehicle_Roster_%PURPOSE%'))
                    f.write('{0:40s}{1:s}\n'.format('PROJECT_DIRECTORY', '%SCEN_DIR%'))
                    f.write('{0:40s}{1:s}\n'.format('REPORT_FILE', r'%SCEN_DIR%\STM\STM_A\01_DynusT\01_Controls\Convert_Vehicle_Roster_%PURPOSE%.prn'))
                    f.write('{0:40s}{1:s}\n'.format('NUMBER_OF_ZONES', '5263'))
                    f.write('{0:40s}{1:s}\n'.format('ORIGIN_FILE', r'%SCEN_DIR%\STM\STM_A\01_DynusT\03_Model\origin.dat'))
                    f.write('{0:40s}{1:s}\n'.format('NEW_VEHICLE_ROSTER_FILE', r'%SCEN_DIR%\STM\STM_A\01_DynusT\02_Demand\Vehicles_%PURPOSE%.dat'))
                    f.write('\n')

                f.write('{0:40s}{1:s}\n'.format(key_names[0], matrix_file_out))
                f.write('{0:40s}{1:s}\n'.format(key_names[1], t))
                f.write('{0:40s}{1:s}\n'.format(key_names[2], time_period))
                f.write('{0:40s}{1:s}\n'.format(key_names[3], diurnal_file))
                f.write('{0:40s}{1:d}\n'.format(key_names[4], purp))
                f.write('{0:40s}{1:.2f}\n'.format(key_names[5], vot))
                f.write('{0:40s}{1:d}\n'.format(key_names[6], occ))
                f.write('{0:40s}{1:d}\n'.format(key_names[7], vtype))
                f.write('\n')

    print("Processed {0:d} matrices".format(matrix_count))