from datetime import datetime
import time
import numpy as np
import pyqtgraph as pg
from pyqtgraph.console import ConsoleWidget

from util import SharedData
from color import Color
from panel import BaseGraphicsPanel, BaseConsolePanel
from monitor import BaseMonitor


class CustomPanel1(BaseGraphicsPanel):

    def init_vars(self) -> None:
        self.sd_video = SharedData()
        self.sd_line = SharedData()
        self.sd_scatter = SharedData(maxlen=3)
        self.sd_multi1 = SharedData(maxlen=20)
        self.sd_multi2 = SharedData(maxlen=20)
        self.sd_multi3 = SharedData(maxlen=20)

    def init_widget(self, widget: 'pg.GraphicsLayoutWidget') -> None:
        gl = pg.GraphicsLayout()
        vbox1 = gl.addViewBox(col=0, row=0, colspan=2,
                              lockAspect=True, defaultPadding=0.01)
        plot1 = gl.addPlot(col=0, row=1)
        plot2 = gl.addPlot(col=1, row=1)
        plot3 = gl.addPlot(col=0, row=2, colspan=2)
        widget.addItem(gl)

        self.setup_video(vbox1, self.sd_video, 0)
        self.setup_line_graph(
            plot1, self.sd_line, title='Line Graph',
            xlabel='time', xunit='s')
        self.setup_scatter_plot(
            plot2, self.sd_scatter, title='Scatter Plot',
            xunit='mm', yunit='mm', xrange=(0, 1), yrange=(0, 1),
            colors=Color.BLUE)
        self.setup_line_graph(
            plot3, self.sd_multi1, self.sd_multi2, self.sd_multi3,
            colors=Color.WHEEL12, legends=['A', 'B', 'C'], fill=True)


class CustomPanel2(BaseConsolePanel):

    def init_vars(self) -> None:
        self.sd = SharedData()

    def init_widget(self, widget: 'ConsoleWidget') -> None:
        self.setup_console(widget, self.sd)


class CustomMonitor(BaseMonitor):

    def __init__(self, panel1, panel2):
        super().__init__(title='Custom Monitor')
        self.panel1 = panel1
        self.panel2 = panel2

    def init_panels(self, frame: 'pg.LayoutWidget') -> None:
        frame.addWidget(self.panel1.build(), col=0)
        frame.addWidget(self.panel2.build(), col=1)
        frame.layout.setColumnStretch(0, 2)
        frame.layout.setColumnStretch(1, 1)


if __name__ == '__main__':
    panel1 = CustomPanel1()
    panel2 = CustomPanel2()
    monitor = CustomMonitor(panel1, panel2)
    monitor.run_mp()

    iter = 0
    while True:
        panel1.sd_line.push(np.random.rand())
        panel1.sd_scatter.push((np.random.rand(), np.random.rand()))

        panel1.sd_multi1.push(np.random.rand())
        panel1.sd_multi2.push(np.random.rand())
        panel1.sd_multi3.push(np.random.rand())

        panel2.sd.push('[{}] log-{}'.format(datetime.now().timestamp(), iter))
        iter += 1
        time.sleep(1)
