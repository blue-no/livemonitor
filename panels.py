from datetime import datetime

import pyqtgraph as pg
from pyqtgraph.console import ConsoleWidget

from base import _BasePanel
from livemonitor.base import SharedData


class PrinterPanelV1(_BasePanel):

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

        self.sd_video = self._generate_video_sd()
        self.sds_md = self._generate_timeseries_sd(
            n_plots=len(md_legends), histlen=histlen)
        self.sd_pd = self._generate_scatter_sd(
            n_plots=1, histlen=1)

    def build_widget(self):
        widget = pg.GraphicsLayoutWidget()
        layout = pg.GraphicsLayout()
        vbox = layout.addViewBox(col=0, row=0, colspan=2, lockAspect=True, defaultPadding=0.01)
        plot1 = layout.addPlot(col=0, row=1)
        plot2 = layout.addPlot(col=1, row=1)
        widget.addItem(layout)

        self._setup_video(vbox, self.sd_video, self.cap_target)
        self._setup_timeseries_plots(
            plot1, self.sds_md, title=self.md_labels.get('title', None),
            xlabel=self.md_labels.get('xlabel', None),
            ylabel=self.md_labels.get('ylabel', None),
            xunit=self.md_labels.get('xunit', None),
            yunit=self.md_labels.get('yunit', None),
            legends=self.md_legends)
        self._setup_scatter_plots(
            plot2, self.sd_pd, title=self.pd_labels.get('title', None),
            xlabel=self.pd_labels.get('xlabel', None),
            ylabel=self.pd_labels.get('ylabel', None),
            xunit=self.pd_labels.get('xunit', None),
            yunit=self.pd_labels.get('yunit', None),
            xrange=self.pd_ranges.get('x', None),
            yrange=self.pd_ranges.get('y', None),
            i_color=3)

        return widget

    def get_frame(self):
        if self.sd_video.is_empty() > 0:
            return self.sd_video.pop()
        return None

    def add_multidata(self, *vals):
        for sd, v in zip(self.sds_md, vals):
            sd.push(v)

    def set_pairdata(self, v1, v2):
        self.sd_pd[0]['x'].push(v1)
        self.sd_pd[0]['y'].push(v2)


class ConsolePanelV1(_BasePanel):

    def __init__(self, sep='\n') -> None:
        self.sep = sep
        self.widget = None
        self.sd = self._generate_console_sd()

    def build_widget(self):
        self.widget = ConsoleWidget()
        self._setup_console(self.widget, self.sd)
        return self.widget

    def add_log(self, *strings):
        string = ' '.join(list(map(str, strings)))
        self.sd.push('[{}] {}{}'.format(
            str(datetime.now().time())[:12], str(string), self.sep))


class IMDataPanelV2(_BasePanel):

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

        self.sd_video1 = self._generate_video_sd()
        self.sd_video2 = self._generate_video_sd()
        self.sds_plot1 = self._generate_timeseries_sd()
        self.sds_plot2 = self._generate_timeseries_sd()
        self.sds_plot3 = self._generate_timeseries_sd()

    def build_widget(self):
        widget = pg.GraphicsLayoutWidget()
        layout = pg.GraphicsLayout()
        widget.addItem(layout)

        vbox1 = layout.addViewBox(col=0, row=0, lockAspect=True, defaultPadding=0.01)
        vbox2 = layout.addViewBox(col=0, row=1, lockAspect=True, defaultPadding=0.01)
        plot1 = layout.addPlot(col=1, row=0)
        plot2 = layout.addPlot(col=1, row=1)
        plot3 = layout.addPlot(col=0, row=2, colspan=2)
        layout.layout.setColumnStretchFactor(0, 2)
        layout.layout.setColumnStretchFactor(1, 3)

        self._setup_video(vbox1, self.sd_video1, self.cap1_target)
        self._setup_video(vbox2, self.sd_video2, self.cap2_target)
        self._setup_timeseries_plots(
            plot1, self.sds_plot1, title=self.d1_labels.get('title', None),
            xlabel=self.d1_labels.get('xlabel', None),
            ylabel=self.d1_labels.get('ylabel', None),
            xunit=self.d1_labels.get('xunit', None),
            yunit=self.d1_labels.get('yunit', None),
            i_color=4, fill=True)
        self._setup_timeseries_plots(
            plot2, self.sds_plot2, title=self.d2_labels.get('title', None),
            xlabel=self.d2_labels.get('xlabel', None),
            ylabel=self.d2_labels.get('ylabel', None),
            xunit=self.d2_labels.get('xunit', None),
            yunit=self.d2_labels.get('yunit', None),
            i_color=4, fill=True)
        self._setup_timeseries_plots(
            plot3, self.sds_plot3, title=self.d3_labels.get('title', None),
            xlabel=self.d3_labels.get('xlabel', None),
            ylabel=self.d3_labels.get('ylabel', None),
            xunit=self.d3_labels.get('xunit', None),
            yunit=self.d3_labels.get('yunit', None),
            i_color=5, fill=True)
        return widget

    def get_frame1(self):
        if self.sd_video1.is_empty():
            return None
        return self.sd_video1.pop()

    def get_frame2(self):
        if self.sd_video2.is_empty():
            return None
        return self.sd_video2.pop()

    def set_plot1(self, values):
        self.sds_plot1[0].clear()
        self.sds_plot1[0].push(*values)

    def set_plot2(self, values):
        self.sds_plot2[0].clear()
        self.sds_plot2[0].push(*values)

    def add_plot3(self, value):
        self.sds_plot3[0].push(value)
