

## OssEEG: EEG Analysis 

OssEEG is a graphical user interface (GUI) application for processing, analyzing, and visualizing electroencephalogram (EEG) data. It is designed for researchers and practitioners who want to easily load EEG data, apply various preprocessing techniques, perform Independent Component Analysis (ICA), and visualize the results.

## Features

EEG File Loading: Supports loading of EEG data files in multiple formats.
Preprocessing Tools: Includes tools for low-pass filtering, high-pass filtering, and custom filtering of EEG data.
ICA Analysis: Allows users to run ICA on EEG data to identify and isolate independent components.
Component Visualization: Provides visualization of ICA component properties and associated EEG traces in a user-friendly GUI.
Multi-Component Visualization: Supports simultaneous display of multiple ICA components in separate windows.
Reporting and Exporting: Generate and export analysis reports.


## Installing the Project

Clone the Repository

bash
Copy code
git clone https://github.com/kingossi/OssEEG.git
cd OssEEG
Create and Activate a Virtual Environment

bash
Copy code
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install Required Packages

bash
Copy code
python main.py
Loading EEG Data

Click on File > Load EEG File from the menu bar.
Choose the EEG data file from your local file system. Supported formats include .fif, .edf, .bdf, and others compatible with MNE.

## Preprocessing EEG Data

Use the Preprocessing panel on the left side to apply filters to the EEG data:
Low-Pass Filter: Removes high-frequency noise.
High-Pass Filter: Removes low-frequency drift.
Custom Filter: Define your own filter parameters.
Running ICA
Click the Run ICA button in the Preprocessing panel.
A loading animation will appear while ICA is computed. Upon completion, a visualization of ICA components will be displayed.
Visualizing ICA Components
Select the ICA components of interest from the displayed list.
Click Plot Properties to open a new window showing the properties of the selected components, including topography, ERP/ERF, power spectrum, and more.
To view multiple ICA components simultaneously, select multiple components and click Plot Properties again. Each component will pop up in a separate window.
Excluding ICA Components
Select the components to exclude by clicking on them.
Click Exclude Selected to remove the selected ICA components from the EEG data.
Exporting Reports
Click on Export > Generate Report from the menu bar.
Follow the prompts to generate and save an analysis report.

## Contributing

Contributions to OssEEG are welcome! If you would like to contribute, please follow these steps:

Fork the repository.
Create a new branch for your feature or bugfix.
bash
Copy code
git checkout -b feature-name
Make your changes and commit them with descriptive messages.
bash
Copy code
git commit -m "Add feature X"
Push your branch to your forked repository.
bash
Copy code
git push origin feature-name
Submit a pull request to the main branch of the original repository.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Contact

For questions, suggestions, or issues, please open an issue on the GitHub repository or contact me directly.

## Acknowledgments

MNE-Python team for providing excellent tools for EEG analysis.
PyQt developers for the robust GUI framework.
Vincenzo Marra for his invaluable feedback and support
