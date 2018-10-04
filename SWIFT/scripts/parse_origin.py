"""

Parse Dynus-T origin file usually named "origin.dat"


1    3    0
307506  25490   0
25491   79273   0
274990  279788  0

Zone ID, # of generation links, Vehicle generation weight switch (0 means equal distribution)


"""

import os
import h5py
import numpy as np


def parse_origins(origin_file, zones=5263):
    """

    :param origin_file:
    :return: an numpy array
    """

    origins = np.zeros((zones+1,200,2),dtype='i')

    f = open(origin_file, 'r')
    data = f.readlines()
    f.close()

    n = len(data)
    k = 0

    while k < n:
        s = data[k].split()
        k += 1

        zon = int(s[0])
        x = int(s[1])

        origins[zon, 0, 0] = x

        for i in range(x):
            s = data[k].split()
            a = int(s[0])
            b = int(s[1])
            j = i + 1

            try:
                origins[zon, j, 0] = a
                origins[zon, j, 1] = b
            except:
                print(zon, i, a)

            k += 1

    return origins



if __name__=='__main__':
    scen_dir = r"Q:\Houston8_DTA_Interim\_dst\HGAC_16a"
    origin_file = os.path.join(scen_dir, "origin.dat")
    # print(os.path.abspath(origin_file))
    parse_origins(origin_file)






