

from enum import IntEnum
from collections import namedtuple


class Codes_Key_Thresholds(IntEnum):
    COMMON_KEY = 19
    NETWORK_KEY = 99
    SYSTEM_KEY = 499

class Codes_Execution_Status(IntEnum):
    OK = 0
    ERROR = 1

class Codes_Vehicle_Class(IntEnum):
    HISTORICAL      = 1
    SYSTEM_OPTIMAL  = 2
    UE              = 3
    ENROUTE_INFO    = 4
    PRETRIP_INFO    = 5

    # todo: Code checking and conversion


class Codes_Vehicle_Type(IntEnum):
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
    TIME_RANGE = 5      # comma-delimited integer range like 0..6, 19..24 or 6..9
    FILE = 6
    SET = 7             # comma-delimited integers, 1, 3, 4..5 or 1..3,


class Key_Group_Types(IntEnum):
    NOGROUP = 0
    GROUP = 1

# Output file always starts with "NEW_" and ends with "_FILE"
Key_Info = namedtuple('Key_Info', ('value_type', 'value_default', 'group_type', 'key_order'))



KEY_DB = {
    # Key                       # Value_Type                  # Default_input_value

    'INVALID_KEY':              Key_Info(Key_Value_Types.STRING,      None,              Key_Group_Types.NOGROUP, 0),

    'TITLE':                    Key_Info(Key_Value_Types.STRING,      None,              Key_Group_Types.NOGROUP, 1),
    'REPORT_FILE':              Key_Info(Key_Value_Types.FILE,        None,              Key_Group_Types.NOGROUP, 2),
    'PROJECT_DIRECTORY':        Key_Info(Key_Value_Types.STRING,      None,              Key_Group_Types.NOGROUP, 3),
    'RANDOM_SEED':              Key_Info(Key_Value_Types.INTEGER,     0,                 Key_Group_Types.NOGROUP, 4),

    'NUMBER_OF_ZONES':          Key_Info(Key_Value_Types.INTEGER,     None,     Key_Group_Types.NOGROUP, 20),
    'ORIGIN_FILE':              Key_Info(Key_Value_Types.FILE,        None,     Key_Group_Types.NOGROUP, 21),
    'NEW_VEHICLE_ROSTER_FILE':  Key_Info(Key_Value_Types.FILE,        None,     Key_Group_Types.NOGROUP, 22),
    'TRAJECTORY_FILE':          Key_Info(Key_Value_Types.FILE,        None,     Key_Group_Types.NOGROUP, 23),
    'TRAJECTORY_FORMAT':        Key_Info(Key_Value_Types.STRING,      "BINARY", Key_Group_Types.NOGROUP, 24),
    'NEW_TRAJECTORY_FILE':      Key_Info(Key_Value_Types.FILE,        None,     Key_Group_Types.NOGROUP, 25),
    'NEW_TRAJECTORY_FORMAT':    Key_Info(Key_Value_Types.STRING,      "BINARY", Key_Group_Types.NOGROUP, 25),
    'TRIP_ADJUSTMENT_FILE':     Key_Info(Key_Value_Types.FILE,        None,     Key_Group_Types.NOGROUP, 26),
    'NEW_VEHICLE_MAP_FILE':     Key_Info(Key_Value_Types.FILE,        None,     Key_Group_Types.NOGROUP, 27),
    'NEW_FLAT_TRIP_FILE':       Key_Info(Key_Value_Types.FILE,        None,     Key_Group_Types.NOGROUP, 28),


    'TRIP_TABLE_FILE':          Key_Info(Key_Value_Types.FILE,        None,    Key_Group_Types.GROUP, 100),
    'MATRIX_NAME':              Key_Info(Key_Value_Types.STRING,      None,    Key_Group_Types.GROUP, 101),
    'TIME_PERIOD_RANGE':        Key_Info(Key_Value_Types.TIME_RANGE,  "0..24", Key_Group_Types.GROUP, 102),
    'DIURNAL_FILE':             Key_Info(Key_Value_Types.FILE,        None,      Key_Group_Types.GROUP, 103),
    'TRIP_PURPOSE_CODE':        Key_Info(Key_Value_Types.INTEGER,     1,       Key_Group_Types.GROUP, 104),
    'VALUE_OF_TIME':            Key_Info(Key_Value_Types.FLOAT,       10.0,    Key_Group_Types.GROUP, 105),
    'VEHICLE_CLASS':            Key_Info(Key_Value_Types.INTEGER,     Codes_Vehicle_Class.UE, Key_Group_Types.GROUP, 106),
    'VEHICLE_TYPE':             Key_Info(Key_Value_Types.INTEGER,     Codes_Vehicle_Type.SOV, Key_Group_Types.GROUP, 107),
    'VEHICLE_OCCUPANCY':        Key_Info(Key_Value_Types.INTEGER,     1,  Key_Group_Types.GROUP, 108),
    'VEHICLE_GENERATION_MODE':  Key_Info(Key_Value_Types.INTEGER,     1,    Key_Group_Types.GROUP, 109),
    'INDIFFERENCE_BAND':        Key_Info(Key_Value_Types.FLOAT,       0.0,  Key_Group_Types.GROUP, 110),
    'NUMBER_OF_STOPS':          Key_Info(Key_Value_Types.INTEGER,     1,    Key_Group_Types.GROUP, 111),
    'ENROUTE_INFO':             Key_Info(Key_Value_Types.INTEGER,     0,    Key_Group_Types.GROUP, 112),
    'COMPLIANCE_RATE':          Key_Info(Key_Value_Types.FLOAT,       0.0,  Key_Group_Types.GROUP, 113),
    'EVACUATION_FLAG':          Key_Info(Key_Value_Types.INTEGER,     0,    Key_Group_Types.GROUP, 114),
    'ACTIVITY_DURATION':        Key_Info(Key_Value_Types.FLOAT,       0.0,  Key_Group_Types.GROUP, 115),
    'ARRIVAL_TIME':             Key_Info(Key_Value_Types.FLOAT,       0.0,  Key_Group_Types.GROUP, 116),
    'WAIT_TIME':                Key_Info(Key_Value_Types.FLOAT,       0.0,  Key_Group_Types.GROUP, 117),
    'INITIAL_GAS':              Key_Info(Key_Value_Types.FLOAT,       0.0,  Key_Group_Types.GROUP, 118),
    'VEHICLE_ROSTER_FILE':      Key_Info(Key_Value_Types.FILE,        None, Key_Group_Types.GROUP, 119),
    'START_TRIP_NUMBER':        Key_Info(Key_Value_Types.INTEGER,     1,    Key_Group_Types.NOGROUP, 120),
    'PERIOD_MAP_FILE':          Key_Info(Key_Value_Types.FILE,        None, Key_Group_Types.NOGROUP, 121),
    'INCOME_MAP_FILE':          Key_Info(Key_Value_Types.FILE,        None, Key_Group_Types.NOGROUP, 122),
    'ZONE_MAP_FILE':            Key_Info(Key_Value_Types.FILE,        None, Key_Group_Types.NOGROUP, 123),
    'NEW_PROBLEM_FILE':         Key_Info(Key_Value_Types.FILE,        None, Key_Group_Types.NOGROUP, 124),
    'SELECTION_FILE':           Key_Info(Key_Value_Types.FILE,        None, Key_Group_Types.NOGROUP, 125),
    'SELECTION_FORMAT':         Key_Info(Key_Value_Types.STRING,      "COMMA_DELIMITED", Key_Group_Types.NOGROUP, 126),
}
if __name__ == '__main__':
    pass
