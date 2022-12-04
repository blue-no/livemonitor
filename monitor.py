import multiprocessing as mp

import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets


class BaseMonitor:

    def __init__(self, title=None):
        self.title = title

    def layout_panels(self, frame: 'pg.LayoutWidget') -> None:
        raise NotImplementedError

    def run(self):
        app = pg.mkQApp()
        window = QtWidgets.QMainWindow()
        window.setWindowTitle(self.title)

        frame = pg.LayoutWidget()
        frame.layout.setContentsMargins(5, 5, 5, 5)
        window.setCentralWidget(frame)

        self.layout_panels(frame)

        window.show()
        app.exec_()

    def run_mp(self):
        mp.Process(target=self.run).start()
