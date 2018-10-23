"""

Parse Dynus-T origin file usually named "origin.dat"


1    3    0
307506  25490   0
25491   79273   0
274990  279788  0

Zone ID, # of generation links, Vehicle generation weight switch (0 means equal distribution)


"""

import os


def parse_origins(origin_file, zones=5263):
    """

    :param origin_file:
    :return: an dict zone -> [(from_node, to_node, weight)]
    """

    origins = {}
    with open(origin_file, 'r') as dy_origin_file:
        total_num_origins = 0
        pos = 0
        zone = num_origins = -1
        for j, line in enumerate(dy_origin_file):
            record = line.strip().split()
            if j == 0 or j == pos:
                zone, num_origins = int(record[0]), int(record[1])
                pos = pos + num_origins + 1
            else:
                total_num_origins += 1
                from_node, to_node, weight = int(record[0]), int(record[1]), int(record[2])
                if zone not in origins:
                    origins[zone] = [(from_node, to_node, weight)]
                else:
                    origins[zone].append((from_node, to_node, weight))
    print("Number of Dynus-T Origin Records = {0:d}".format(total_num_origins))
    return origins



if __name__=='__main__':
    scen_dir = r"Q:\Houston8_DTA_Interim\_dst\HGAC_16a"
    origin_file = os.path.join(scen_dir, "origin.dat")
    origins = parse_origins(origin_file)
    print('Done')





