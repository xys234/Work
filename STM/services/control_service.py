from collections import namedtuple
from enum import Enum, IntEnum, unique
from internals.key import Key, KeyValueTypes

KeyInfo = namedtuple('KeyInfo', ('value_type', 'default', 'order', 'help'))

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
    'TITLE':                    KeyInfo(KeyValueTypes.STRING,      '', Offset.EXECUTION_KEYS_OFFSET+1, Help.NO_HELP),
    'REPORT_FILE':              KeyInfo(KeyValueTypes.FILE,        '', Offset.EXECUTION_KEYS_OFFSET+2, Help.FILE_HELP),
    'PROJECT_DIRECTORY':        KeyInfo(KeyValueTypes.STRING,      '', Offset.EXECUTION_KEYS_OFFSET+3, Help.NO_HELP),
    'RANDOM_SEED':              KeyInfo(KeyValueTypes.INTEGER,     0,  Offset.EXECUTION_KEYS_OFFSET+3, Help.NO_HELP),
}

NETWORK_KEYS = {
    'NETWORK_FILE': KeyInfo(KeyValueTypes.FILE, '', Offset.NETWORK_KEYS_OFFSET + 1, Help.FILE_HELP),
    'ORIGIN_FILE': KeyInfo(KeyValueTypes.FILE, '', Offset.NETWORK_KEYS_OFFSET + 2, Help.FILE_HELP),
    'TRAJECTORY_FILE': KeyInfo(KeyValueTypes.FILE, '', Offset.NETWORK_KEYS_OFFSET + 3, Help.FILE_HELP),
    'TRAJECTORY_FORMAT': KeyInfo(KeyValueTypes.STRING, 'BINARY', Offset.NETWORK_KEYS_OFFSET + 3, Help.NO_HELP),

}


KEYS_DATABASE = {**SYSTEM_KEYS, **NETWORK_KEYS}


class ControlService(object):
    def __init__(self, control_file=None):
        self.control_file = control_file
        self.keys = {}
        self.highest_group = 0

    def read_control(self):
        pass

    def update_system_keys(self):
        pass

    def check_required_keys(self, required_keys=()):
        pass

    def update_keys(self):
        pass

    def validate_keys(self):
        pass