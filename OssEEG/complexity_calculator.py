from PyQt6 import QtWidgets, QtGui

from complexity_worker import ComplexityWorker
import logging
from PyQt6.QtWidgets import QFileDialog, QDialog, QVBoxLayout

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class ComplexityCalculator:
    def __init__(self, eeg_analyzer):
        self.eeg_analyzer = eeg_analyzer
        self.complexityButton = None
        self.exportButton = None
        self.complexityLayout = None
        self.complexityWidget = None
        logging.debug('Initialized ComplexityCalculator.')

    def initUI(self, layout):
        if self.complexityButton is None:
            self.complexityButton = QtWidgets.QPushButton('Calculate Complexity')
            self.complexityButton.clicked.connect(self.calculate_complexity)
            self.complexityButton.setEnabled(False)

        if self.complexityButton.parent() is not None:
            self.complexityButton.setParent(None)

        layout.addWidget(self.complexityButton)

        if self.exportButton is None:
            self.exportButton = QtWidgets.QPushButton('Export Report')
            self.exportButton.clicked.connect(self.export_report)
            self.exportButton.setEnabled(False)

        if self.exportButton.parent() is not None:
            self.exportButton.setParent(None)

        layout.addWidget(self.exportButton)

        if self.complexityLayout is None:
            self.complexityLayout = QtWidgets.QVBoxLayout()

        if self.complexityLayout.parent() is not None:
            old_parent = self.complexityLayout.parent()
            if isinstance(old_parent, QtWidgets.QWidget):
                old_parent.layout().removeItem(self.complexityLayout)

        layout.addLayout(self.complexityLayout)

    def enable_complexity_button(self):
        if self.complexityButton is not None:
            self.complexityButton.setEnabled(True)
            logging.debug('Complexity button enabled.')

    def calculate_complexity(self):
        self.clearLayout(self.complexityLayout)
        logging.debug('Started complexity calculation.')

        self.complexityWidget = QtWidgets.QTextEdit()
        self.complexityWidget.setReadOnly(True)
        self.complexityWidget.setText("Calculating complexity measures... (This may take a while)")
        self.complexityLayout.addWidget(self.complexityWidget)

        selected_channels = [item.text() for item in self.eeg_analyzer.channel_selector.channelSelector.selectedItems()]
        selected_indices = [self.eeg_analyzer.channel_names.index(ch) for ch in selected_channels]
        selected_data = self.eeg_analyzer.data[selected_indices]
        selected_channel_names = [self.eeg_analyzer.channel_names[idx] for idx in selected_indices]

        logging.debug(f'Selected channels: {selected_channels}')

        self.complexityWorker = ComplexityWorker(selected_data, self.eeg_analyzer.sf, selected_channel_names,
                                                 downsample_factor=10)
        self.complexityWorker.complexityFinished.connect(self.display_complexity)
        self.complexityWorker.start()

    def display_complexity(self, text):
        self.complexityWidget.setText(text)
        self.exportButton.setEnabled(True)
        logging.debug('Displayed complexity results.')

    def export_report(self):
        dialog = ReportSelectionDialog(self.eeg_analyzer)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            include_complexity, include_specparam = dialog.getSelections()

            report_content = ""
            if include_complexity:
                report_content += self.complexityWidget.toPlainText() + "\n\n"

            if include_specparam:
                specparam_report = self.eeg_analyzer.graph_manager.specparamAnalysisPlot.generate_specparam_report()
                report_content += specparam_report + "\n\n"

            options = QFileDialog.Option.DontUseNativeDialog
            file_name, _ = QFileDialog.getSaveFileName(None, "Save Report", "",
                                                       "Text Files (*.txt);;All Files (*)", options=options)
            if file_name:
                with open(file_name, 'w') as file:
                    file.write(report_content)
                logging.debug(f'Report exported to {file_name}')

    @staticmethod
    def clearLayout(layout):
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)


class ReportSelectionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Select Report Sections')
        self.setGeometry(300, 300, 300, 200)
        self.layout = QVBoxLayout()

        self.complexityCheckBox = QtWidgets.QCheckBox('Include Complexity Results')
        self.specparamCheckBox = QtWidgets.QCheckBox('Include Specparam Model')

        self.layout.addWidget(self.complexityCheckBox)
        self.layout.addWidget(self.specparamCheckBox)

        self.buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def getSelections(self):
        return self.complexityCheckBox.isChecked(), self.specparamCheckBox.isChecked()
