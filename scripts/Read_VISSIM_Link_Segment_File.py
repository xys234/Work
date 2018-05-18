
# coding: utf-8

# In[1]:

import csv
import numpy as np
import pandas as pd

import sys, os

# ### INPUTS

# In[2]:

MPR = int(sys.argv[1])
RESULTS_FOLDER = r"L:\DCS\Projects\_Legacy\CAV\Global Challenge\CAV-IMPACT\Technical\Models\VISSIM\Arterial_Results"
LINK_SEG_DATA = "_Link Segment Results_010.att"
LINK_FILE_NAME="CAV_VISSIM_Links.csv"
FT="ARTERIAL"


# Derived Inputs
RUN_NAME="M" + str(MPR)
EST_FILE_NAME=RUN_NAME+"_EST_adv" + FT



# In[3]:

# All results for an MPR scenario
LOADS = [RESULTS_FOLDER + "\\"  + str(MPR) + "%" + "\\" + "Load-" + str(i) + "\\" + "Load-" + str(i) + LINK_SEG_DATA 
         for i in 1+np.arange(10)]
OUTPUTS = ["Load-" + str(i) + LINK_SEG_DATA for i in 1+np.arange(10)]

# #### Read the Links
SKIP_LINES = 18
for l, o in zip(LOADS, OUTPUTS):
	
	# Delete the file if exists
	if os.path.isfile(o):
		os.remove(o)
	
	with open(o, 'wb') as output:
		with open(l, 'rb') as input:
			j = 0
			for line in input:
				if(j == SKIP_LINES):
					output.writelines(line)
				if(j > SKIP_LINES):
					tokens = line.split(";")
					if(tokens[0] == "AVG"):
						output.writelines(line)
				j += 1
					




