from pyqtgraph.Qt import QtCore


class QLoop:
    __timers = []

    @classmethod
    def run(cls, f, msec):
        timer = QtCore.QTimer()
        timer.timeout.connect(f)
        timer.start(msec)
        cls.__timers.append(timer)
