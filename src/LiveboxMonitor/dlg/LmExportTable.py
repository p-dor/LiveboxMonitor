### Livebox Monitor export table dialog ###

import csv

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.lang.LmLanguages import get_export_table_label as lx, get_main_message as mx


# ################################ Export table dialog ################################
class ExportTableDialog(QtWidgets.QDialog):
    def __init__(self, table_widget, app, parent=None):
        super().__init__(parent)

        self._table_widget = table_widget
        self._app = app

        options_label = QtWidgets.QLabel(lx('Options'), objectName='optionsLabel')
        self._export_header_checkbox = QtWidgets.QCheckBox(lx('Export Header'), objectName='exportHeaderCheckbox')
        self._export_header_checkbox.setChecked(True)

        columns_label = QtWidgets.QLabel(lx('Columns'), objectName='columnsLabel')

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(5)
        grid.addWidget(options_label, 0, 0)
        grid.addWidget(self._export_header_checkbox, 0, 1)
        grid.addWidget(columns_label, 1, 0)

        self._col_checkboxes = []
        for col in range(table_widget.columnCount()):
            self._col_checkbox = QtWidgets.QCheckBox(table_widget.horizontalHeaderItem(col).text())
            self._col_checkbox.setChecked(True)
            self._col_checkboxes.append(self._col_checkbox)
            grid.addWidget(self._col_checkbox, col + 1, 1)

        self._ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
        self._ok_button.clicked.connect(self.accept)
        self._ok_button.setDefault(True)
        cancel_button = QtWidgets.QPushButton(lx('Cancel'), objectName='cancel')
        cancel_button.clicked.connect(self.reject)
        hbox = QtWidgets.QHBoxLayout()
        hbox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        hbox.setSpacing(10)
        hbox.addWidget(self._ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        hbox.addWidget(cancel_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(20)
        vbox.addLayout(grid, 0)
        vbox.addLayout(hbox, 1)

        LmConfig.set_tooltips(self, 'export_table')

        self.setWindowTitle(lx('Export Table'))

        self.setModal(True)
        self.show()


    # Export the table content in a CSV file
    def do_export_table(self):
        # Select file
        file_name = QtWidgets.QFileDialog.getSaveFileName(self, lx('Save File'), '.csv', '*.csv')[0]
        if not file_name:
            return

        # Open file
        try:
            export_file = open(file_name, 'w', newline='')
        except Exception as e:
            LmTools.error(f'File creation error: {e}')
            self._app.display_error(mx('Cannot create the file.', 'createFileErr'))
            return

        self._app._task.start(lx('Exporting data...'))

        # Create CSV writer
        csv_writer = csv.writer(export_file, dialect='excel', delimiter=LmConf.CsvDelimiter)

        # Write header if necessary
        if self._export_header_checkbox.isChecked():
            header = [self._table_widget.horizontalHeaderItem(col).text()
                      for col in range(len(self._col_checkboxes))
                      if self._col_checkboxes[col].isChecked()]
            csv_writer.writerow(header)

        # Write each row
        for row in range(self._table_widget.rowCount()):
            line = [self.do_export_item(row, col)
                    for col in range(len(self._col_checkboxes))
                    if self._col_checkboxes[col].isChecked()]
            csv_writer.writerow(line)

        # Close file
        try:
            export_file.close()
        except Exception as e:
            LmTools.error(f'File saving error: {e}')
            self._app.display_error(mx('Cannot save the file.', 'saveFileErr'))
 
        self._app._task.end()


    # Return an export string for the item at the given row & column
    def do_export_item(self, row, col):
        # Retrieve item, return empty string if None
        item = self._table_widget.item(row, col)
        if not item:
            return ''

        # First try a ExportDataRole data
        data = item.data(LmTools.ItemDataRole.ExportRole)
        if data:
            return str(data)

        # Then try a DisplayRole data
        data = item.data(QtCore.Qt.ItemDataRole.DisplayRole)
        if data:
            return str(data)

        # Then try a UserRole data
        data = item.data(QtCore.Qt.ItemDataRole.UserRole)
        if data:
            return str(data)

        # Otherwise return item text
        return item.text()
