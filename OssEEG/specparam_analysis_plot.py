import gc
import hashlib

import pyqtgraph as pg
from PyQt6 import QtWidgets, QtGui, QtCore

from specparam_worker import SpecparamWorker


class SpecparamAnalysisPlot(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.min_peak_height_input = None
        self.max_n_peaks_input = None
        self.max_width_input = None
        self.min_width_input = None
        self.proxyWidget = None
        self.overlayWidget = None
        self.overlayLayout = None
        self.movie = None
        self.loadingIcon = None
        self.loadingLabel = None
        self.calculateButton = None
        self.aperiodic_curve = None
        self.specparam_curve = None
        self.specparam_plot = None
        self.periodic_curve = None
        self.plotWidget = None
        self.psd_plot = None
        self.initUI()
        self.specparam_worker = None
        self.cache = {}
        self.selected_channels = []
        self.sm = None  # Store the SpectralModel

    def initUI(self):
        layout = QtWidgets.QVBoxLayout()

        # Create plot widget
        self.plotWidget = pg.GraphicsLayoutWidget()
        self.plotWidget.setBackground('w')

        self.psd_plot = self.plotWidget.addPlot(title="Periodic Component")
        self.psd_plot.getViewBox().setBackgroundColor('w')
        self.psd_plot.getAxis('left').setPen('k')
        self.psd_plot.getAxis('bottom').setPen('k')
        self.psd_plot.getAxis('left').setTextPen('k')
        self.psd_plot.getAxis('bottom').setTextPen('k')
        self.psd_plot.showGrid(x=True, y=True, alpha=0.5)
        self.periodic_curve = self.psd_plot.plot(pen='m')

        self.specparam_plot = self.plotWidget.addPlot(title="Specparam Model Fit")
        self.specparam_plot.getViewBox().setBackgroundColor('w')
        self.specparam_plot.getAxis('left').setPen('k')
        self.specparam_plot.getAxis('bottom').setPen('k')
        self.specparam_plot.getAxis('left').setTextPen('k')
        self.specparam_plot.getAxis('bottom').setTextPen('k')
        self.specparam_plot.showGrid(x=True, y=True, alpha=0.5)
        self.specparam_curve = self.specparam_plot.plot(pen='r')
        self.aperiodic_curve = self.specparam_plot.plot(pen='g')

        layout.addWidget(self.plotWidget)

        # Add Specparam options
        options_layout = QtWidgets.QFormLayout()

        self.min_width_input = QtWidgets.QLineEdit()
        self.min_width_input.setValidator(QtGui.QIntValidator(1, 10))
        self.min_width_input.setText("1")
        options_layout.addRow('Min Peak Width:', self.min_width_input)

        self.max_width_input = QtWidgets.QLineEdit()
        self.max_width_input.setValidator(QtGui.QIntValidator(10, 100))
        self.max_width_input.setText("50")
        options_layout.addRow('Max Peak Width:', self.max_width_input)

        self.max_n_peaks_input = QtWidgets.QLineEdit()
        self.max_n_peaks_input.setValidator(QtGui.QIntValidator(1, 10))
        self.max_n_peaks_input.setText("5")
        options_layout.addRow('Max Number of Peaks:', self.max_n_peaks_input)

        self.min_peak_height_input = QtWidgets.QLineEdit()
        self.min_peak_height_input.setValidator(QtGui.QDoubleValidator(0.0, 10.0, 2))
        self.min_peak_height_input.setText("0.1")
        options_layout.addRow('Min Peak Height:', self.min_peak_height_input)

        layout.addLayout(options_layout)

        # Add "Calculate Specparam" button
        self.calculateButton = QtWidgets.QPushButton('Calculate Specparam')
        self.calculateButton.clicked.connect(self.on_calculate_button_clicked)
        layout.addWidget(self.calculateButton)

        # Add "Calculating..." label and loading animation
        self.loadingLabel = QtWidgets.QLabel("Calculating...")
        self.loadingLabel.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.loadingLabel.setVisible(False)  # Initially hidden

        self.loadingIcon = QtWidgets.QLabel()
        self.loadingIcon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.loadingIcon.setVisible(False)  # Initially hidden

        # Set up the loading animation
        self.movie = QtGui.QMovie('monki_v4.gif')
        self.movie.setScaledSize(QtCore.QSize(64, 64))  # Scale the GIF
        self.loadingIcon.setMovie(self.movie)

        # Create a layout for the overlay widget
        self.overlayLayout = QtWidgets.QVBoxLayout()
        self.overlayLayout.addWidget(self.loadingLabel)
        self.overlayLayout.addWidget(self.loadingIcon)

        # Create a widget for the overlay
        self.overlayWidget = QtWidgets.QWidget()
        self.overlayWidget.setLayout(self.overlayLayout)
        self.overlayWidget.setVisible(False)  # Initially hidden

        # Use QGraphicsProxyWidget from PyQt6.QtWidgets
        self.proxyWidget = QtWidgets.QGraphicsProxyWidget()
        self.proxyWidget.setWidget(self.overlayWidget)

        # Add the proxy widget to the plot
        self.psd_plot.scene().addItem(self.proxyWidget)
        self.proxyWidget.setPos(self.plotWidget.width() // 2 - 32, self.plotWidget.height() // 2 - 32)

        self.setLayout(layout)

    def on_calculate_button_clicked(self):
        selected_channels = self.selected_channels
        if not selected_channels:
            QtWidgets.QMessageBox.warning(self, "Warning", "No channels selected.")
            return

        data = self.get_data_for_selected_channels(selected_channels)
        sf = self.get_sampling_frequency()

        self.plot(data, sf)

    def plot(self, data, sf):
        print("Starting plot")
        self.psd_plot.clear()
        self.specparam_plot.clear()

        # Get user-defined FOOOF parameters
        min_width = int(self.min_width_input.text())
        max_width = int(self.max_width_input.text())
        max_n_peaks = int(self.max_n_peaks_input.text())
        min_peak_height = float(self.min_peak_height_input.text())

        print(f"Using parameters: min_width={min_width}, max_width={max_width}, max_n_peaks={max_n_peaks}, "
              f"min_peak_height={min_peak_height}")

        # Create a unique hash for the data and parameters to use as a cache key
        data_hash = hashlib.md5(data.tobytes()).hexdigest()
        cache_key = (data.shape, data_hash, sf, min_width, max_width, max_n_peaks, min_peak_height)

        print(f"Plotting with cache_key: {cache_key}")

        if cache_key in self.cache:
            print("Using cached data")
            freqs, modeled_spectrum, aperiodic_fit, periodic_fit = self.cache[cache_key]
            self.update_plot(freqs, modeled_spectrum, aperiodic_fit, periodic_fit)
        else:
            print("Starting SpecparamWorker")
            self.specparam_worker = SpecparamWorker(data, sf, min_width, max_width, max_n_peaks, min_peak_height)
            self.specparam_worker.specparamFinished.connect(self.update_plot_and_cache)
            self.specparam_worker.finished.connect(self.on_worker_finished)
            self.specparam_worker.start()

            # Show the loading message and animation
            self.loadingLabel.setVisible(True)
            self.loadingIcon.setVisible(True)
            self.overlayWidget.setVisible(True)
            self.movie.start()

    def on_worker_finished(self):
        print("SpecparamWorker finished")
        self.specparam_worker.deleteLater()  # Ensure the worker is properly cleaned up
        self.specparam_worker = None
        gc.collect()  # Manually trigger garbage collection to clean up any residual objects

    def update_plot_and_cache(self, freqs, modeled_spectrum, aperiodic_fit, periodic_fit):
        print("Updating plot and cache")
        data = self.specparam_worker.data
        sf = self.specparam_worker.sf

        # Get user-defined FOOOF parameters
        min_width = int(self.min_width_input.text())
        max_width = int(self.max_width_input.text())
        max_n_peaks = int(self.max_n_peaks_input.text())
        min_peak_height = float(self.min_peak_height_input.text())

        # Create a unique hash for the data and parameters to use as a cache key
        data_hash = hashlib.md5(data.tobytes()).hexdigest()
        cache_key = (data.shape, data_hash, sf, min_width, max_width, max_n_peaks, min_peak_height)

        print(f"Caching data with cache_key: {cache_key}")

        self.cache[cache_key] = (freqs, modeled_spectrum, aperiodic_fit, periodic_fit)
        self.update_plot(freqs, modeled_spectrum, aperiodic_fit, periodic_fit)
        self.sm = self.specparam_worker.sm  # Store the SpectralModel

    def update_plot(self, freqs, modeled_spectrum, aperiodic_fit, periodic_fit):
        print("Updating plot")
        self.periodic_curve.setData(freqs, periodic_fit)  # Plot periodic component
        self.specparam_curve.setData(freqs, modeled_spectrum)
        self.aperiodic_curve.setData(freqs, aperiodic_fit)

        self.psd_plot.addItem(self.periodic_curve)
        self.specparam_plot.addItem(self.specparam_curve)
        self.specparam_plot.addItem(self.aperiodic_curve)

        # Hide the loading message and animation
        self.loadingLabel.setVisible(False)
        self.loadingIcon.setVisible(False)
        self.overlayWidget.setVisible(False)
        self.movie.stop()

    def set_selected_channels(self, selected_channels):
        print(f"Selected channels updated: {selected_channels}")
        self.selected_channels = selected_channels

    def get_data_for_selected_channels(self, selected_channels):
        print(f"Getting data for selected channels: {selected_channels}")
        if not self.eeg_analyzer.channel_names:
            raise ValueError("channel_names is not set")
        channel_indices = [self.eeg_analyzer.channel_names.index(ch) for ch in selected_channels]
        return self.eeg_analyzer.data[channel_indices, :]

    def get_sampling_frequency(self):
        print("Getting sampling frequency")
        if self.eeg_analyzer.sf is None:
            raise ValueError("sampling frequency (sf) is not set")
        return self.eeg_analyzer.sf

    def generate_report(self):
        if self.sm is not None:
            print("Generating Specparam report")
            self.sm.report()
        else:
            print("No Specparam model available to generate report")

    def generate_specparam_report(self):
        if self.sm is not None:
            from io import StringIO
            import sys

            old_stdout = sys.stdout
            sys.stdout = mystdout = StringIO()

            # Generate the report
            self.sm.report()

            # Reset stdout
            sys.stdout = old_stdout

            # Get the report content
            report = mystdout.getvalue()
            return report
        else:
            return "No Specparam model available.\n"
