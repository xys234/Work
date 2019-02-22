from collections import namedtuple
import struct

class Field:
    __slots__ = ('_name', '_type', '_width', '_size', '_value', '_fmt')

    def __init__(self, name=None, type=None, width=None, size=None, value=None, fmt=None):
        """

        :param name:
        :type str
        :param type:
        :type str
        :param width:
        :type int
        :param size:
        :type int
        :param value:
        :param fmt:
        :type str
        """
        self.name = name
        self.type = type
        self.width = width
        self.size = size
        self.value = value
        self.fmt = fmt

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, val):
        self._type = val

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, val):
        self._width = val

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, val):
        self._size = val

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, val):
        self._value = val

    @property
    def fmt(self):
        return self._fmt

    @fmt.setter
    def fmt(self, val):
        self._fmt = val

    @property
    def bytes_fmt(self):

        if self.type == 'i':
            if self.size == 4:
                pass

    def __str__(self):
        return self.fmt.format(self.value)

    def __repr__(self):
        return f'Field(name={self.name}, type={self.type}, width={self.width}, size={self.size}, ' \
               f'value={self.value}, fmt={self.fmt})'

    def __bytes__(self):
        """
        Return the byte representation of the value
        :return:
        """
        return struct.pack(self.bytes_fmt, self.value)

class Record(tuple):
    pass


class File:
    pass


if __name__=='__main__':

    f1 = Field('lanes','i',4,4,3,'Lanes= {:d}')
    print(f1)
    print(f1.__repr__())
    f1_bin = bytes(f1)
    print(struct.unpack(f1.bytes_fmt))