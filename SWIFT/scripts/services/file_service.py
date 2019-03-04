import struct
from services.namedlist import namedlist

# Record field definitions
fieldsNetworkHeaderRecord = (('number_of_zones', 0), ('number_of_nodes', 0),
                             ('number_of_links', 0), ('number_of_k_sp', 0), ('use_super_zones', 0))
BaseNetworkHeaderRecord = namedlist('BaseNetworkHeaderRecord', fieldsNetworkHeaderRecord)

fieldsNetworkNodeZoneRecord = (('node', 0), ('zone', 0))
BaseNetworkNodeZoneRecord = namedlist('BaseNetworkNodeZoneRecord', fieldsNetworkNodeZoneRecord)

fieldsNetworkLinkRecord = (('node', 0), ('zone', 0))
BaseNetworkLinkRecord = namedlist('BaseNetworkLinkRecord', fieldsNetworkLinkRecord)


class RecordMixin:
    converter = {
            'i': int,
            'b': int,
            'h': int,
            'f': float,
        }

    @staticmethod
    def convert(values, fmt):
        if len(values) != len(fmt) - 1:
            raise ValueError(f'Arguments must be a tuple of size {len(values)}')
        return tuple([RecordMixin.converter[f](v) for v, f in zip(values, fmt[1:])])


class NetworkHeaderRecord(RecordMixin, BaseNetworkHeaderRecord):

    __slots__ = ()

    fmt_binary = "=iiiii"
    fmt_string = '{:>7d}{:>7d}{:>7d}{:>7d}{:>7d}'

    def __repr__(self):
        field_list = '(' + ', '.join([f+'=%r' for f in self._fields]) + ')'
        return self.__class__.__name__ + field_list % self.values

    def __str__(self):
        self.to_string()

    @property
    def values(self):
        return tuple(self.__iter__())

    def update(self, values):
        converted_values = RecordMixin.convert(values, self.fmt_binary)
        self._update(**dict(zip(self._fields, converted_values)))

    def to_string(self):
        return self.fmt_string.format(*self.values)

    def from_string(self, values):
        if not isinstance(values, tuple) or not isinstance(values[0], str):
            raise TypeError('Argument must be a tuple of strings')
        if len(values) != len(self._fields):
            raise ValueError(f'Argument must be a tuple of size {len(self)}')

        self.update(values)

    def to_bytes(self):
        return struct.pack(self.fmt_binary, *self.values)

    def from_bytes(self, values):
        self.update(struct.unpack(self.fmt_binary, values))


class NetworkNodeZoneRecord(RecordMixin, BaseNetworkNodeZoneRecord):
    __slots__ = ()

    fmt_binary = "=ii"
    fmt_string = '{:>7d}{:>5d}'

    def __repr__(self):
        field_list = '(' + ', '.join([f+'=%r' for f in self._fields]) + ')'
        return self.__class__.__name__ + field_list % self.values

    def __str__(self):
        self.to_string()

    @property
    def values(self):
        return tuple(self.__iter__())

    def update(self, values):
        converted_values = RecordMixin.convert(values, self.fmt_binary)
        self._update(**dict(zip(self._fields, converted_values)))

    def to_string(self):
        return self.fmt_string.format(*self.values)

    def from_string(self, values):
        if not isinstance(values, tuple) or not isinstance(values[0], str):
            raise TypeError('Argument must be a tuple of strings')
        if len(values) != len(self._fields):
            raise ValueError(f'Argument must be a tuple of size {len(self)}')

        self.update(values)


class NetworkLinkRecord(RecordMixin, BaseNetworkNodeZoneRecord):
    __slots__ = ()

    fmt_binary = "=ii"
    fmt_string = '{:>7d}{:>5d}'

    def __repr__(self):
        field_list = '(' + ', '.join([f+'=%r' for f in self._fields]) + ')'
        return self.__class__.__name__ + field_list % self.values

    def __str__(self):
        self.to_string()

    @property
    def values(self):
        return tuple(self.__iter__())

    def update(self, values):
        converted_values = RecordMixin.convert(values, self.fmt_binary)
        self._update(**dict(zip(self._fields, converted_values)))

    def to_string(self):
        return self.fmt_string.format(*self.values)

    def from_string(self, values):
        if not isinstance(values, tuple) or not isinstance(values[0], str):
            raise TypeError('Argument must be a tuple of strings')
        if len(values) != len(self._fields):
            raise ValueError(f'Argument must be a tuple of size {len(self)}')

        self.update(values)




class File:
    pass


if __name__=='__main__':

    r = NetworkHeaderRecord()
    print(repr(r))
    r.from_string(('5263', '22942', '45701', '1', '1'))
    print(r.to_string())
    r2 = NetworkHeaderRecord()
    r_bin = r.to_bytes()
    r2.from_bytes(r_bin)
    print(r2.to_string())