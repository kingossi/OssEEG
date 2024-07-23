import numpy as np
import pyqtgraph as pg
from PyQt6 import QtWidgets, QtCore
from scipy import signal
import pandas as pd


class WelchAnalysisPlot(QtWidgets.QWidget):
    def __init__(self, band_d):
        super().__init__()
        self.histogramWidget = None
        self.plotWidget = None
        self.tableWidget = None
        self.band_d = band_d
        self.base_colors = [(255, 0, 0, 100), (0, 255, 0, 100), (0, 0, 255, 100), (255, 255, 0, 100),
                            (0, 255, 255, 100)]
        self.initUI()

    def initUI(self):
        main_layout = QtWidgets.QHBoxLayout()

        self.plotWidget = pg.PlotWidget(title="Welch's Power Spectral Density")
        self.plotWidget.setBackground('w')
        self.plotWidget.getAxis('left').setPen('k')
        self.plotWidget.getAxis('bottom').setPen('k')
        self.plotWidget.getAxis('left').setTextPen('k')
        self.plotWidget.getAxis('bottom').setTextPen('k')
        self.plotWidget.showGrid(x=True, y=True, alpha=0.5)
        main_layout.addWidget(self.plotWidget, 3)

        right_layout = QtWidgets.QVBoxLayout()

        self.histogramWidget = pg.PlotWidget(title="Relative Band Distribution")
        self.histogramWidget.setBackground('w')
        self.histogramWidget.getAxis('left').setPen('k')
        self.histogramWidget.getAxis('bottom').setPen('k')
        self.histogramWidget.getAxis('left').setTextPen('k')
        self.histogramWidget.getAxis('bottom').setTextPen('k')
        self.histogramWidget.showGrid(x=True, y=True, alpha=0.5)
        right_layout.addWidget(self.histogramWidget, 1)

        self.tableWidget = QtWidgets.QTableWidget()
        self.tableWidget.setStyleSheet("background-color: white;")
        self.tableWidget.setColumnWidth(1, 200)
        self.tableWidget.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Expanding)
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        right_layout.addWidget(self.tableWidget, 1)

        main_layout.addLayout(right_layout, 1)
        self.setLayout(main_layout)

        # Add the cursor line and text
        self.cursor_line = pg.InfiniteLine(angle=90, movable=False, pen='b')
        self.plotWidget.addItem(self.cursor_line)
        self.cursor_text = pg.TextItem(color='k', anchor=(0, 1))
        self.plotWidget.addItem(self.cursor_text)
        self.plotWidget.scene().sigMouseClicked.connect(self.mouseClicked)

    def plot(self, data, sf):
        self.plotWidget.clear()
        self.histogramWidget.clear()

        max_freq = 60  # Set maximum frequency to display

        if data.ndim == 2:  # Handle multi-channel data
            psd_all = []
            for channel in data:
                freqs, psd = signal.welch(channel, sf, nperseg=4 * sf)  # 4s window
                psd_all.append(psd)
            psd = np.mean(psd_all, axis=0)
        else:  # Handle single-channel data
            freqs, psd = signal.welch(data, sf, nperseg=4 * sf)  # 4s window

        # Limit the frequency range
        mask = freqs <= max_freq
        freqs = freqs[mask]
        psd = psd[mask]

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

    def mouseClicked(self, event):
        pos = event.scenePos()
        if self.plotWidget.sceneBoundingRect().contains(pos):
            mouse_point = self.plotWidget.plotItem.vb.mapSceneToView(pos)
            x_value = mouse_point.x()
            y_value = self.get_y_value(x_value)
            print(f"Mouse clicked at x={x_value:.2f}, y={y_value}")
            if y_value is not None:
                self.cursor_line.setPos(x_value)
                self.cursor_text.setText(f"({x_value:.2f}, {y_value:.2e})")
                self.cursor_text.setPos(mouse_point)
                self.cursor_text.show()
                self.plotWidget.update()

    def get_y_value(self, x_value):
        curve = self.plotWidget.plotItem.curves[0]
        data = curve.getData()
        if data is not None:
            x_data, y_data = data
            idx = (np.abs(x_data - x_value)).argmin()
            print(f"Closest index: {idx}, x_data: {x_data[idx]}, y_data: {y_data[idx]}")
            if 0 <= idx < len(y_data):
                return y_data[idx]
        print("No data found")
        return None
