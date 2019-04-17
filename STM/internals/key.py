from internals.key_db import *


class Key(object):
    """

    key class

    """

    def __init__(self, key, input_value=None):
        self._key = key
        if input_value is None:
            self._input_value = str(KEYS_DATABASE[key].default)     # input value is always string
        else:
            self._input_value = str(input_value)
        self._value = self._input_value
        self._root = self.key
        self._group = 0

        parts = self.key.split("_")
        if parts[-1].isdigit():
            self._root = self.key[:len(self.key)-len(parts[-1])-1]
            self._group = int(parts[-1])
        self._type = KEYS_DATABASE[self.root].value_type
        self._order = KEYS_DATABASE[self.root].order

    def __repr__(self):
        return "%s(key=%s, input_value=%s)" % (self.__class__.__name__, self._key, self._input_value)

    def __str__(self):
        return "%s(key=%s, input_value=%s, value=%s, root=%s, group=%s)" % (
            self.__class__.__name__, self._key, self.input_value, self.value, self.root, self.group
        )

    @property
    def key(self):
        return self._key

    @key.setter
    def key(self, value):
        self._key = value

    @property
    def input_value(self):
        return self._input_value

    @input_value.setter
    def input_value(self, value):
        self._input_value = value

    @property
    def group(self):
        return self._group

    @group.setter
    def group(self, value):
        self._group = value

    @property
    def nested(self):
        return self._group > 0

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    @property
    def root(self):
        return self._root

    @root.setter
    def root(self, value):
        self._root = value

    @property
    def value_type(self):
        return self._type

    @property
    def order(self):
        return self._order


if __name__ == '__main__':
    key1 = Key(key='NETWORK_FILE', input_value='fake_path')
    print(key1)
    key2 = Key(key='TRIP_TABLE_FILE', input_value='fake_path')
    print(key2)
