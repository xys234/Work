import os
import numpy as np
import h5py
import time
from parse_origins import parse_origins


def get_period_share(period, tod_times, tod_shares):
    """

    :param period: a list of tuples specifying period start and end times
    :param tod_times:
    :param tod_shares:
    :return:
    """
    share = []
    times = []
    for p in period:
        for t, s in zip(tod_times, tod_shares):
            if p[0] <= t < p[1]:
                share.append(s)
                times.append(t)
    return share, times


def bucket_rounding(mat):
    """
    bucket rounding and add the difference to the diagonal elements
    :param mat: an numpy 2d-array
    :return: an numpy 2d-array of dtype np.uint16
    """

    assert len(mat.shape) == 2, "Input shape must be 2"
    rounded = np.zeros_like(mat, dtype=mat.dtype)

    for i in range(mat.shape[0]):
        residual = 0
        for j in range(mat.shape[1]):
            if mat[i, j] != 0:
                val = np.round(mat[i, j] + residual)
                residual += mat[i, j] - val
                rounded[i, j] = val

    total_diff = int(round(rounded.sum() - mat.sum()))
    diff = np.where(total_diff > 0, -1, 1)
    indices = np.argsort(np.diagonal(rounded))[::-1].astype(np.int16)[:np.abs(total_diff)]
    rounded[indices, indices] += diff
    return rounded.clip(min=0).astype(np.int16)


def normal_rounding(mat):
    """
    normal rounding and add the difference to the diagonal elements
    :param mat:
    :return:
    """

    rounded = mat.round()
    total_diff = int(round(rounded.sum() - mat.sum()))
    diff = np.where(total_diff>0, -1, 1)
    indices = np.argsort(np.diagonal(rounded))[::-1].astype(np.int16)[:np.abs(total_diff)]
    rounded[indices, indices] += diff
    return rounded.clip(min=0).astype(np.int16)

def to_vehicles(matrix, tod_times, tod_shares, vots, period_def, origins, misc=0):
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

        period_share, period_times = get_period_share(period_def[period], tod_times, tod_shares)
        od = h5['/matrices/' + tab][:]



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

    # test bucket rounding
    np.random.seed(42)
    m = np.random.random([5237, 5237])
    # m = np.random.random([1000,1000])
    # m = np.random.random([3,3])

    time_bucket, time_normal = 0.0, 0.0

    start = time.clock()
    m_bucket_rounded = bucket_rounding(m)
    end = time.clock()
    time_bucket = end - start

    start = time.clock()
    m_rounded = normal_rounding(m)
    end = time.clock()
    time_normal = end - start

    # print(m)
    # print(m_rounded)
    print("Input Total = {0:.2f}".format(m.sum()))
    print("Normal rounding Total = {0:.2f}".format(m_rounded.sum()))
    print("Bucket rounding Total = {0:.2f}".format(m_bucket_rounded.sum()))
    print("Max row total difference = {0:.2f}".format(max(np.abs(m.sum(axis=0) - m_rounded.sum(axis=0)))))

    print("Normal rounding Time = {0:.2f}".format(time_normal))
    print("Bucket rounding Time = {0:.2f}".format(time_bucket))
