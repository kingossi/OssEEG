from PyQt6 import QtWidgets, QtGui
from PyQt6.QtWidgets import QFileDialog, QDialog, QVBoxLayout
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')


class ReportSelectionDialog(QDialog):
    def __init__(self, eeg_analyzer, parent=None):
        super().__init__(parent)
        self.eeg_analyzer = eeg_analyzer
        self.setWindowTitle('Select Report Sections')
        self.setGeometry(300, 300, 300, 200)
        self.layout = QVBoxLayout()

        self.complexityCheckBox = QtWidgets.QCheckBox('Include Complexity Results')
        self.specparamCheckBox = QtWidgets.QCheckBox('Include Specparam Model')
        self.icaCheckBox = QtWidgets.QCheckBox('Include ICA Components')

        self.layout.addWidget(self.complexityCheckBox)
        self.layout.addWidget(self.specparamCheckBox)
        self.layout.addWidget(self.icaCheckBox)

        self.buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok | QtWidgets.QDialogButtonBox.StandardButton.Cancel)
        self.buttonBox.accepted.connect(self.export_report)
        self.buttonBox.rejected.connect(self.reject)

        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def getSelections(self):
        return self.complexityCheckBox.isChecked(), self.specparamCheckBox.isChecked(), self.icaCheckBox.isChecked()

    def export_report(self):
        include_complexity, include_specparam, include_ica = self.getSelections()

        report_content = "<html><head><title>EEG Analysis Report</title></head><body>"
        if include_complexity:
            complexity_text = self.eeg_analyzer.complexity_calculator.complexityWidget.toPlainText()
            report_content += "<h2>Complexity Measures:</h2><pre>" + complexity_text + "</pre><br>"

        if include_specparam:
            specparam_report = self.eeg_analyzer.graph_manager.specparamAnalysisPlot.generate_specparam_report()
            report_content += "<h2>Specparam Model:</h2><pre>" + specparam_report + "</pre><br>"

        if include_ica and self.eeg_analyzer.ica_manager.ica_image_path:
            report_content += "<h2>ICA Components:</h2>"
            report_content += f"<img src='{self.eeg_analyzer.ica_manager.ica_image_path}' alt='ICA Components'><br>"

        report_content += "</body></html>"

        options = QFileDialog.Option.DontUseNativeDialog
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Report", "",
                                                   "HTML Files (*.html);;All Files (*)", options=options)
        if file_name:
            if not file_name.endswith(".html"):
                file_name += ".html"
            with open(file_name, 'w') as file:
                file.write(report_content)
            logging.debug(f'Report exported to {file_name}')

        self.accept()
