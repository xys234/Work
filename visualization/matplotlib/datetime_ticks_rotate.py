import datetime

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

from matplotlib.dates import num2date
from matplotlib.ticker import FuncFormatter


# Create data
vals = np.arange(1, 6, 1)
dates = pd.date_range(start='2020/01/22 10:00:00', end='2020/01/22 15:00:00', periods=5)


# Plot
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dates, vals)

# Formatter; https://matplotlib.org/api/dates_api.html#matplotlib.dates.date2num
def format_date(x: np.float64, pos):

    # https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
    return num2date(x).strftime("%Y-%m-%d %H:%M")
date_formatter = FuncFormatter(format_date)

# rotate the tick labels; https://matplotlib.org/api/axis_api.html
ax.xaxis.set_tick_params(labelrotation=15)
ax.xaxis.set_major_formatter(date_formatter)


fig.savefig('datetime_ticks_rotate.png', format='png')