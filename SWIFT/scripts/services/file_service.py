import struct
from services.namedlist import namedlist

fieldsNetworkHeaderRecord = ('number_of_zones', 'number_of_nodes',
                             'number_of_links', 'number_of_k_sp', 'use_super_zones')
BaseNetworkHeaderRecord = namedlist('BaseNetworkHeaderRecord', fieldsNetworkHeaderRecord)


class NetworkHeaderRecord(BaseNetworkHeaderRecord):

    fmt_bin = "=5i"

    def __repr__(self):
        field_list = '(' + ', '.join([f+'=%r' for f in self._fields]) + ')'
        return self.__class__.__name__ + field_list % tuple(self.__iter__())

    def __str__(self):
        self.to_str()

    def update(self, values):
        if len(values) != len(self):
            raise ValueError(f'Argument must be a tuple of size {len(self)}')
        self._update(**dict(zip(self._fields, values)))

    def to_str(self):
        return f'{self.number_of_zones:>7}{self.number_of_nodes:>7}{self.number_of_links:>7}' \
               f'{self.number_of_k_sp:>7}{self.use_super_zones:>7}'

    def from_str(self, values):
        if not isinstance(values, tuple) or not isinstance(values[0], str):
            raise TypeError('Argument must be a tuple of strings')
        if len(values) != len(self._fields):
            raise ValueError(f'Argument must be a tuple of size {len(self)}')

        self.update(values)

    def to_bin(self):
        return struct.pack(self.fmt_bin, *tuple(self.__iter__()))

    def from_bin(self, values):
        self.update(struct.unpack(self.fmt_bin, values))

class File:
    pass


if __name__=='__main__':

    r = NetworkHeaderRecord(5263, 22942, 45701, 1, 1)
    print(repr(r))
    print(r.to_str())
    print(isinstance(r, NetworkHeaderRecord))
    r2 = NetworkHeaderRecord(0,0,0,0,0)
    r_bin = r.to_bin()
    r2.from_bin(r_bin)
    print(r2.to_str())