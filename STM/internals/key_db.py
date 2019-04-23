from enum import Enum, IntEnum, unique
from collections import namedtuple


KeyInfo = namedtuple('KeyInfo', ('value_type', 'default', 'order', 'group', 'help'))


@unique
class KeyValueTypes(IntEnum):
    INTEGER = 0
    FLOAT = 1
    STRING = 2
    FILE = 3
    INTEGER_LIST = 4
    FLOAT_LIST = 5
    TIME_RANGE = 6
    BOOLEAN = 7


@unique
class KeyGroupTypes(IntEnum):
    SINGLE = 0
    GROUP = 1


@unique
class Offset(IntEnum):
    EXECUTION_KEYS_OFFSET = 0
    NETWORK_KEYS_OFFSET = 10
    SETTINGS_KEYS_OFFSET = 100


@unique
class Help(Enum):
    NO_HELP = ''
    FILE_HELP = '[PROJECT_DIRECTORY]filename'
    RANGE_HELP = '1, 2, 3..10'
    INTEGER_LIST_HELP = '1, 2, 3'
    FLOAT_LIST_HELP = '0.1, 0.3, 0.5'


@unique
class VehicleClass(IntEnum):
    HISTORICAL = 1
    SYSTEM_OPTIMAL = 2
    UE = 3
    ENROUTE_INFO = 4
    PRETRIP_INFO = 5

    def __str__(self):
        return str(self.value)

@unique
class VehicleType(IntEnum):
    SOV = 0
    TRUCK = 1
    HOV = 2

    def __str__(self):
        return str(self.value)


SYSTEM_KEYS = {
    'TITLE':                    KeyInfo(KeyValueTypes.STRING,      '', Offset.EXECUTION_KEYS_OFFSET+1, KeyGroupTypes.SINGLE, Help.NO_HELP),
    'REPORT_FILE':              KeyInfo(KeyValueTypes.FILE,        '', Offset.EXECUTION_KEYS_OFFSET+2, KeyGroupTypes.SINGLE, Help.FILE_HELP),
    'PROJECT_DIRECTORY':        KeyInfo(KeyValueTypes.STRING,      './', Offset.EXECUTION_KEYS_OFFSET+3, KeyGroupTypes.SINGLE, Help.NO_HELP),
    'RANDOM_SEED':              KeyInfo(KeyValueTypes.INTEGER,     47,  Offset.EXECUTION_KEYS_OFFSET+4, KeyGroupTypes.SINGLE, Help.NO_HELP),
}

NETWORK_KEYS = {
    'NETWORK_FILE': KeyInfo(KeyValueTypes.FILE, '', Offset.NETWORK_KEYS_OFFSET + 1, KeyGroupTypes.SINGLE, Help.FILE_HELP),
    'ORIGIN_FILE': KeyInfo(KeyValueTypes.FILE, '', Offset.NETWORK_KEYS_OFFSET + 2, KeyGroupTypes.SINGLE, Help.FILE_HELP),
    'TRAJECTORY_FILE': KeyInfo(KeyValueTypes.FILE, '', Offset.NETWORK_KEYS_OFFSET + 3, KeyGroupTypes.SINGLE, Help.FILE_HELP),
    'TRAJECTORY_FORMAT': KeyInfo(KeyValueTypes.STRING, 'BINARY', Offset.NETWORK_KEYS_OFFSET + 4, KeyGroupTypes.SINGLE, Help.NO_HELP),
    'TRIP_TABLE_FILE': KeyInfo(KeyValueTypes.FILE, '', Offset.NETWORK_KEYS_OFFSET + 5, KeyGroupTypes.GROUP, Help.FILE_HELP),
    'NEW_VEHICLE_ROSTER_FILE': KeyInfo(KeyValueTypes.FILE, '', Offset.NETWORK_KEYS_OFFSET + 6, KeyGroupTypes.SINGLE, Help.FILE_HELP),
    'VEHICLE_ROSTER_FILE': KeyInfo(KeyValueTypes.FILE, '', Offset.NETWORK_KEYS_OFFSET + 7, KeyGroupTypes.GROUP, Help.FILE_HELP),
    'NEW_FLAT_TRIP_FILE': KeyInfo(KeyValueTypes.FILE, '', Offset.NETWORK_KEYS_OFFSET + 8, KeyGroupTypes.SINGLE, Help.FILE_HELP),
    'SELECTION_FILE': KeyInfo(KeyValueTypes.FILE, '', Offset.NETWORK_KEYS_OFFSET + 9, KeyGroupTypes.SINGLE, Help.FILE_HELP),
    'SELECTION_FORMAT': KeyInfo(KeyValueTypes.STRING, 'COMMA_DELIMITED', Offset.NETWORK_KEYS_OFFSET + 10, KeyGroupTypes.SINGLE, Help.FILE_HELP),

}

SETTINGS_KEYS = {
    'NUMBER_OF_ZONES': KeyInfo(KeyValueTypes.INTEGER, '', Offset.SETTINGS_KEYS_OFFSET + 1, KeyGroupTypes.SINGLE, Help.NO_HELP),
    'MATRIX_NAME': KeyInfo(KeyValueTypes.STRING, '', Offset.SETTINGS_KEYS_OFFSET + 2, KeyGroupTypes.GROUP, Help.NO_HELP),
    'TIME_PERIOD_RANGE': KeyInfo(KeyValueTypes.TIME_RANGE, '', Offset.SETTINGS_KEYS_OFFSET + 3, KeyGroupTypes.GROUP, Help.NO_HELP),
    'DIURNAL_FILE': KeyInfo(KeyValueTypes.FILE, '', Offset.SETTINGS_KEYS_OFFSET + 4, KeyGroupTypes.GROUP, Help.NO_HELP),
    'TRIP_PURPOSE_CODE': KeyInfo(KeyValueTypes.INTEGER, '', Offset.SETTINGS_KEYS_OFFSET + 5, KeyGroupTypes.GROUP, Help.NO_HELP),
    'VALUE_OF_TIME': KeyInfo(KeyValueTypes.FLOAT, '', Offset.SETTINGS_KEYS_OFFSET + 6, KeyGroupTypes.GROUP, Help.NO_HELP),
    'VEHICLE_OCCUPANCY': KeyInfo(KeyValueTypes.INTEGER, '', Offset.SETTINGS_KEYS_OFFSET + 7, KeyGroupTypes.GROUP, Help.NO_HELP),
    'VEHICLE_CLASS': KeyInfo(KeyValueTypes.INTEGER, VehicleClass.UE, Offset.SETTINGS_KEYS_OFFSET + 8, KeyGroupTypes.GROUP, Help.NO_HELP),
    'VEHICLE_TYPE': KeyInfo(KeyValueTypes.INTEGER, VehicleType.SOV, Offset.SETTINGS_KEYS_OFFSET + 9, KeyGroupTypes.GROUP, Help.NO_HELP),
    'VEHICLE_GENERATION_MODE': KeyInfo(KeyValueTypes.INTEGER, 1, Offset.SETTINGS_KEYS_OFFSET + 10, KeyGroupTypes.GROUP, Help.NO_HELP),
    'INDIFFERENCE_BAND': KeyInfo(KeyValueTypes.FLOAT, 0.0, Offset.SETTINGS_KEYS_OFFSET + 11, KeyGroupTypes.GROUP, Help.NO_HELP),
    'NUMBER_OF_STOPS': KeyInfo(KeyValueTypes.INTEGER, 1, Offset.SETTINGS_KEYS_OFFSET + 12, KeyGroupTypes.GROUP, Help.NO_HELP),
    'ENROUTE_INFO': KeyInfo(KeyValueTypes.INTEGER, 0, Offset.SETTINGS_KEYS_OFFSET + 13, KeyGroupTypes.GROUP, Help.NO_HELP),
    'COMPLIANCE_RATE': KeyInfo(KeyValueTypes.FLOAT, 0.0, Offset.SETTINGS_KEYS_OFFSET + 14, KeyGroupTypes.GROUP, Help.NO_HELP),
    'EVACUATION_FLAG': KeyInfo(KeyValueTypes.INTEGER, 0, Offset.SETTINGS_KEYS_OFFSET + 15, KeyGroupTypes.GROUP, Help.NO_HELP),
    'ACTIVITY_DURATION': KeyInfo(KeyValueTypes.FLOAT, 0.0, Offset.SETTINGS_KEYS_OFFSET + 16, KeyGroupTypes.GROUP, Help.NO_HELP),
    'ARRIVAL_TIME': KeyInfo(KeyValueTypes.FLOAT, 0.0, Offset.SETTINGS_KEYS_OFFSET + 17, KeyGroupTypes.GROUP, Help.NO_HELP),
    'WAIT_TIME': KeyInfo(KeyValueTypes.FLOAT, 0.0, Offset.SETTINGS_KEYS_OFFSET + 18, KeyGroupTypes.GROUP, Help.NO_HELP),
    'INITIAL_GAS': KeyInfo(KeyValueTypes.FLOAT, 0.0, Offset.SETTINGS_KEYS_OFFSET + 19, KeyGroupTypes.GROUP, Help.NO_HELP),
    'START_TRIP_NUMBER': KeyInfo(KeyValueTypes.INTEGER, 1, Offset.SETTINGS_KEYS_OFFSET + 20, KeyGroupTypes.SINGLE, Help.NO_HELP),
    'RENUMBER_TRIPS': KeyInfo(KeyValueTypes.BOOLEAN, 'TRUE', Offset.SETTINGS_KEYS_OFFSET + 21, KeyGroupTypes.SINGLE, Help.NO_HELP),

}


KEYS_DATABASE = {**SYSTEM_KEYS, **NETWORK_KEYS, **SETTINGS_KEYS}
