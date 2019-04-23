from enum import IntEnum


class TaskStatus(IntEnum):
    OK = 0
    FAIL = 1
    UPSTREAM_FAIL = 2

    def __str__(self):
        return str(self._name_)


if __name__ == '__main__':
    t = TaskStatus.UPSTREAM_FAIL
    print(str(t))