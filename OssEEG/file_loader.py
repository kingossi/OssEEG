from PyQt6 import QtWidgets


class FileLoader:
    def __init__(self, eeg_analyzer):
        self.eeg_analyzer = eeg_analyzer

    def loadFile(self, file_path=None):
        if not file_path:
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self.eeg_analyzer, "Open EEG File", "", "EEG Files (*.fif *.eeg *.edf);;All Files (*)")

        if file_path:
            try:
                self.eeg_analyzer.raw, self.eeg_analyzer.data = self.eeg_analyzer.file_handler.load_file(file_path)
                self.eeg_analyzer.sf = int(self.eeg_analyzer.raw.info['sfreq'])
                self.eeg_analyzer.channel_names = self.eeg_analyzer.raw.info['ch_names']
                self.eeg_analyzer.channel_selector.populate_channel_selector()
                self.eeg_analyzer.graph_manager.display_data()
                self.eeg_analyzer.ica_manager.enable_ica_button()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self.eeg_analyzer, "File Load Error", str(e))
