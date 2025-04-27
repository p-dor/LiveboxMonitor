### Livebox Monitor Reboot History dialog ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.lang.LmLanguages import GetRHistoryDialogLabel as lx


# ################################ Reboot History dialog ################################
class RebootHistoryDialog(QtWidgets.QDialog):
    def __init__(self, name, parent=None):
        super(RebootHistoryDialog, self).__init__(parent)
        self.resize(550, 56 + LmConfig.DialogHeight(10))

        self._history_table = QtWidgets.QTableWidget(objectName='historyTable')
        self._history_table.setColumnCount(4)
        self._history_table.setHorizontalHeaderLabels((lx('Boot Date'), lx('Boot Reason'), lx('Shutdown Date'), lx('Shutdown Reason')))
        header = self._history_table.horizontalHeader()
        header.setSectionsMovable(False)
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
        model = header.model()
        model.setHeaderData(0, QtCore.Qt.Orientation.Horizontal, 'reboot_BootDate', QtCore.Qt.ItemDataRole.UserRole)
        model.setHeaderData(1, QtCore.Qt.Orientation.Horizontal, 'reboot_BootReason', QtCore.Qt.ItemDataRole.UserRole)
        model.setHeaderData(2, QtCore.Qt.Orientation.Horizontal, 'reboot_ShutdownDate', QtCore.Qt.ItemDataRole.UserRole)
        model.setHeaderData(3, QtCore.Qt.Orientation.Horizontal, 'reboot_ShutdownReason', QtCore.Qt.ItemDataRole.UserRole)
        self._history_table.setColumnWidth(0, 125)
        self._history_table.setColumnWidth(1, 225)
        self._history_table.setColumnWidth(2, 125)
        self._history_table.setColumnWidth(3, 225)
        self._history_table.verticalHeader().hide()
        self._history_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self._history_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        LmConfig.SetTableStyle(self._history_table)

        hbox = QtWidgets.QHBoxLayout()
        ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        hbox.addWidget(ok_button, 1, QtCore.Qt.AlignmentFlag.AlignRight)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self._history_table, 0)
        vbox.addLayout(hbox, 1)

        LmConfig.SetToolTips(self, 'rhistory')

        self.setWindowTitle(lx(f'{name} Reboot History'))
        self.setModal(True)
        self.show()


    def load_history(self, history):
        i = 0

        for aKey in history:
            d = history[aKey]
            self._history_table.insertRow(i)
            self._history_table.setItem(i, 0, QtWidgets.QTableWidgetItem(LmTools.FmtLiveboxTimestamp(d.get('BootDate'))))
            self._history_table.setItem(i, 1, QtWidgets.QTableWidgetItem(d.get('BootReason', lx('Unknown'))))
            self._history_table.setItem(i, 2, QtWidgets.QTableWidgetItem(LmTools.FmtLiveboxTimestamp(d.get('ShutdownDate'))))
            self._history_table.setItem(i, 3, QtWidgets.QTableWidgetItem(d.get('ShutdownReason', lx('Unknown'))))
            i += 1
