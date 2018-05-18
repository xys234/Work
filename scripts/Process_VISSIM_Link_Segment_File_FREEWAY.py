
# coding: utf-8

# In[1]:

import csv
import numpy as np
import pandas as pd

import sys, os

# ### INPUTS

# In[2]:

MPR = int(sys.argv[1])
RESULTS_FOLDER = r"L:\DCS\Projects\_Legacy\CAV\Global Challenge\CAV-IMPACT\Technical\Models\VISSIM\Freeway_Results"
LINK_SEG_DATA = "_Link Segment Results_010.att"
LINK_FILE_NAME="CAV_VISSIM_Links.csv"

MULTI_SAMPLE=False

# Derived Inputs
RUN_NAME="M" + str(MPR)
EST_FILE_NAME=RUN_NAME+"_EST"



# In[3]:

# All results for an MPR scenario
LOADS = [RESULTS_FOLDER + "\\"  + str(MPR) + "%" + "\\" + "Load-" + str(i) + "\\" + "Load-" + str(i) + LINK_SEG_DATA 
         for i in 1+np.arange(10)]


# #### Read the Links

# In[4]:

Links = pd.read_csv(LINK_FILE_NAME, sep=",",  
                          dtype={
                                 "Link":np.int16,
                                 "LinkType":str,
                                 "NumLanes":np.int8,
                                 "Length":np.float32,
                                 "IsConn":np.int8,
                                 "FT":str
                          }
                         )
dict_links = Links.set_index("Link").T.to_dict(orient='list')


# In[5]:

def get_link_attribute(Links, link, attr):
    '''
        Link attribute selector.
        Links: a pandas dataframe contains link attributes
        link: a link
        attr: a string for attr
        
        Sample Link file
        
        {
             1: ['5: Urban-Mixed', 2, 480.73590087890625, 0, 'Connector'],
             2: ['5: Urban-Mixed', 2, 491.6012878417969, 0, 'Connector'],
             3: ['5: Urban-Mixed', 2, 493.388427734375, 0, 'Connector'],
        }
    
    '''
    selector = {
                  "LinkType":0,
                  "NumLanes":1,
                  "Length":2,
                  "IsConn":3,
                  "FT":4
                }
    
    return(Links[link][selector[attr]])
    


# In[6]:

def p2f(x):
    if x!="":
        return float(x.strip('%'))/100
    else:
        return(0.0)


# In[7]:

def read_one_run(FILE_NAME, skiprows=18, filetype="LINK_SEG"):
    if filetype=="LINK_SEG":
        link_seg = pd.read_csv(FILE_NAME, sep=";", skiprows=skiprows, 
                              converters={
                                     0:str(),
                                     3:float(),
                                     4:p2f,
                                     5:float(),
                                     6:float()
                              }
                             )
        
    # rename the column
    link_seg = link_seg.rename(columns={ 
        link_seg.columns[0]: "SIMRUN",
        link_seg.columns[3]: "DENSITY",
        link_seg.columns[4]: "DELAYREL",
        link_seg.columns[5]: "SPEED",
        link_seg.columns[6]: "VOLUME"
    })
    return link_seg


# In[8]:

# Read the link segment data
df_link_seg_data = [read_one_run(f) for f in LOADS]


# In[9]:

result_link_seg = pd.concat(df_link_seg_data, keys=np.arange(len(df_link_seg_data))+1, names=['Load']).reset_index().drop("level_1", axis=1)


# In[10]:

# Process ONLY the average data
result_link_seg = result_link_seg[result_link_seg.SIMRUN=="AVG"].reset_index().drop("index", axis=1)


# #### Data Cleaning

# In[13]:

# Set speed = 0 if density = 0 or volume = 0
result_link_seg.loc[(result_link_seg.DENSITY == 0) | (result_link_seg.VOLUME == 0), "SPEED"] = 0.0


# In[14]:

# Split the link evaluation segments
split_link_seg = lambda x: pd.Series([int(i) for i in x.split('-')])
result_link_seg[['LINK','SEGA', 'SEGB']] = result_link_seg['LINKEVALSEGMENT'].apply(split_link_seg)


# In[15]:

# Split the time stamps
split_time_int = lambda x: pd.Series([int(i) for i in x.split('-')])
result_link_seg[['TIMEA','TIMEB']] = result_link_seg['TIMEINT'].apply(split_time_int)


# In[16]:

# Get lane flow and lane density
get_lanes =lambda x: get_link_attribute(dict_links, link=x, attr="NumLanes")
result_link_seg['LANES'] = result_link_seg['LINK'].apply(get_lanes)
result_link_seg['LANEFLOW'] = result_link_seg.VOLUME / result_link_seg.LANES
result_link_seg['LANEDENSITY'] = result_link_seg.DENSITY / result_link_seg.LANES


# In[17]:

# Get facility type
get_ft =lambda x: get_link_attribute(dict_links, link=x, attr="FT")
result_link_seg['FT'] = result_link_seg['LINK'].apply(get_ft)

# save the data for later 
result_link_seg.to_csv("Link_Seg_Data_FREEWAY"+"_"+RUN_NAME+".csv", header=True, index=False)

# In[18]:

# Only freeway but not connectors or ramps
result_link_seg = result_link_seg[result_link_seg.LINK.isin([10, 11, 17])].reset_index(drop=True)

if MULTI_SAMPLE:
	for s in np.arange(10)+1:
		result_link_seg_sample = result_link_seg.sample(10000, random_state=s)
		with open(EST_FILE_NAME+"_"+str(s)+".dat", 'wb') as csvfile:
			csvfile.writelines("VISSIM CAV LINK SEGMENT DATA -- "+RUN_NAME+"\r\n")
			csvfile.writelines(str(result_link_seg_sample.shape[0])+"\t1.000\t1.600\t0.625"+"\r\n")
			writer = csv.writer(csvfile, delimiter='\t', dialect='excel', lineterminator="\r\n")
			for i in result_link_seg_sample.loc[:,["LANEFLOW", "SPEED", "LANEDENSITY"]].values:
				writer.writerow(i, )
else:
	result_link_seg_sample = result_link_seg.sample(10000)
	with open(EST_FILE_NAME+".dat", 'wb') as csvfile:
		csvfile.writelines("VISSIM CAV LINK SEGMENT DATA -- "+RUN_NAME+"\r\n")
		csvfile.writelines(str(result_link_seg_sample.shape[0])+"\t1.000\t1.600\t0.625"+"\r\n")
		writer = csv.writer(csvfile, delimiter='\t', dialect='excel', lineterminator="\r\n")
		for i in result_link_seg_sample.loc[:,["LANEFLOW", "SPEED", "LANEDENSITY"]].values:
			writer.writerow(i, )


