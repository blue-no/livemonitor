import multiprocessing as mp
from typing import Any, Callable, Optional

from pyqtgraph.Qt import QtCore


class QtLoop:
    __timers = []

    @classmethod
    def run(cls, f: Callable, msec: int) -> None:
        timer = QtCore.QTimer()
        timer.timeout.connect(f)
        timer.start(msec)
        cls.__timers.append(timer)


class SharedData:

    def __init__(self, maxlen: Optional[int] = None) -> None:
        self.maxlen = maxlen
        self.__values = mp.Manager().list([[]])

    def get(self) -> Any:
        return self.__values[0]

    def push(self, *values: Any) -> None:
        new = self.__values[0] + list(values)
        if self.maxlen is not None:
            new = new[-self.maxlen:]
        self.__values[0] = new

    def replace(self, values: Any) -> None:
        new = list(values)
        if self.maxlen is not None:
            new = new[-self.maxlen:]
        self.__values[0] = new

    def clear(self) -> None:
        self.__values[0] = []
