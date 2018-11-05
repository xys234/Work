import numpy as np

def dt_gen():
    for i in range(4):
        yield np.random.choice([2,4,6,7])
    return 100

def all_even():
    n = 0
    while True:
        yield n
        n += 2

if __name__ == '__main__':

    d = dt_gen()
    print(next(d))
    print(next(d))
    print(next(d))
    print(next(d))
    print(next(d))
    print(d)