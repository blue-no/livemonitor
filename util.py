import multiprocessing as mp
from multiprocessing.managers import ListProxy
from typing import Any, Callable, Iterator, Optional

from pyqtgraph.Qt import QtCore


class QtLoop:
    __timers = []

    @classmethod
    def run(cls, f: Callable, msec: int) -> None:
        timer = QtCore.QTimer()
        timer.timeout.connect(f)
        timer.start(msec)
        cls.__timers.append(timer)


class ListContainer:

    def __init__(
            self, n_lists: int = 1, list_maxlen: Optional[int] = None) -> None:
        m = mp.Manager()
        self.list_maxlen = list_maxlen
        self.__n_lists = n_lists
        self.__lists = m.list([[] for _ in range(n_lists)])

    @property
    def n_lists(self) -> int:
        return self.__n_lists

    def get(self, index) -> ListProxy:
        return self.__lists[index]

    def iter_lists(self) -> Iterator[ListProxy]:
        for list_ in self.__lists:
            yield list_

    def append(self, index: int, *values: Any) -> None:
        new = self.__lists[index] + list(values)
        if self.list_maxlen is not None:
            new = new[-self.list_maxlen:]
        self.__lists[index] = new

    def replace(self, index: int, *values: Any) -> None:
        new = list(values)
        if self.list_maxlen is not None:
            new = new[-self.list_maxlen:]
        self.__lists[index] = new

    def clear(self, index: int) -> None:
        # self.__lists[index][:] = []
        self.__lists[index] = []
