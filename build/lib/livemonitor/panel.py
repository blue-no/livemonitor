from typing import List, Optional, Tuple, Union

import cv2
import numpy as np
import pyqtgraph as pg
from pyqtgraph.console import ConsoleWidget
from pyqtgraph.Qt import QtWidgets

from .color import code_to_rgb
from .util import SharedData, QtLoop


class BaseGraphicsPanel:

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

    def setup_video(
            self, view_box: 'pg.ViewBox', sd: 'SharedData',
            target: Union[int, str], loop_msec: int = 33) -> None:
        imgitem = pg.ImageItem()
        view_box.addItem(imgitem)
        cap = cv2.VideoCapture(target)

        def main():
            try:
                frame = cv2.rotate(cap.read()[1], cv2.ROTATE_90_CLOCKWISE)
                imgitem.setImage(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                sd.replace(0, frame)
            except:
                cap.release()

        QtLoop.run(main, loop_msec)

    def setup_frame(
            self, view_box: 'pg.ViewBox', sd: 'SharedData',
            loop_msec: int = 500) -> None:
        imgitem = pg.ImageItem()
        view_box.addItem(imgitem)

        def main():
            img = sd.get()
            if len(img) > 0:
                imgitem.setImage(cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE))

        QtLoop.run(main, loop_msec)

    def setup_line_graph(
            self, plot_item: 'pg.PlotItem', *sds: 'SharedData',
            title: Optional[str] = None,
            xlabel: Optional[str] = None, xunit: Optional[str] = None,
            ylabel: Optional[str] = None, yunit: Optional[str] = None,
            xrange: Optional[tuple] = None, yrange: Optional[tuple] = None,
            legends: List[str] = [],
            colors: Optional[Union[List[tuple], str]] = None,
            fill: bool = False, loop_msec: int = 100) -> None:
        plot_item.setTitle(title=title)
        plot_item.setLabel(axis='bottom', text=xlabel, units=xunit)
        plot_item.setLabel(axis='left', text=ylabel, units=yunit)
        if xrange is not None:
            plot_item.setXRange(*xrange, padding=0)
        if yrange is not None:
            plot_item.setYRange(*yrange, padding=0)

        show_legend = len(legends) > 0
        ps: List[pg.PlotDataItem] = []

        if show_legend:
            leg = pg.LegendItem(offset=(35, 15), verSpacing=-10)
            leg.setParentItem(plot_item)

        for i in range(len(sds)):
            kwargs = {}
            if colors is not None:
                color = colors[i%len(colors)]
                if isinstance(color, str):
                    color = code_to_rgb(color)
                kwargs['pen'] = color
                if fill:
                    kwargs['brush'] = (*color, 50)
                    kwargs['fillLevel'] = 0.0
            _p = plot_item.plot([], **kwargs)
            ps.append(_p)
            if show_legend:
                leg.addItem(_p, legends[i])

        def main():
            for p, sd in zip(ps, sds):
                p.setData(np.array(sd.get()))

        QtLoop.run(main, loop_msec)

    def setup_scatter_plot(
            self, plot_item: 'pg.PlotItem', *sds: 'SharedData',
            title: Optional[str] = None,
            xlabel: Optional[str] = None, xunit: Optional[str] = None,
            ylabel: Optional[str] = None, yunit: Optional[str] = None,
            xrange: Optional[tuple] = None, yrange: Optional[tuple] = None,
            legends: List[str] = [],
            colors: Optional[Union[str, List[tuple], List[str]]] = None,
            loop_msec: int = 100) -> None:
        plot_item.setTitle(title=title)
        plot_item.setLabel(axis='bottom', text=xlabel, units=xunit)
        plot_item.setLabel(axis='left', text=ylabel, units=yunit)
        if xrange is not None:
            plot_item.setXRange(*xrange, padding=0)
        if yrange is not None:
            plot_item.setYRange(*yrange, padding=0)

        show_legend = len(legends) > 0
        ps: List[pg.PlotDataItem] = []

        if show_legend:
            leg = pg.LegendItem(offset=(35, 15), verSpacing=-10)
            leg.setParentItem(plot_item)

        for i in range(len(sds)):
            kwargs = {'pen': None, 'symbolSize': 10}
            if colors is not None:
                color = colors[i%len(colors)]
                if isinstance(color, str):
                    color = code_to_rgb(color)
                kwargs['symbolBrush'] = color
                kwargs['symbolPen'] = color
            _p = plot_item.plot([], **kwargs)
            ps.append(_p)
            if show_legend:
                leg.addItem(_p, legends[i])

        def main():
            for p, sd in zip(ps, sds):
                values = sd.get()
                p.setData([t[0] for t in values], [t[1] for t in values])

        QtLoop.run(main, loop_msec)


class BaseConsolePanel:

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

    def setup_console(
            self, wid: 'ConsoleWidget', sd: 'SharedData',
            loop_msec: int = 100) -> None:

        def main():
            for s in sd.get():
                wid.write(s+'\n')
            sd.clear()

        QtLoop.run(main, loop_msec)
