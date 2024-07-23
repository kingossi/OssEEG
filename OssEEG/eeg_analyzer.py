import sys
import numpy as np
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QMainWindow, QSplitter, QVBoxLayout, QWidget, QMessageBox, QDialog

from channel_selector import ChannelSelector
from complexity_calculator import ComplexityCalculator
from eeg_file_handler import EEGFileHandler
from file_loader import FileLoader
from graph_manager import GraphManager
from ica_manager import ICAManager

class EEGAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.sf = 128.  # default sampling frequency
        self.band_d = {'Infra': [-np.inf, 0.1],
                       'Delta': [0.1, 4.],
                       'Theta': [4., 8.],
                       'Alpha': [8., 13.],
                       'Beta': [13., 20.],
                       'Low Gamma': [20., 50.],
                       'Hi Gamma': [50., np.inf]}
        self.file_handler = EEGFileHandler()
        self.file_loader = FileLoader(self)
        self.channel_selector = ChannelSelector(self)
        self.graph_manager = GraphManager(self)
        self.ica_manager = ICAManager(self)
        self.complexity_calculator = ComplexityCalculator(self)
        self.raw = None
        self.data = None
        self.channel_names = []  # Initialize channel_names
        self.initUI()

    def initUI(self):
        self.setWindowTitle('OssEEG')
        self.setGeometry(100, 100, 1200, 800)

        # Set the window icon
        self.setWindowIcon(QtGui.QIcon('logo.png'))

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        menu_bar = self.menuBar()

        # Adding logo to the menu bar
        logo_menu = menu_bar.addMenu('Info')

        about_action = QtGui.QAction('About', self)
        about_action.triggered.connect(self.showAboutDialog)
        logo_menu.addAction(about_action)

        terms_action = QtGui.QAction('Terms and Conditions', self)
        terms_action.triggered.connect(self.showTermsDialog)
        logo_menu.addAction(terms_action)

        file_menu = menu_bar.addMenu('File')

        load_file_action = QtGui.QAction('Load EEG File', self)
        load_file_action.triggered.connect(self.file_loader.loadFile)
        file_menu.addAction(load_file_action)

        # Adding Reporting to the menu
        report_menu = menu_bar.addMenu('Export')

        generate_report_action = QtGui.QAction('Generate Report', self)
        generate_report_action.triggered.connect(self.showReportDialog)
        report_menu.addAction(generate_report_action)

        mainSplitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        mainSplitter.setOpaqueResize(False)

        preprocWidget = QWidget()
        preprocLayout = QVBoxLayout(preprocWidget)
        preprocGroupBox = QtWidgets.QGroupBox("Preprocessing")
        preprocLayout.addWidget(preprocGroupBox)
        preprocBoxLayout = QVBoxLayout()
        preprocGroupBox.setLayout(preprocBoxLayout)

        self.ica_manager.initUI(preprocBoxLayout)

        mainSplitter.addWidget(preprocWidget)

        analysisWidget = AnalysisWidget(self)
        analysisLayout = QVBoxLayout(analysisWidget)
        analysisGroupBox = QtWidgets.QGroupBox("Data Analysis")
        analysisLayout.addWidget(analysisGroupBox)
        analysisBoxLayout = QVBoxLayout()
        analysisGroupBox.setLayout(analysisBoxLayout)

        self.graph_manager.initUI(analysisBoxLayout)

        mainSplitter.addWidget(analysisWidget)

        channelSelectWidget = QWidget()
        channelSelectLayout = QVBoxLayout(channelSelectWidget)
        channelSelectGroupBox = QtWidgets.QGroupBox("Channel Selection")
        channelSelectLayout.addWidget(channelSelectGroupBox)
        channelSelectBoxLayout = QVBoxLayout()
        channelSelectGroupBox.setLayout(channelSelectBoxLayout)

        self.channel_selector.initUI(channelSelectBoxLayout)

        mainSplitter.addWidget(channelSelectWidget)

        # Set initial sizes
        mainSplitter.setStretchFactor(0, 1)
        mainSplitter.setStretchFactor(1, 5)
        mainSplitter.setStretchFactor(2, 1)

        layout.addWidget(mainSplitter)

        self.setCentralWidget(central_widget)
        self.show()

    def showAboutDialog(self):
        QMessageBox.about(self, "About", "OssEEG\nVersion 1.0\nDeveloped by Ossi (: ")

    def showTermsDialog(self):
        QMessageBox.information(self, "Terms and Conditions", "This software is licensed under the GPL license.\nFor more details, visit https://www.gnu.org/licenses/gpl-3.0.html")

    def showReportDialog(self):
        reportDialog = QDialog(self)
        reportDialog.setWindowTitle("Reporting")
        reportDialog.setGeometry(300, 300, 600, 400)
        layout = QVBoxLayout(reportDialog)
        reportBoxLayout = QVBoxLayout()
        self.complexity_calculator.initUI(reportBoxLayout)
        layout.addLayout(reportBoxLayout)
        reportDialog.setLayout(layout)
        self.complexity_calculator.enable_complexity_button()  # Enable the button here

        # Generate Specparam report if available
        if self.graph_manager.specparamAnalysisPlot.sm is not None:
            self.graph_manager.specparamAnalysisPlot.generate_report()
        else:
            print("No Specparam model available for report generation")

        reportDialog.show()  # Use show() instead of exec() to make the dialog non-blocking

    def loadData(self, raw, data, channel_names, sf):
        self.raw = raw
        self.data = data
        self.channel_names = channel_names
        self.sf = sf
        self.channel_selector.populate_channel_selector()
        self.graph_manager.updateGraph()
        self.complexity_calculator.enable_complexity_button()  # Enable the button when data is loaded

class AnalysisWidget(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.parent.file_loader.loadFile(file_path)
        event.acceptProposedAction()
