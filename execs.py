import multiprocessing as mp
import time
import numpy as np

from monitors import Monitor1
from panels import *


def main1():
    pp = PrinterPanelV1(
        cap_target=0,
        md_labels={'title': 'sensor01', 'xlabel': 'time', 'ylabel': 'value'},
        md_legends=['current', 'target'],
        pd_labels={'title': 'sensor02'},
        pd_ranges={'x': (0, 100), 'y': (0, 100)},
        histlen=15)
    cp = ConsolePanelV1()
    ip = IMDataPanelV2(
        cap1_target=1, cap2_target=2,
        d1_labels={'title': 'capture01', 'xlabel': 'length', 'ylabel': 'width', 'yunit': 'µm'},
        d2_labels={'title': 'capture02', 'xlabel': 'length', 'ylabel': 'height', 'yunit': 'µm'},
        d3_labels={'title': 'summary', 'xlabel': 'length', 'ylabel': 'width', 'yunit': 'µm'},
        histlen=15)

    mon = Monitor1('Ultimaker Live Monitor', pp, cp, ip)
    mp.Process(target=mon.run).start()
    time.sleep(3)

    for i in range(1000):
        print(i)
        pp.add_multidata(np.random.rand(), np.random.rand())
        pp.set_pairdata(np.random.randint(0, 100), np.random.randint(0, 100))
        cp.add_log(f'test {i}')
        ip.set_plot1(np.random.normal(size=100))
        ip.set_plot2(np.random.normal(size=100))
        ip.add_plot3(np.random.rand())
        time.sleep(1.0)


if __name__ == '__main__':
    main1()
