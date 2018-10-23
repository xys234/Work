import numpy as np
from scipy.interpolate import interp1d

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

    # normalize the share
    share = [s * 1.0 / sum(share) for s in share]
    return share, times


def get_departures(period, tod_times, tod_shares, points = 14400, size=1000):
    """
    :param period: a list of tuples specifying period start and end times

    """
    # Do the interpolation
    if len(tod_times) < points:
        f = interp1d(tod_times, tod_shares, kind='cubic')
        tod_times = np.linspace(0, max(tod_times), points)
        tod_shares = f(tod_times)

    shares, times = get_period_share(period, tod_times, tod_shares)
    selected_time = 0.0
    for t in range(size):
        index = np.random.choice(np.arange(len(shares)), p=shares)
        if index >= len(shares) - 1:
            selected_time = np.random.uniform(times[index], period[0][1], size=1)[0]
        else:
            start_time, end_time = times[index], times[index + 1]
            selected_time = np.random.uniform(start_time, end_time, size=1)[0]
        yield selected_time


if __name__ == '__main__':

    np.random.seed(42)
    tod_times = list(range(24))

    tod_shares = [0.0010, 0.0010, 0.0010, 0.0020, 0.0050, 0.0150, 0.0501, 0.1022, 0.0581, 0.0411, 0.0481, 0.0571, 0.0571,
               0.0521, 0.0651, 0.0982, 0.0852, 0.0832, 0.0651, 0.0451, 0.0301, 0.0220, 0.0100, 0.0050]
    period_def = {'am': [(6, 9)], 'md': [(9, 15)], 'pm': [(15, 19)], 'ov': [(0, 6), (19, 24)]}
    period = 'ov'

    departure_times = []
    sample_size = 10
    # for p in period_def.keys():
    for p in ['am']:
        print("Processing period {0:s}".format(p))
        dt = get_departures(period_def[p], tod_times, tod_shares, points=24, size=sample_size)
        for t in dt:
            departure_times.append(t)
    print(departure_times)