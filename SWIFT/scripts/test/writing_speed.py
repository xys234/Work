import numpy as np
import random
import time
from services.data_service import DTGenerator
from services.report_service import Report_Service
from services.network_service import parse_origins

rs = Report_Service('writing_speed.prn')
logger = rs.get_logger()

origin_file = r'C:\Projects\Repo\Work\SWIFT\data\Dynus_T\origin.dat'
origins = parse_origins(origin_file, logger=logger)


hours = np.arange(0, 25, 1)
share = [0.0010, 0.0010, 0.0010, 0.0020, 0.0050, 0.0150, 0.0501, 0.1022, 0.0581, 0.0411, 0.0481, 0.0571, 0.0571,
         0.0521, 0.0651, 0.0982, 0.0852, 0.0832, 0.0651, 0.0451, 0.0301, 0.0220, 0.0100, 0.0050, 0]
points = 600 * 24

vots = {"hbwi1da": 9.6, "hbwi2da": 15.04, "hbwi3da": 20.48, "hbwi4da": 27.52, "hbwi5da": 37.12, "hbwi12a2": 21.56,
        "hbwai3a2": 35.84, "hbwi45a2": 56.56, "hbwi12a3": 30.8, "hbwi3a3": 51.2, "hbwi45a3": 80.8,
        "hnwi12da": 7.03, "hnwi3da": 13.44, "hnwi45da": 23.65, "hnwi12a2": 12.3, "hnwai3a2": 23.52,
        "hnwi45a2": 41.39, "hnwi12a3": 17.57, "hnwi3a3": 33.6, "hnwi45a3": 59.12,
        "nhodai12": 7.03, "nhodai3": 13.44, "nhodai453": 23.65, "nhos2i12": 12.3, "nhos2i3": 23.52,
        "nhos2i45": 41.39, "nhos3i12": 17.57, "nhos3i3": 33.6, "nhos3i45": 59.12,
        "nhwdai1": 9.6, "nhwdai2": 15.04, "nhwdai3": 20.48, "nhwdai4": 27.52, "nhwdai5": 37.12, "nhws2i12": 21.56,
        "nhws2i3": 35.84, "nhws2i45": 56.56, "nhws3i12": 30.8, "nhws3i3": 51.2, "nhws3i45": 80.8,
        "Cargo": 64.0, "Serv": 40.0, "taxi": 18.94, "exta": 18.94}

period_def = {'am': [(6, 9)], 'md': [(9, 15)], 'pm': [(15, 19)], 'ov': [(0, 6), (19, 24)]}

def to_vehicles(od, origins, dt_pool, logger):
    total_trips = od.sum()
    logger.info('Total number of trips  = {0:.0f}'.format(total_trips))

    muc_class = 3
    vtype = 1
    vot = 23.45
    purp = 2

    dt_generator = DTGenerator(hours, share, interp=points).dt(period=period_def['am'], size=total_trips)
    dt_pool = (t for t in dt_generator)

    # Step 3: write the vehicle records
    for i in range(od.shape[0]):
        for j in range(od.shape[0]):
            trip = od[i][j]
            if trip > 0:
                gen_link_choice = np.random.choice(len(origins[i + 1]))
                anode, bnode = origins[i + 1][gen_link_choice][0], origins[i + 1][gen_link_choice][1]
                orig = i + 1
                dest = j + 1
                ipos = float(np.random.randint(1, 10000)) / 10000
                for k in range(trip):
                    dtime = next(dt_pool)
                    yield anode, bnode, dtime, muc_class, vtype, 0, 0, 1, 0, 0.2, 0, orig, 0, ipos, vot, 0, 0, purp, 0, dest, 0

    # for i in range(number_of_lines):
    #     dt = next(dt_gen)
    #     yield tuple(random.choices(range(number_of_fields), k=number_of_fields))+(20, dt)


t0 = time.time()
dt_pool = (t for t in dt_generator)
d2_pool = to_vehicles(number_of_lines, number_of_fields, dt_pool, logger)

with open('test.txt', mode='a', newline="", buffering=10_000_000) as f:

    for i, data1 in enumerate(d2_pool):
        time_1 = time.time()
        logger.info('DEBUG: TRIP {0:d} = {1:.8f}'.format(i, time_1))
        data = (i, *data1[:-2])
        time_2 = time.time()
        # logger.info('DEBUG: TIME 1 = {0:.8f}'.format(time_2 - time_1))
        record = '%9d%7d%7d%8.1f%6d%6d%6d%6d%6d%6d%8.4f%8.4f%6d%6d%12.8f%8.2f%5d%7.1f%5d%5.1f\n' % (data)
        time_3 = time.time()
        # logger.info('DEBUG: TIME 2 = {0:.8f}'.format(time_3 - time_2))
        f.write(record)
        time_4 = time.time()
        # logger.info('DEBUG: TIME 3 = {0:.8f}'.format(time_4 - time_3))
        record = '%12d%7.2f\n' % (data1[-2:])
        time_5 = time.time()
        # logger.info('DEBUG: TIME 4 = {0:.8f}'.format(time_5 - time_4))
        f.write(record)
        time_6 = time.time()
        # logger.info('DEBUG: TIME 5 = {0:.8f}'.format(time_6 - time_5))


d = time.time() - t0
logger.info("duration: %.2f s." % d)