import numpy as np
import h5py
from rounding import normal_rounding

from services.report_service import get_logger

logger = get_logger('__name__')

def to_vehicles(matrix, dt_generator, vots, period_def, origins):
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

    for tab in tables:
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
        # todo: Step 1: round the matrix
        od = normal_rounding(od)

        # todo: Step 2: get the departure times
        total_trips = od.sum()
        dt_pool = (t for t in dt_generator.dt(period=period_def[period], size=total_trips))

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
                        dtime = next(dt_pool)
                        yield anode, bnode, dtime, muc_class, vtype, 0, 0, 1, 0, 0.2, 0, orig, 0, ipos, vot, 0, 0, purp, 0, dest, 0


def write_vehicles(vehicle_file, vehicle_pool, start_id=1):
    '''
    write out the vehicle file

    :param vehicle_file:
    :param vehicle_pool: vehicle records
    :return: None
    '''

    with open(vehicle_file, mode='w', buffering=10_000) as f:
        vid = start_id
        for i, vals in enumerate(vehicle_pool):
            vid = start_id + i
            data = (vid, *vals[:-2])
            record = '%9d%7d%7d%8.1f%6d%6d%6d%6d%6d%6d%8.4f%8.4f%6d%6d%12.8f%8.2f%5d%7.1f%5d%5.1f\n' % (data)
            f.write(record)
            record = '%12d%7.2f\n' % (vals[-2:])
            f.write(record)
        logger.info("Total vehicles converted = {0:d}".format(vid))


if __name__ == '__main__':
    pass
    # to_vehicles(matrices_am, tod_shares, vots, period_def[3], origins)

    # test get_period_shares
    # for p, d in period_def.items():
    #     share = get_period_share(d, tod_times, tod_shares)
    #     print("Period {0} share = {1:.4f}".format(p, share))


