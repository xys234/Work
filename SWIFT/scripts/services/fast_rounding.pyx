import numpy as np


def bucket_rounding(double[:, :] mat):
    if mat.ndim != 2:
        raise ValueError("Input must be a 2-dimensional numpy array")

    cdef double[:, :] rounded = np.zeros_like(mat, dtype=np.double)
    cdef:
        int i, j, n
        double val = 0.0
        double residual = 0.0
        double ss = 0.0
        double ss_rounded = 0.0

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

def to_vehicles_helper(od, dt_generator, period, origins, int vtype, int vclass,
                       int occ, int gen_mode, int num_stops, int info, double indiff_band,
                       double comp_rate, int evac, double arrival_time, double gas, double wait_time,
                       int purp, double vot):
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

    cdef:
        int total_trips = 0
        int i, j, k, trip
        int field_filler = 0

        int[:, :] mv

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