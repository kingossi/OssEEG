import logging

logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

import logging
import matplotlib.patches as patches
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QDialog
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mne.viz import plot_ica_properties

from OssEEG.ica_worker import ICAWorker

logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)

import logging
import matplotlib.pyplot as plt
from PyQt6 import QtCore, QtGui, QtWidgets

logging.getLogger('matplotlib.font_manager').setLevel(logging.WARNING)




class ICAManager(QtWidgets.QWidget):
    def __init__(self, eeg_analyzer):
        super().__init__()
        self.icaPlotLayout = None
        self.icaButton = None
        self.eeg_analyzer = eeg_analyzer
        self.selected_components = set()
        self.axes = []
        self.canvas = None
        self.dialogs = []
        self.patches = {}
        self.ica_image_path = None
        self.loadingLabel = None
        self.loadingIcon = None
        self.movie = None

    def initUI(self, layout):
        self.icaButton = QtWidgets.QPushButton('Run ICA')
        self.icaButton.clicked.connect(self.run_ica)
        self.icaButton.setEnabled(False)
        layout.addWidget(self.icaButton)

        self.icaPlotLayout = QVBoxLayout()
        layout.addLayout(self.icaPlotLayout)

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

        layout.addWidget(self.overlayWidget)

    def enable_ica_button(self):
        self.icaButton.setEnabled(True)

    def run_ica(self):
        self.show_loading_indicator()
        self.eeg_analyzer.ica_thread = ICAWorker(self.eeg_analyzer.raw)
        self.eeg_analyzer.ica_thread.icaFinished.connect(self.handle_ica_finished)
        self.eeg_analyzer.ica_thread.start()

    def handle_ica_finished(self, ica, ica_fig):
        self.hide_loading_indicator()
        self.eeg_analyzer.ica = ica
        self.clearLayout(self.icaPlotLayout)
        self.canvas = FigureCanvas(ica_fig)
        self.icaPlotLayout.addWidget(self.canvas)

        self.axes = ica_fig.axes
        for i, ax in enumerate(self.axes):
            ax.set_picker(True)  # Enable picking on the axes
            ax.figure.canvas.mpl_connect('pick_event', self.on_pick)

        self.show_ica_exclusion_ui()

    def show_loading_indicator(self):
        self.loadingLabel.setVisible(True)
        self.loadingIcon.setVisible(True)
        self.overlayWidget.setVisible(True)
        self.movie.start()

    def hide_loading_indicator(self):
        self.loadingLabel.setVisible(False)
        self.loadingIcon.setVisible(False)
        self.overlayWidget.setVisible(False)
        self.movie.stop()

    def on_pick(self, event):
        ax = event.artist.axes
        if ax in self.axes:
            idx = self.axes.index(ax)
            if idx in self.selected_components:
                self.selected_components.remove(idx)
            else:
                self.selected_components.add(idx)
            self.update_selection()

    def update_selection(self):
        for i, ax in enumerate(self.axes):
            if i in self.selected_components:
                if i not in self.patches:
                    patch = patches.Rectangle((0, 0), 1, 1, transform=ax.transAxes,
                                              color='yellow', alpha=0.3)
                    ax.add_patch(patch)
                    self.patches[i] = patch
            else:
                if i in self.patches:
                    self.patches[i].remove()
                    del self.patches[i]
        self.canvas.draw_idle()

    def show_ica_exclusion_ui(self):
        exclusionWidget = QWidget()
        exclusionLayout = QVBoxLayout(exclusionWidget)
        exclusionLabel = QtWidgets.QLabel("Select ICA components to exclude or plot properties:")
        exclusionLayout.addWidget(exclusionLabel)

        plotPropsButton = QtWidgets.QPushButton("Plot Properties")
        plotPropsButton.clicked.connect(self.plot_selected_ica_properties)
        exclusionLayout.addWidget(plotPropsButton)

        excludeButton = QtWidgets.QPushButton("Exclude Selected")
        excludeButton.clicked.connect(self.exclude_selected_ica)
        exclusionLayout.addWidget(excludeButton)
        self.icaPlotLayout.addWidget(exclusionWidget)

    def plot_selected_ica_properties(self):
        selected_indices = list(self.selected_components)
        for index in selected_indices:
            dialog = QDialog()
            dialog.setWindowTitle(f"ICA Component {index} Properties")
            dialog.setGeometry(100, 100, 800, 600)
            layout = QVBoxLayout(dialog)

            fig, axes = plt.subplots(1, 5, figsize=(15, 3))
            plot_ica_properties(self.eeg_analyzer.ica, self.eeg_analyzer.raw, picks=[index], axes=axes)

            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)

            self.dialogs.append(dialog)
            dialog.show()

    def exclude_selected_ica(self):
        self.eeg_analyzer.ica_exclude = list(self.selected_components)
        self.update_data_excluding_ica()

    def update_data_excluding_ica(self):
        self.eeg_analyzer.ica.apply(self.eeg_analyzer.raw, exclude=self.eeg_analyzer.ica_exclude)
        self.eeg_analyzer.data = self.eeg_analyzer.raw.get_data()
        self.eeg_analyzer.graph_manager.display_data()

    @staticmethod
    def clearLayout(layout):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

