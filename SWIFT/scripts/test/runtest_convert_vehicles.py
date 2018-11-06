import h5py
import numpy as np
import os
from convert_demand import to_vehicles, write_vehicles
from parse_origins import parse_origins
from dt_generator import DTGenerator


def create_test_data(filename, matrix_name, dims=(10,10)):
    with h5py.File(filename, "w") as f:
        group = f.create_group('matrices')
        data = np.random.randint(1, 10, size=dims)
        print("Total number of input vehicles = {0:d}".format(data.sum()))
        mat = group.create_dataset(matrix_name, dims, dtype='i', data=data)




if __name__ == '__main__':
    folder = '..\..\data\Dynus_T'
    matrix_test = os.path.join(folder, 'test.omx')
    matrix_name = "amhbwai3a2"
    create_test_data(matrix_test, matrix_name)


    matrices_am = ["OD AM3HR HBNW Vehicles", "OD AM3HR HBW Vehicles", "OD AM3HR NHB Vehicles", "OD AM3HR Other VEHICLEs"]
    matrices_md = ["OD MD6HR HBNW Vehicles", "OD MD6HR HBW Vehicles", "OD MD6HR NHB Vehicles", "OD MD6HR Other VEHICLEs"]
    matrices_pm = ["OD PM4HR HBNW Vehicles", "OD PM4HR HBW Vehicles", "OD PM4HR NHB Vehicles", "OD PM4HR Other VEHICLEs"]
    matrices_ov = ["OD OV8HR HBNW Vehicles", "OD OV8HR HBW Vehicles", "OD OV8HR NHB Vehicles", "OD OV8HR Other VEHICLEs"]

    purp = ["hnw", "hbw", "nho", "nhw"]
    periods = ["am", "md", "pm", "ov"]
    periods_other = ["AM3", "MD6", "PM4", "OV8"]

    # right open; day starts at 0
    period_def = {'am': [(6, 9)], 'md': [(9,15)], 'pm': [(15,19)], 'ov': [(0, 6), (19, 24)]}

    # tabs = [
    #         ["i12da", "i3da", "i45da",                  # HBNW-DA
    #          "i12a2", "ai3a2", "i45a2",                 # HBNW-S2
    #          "i12a3", "i3a3", "i45a3"],                 # HBNW-S3
    #         ["i1da", "i2da", "i3da", "i4da", "i5da",    # HBW-DA
    #          "i12a2", "ai3a2", "i45a2",                 # HBW-S2
    #          "i12a3", "i3a3", "i45a3"],                 # HBW-S3
    #         ["dai12", "dai3", "dai453",                 # NHO-DAN
    #          "s2i12", "s2i3", "s2i45",                  # NHO-S2
    #          "s3i12", "s3i3", "s3i45",                  # NHO-S3
    #          "dai1", "dai2", "dai3", "dai4", "dai5",    # NHW-DA
    #          "s2i12", "s2i3", "s2i45",                  # NHW-S2
    #          "s3i12", "s3i3", "s3i45"],                 # NHW-S3
    #        ["Cargo", "Serv", "taxi", "exta"]            # OTHER
    #        ]

    hours = np.arange(0, 25, 1)
    share = [0.0010, 0.0010, 0.0010, 0.0020, 0.0050, 0.0150, 0.0501, 0.1022, 0.0581, 0.0411, 0.0481, 0.0571, 0.0571,
             0.0521, 0.0651, 0.0982, 0.0852, 0.0832, 0.0651, 0.0451, 0.0301, 0.0220, 0.0100, 0.0050, 0]
    points = 600 * 24
    dt_generator = DTGenerator(x=hours, prob=share, interp=points, seed=42)

    vots = {"hbwi1da": 9.6, "hbwi2da": 15.04, "hbwi3da": 20.48, "hbwi4da": 27.52, "hbwi5da": 37.12, "hbwi12a2": 21.56,
           "hbwai3a2": 35.84, "hbwi45a2": 56.56, "hbwi12a3": 30.8, "hbwi3a3": 51.2, "hbwi45a3": 80.8,
           "hnwi12da": 7.03, "hnwi3da": 13.44, "hnwi45da": 23.65, "hnwi12a2": 12.3, "hnwai3a2": 23.52,
           "hnwi45a2": 41.39,"hnwi12a3": 17.57, "hnwi3a3": 33.6, "hnwi45a3": 59.12,
           "nhodai12": 7.03, "nhodai3": 13.44, "nhodai453": 23.65, "nhos2i12": 12.3, "nhos2i3": 23.52,
           "nhos2i45": 41.39, "nhos3i12": 17.57, "nhos3i3": 33.6, "nhos3i45": 59.12,
           "nhwdai1": 9.6, "nhwdai2": 15.04, "nhwdai3": 20.48, "nhwdai4": 27.52, "nhwdai5": 37.12, "nhws2i12": 21.56,
           "nhws2i3": 35.84, "nhws2i45": 56.56, "nhws3i12": 30.8, "nhws3i3": 51.2, "nhws3i45": 80.8,
           "Cargo": 64.0, "Serv": 40.0, "taxi": 18.94, "exta": 18.94}

    dynust_folder = '..\..\data\Dynus_T'
    DynusT_origin_file = os.path.join(dynust_folder, 'origin.dat')

    origins = parse_origins(DynusT_origin_file)
    vehicle_file_path = os.path.join(dynust_folder, 'vehicles.dat')

    vehicle_pool = to_vehicles(matrix_test, dt_generator, vots, period_def, origins)
    write_vehicles(vehicle_file_path, vehicle_pool)

