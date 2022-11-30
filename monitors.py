import multiprocessing as mp

import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets

from base import _BaseMonitor


class Monitor1(_BaseMonitor):

    def __init__(
            self,
            title=None,
            panel1=None,
            panel2=None,
            panel3=None) -> None:
        super().__init__(title=title)
        self.panel1 = panel1
        self.panel2 = panel2
        self.panel3 = panel3

    def _layout_panels(self, frame: pg.LayoutWidget) -> None:
        if self.panel1 is not None:
            frame.addWidget(
                self.panel1.build_widget(), col=0, row=0, rowspan=2)
        if self.panel2 is not None:
            frame.addWidget(
                self.panel2.build_widget(), col=0, row=2)
        if self.panel3 is not None:
            frame.addWidget(
                self.panel3.build_widget(), col=1, row=0, rowspan=3)
        frame.layout.setColumnStretch(0, 2)
        frame.layout.setColumnStretch(1, 3)
