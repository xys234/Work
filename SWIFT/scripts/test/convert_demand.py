import time
import numpy as np
import h5py
from rounding import bucket_rounding
from services.data_service import DTGenerator
from services.network_service import parse_origins
from services.report_service import Report_Service

def to_vehicles(matrix, tab, dt_generator, vots, period_def, origins, logger):
    """

    :param matrix: an omx matrix file for a period-purpose combination
    :param tabs: the tabs to extract mode and income
    :param tod_times: times in floats in [0, 25)
    :param tod_shares: trip shares in floats in [0, 1)
    :param vots:
    :param period_def: a tuple [start, end)
    :param origins: a dict storing origins
    :param misc: for MISC trips or not
    :return:

    "        #   usec   dsec   stime vehcls vehtype ioc #ONode #IntDe info ribf    comp   izone Evac InitPos    VoT  tFlag pArrTime TP IniGas\n"
    vid, anode (gen link), bnode, dtime, 3, vtype, 0, 0, 1, 0, 0.2, 0, orig, 0, ipos (origin zone ID), vot, 0, 0, purp, 0



    """

    muc_class = 3       # DUE

    # Open the matrix
    h5 = h5py.File(matrix, 'r')
    tables = h5['/matrices/'].keys()
    print("Processing matrix: {0}".format(matrix))

    vclass = 0
    vtype = 0
    purp = 0
    vot = 0
    period = 0

    for p in period_def.keys():
        if tab.find(p) >= 0:
            period = p
            print("Processing period {0}".format(p))
            break

    if tab.find("da") >= 0:
        vtype = 1
    elif tab.find("s2") >= 0 or tab.find("a2") >= 0:
        vtype = 2
    elif tab.find("s3") >= 0 or tab.find("a3") >= 0:
        vtype = 3
    elif tab.find("Cargo") >= 0:
        vtype = 6
    elif tab.find("Serv") >= 0:
        vtype = 5
    elif tab.find("taxi") >= 0:
        vtype = 4
    elif tab.find("exta") >= 0:
        vtype = 1

    if tab.find("hbw") >= 0:
        purp = 1
    elif tab.find("hnw") >= 0:
        purp = 2
    elif tab.find("nhw") >= 0:
        purp = 3
    elif tab.find("nho") >= 0:
        purp = 4
    else:
        purp = 5

    for key in vots:
        if tab.find(key) >= 0:
            vot = vots[key]
            break


        od = h5['/matrices/' + tab][:]
        # Step 1: round the matrix
        logger.info('START rounding    time = {0:.0f}'.format(time.time()))
        od = bucket_rounding(od)
        logger.info('AFTER rounding    time = {0:.0f}'.format(time.time()))

        # Step 2: get the departure times
        total_trips = od.sum()
        logger.info('Total number of trips  = {0:.0f}'.format(total_trips))
        dt_pool = (t for t in dt_generator.dt(period=period_def[period], size=total_trips))

        # Step 3: write the vehicle records
        for i in range(od.shape[0]):
            for j in range(od.shape[0]):
                trip = od[i][j]
                if trip > 0:
                    gen_link_choice = np.random.choice(len(origins[i+1]))
                    anode, bnode = origins[i+1][gen_link_choice][0], origins[i+1][gen_link_choice][1]
                    orig = i + 1
                    dest = j + 1
                    ipos = float(np.random.randint(1, 10000)) / 10000
                    for k in range(trip):
                        dtime = next(dt_pool)
                        yield anode, bnode, dtime, muc_class, vtype, 0, 0, 1, 0, 0.2, 0, orig, 0, ipos, vot, 0, 0, purp, 0, dest, 0


def write_vehicles(vehicle_file, vehicle_pool, start_id=1, logger=None):
    '''
    write out the vehicle file

    :param vehicle_file:
    :param vehicle_pool: vehicle records
    :return: None
    '''

    with open(vehicle_file, mode='w', buffering=10_000_000) as f:
        vid = start_id
        for i, vals in enumerate(vehicle_pool):
            time_1 = time.time()
            logger.info('DEBUG: TRIP {0:d} = {1:.8f}'.format(i, time_1))
            vid = start_id + i
            data = (vid, *vals[:-2])
            time_2 = time.time()
            # logger.info('DEBUG: TIME 1 = {0:.8f}'.format(time_2-time_1))
            record = '%9d%7d%7d%8.1f%6d%6d%6d%6d%6d%6d%8.4f%8.4f%6d%6d%12.8f%8.2f%5d%7.1f%5d%5.1f\n' % (data)
            time_3 = time.time()
            # logger.info('DEBUG: TIME 2 = {0:.8f}'.format(time_3-time_2))
            f.write(record)
            time_4 = time.time()
            # logger.info('DEBUG: TIME 3 = {0:.8f}'.format(time_4-time_3))
            record = '%12d%7.2f\n' % (vals[-2:])
            time_5 = time.time()
            # logger.info('DEBUG: TIME 4 = {0:.8f}'.format(time_5-time_4))
            f.write(record)
            time_6 = time.time()
            # logger.info('DEBUG: TIME 5 = {0:.8f}'.format(time_6-time_5))

    logger.info("Total vehicles converted = {0:d}".format(vid))


if __name__ == '__main__':
    matrices_am = ["OD AM3HR HBNW Vehicles", "OD AM3HR HBW Vehicles", "OD AM3HR NHB Vehicles", "OD AM3HR Other VEHICLEs"]
    matrices_md = ["OD MD6HR HBNW Vehicles", "OD MD6HR HBW Vehicles", "OD MD6HR NHB Vehicles", "OD MD6HR Other VEHICLEs"]
    matrices_pm = ["OD PM4HR HBNW Vehicles", "OD PM4HR HBW Vehicles", "OD PM4HR NHB Vehicles", "OD PM4HR Other VEHICLEs"]
    matrices_ov = ["OD OV8HR HBNW Vehicles", "OD OV8HR HBW Vehicles", "OD OV8HR NHB Vehicles", "OD OV8HR Other VEHICLEs"]
    matrices = matrices_am + matrices_md + matrices_pm + matrices_ov

    purp = ["hnw", "hbw", "nho", "nhw"]
    periods = ["am", "md", "pm", "ov"]
    periods_other = ["AM3", "MD6", "PM4", "OV8"]

    # right open; day starts at 0
    period_def = {'am': [(6, 9)], 'md': [(9,15)], 'pm': [(15,19)], 'ov': [(0, 6), (19, 24)]}

    hours = np.arange(0, 25, 1)
    share = [0.0010, 0.0010, 0.0010, 0.0020, 0.0050, 0.0150, 0.0501, 0.1022, 0.0581, 0.0411, 0.0481, 0.0571, 0.0571,
             0.0521, 0.0651, 0.0982, 0.0852, 0.0832, 0.0651, 0.0451, 0.0301, 0.0220, 0.0100, 0.0050, 0]
    points = 600 * 24

    vots = {"hbwi1da": 9.6, "hbwi2da": 15.04, "hbwi3da": 20.48, "hbwi4da": 27.52, "hbwi5da": 37.12, "hbwi12a2": 21.56,
            "hbwai3a2": 35.84, "hbwi45a2": 56.56, "hbwi12a3": 30.8, "hbwi3a3": 51.2, "hbwi45a3": 80.8,
            "hnwi12da": 7.03, "hnwi3da": 13.44, "hnwi45da": 23.65, "hnwi12a2": 12.3, "hnwai3a2": 23.52,
            "hnwi45a2": 41.39,"hnwi12a3": 17.57, "hnwi3a3": 33.6, "hnwi45a3": 59.12,
            "nhodai12": 7.03, "nhodai3": 13.44, "nhodai453": 23.65, "nhos2i12": 12.3, "nhos2i3": 23.52,
            "nhos2i45": 41.39, "nhos3i12": 17.57, "nhos3i3": 33.6, "nhos3i45": 59.12,
            "nhwdai1": 9.6, "nhwdai2": 15.04, "nhwdai3": 20.48, "nhwdai4": 27.52, "nhwdai5": 37.12, "nhws2i12": 21.56,
            "nhws2i3": 35.84, "nhws2i45": 56.56, "nhws3i12": 30.8, "nhws3i3": 51.2, "nhws3i45": 80.8,
            "Cargo": 64.0, "Serv": 40.0, "taxi": 18.94, "exta": 18.94}

    dt_generator = DTGenerator(hours, share, interp=points)
    vehicle_file = "vehicle_test.dat"
    origin_file = r'C:\Projects\Repo\Work\SWIFT\data\Dynus_T\origin.dat'

    rs = Report_Service('test.prn')
    logger = rs.get_logger()

    origins = parse_origins(origin_file, logger=logger)

    # matrix_file = r'C:\Projects\Repo\Work\SWIFT\data\Dynus_T\OD\2017\OD AM3HR HBNW Vehicles.omx'
    matrix_file = r'C:\Projects\Repo\Work\SWIFT\scripts\test\test.omx'
    tab = 'amhnwai3a2'
    vehicle_pool = to_vehicles(matrix_file, tab, dt_generator, vots, period_def, origins, logger=logger)
    write_vehicles(vehicle_file, vehicle_pool, logger=logger)
