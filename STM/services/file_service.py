import struct
from services.namedlist import namedlist
from collections import Sequence

# Network file record field definitions
fieldsNetworkHeaderRecord = (('number_of_zones', 0), ('number_of_nodes', 0),
                             ('number_of_links', 0), ('number_of_k_sp', 0), ('use_super_zones', 0))
BaseNetworkHeaderRecord = namedlist('BaseNetworkHeaderRecord', fieldsNetworkHeaderRecord)

fieldsNetworkNodeZoneRecord = (('node', 0), ('zone', 0))
BaseNetworkNodeZoneRecord = namedlist('BaseNetworkNodeZoneRecord', fieldsNetworkNodeZoneRecord)

fieldsNetworkLinkRecord = (
                            ('Anode', 0),
                            ('Bnode', 0),
                            ('Lbay', 0),
                            ('Rbay', 0),
                            ('length', 0),
                            ('lanes', 0),
                            ('tfm', 0),
                            ('spd_fac', 0),
                            ('spd_limit', 0),
                            ('service_rate', 0),
                            ('sat_rate', 0),
                            ('ftype', 0),
                            ('grade', 0),
                        )
BaseNetworkLinkRecord = namedlist('BaseNetworkLinkRecord', fieldsNetworkLinkRecord)

fieldsTrafficFlowModelRecord = (
            ('tfmid', 0),
            ('regime', 0),
            ('form', 2),
            ('kcut', 20.0),
            ('vf', 60.0),
            ('v0', 40.0),
            ('kjam', 200.0),
            ('alpha', 2.5),
            ('beta', 1.0),
)
BaseTrafficFlowModelRecord = namedlist('BaseTrafficFlowModelRecord', fieldsTrafficFlowModelRecord)


fieldsTripFileRecord = (
            ('vehid', 0),
            ('u_node', 0),
            ('d_node', 0),
            ('stime', 0),
            ('muc', 0),
            ('veh_type', 0),
            ('loc', 0),
            ('gen_mode', 1),
            ('num_stops', 1),
            ('info', 0),
            ('ribf', 0),
            ('comp', 0),
            ('izone', 0),
            ('evac', 0),
            ('init_pos', 0),
            ('vot', 0),
            ('tflag', 0),
            ('parr_time', 0),
            ('purpose', 0),
            ('init_gas', 0),
            ('dzone', 0),
            ('wait', 0),

)
BaseTripFileRecord = namedlist('BaseTripFileRecord', fieldsTripFileRecord)


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
    fmt_string = '{:>7d}{:>7d}{:>7d}{:>7d}{:>7d}\n'

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

    def from_string(self, values):
        if not isinstance(values, Sequence) or not isinstance(values[0], str):
            raise TypeError('Argument must be a tuple of strings')
        if len(values) != len(self._fields):
            raise ValueError(f'Argument must be a tuple of size {len(self)}')

        self.update(values)

    def from_bytes(self, values):
        self.update(struct.unpack(self.fmt_binary, values))

    def to_string(self):
        return self.fmt_string.format(*self.values)

    def to_bytes(self):
        return struct.pack(self.fmt_binary, *self.values)


class NetworkNodeZoneRecord(RecordMixin, BaseNetworkNodeZoneRecord):
    __slots__ = ()

    fmt_binary = "=ii"
    fmt_string = '{:>7d}{:>5d}\n'

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
        if not isinstance(values, Sequence) or not isinstance(values[0], str):
            raise TypeError('Argument must be a tuple of strings')
        if len(values) != len(self._fields):
            raise ValueError(f'Argument must be a tuple of size {len(self)}')

        self.update(values)


class NetworkLinkRecord(RecordMixin, BaseNetworkLinkRecord):
    __slots__ = ()

    fmt_binary = "=iiiifiiiiiiii"
    fmt_string = '{:>7d}{:7d}{:5d}{:5d}{:7.0f}{:3d}{:7d}{:4d}{:4d}{:6d}{:6d}{:3d}{:4d}\n'

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
        if not isinstance(values, Sequence) or not isinstance(values[0], str):
            raise TypeError('Argument must be a tuple of strings')
        if len(values) != len(self._fields):
            raise ValueError(f'Argument must be a tuple of size {len(self)}')

        self.update(values)


class TrafficFlowModelRecord(RecordMixin, BaseTrafficFlowModelRecord):
    __slots__ = ()

    fmt_binary = "=iiiiiiiff"
    fmt_string = '{:d} {:d} {:d}\n{:d} {:d} {:d} {:d} {:.2f} {:.2f}\n'

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
        if not isinstance(values, Sequence) or not isinstance(values[0], str):
            raise TypeError('Argument must be a tuple of strings')
        if len(values) != len(self._fields):
            raise ValueError(f'Argument must be a tuple of size {len(self)}')

        self.update(values)


class TripFileRecord(RecordMixin, BaseTripFileRecord):
    __slots__ = ()

    fmt_binary = "=iiifiiiiiiffiiffififif"
    fmt_string = "{:>9d}{:>7d}{:>7d}{:>8.1f}{:>6d}{:>6d}{:>6d}{:>6d}{:>6d}{:>6d}{:>8.4f}{:>8.4f}{:>6d}" \
                 "{:>6d}{:>12.8f}{:>8.2f}{:>5d}{:>7.1f}{:>5d}{:>5.1f}\n{:>12d}{:>7.2f}\n"

    def __repr__(self):
        field_list = '(' + ', '.join([f+'=%r' for f in self._fields]) + ')'
        return self.__class__.__name__ + field_list % self.values

    def __str__(self):
        return self.to_string()

    @property
    def values(self):
        return tuple(self.__iter__())

    def update(self, values):
        converted_values = RecordMixin.convert(values, self.fmt_binary)
        self._update(**dict(zip(self._fields, converted_values)))

    def from_string(self, values):
        if not isinstance(values, Sequence) or not isinstance(values[0], str):
            raise TypeError('Argument must be a tuple of strings')
        if len(values) != len(self._fields):
            raise ValueError(f'Argument must be a tuple of size {len(self)}')

        self.update(values)

    def to_string(self):
        return self.fmt_string.format(*self.values)


class File:

    def __init__(self, name=None):
        self.name = name
        self.records = []

    def __iter__(self):
        return iter(self.records)

    def __len__(self):
        return len(self.records)

    def __getitem__(self, item):
        return self.records[item]

    def append(self, record):
        self.records.append(record)


if __name__ == '__main__':

    r = NetworkHeaderRecord()
    print(repr(r))
    r.from_string(('5263', '22942', '45701', '1', '1'))
    print(r.to_string())
    r2 = NetworkHeaderRecord()
    r_bin = r.to_bytes()
    r2.from_bytes(r_bin)
    print(r2.to_string())
    r3 = NetworkLinkRecord()
    print(isinstance(r3, NetworkLinkRecord))
