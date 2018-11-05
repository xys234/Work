import os
import numpy as np
import h5py
import time
from rounding import normal_rounding, bucket_rounding
from parse_origins import parse_origins
from dt_generator import DTGenerator


def to_vehicles(matrix, vehfile, tod_times, tod_shares, vots, period_def, origins, start_id = 1, misc=0):
    """
    Convert the input matrix to a generator of vehicles
    :param matrix: an omx matrix file for a period-purpose combination
    :param tabs: the tabs to extract mode and income
    :param tod_times: times in floats in [0, 24)
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
        if matrix.find(p) >= 0:
            period = p
            print("Processing period {0}".format(p))
            break

    for tab in tables:
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
        # todo: Step 1: round the matrix
        od = normal_rounding(od)

        # todo: Step 2: get the departure times
        total_trips = od.sum()
        dt_pool = (t for t in DTGenerator.dt(period=period, size=total_trips))

        # todo: Step 3: write the vehicle records
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
                        vid = start_id + k + 1
                        dtime = next(dt_pool)
                        yield vid, anode, bnode, dtime, 3, vtype, 0, 0, 1, 0, 0.2, 0, orig, 0, ipos, vot, 0, 0, purp, 0, dest, 0



        # with open(vehfile, mode='w') as f:
        #     record = '%9d%7d%7d%8.1f%6d%6d%6d%6d%6d%6d%8.4f%8.4f%6d%6d%12.8f%8.2f%5d%7.1f%5d%5.1f\n' % (
        #         vid, anode, bnode, dtime, 3, vtype, 0, 0, 1, 0, 0.2, 0, orig, 0, ipos, vot, 0, 0, purp, 0)
        #     f.write(record)
        #
        #     record = '%12d%7.2f\n' % (dest, 0)
        #     f.write(record)

        return total_trips


if __name__ == '__main__':
    matrices_am = ["OD AM3HR HBNW Vehicles", "OD AM3HR HBW Vehicles", "OD AM3HR NHB Vehicles", "OD AM3HR Other VEHICLEs"]
    matrices_md = ["OD MD6HR HBNW Vehicles", "OD MD6HR HBW Vehicles", "OD MD6HR NHB Vehicles", "OD MD6HR Other VEHICLEs"]
    matrices_pm = ["OD PM4HR HBNW Vehicles", "OD PM4HR HBW Vehicles", "OD PM4HR NHB Vehicles", "OD PM4HR Other VEHICLEs"]
    matrices_ov = ["OD OV8HR HBNW Vehicles", "OD OV8HR HBW Vehicles", "OD OV8HR NHB Vehicles", "OD OV8HR Other VEHICLEs"]

    purp = ["hnw", "hbw", "nho", "nhw"]
    periods = ["am", "md", "pm", "ov"]
    periods_other = ["AM3", "MD6", "PM4", "OV8"]

    # right open; day starts at 0
    period_def = {'am': [(6, 9)], 'md': [(9,15)], 'pm': [(15,19)], 'ov': [(0, 6), (19, 24)]}

    # tabs = [
    #         ["i12da", "i3da", "i45da",                  # HBNW-DA
    #          "i12a2", "ai3a2", "i45a2",                 # HBNW-S2
    #          "i12a3", "i3a3", "i45a3"],                 # HBNW-S3
    #         ["i1da", "i2da", "i3da", "i4da", "i5da",    # HBW-DA
    #          "i12a2", "ai3a2", "i45a2",                 # HBW-S2
    #          "i12a3", "i3a3", "i45a3"],                 # HBW-S3
    #         ["dai12", "dai3", "dai453",                 # NHO-DAN
    #          "s2i12", "s2i3", "s2i45",                  # NHO-S2
    #          "s3i12", "s3i3", "s3i45",                  # NHO-S3
    #          "dai1", "dai2", "dai3", "dai4", "dai5",    # NHW-DA
    #          "s2i12", "s2i3", "s2i45",                  # NHW-S2
    #          "s3i12", "s3i3", "s3i45"],                 # NHW-S3
    #        ["Cargo", "Serv", "taxi", "exta"]            # OTHER
    #        ]

    tod_times = list(range(24))

    tod_shares = [0.0010, 0.0010, 0.0010, 0.0020, 0.0050, 0.0150, 0.0501, 0.1022, 0.0581, 0.0411, 0.0481, 0.0571, 0.0571,
               0.0521, 0.0651, 0.0982, 0.0852, 0.0832, 0.0651, 0.0451, 0.0301, 0.0220, 0.0100, 0.0050]

    vots = {"hbwi1da": 9.6, "hbwi2da": 15.04, "hbwi3da": 20.48, "hbwi4da": 27.52, "hbwi5da": 37.12, "hbwi12a2": 21.56,
           "hbwai3a2": 35.84, "hbwi45a2": 56.56, "hbwi12a3": 30.8, "hbwi3a3": 51.2, "hbwi45a3": 80.8,
           "hnwi12da": 7.03, "hnwi3da": 13.44, "hnwi45da": 23.65, "hnwi12a2": 12.3, "hnwai3a2": 23.52,
           "hnwi45a2": 41.39,"hnwi12a3": 17.57, "hnwi3a3": 33.6, "hnwi45a3": 59.12,
           "nhodai12": 7.03, "nhodai3": 13.44, "nhodai453": 23.65, "nhos2i12": 12.3, "nhos2i3": 23.52,
           "nhos2i45": 41.39, "nhos3i12": 17.57, "nhos3i3": 33.6, "nhos3i45": 59.12,
           "nhwdai1": 9.6, "nhwdai2": 15.04, "nhwdai3": 20.48, "nhwdai4": 27.52, "nhwdai5": 37.12, "nhws2i12": 21.56,
           "nhws2i3": 35.84, "nhws2i45": 56.56, "nhws3i12": 30.8, "nhws3i3": 51.2, "nhws3i45": 80.8,
           "Cargo": 64.0, "Serv": 40.0, "taxi": 18.94, "exta": 18.94}

    dynust_folder = '..\data\Dynus_T'
    DynusT_origin_file = os.path.join(dynust_folder, 'origin.dat')

    # origins = parse_origins(DynusT_origin_file)
    # to_vehicles(matrices_am, tod_shares, vots, period_def[3], origins)

    # test get_period_shares
    # for p, d in period_def.items():
    #     share = get_period_share(d, tod_times, tod_shares)
    #     print("Period {0} share = {1:.4f}".format(p, share))


