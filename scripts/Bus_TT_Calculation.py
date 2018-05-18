
# coding: utf-8

# In[1]:

from pandas import DataFrame, Series
import pandas as pd
import numpy as np

import sys, os

path = str(sys.argv[1])
drive, path_and_file = os.path.splitdrive(path)
direc, file = os.path.split(path_and_file)
scen, ext = os.path.splitext(file)


# ## Read the data

# In[2]:

df = pd.read_table(os.path.join(drive, path_and_file),sep=';',skiprows=16)


# Drop all PTSTOP with NaN
df2 = df.dropna(axis=0)

# ## Extract the arrival and departure vehicle



# Group-by 'NO','PTLINE', 'PTSTOP', which uniquely identify each record
# select the min simsec and max simsec
df2_group = df2.groupby(['NO','PTLINE', 'PTSTOP'])



df2_arrivals = df2_group.head(1)


# ## Compute the headways by sorting by stop, PTLINE and simulation time stamp


df2_headway = df2_arrivals.sort_values(by=['PTSTOP','PTLINE','SIMSEC'])



# headway = Trail veh -  lead veh
arrivals = (df2_headway['SIMSEC']).values
lead = arrivals[0:len(arrivals)-1]
trail = arrivals[1:]
headway = np.zeros(len(arrivals))
headway[1:] = trail - lead



# Store the results
df2_headway['headway']=headway
df2_headway_output = df2_headway[df2_headway['headway']>0]


headway_name = drive+direc+'/'+scen+"_headway.csv"
df2_headway_output.to_csv(os.path.normpath(headway_name), index=False)

# ## Compute the dwell time


df2_first = df2_group.head(1)
df2_last = df2_group.tail(1)



# merge using ['NO','PTLINE', 'PTSTOP']
merged = pd.merge(df2_first, df2_last, left_on = ['NO','PTLINE', 'PTSTOP'], right_on=['NO','PTLINE', 'PTSTOP'], suffixes=['_min','_max'])


merged['dwell_time'] = merged['SIMSEC_max'] - merged['SIMSEC_min']
dwell_time = merged[['$VEHICLE:SIMRUN_min', 'PTLINE', 'NO', 'PTSTOP', 'dwell_time']]
dwell_time.rename(columns={'$VEHICLE:SIMRUN_min':'$VEHICLE:SIMRUN'})
dwell_name = drive+direc+'/'+scen+"_dwell_time.csv"
dwell_time.to_csv(os.path.normpath(dwell_name), index=False)



