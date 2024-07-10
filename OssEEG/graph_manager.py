from PyQt6 import QtWidgets
from eeg_time_series_plot import EEGTimeSeriesPlot
from welch_analysis_plot import WelchAnalysisPlot
from specparam_analysis_plot import SpecparamAnalysisPlot

class GraphManager:
    def __init__(self, eeg_analyzer):
        self.eeg_analyzer = eeg_analyzer

    def initUI(self, layout):
        self.graphSelector = QtWidgets.QComboBox()
        self.graphSelector.addItems(
            ["Time Series", "Welch Analysis", "Specparam Analysis"])
        self.graphSelector.currentIndexChanged.connect(self.updateGraph)
        layout.addWidget(self.graphSelector)

        self.eegTimeSeriesPlot = EEGTimeSeriesPlot()
        self.welchAnalysisPlot = WelchAnalysisPlot(self.eeg_analyzer.band_d)
        self.specparamAnalysisPlot = SpecparamAnalysisPlot()

        self.graphLayout = QtWidgets.QVBoxLayout()
        layout.addLayout(self.graphLayout)

    def updateGraph(self):
        self.clearLayout(self.graphLayout)
        selected_channels = [item.text() for item in self.eeg_analyzer.channel_selector.channelSelector.selectedItems()]
        if not selected_channels:
            return
        if len(selected_channels) > self.eegTimeSeriesPlot.max_display_channels:
            selected_channels = selected_channels[:self.eegTimeSeriesPlot.max_display_channels]

        current_graph = self.graphSelector.currentText()
        if current_graph == "Time Series":
            self.graphLayout.addWidget(self.eegTimeSeriesPlot)
            self.eegTimeSeriesPlot.plot(self.eeg_analyzer.data, self.eeg_analyzer.sf, self.eeg_analyzer.channel_names, selected_channels)
            self.eeg_analyzer.complexity_calculator.enable_complexity_button()
            self.eeg_analyzer.ica_manager.enable_ica_button()
        elif current_graph == "Welch Analysis":
            self.graphLayout.addWidget(self.welchAnalysisPlot)
            selected_indices = [self.eeg_analyzer.channel_names.index(ch) for ch in selected_channels]
            self.welchAnalysisPlot.plot(self.eeg_analyzer.data[selected_indices], self.eeg_analyzer.sf)
            self.eeg_analyzer.complexity_calculator.enable_complexity_button()
            self.eeg_analyzer.ica_manager.enable_ica_button()
        elif current_graph == "Specparam Analysis":
            self.graphLayout.addWidget(self.specparamAnalysisPlot)
            selected_indices = [self.eeg_analyzer.channel_names.index(ch) for ch in selected_channels]
            self.specparamAnalysisPlot.plot(self.eeg_analyzer.data[selected_indices], self.eeg_analyzer.sf)
            self.eeg_analyzer.complexity_calculator.enable_complexity_button()
            self.eeg_analyzer.ica_manager.enable_ica_button()

    @staticmethod
    def clearLayout(layout):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

    def display_data(self):
        self.updateGraph()
