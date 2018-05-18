
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

line_id  = int(sys.argv[2])
start_id = int(sys.argv[3])
end_id   = int(sys.argv[4])


# ## Read the data

# In[2]:

df = pd.read_table(os.path.join(drive, path_and_file),sep=';',skiprows=16)


# Drop all PTSTOP with NaN
df2 = df.dropna(axis=0)

# ## Extract the arrival and departure vehicle



# Group-by 'NO','PTLINE', 'PTSTOP', which uniquely identify each record
# select the min simsec and max simsec
df2 = df2[(df2['PTLINE']==line_id) & ((df2['PTSTOP']==start_id) | (df2['PTSTOP']==end_id))]
df2_group = df2.groupby(['NO','PTLINE', 'PTSTOP'])



df2_head = df2_group.head(1)
df2_tail = df2_group.tail(1)


merged = pd.merge(df2_head, df2_tail, left_on = ['NO','PTLINE', 'PTSTOP'], right_on=['NO','PTLINE', 'PTSTOP'], suffixes=['_min','_max'])
merged_sort = merged.sort_values(by=['PTLINE', 'NO', 'SIMSEC_min'])


start_stop = merged_sort[(merged_sort['PTLINE']==line_id) & (merged_sort['PTSTOP']==start_id)]
start_stop = start_stop[['PTLINE','NO','PTSTOP','SIMSEC_min','SIMSEC_max']] 

end_stop = merged_sort[(merged_sort['PTLINE']==line_id) & (merged_sort['PTSTOP']==end_id)]
end_stop = end_stop[['PTLINE','NO','PTSTOP','SIMSEC_min','SIMSEC_max']]


merged_start_end = pd.merge(start_stop, end_stop, left_on = ['NO','PTLINE'], right_on=['NO','PTLINE'], suffixes=['_start','_end'])
merged_start_end['TT'] = merged_start_end['SIMSEC_min_end'] - merged_start_end['SIMSEC_max_start']

output_name = drive+direc+'/'+scen+"_station_time.csv"
merged_start_end.to_csv(os.path.normpath(output_name), index=False)
