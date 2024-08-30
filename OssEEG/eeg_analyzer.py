import logging

import joblib
from PyQt6.QtWidgets import QMainWindow, QSplitter, QVBoxLayout, QWidget, QMessageBox, QDialog

from OssEEG.ml_manager import ModelManager

logging.basicConfig(level=logging.WARNING)

from PyQt6 import QtWidgets, QtGui, QtCore
import numpy as np
from channel_selector import ChannelSelector
from complexity_calculator import ComplexityCalculator
from eeg_file_handler import EEGFileHandler
from file_loader import FileLoader
from graph_manager import GraphManager
from ica_manager import ICAManager
from scipy.stats import kurtosis

import logging

logging.basicConfig(level=logging.WARNING)


class EEGAnalyzer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.predictButton = None
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
        self.model_manager = ModelManager(self)  # Initialize ModelManager
        self.initUI()

    def initUI(self):
        self.setWindowTitle('OssEEG')
        self.setGeometry(100, 100, 1200, 800)

        # Set the window icon
        self.setWindowIcon(QtGui.QIcon('logo.png'))

        # Create the central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)

        # Create the menu bar
        menu_bar = self.menuBar()

        # Info menu
        logo_menu = menu_bar.addMenu('Info')

        about_action = QtGui.QAction('About', self)
        about_action.triggered.connect(self.showAboutDialog)
        logo_menu.addAction(about_action)

        terms_action = QtGui.QAction('Terms and Conditions', self)
        terms_action.triggered.connect(self.showTermsDialog)
        logo_menu.addAction(terms_action)

        # File menu
        file_menu = menu_bar.addMenu('File')

        load_file_action = QtGui.QAction('Load EEG File', self)
        load_file_action.triggered.connect(self.file_loader.loadFile)
        file_menu.addAction(load_file_action)

        # Export menu
        report_menu = menu_bar.addMenu('Export')

        generate_report_action = QtGui.QAction('Generate Report', self)
        generate_report_action.triggered.connect(self.showReportDialog)
        report_menu.addAction(generate_report_action)

        # Model menu
        model_menu = menu_bar.addMenu('Model')

        # Add actions for the Model menu
        load_model_action = QtGui.QAction('Load Model', self)
        load_model_action.triggered.connect(self.load_model)  # Calls load_model method
        model_menu.addAction(load_model_action)

        predict_events_action = QtGui.QAction('Predict Events', self)
        predict_events_action.triggered.connect(self.predict_events)  # Calls predict_events method
        model_menu.addAction(predict_events_action)

        # Main Splitter to divide the main window horizontally
        main_splitter = QSplitter(QtCore.Qt.Orientation.Horizontal)
        main_splitter.setOpaqueResize(False)

        # Preprocessing widget
        preproc_widget = QWidget()
        preproc_layout = QVBoxLayout(preproc_widget)
        preproc_group_box = QtWidgets.QGroupBox("Preprocessing")
        preproc_layout.addWidget(preproc_group_box)
        preproc_box_layout = QVBoxLayout()
        preproc_group_box.setLayout(preproc_box_layout)

        # Add Preprocessing Buttons
        self.add_preprocessing_buttons(preproc_box_layout)

        # Initialize ICA Manager UI
        self.ica_manager.initUI(preproc_box_layout)

        # Add preprocessing widget to splitter
        main_splitter.addWidget(preproc_widget)

        # Data Analysis widget
        analysis_widget = AnalysisWidget(self)
        analysis_layout = QVBoxLayout(analysis_widget)
        analysis_group_box = QtWidgets.QGroupBox("Data Analysis")
        analysis_layout.addWidget(analysis_group_box)
        analysis_box_layout = QVBoxLayout()
        analysis_group_box.setLayout(analysis_box_layout)

        # Initialize Graph Manager UI
        self.graph_manager.initUI(analysis_box_layout)

        # Add data analysis widget to splitter
        main_splitter.addWidget(analysis_widget)

        # Channel Selection widget
        channel_select_widget = QWidget()
        channel_select_layout = QVBoxLayout(channel_select_widget)
        channel_select_group_box = QtWidgets.QGroupBox("Channel Selection")
        channel_select_layout.addWidget(channel_select_group_box)
        channel_select_box_layout = QVBoxLayout()
        channel_select_group_box.setLayout(channel_select_box_layout)

        # Initialize Channel Selector UI
        self.channel_selector.initUI(channel_select_box_layout)

        # Add channel selection widget to splitter
        main_splitter.addWidget(channel_select_widget)

        # Set initial sizes
        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 5)
        main_splitter.setStretchFactor(2, 1)

        # Add main splitter to main layout
        main_layout.addWidget(main_splitter)

        # Set the central widget and layout
        self.setCentralWidget(central_widget)
        self.show()

    def add_preprocessing_buttons(self, layout):
        # Create a container widget for the buttons
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(0, 0, 0, 0)  # Remove margins
        button_layout.setSpacing(5)  # Small spacing between buttons

        # Low-pass filter button
        low_pass_button = QtWidgets.QPushButton('Low-Pass Filter')
        low_pass_button.clicked.connect(self.apply_low_pass_filter)
        button_layout.addWidget(low_pass_button)

        # High-pass filter button
        high_pass_button = QtWidgets.QPushButton('High-Pass Filter')
        high_pass_button.clicked.connect(self.apply_high_pass_filter)
        button_layout.addWidget(high_pass_button)

        # Custom filter button
        custom_filter_button = QtWidgets.QPushButton('Custom Filter')
        custom_filter_button.clicked.connect(self.apply_custom_filter)
        button_layout.addWidget(custom_filter_button)

        # Add the container widget to the main layout
        layout.addWidget(button_container, alignment=QtCore.Qt.AlignmentFlag.AlignTop)

    def apply_low_pass_filter(self):
        if self.raw is not None:
            self.raw.filter(None, 40., fir_design='firwin')
            self.data = self.raw.get_data()
            self.graph_manager.updateGraph()

    def apply_high_pass_filter(self):
        if self.raw is not None:
            self.raw.filter(1., None, fir_design='firwin')
            self.data = self.raw.get_data()
            self.graph_manager.updateGraph()

    def apply_custom_filter(self):
        if self.raw is not None:
            low_cutoff, ok1 = QtWidgets.QInputDialog.getDouble(self, "Custom Filter", "Enter Low Cutoff Frequency:",
                                                               1.0, 0, 1000, 2)
            high_cutoff, ok2 = QtWidgets.QInputDialog.getDouble(self, "Custom Filter", "Enter High Cutoff Frequency:",
                                                                40.0, 0, 1000, 2)
            if ok1 and ok2:
                self.raw.filter(low_cutoff, high_cutoff, fir_design='firwin')
                self.data = self.raw.get_data()
                self.graph_manager.updateGraph()

    def calculate_kurtosis(self):
        if self.data is not None:
            # Calculate kurtosis for each channel
            kurtosis_values = kurtosis(self.data, axis=1, fisher=False)
            for ch_name, kurt_value in zip(self.channel_names, kurtosis_values):
                print(f"Kurtosis for {ch_name}: {kurt_value:.4f}")
            return kurtosis_values
        else:
            QMessageBox.warning(self, "No Data", "No EEG data available for kurtosis calculation.")
            return None

    def load_model(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Load Model", "",
                                                             "All Files (*);;Pickle Files (*.pkl)")
        if file_name:
            try:
                self.model = joblib.load(file_name)  # Load scikit-learn model
                if self.predictButton is not None:
                    self.predictButton.setEnabled(True)
                    logging.info(f"Model loaded from {file_name}")
                else:
                    logging.error("Predict button is not initialized.")
            except Exception as e:
                logging.error(f"Failed to load model: {e}")
                QtWidgets.QMessageBox.critical(None, "Error", "Failed to load model.")

    def predict_events(self):
        if self.data is None:
            QMessageBox.warning(self, "Warning", "No EEG data available for prediction.")
            return

        # Use the predict method from ModelManager
        predictions = self.model_manager.predict(self.data)

        if predictions is not None:
            # Handle the predictions (e.g., display them, store them, etc.)
            print(f"Predictions: {predictions}")
            # Optionally, display predictions in the GUI or log them
        else:
            logging.error("Failed to get predictions from the model.")

    def showAboutDialog(self):
        QMessageBox.about(self, "About",
                          "OssEEG\nVersion 1.0\nDeveloped by Ossi (: \nLoading gif created by Mark Kuznetsov")

    def showTermsDialog(self):
        QMessageBox.information(self, "Terms and Conditions", "This software is licensed under the GPL license."
                                                              "\nFor more details, visit "
                                                              "https://www.gnu.org/licenses/gpl-3.0.html")

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
