from enum import Enum, IntEnum, unique
from collections import namedtuple


KeyInfo = namedtuple('KeyInfo', ('value_type', 'default', 'order', 'group', 'help'))


class KeyValueTypes(IntEnum):
    INTEGER = 0
    FLOAT = 1
    STRING = 2
    FILE = 3
    INTEGER_LIST = 4
    FLOAT_LIST = 5
    TIME_RANGE = 6


@unique
class KeyGroupTypes(IntEnum):
    SINGLE = 0
    GROUP = 1


@unique
class Offset(IntEnum):
    EXECUTION_KEYS_OFFSET = 0
    NETWORK_KEYS_OFFSET = 10
    SETTINGS_KEYS_OFFSET = 100


class Help(Enum):
    NO_HELP = ''
    FILE_HELP = '[PROJECT_DIRECTORY]filename'
    RANGE_HELP = '1, 2, 3..10'
    INTEGER_LIST_HELP = '1, 2, 3'
    FLOAT_LIST_HELP = '0.1, 0.3, 0.5'


SYSTEM_KEYS = {
    'TITLE':                    KeyInfo(KeyValueTypes.STRING,      '', Offset.EXECUTION_KEYS_OFFSET+1, KeyGroupTypes.SINGLE, Help.NO_HELP),
    'REPORT_FILE':              KeyInfo(KeyValueTypes.FILE,        '', Offset.EXECUTION_KEYS_OFFSET+2, KeyGroupTypes.SINGLE, Help.FILE_HELP),
    'PROJECT_DIRECTORY':        KeyInfo(KeyValueTypes.STRING,      '', Offset.EXECUTION_KEYS_OFFSET+3, KeyGroupTypes.SINGLE, Help.NO_HELP),
    'RANDOM_SEED':              KeyInfo(KeyValueTypes.INTEGER,     47,  Offset.EXECUTION_KEYS_OFFSET+4, KeyGroupTypes.SINGLE, Help.NO_HELP),
}

NETWORK_KEYS = {
    'NETWORK_FILE': KeyInfo(KeyValueTypes.FILE, '', Offset.NETWORK_KEYS_OFFSET + 1, KeyGroupTypes.SINGLE, Help.FILE_HELP),
    'ORIGIN_FILE': KeyInfo(KeyValueTypes.FILE, '', Offset.NETWORK_KEYS_OFFSET + 2, KeyGroupTypes.SINGLE, Help.FILE_HELP),
    'TRAJECTORY_FILE': KeyInfo(KeyValueTypes.FILE, '', Offset.NETWORK_KEYS_OFFSET + 3, KeyGroupTypes.SINGLE, Help.FILE_HELP),
    'TRAJECTORY_FORMAT': KeyInfo(KeyValueTypes.STRING, 'BINARY', Offset.NETWORK_KEYS_OFFSET + 4, KeyGroupTypes.SINGLE, Help.NO_HELP),
    'TRIP_TABLE_FILE': KeyInfo(KeyValueTypes.FILE, '', Offset.NETWORK_KEYS_OFFSET + 5, KeyGroupTypes.GROUP, Help.FILE_HELP),

}


KEYS_DATABASE = {**SYSTEM_KEYS, **NETWORK_KEYS}
