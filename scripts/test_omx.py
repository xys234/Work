'''

The script tests using PyTable APIs to read OMX file
The OMX APIs assume the group name is "data". This is too restrictive.

to-do:
test writing numpy arrays to matrices


'''

import openmatrix as omx
import numpy as np
import time

print("Open Matrix version = {0}".format(omx.__version__))

MATRIX_FILE_PATH = r'L:\DCS\Projects\_Legacy\60563434_SWIFT\400_Technical\410 Transportation Modeling\DATA\H-GAC\Trip Tables\OD\Y2017_OD_TOD\OD AM3HR HBNW Vehicles.OMX'

matrix_od = omx.open_file(MATRIX_FILE_PATH,'r')

## get all groups in a file, i.e. the root node
groups 		=  matrix_od.root._v_groups					# This is a Pytable group
groups_keys =  matrix_od.root._v_groups.keys()			# This is a Python dictionary view object, dict_keys
print(type(groups_keys))
print("is matrices in the group: {0}".format("matrices" in groups_keys))


## get the list of matrices within a group; check if a matrix exists
matrices 		= matrix_od.root._f_get_child(list(groups_keys)[0])
matrices_keys 	= matrices._v_children.keys()
print(matrices_keys)														# This is a Python dictionary view object, dict_keys
print("is amhnwai3a2 in the group: {0}".format("amhnwai3a2" in matrices_keys))

## Check the shape of an individual matrix
m = matrices._f_get_child(list(matrices_keys)[0])
print(list(matrices_keys)[0])
print(type(m))
print("matrix shape is {0}".format(m.shape))
print("matrix size in memory = {0:.1f} M".format(m.size_in_memory/(1024*1024)))
print("matrix size in disk = {0:.1f} M".format(m.size_on_disk/(1024*1024)))

## Get the numpy array, 0.8 seconds
start_time = time.time()
m_np = m.read()
print(type(m_np))
print("--- Convert to numpy array in %s seconds ---" % (time.time() - start_time))
print(np.sum(np.sum(m_np)))
# matrix_od.close()

myfile = omx.open_file('myfile.omx','w')   # use 'a' to append/edit an existing file

# Write to the file. The OMX viewer only works when open the file in read-only mode
m_np = m_np + 1.0
print(type(m_np))
# print(np.sum(np.sum(m_np)))
# ones = np.ones((5263, 5263))
# myfile['m1'] = ones
myfile['m1'] = m_np				# The default node name is "data"
myfile.close()
