### Livebox Monitor actions tab module ###

from PyQt6 import QtGui
from PyQt6 import QtCore
from PyQt6 import QtWidgets

import LmTools
from LmIcons import LmIcon
import LmConfig


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

		aWifiGlobalStatusButton = QtWidgets.QPushButton('Show global status...')
		aWifiGlobalStatusButton.clicked.connect(self.wifiGlobalStatusButtonClick)
		aWifiButtons.addWidget(aWifiGlobalStatusButton)

		aWifiGroupBox = QtWidgets.QGroupBox('Wifi')
		aWifiGroupBox.setMaximumWidth((BUTTON_WIDTH * 2) + 100)
		aWifiGroupBox.setLayout(aWifiButtons)

		# Reboot buttons column
		aRebootButtons = QtWidgets.QVBoxLayout()
		aRebootButtons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aRebootButtons.setSpacing(20)

		aRebootLiveboxButton = QtWidgets.QPushButton('Reboot Livebox...')
		aRebootLiveboxButton.clicked.connect(self.rebootLiveboxButtonClick)
		aRebootLiveboxButton.setMinimumWidth(BUTTON_WIDTH)
		aRebootButtons.addWidget(aRebootLiveboxButton, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

		aRebootHistoryButton = QtWidgets.QPushButton('Reboot History...')
		aRebootHistoryButton.clicked.connect(self.rebootHistoryButtonClick)
		aRebootHistoryButton.setMinimumWidth(BUTTON_WIDTH)
		aRebootButtons.addWidget(aRebootHistoryButton, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

		aRebootGroupBox = QtWidgets.QGroupBox('Reboots')
		aRebootGroupBox.setMaximumWidth(BUTTON_WIDTH + 50)
		aRebootGroupBox.setLayout(aRebootButtons)

		# Misc buttons column
		aMiscButtons = QtWidgets.QVBoxLayout()
		aMiscButtons.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aMiscButtons.setSpacing(20)

		aPhoneRingButton = QtWidgets.QPushButton('Phone Ring')
		aPhoneRingButton.clicked.connect(self.phoneRingButtonClick)
		aPhoneRingButton.setMinimumWidth(BUTTON_WIDTH)
		aMiscButtons.addWidget(aPhoneRingButton, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

		aLedButton = QtWidgets.QPushButton('Show LED Status...')
		aLedButton.clicked.connect(self.ledButtonClick)
		aLedButton.setMinimumWidth(BUTTON_WIDTH)
		aMiscButtons.addWidget(aLedButton, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

		aMiscGroupBox = QtWidgets.QGroupBox('Misc')
		aMiscGroupBox.setMaximumWidth(BUTTON_WIDTH + 50)
		aMiscGroupBox.setLayout(aMiscButtons)

		# Layout
		aHBox = QtWidgets.QHBoxLayout()
		aHBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
		aHBox.setSpacing(40)
		aHBox.addWidget(aWifiGroupBox, 1, QtCore.Qt.AlignmentFlag.AlignTop)
		aHBox.addWidget(aRebootGroupBox, 1, QtCore.Qt.AlignmentFlag.AlignTop)
		aHBox.addWidget(aMiscGroupBox, 1, QtCore.Qt.AlignmentFlag.AlignTop)
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

		aStatusDialog = WifiGlobalStatusDialog(self, aGlobalStatus)
		aStatusDialog.exec()


	### Click on Reboot Livebox button
	def rebootLiveboxButtonClick(self):
		if LmTools.AskQuestion('Are you sure you want to reboot the Livebox?'):
			try:
				LmTools.MouseCursor_Busy()
				self._session.request('NMC:reboot', { 'reason': 'GUI_Reboot' })
				LmTools.MouseCursor_Normal()
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


	### Click on Phone Ring button
	def phoneRingButtonClick(self):
		try:
			LmTools.MouseCursor_Busy()
			d = self._session.request('VoiceService.VoiceApplication:ring')
			LmTools.MouseCursor_Normal()
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			LmTools.MouseCursor_Normal()
			d = None

		if d is None:
			LmTools.DisplayError('VoiceService.VoiceApplication:ring service error')
		else:
			LmTools.DisplayStatus('Phone should be ringing.')
		

	### Click on LED Status button
	def ledButtonClick(self):
		self.startTask('Getting LED Status...')

		aLedStatusTxt = 'Internet = ' + self.getLedStatus('Internet Led') + '\n'
		aLedStatusTxt += 'Wifi = ' + self.getLedStatus('Wifi Led') + '\n'
		aLedStatusTxt += 'VoIP = ' + self.getLedStatus('Voip Led') + '\n'
		aLedStatusTxt += 'LAN = ' + self.getLedStatus('LAN Led') + '\n'

		self.endTask()

		LmTools.DisplayStatus(aLedStatusTxt)


	### Get LED Status
	def getLedStatus(self, iName):
		try:
			d = self._session.request('NMC.LED:getLedStatus', { 'name': iName })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is None:
			s = None
		else:
			s = d.get('status')

		if (s is None) or (not s):
			return ''

		d = d.get('data')
		if d is None:
			return ''

		return d.get('state', 'Unknown') + ' / ' + d.get('color', 'Unknown')



# ############# Display reboot history dialog #############
class RebootHistoryDialog(QtWidgets.QDialog):
	def __init__(self, iName, iParent = None):
		super(RebootHistoryDialog, self).__init__(iParent)
		self.resize(700, 385)

		self._historyTable = QtWidgets.QTableWidget()
		self._historyTable.setColumnCount(4)
		self._historyTable.setHorizontalHeaderLabels(('Boot Date', 'Boot Reason', 'Shutdown Date', 'Shutdown Reason'))
		self._historyTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Fixed)
		self._historyTable.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.Stretch)
		self._historyTable.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Fixed)
		self._historyTable.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)
		self._historyTable.setColumnWidth(0, 125)
		self._historyTable.setColumnWidth(1, 225)
		self._historyTable.setColumnWidth(2, 125)
		self._historyTable.setColumnWidth(3, 225)
		self._historyTable.verticalHeader().hide()
		self._historyTable.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
		self._historyTable.setGridStyle(QtCore.Qt.PenStyle.SolidLine)
		self._historyTable.setStyleSheet(LmConfig.LIST_STYLESHEET)
		self._historyTable.horizontalHeader().setStyleSheet(LmConfig.LIST_HEADER_STYLESHEET)
		self._historyTable.horizontalHeader().setFont(LmTools.BOLD_FONT)
		self._historyTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

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
	def __init__(self, iParent, iStatus):
		super(WifiGlobalStatusDialog, self).__init__(iParent)
		self.resize(550, 415)

		self._status = iStatus
		self._statusTable = QtWidgets.QTableWidget()
		self._statusTable.setColumnCount(1 + len(iStatus))
		aHeaders = []
		aHeaders.append('Interfaces')
		for s in self._status:
			aHeaders.append(s[WifiKey.AccessPoint])
		self._statusTable.setHorizontalHeaderLabels((*aHeaders,))
		self._statusTable.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.Stretch)
		self._statusTable.setColumnWidth(0, 200)
		i = 1
		while i <= len(self._status):
			self._statusTable.horizontalHeader().setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeMode.Fixed)
			self._statusTable.setColumnWidth(i, 125)
			i += 1
		self._statusTable.verticalHeader().hide()
		self._statusTable.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
		self._statusTable.setGridStyle(QtCore.Qt.PenStyle.SolidLine)
		self._statusTable.setStyleSheet(LmConfig.LIST_STYLESHEET)
		self._statusTable.horizontalHeader().setStyleSheet(LmConfig.LIST_HEADER_STYLESHEET)
		self._statusTable.horizontalHeader().setFont(LmTools.BOLD_FONT)
		self._statusTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

		aHBox = QtWidgets.QHBoxLayout()
		aOKButton = QtWidgets.QPushButton('OK', self)
		aOKButton.clicked.connect(self.accept)
		aOKButton.setDefault(True)
		aHBox.addWidget(aOKButton, 1, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addWidget(self._statusTable, 0)
		aVBox.addLayout(aHBox, 1)

		self.loadStatus()

		self.setWindowTitle('Wifi Global Status')
		self.setModal(True)
		self.show()


	def loadStatus(self):
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
		i = self.addStatusLine('Guest 2.4GHz VAP', WifiKey.Guest2VAP, i)
		i = self.addStatusLine('Guest 5GHz VAP', WifiKey.Guest5VAP, i)


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
