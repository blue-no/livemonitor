import multiprocessing as mp
import time
import numpy as np

from monitors import Monitor1
from panels import *


def main1():
    pp = PrinterPanelV1(
        cap_target=0,
        md_labels={'title': 'sensor01', 'x': 'time', 'y': 'value'},
        md_legends=['current', 'target'],
        pd_labels={'title': 'sensor02'},
        pd_ranges={'x': (0, 100), 'y': (0, 100)},
        histlen=15)
    cp = ConsolePanelV1()
    ip = IMDataPanelV1(
        d1_labels={'title': 'capture01', 'x': 'length', 'y': 'height [µm]'},
        d2_labels={'title': 'capture02', 'x': 'length', 'y': 'width [µm]'},
        d3_labels={'title': 'summary', 'x': 'length', 'y': 'width [µm]'},
        histlen=15)

    mon = Monitor1('Ultimaker Live Monitor', pp, cp, ip)
    mp.Process(target=mon.run).start()

    for i in range(1000):
        print(i)
        pp.add_multidata([np.random.rand(), np.random.rand()])
        pp.put_pairdata((np.random.randint(0, 100), np.random.randint(0, 100)))
        cp.put_log(f'test {i}')
        ip.put_image1(np.random.normal(size=(400, 300)))
        ip.put_image2(np.random.normal(size=(400, 300)))
        ip.add_plot1(np.random.rand())
        ip.add_plot2(np.random.rand())
        ip.add_plot3(np.random.rand())
        time.sleep(1.0)


if __name__ == '__main__':
    main1()
