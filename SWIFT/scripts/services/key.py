
from services.sys_defs import *
from collections import namedtuple

class Key():
    def __init__(self, key=None, key_type=None, value=None):
        self._key = key
        self.key_type = key_type
        self._value_default = None
        self._value_type = None
        self._root_key = None
        self._key_group = 0
        self.value = value

        self._initialize_key()

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    @property
    def key(self):
        return self._key

    @property
    def root_key(self):
        return self._root_key

    @root_key.setter
    def root_key(self, value):
        self._root_key = value

    @property
    def value_type(self):
        return self._value_type

    @property
    def value_default(self):
        return self._value_default

    @property
    def key_group(self):
        return self._key_group

    @key_group.setter
    def key_group(self, value):
        self._key_group = value

    @property
    def key_type(self):
        return self._key_type

    @key_type.setter
    def key_type(self, value):
        self._key_type = value

    def __str__(self):
        return str(dict(key=self.key, key_type=self._key_type, root_key=self.root_key,
                        value_type=self._value_type, value=self.value, key_group=self.key_group
                        )
                   )

    def to_dict(self):
        key = namedtuple('key', ('key', 'key_type', 'value_default', 'value_type', 'root_key', 'key_group', 'value'))
        return {self.key: key(self.key, self.key_type, self.value_default,
                              self.value_type, self.root_key, self.key_group, self.value)}

    def _update_key_value(self):
        converter = int
        if self.value_type == Key_Value_Types.STRING:
            converter = str
        elif self.value_type == Key_Value_Types.FLOAT:
            converter = float
        if self.value:
            self.value = converter(self.value)

    def _initialize_key(self):
        """
         update the fields based on the key database
        :param :
        :return:
        """

        parts = self.key.split("_")
        if parts[-1].isdigit():
            self.root_key = self.key[:len(self.key)-len(parts[-1])-1]
            self.key_group = int(parts[-1])
        else:
            self.root_key = self.key

        if self.root_key in KEY_DB:
            self._value_type, self._value_default = KEY_DB[self.root_key].value_type, KEY_DB[self.root_key].value_default
        else:
            self.root_key = None

        if self.value is None:
            self.value = KEY_DB[self.root_key].value_default          # set to default value

        self._update_key_value()

    @classmethod
    def get_root(cls, keyname):
        """
        get the root key name
        :param keyname:
        :type  str
        :return:
        """

        parts = keyname.split("_")
        if parts[-1].isdigit():
            return keyname[:len(keyname) - len(parts[-1]) - 1], int(parts[-1])
        else:
            return keyname, 0


if __name__=='__main__':

    key1_def = dict(key="TRIP_TABLE_FILE_1", key_type=Key_Value_Types.STRING, value='Matrix_am.omx')
    key1 = Key(**key1_def)
    print(key1)

    key2_def = dict(key="JUNK_KEY", key_type=Key_Value_Types.STRING, value='Matrix_am_hbw.omx')
    key2 = Key(**key2_def)
    print(key2)

    key3_def = dict(key="VALUE_OF_TIME_2", key_type=Key_Value_Types.FLOAT, value='23.7')
    key3 = Key(**key3_def)
    print(key3)