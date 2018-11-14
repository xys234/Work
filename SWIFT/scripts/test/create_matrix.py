import h5py
import numpy as np

def create_matrix(file, matrix_name, size):

    data = np.random.random(size=size)

    f = h5py.File(file, 'w')
    grp = f.create_group('matrices')
    grp.create_dataset(name=matrix_name, data=data)



if __name__=='__main__':
    file = r'C:\Projects\Repo\Work\SWIFT\scripts\test\test.omx'
    matrix_name = 'amhnwai3a2'
    size = (3,3)
    create_matrix(file, matrix_name, size)