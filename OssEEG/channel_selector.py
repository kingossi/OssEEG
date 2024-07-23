from PyQt6 import QtWidgets, QtCore

class ChannelSelector:
    def __init__(self, eeg_analyzer):
        self.eeg_analyzer = eeg_analyzer

    def initUI(self, layout):
        self.selectAllCheckbox = QtWidgets.QCheckBox("Select All")
        self.selectAllCheckbox.stateChanged.connect(self.toggleSelectAll)
        layout.addWidget(self.selectAllCheckbox)

        self.channelSelector = QtWidgets.QListWidget()
        self.channelSelector.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)
        self.channelSelector.itemSelectionChanged.connect(self.handleChannelSelectionChange)
        layout.addWidget(self.channelSelector)

    def populate_channel_selector(self):
        self.channelSelector.blockSignals(True)
        self.channelSelector.clear()
        for ch_name in self.eeg_analyzer.channel_names:
            item = QtWidgets.QListWidgetItem(ch_name)
            item.setSelected(True)
            self.channelSelector.addItem(item)
        self.selectAllCheckbox.setChecked(True)
        self.channelSelector.blockSignals(False)

    def toggleSelectAll(self, state):
        self.channelSelector.blockSignals(True)
        for index in range(self.channelSelector.count()):
            item = self.channelSelector.item(index)
            item.setSelected(state == QtCore.Qt.CheckState.Checked)
        self.channelSelector.blockSignals(False)
        self.eeg_analyzer.graph_manager.updateGraph()

    def handleChannelSelectionChange(self):
        selected_channels = [item.text() for item in self.channelSelector.selectedItems()]
        self.eeg_analyzer.graph_manager.specparamAnalysisPlot.set_selected_channels(selected_channels)

        if self.selectAllCheckbox.isChecked() and not all(item.isSelected() for item in self.channelSelector.findItems("*", QtCore.Qt.MatchFlag.MatchWildcard)):
            self.selectAllCheckbox.blockSignals(True)
            self.selectAllCheckbox.setChecked(False)
            self.selectAllCheckbox.blockSignals(False)
        elif not self.selectAllCheckbox.isChecked() and all(item.isSelected() for item in self.channelSelector.findItems("*", QtCore.Qt.MatchFlag.MatchWildcard)):
            self.selectAllCheckbox.blockSignals(True)
            self.selectAllCheckbox.setChecked(True)
            self.selectAllCheckbox.blockSignals(False)
        self.eeg_analyzer.graph_manager.updateGraph()
