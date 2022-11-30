import multiprocessing as mp
from typing import Dict, List, Union
import cv2

import pyqtgraph as pg
from pyqtgraph.console import ConsoleWidget
from pyqtgraph.Qt import QtCore, QtWidgets

from common import colors


class QLoop:
    __timers = []

    @classmethod
    def run(cls, f, msec):
        timer = QtCore.QTimer()
        timer.timeout.connect(f)
        timer.start(msec)
        cls.__timers.append(timer)


class SharedData:

    def __init__(self, maxlen=None):
        self.__maxlen = maxlen
        self.__values = mp.Manager().list()

    def is_empty(self):
        return len(self.__values) == 0

    def push(self, *values):
        self.__values += list(values)
        self.__values[:len(self.__values)-self.__maxlen] = []

    def pop(self):
        return self.__values.pop(0)

    def clear(self):
        self.__values[:] = []

    @property
    def values(self):
        return self.__values

    def as_list(self):
        return list(self.__values)


class _BasePanel:

    def build_widget(self):
        raise NotImplementedError

    def _generate_video_sd(self) -> SharedData:
        return SharedData(maxlen=1)

    def _setup_video(
            self, box: pg.ViewBox, sd: SharedData,
            vc_target: Union[int, str]) -> None:
        imgitem = pg.ImageItem()
        box.addItem(imgitem)
        cap = cv2.VideoCapture(vc_target)

        def main():
            try:
                frame = cv2.rotate(cap.read()[1], cv2.ROTATE_90_CLOCKWISE)
                imgitem.setImage(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                sd.push(frame)
            except:
                cap.release()

        QLoop.run(main, 100)

    def _generate_timeseries_sd(
            self, n_plots: int = 1, histlen: int = 10000) -> List[SharedData]:
        sds = []
        for _ in range(n_plots):
            sds.append(SharedData(maxlen=histlen))
        return sds

    def _setup_timeseries_plots(
            self, item: pg.PlotItem, sds: List[SharedData], title: str = None,
            xlabel: str = None, xunit: str = None,
            ylabel: str = None, yunit: str = None,
            xrange: tuple = None, yrange: tuple = None,
            legends: List[str] = [], i_color: int = None,
            fill: bool = False) -> None:
        item.setTitle(title=title)
        item.setLabel(axis='bottom', text=xlabel, units=xunit)
        item.setLabel(axis='left', text=ylabel, units=yunit)
        if xrange is not None:
            item.setXRange(*xrange, padding=0)
        if yrange is not None:
            item.setYRange(*yrange, padding=0)

        show_legend = len(legends) > 0
        ps: List[pg.PlotDataItem] = []

        if show_legend:
            leg = pg.LegendItem(offset=(35, 15), verSpacing=-10)
            leg.setParentItem(item)

        for i in range(len(sds)):
            clr = colors(i) if i_color is None else colors(i_color)
            _p = item.plot(
                [], pen=clr, fillLevel=0.0,
                brush=(*clr, 100) if fill else None)
            ps.append(_p)
            if show_legend:
                leg.addItem(_p, legends[i])

        def main():
            for p, sd in zip(ps, sds):
                p.setData(sd.as_list())

        QLoop.run(main, 100)

    def _generate_scatter_sd(
            self, n_plots: int = 1, histlen: int = 10000
            ) -> List[Dict[str, SharedData]]:
        sds = []
        for _ in range(n_plots):
            sds.append({
                'x': SharedData(maxlen=histlen),
                'y': SharedData(maxlen=histlen)})
        return sds

    def _setup_scatter_plots(
            self, item: pg.PlotItem, sds: List[Dict[str, SharedData]],
            title: str = None,
            xlabel: str = None, xunit: str = None,
            ylabel: str = None, yunit: str = None,
            xrange: tuple = None, yrange: tuple = None,
            legends: List[str] = [], i_color: int = None,) -> None:
        item.setTitle(title=title)
        item.setLabel(axis='bottom', text=xlabel, units=xunit)
        item.setLabel(axis='left', text=ylabel, units=yunit)
        if xrange is not None:
            item.setXRange(*xrange, padding=0)
        if yrange is not None:
            item.setYRange(*yrange, padding=0)

        show_legend = len(legends) > 0
        ps: List[pg.PlotDataItem] = []

        if show_legend:
            leg = pg.LegendItem(offset=(35, 15), verSpacing=-10)
            leg.setParentItem(item)

        for i in range(len(sds)):
            clr = colors(i) if i_color is None else colors(i_color)
            _p = item.plot(
                [], symbolBrush=clr, symbolPen=None, symbolSize=10)
            ps.append(_p)
            if show_legend:
                leg.addItem(_p, legends[i])

        def main():
            for p, sd in zip(ps, sds):
                p.setData(sd['x'].as_list(), sd['y'].as_list())

        QLoop.run(main, 100)

    def _generate_console_sd(self) -> SharedData:
        return SharedData(maxlen=100)

    def _setup_console(self, wid: ConsoleWidget, sd: SharedData) -> None:
        def main():
            for s in sd.values:
                wid.write(s)
            sd.clear()

        QLoop.run(main, 100)



class _BaseMonitor:

    def __init__(self, title=None) -> None:
        self.title = title

    def _layout_panels(self, frame: pg.LayoutWidget) -> None:
        raise NotImplementedError

    def run(self):
        app = pg.mkQApp()
        window = QtWidgets.QMainWindow()
        window.setWindowTitle(self.title)

        frame = pg.LayoutWidget()
        frame.layout.setContentsMargins(5, 5, 5, 5)
        window.setCentralWidget(frame)

        self._layout_panels(frame)

        window.show()
        app.exec_()
