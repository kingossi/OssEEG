from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QListWidgetItem, QDialog
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from mne.viz import plot_ica_properties

from OssEEG.ica_worker import ICAWorker


class ICAManager:
    def __init__(self, eeg_analyzer):
        self.eeg_analyzer = eeg_analyzer
        self.dialogs = []  # To keep references to the dialog windows

    def initUI(self, layout):
        self.icaButton = QtWidgets.QPushButton('Run ICA')
        self.icaButton.clicked.connect(self.run_ica)
        self.icaButton.setEnabled(False)
        layout.addWidget(self.icaButton)

        self.icaPlotLayout = QVBoxLayout()
        layout.addLayout(self.icaPlotLayout)

    def enable_ica_button(self):
        self.icaButton.setEnabled(True)

    def run_ica(self):
        self.eeg_analyzer.ica_thread = ICAWorker(self.eeg_analyzer.raw)
        self.eeg_analyzer.ica_thread.icaFinished.connect(self.handle_ica_finished)
        self.eeg_analyzer.ica_thread.start()

    def handle_ica_finished(self, ica, ica_fig):
        self.eeg_analyzer.ica = ica
        self.clearLayout(self.icaPlotLayout)
        canvas = FigureCanvas(ica_fig)
        self.icaPlotLayout.addWidget(canvas)
        self.show_ica_exclusion_ui()

    def show_ica_exclusion_ui(self):
        exclusionWidget = QWidget()
        exclusionLayout = QVBoxLayout(exclusionWidget)
        exclusionLabel = QtWidgets.QLabel("Select ICA components to exclude or plot properties:")
        exclusionLayout.addWidget(exclusionLabel)

        self.icaSelector = QtWidgets.QListWidget()
        self.icaSelector.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        for i in range(self.eeg_analyzer.ica.n_components_):
            item = QListWidgetItem(f"ICA{str(i).zfill(3)}")
            self.icaSelector.addItem(item)
        exclusionLayout.addWidget(self.icaSelector)

        plotPropsButton = QtWidgets.QPushButton("Plot Properties")
        plotPropsButton.clicked.connect(self.plot_selected_ica_properties)
        exclusionLayout.addWidget(plotPropsButton)

        excludeButton = QtWidgets.QPushButton("Exclude Selected")
        excludeButton.clicked.connect(self.exclude_selected_ica)
        exclusionLayout.addWidget(excludeButton)

        self.icaPlotLayout.addWidget(exclusionWidget)

    def plot_selected_ica_properties(self):
        selected_indices = [int(item.text().replace("ICA", "")) for item in self.icaSelector.selectedItems()]
        for index in selected_indices:
            dialog = QDialog()
            dialog.setWindowTitle(f"ICA Component {index} Properties")
            dialog.setGeometry(100, 100, 800, 600)
            layout = QVBoxLayout(dialog)

            fig, axes = plt.subplots(1, 5, figsize=(15, 3))
            plot_ica_properties(self.eeg_analyzer.ica, self.eeg_analyzer.raw, picks=[index], axes=axes)

            canvas = FigureCanvas(fig)
            layout.addWidget(canvas)

            self.dialogs.append(dialog)  # Keep a reference to the dialog
            dialog.show()  # Use show() instead of exec() to allow multiple dialogs to be open

    def exclude_selected_ica(self):
        self.eeg_analyzer.ica_exclude = [int(item.text().replace("ICA", "")) for item in self.icaSelector.selectedItems()]
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