import numpy as np
from internals.sorted_collection import SortedCollection


def bucket_rounding(mat):
    if mat.ndim != 2:
        raise ValueError("Input must be a 2-dimensional numpy array")

    rounded = np.zeros_like(mat, dtype=np.double)

    n = mat.shape[0]
    for i in range(n):
        residual = 0
        for j in range(n):
            if mat[i, j] != 0:
                val = round(mat[i, j] + residual)
                residual += mat[i, j] - val
                rounded[i, j] = val

    total_diff = np.round(rounded.sum() - mat.sum())
    if total_diff > 0:
        diff = -1
    else:
        diff = 1
    indices = np.argsort(np.diag(rounded))[::-1].astype(np.int16)[:np.abs(total_diff)]
    for i in range(indices.shape[0]):
        rounded[int(indices[i]), int(indices[i])] += diff

    for i in range(rounded.shape[0]):
        for j in range(rounded.shape[1]):
            rounded[i, j] = max(0, rounded[i, j])
    return rounded.astype(np.int32)


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

    for i in range(od.shape[0]):
        for j in range(od.shape[0]):
            trip = od[i, j]
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


class Lookup:
    def __init__(self, x, y, name):
        """

        :param x:
        :type  x: list
        :param y:
        :type  y: list
        :param name:
        :type  name: str
        """

        if len(x) != len(y):
            raise ValueError('Input x and y must have equal length')

        self.sorted_collection = SortedCollection(zip(x, y), key=lambda e: e[0])
        self.name = name

    def lookup(self, x, exact=False):
        """
        Find the item (x, value)
        :param x:
        :param exact:
        :return:

        when approximate match is enabled
        if the item is present, the item will be returned.
        if the item's key is lower than the smallest key, the smallest key item is returned
        if the item's key is larger than the largest key, the largest key item is returned
        if the item's key is within range, a value by linear interpolation is returned

        The returned item is always a tuple (x, value)

        """

        item = None
        try:
            item = self.sorted_collection.find(x)
        except ValueError:
            pass

        if exact or item:
            return item
        else:
            low, high = None, None
            try:
                low = self.sorted_collection.find_lt(x)
            except ValueError:
                pass

            try:
                high = self.sorted_collection.find_gt(x)
            except ValueError:
                pass

            if not low and high:
                return x, high[1]
            elif low and not high:
                return x, low[1]
            else:
                (x0, y0), (x1, y1) = low, high
                return x, y0 + (x - x0) * (y1 - y0) / (x1 - x0)