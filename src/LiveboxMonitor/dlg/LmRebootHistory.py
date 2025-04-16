### Livebox Monitor Reboot History dialog ###

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.lang.LmLanguages import GetRHistoryDialogLabel as lx


# ################################ Reboot History dialog ################################
class RebootHistoryDialog(QtWidgets.QDialog):
	def __init__(self, iName, iParent = None):
		super(RebootHistoryDialog, self).__init__(iParent)
		self.resize(550, 56 + LmConfig.DialogHeight(10))

		self._historyTable = QtWidgets.QTableWidget(objectName = 'historyTable')
		self._historyTable.setColumnCount(4)
		self._historyTable.setHorizontalHeaderLabels((lx('Boot Date'), lx('Boot Reason'), lx('Shutdown Date'), lx('Shutdown Reason')))
		aHeader = self._historyTable.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aHeader.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aModel = aHeader.model()
		aModel.setHeaderData(0, QtCore.Qt.Orientation.Horizontal, 'reboot_BootDate', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(1, QtCore.Qt.Orientation.Horizontal, 'reboot_BootReason', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(2, QtCore.Qt.Orientation.Horizontal, 'reboot_ShutdownDate', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(3, QtCore.Qt.Orientation.Horizontal, 'reboot_ShutdownReason', QtCore.Qt.ItemDataRole.UserRole)
		self._historyTable.setColumnWidth(0, 125)
		self._historyTable.setColumnWidth(1, 225)
		self._historyTable.setColumnWidth(2, 125)
		self._historyTable.setColumnWidth(3, 225)
		self._historyTable.verticalHeader().hide()
		self._historyTable.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
		self._historyTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		LmConfig.SetTableStyle(self._historyTable)

		aHBox = QtWidgets.QHBoxLayout()
		aOKButton = QtWidgets.QPushButton(lx('OK'), objectName = 'ok')
		aOKButton.clicked.connect(self.accept)
		aOKButton.setDefault(True)
		aHBox.addWidget(aOKButton, 1, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addWidget(self._historyTable, 0)
		aVBox.addLayout(aHBox, 1)

		LmConfig.SetToolTips(self, 'rhistory')

		self.setWindowTitle(lx('{} Reboot History').format(iName))
		self.setModal(True)
		self.show()


	def loadHistory(self, iHistory):
		i = 0

		for aKey in iHistory:
			d = iHistory[aKey]
			self._historyTable.insertRow(i)
			self._historyTable.setItem(i, 0, QtWidgets.QTableWidgetItem(LmTools.FmtLiveboxTimestamp(d.get('BootDate'))))
			self._historyTable.setItem(i, 1, QtWidgets.QTableWidgetItem(d.get('BootReason', lx('Unknown'))))
			self._historyTable.setItem(i, 2, QtWidgets.QTableWidgetItem(LmTools.FmtLiveboxTimestamp(d.get('ShutdownDate'))))
			self._historyTable.setItem(i, 3, QtWidgets.QTableWidgetItem(d.get('ShutdownReason', lx('Unknown'))))
			i += 1
