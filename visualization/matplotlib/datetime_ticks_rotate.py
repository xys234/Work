import datetime

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

from matplotlib.ticker import FuncFormatter


# Create data
vals = np.arange(1, 6, 1)
dates = pd.date_range(start='2020/01/22 10:00:00', end='2020/01/22 15:00:00', periods=5)


# Plot
fig, ax = plt.subplots(figsize=(12,8))
ax.plot(dates, vals)

# rotate the tick labels
ax.tick_params(labelrotation=45)

fig.savefig('datetime_ticks_rotate.png', format='png')