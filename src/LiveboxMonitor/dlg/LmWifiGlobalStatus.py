### Livebox Monitor Wifi Global Status dialog ###

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.api.LmWifiApi import WifiKey, WifiStatus
from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.lang.LmLanguages import GetWifiGlobalDialogLabel as lx


# ################################ Wifi Global Status dialog ################################
class WifiGlobalStatusDialog(QtWidgets.QDialog):
	def __init__(self, iParent, iStatus, iLiveboxModel):
		super(WifiGlobalStatusDialog, self).__init__(iParent)

		self._status = iStatus
		self._statusTable = QtWidgets.QTableWidget(objectName = 'statusTable')
		self._statusTable.setColumnCount(1 + len(iStatus))
		aHeaders = []
		aHeaders.append(lx('Interfaces'))
		for s in self._status:
			aHeaders.append(s[WifiKey.AccessPoint])
		self._statusTable.setHorizontalHeaderLabels((*aHeaders,))
		aTableHeader = self._statusTable.horizontalHeader()
		aTableHeader.setSectionsMovable(False)
		aTableHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aTableHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
		self._statusTable.setColumnWidth(0, 200)
		i = 1
		while i <= len(self._status):
			self._statusTable.setColumnWidth(i, 125)
			i += 1
		self._statusTable.verticalHeader().hide()
		self._statusTable.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
		self._statusTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		LmConfig.SetTableStyle(self._statusTable)

		aHBox = QtWidgets.QHBoxLayout()
		aOKButton = QtWidgets.QPushButton(lx('OK'), objectName = 'ok')
		aOKButton.clicked.connect(self.accept)
		aOKButton.setDefault(True)
		aHBox.addWidget(aOKButton, 1, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addWidget(self._statusTable, 0)
		aVBox.addLayout(aHBox, 1)

		i = self.loadStatus(iLiveboxModel)
		self.resize(550, 56 + LmConfig.DialogHeight(i))

		LmConfig.SetToolTips(self, 'wglobal')

		self.setWindowTitle(lx('Wifi Global Status'))
		self.setModal(True)
		self.show()


	def loadStatus(self, iLiveboxModel):
		i = 0
		i = self.addStatusLine(lx('{} Enabled').format('Wifi'), WifiKey.Enable, i)
		i = self.addStatusLine(lx('{} Active').format('Wifi'), WifiKey.Status, i)
		i = self.addStatusLine(lx('Wifi Scheduler'), WifiKey.Scheduler, i)
		i = self.addStatusLine(lx('{} Enabled').format('Wifi 2.4GHz'), WifiKey.Wifi2Enable, i)
		i = self.addStatusLine(lx('{} Active').format('Wifi 2.4GHz'), WifiKey.Wifi2Status, i)
		i = self.addStatusLine(lx('{} VAP').format('Wifi 2.4GHz'), WifiKey.Wifi2VAP, i)
		i = self.addStatusLine(lx('{} Enabled').format('Wifi 5GHz'), WifiKey.Wifi5Enable, i)
		i = self.addStatusLine(lx('{} Active').format('Wifi 5GHz'), WifiKey.Wifi5Status, i)
		i = self.addStatusLine(lx('{} VAP').format('Wifi 5GHz'), WifiKey.Wifi5VAP, i)
		if iLiveboxModel >= 6:
			i = self.addStatusLine(lx('{} Enabled').format('Wifi 6GHz'), WifiKey.Wifi6Enable, i)
			i = self.addStatusLine(lx('{} Active').format('Wifi 6GHz'), WifiKey.Wifi6Status, i)
			i = self.addStatusLine(lx('{} VAP').format('Wifi 6GHz'), WifiKey.Wifi6VAP, i)
		i = self.addStatusLine(lx('{} VAP').format(lx('Guest 2.4GHz')), WifiKey.Guest2VAP, i)
		i = self.addStatusLine(lx('{} VAP').format(lx('Guest 5GHz')), WifiKey.Guest5VAP, i)
		return i


	def addStatusLine(self, iTitle, iKey, iIndex):
		self._statusTable.insertRow(iIndex)

		self._statusTable.setItem(iIndex, 0, QtWidgets.QTableWidgetItem(iTitle))

		i = 1
		for s in self._status:
			aStatus = s.get(iKey)
			if aStatus == WifiStatus.Enable:
				aIconItem = QtWidgets.QLabel()
				aIconItem.setPixmap(LmIcon.TickPixmap)
				aIconItem.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self._statusTable.setCellWidget(iIndex, i, aIconItem)
			elif aStatus == WifiStatus.Disable:
				aIconItem = QtWidgets.QLabel()
				aIconItem.setPixmap(LmIcon.CrossPixmap)
				aIconItem.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self._statusTable.setCellWidget(iIndex, i, aIconItem)
			elif aStatus == WifiStatus.Error:
				aItem = QtWidgets.QTableWidgetItem(lx('Error'))
				aItem.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
				aItem.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self._statusTable.setItem(iIndex, i, aItem)
			elif aStatus == WifiStatus.Inactive:
				aItem = QtWidgets.QTableWidgetItem(lx('Inactive'))
				aItem.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
				aItem.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self._statusTable.setItem(iIndex, i, aItem)
			elif aStatus == WifiStatus.Unsigned:
				aItem = QtWidgets.QTableWidgetItem(lx('Not signed'))
				aItem.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
				aItem.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self._statusTable.setItem(iIndex, i, aItem)
			i += 1

		return iIndex + 1
