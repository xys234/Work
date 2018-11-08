import numpy as np
from scipy.interpolate import interp1d
from services import report_service

logger = report_service.get_logger(__name__)

class DTGenerator:
    def __init__(self, x, prob, seed=0, interp=0):
        """

        :param x:      x values for the probability density
        :param prob:   probabilities
        :param seed:   random seed
        :param interp: number of interpolation points
        """
        self._prob = prob
        self._x = x
        self._seed = seed
        self._interp = interp

        if len(x) != len(prob):
            logger.error("The lengths of input distribution do not match", exc_info=True)
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


if __name__ == '__main__':
    hours = np.arange(0, 25, 1)
    share = [0.0010, 0.0010, 0.0010, 0.0020, 0.0050, 0.0150, 0.0501, 0.1022, 0.0581, 0.0411, 0.0481, 0.0571, 0.0571,
             0.0521, 0.0651, 0.0982, 0.0852, 0.0832, 0.0651, 0.0451, 0.0301, 0.0220, 0.0100, 0.0050, 0]
    points = 600 * 24

    trips = [1000] * 4
    periods = [[(6, 9)], [(9, 15)], [(15, 19)], [(0, 6), (19, 24)]]
    # dt_gen = DTGenerator(x=hours, prob=share, interp=points, seed=42)
    dt_gen = DTGenerator(x=range(3), prob=range(4), interp=points, seed=42)


    # period = [(0, 6), (19, 24)]
    # probs, xs = dt_gen._select_range(period)
    # print(np.min(xs))

    import time

    start = time.clock()
    departure_times = np.array([])
    for trip, period in zip(trips, periods):
        departure_times = np.concatenate([departure_times, dt_gen.dt(period, trip)])
    end = time.clock()
    logger.info("Total Processing Time = {0:.2f} seconds".format(end - start))

