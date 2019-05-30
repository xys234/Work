import h5py
import os


def parse_matrix_table(matrix_file_name, matrix_name, vots):
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

    cav, ev = False, False

    if matrix_name.lower().find("da") >= 0:
        if matrix_name.lower().find("cav") >= 0:
            vtype = 5
            occ = 0
            cav = True
        elif matrix_name.lower().find("reg") >= 0:
            vtype = 1
            occ = 0
            cav = False

    elif matrix_name.lower().find("s2") >= 0 or matrix_name.find("a2") >= 0:
        if matrix_name.lower().find("cav") >= 0:
            vtype = 6
            occ = 1
            cav = True
        elif matrix_name.lower().find("reg") >= 0:
            vtype = 2
            occ = 1
            cav = False
    elif matrix_name.lower().find("s3") >= 0 or matrix_name.find("a3") >= 0:
        if matrix_name.lower().find("cav") >= 0:
            vtype = 6
            occ = 1
            cav = True
        elif matrix_name.lower().find("reg") >= 0:
            vtype = 2
            occ = 1
            cav = False
    elif matrix_name.lower().find("cargo") >= 0:
        if matrix_name.lower().find("cav") >= 0:
            vtype = 8
            occ = 2
            cav = True
        else:
            vtype = 4
            occ = 2
            cav = False
    elif matrix_name.lower().find("serv") >= 0:
        if matrix_name.lower().find("cav") >= 0:
            vtype = 7
            occ = 2
            cav = True
        else:
            vtype = 3
            occ = 2
            cav = False
    elif matrix_name.lower().find("taxi") >= 0:
        vtype = 2
        occ = 1
    elif matrix_name.lower().find("exta") >= 0:
        vtype = 2
        occ = 0
    elif matrix_name.lower().find("tnc") >= 0:
        vtype = 9
        occ = 1

    if matrix_name.find("_w") >= 0:
        if matrix_file_name.lower().find("dynust nonev") >= 0:
            purp = 1
        else:
            purp = 10
            ev = True
    elif matrix_name.find("_nw") >= 0:
        if matrix_file_name.lower().find("dynust nonev") >= 0:
            purp = 2
        else:
            purp = 20
            ev = True
    elif matrix_name.lower().find("taxi") >= 0:
        if matrix_file_name.lower().find("dynust nonev") >= 0:
            purp = 3
        else:
            purp = 30
            ev = True
    elif matrix_name.lower().find("tnc") >= 0:
        if matrix_file_name.lower().find("dynust nonev") >= 0:
            purp = 4
        else:
            purp = 40
            ev = True
    elif matrix_name.lower().find("serv") >= 0:
        if matrix_file_name.lower().find("dynust nonev") >= 0:
            purp = 5
        else:
            purp = 50
            ev = True
    elif matrix_name.lower().find("cargo") >= 0:
        if matrix_file_name.lower().find("dynust nonev") >= 0:
            purp = 6
        else:
            purp = 60
            ev = True

    # Time periods
    if matrix_file_name.lower().find("am") >= 0:
        period = 'am'
        time_period = '6..9'
    elif matrix_file_name.lower().find("md") >= 0:
        period = 'md'
        time_period = '9..15'
    elif matrix_file_name.lower().find("pm") >= 0:
        period = 'pm'
        time_period = '15..19'
    else:
        period = 'ov'
        time_period = '0..6, 19..24'

    for key in vots.keys():
        if matrix_name.lower().find(key) >= 0:
            vot = vots[key]
            break

    return dict(vtype=vtype, occ=occ, purp=purp, vot=vot, time_period=time_period, period=period, cav=cav, ev=ev)


def get_suffix(cav, ev, purp, time_period):

    if cav:
        cav = "CAV"
    else:
        cav = "REG"

    if ev:
        ev = "EV"
    else:
        ev = "NonEV"

    if purp in (1, 10):
        purp = "WK"
    elif purp in (2, 20):
        purp = 'NW'
    elif purp in (3, 30, 4, 40, 5, 50, 6, 60):
        purp = "MS"

    return "_".join((purp, cav, ev, time_period.upper()))


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

    # matrix_folder = r'C:\Projects\SWIFT\SWIFT_Project_Data\Inputs\OD\2045'
    matrix_folder = r'L:\DCS\Projects\_Legacy\60563434_SWIFT\400_Technical\SWIFT_Workspace\Scenarios\Scenario_S12\STM\STM_D\Outputs_SWIFT'
    matrices_am = ["OD AM3HR Vehicles4DynusT EV", "OD AM3HR Vehicles4DynusT NonEV"]
    matrices_md = ["OD MD6HR Vehicles4DynusT EV", "OD MD6HR Vehicles4DynusT NonEV"]
    matrices_pm = ["OD PM4HR Vehicles4DynusT EV", "OD PM4HR Vehicles4DynusT NonEV"]
    matrices_ov = ["OD OV8HR Vehicles4DynusT EV", "OD OV8HR Vehicles4DynusT NonEV"]
    matrices = matrices_am + matrices_md + matrices_pm + matrices_ov

    ev = ["EV", "NonEV"]
    purps = ["WK", "NW", "MS"]
    cav = ['CAV', 'REG']
    periods = ["AM", "MD", "PM", "OV"]

    # right open; day starts at 0
    period_def = {'AM': [(6, 9)], 'MD': [(9, 15)], 'PM': [(15,19)], 'OV': [(0, 6), (19, 24)]}

    vots = {
        "wi1da": 9.6, "wi2da": 15.04, "wi3da": 20.48, "wi4da": 27.52, "wi5da": 37.12,
        "wi12a2": 21.56, "wi3a2": 35.84, "wi45a2": 56.56,
        "wi12a3": 30.8, "wi3a3": 51.2, "wi45a3": 80.8,
        "nwi12da": 7.03, "nwi3da": 13.44, "nwi45da": 23.65,
        "nwi12a2": 12.3, "nwi3a2": 23.52, "nwi45a2": 41.39,
        "nwi12a3": 17.57, "nwi3a3": 33.6, "nwi45a3": 59.12,
        "cargo": 64.0, "serv": 40.0, "taxi_exta": 18.94, "tnc": 18.94
    }

    # vots = {"hbwi1da": 9.6, "hbwi2da": 15.04, "hbwi3da": 20.48, "hbwi4da": 27.52, "hbwi5da": 37.12, "hbwi12a2": 21.56,
    #         "hbwai3a2": 35.84, "hbwi45a2": 56.56, "hbwi12a3": 30.8, "hbwi3a3": 51.2, "hbwi45a3": 80.8,
    #         "hnwi12da": 7.03, "hnwi3da": 13.44, "hnwi45da": 23.65, "hnwi12a2": 12.3, "hnwai3a2": 23.52,
    #         "hnwi45a2": 41.39,"hnwi12a3": 17.57, "hnwi3a3": 33.6, "hnwi45a3": 59.12,
    #         "nhodai12": 7.03, "nhodai3": 13.44, "nhodai453": 23.65, "nhos2i12": 12.3, "nhos2i3": 23.52,
    #         "nhos2i45": 41.39, "nhos3i12": 17.57, "nhos3i3": 33.6, "nhos3i45": 59.12,
    #         "nhwdai1": 9.6, "nhwdai2": 15.04, "nhwdai3": 20.48, "nhwdai4": 27.52, "nhwdai5": 37.12, "nhws2i12": 21.56,
    #         "nhws2i3": 35.84, "nhws2i45": 56.56, "nhws3i12": 30.8, "nhws3i3": 51.2, "nhws3i45": 80.8,
    #         "Cargo": 64.0, "Serv": 40.0, "taxi": 18.94, "exta": 18.94}
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
        matrix_file_out = os.path.join(r'%SCEN_DIR%\STM\STM_D\Outputs_SWIFT', m + '.omx')
        h5 = h5py.File(matrix_file, 'r')
        tables = h5['/data/'].keys()

        purp = vot = occ = vtype = 0
        for t in tables:
            if t.find('all') >= 0 or t.find('M') >= 0:
                continue
            matrix_count += 1

            info = parse_matrix_table(m, t, vots)
            vtype = info['vtype']
            occ = info['occ']
            purp = info['purp']
            vot = info['vot']
            time_period = info['time_period']
            period = info['period']
            cav = info['cav']
            ev = info['ev']

            mode = 'w'
            control_file_suffix = get_suffix(cav, ev, purp, period)
            control_file = os.path.join(control_file_folder,
                                        "ConvertTrips_" + control_file_suffix + ".ctl")

            # Determine if the file has been opened
            if control_file_suffix in control_file_map:
                control_file_map[control_file_suffix] += 1
                mode = 'a'
            else:
                control_file_map[control_file_suffix] = 1

            key_group = control_file_map[control_file_suffix]

            with open(control_file, mode=mode) as f:
                key_names = [k+'_'+str(key_group) for k in rotation_keys]

                if key_group == 1:
                    f.write('{0:40s}{1:s}\n'.format('TITLE', 'Convert_Vehicle_Roster_{:s}'.format(control_file_suffix)))
                    f.write('{0:40s}{1:s}\n'.format('PROJECT_DIRECTORY', '%SCEN_DIR%'))
                    f.write('{0:40s}{1:s}\n'.format('REPORT_FILE', r'%SCEN_DIR%\STM\STM_A\01_DynusT\01_Controls\Convert_Vehicle_Roster_{:s}.prn'.format(control_file_suffix)))
                    f.write('{0:40s}{1:s}\n'.format('NUMBER_OF_ZONES', '5263'))
                    f.write('{0:40s}{1:s}\n'.format('RANDOM_SEED', '47'))
                    f.write('{0:40s}{1:s}\n'.format('ORIGIN_FILE', r'%SCEN_DIR%\STM\STM_A\01_DynusT\03_Model\origin.dat'))
                    f.write('{0:40s}{1:s}\n'.format('NEW_VEHICLE_ROSTER_FILE', r'%SCEN_DIR%\STM\STM_A\01_DynusT\02_Demand\Vehicles_{:s}.bin'.format(control_file_suffix)))
                    f.write('{0:40s}{1:s}\n'.format('NEW_VEHICLE_ROSTER_FORMAT', 'BINARY'))
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
