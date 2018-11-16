
import os
import numpy as np
from scipy.interpolate import interp1d


class DTGenerator:
    def __init__(self, x, prob, seed=0, interp=0, logger=None):
        """

        :param x:      x values for the probability density
        :param prob:   probabilities
        :param seed:   random seed
        :param interp: number of interpolation points
        :param logger: number of interpolation points
        """
        self._prob = prob
        self._x = x
        self._seed = seed
        self._interp = interp

        if len(x) != len(prob):
            if logger is not None:
                logger.error("The lengths of input distribution do not match")
            raise ValueError("The lengths of input distribution do not match")

        self._prob_interp = prob
        if interp:
            self._x_interp = np.linspace(x[0], x[-1], self._interp)
            interpolator = interp1d(self._x, self._prob, kind='cubic')
            self._prob_interp = interpolator(self._x_interp)
            self._prob_interp = self._prob_interp / sum(self._prob_interp)
        else:
            self._x_interp = self._x
        np.random.seed(self._seed)

    def _select_range(self, period=None):
        """

        :param period: period start and end times
        :type  list of tuples
        :return:
        """
        if period:
            selector = np.array([False]*len(self._x_interp))
            for p in period:
                selector = selector | ((self._x_interp >= p[0]) & (self._x_interp < p[1]))

            xs = self._x_interp[selector]
            probs = self._prob_interp[selector]
            probs = probs / np.sum(probs)
            return probs, xs
        return self._prob_interp, self._x_interp

    def dt(self, period, size=1):
        probs, xs = self._select_range(period)
        return np.random.choice(xs, p=probs, size=size)


def bucket_rounding(mat):
    """
    bucket rounding and add the difference to the diagonal elements
    :param mat: an numpy 2d-array
    :return: an numpy 2d-array of dtype np.uint16
    """

    if len(mat.shape) != 2:
        raise ValueError("Input must be a 2-dimensional numpy array")

    threshold = 0.05
    rows, columns = mat.shape
    mat_list = mat.tolist()
    for i in range(rows):
        residual = 0
        if mat[i].sum() <= threshold:
            continue
        for j in range(columns):
            if mat_list[i][j] != 0:
                val = np.round(mat_list[i][j] + residual)
                residual += mat_list[i][j] - val
                mat_list[i][j] = val

    rounded = np.array(mat_list)
    total_diff = int(round(rounded.sum() - mat.sum()))
    diff = np.where(total_diff > 0, -1, 1)
    indices = np.argsort(np.diagonal(rounded))[::-1].astype(np.int16)[:np.abs(total_diff)]
    rounded[indices, indices] += diff
    return rounded.clip(min=0).astype(np.int16)


def normal_rounding(mat):
    """
    normal rounding and add the difference to the diagonal elements
    :param mat: an numpy 2d-array
    :return:
    """
    if len(mat.shape) != 2:
        raise ValueError("Input must be a 2-dimensional numpy array")

    rounded = mat.round()
    total_diff = int(round(rounded.sum() - mat.sum()))
    diff = np.where(total_diff > 0, -1, 1)
    indices = np.argsort(np.diagonal(rounded))[::-1].astype(np.int16)[:np.abs(total_diff)]
    rounded[indices, indices] += diff
    return rounded.clip(min=0).astype(np.int16)

def parse_time_range(time_range, logger=None):
    """
    parse the time range
    :param time_range: parse comma-separated ranges like "0..6, 15..19"
    :type  str
    :return: "0..6, 15..19" is parsed into [(0, 6), (15, 19)]
    """

    if not isinstance(time_range, str):
        logger.error("Time range must be a string")
        return [(-1, -1)]

    parts = time_range.split(",")
    ranges = []

    for part in parts:
        if part.find("..") < 0:
            logger.error("Time range must have both start and end times. Input is %s" % part)
            return [(-1, -1)]
        else:
            start_time, end_time = part.split("..")
            ranges.append((float(start_time), float(end_time)))
    return ranges


def read_diurnal_file(diurnal_file, logger=None):
    """

    :param diurnal_file: a csv file for diurnal distribution between 0 and 24
    :return: two lists: hours and probs

    only two columns of data should be present
    an example diurnal file

    Hour,Share
    0,0.001
    1,0.001
    2,0.001
    3,0.002
    4,0.005
    5,0.015
    6,0.0501
    7,0.1022
    8,0.0581
    9,0.0411
    10,0.0481
    11,0.0571
    12,0.0571
    13,0.0521
    14,0.0651
    15,0.0982
    16,0.0852
    17,0.0832
    18,0.0651
    19,0.0451
    20,0.0301
    21,0.022
    22,0.01
    23,0.005
    24,0

    """

    if not os.path.exists(diurnal_file):
        if logger is not None:
            logger.info("Diurnal file %s does not exist" % diurnal_file)
        raise FileNotFoundError("Diurnal file %s does not exist" % diurnal_file)

    hours, probs = [], []
    with open(diurnal_file, mode='r') as f:
        next(f)
        for line in f:
            hour, prob = line.strip().split(',')
            hours.append(float(hour.strip()))
            probs.append(float(prob.strip()))
    return hours, probs


if __name__ == '__main__':

    pass
