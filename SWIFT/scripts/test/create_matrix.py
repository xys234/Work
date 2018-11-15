import h5py
import numpy as np

def create_matrix(file, matrix_name, size, unity=False):

    if not unity:
        data = np.random.random(size=size)
    else:
        data = np.ones(size, dtype=np.int8)

    f = h5py.File(file, 'w')
    grp = f.create_group('matrices')
    grp.create_dataset(name=matrix_name, data=data, dtype=data.dtype)



if __name__=='__main__':
    file = r'C:\Projects\Repo\Work\SWIFT\scripts\test\test.omx'
    matrix_name = 'amhbwi1da'
    # size = (50,50)
    # size = (1000,1000)
    size = (5263,5263)
    create_matrix(file, matrix_name, size, unity=False)