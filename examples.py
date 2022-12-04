from datetime import datetime
import time
import numpy as np
import pyqtgraph as pg
from pyqtgraph.console import ConsoleWidget

from util import ListContainer
from color import WHEEL_6
from panel import BaseGraphicsPanel, BaseConsolePanel
from monitor import BaseMonitor


class CustomPanel1(BaseGraphicsPanel):

    def init_vars(self) -> None:
        self.lc_video = ListContainer()
        self.lc_line = ListContainer(list_maxlen=10)
        self.lc_line2 = ListContainer(list_maxlen=10)
        self.lc_scatter_x = ListContainer(list_maxlen=3)
        self.lc_scatter_y = ListContainer(list_maxlen=3)
        self.lc_multi_lines = ListContainer(n_lists=3, list_maxlen=20)

    def init_widget(self, widget: 'pg.GraphicsLayoutWidget') -> None:
        gl = pg.GraphicsLayout()
        vbox1 = gl.addViewBox(col=0, row=0, colspan=2, lockAspect=True, defaultPadding=0.01)
        plot1 = gl.addPlot(col=0, row=1)
        plot2 = gl.addPlot(col=1, row=1)
        plot3 = gl.addPlot(col=0, row=2, colspan=2)
        widget.addItem(gl)

        self.setup_video(vbox1, self.lc_video, 0)
        self.setup_line_graph(plot1, self.lc_line, colors=[(255, 128, 0)], legends=['A'])
        self.setup_line_graph(plot1, self.lc_line2, colors=[(0, 128, 255)], legends=['B'])
        self.setup_scatter_plot(plot2, self.lc_scatter_x, self.lc_scatter_y)
        self.setup_line_graph(plot3, self.lc_multi_lines, legends=['A', 'B', 'C'])


class CustomPanel2(BaseConsolePanel):

    def init_vars(self) -> None:
        self.lc = ListContainer()

    def init_widget(self, widget: 'ConsoleWidget') -> None:
        self.setup_console(widget, self.lc)


class CustomMonitor(BaseMonitor):

    def __init__(self, panel1, panel2):
        super().__init__(title='Custom Monitor')
        self.panel1 = panel1
        self.panel2 = panel2

    def layout_panels(self, frame: 'pg.LayoutWidget') -> None:
        frame.addWidget(self.panel1.build(), col=0)
        frame.addWidget(self.panel2.build(), col=1)
        frame.layout.setColumnStretch(0, 3)
        frame.layout.setColumnStretch(1, 1)


if __name__ == '__main__':
    panel1 = CustomPanel1()
    panel2 = CustomPanel2()
    monitor = CustomMonitor(panel1, panel2)
    monitor.run_mp()

    iter = 0
    while True:
        panel1.lc_line.append(0, np.random.rand())
        panel1.lc_line2.append(0, np.random.rand())
        panel1.lc_scatter_x.append(0, np.random.rand())
        panel1.lc_scatter_y.append(0, np.random.rand())
        for idx in range(3):
            panel1.lc_multi_lines.append(idx, np.random.rand())
        panel2.lc.append(0, '[{}] log-{}'.format(
            datetime.now().timestamp(), iter))
        iter += 1
        time.sleep(1.5)
