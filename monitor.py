import multiprocessing as mp

import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets


class BaseMonitor:

    def __init__(self, title=None, qt_material_theme='dark_blue.xml'):
        self.title = title
        self.qt_material_theme = qt_material_theme

    def init_panels(self, frame: 'pg.LayoutWidget') -> None:
        raise NotImplementedError

    def run(self):
        app = pg.mkQApp()
        try:
            from qt_material import apply_stylesheet
            apply_stylesheet(
                app, theme=self.qt_material_theme,
                extra={'font_family': 'Arial'})
        except ImportError:
            pass

        window = QtWidgets.QMainWindow()
        window.setWindowTitle(self.title)

        frame = pg.LayoutWidget()
        frame.layout.setContentsMargins(5, 5, 5, 5)
        window.setCentralWidget(frame)

        self.init_panels(frame)

        window.showMaximized()
        app.exec_()

    def run_mp(self):
        mp.Process(target=self.run).start()
