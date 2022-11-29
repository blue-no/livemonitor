from datetime import datetime
import multiprocessing as mp
import cv2
import numpy as np

import pyqtgraph as pg
from pyqtgraph.console import ConsoleWidget

from common import QLoop


COLORS = (
    (215, 86, 116),
    (251, 141, 61),
    (217, 200, 27),
    (0, 165, 131),
    (0, 125, 175),
    (139, 99, 172)
)


class PrinterPanelV1:

    def __init__(
            self, cap_target=0,
            md_labels=None, md_legends=[],
            pd_labels=None, pd_ranges=(),
            histlen=10) -> None:
        self.cap_target = cap_target
        self.md_labels = md_labels
        self.md_legends = md_legends
        self.pd_labels = pd_labels
        self.pd_ranges = pd_ranges
        self.histlen = histlen
        self.__init_var()

    def build_widget(self):
        widget = pg.GraphicsLayoutWidget()
        layout = pg.GraphicsLayout()
        self.vbox = layout.addViewBox(col=0, row=0, colspan=2, lockAspect=True, defaultPadding=0.01)
        self.plot1 = layout.addPlot(col=0, row=1)
        self.plot2 = layout.addPlot(col=1, row=1)
        self.__setup_video()
        self.__setup_multidata()
        self.__setup_pairdata()
        widget.addItem(layout)
        return widget

    def __init_var(self):
        manager = mp.Manager()
        self.multi_data = manager.list()
        self.pair_data = manager.dict()
        for _ in range(len(self.md_legends)):
            self.multi_data.append(manager.list())

    def __setup_video(self):
        imgitem = pg.ImageItem()
        self.vbox.addItem(imgitem)
        cap = cv2.VideoCapture(self.cap_target)

        def main():
            try:
                frame = cv2.rotate(cv2.cvtColor(
                    cap.read()[1], cv2.COLOR_BGR2RGB),
                    cv2.ROTATE_90_CLOCKWISE)
                imgitem.setImage(frame)
            except:
                cap.release()
        QLoop.run(main, 100)

    def __setup_multidata(self):
        self.plot1.setTitle(self.md_labels.get('title', None))
        self.plot1.setLabel('bottom', self.md_labels.get('x', None))
        self.plot1.setLabel('left', self.md_labels.get('y', None))
        leg = pg.LegendItem(offset=(35, 15), verSpacing=-10)
        leg.setParentItem(self.plot1)
        ps = []

        for i, label in enumerate(self.md_legends):
            p = self.plot1.plot([], pen=COLORS[i])
            ps.append(p)
            leg.addItem(p, label)

        def main():
            for p, q in zip(ps, self.multi_data):
                del q[:-self.histlen]
                p.setData(list(q))
        QLoop.run(main, 100)

    def __setup_pairdata(self):
        self.plot2.setTitle(self.pd_labels.get('title', None))
        self.plot2.setLabel('bottom', self.pd_labels.get('x', None))
        self.plot2.setLabel('left', self.pd_labels.get('y', None))
        self.plot2.setXRange(*self.pd_ranges.get('x', None), padding=0)
        self.plot2.setYRange(*self.pd_ranges.get('x', None), padding=0)
        p = self.plot2.plot([], symbolBrush=COLORS[3], symbolPen=None, symbolSize=10)

        def main():
            if len(self.pair_data) < 2:
                return
            x, y = self.pair_data[0], self.pair_data[1]
            p.setData([x], [y])
        QLoop.run(main, 100)

    def add_multidata(self, data=[]):
        for q, d in zip(self.multi_data, data):
            q.append(d)

    def put_pairdata(self, data=()):
        self.pair_data[0] = data[0]
        self.pair_data[1] = data[1]


class ConsolePanelV1:

    def __init__(self, sep='\n') -> None:
        self.sep = sep
        self.widget = None
        self.__init_var()

    def build_widget(self):
        self.widget = ConsoleWidget()
        self.__setup_console()
        return self.widget

    # def add_variable(self, var, txt):
    #     self.space[txt] = var

    def __init_var(self):
        self.lines = mp.Manager().list()
        # self.space = mp.Manager().dict()

    def __setup_console(self):
        def main():
            for s in self.lines:
                self.widget.write(s)
            del self.lines[:]

            # for key, obj in self.space.items():
            #     self.widget.localNamespace.update({key: obj})
            #     self.widget.write('{}={}'.format(key, obj))
            #     del self.space[key]
        QLoop.run(main, 100)

    def put_log(self, *strings):
        string = ' '.join(list(map(str, strings)))
        self.lines.append('[{}] {}{}'.format(
            str(datetime.now().time())[:12], str(string), self.sep))


class IMDataPanelV1:

    def __init__(
            self, d1_labels=None, d2_labels=None, d3_labels=None,
            histlen=10) -> None:
        self.d1_labels = d1_labels
        self.d2_labels = d2_labels
        self.d3_labels = d3_labels
        self.histlen = histlen
        self.__init_var()

    def build_widget(self):
        widget = pg.GraphicsLayoutWidget()
        layout = pg.GraphicsLayout()
        self.vbox1 = layout.addViewBox(col=0, row=0, lockAspect=True, defaultPadding=0.01)
        self.vbox2 = layout.addViewBox(col=0, row=1, lockAspect=True, defaultPadding=0.01)
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

    def __init_var(self):
        manager = mp.Manager()
        self.frame1 = mp.Queue(maxsize=1)
        self.frame2 = mp.Queue(maxsize=1)
        self.data1 = manager.list()
        self.data2 = manager.list()
        self.data3 = manager.list()

    def __setup_image1(self):
        imgitem = pg.ImageItem()
        self.vbox1.addItem(imgitem)

        def main():
            img = self.frame1
            if not img.empty():
                imgitem.setImage(np.array(img.get()))
        QLoop.run(main, 100)

    def __setup_image2(self):
        imgitem = pg.ImageItem()
        self.vbox2.addItem(imgitem)

        def main():
            img = self.frame2
            if not img.empty():
                imgitem.setImage(np.array(img.get()))
        QLoop.run(main, 100)

    def __setup_plot1(self):
        self.plot1.setTitle(self.d1_labels.get('title', None))
        self.plot1.setLabel('bottom', self.d1_labels.get('x', None))
        self.plot1.setLabel('left', self.d1_labels.get('y', None))
        p = self.plot1.plot([], pen=COLORS[4], fillLevel=0.0, brush=(*COLORS[4], 100))

        def main():
            del self.data1[:-self.histlen]
            p.setData(list(self.data1))
        QLoop.run(main, 100)

    def __setup_plot2(self):
        self.plot2.setTitle(self.d2_labels.get('title', None))
        self.plot2.setLabel('bottom', self.d2_labels.get('x', None))
        self.plot2.setLabel('left', self.d2_labels.get('y', None))
        p = self.plot2.plot([], pen=COLORS[4], fillLevel=0.0, brush=(*COLORS[4], 100))

        def main():
            del self.data2[:-self.histlen]
            p.setData(list(self.data2))
        QLoop.run(main, 100)

    def __setup_plot3(self):
        self.plot3.setTitle(self.d3_labels.get('title', None))
        self.plot3.setLabel('bottom', self.d3_labels.get('x', None))
        self.plot3.setLabel('left', self.d3_labels.get('y', None))
        p = self.plot3.plot([], pen=COLORS[5], fillLevel=0.0, brush=(*COLORS[5], 100))

        def main():
            del self.data3[:-self.histlen]
            p.setData(list(self.data3))
        QLoop.run(main, 100)

    def put_image1(self, img):
        self.frame1.put(img)

    def put_image2(self, img):
        self.frame2.put(img)

    def add_plot1(self, data):
        self.data1.append(data)

    def add_plot2(self, data):
        self.data2.append(data)

    def add_plot3(self, data):
        self.data3.append(data)


class IMDataPanelV2:

    def __init__(
            self, cap1_target, cap2_target,
            d1_labels=None, d2_labels=None, d3_labels=None,
            histlen=10) -> None:
        self.cap1_target = cap1_target
        self.cap2_target = cap2_target
        self.d1_labels = d1_labels
        self.d2_labels = d2_labels
        self.d3_labels = d3_labels
        self.histlen = histlen
        self.__init_var()

    def build_widget(self):
        widget = pg.GraphicsLayoutWidget()
        layout = pg.GraphicsLayout()
        self.vbox1 = layout.addViewBox(col=0, row=0, lockAspect=True, defaultPadding=0.01)
        self.vbox2 = layout.addViewBox(col=0, row=1, lockAspect=True, defaultPadding=0.01)
        self.plot1 = layout.addPlot(col=1, row=0)
        self.plot2 = layout.addPlot(col=1, row=1)
        self.plot3 = layout.addPlot(col=0, row=2, colspan=2)
        self.__setup_video1()
        self.__setup_plot1()
        self.__setup_video2()
        self.__setup_plot2()
        self.__setup_plot3()
        widget.addItem(layout)
        layout.layout.setColumnStretchFactor(0, 2)
        layout.layout.setColumnStretchFactor(1, 3)
        return widget

    def __init_var(self):
        manager = mp.Manager()
        self.frame1 = manager.list()
        self.frame2 = manager.list()
        self.data1 = manager.list()
        self.data2 = manager.list()
        self.data3 = manager.list()

    def __setup_video1(self):
        imgitem = pg.ImageItem()
        self.vbox1.addItem(imgitem)
        cap = cv2.VideoCapture(self.cap1_target)

        def main():
            try:
                frame = cap.read()[1]
                imgitem.setImage(
                    cv2.cvtColor(cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE),
                                 cv2.COLOR_BGR2RGB))
                self.frame1.append(frame)
                del self.frame1[:-1]
            except:
                cap.release()
        QLoop.run(main, 100)

    def __setup_video2(self):
        imgitem = pg.ImageItem()
        self.vbox2.addItem(imgitem)
        cap = cv2.VideoCapture(self.cap2_target)

        def main():
            try:
                frame = cap.read()[1]
                imgitem.setImage(
                    cv2.cvtColor(cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE),
                                 cv2.COLOR_BGR2RGB))
                self.frame2.append(frame)
                del self.frame2[:-1]
            except:
                cap.release()
        QLoop.run(main, 100)

    def __setup_plot1(self):
        self.plot1.setTitle(self.d1_labels.get('title', None))
        self.plot1.setLabel('bottom', self.d1_labels.get('x', None))
        self.plot1.setLabel('left', self.d1_labels.get('y', None))
        p = self.plot1.plot([], pen=COLORS[4], fillLevel=0.0, brush=(*COLORS[4], 100))

        def main():
            p.setData(list(self.data1))
        QLoop.run(main, 100)

    def __setup_plot2(self):
        self.plot2.setTitle(self.d2_labels.get('title', None))
        self.plot2.setLabel('bottom', self.d2_labels.get('x', None))
        self.plot2.setLabel('left', self.d2_labels.get('y', None))
        p = self.plot2.plot([], pen=COLORS[4], fillLevel=0.0, brush=(*COLORS[4], 100))

        def main():
            p.setData(list(self.data2))
        QLoop.run(main, 100)

    def __setup_plot3(self):
        self.plot3.setTitle(self.d3_labels.get('title', None))
        self.plot3.setLabel('bottom', self.d3_labels.get('x', None))
        self.plot3.setLabel('left', self.d3_labels.get('y', None))
        p = self.plot3.plot([], pen=COLORS[5], fillLevel=0.0, brush=(*COLORS[5], 100), symbolPen=None, symbolBrush=COLORS[5], symbolSize=10)

        def main():
            del self.data3[:-self.histlen]
            p.setData(list(self.data3))
        QLoop.run(main, 100)

    def get_frame1(self):
        if len(self.frame1) == 0:
            return None
        return np.array(self.frame1[0], dtype=np.uint8)

    def get_frame2(self):
        if len(self.frame2) == 0:
            return None
        return np.array(self.frame2[0], dtype=np.uint8)

    def put_plot1(self, data):
        del self.data1[:]
        self.data1 += data

    def put_plot2(self, data):
        del self.data2[:]
        self.data2 += data

    def add_plot3(self, data):
        self.data3.append(data)
