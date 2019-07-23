"""

This script reads a csv toll records and write out a DynusT toll file


"""

import sys

def write_formatted_tolls(csv_toll_file, output_toll_file):

    fmt = "{:7d} {:7d} {:7d} {:5d} {:5d} {:5d} "
    converter = [int, int, int, int, int, int]
    records = []
    number_of_tolls = 6

    with open(csv_toll_file, mode='r') as input_toll:
        r = 0
        for line in input_toll:
            r += 1
            sys.stdout.write("\rProcessing {:d} record".format(r))
            data = line.split(',')
            data = [f.strip() for f in data]
            if r == 1:
                number_of_tolls = len(data) - len(fmt.split())
                fmt = fmt + " ".join(["{:8.3f}"] * number_of_tolls) + " \n"
                converter.extend([float]*number_of_tolls)
            data = [c(f) for c, f in zip(converter, data)]
            records.append(tuple(data))

    with open(output_toll_file, mode='w') as output_toll:
        header_1 = " ".join(["10.000"]*number_of_tolls) + " \n"
        header_2 = "15.000 {:d}\n".format(len(records))
        output_toll.write(header_1)
        output_toll.write(header_2)
        for record in records:
            output_toll.write(fmt.format(*record))


if __name__ == '__main__':
    import os
    project_dir = r"L:\DCS\Projects\_Legacy\60563434_SWIFT\400_Technical\Houston_8_County_DTA_CalibValid\_dst\HGAC_45_N2"
    input_toll_file = os.path.join(project_dir, "toll.csv")
    output_toll_file = os.path.join(project_dir, "Toll.dat")
    write_formatted_tolls(input_toll_file, output_toll_file)
