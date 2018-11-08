

from enum import IntEnum

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



KEY_DB = {
        # Key                       # Value_Type                         # Value_Default
        'TITLE':                    (Key_Value_Types.STRING,             None),
        'REPORT_FILE':              (Key_Value_Types.STRING,             None),

        'TRIP_TABLE_FILE':          (Key_Value_Types.STRING,             None),
        'TRIP_PURPOSE_CODE':        (Key_Value_Types.INTEGER,            1),
        'VALUE_OF_TIME':            (Key_Value_Types.FLOAT,              10.0),
        'VEHICLE_CLASS':            (Key_Value_Types.INTEGER,            Codes_Vehicle_Class.UE),
        'VEHICLE_TYPE':             (Key_Value_Types.INTEGER,            1),
        'VEHICLE_OCCUPANCY':        (Key_Value_Types.INTEGER,            Codes_Vehicle_Occupancy.SOV),
        'VEHICLE_GENERATION_MODE':  (Key_Value_Types.INTEGER,            1),
        'NUMBER_OF_STOPS':          (Key_Value_Types.INTEGER,            1),
        'ENROUTE_INFO':             (Key_Value_Types.INTEGER,            0),
        'COMPLIANCE_RATE':          (Key_Value_Types.FLOAT,              0.0),
        'EVACUATION_FLAG':          (Key_Value_Types.INTEGER,            0),
        'ACTIVITY_DURATION':        (Key_Value_Types.FLOAT,              0.0),
        'ARRIVAL_TIME':             (Key_Value_Types.FLOAT,              0.0)
}




