from typing import List, Optional, Union
import cv2

import pyqtgraph as pg
from pyqtgraph.console import ConsoleWidget
from pyqtgraph.Qt import QtWidgets

try:
    from .util import ListContainer, QtLoop
except ImportError:
    from util import ListContainer, QtLoop


class BasePanel:

    def build(self) -> 'QtWidgets.QWidget':
        raise NotImplementedError

    def setup_video(
            self, view_box: 'pg.ViewBox', lc: 'ListContainer',
            target: Union[int, str], loop_msec: int = 33) -> None:
        imgitem = pg.ImageItem()
        view_box.addItem(imgitem)
        cap = cv2.VideoCapture(target)

        def main():
            try:
                frame = cv2.rotate(cap.read()[1], cv2.ROTATE_90_CLOCKWISE)
                imgitem.setImage(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                lc.replace(0, frame)
            except:
                cap.release()

        QtLoop.run(main, loop_msec)

    def setup_line_graph(
            self, plot_item: 'pg.PlotItem', lc: 'ListContainer',
            title: Optional[str] = None,
            xlabel: Optional[str] = None, xunit: Optional[str] = None,
            ylabel: Optional[str] = None, yunit: Optional[str] = None,
            xrange: Optional[tuple] = None, yrange: Optional[tuple] = None,
            legends: List[str] = [], colors: Optional[List[tuple]] = None,
            fill: bool = False, loop_msec: int = 100) -> None:
        plot_item.setTitle(title=title)
        plot_item.setLabel(axis='bottom', text=xlabel, units=xunit)
        plot_item.setLabel(axis='left', text=ylabel, units=yunit)
        if xrange is not None: plot_item.setXRange(*xrange, padding=0)
        if yrange is not None: plot_item.setYRange(*yrange, padding=0)

        show_legend = len(legends) > 0
        ps: List[pg.PlotDataItem] = []

        if show_legend:
            leg = pg.LegendItem(offset=(35, 15), verSpacing=-10)
            leg.setParentItem(plot_item)

        for i in range(lc.n_lists):
            kwargs = {}
            if colors is not None:
                color = colors[i%len(colors)]
                kwargs['pen'] = color
                if fill is not None:
                    kwargs['brush'] = (*color, 100)
                    kwargs['fillLevel'] = 0.0
            _p = plot_item.plot([], **kwargs)
            ps.append(_p)
            if show_legend: leg.addItem(_p, legends[i])

        def main():
            for p, l in zip(ps, lc.iter_lists()):
                p.setData(l)

        QtLoop.run(main, loop_msec)

    def setup_scatter_plot(
            self, plot_item: 'pg.PlotItem',
            lc_x: 'ListContainer', lc_y: 'ListContainer',
            title: Optional[str] = None,
            xlabel: Optional[str] = None, xunit: Optional[str] = None,
            ylabel: Optional[str] = None, yunit: Optional[str] = None,
            xrange: Optional[tuple] = None, yrange: Optional[tuple] = None,
            legends: List[str] = [], colors: Optional[List[tuple]] = None,
            loop_msec: int = 100) -> None:
        plot_item.setTitle(title=title)
        plot_item.setLabel(axis='bottom', text=xlabel, units=xunit)
        plot_item.setLabel(axis='left', text=ylabel, units=yunit)
        if xrange is not None: plot_item.setXRange(*xrange, padding=0)
        if yrange is not None: plot_item.setYRange(*yrange, padding=0)

        show_legend = len(legends) > 0
        ps: List[pg.PlotDataItem] = []

        if show_legend:
            leg = pg.LegendItem(offset=(35, 15), verSpacing=-10)
            leg.setParentItem(plot_item)

        for i in range(lc_x.n_lists):
            kwargs = {'pen': None, 'symbolPen': None, 'symbolSize': 10}
            if colors is not None:
                color = colors[i%len(colors)]
                kwargs['symbolBrush'] = color
            _p = plot_item.plot([], **kwargs)
            ps.append(_p)
            if show_legend: leg.addItem(_p, legends[i])

        def main():
            for p, lx, ly in zip(ps, lc_x.iter_lists(), lc_y.iter_lists()):
                p.setData(lx, ly)

        QtLoop.run(main, loop_msec)

    def setup_console(
            self, wid: 'ConsoleWidget', lc: 'ListContainer',
            loop_msec: int = 100) -> None:

        def main():
            for s in lc.get(0):
                wid.write(s+'\n')
            lc.clear(0)

        QtLoop.run(main, loop_msec)


class BaseGraphicsPanel(BasePanel):

    def __init__(self) -> None:
        self.init_vars()

    def build(self) -> 'QtWidgets.QWidget':
        widget = pg.GraphicsLayoutWidget()
        self.init_widget(widget=widget)
        return widget

    def init_vars(self) -> None:
        raise NotImplementedError

    def init_widget(self, widget: 'pg.GraphicsLayoutWidget') -> None:
        raise NotImplementedError


class BaseConsolePanel(BasePanel):

    def __init__(self) -> None:
        self.init_vars()

    def build(self) -> 'QtWidgets.QWidget':
        widget = ConsoleWidget()
        self.init_widget(widget)
        return widget

    def init_vars(self) -> None:
        raise NotImplementedError

    def init_widget(self, widget: 'ConsoleWidget') -> None:
        raise NotImplementedError
