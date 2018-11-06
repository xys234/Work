import numpy as np
import textwrap

def dt_gen():
    for i in range(4):
        yield 2,3,4


def all_even():
    n = 0
    while True:
        yield n
        n += 2


def wrap_list(lst, items_per_line=5):
    lines = []
    for i in range(0, len(lst), items_per_line):
        chunk = lst[i:i + items_per_line]
        line = ", ".join("{!r}".format(x) for x in chunk)
        lines.append(line)
    return "" + ",\n ".join(lines) + ""

if __name__ == '__main__':

    nums = list(range(20))
    # nums_str = ",".join(nums)
    print(wrap_list(nums))