from enum import IntEnum


class KeyValueTypes(IntEnum):
    INTEGER = 0
    FLOAT = 1
    STRING = 2
    FILE = 3
    INTEGER_LIST = 4
    FLOAT_LIST = 5


class Key(object):
    """

    key class

    """

    def __init__(self, name=None, input_value=None, value_type=None, group=0):
        self._name = name
        self._input_value = input_value
        self._group = group
        self._type = value_type

        self._value = self._input_value

    def __repr__(self):
        return "%s(name=%s, input_value=%s, value_type=%s, nested=%s)" % (self.__class__.__name__, self._name,
                                                                          self._input_value, self._type, self._group)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value

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

    def convert(self, converter, *args, **kwargs):
        self._value = converter(self._input_value, args, kwargs)


if __name__ == '__main__':
    key1 = Key(name='TRIP_FILE', input_value='fake_path', value_type=KeyValueTypes.FILE)
    print(key1)