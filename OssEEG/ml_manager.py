import numpy as np
import logging
from PyQt6 import QtWidgets
from keras.src.saving import load_model

logging.basicConfig(level=logging.WARNING)


class ModelManager:
    def __init__(self, eeg_analyzer):
        self.eeg_analyzer = eeg_analyzer
        self.model = None
        self.modelButton = None
        self.predictButton = None

    def initUI(self, layout):
        self.modelButton = QtWidgets.QPushButton('Load Model')
        self.modelButton.clicked.connect(self.load_model)
        layout.addWidget(self.modelButton)

        self.predictButton = QtWidgets.QPushButton('Predict Events')
        self.predictButton.clicked.connect(self.predict_events)
        self.predictButton.setEnabled(False)
        layout.addWidget(self.predictButton)

    def load_model(self):
        options = QtWidgets.QFileDialog.Options()
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Load Model", "",
                                                             "All Files (*);;H5 Files (*.h5);;Pickle Files (*.pkl)",
                                                             options=options)
        if file_name:
            try:
                self.model = load_model(file_name)  # Load Keras model
                # If using scikit-learn, use joblib or pickle
                # from sklearn.externals import joblib
                # self.model = joblib.load(file_name)
                self.predictButton.setEnabled(True)
                logging.info(f"Model loaded from {file_name}")
            except Exception as e:
                logging.error(f"Failed to load model: {e}")
                QtWidgets.QMessageBox.critical(None, "Error", "Failed to load model.")

    def predict_events(self):
        if self.model is None:
            QtWidgets.QMessageBox.warning(None, "Warning", "No model loaded.")
            return

        data = self.eeg_analyzer.data
        predictions = self.model.predict(data)

        self.display_predictions(predictions)

    def display_predictions(self, predictions):
        # Implement how to display predictions
        # For example, print them or display in a text widget
        print(predictions)
        QtWidgets.QMessageBox.information(None, "Predictions", str(predictions))
