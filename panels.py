from datetime import datetime
import multiprocessing as mp
import cv2
import numpy as np

import pyqtgraph as pg
from pyqtgraph.console import ConsoleWidget

from common import QLoop


C = (
    (215, 86, 116),
    (251, 141, 61),
    (217, 200, 27),
    (0, 165, 131),
    (0, 125, 175),
    (139, 99, 172)
)


class PrinterPanel:

    def __init__(
            self, manager, cap_target=0,
            md_labels=None, md_legends=[],
            pd_labels=None, pd_ranges=(),
            histlen=10) -> None:
        self.cap_target = cap_target
        self.md_labels = md_labels
        self.md_legends = md_legends
        self.pd_labels = pd_labels
        self.pd_ranges = pd_ranges
        self.histlen = histlen
        self.__init_var(manager)

    def build_widget(self, manager=None):
        widget = pg.GraphicsLayoutWidget()
        layout = pg.GraphicsLayout()
        self.vbox = layout.addViewBox(col=0, row=0, colspan=2, lockAspect=True)
        self.plot1 = layout.addPlot(col=0, row=1)
        self.plot2 = layout.addPlot(col=1, row=1)
        self.__setup_video()
        self.__setup_multidata()
        self.__setup_pairdata()
        widget.addItem(layout)
        return widget

    def __init_var(self, manager):
        self.__d1 = []
        self.__d2 = mp.Queue(maxsize=1)
        for _ in range(len(self.md_legends)):
            self.__d1.append(manager.list())

    def __setup_video(self):
        img = pg.ImageItem()
        self.vbox.addItem(img)
        cap = cv2.VideoCapture(self.cap_target)

        def main():
            try:
                frame = cv2.rotate(cv2.cvtColor(
                    cap.read()[1], cv2.COLOR_BGR2RGB),
                    cv2.ROTATE_90_CLOCKWISE)
                img.setImage(frame)
            except:
                cap.release()
        QLoop.run(main, 10)

    def __setup_multidata(self):
        self.plot1.setTitle(self.md_labels.get('title', None))
        self.plot1.setLabel('bottom', self.md_labels.get('x', None))
        self.plot1.setLabel('left', self.md_labels.get('y', None))
        leg = pg.LegendItem(offset=(35, 15), verSpacing=-10)
        leg.setParentItem(self.plot1)
        ps = []

        for i, label in enumerate(self.md_legends):
            p = self.plot1.plot([], pen=C[i])
            ps.append(p)
            leg.addItem(p, label)

        def main():
            for p, q in zip(ps, self.__d1):
                del q[:-self.histlen]
                p.setData(list(q))
        QLoop.run(main, 100)

    def __setup_pairdata(self):
        self.plot2.setTitle(self.pd_labels.get('title', None))
        self.plot2.setLabel('bottom', self.pd_labels.get('x', None))
        self.plot2.setLabel('left', self.pd_labels.get('y', None))
        self.plot2.setXRange(*self.pd_ranges.get('x', None), padding=0)
        self.plot2.setYRange(*self.pd_ranges.get('x', None), padding=0)
        p = self.plot2.plot([], symbolBrush=C[3])

        def main():
            if self.__d2.empty():
                return
            x, y = self.__d2.get()
            p.setData([x], [y])
        QLoop.run(main, 100)

    def add_multidata(self, data=[]):
        for q, d in zip(self.__d1, data):
            q.append(d)

    def put_pairdata(self, data=()):
        self.__d2.put(data)


class ConsolePanel:

    def __init__(self, manager, sep='\n') -> None:
        self.sep = sep
        self.widget = None
        self.__init_var()

    def build_widget(self, manager=None):
        self.widget = ConsoleWidget()
        self.__setup_console()
        return self.widget

    def __init_var(self):
        self.__q = mp.Queue()

    def __setup_console(self):
        def main():
            while not self.__q.empty():
                self.widget.write(self.__q.get())
        QLoop.run(main, 100)

    def put_log(self, string):
        self.__q.put('[{}] {}{}'.format(
            str(datetime.now().time())[:12], str(string), self.sep))


class IMDataPanel:

    def __init__(
            self, manager,
            d1_labels=None, d2_labels=None, d3_labels=None,
            histlen=10) -> None:
        self.d1_labels = d1_labels
        self.d2_labels = d2_labels
        self.d3_labels = d3_labels
        self.histlen = histlen
        self.__init_var(manager)

    def build_widget(self, manager=None):
        widget = pg.GraphicsLayoutWidget()
        layout = pg.GraphicsLayout()
        self.vbox1 = layout.addViewBox(col=0, row=0, lockAspect=True)
        self.vbox2 = layout.addViewBox(col=0, row=1, lockAspect=True)
        self.plot1 = layout.addPlot(col=1, row=0)
        self.plot2 = layout.addPlot(col=1, row=1)
        self.plot3 = layout.addPlot(col=0, row=2, colspan=2)
        self.__setup_image1()
        self.__setup_plot1()
        self.__setup_image2()
        self.__setup_plot2()
        self.__setup_plot3()
        widget.addItem(layout)
        layout.layout.setColumnStretchFactor(0, 2)
        layout.layout.setColumnStretchFactor(1, 3)
        return widget

    def __init_var(self, manager):
        self.__img1 = mp.Queue(maxsize=1)
        self.__img2 = mp.Queue(maxsize=1)
        self.__q1 = manager.list()
        self.__q2 = manager.list()
        self.__q3 = manager.list()

    def __setup_image1(self):
        imgitem = pg.ImageItem()
        self.vbox1.addItem(imgitem)

        def main():
            img = self.__img1
            if not img.empty():
                imgitem.setImage(np.array(img.get()))
        QLoop.run(main, 100)

    def __setup_image2(self):
        imgitem = pg.ImageItem()
        self.vbox2.addItem(imgitem)

        def main():
            img = self.__img2
            if not img.empty():
                imgitem.setImage(np.array(img.get()))
        QLoop.run(main, 100)

    def __setup_plot1(self):
        self.plot1.setTitle(self.d1_labels.get('title', None))
        self.plot1.setLabel('bottom', self.d1_labels.get('x', None))
        self.plot1.setLabel('left', self.d1_labels.get('y', None))
        p = self.plot1.plot([], pen=C[4], fillLevel=0.0, brush=(*C[4], 100))

        def main():
            nonlocal p
            del self.__q1[:-self.histlen]
            p.setData(list(self.__q1))
        QLoop.run(main, 100)

    def __setup_plot2(self):
        self.plot2.setTitle(self.d2_labels.get('title', None))
        self.plot2.setLabel('bottom', self.d2_labels.get('x', None))
        self.plot2.setLabel('left', self.d2_labels.get('y', None))
        p = self.plot2.plot([], pen=C[4], fillLevel=0.0, brush=(*C[4], 100))

        def main():
            del self.__q2[:-self.histlen]
            p.setData(list(self.__q2))
        QLoop.run(main, 100)

    def __setup_plot3(self):
        self.plot3.setTitle(self.d3_labels.get('title', None))
        self.plot3.setLabel('bottom', self.d3_labels.get('x', None))
        self.plot3.setLabel('left', self.d3_labels.get('y', None))
        p = self.plot3.plot([], pen=C[5], fillLevel=0.0, brush=(*C[5], 100))

        def main():
            del self.__q3[:-self.histlen]
            p.setData(list(self.__q3))
        QLoop.run(main, 100)

    def put_image1(self, img):
        self.__img1.put(img)

    def put_image2(self, img):
        self.__img2.put(img)

    def add_plot1(self, data):
        self.__q1.append(data)

    def add_plot2(self, data):
        self.__q2.append(data)

    def add_plot3(self, data):
        self.__q3.append(data)
