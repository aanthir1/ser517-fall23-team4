import pandas as pd
from groupLabelling_ui import Ui_Dialog
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QWidget, QInputDialog, QTableWidgetItem
from PyQt5.QtCore import pyqtSignal

class Impl_GroupLabelling_Window(Ui_Dialog, QtWidgets.QMainWindow):
    """Creates Group Labeler window"""
    window_closed = pyqtSignal(str)

    def __init__(self, dataset_path):
        """Initializes Group Labeler window object"""
        super(Impl_GroupLabelling_Window, self).__init__()
        self.setupUi(self)
        self.path = dataset_path
        self.pushButton.clicked.connect(self.displayMatchingRecordsfromfile)
        self.save_dataset_button.clicked.connect(self.saveDataset)
        self.go_back_button.clicked.connect(self.goToLabeller)
        self.displayed_records_df = pd.DataFrame()

        # Add items to the comboBox
        try:
            df = pd.read_csv(dataset_path)  # Use read_excel for Excel files
            column_names = df.columns
            self.comboBox.addItems(column_names)  # Add column names directly to the comboBox
            max_width = self.comboBox.view().sizeHintForColumn(0)
            self.comboBox.view().setMinimumWidth(max_width)
            self.comboBox.currentIndexChanged.connect(self.updateDropdownItems)  # Connect the event handler
        except Exception as e:
            print("Error:", e)
    
    def updateDropdownItems(self, index):
        """Update the dropdown with unique values from the selected column"""
        selected_column = self.comboBox.currentText()  # Get the selected column name
        if selected_column:
            try:
                df = pd.read_csv(self.path)
                unique_values = df[selected_column].unique()
                self.comboBox_2.clear()  # Clear the existing items
                self.comboBox_2.addItems([str(val) for val in unique_values])
                max_width = self.comboBox_2.view().sizeHintForColumn(0)
                self.comboBox_2.view().setMinimumWidth(max_width)

            except Exception as e:
                print("Error:", e)

    def displayMatchingRecordsfromfile(self):
        key = self.comboBox.currentText()
        value = self.comboBox_2.currentText()

        if key and value:
            try:
                df = pd.read_csv(self.path)
                matching_records = df[df[key] == value]
                
                # Check if the "Output" column already exists in matching_records DataFrame and remove it
                output_column_name = "Output"
                if output_column_name in matching_records.columns:
                    matching_records.drop(columns=[output_column_name], inplace=True)
                
                num_columns = len(matching_records.columns)

                # Clear previous content in the QTableWidget
                self.tbl_MatchingRecords.setRowCount(0)
                self.tbl_MatchingRecords.setColumnCount(num_columns + 1)
                header_labels = matching_records.columns.tolist() + [output_column_name]
                self.tbl_MatchingRecords.setHorizontalHeaderLabels(header_labels)
                self.displayed_records_df = matching_records
                self.num_columns = len(self.displayed_records_df.columns)

                # Get the selected radio button
                if self.true_radio_button.isChecked():
                    output_value = True
                elif self.false_radio_button.isChecked():
                    output_value = False
                elif self.clear_button.isChecked():
                    output_value = None

                # Populate the QTableWidget with matching records and set the output value
                for i, (_, row) in enumerate(matching_records.iterrows()):
                    self.tbl_MatchingRecords.insertRow(i)
                    for j, val in enumerate(row):
                        item = QtWidgets.QTableWidgetItem(str(val))
                        self.tbl_MatchingRecords.setItem(i, j, item)
                    output_item = QtWidgets.QTableWidgetItem(str(output_value))  # Always add the "Output" value
                    self.tbl_MatchingRecords.setItem(i, num_columns, output_item)

            except Exception as e:
                print("Error:", e)


                
    def saveDataset(self):
        # Create a QMessageBox for confirmation
        confirm_msg = QMessageBox()
        confirm_msg.setIcon(QMessageBox.Warning)
        confirm_msg.setText("Are you sure you want to save the file?")
        confirm_msg.setWindowTitle("Confirmation")
        confirm_msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        
        # Show the confirmation dialog and get the user's choice
        choice = confirm_msg.exec_()
        
        if choice == QMessageBox.Ok:  # User clicked "OK"
            key = self.comboBox.currentText()
            value = self.comboBox_2.currentText()

            if key and value:
                try:
                    df = pd.read_csv(self.path)
                    matching_records = df[df[key] == value]

                    if self.true_radio_button.isChecked():
                        output_value = True
                    elif self.false_radio_button.isChecked():
                        output_value = False
                    else:
                        output_value = None

                    file_dialog = QFileDialog(self, "Save Labeled Dataset File", "", "CSV Files (*.csv)")
                    file_dialog.setAcceptMode(QFileDialog.AcceptSave)

                    if file_dialog.exec_():
                        selected_file = file_dialog.selectedFiles()[0]
                        self.path = selected_file

                        matching_records.loc[:, 'Output'] = output_value
                        matching_records.to_csv(selected_file, index=False)

                        msg = QMessageBox()
                        msg.setIcon(QMessageBox.Information)
                        msg.setText("Labeled dataset file at: {} saved successfully!".format(selected_file))
                        msg.setWindowTitle("File saved")
                        msg.exec_()

                except Exception as e:
                    print("Error:", e)
        else:
            # User clicked "Cancel" or closed the dialog, do nothing
            pass
    
    def unlabelRows(self):
        try:
            if not self.displayed_records_df.empty:
                # Iterate through displayed records and set the "Output" value to None in the QTableWidget
                for i in range(self.displayed_records_df.shape[0]):
                    self.tbl_MatchingRecords.setItem(i, self.num_columns, QTableWidgetItem("None"))  # Set the item in the "Output" column

                # Set the "Output" values to None in the displayed_records_df
                self.displayed_records_df['Output'] = "None"

            else:
                QMessageBox.information(self, "No Records", "No records to unlabel.")
        except Exception as e:
            print("Error:", e)
            
    def goToLabeller(self):
        self.close()
            
    def closeEvent(self, event):
        self.window_closed.emit(self.path)