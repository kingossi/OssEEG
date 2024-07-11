import numpy as np
import pyqtgraph as pg
from PyQt6 import QtWidgets, QtCore
from mne.time_frequency import psd_array_multitaper
from scipy.signal import decimate
import pandas as pd

class MultitaperPSDPlot(QtWidgets.QWidget):
    def __init__(self, band_d, downsample_factor=10):
        super().__init__()
        self.band_d = band_d
        self.downsample_factor = downsample_factor
        self.base_colors = [(255, 0, 0, 100), (0, 255, 0, 100), (0, 0, 255, 100), (255, 255, 0, 100),
                            (0, 255, 255, 100)]
        self.cache = {}
        self.initUI()

    def initUI(self):
        main_layout = QtWidgets.QHBoxLayout()

        self.plotWidget = pg.PlotWidget(title="Multitaper Power Spectral Density")
        main_layout.addWidget(self.plotWidget, 3)

        right_layout = QtWidgets.QVBoxLayout()
        self.histogramWidget = pg.PlotWidget(title="Relative Band Distribution")
        right_layout.addWidget(self.histogramWidget, 1)

        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(self.tableWidget, 1)

        main_layout.addLayout(right_layout, 1)
        self.setLayout(main_layout)

    def plot(self, data, sf):
        self.plotWidget.clear()
        self.histogramWidget.clear()

        max_freq = 60  # Set maximum frequency to display

        # Downsample the data
        data_ds = decimate(data, self.downsample_factor, axis=1)
        sf_ds = sf / self.downsample_factor

        cache_key = (tuple(data_ds.flatten()), sf_ds, max_freq)
        if cache_key in self.cache:
            freqs, psd = self.cache[cache_key]
            self._plot_results(freqs, psd)
        else:
            self.worker = MultitaperPSDWorker(data_ds, sf_ds, max_freq, self.band_d, cache_key)
            self.worker.resultReady.connect(self.handle_results)
            self.worker.start()

    def handle_results(self, freqs, psd, cache_key):
        self.cache[cache_key] = (freqs, psd)
        self._plot_results(freqs, psd)

    def _plot_results(self, freqs, psd):
        self.plotWidget.plot(freqs, psd, pen='r')

        colors = self.extend_colors(len(self.band_d))

        for idx, (band, (low, high)) in enumerate(self.band_d.items()):
            mask = (freqs >= low) & (freqs < high)
            if np.any(mask):
                color = colors[idx % len(colors)]
                self.plotWidget.plot(freqs[mask], psd[mask], fillLevel=0, brush=color, pen=None)

        self.calculate_relative_power(freqs, psd, colors)

    def extend_colors(self, num_bands):
        colors = self.base_colors * (num_bands // len(self.base_colors) + 1)
        return colors[:num_bands]

    def calculate_relative_power(self, freqs, psd, colors):
        total_power = np.trapz(psd, freqs)
        relative_powers = {}

        for band, (low, high) in self.band_d.items():
            mask = (freqs >= low) & (freqs < high)
            band_power = np.trapz(psd[mask], freqs[mask])
            relative_powers[band] = band_power / total_power

        self.update_table(relative_powers)
        self.plot_histogram(relative_powers, colors)

    def update_table(self, relative_powers):
        df = pd.DataFrame(list(relative_powers.items()), columns=['Band', 'Relative Power'])
        self.tableWidget.setRowCount(df.shape[0])
        self.tableWidget.setColumnCount(df.shape[1])
        self.tableWidget.setHorizontalHeaderLabels(df.columns)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                item = QtWidgets.QTableWidgetItem(
                    f"{df.iat[i, j]:.6f}" if isinstance(df.iat[i, j], float) else str(df.iat[i, j]))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                item.setFlags(
                    QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
                self.tableWidget.setItem(i, j, item)

    def plot_histogram(self, relative_powers, colors):
        bands = list(relative_powers.keys())
        values = list(relative_powers.values())
        brushes = [pg.mkBrush(color) for color in colors[:len(bands)]]

        bg1 = pg.BarGraphItem(x=np.arange(len(bands)), height=values, width=0.6, brushes=brushes)
        self.histogramWidget.addItem(bg1)
        self.histogramWidget.getAxis('bottom').setTicks([[(i, band) for i, band in enumerate(bands)]])


class MultitaperPSDWorker(QtCore.QThread):
    resultReady = QtCore.pyqtSignal(np.ndarray, np.ndarray, tuple)

    def __init__(self, data, sf, max_freq, band_d, cache_key):
        super().__init__()
        self.data = data
        self.sf = sf
        self.max_freq = max_freq
        self.band_d = band_d
        self.cache_key = cache_key

    def run(self):
        if self.data.ndim == 2:  # Handle multi-channel data
            psd_all = []
            for channel in self.data:
                psd, freqs = psd_array_multitaper(channel, sfreq=self.sf, fmax=self.max_freq, adaptive=True, low_bias=True, normalization='full', verbose=0)
                psd_all.append(psd)
            psd = np.mean(psd_all, axis=0)
        else:  # Handle single-channel data
            psd, freqs = psd_array_multitaper(self.data, sfreq=self.sf, fmax=self.max_freq, adaptive=True, low_bias=True, normalization='full', verbose=0)

        self.resultReady.emit(freqs, psd, self.cache_key)
