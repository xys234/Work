

from enum import IntEnum
from collections import namedtuple

class Codes_Vehicle_Class(IntEnum):
    HISTORICAL      = 1
    SYSTEM_OPTIMAL  = 2
    UE              = 3
    ENROUTE_INFO    = 4
    PRETRIP_INFO    = 5

    # todo: Code checking and conversion


class Codes_Vehicle_Occupancy(IntEnum):
    SOV = 0
    TRUCK = 1
    HOV = 2


class Control_Key_Types(IntEnum):
    REQUIRED = 1
    OPTIONAL = 0


class Key_Value_Types(IntEnum):
    INTEGER = 1
    FLOAT = 2
    BOOLEAN = 3
    STRING = 4
    RANGES = 5      # comma


class Key_Group_Types(IntEnum):
    NOGROUP = 0
    GROUP = 1



Key_Info = namedtuple('Key_Info', ('value_type', 'value_default', 'group_type'))
KEY_DB = {
        # Key                       # Value_Type                  # Value_Default
        'TITLE':                    Key_Info(Key_Value_Types.STRING,      None,              Key_Group_Types.NOGROUP),
        'REPORT_FILE':              Key_Info(Key_Value_Types.STRING,      None,              Key_Group_Types.NOGROUP),
        'PROJECT_DIRECTORY':        Key_Info(Key_Value_Types.STRING,      None,              Key_Group_Types.NOGROUP),

        'TRIP_TABLE_FILE':          Key_Info(Key_Value_Types.STRING,      None,                         Key_Group_Types.GROUP),
        'MATRIX_NAME':              Key_Info(Key_Value_Types.STRING,      None,                         Key_Group_Types.GROUP),
        'TIME_PERIOD_RANGE':        Key_Info(Key_Value_Types.RANGES,      "0..24",                      Key_Group_Types.GROUP),
        'DIURNAL_FILE':             Key_Info(Key_Value_Types.STRING,      None,                         Key_Group_Types.GROUP),
        'TRIP_PURPOSE_CODE':        Key_Info(Key_Value_Types.INTEGER,     1,                            Key_Group_Types.GROUP),
        'VALUE_OF_TIME':            Key_Info(Key_Value_Types.FLOAT,       10.0,                         Key_Group_Types.GROUP),
        'VEHICLE_CLASS':            Key_Info(Key_Value_Types.INTEGER,     Codes_Vehicle_Class.UE,       Key_Group_Types.GROUP),
        'VEHICLE_TYPE':             Key_Info(Key_Value_Types.INTEGER,     1,                            Key_Group_Types.GROUP),
        'VEHICLE_OCCUPANCY':        Key_Info(Key_Value_Types.INTEGER,     Codes_Vehicle_Occupancy.SOV,  Key_Group_Types.GROUP),
        'VEHICLE_GENERATION_MODE':  Key_Info(Key_Value_Types.INTEGER,     1,    Key_Group_Types.GROUP),
        'INDIFFERENCE_BAND':        Key_Info(Key_Value_Types.FLOAT,       0.0,  Key_Group_Types.GROUP),
        'NUMBER_OF_STOPS':          Key_Info(Key_Value_Types.INTEGER,     1,    Key_Group_Types.GROUP),
        'ENROUTE_INFO':             Key_Info(Key_Value_Types.INTEGER,     0,    Key_Group_Types.GROUP),
        'COMPLIANCE_RATE':          Key_Info(Key_Value_Types.FLOAT,       0.0,  Key_Group_Types.GROUP),
        'EVACUATION_FLAG':          Key_Info(Key_Value_Types.INTEGER,     0,    Key_Group_Types.GROUP),
        'ACTIVITY_DURATION':        Key_Info(Key_Value_Types.FLOAT,       0.0,  Key_Group_Types.GROUP),
        'ARRIVAL_TIME':             Key_Info(Key_Value_Types.FLOAT,       0.0,  Key_Group_Types.GROUP),
        'WAIT_TIME':                Key_Info(Key_Value_Types.FLOAT,       0.0,  Key_Group_Types.GROUP),
        'INITIAL_GAS':              Key_Info(Key_Value_Types.FLOAT,       0.0,  Key_Group_Types.GROUP)
}



##### -------------  Utility ----------------- ####
def parse_time_range(time_range):
    """

    :param time_range: parse comma-separated ranges like "0..6, 15..19"
    :type  str
    :return: "0..6, 15..19" is parsed into [(0, 6), (15, 19)]
    """

    if not isinstance(time_range, str):
        raise TypeError("Time range must be a string")

    parts = time_range.split(",")
    ranges = []

    for part in parts:
        if part.find("..") < 0:
            raise ValueError("Time range must have both start and end times. Input is %s" % part)
        else:
            start_time, end_time = part.split("..")
            ranges.append((float(start_time), float(end_time)))

    return ranges


if __name__=='__main__':
    time_range = "0..6, 19..24"
    print(parse_time_range(time_range))

    time_range = "15..19"
    print(parse_time_range(time_range))

    # time_range = 3
    # print(parse_time_range(time_range))

    time_range = "17, 18"
    print(parse_time_range(time_range))