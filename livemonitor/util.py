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

    @classmethod
    def stop_all(cls) -> None:
        for timer in cls.__timers:
            timer.stop()


class SharedData:

    def __init__(self, maxlen: Optional[int] = None) -> None:
        self.maxlen = maxlen
        self.__values = mp.Manager().list([[]])

    def get(self) -> Any:
        try:
            return self.__values[0]
        except Exception:
            exit()

    def push(self, *values: Any) -> None:
        try:
            new = self.__values[0] + list(values)
            if self.maxlen is not None:
                new = new[-self.maxlen:]
            self.__values[0] = new
        except Exception:
            exit()

    def replace(self, values: Any) -> None:
        try:
            new = values
            if self.maxlen is not None:
                new = new[-self.maxlen:]
            self.__values[0] = new
        except Exception:
            exit()

    def clear(self) -> None:
        try:
            self.__values[0] = []
        except Exception:
            exit()
