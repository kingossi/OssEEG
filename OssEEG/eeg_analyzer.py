import numpy as np
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtWidgets import QMainWindow, QSplitter, QVBoxLayout, QWidget

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
        self.initUI()

    def initUI(self):
        self.setWindowTitle('EEG Analysis Tool')
        self.setGeometry(100, 100, 1200, 800)

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')

        load_file_action = QtGui.QAction('Load EEG File', self)
        load_file_action.triggered.connect(self.file_loader.loadFile)
        file_menu.addAction(load_file_action)

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

        analysisWidget = QWidget()
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

        reportWidget = QWidget()
        reportLayout = QVBoxLayout(reportWidget)
        reportGroupBox = QtWidgets.QGroupBox("Reporting")
        reportLayout.addWidget(reportGroupBox)
        reportBoxLayout = QVBoxLayout()
        reportGroupBox.setLayout(reportBoxLayout)

        self.complexity_calculator.initUI(reportBoxLayout)

        mainSplitter.addWidget(reportWidget)

        layout.addWidget(mainSplitter)

        self.setCentralWidget(central_widget)
        self.show()







