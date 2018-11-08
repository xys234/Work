import numpy as np
import textwrap

class Celsius:
    def __init__(self, temperature = 0):
        self._temperature = temperature
        print("created")

    def to_fahrenheit(self):
        return (self.temperature * 1.8) + 32

    @property
    def temperature(self):
        print("Getting value")
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        if value < -273:
            raise ValueError("Temperature below -273 is not possible")
        print("Setting value")
        self._temperature = value


def wrap_list(lst, items_per_line=5):
    lines = []
    for i in range(0, len(lst), items_per_line):
        chunk = lst[i:i + items_per_line]
        line = ", ".join("{!r}".format(x) for x in chunk)
        lines.append(line)
    return "" + ",\n ".join(lines) + ""

if __name__ == '__main__':

    t1 = Celsius(20)
    t1.temperature = 40
    print(t1.temperature)