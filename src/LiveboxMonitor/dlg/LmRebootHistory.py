### Livebox Monitor Reboot History dialog ###

from enum import IntEnum

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmTableWidget import LmTableWidget
from LiveboxMonitor.lang.LmLanguages import get_reboot_history_label as lx


# ################################ VARS & DEFS ################################

# Reboot history columns
class RebootCol(IntEnum):
    BootDate = 0
    BootReason = 1
    ShutdownDate = 2
    ShutdownReason = 3


# ################################ Reboot History dialog ################################
class RebootHistoryDialog(QtWidgets.QDialog):
    def __init__(self, name, parent=None):
        super().__init__(parent)
        self.resize(550, 56 + LmConfig.dialog_height(10))

        self._history_table = LmTableWidget(objectName='historyTable')
        self._history_table.set_columns({RebootCol.BootDate: [lx('Boot Date'), 125, 'reboot_BootDate'],
                                         RebootCol.BootReason: [lx('Boot Reason'), 225, 'reboot_BootReason'],
                                         RebootCol.ShutdownDate: [lx('Shutdown Date'), 125, 'reboot_ShutdownDate'],
                                         RebootCol.ShutdownReason: [lx('Shutdown Reason'), 225, 'reboot_ShutdownReason']})
        self._history_table.set_header_resize([RebootCol.BootReason, RebootCol.ShutdownReason])
        self._history_table.set_standard_setup(parent, allow_sel=False, allow_sort=False)

        hbox = QtWidgets.QHBoxLayout()
        ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        hbox.addWidget(ok_button, 1, QtCore.Qt.AlignmentFlag.AlignRight)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self._history_table, 0)
        vbox.addLayout(hbox, 1)

        LmConfig.set_tooltips(self, 'rhistory')

        self.setWindowTitle(lx('{} Reboot History').format(name))
        self.setModal(True)
        self.show()


    def load_history(self, history):
        for i, key in enumerate(history):
            d = history[key]
            self._history_table.insertRow(i)
            self._history_table.setItem(i, RebootCol.BootDate, QtWidgets.QTableWidgetItem(LmTools.fmt_livebox_timestamp(d.get('BootDate'))))
            self._history_table.setItem(i, RebootCol.BootReason, QtWidgets.QTableWidgetItem(d.get('BootReason', lx('Unknown'))))
            self._history_table.setItem(i, RebootCol.ShutdownDate, QtWidgets.QTableWidgetItem(LmTools.fmt_livebox_timestamp(d.get('ShutdownDate'))))
            self._history_table.setItem(i, RebootCol.ShutdownReason, QtWidgets.QTableWidgetItem(d.get('ShutdownReason', lx('Unknown'))))
