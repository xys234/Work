
from services import sys_defs

class Key():
    def __init__(self, key, key_type='required', value_type='float', value=None):
        self.key = key.upper()
        self.key_type = key_type.upper()
        self.value_type = value_type.upper()
        self.value = value.upper()
        self.root_keys = {}


    def _get_root_key(self, key):
        '''
        get the root key of a key
        :param key:
        :return: the root key
        '''

        parts = key.split("_")
        if parts[-1].is_digit():
            return key[:len(key)-len(parts[-1])]
        else:
            return key


    def _check_key(self):

        if self.key_type:
            pass

        convertor = float
        if self.key_type.upper() == sys_defs.KEY_VALUE_TYPES:
            pass

