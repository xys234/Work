import numpy as np
from numba import njit


@njit
def bucket_rounding(mat):
    if mat.ndim != 2:
        raise ValueError("Input must be a 2-dimensional numpy array")

    rounded = np.zeros_like(mat, dtype=np.double)
    ss = 0.0
    ss_rounded = 0.0

    n = mat.shape[0]
    for i in range(n):
        residual = 0
        for j in range(n):
            if mat[i, j] != 0:
                val = round(mat[i, j] + residual)
                residual += mat[i, j] - val
                rounded[i, j] = val
                ss += mat[i, j]
                ss_rounded += val

    rounded_arr = np.asarray(rounded)
    mat_arr = np.asarray(mat)
    total_diff = int(np.round(rounded_arr.sum() - mat_arr.sum()))
    diff = np.where(total_diff > 0, -1, 1)
    indices = np.argsort(np.diagonal(rounded_arr))[::-1].astype(np.int16)[:np.abs(total_diff)]
    rounded_arr[indices, indices] += diff
    return rounded_arr.clip(min=0).astype(np.int32)


@njit
def to_vehicles_helper(od, dt_generator, period, origins, vtype, vclass,
                      occ, gen_mode, num_stops, info, indiff_band,
                       comp_rate, evac, arrival_time, gas, wait_time,
                       purp, vot):
    """

    :param od:
    :param vtype:
    :param vclass:
    :param purp:
    :param vot:
    :param dt_generator:
    :param period:
    :param origins:
    :return:
    """

    total_trips = 0
    field_filler = 0

    # Get the departure times
    total_trips = od.sum()
    dt_pool = (t for t in dt_generator)

    mv = memoryview(od)
    for i in range(mv.shape[0]):
        for j in range(mv.shape[0]):
            trip = mv[i, j]
            if trip > 0:
                gen_link_choice = np.random.choice(len(origins[i+1]))
                anode, bnode = origins[i+1][gen_link_choice][0], origins[i+1][gen_link_choice][1]
                orig = i + 1
                dest = j + 1
                ipos = float(np.random.randint(1, 10000)) / 10000
                for k in range(trip):
                    dtime = next(dt_pool)
                    yield anode, bnode, dtime, vclass, vtype, occ, \
                              gen_mode, num_stops, info, indiff_band, \
                              comp_rate, orig, evac, ipos, vot, field_filler, arrival_time, \
                              purp, gas, dest, wait_time  # 21 fields


def parse_origins(origin_file, zones=5263, logger=None):
    """
    Parse dynus-T origin file to get a dictionary of all origins
    :param origin_file: full path to the origin file
    :type  string
    :return:  zone -> [(from_node, to_node, weight)]
    :type: dict
    """

    origins = {}
    with open(origin_file, 'r') as dy_origin_file:
        total_num_origins = 0
        pos = 0
        zone = num_origins = -1
        for j, line in enumerate(dy_origin_file):
            record = line.strip().split()
            if j == 0 or j == pos:
                zone, num_origins = int(record[0]), int(record[1])
                pos = pos + num_origins + 1
            else:
                total_num_origins += 1
                from_node, to_node, weight = int(record[0]), int(record[1]), int(record[2])
                if zone not in origins:
                    origins[zone] = [(from_node, to_node, weight)]
                else:
                    origins[zone].append((from_node, to_node, weight))

    # Scan the origins to find the zones without origins
    zones_without_origin = []
    for i in range(zones):
        if i+1 not in origins:
            zones_without_origin.append(i+1)

    if zones_without_origin:
        logger.warning('{0:d} zones do not have origins: {1}'.format(len(zones_without_origin), zones_without_origin))
    logger.info("Number of Dynus-T Origin Records = {0:d}".format(total_num_origins))
    return origins


