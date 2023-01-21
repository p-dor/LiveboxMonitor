### Livebox Monitor actions tab module ###

import json
import webbrowser

from PyQt6 import QtGui
from PyQt6 import QtCore
from PyQt6 import QtWidgets

from src import LmTools
from src.LmIcons import LmIcon
from src import LmConfig
from src.LmConfig import LmConf
from src.LmConfig import PrefsDialog
from src.LmConfig import SetApplicationStyle

from __init__ import __url__, __copyright__


# ################################ VARS & DEFS ################################

# Static Config
BUTTON_WIDTH = 150

# Wifi status keys
class WifiKey:
	AccessPoint = 'Name'
	Enable = 'WE'
	Status = 'WS'
	Scheduler = 'SCH'
	Wifi2Enable = 'W2E'
	Wifi2Status = 'W2S'
	Wifi2VAP = 'W2V'
	Wifi5Enable = 'W5E'
	Wifi5Status = 'W5S'
	Wifi5VAP = 'W5V'
	Wifi6Enable = 'W6E'
	Wifi6Status = 'W6S'
	Wifi6VAP = 'W6V'
	Guest2VAP = 'G2V'
	Guest5VAP = 'G5V'

# Wifi status values
class WifiStatus:
	Enable = 'Y'
	Disable = 'N'
	Error = 'E'
	Inactive = 'I'
	Unsigned = 'S'


# ################################ LmActions class ################################
class LmActions:

	### Create actions tab
	def createActionsTab(self):
		self._actionsTab = QtWidgets.QWidget()

		# Wifi buttons group
		aWifiButtons = QtWidgets.QVBoxLayout()
		aWifiButtons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aWifiButtons.setSpacing(20)

		aWifiSet = QtWidgets.QHBoxLayout()
		aWifiSet.setSpacing(20)

		aWifiOnButton = QtWidgets.QPushButton('Wifi ON')
		aWifiOnButton.clicked.connect(self.wifiOnButtonClick)
		aWifiOnButton.setMinimumWidth(BUTTON_WIDTH)
		aWifiSet.addWidget(aWifiOnButton)

		aWifiOffButton = QtWidgets.QPushButton('Wifi OFF')
		aWifiOffButton.clicked.connect(self.wifiOffButtonClick)
		aWifiOffButton.setMinimumWidth(BUTTON_WIDTH)
		aWifiSet.addWidget(aWifiOffButton)
		aWifiButtons.addLayout(aWifiSet, 0)

		aGuestWifiSet = QtWidgets.QHBoxLayout()
		aGuestWifiSet.setSpacing(20)

		aGuestWifiOnButton = QtWidgets.QPushButton('Guest Wifi ON')
		aGuestWifiOnButton.clicked.connect(self.guestWifiOnButtonClick)
		aGuestWifiOnButton.setMinimumWidth(BUTTON_WIDTH)
		aGuestWifiSet.addWidget(aGuestWifiOnButton)

		aGuestWifiOffButton = QtWidgets.QPushButton('Guest Wifi OFF')
		aGuestWifiOffButton.clicked.connect(self.guestWifiOffButtonClick)
		aGuestWifiOffButton.setMinimumWidth(BUTTON_WIDTH)
		aGuestWifiSet.addWidget(aGuestWifiOffButton)
		aWifiButtons.addLayout(aGuestWifiSet, 0)

		aSchedulerSet = QtWidgets.QHBoxLayout()
		aSchedulerSet.setSpacing(20)

		aSchedulerOnButton = QtWidgets.QPushButton('Wifi Scheduler ON')
		aSchedulerOnButton.clicked.connect(self.schedulerOnButtonClick)
		aSchedulerOnButton.setMinimumWidth(BUTTON_WIDTH)
		aSchedulerSet.addWidget(aSchedulerOnButton)

		aSchedulerOffButton = QtWidgets.QPushButton('Wifi Scheduler OFF')
		aSchedulerOffButton.clicked.connect(self.schedulerOffButtonClick)
		aSchedulerOffButton.setMinimumWidth(BUTTON_WIDTH)
		aSchedulerSet.addWidget(aSchedulerOffButton)
		aWifiButtons.addLayout(aSchedulerSet, 0)

		aSeparator = QtWidgets.QFrame()
		aSeparator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
		aSeparator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
		aWifiButtons.addWidget(aSeparator)

		aWifiGlobalStatusButton = QtWidgets.QPushButton('Show Global Status...')
		aWifiGlobalStatusButton.clicked.connect(self.wifiGlobalStatusButtonClick)
		aWifiButtons.addWidget(aWifiGlobalStatusButton)

		aWifiGroupBox = QtWidgets.QGroupBox('Wifi')
		aWifiGroupBox.setLayout(aWifiButtons)

		# Reboot buttons column
		aRebootButtons = QtWidgets.QVBoxLayout()
		aRebootButtons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aRebootButtons.setSpacing(20)

		aRebootLiveboxButton = QtWidgets.QPushButton('Reboot Livebox...')
		aRebootLiveboxButton.clicked.connect(self.rebootLiveboxButtonClick)
		aRebootLiveboxButton.setMinimumWidth(BUTTON_WIDTH)
		aRebootButtons.addWidget(aRebootLiveboxButton)

		aRebootHistoryButton = QtWidgets.QPushButton('Reboot History...')
		aRebootHistoryButton.clicked.connect(self.rebootHistoryButtonClick)
		aRebootHistoryButton.setMinimumWidth(BUTTON_WIDTH)
		aRebootButtons.addWidget(aRebootHistoryButton)

		aRebootGroupBox = QtWidgets.QGroupBox('Reboots')
		aRebootGroupBox.setLayout(aRebootButtons)

		# About, preferences, debug and quit column
		aRightZone = QtWidgets.QVBoxLayout()

		# About box
		aAboutWidgets = QtWidgets.QVBoxLayout()
		aAboutWidgets.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aAboutWidgets.setSpacing(15)

		aAppIcon = QtWidgets.QLabel()
		aAppIcon.setPixmap(LmIcon.AppIconPixmap)
		aAppIcon.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		aAppIcon.setMaximumWidth(64)
		aAppIcon.setMinimumWidth(64)
		aAboutWidgets.addWidget(aAppIcon, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

		aAppName = QtWidgets.QLabel(self._applicationName)
		aAppName.setFont(LmTools.BOLD_FONT)
		aAboutWidgets.addWidget(aAppName, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

		aAboutWidgets.addWidget(QtWidgets.QLabel('An Open Source project'), 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

		aOpenSourceURL = QtWidgets.QLabel(__url__)
		aOpenSourceURL.setStyleSheet('QLabel { color : blue; }')
		aOpenSourceURL.mousePressEvent = self.openSourceButtonClick
		aAboutWidgets.addWidget(aOpenSourceURL, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

		aAboutWidgets.addWidget(QtWidgets.QLabel(__copyright__), 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

		aAboutGroupBox = QtWidgets.QGroupBox('About')
		aAboutGroupBox.setLayout(aAboutWidgets)

		aRightZone.addWidget(aAboutGroupBox, 0, QtCore.Qt.AlignmentFlag.AlignTop)

		# Setup box
		aSetupButtons = QtWidgets.QVBoxLayout()
		aSetupButtons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aSetupButtons.setSpacing(20)

		aPrefsButton = QtWidgets.QPushButton('Preferences...')
		aPrefsButton.clicked.connect(self.prefsButtonClick)
		aSetupButtons.addWidget(aPrefsButton)

		aChangeProfileButton = QtWidgets.QPushButton('Change Profile...')
		aChangeProfileButton.clicked.connect(self.changeProfileButtonClick)
		aSetupButtons.addWidget(aChangeProfileButton)

		aSetupGroupBox = QtWidgets.QGroupBox('Setup')
		aSetupGroupBox.setLayout(aSetupButtons)

		aRightZone.addWidget(aSetupGroupBox, 0, QtCore.Qt.AlignmentFlag.AlignTop)

		# Debug box
		aDebugButtons = QtWidgets.QVBoxLayout()
		aDebugButtons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aDebugButtons.setSpacing(20)

		aShowRawDeviceListButton = QtWidgets.QPushButton('Raw Device List...')
		aShowRawDeviceListButton.clicked.connect(self.showRawDeviceListButtonClick)
		aDebugButtons.addWidget(aShowRawDeviceListButton)
		aShowRawTopologyButton = QtWidgets.QPushButton('Raw Topology...')
		aShowRawTopologyButton.clicked.connect(self.showRawTopologyButtonClick)
		aDebugButtons.addWidget(aShowRawTopologyButton)
		aSetLogLevelButton = QtWidgets.QPushButton('Set Log Level...')
		aSetLogLevelButton.clicked.connect(self.setLogLevelButtonClick)
		aDebugButtons.addWidget(aSetLogLevelButton)

		aDebugGroupBox = QtWidgets.QGroupBox('Debug')
		aDebugGroupBox.setLayout(aDebugButtons)

		aRightZone.addWidget(aDebugGroupBox, 0, QtCore.Qt.AlignmentFlag.AlignTop)

		# Quit button
		aQuitButton = QtWidgets.QPushButton('Quit Application')
		aQuitButton.clicked.connect(self.quitButtonClick)
		aQuitButton.setMinimumWidth(BUTTON_WIDTH)
		aRightZone.addWidget(aQuitButton, 1, QtCore.Qt.AlignmentFlag.AlignBottom)

		# Layout
		aHBox = QtWidgets.QHBoxLayout()
		aHBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
		aHBox.setSpacing(40)
		aHBox.addWidget(aWifiGroupBox, 1, QtCore.Qt.AlignmentFlag.AlignTop)
		aHBox.addWidget(aRebootGroupBox, 1, QtCore.Qt.AlignmentFlag.AlignTop)
		aHBox.addLayout(aRightZone, 1)
		self._actionsTab.setLayout(aHBox)

		self._tabWidget.addTab(self._actionsTab, 'Actions')


	### Click on Wifi ON button
	def wifiOnButtonClick(self):
		try:
			LmTools.MouseCursor_Busy()
			d = self._session.request('NMC.Wifi:set', { 'Enable': True, 'Status' : True })
			LmTools.MouseCursor_Normal()
			if d is not None:
				d = d.get('status')
			if (d is None) or (not d):
				LmTools.DisplayError('NMC.Wifi:set service error')
			else:
				LmTools.DisplayStatus('Wifi activated.')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			LmTools.MouseCursor_Normal()
			LmTools.DisplayError('NMC.Wifi:set service error')


	### Click on Wifi OFF button
	def wifiOffButtonClick(self):
		try:
			LmTools.MouseCursor_Busy()
			d = self._session.request('NMC.Wifi:set', { 'Enable': False, 'Status' : False })
			LmTools.MouseCursor_Normal()
			if d is not None:
				d = d.get('status')
			if (d is None) or (not d):
				LmTools.DisplayError('NMC.Wifi:set service error')
			else:
				LmTools.DisplayStatus('Wifi deactivated.')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			LmTools.MouseCursor_Normal()
			LmTools.DisplayError('NMC.Wifi:set service error')


	### Click on guest Wifi ON button
	def guestWifiOnButtonClick(self):
		try:
			LmTools.MouseCursor_Busy()
			d = self._session.request('NMC.Guest:set', { 'Enable': True })
			LmTools.MouseCursor_Normal()
			if d is None:
				LmTools.DisplayError('NMC.Guest:set service error')
			else:
				LmTools.DisplayStatus('Guest Wifi activated. Reactivate Scheduler if required.')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			LmTools.MouseCursor_Normal()
			LmTools.DisplayError('NMC.Guest:set service error')


	### Click on guest Wifi OFF button
	def guestWifiOffButtonClick(self):
		try:
			LmTools.MouseCursor_Busy()
			d = self._session.request('NMC.Guest:set', { 'Enable': False })
			LmTools.MouseCursor_Normal()
			if d is None:
				LmTools.DisplayError('NMC.Guest:set service error')
			else:
				LmTools.DisplayStatus('Guest Wifi deactivated.')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			LmTools.MouseCursor_Normal()
			LmTools.DisplayError('NMC.Guest:set service error')


	### Click on Scheduler ON button
	def schedulerOnButtonClick(self):
		try:
			LmTools.MouseCursor_Busy()
			d = self._session.request('Scheduler:enableSchedule', { 'type' : 'WLAN', 'ID' : 'wl0', 'enable': True })
			LmTools.MouseCursor_Normal()
			if d is not None:
				d = d.get('status')
			if (d is None) or (not d):
				LmTools.DisplayError('Scheduler:enableSchedule service error')
			else:
				LmTools.DisplayStatus('Scheduler activated.')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			LmTools.MouseCursor_Normal()
			LmTools.DisplayError('Scheduler:enableSchedule service error')


	### Click on Scheduler OFF button
	def schedulerOffButtonClick(self):
		try:
			LmTools.MouseCursor_Busy()
			d = self._session.request('Scheduler:enableSchedule', { 'type' : 'WLAN', 'ID' : 'wl0', 'enable': False })
			LmTools.MouseCursor_Normal()
			if d is not None:
				d = d.get('status')
			if (d is None) or (not d):
				LmTools.DisplayError('Scheduler:enableSchedule service error')
			else:
				LmTools.DisplayStatus('Scheduler deactivated.')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			LmTools.MouseCursor_Normal()
			LmTools.DisplayError('Scheduler:enableSchedule service error')


	### Click on Global Wifi Status button
	def wifiGlobalStatusButtonClick(self):
		self.startTask('Getting Wifi Global Status...')

		# Getting Livebox status
		aLiveboxStatus = self.getLiveboxWifiStatus()

		# Getting Repeater statuses
		aGlobalStatus = self.getRepeatersWifiStatus()
		aGlobalStatus.insert(0, aLiveboxStatus)

		self.endTask()

		aStatusDialog = WifiGlobalStatusDialog(self, aGlobalStatus, self._liveboxModel)
		aStatusDialog.exec()


	### Click on Reboot Livebox button
	def rebootLiveboxButtonClick(self):
		if LmTools.AskQuestion('Are you sure you want to reboot the Livebox?'):
			try:
				LmTools.MouseCursor_Busy()
				r = self._session.request('NMC:reboot', { 'reason': 'GUI_Reboot' })
				LmTools.MouseCursor_Normal()
				if r is None:
					LmTools.DisplayError('NMC:reboot service error')
				else:
					LmTools.DisplayStatus('Application will now quit.')
					self.close()
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				LmTools.MouseCursor_Normal()
				LmTools.DisplayError('NMC:reboot service error')


	### Click on Reboot History button
	def rebootHistoryButtonClick(self):
		self.startTask('Getting Reboot History...')

		try:
			d = self._session.request('NMC.Reboot.Reboot:get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')

		self.endTask()

		if d is None:
			LmTools.DisplayError('NMC.Reboot.Reboot:get service error')
			return

		aHistoryDialog = RebootHistoryDialog('Livebox', self)
		aHistoryDialog.loadHistory(d)
		aHistoryDialog.exec()


	### Open Source project web button
	def openSourceButtonClick(self, iEvent):
		webbrowser.open_new_tab(__url__)


	### Click on preferences button
	def prefsButtonClick(self):
		aPrefsDialog = PrefsDialog(self)
		if aPrefsDialog.exec():
			LmConf.assignProfile()
			LmConf.save()
			SetApplicationStyle()
			self.resetUI()


	### Change the current profile in use
	def changeProfileButtonClick(self):
		if LmConf.askProfile():
			LmConf.assignProfile()
			self.resetUI()


	### Click on show raw device list button
	def showRawDeviceListButtonClick(self):
		LmTools.DisplayInfos('Raw Device List', json.dumps(self._liveboxDevices, indent = 2))


	### Click on show raw topology button
	def showRawTopologyButtonClick(self):
		LmTools.DisplayInfos('Raw Topology', json.dumps(self._liveboxTopology, indent = 2))


	### Click on set log level button
	def setLogLevelButtonClick(self):
		aLevels = ['0', '1', '2']
		aLevel, aOK = QtWidgets.QInputDialog.getItem(None, 'Log level selection',
													 'Please select a log level:',
													 aLevels, LmConf.LogLevel, False)
		if aOK:
			LmConf.setLogLevel(int(aLevel))


	### Click on Quit Application button
	def quitButtonClick(self):
		self.close()



# ############# Display reboot history dialog #############
class RebootHistoryDialog(QtWidgets.QDialog):
	def __init__(self, iName, iParent = None):
		super(RebootHistoryDialog, self).__init__(iParent)
		self.resize(550, 56 + LmConfig.DialogHeight(10))

		self._historyTable = QtWidgets.QTableWidget()
		self._historyTable.setColumnCount(4)
		self._historyTable.setHorizontalHeaderLabels(('Boot Date', 'Boot Reason', 'Shutdown Date', 'Shutdown Reason'))
		aHeader = self._historyTable.horizontalHeader()
		aHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Fixed)
		aHeader.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aHeader.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Fixed)
		aHeader.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
		self._historyTable.setColumnWidth(0, 125)
		self._historyTable.setColumnWidth(1, 225)
		self._historyTable.setColumnWidth(2, 125)
		self._historyTable.setColumnWidth(3, 225)
		self._historyTable.verticalHeader().hide()
		self._historyTable.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
		self._historyTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		LmConfig.SetTableStyle(self._historyTable)

		aHBox = QtWidgets.QHBoxLayout()
		aOKButton = QtWidgets.QPushButton('OK', self)
		aOKButton.clicked.connect(self.accept)
		aOKButton.setDefault(True)
		aHBox.addWidget(aOKButton, 1, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addWidget(self._historyTable, 0)
		aVBox.addLayout(aHBox, 1)

		self.setWindowTitle(iName + ' Reboot History')
		self.setModal(True)
		self.show()


	def loadHistory(self, iHistory):
		i = 0

		for aKey in iHistory:
			d = iHistory[aKey]
			self._historyTable.insertRow(i)
			self._historyTable.setItem(i, 0, QtWidgets.QTableWidgetItem(LmTools.FmtLiveboxTimestamp(d.get('BootDate'))))
			self._historyTable.setItem(i, 1, QtWidgets.QTableWidgetItem(d.get('BootReason', 'Unknown')))
			self._historyTable.setItem(i, 2, QtWidgets.QTableWidgetItem(LmTools.FmtLiveboxTimestamp(d.get('ShutdownDate'))))
			self._historyTable.setItem(i, 3, QtWidgets.QTableWidgetItem(d.get('ShutdownReason', 'Unknown')))
			i += 1



# ############# Display Wifi global status dialog #############
class WifiGlobalStatusDialog(QtWidgets.QDialog):
	def __init__(self, iParent, iStatus, iLiveboxModel):
		super(WifiGlobalStatusDialog, self).__init__(iParent)

		self._status = iStatus
		self._statusTable = QtWidgets.QTableWidget()
		self._statusTable.setColumnCount(1 + len(iStatus))
		aHeaders = []
		aHeaders.append('Interfaces')
		for s in self._status:
			aHeaders.append(s[WifiKey.AccessPoint])
		self._statusTable.setHorizontalHeaderLabels((*aHeaders,))
		aTableHeader = self._statusTable.horizontalHeader()
		aTableHeader.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
		self._statusTable.setColumnWidth(0, 200)
		i = 1
		while i <= len(self._status):
			aTableHeader.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.Fixed)
			self._statusTable.setColumnWidth(i, 125)
			i += 1
		self._statusTable.verticalHeader().hide()
		self._statusTable.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
		self._statusTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		LmConfig.SetTableStyle(self._statusTable)

		aHBox = QtWidgets.QHBoxLayout()
		aOKButton = QtWidgets.QPushButton('OK', self)
		aOKButton.clicked.connect(self.accept)
		aOKButton.setDefault(True)
		aHBox.addWidget(aOKButton, 1, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addWidget(self._statusTable, 0)
		aVBox.addLayout(aHBox, 1)

		i = self.loadStatus(iLiveboxModel)
		self.resize(550, 56 + LmConfig.DialogHeight(i))

		self.setWindowTitle('Wifi Global Status')
		self.setModal(True)
		self.show()


	def loadStatus(self, iLiveboxModel):
		i = 0
		i = self.addStatusLine('Wifi Enabled', WifiKey.Enable, i)
		i = self.addStatusLine('Wifi Active', WifiKey.Status, i)
		i = self.addStatusLine('Wifi Scheduler', WifiKey.Scheduler, i)
		i = self.addStatusLine('Wifi 2.4GHz Enabled', WifiKey.Wifi2Enable, i)
		i = self.addStatusLine('Wifi 2.4GHz Active', WifiKey.Wifi2Status, i)
		i = self.addStatusLine('Wifi 2.4GHz VAP', WifiKey.Wifi2VAP, i)
		i = self.addStatusLine('Wifi 5GHz Enabled', WifiKey.Wifi5Enable, i)
		i = self.addStatusLine('Wifi 5GHz Active', WifiKey.Wifi5Status, i)
		i = self.addStatusLine('Wifi 5GHz VAP', WifiKey.Wifi5VAP, i)
		if iLiveboxModel == 'LB6':
			i = self.addStatusLine('Wifi 6GHz Enabled', WifiKey.Wifi6Enable, i)
			i = self.addStatusLine('Wifi 6GHz Active', WifiKey.Wifi6Status, i)
			i = self.addStatusLine('Wifi 6GHz VAP', WifiKey.Wifi6VAP, i)
		i = self.addStatusLine('Guest 2.4GHz VAP', WifiKey.Guest2VAP, i)
		i = self.addStatusLine('Guest 5GHz VAP', WifiKey.Guest5VAP, i)
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
				aItem = QtWidgets.QTableWidgetItem('Error')
				aItem.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
				aItem.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self._statusTable.setItem(iIndex, i, aItem)
			elif aStatus == WifiStatus.Inactive:
				aItem = QtWidgets.QTableWidgetItem('Inactive')
				aItem.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
				aItem.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self._statusTable.setItem(iIndex, i, aItem)
			elif aStatus == WifiStatus.Unsigned:
				aItem = QtWidgets.QTableWidgetItem('Not signed')
				aItem.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
				aItem.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
				self._statusTable.setItem(iIndex, i, aItem)
			i += 1

		return iIndex + 1
