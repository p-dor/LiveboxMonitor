### Livebox Monitor Wifi Repeater info tab module ###

import datetime

from enum import IntEnum

from PyQt6 import QtGui
from PyQt6 import QtCore
from PyQt6 import QtWidgets

import LmTools
import LmConfig
from LmConfig import LmConf
from LmConfig import MonitorTab
from LmIcons import LmIcon
from LmSession import LmSession
from LmInfoTab import InfoCol
from LmInfoTab import StatsCol
from LmActionsTab import RebootHistoryDialog, WifiKey, WifiStatus


# ################################ VARS & DEFS ################################

# Static Config
WIFI_REPEATER_TYPE = 'SAH AP'
DEFAULT_REPEATER_NAME = 'RW #'

NET_INTF = [
	{ 'Key': 'bridge',     'Name': 'LAN',          'Type': 'lan', 'SwapStats': True  },
	{ 'Key': 'eth0',       'Name': 'Ethernet 1',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'eth1',       'Name': 'Ethernet 2',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'vap2g0priv', 'Name': 'Wifi 2.4GHz',  'Type': 'wif', 'SwapStats': True  },
	{ 'Key': 'vap5g0priv', 'Name': 'Wifi 5GHz',    'Type': 'wif', 'SwapStats': True  }
]



# ################################ LmRepeater class ################################

class LmRepeater:

	### Create Repeater tab
	def createRepeaterTab(self, iRepeater):
		iRepeater._tab = QtWidgets.QWidget()

		# Statistics list
		aStatsList = QtWidgets.QTableWidget()
		aStatsList.setColumnCount(StatsCol.Count)
		aStatsList.setHorizontalHeaderLabels(('Key', 'Name', 'Down', 'Up', 'DRate', 'URate'))
		aStatsList.setColumnHidden(StatsCol.Key, True)
		aStatsList.horizontalHeader().setSectionResizeMode(StatsCol.Name, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aStatsList.horizontalHeader().setSectionResizeMode(StatsCol.Down, QtWidgets.QHeaderView.ResizeMode.Fixed)
		aStatsList.horizontalHeader().setSectionResizeMode(StatsCol.Up, QtWidgets.QHeaderView.ResizeMode.Fixed)
		aStatsList.horizontalHeader().setSectionResizeMode(StatsCol.DownRate, QtWidgets.QHeaderView.ResizeMode.Fixed)
		aStatsList.horizontalHeader().setSectionResizeMode(StatsCol.UpRate, QtWidgets.QHeaderView.ResizeMode.Fixed)
		aStatsList.setColumnWidth(StatsCol.Name, 90)
		aStatsList.setColumnWidth(StatsCol.Down, 65)
		aStatsList.setColumnWidth(StatsCol.Up, 65)
		aStatsList.setColumnWidth(StatsCol.DownRate, 65)
		aStatsList.setColumnWidth(StatsCol.UpRate, 65)
		aStatsList.verticalHeader().hide()
		aStatsList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
		aStatsList.setGridStyle(QtCore.Qt.PenStyle.SolidLine)
		aStatsList.setStyleSheet(LmConfig.LIST_STYLESHEET)
		aStatsList.horizontalHeader().setStyleSheet(LmConfig.LIST_HEADER_STYLESHEET)
		aStatsList.horizontalHeader().setFont(LmTools.BOLD_FONT)
		aStatsList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		aStatsList.setMinimumWidth(350)

		i = 0
		for s in NET_INTF:
			aStatsList.insertRow(i)
			aStatsList.setItem(i, StatsCol.Key, QtWidgets.QTableWidgetItem(s['Key']))
			aStatsList.setItem(i, StatsCol.Name, QtWidgets.QTableWidgetItem(s['Name']))
			i += 1
		aStatsListSize = LmConfig.LIST_HEADER_HEIGHT + (LmConfig.LIST_LINE_HEIGHT * i)
		aStatsList.setMinimumHeight(aStatsListSize)
		aStatsList.setMaximumHeight(aStatsListSize)

		iRepeater._statsList = aStatsList

		# 1st action buttons line
		aButtonsSet1 = QtWidgets.QHBoxLayout()
		aButtonsSet1.setSpacing(20)

		aWifiOnButton = QtWidgets.QPushButton('Wifi ON')
		aWifiOnButton.clicked.connect(iRepeater.wifiOnButtonClick)
		aButtonsSet1.addWidget(aWifiOnButton)

		aWifiOffButton = QtWidgets.QPushButton('Wifi OFF')
		aWifiOffButton.clicked.connect(iRepeater.wifiOffButtonClick)
		aButtonsSet1.addWidget(aWifiOffButton)

		# 2nd action buttons line
		aButtonsSet2 = QtWidgets.QHBoxLayout()
		aButtonsSet2.setSpacing(20)

		aSchedulerOnButton = QtWidgets.QPushButton('Wifi Scheduler ON')
		aSchedulerOnButton.clicked.connect(iRepeater.schedulerOnButtonClick)
		aButtonsSet2.addWidget(aSchedulerOnButton)

		aSchedulerOffButton = QtWidgets.QPushButton('Wifi Scheduler OFF')
		aSchedulerOffButton.clicked.connect(iRepeater.schedulerOffButtonClick)
		aButtonsSet2.addWidget(aSchedulerOffButton)

		# 3nd action buttons line
		aButtonsSet3 = QtWidgets.QHBoxLayout()
		aButtonsSet3.setSpacing(20)

		aRebootRepeaterButton = QtWidgets.QPushButton('Reboot Repeater...')
		aRebootRepeaterButton.clicked.connect(iRepeater.rebootRepeaterButtonClick)
		aButtonsSet3.addWidget(aRebootRepeaterButton)

		aRebootHistoryButton = QtWidgets.QPushButton('Reboot History...')
		aRebootHistoryButton.clicked.connect(iRepeater.rebootHistoryButtonClick)
		aButtonsSet3.addWidget(aRebootHistoryButton)

		# 4nd action buttons line
		aButtonsSet4 = QtWidgets.QHBoxLayout()
		aButtonsSet4.setSpacing(20)

		aResignButton = QtWidgets.QPushButton('Resign...')
		aResignButton.clicked.connect(iRepeater.resignButtonClick)
		aButtonsSet4.addWidget(aResignButton)

		# Action buttons group box
		aGroupBox = QtWidgets.QGroupBox('Actions')
		aGroupBoxLayout = QtWidgets.QVBoxLayout()
		aGroupBoxLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aGroupBoxLayout.setSpacing(20)
		aGroupBoxLayout.addLayout(aButtonsSet1, 0)
		aGroupBoxLayout.addLayout(aButtonsSet2, 0)
		aGroupBoxLayout.addLayout(aButtonsSet3, 0)
		aGroupBoxLayout.addLayout(aButtonsSet4, 0)
		aGroupBox.setLayout(aGroupBoxLayout)

		# Stats & actions box
		aLeftBox = QtWidgets.QVBoxLayout()
		aLeftBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aLeftBox.setSpacing(20)
		aLeftBox.addWidget(iRepeater._statsList, 0, QtCore.Qt.AlignmentFlag.AlignTop)
		aLeftBox.addWidget(aGroupBox, 0, QtCore.Qt.AlignmentFlag.AlignTop)

		# Attribute list
		aRepeaterAList = QtWidgets.QTableWidget()
		aRepeaterAList.setColumnCount(InfoCol.Count)
		aRepeaterAList.setHorizontalHeaderLabels(('Attribute', 'Value'))
		aRepeaterAList.horizontalHeader().setSectionResizeMode(InfoCol.Attribute, QtWidgets.QHeaderView.ResizeMode.Fixed)
		aRepeaterAList.horizontalHeader().setSectionResizeMode(InfoCol.Value, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aRepeaterAList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		aRepeaterAList.setColumnWidth(InfoCol.Attribute, 200)
		aRepeaterAList.setColumnWidth(InfoCol.Value, 600)
		aRepeaterAList.verticalHeader().hide()
		aRepeaterAList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
		aRepeaterAList.setGridStyle(QtCore.Qt.PenStyle.SolidLine)
		aRepeaterAList.setStyleSheet(LmConfig.LIST_STYLESHEET)
		aRepeaterAList.horizontalHeader().setStyleSheet(LmConfig.LIST_HEADER_STYLESHEET)
		aRepeaterAList.horizontalHeader().setFont(LmTools.BOLD_FONT)
		aRepeaterAList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		iRepeater._repeaterAList = aRepeaterAList

		# Lists layout
		aListBox = QtWidgets.QHBoxLayout()
		aListBox.setSpacing(10)
		aListBox.addLayout(aLeftBox, 0)
		aListBox.addWidget(iRepeater._repeaterAList, 1)

		# Button bar
		aButtonsBox = QtWidgets.QHBoxLayout()
		aButtonsBox.setSpacing(10)

		aRepeaterInfoButton = QtWidgets.QPushButton('Repeater Infos')
		aRepeaterInfoButton.clicked.connect(iRepeater.repeaterInfoButtonClick)
		aButtonsBox.addWidget(aRepeaterInfoButton)

		aWifiInfoButton = QtWidgets.QPushButton('Wifi Infos')
		aWifiInfoButton.clicked.connect(iRepeater.wifiInfoButtonClick)
		aButtonsBox.addWidget(aWifiInfoButton)

		aLanInfoButton = QtWidgets.QPushButton('LAN Infos')
		aLanInfoButton.clicked.connect(iRepeater.lanInfoButtonClick)
		aButtonsBox.addWidget(aLanInfoButton)

		aSeparator = QtWidgets.QFrame()
		aSeparator.setFrameShape(QtWidgets.QFrame.Shape.VLine)
		aSeparator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
		aButtonsBox.addWidget(aSeparator)

		aExportInfoButton = QtWidgets.QPushButton('Export...')
		aExportInfoButton.clicked.connect(iRepeater.exportInfoButtonClick)
		aButtonsBox.addWidget(aExportInfoButton)

		# Layout
		aVBox = QtWidgets.QVBoxLayout()
		aVBox.setSpacing(10)
		aVBox.addLayout(aListBox, 0)
		aVBox.addLayout(aButtonsBox, 1)
		iRepeater._tab.setLayout(aVBox)

		self._tabWidget.addTab(iRepeater._tab, iRepeater._name)
		iRepeater.setTabIcon()


	### Itentify potential Wifi Repeater device & add it to the list
	def identifyRepeater(self, iDevice):
		if iDevice.get('DeviceType', '') == WIFI_REPEATER_TYPE:
			aIndex = len(self._repeaters)
			aKey = iDevice.get('Key', '')

			aMacAddr = iDevice.get('PhysAddress', '')
			try:
				aName = LmConf.MacAddrTable[aMacAddr]
			except:
				aName = DEFAULT_REPEATER_NAME + str(aIndex + 1)

			aIPv4Struct = iDevice.get('IPv4Address')
			if (aIPv4Struct is not None) and (len(aIPv4Struct)):
				aIPAddress = aIPv4Struct[0].get('Address', '')
			else:
				aIPAddress = None

			aActive = iDevice.get('Active', False)

			aRepeater = LmRepHandler(self, aIndex, aKey, aName, aIPAddress, aActive)
			self._repeaters.append(aRepeater)

			return aRepeater
		else:
			return None


	### Add and setup a potential new Wifi Repeater device
	def addPotentialRepeater(self, iDevice):
		aRepeater = self.identifyRepeater(iDevice)
		if aRepeater is not None:
			self.createRepeaterTab(aRepeater)
			aRepeater.signin()


	### Init repeater tabs & sessions
	def initRepeaters(self):
		for r in self._repeaters:
			self.createRepeaterTab(r)
		self.signinRepeaters()


	### Sign in to all repeaters
	def signinRepeaters(self):
		self.startTask('Signing in to repeaters...')
		for r in self._repeaters:
			r.signin()
		self.endTask()


	### Sign out for all repeaters
	def signoutRepeaters(self):
		for r in self._repeaters:
			r.signout()


	### React to device a name update
	def repeaterUpdateDeviceName(self, iDeviceKey):
		for r in self._repeaters:
			if r._key == iDeviceKey:
				r.processUpdateDeviceName()
				break


	### React to device updated event
	def repeaterDeviceUpdatedEvent(self, iDeviceKey, iEvent):
		for r in self._repeaters:
			if r._key == iDeviceKey:
				r.processDeviceUpdatedEvent(iEvent)
				break


	### React to active status change event
	def repeaterActiveEvent(self, iDeviceKey, iIsActive):
		for r in self._repeaters:
			if r._key == iDeviceKey:
				r.processActiveEvent(iIsActive)
				break


	### React to IP Address change event
	def repeaterIPAddressEvent(self, iDeviceKey, iIPv4):
		for r in self._repeaters:
			if r._key == iDeviceKey:
				r.processIPAddressEvent(iIPv4)
				break


	### Get Repeaters Wifi statuses (used by ActionsTab)
	def getRepeatersWifiStatus(self):
		aGlobalStatus = []

		for r in self._repeaters:
			u = r.getWifiStatus()
			aGlobalStatus.append(u)

		return aGlobalStatus


	### Init the Repeater stats collector thread
	def initRepeaterStatsLoop(self):
		self._repeaterStatsThread = None
		self._repeaterStatsLoop = None


	### Start the Repeater stats collector thread
	def startRepeaterStatsLoop(self):
		self._repeaterStatsThread = QtCore.QThread()
		self._repeaterStatsLoop = RepeaterStatsThread(self._repeaters)
		self._repeaterStatsLoop.moveToThread(self._repeaterStatsThread)
		self._repeaterStatsThread.started.connect(self._repeaterStatsLoop.run)
		self._repeaterStatsLoop._statsReceived.connect(self.processRepeaterStats)
		self._repeaterStatsLoop._resume.connect(self._repeaterStatsLoop.resume)
		self._repeaterStatsThread.start()


	### Suspend the Repeater stats collector thread
	def suspendRepeaterStatsLoop(self):
		if self._repeaterStatsThread is not None:
			self._repeaterStatsLoop.stop()


	### Resume the Repeater stats collector thread
	def resumeRepeaterStatsLoop(self):
		if self._repeaterStatsThread is None:
			self.startRepeaterStatsLoop()
		else:
			self._repeaterStatsLoop._resume.emit()


	### Stop the Repeater stats collector thread
	def stopRepeaterStatsLoop(self):
		if self._repeaterStatsThread is not None:
			self._repeaterStatsThread.quit()
			self._repeaterStatsThread.wait()
			self._repeaterStatsThread = None
			self._repeaterStatsLoop = None


	### Process a new Repeater stats
	def processRepeaterStats(self, iStats):
		# Get stats data
		r = iStats['Repeater']
		aKey = iStats['Key']
		aTimestamp = iStats['Timestamp']
		aDownBytes = iStats['RxBytes']
		aUpBytes = iStats['TxBytes']
		aDownErrors = iStats['RxErrors']
		aUpErrors = iStats['TxErrors']
		aDownRateBytes = 0
		aUpRateBytes = 0
		aDownDeltaErrors = 0
		aUpDeltaErrors = 0

		# Try to find a previously received statistic record
		aPrevStats = r._statsMap.get(aKey)
		if aPrevStats is not None:
			aPrevTimestamp = aPrevStats['Timestamp']
			aPrevDownBytes = aPrevStats['RxBytes']
			aPrevUpBytes = aPrevStats['TxBytes']
			aElapsed = int((aTimestamp - aPrevTimestamp).total_seconds())
			if aElapsed > 0:
				if aDownBytes > aPrevDownBytes:
					aDownRateBytes = int((aDownBytes - aPrevDownBytes) / aElapsed)
				if aUpBytes > aPrevUpBytes:
					aUpRateBytes = int((aUpBytes - aPrevUpBytes) / aElapsed)
			aDownDeltaErrors = aDownErrors - aPrevStats['RxErrors']
			aUpDeltaErrors = aUpErrors - aPrevStats['TxErrors']

		# Remember current stats
		r._statsMap[aKey] = iStats

		# Update UI
		aListLine = r.findStatsLine(aKey)
		if aListLine >= 0:
			aDown = QtWidgets.QTableWidgetItem(LmTools.FmtBytes(aDownBytes))
			aDown.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVertical_Mask)
			if aDownErrors:
				aDown.setForeground(QtCore.Qt.GlobalColor.red)
			r._statsList.setItem(aListLine, StatsCol.Down, aDown)

			aUp = QtWidgets.QTableWidgetItem(LmTools.FmtBytes(aUpBytes))
			aUp.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVertical_Mask)
			if aUpErrors:
				aUp.setForeground(QtCore.Qt.GlobalColor.red)
			r._statsList.setItem(aListLine, StatsCol.Up, aUp)

			if aDownRateBytes:
				aDownRate = QtWidgets.QTableWidgetItem(LmTools.FmtBytes(aDownRateBytes) + '/s')
				if aDownDeltaErrors:
					aDownRate.setForeground(QtCore.Qt.GlobalColor.red)
				aDownRate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVertical_Mask)
			else:
				aDownRate = QtWidgets.QTableWidgetItem('')
			r._statsList.setItem(aListLine, StatsCol.DownRate, aDownRate)

			if aUpRateBytes:
				aUpRate = QtWidgets.QTableWidgetItem(LmTools.FmtBytes(aUpRateBytes) + '/s')
				if aUpDeltaErrors:
					aUpRate.setForeground(QtCore.Qt.GlobalColor.red)
				aUpRate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVertical_Mask)
			else:
				aUpRate = QtWidgets.QTableWidgetItem('')
			r._statsList.setItem(aListLine, StatsCol.UpRate, aUpRate)



# ################################ LmRepHandler class ################################

class LmRepHandler:

	### Init handler
	def __init__(self, iApp, iIndex, iKey, iName, iIPAddress, iActive):
		self._app = iApp
		self._key = iKey
		self._name = iName
		self._ipAddr = iIPAddress
		self._active = iActive
		self._session = None
		self._signed = False
		self._tab = None
		self._tabIndex = MonitorTab.Repeaters + iIndex
		self._statsList = None
		self._statsMap = {}
		self._repeaterAList = None


	### Sign in to repeater
	def signin(self):
		if self.isActive():
			self.signout()
			self._session = LmSession('http://' + self._ipAddr + '/', self._name)
			r = self._session.signin(True)	# Need to ignore cookie as sessions opened with >1h cookie generate errors
			if r:
				self._signed = True
			else:
				LmTools.MouseCursor_Normal()
				LmTools.DisplayError('Repeater ' + self._name + ' authentication failed.')
				self._session = None
			self.setTabIcon()


	### Check if signed to repeater
	def isSigned(self):
		return self._signed


	### Sign out from repeater
	def signout(self):
		if self.isSigned():
			self._signed = False
			self._session.close()
			self._session = None
			self.setTabIcon()


	### Check if active
	def isActive(self):
		return (self._ipAddr is not None) and self._active


	### Set tab icon according to connection status
	def setTabIcon(self):
		if self._tab is not None:
			if self.isSigned():
				self._app._tabWidget.setTabIcon(self._tabIndex, QtGui.QIcon(LmIcon.TickPixmap))
			elif self.isActive():
				self._app._tabWidget.setTabIcon(self._tabIndex, QtGui.QIcon(LmIcon.DenyPixmap))
			else:
				self._app._tabWidget.setTabIcon(self._tabIndex, QtGui.QIcon(LmIcon.CrossPixmap))


	### Find Repeater stats line from stat key
	def findStatsLine(self, iStatsKey):
		if (self._statsList is not None) and len(iStatsKey):
			i = 0
			n = self._statsList.rowCount()
			while (i < n):
				aItem = self._statsList.item(i, StatsCol.Key)
				if aItem.text() == iStatsKey:
					return i
				i += 1
		return -1


	### Process an update of the device name
	def processUpdateDeviceName(self):
		aNewName = LmConf.MacAddrTable.get(self._key, None)
		if aNewName is None:
			aNewName = DEFAULT_REPEATER_NAME + str(self._tabIndex - MonitorTab.Repeaters + 1)
		self._name = aNewName
		self._app._tabWidget.setTabText(self._tabIndex, self._name)


	### Process a device updated event
	def processDeviceUpdatedEvent(self, iEvent):
		aIPv4Struct = iEvent.get('IPv4Address')
		if (aIPv4Struct is None) or (len(aIPv4Struct) == 0):
			aIPv4 = None
		else:
			aIPv4 = aIPv4Struct[0].get('Address', '')
		if self._ipAddr != aIPv4:
			self.processIPAddressEvent(aIPv4)

		self.processActiveEvent(iEvent.get('Active', False))


	### Process an active status change event
	def processActiveEvent(self, iIsActive):
		if self.isActive() != iIsActive:
			if iIsActive:
				self._active = True
				self.signin()
			else:
				self._active = False
				self._signed = False
				self._session = None
				self.setTabIcon()


	### Process a IP Address change event
	def processIPAddressEvent(self, iIPv4):
		self._signed = False
		self._session = None
		self._ipAddr = iIPv4
		self.signin()


	### Click on Repeater infos button
	def repeaterInfoButtonClick(self):
		if self.isSigned():
			self._app.startTask('Getting repeater information...')

			self._repeaterAList.clearContents()
			self._repeaterAList.setRowCount(0)

			self.loadRepeaterInfo()

			self._app.endTask()
		else:
			LmTools.DisplayError('Not signed to repeater.')


	### Click on Wifi infos button
	def wifiInfoButtonClick(self):
		if self.isSigned():
			self._app.startTask('Getting Wifi information...')

			self._repeaterAList.clearContents()
			self._repeaterAList.setRowCount(0)

			self.loadWifiInfo()

			self._app.endTask()
		else:
			LmTools.DisplayError('Not signed to repeater.')


	### Click on LAN infos button
	def lanInfoButtonClick(self):
		if self.isSigned():
			self._app.startTask('Getting LAN information...')

			self._repeaterAList.clearContents()
			self._repeaterAList.setRowCount(0)

			self.loadLanInfo()

			self._app.endTask()
		else:
			LmTools.DisplayError('Not signed to repeater.')


	### Click on Export infos button
	def exportInfoButtonClick(self):
		if self.isSigned():
			aFileName = QtWidgets.QFileDialog.getSaveFileName(self._app, 'Save File', self._name + ' Infos.txt', '*.txt')
			aFileName = aFileName[0]
			if aFileName == '':
				return

			try:
				self._app._exportFile = open(aFileName, 'w')
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				LmTools.DisplayError('Cannot create the file.')
				return

			self._app.startTask('Exporting all information...')

			i = 0
			i = self.loadRepeaterInfo(i)
			i = self.loadWifiInfo(i)
			i = self.loadLanInfo(i)

			self._app._exportFile.close()
			self._app._exportFile = None

			self._app.endTask()
		else:
			LmTools.DisplayError('Not signed to repeater.')


	### Click on Wifi ON button
	def wifiOnButtonClick(self):
		if self.isSigned():
			try:
				LmTools.MouseCursor_Busy()
				d = self._session.request('NMC.Wifi:set', { 'Enable': True, 'Status' : True })
				LmTools.MouseCursor_Normal()
				if d is None:
					LmTools.DisplayError('NMC.Wifi:set service error')
				else:
					LmTools.DisplayStatus('Wifi activated (probably only 5GHz).')
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				LmTools.MouseCursor_Normal()
				LmTools.DisplayError('NMC.Wifi:set service error')
		else:
			LmTools.DisplayError('Not signed to repeater.')


	### Click on Wifi OFF button
	def wifiOffButtonClick(self):
		if self.isSigned():
			try:
				LmTools.MouseCursor_Busy()
				d = self._session.request('NMC.Wifi:set', { 'Enable': False, 'Status' : False })
				LmTools.MouseCursor_Normal()
				if d is None:
					LmTools.DisplayError('NMC.Wifi:set service error')
				else:
					LmTools.DisplayStatus('Wifi deactivated (probably only 5GHz).')
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				LmTools.MouseCursor_Normal()
				LmTools.DisplayError('NMC.Wifi:set service error')
		else:
			LmTools.DisplayError('Not signed to repeater.')


	### Click on Wifi Scheduler ON button
	def schedulerOnButtonClick(self):
		if self.isSigned():
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
		else:
			LmTools.DisplayError('Not signed to repeater.')


	### Click on Wifi Scheduler OFF button
	def schedulerOffButtonClick(self):
		if self.isSigned():
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
		else:
			LmTools.DisplayError('Not signed to repeater.')


	### Click on Reboot Repeater button
	def rebootRepeaterButtonClick(self):
		if self.isSigned():
			if LmTools.AskQuestion('Are you sure you want to reboot the Repeater?'):
				try:
					LmTools.MouseCursor_Busy()
					d = self._session.request('NMC:reboot', { 'reason': 'WebUI reboot' })
					LmTools.MouseCursor_Normal()
					if d.get('status', False):
						self._signed = False
						self._session = None
						self.setTabIcon()
						LmTools.DisplayStatus('Repeater is now restarting.')
					else:
						LmTools.DisplayError('NMC:reboot service failed')
				except BaseException as e:
					LmTools.Error('Error: {}'.format(e))
					LmTools.MouseCursor_Normal()
					LmTools.DisplayError('NMC:reboot service error')
		else:
			LmTools.DisplayError('Not signed to repeater.')


	### Click on Reboot History button
	def rebootHistoryButtonClick(self):
		if self.isSigned():
			self._app.startTask('Getting Reboot History...')

			try:
				d = self._session.request('NMC.Reboot.Reboot:get')
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				d = None
			if d is not None:
				d = d.get('status')

			self._app.endTask()

			if d is None:
				LmTools.DisplayError('NMC.Reboot.Reboot:get service error')
				return

			aHistoryDialog = RebootHistoryDialog('Repeater', self._app)
			aHistoryDialog.loadHistory(d)
			aHistoryDialog.exec()
		else:
			LmTools.DisplayError('Not signed to repeater.')


	### Click on Resign button
	def resignButtonClick(self):
		if self.isActive():
			if LmTools.AskQuestion('Are you sure you want to resign to the Repeater?'):
				LmTools.MouseCursor_Busy()
				self.signin()
				LmTools.MouseCursor_Normal()
		else:
			LmTools.DisplayError('Repeater is inactive.')


	### Add a title line in an info attribute/value list
	def addTitleLine(self, iLine, iTitle):
		return self._app.addTitleLine(self._repeaterAList, iLine, iTitle)


	### Add a line in an info attribute/value list
	def addInfoLine(self, iLine, iAttribute, iValue, iQualifier = LmTools.ValQual.Default):
		return self._app.addInfoLine(self._repeaterAList, iLine, iAttribute, iValue, iQualifier)


	### Load Repeater infos
	def loadRepeaterInfo(self, iIndex = 0):
		i = self.addTitleLine(iIndex, 'Repeater Information')

		try:
			d = self._session.request('DeviceInfo:get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(i, 'Repeater Infos', 'DeviceInfo:get query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(i, 'Model Name', d.get('ModelName'))
			i = self.addInfoLine(i, 'Repeater Up Time', LmTools.FmtTime(d.get('UpTime')))
			i = self.addInfoLine(i, 'Serial Number', d.get('SerialNumber'))
			i = self.addInfoLine(i, 'Hardware Version', d.get('HardwareVersion'))
			i = self.addInfoLine(i, 'Software Version', d.get('SoftwareVersion'))
			i = self.addInfoLine(i, 'Orange Firmware Version', d.get('AdditionalSoftwareVersion'))
			i = self.addInfoLine(i, 'Country', LmTools.FmtStrUpper(d.get('Country')))

		try:
			d = self._session.request('Time:getTime')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			s = d.get('status', False)
			d = d.get('data')
		if (not s) or (d is None):
			i = self.addInfoLine(i, 'Time', 'Time:getTime query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(i, 'Time', d.get('time'))

		# Unfortunately DeviceInfo.MemoryStatus:get service access is denied.

		return i


	### Load Wifi infos
	def loadWifiInfo(self, iIndex = 0):
		i = self.addTitleLine(iIndex, 'Wifi Information')

		try:
			d = self._session.request('NMC.Wifi:get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('data')
		if d is None:
			i = self.addInfoLine(i, 'Wifi', 'NMC.Wifi:get query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(i, 'Enabled', LmTools.FmtBool(d.get('Enable')))
			i = self.addInfoLine(i, 'Active', LmTools.FmtBool(d.get('Status')))
			i = self.addInfoLine(i, 'Read Only', LmTools.FmtBool(d.get('ReadOnlyStatus')))
			i = self.addInfoLine(i, 'Pairing Status', d.get('PairingStatus'))
			i = self.addInfoLine(i, 'PIN Code', d.get('PINCode'))

		try:
			d = self._session.request('Scheduler:getCompleteSchedules', { 'type': 'WLAN' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if (d is not None) and (d.get('status', False)):
			d = d.get('data')
		else:
			d = None
		if d is None:
			i = self.addInfoLine(i, 'Scheduler Enabled', 'Scheduler:getCompleteSchedules query error', LmTools.ValQual.Error)
		else:
			d = d.get('scheduleInfo', [])
			if len(d):
				aActive = d[0].get('enable', False)
			else:
				aActive = False
			i = self.addInfoLine(i, 'Scheduler Enabled', LmTools.FmtBool(aActive))

		b = None
		w = None
		try:
			d = self._session.request('NeMo.Intf.lan:getMIBs', { 'mibs': 'base wlanradio' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			b = d.get('base')
			w = d.get('wlanradio')

		try:
			d = self._session.request('NeMo.Intf.lan:getMIBs', { 'mibs': 'wlanvap', 'flag': 'wlanvap !secondary' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			d = d.get('wlanvap')

		if (d is None) or (b is None) or (w is None):
			i = self.addInfoLine(i, 'Wifi', 'NeMo.Intf.lan:getMIBs query error', LmTools.ValQual.Error)
			return i 

		for s in NET_INTF:
			if s['Type'] != 'wif':
				continue
			i = self.addTitleLine(i, s['Name'])

			# Get Wifi interface key in wlanradio list
			aIntfKey = None
			aBase = b.get(s['Key'])
			if aBase is not None:
				i = self.addInfoLine(i, 'Enabled', LmTools.FmtBool(aBase.get('Enable')))
				i = self.addInfoLine(i, 'Active', LmTools.FmtBool(aBase.get('Status')))
				aLowLevelIntf = aBase.get('LLIntf')
				if aLowLevelIntf is not None:
					for aKey in aLowLevelIntf:
						aIntfKey = aKey
						break

			q = w.get(aIntfKey) if aIntfKey is not None else None
			r = d.get(s['Key'])
			if (q is None) or (r is None):
				continue

			i = self.addInfoLine(i, 'Radio Status', q.get('RadioStatus'))
			i = self.addInfoLine(i, 'VAP Status', r.get('VAPStatus'))
			i = self.addInfoLine(i, 'Vendor Name', LmTools.FmtStrUpper(q.get('VendorName')))
			i = self.addInfoLine(i, 'MAC Address', LmTools.FmtStrUpper(r.get('MACAddress')))
			i = self.addInfoLine(i, 'SSID', r.get('SSID'))
			i = self.addInfoLine(i, 'SSID Advertisement', LmTools.FmtBool(r.get('SSIDAdvertisementEnabled')))

			t = r.get('Security')
			if t is not None:
				i = self.addInfoLine(i, 'Security Mode', t.get('ModeEnabled'))
				i = self.addInfoLine(i, 'WEP Key', t.get('WEPKey'))
				i = self.addInfoLine(i, 'PreShared Key', t.get('PreSharedKey'))
				i = self.addInfoLine(i, 'Key Pass Phrase', t.get('KeyPassPhrase'))

			t = r.get('WPS')
			if t is not None:
				i = self.addInfoLine(i, 'WPS Enabled', LmTools.FmtBool(t.get('Enable')))
				i = self.addInfoLine(i, 'WPS Methods', t.get('ConfigMethodsEnabled'))
				i = self.addInfoLine(i, 'WPS Self PIN', t.get('SelfPIN'))
				i = self.addInfoLine(i, 'WPS Pairing In Progress', LmTools.FmtBool(t.get('PairingInProgress')))

			t = r.get('MACFiltering')
			if t is not None:
				i = self.addInfoLine(i, 'MAC Filtering', t.get('Mode'))

			i = self.addInfoLine(i, 'Max Bitrate', LmTools.FmtInt(q.get('MaxBitRate')))
			i = self.addInfoLine(i, 'AP Mode', LmTools.FmtBool(q.get('AP_Mode')))
			i = self.addInfoLine(i, 'STA Mode', LmTools.FmtBool(q.get('STA_Mode')))
			i = self.addInfoLine(i, 'WDS Mode', LmTools.FmtBool(q.get('WDS_Mode')))
			i = self.addInfoLine(i, 'WET Mode', LmTools.FmtBool(q.get('WET_Mode')))
			i = self.addInfoLine(i, 'Frequency Band', q.get('OperatingFrequencyBand'))
			i = self.addInfoLine(i, 'Channel Bandwidth', q.get('CurrentOperatingChannelBandwidth'))
			i = self.addInfoLine(i, 'Standard', q.get('OperatingStandards'))
			i = self.addInfoLine(i, 'Channel', LmTools.FmtInt(q.get('Channel')))
			i = self.addInfoLine(i, 'Auto Channel Supported', LmTools.FmtBool(q.get('AutoChannelSupported')))
			i = self.addInfoLine(i, 'Auto Channel Enabled', LmTools.FmtBool(q.get('AutoChannelEnable')))
			i = self.addInfoLine(i, 'Channel Change Reason', q.get('ChannelChangeReason'))
			i = self.addInfoLine(i, 'Max Associated Devices', LmTools.FmtInt(q.get('MaxAssociatedDevices')))
			i = self.addInfoLine(i, 'Active Associated Devices', LmTools.FmtInt(q.get('ActiveAssociatedDevices')))
			i = self.addInfoLine(i, 'Noise', LmTools.FmtInt(q.get('Noise')))
			i = self.addInfoLine(i, 'Antenna Defect', LmTools.FmtBool(q.get('AntennaDefect')))

		return i


	### Load LAN infos
	def loadLanInfo(self, iIndex = 0):
		i = self.addTitleLine(iIndex, 'LAN Information')

		d = None
		try:
			q = self._session.request('NMC:getWANStatus')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			q = None
		if q is not None:
			d = q.get('status')
		if (d is None) or (not d):
			i = self.addInfoLine(i, 'LAN Infos', 'NMC:getWANStatus query error', LmTools.ValQual.Error)
		if q is not None:
			d = q.get('data')
		else:
			d = None
		if d is None:
			i = self.addInfoLine(i, 'LAN Infos', 'NMC:getWANStatus data error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(i, 'MAC Address', LmTools.FmtStrUpper(d.get('MACAddress')))
			i = self.addInfoLine(i, 'Link Status', LmTools.FmtStrCapitalize(d.get('LinkState')))
			i = self.addInfoLine(i, 'Link Type', LmTools.FmtStrUpper(d.get('LinkType')))
			i = self.addInfoLine(i, 'Protocol', LmTools.FmtStrUpper(d.get('Protocol')))
			i = self.addInfoLine(i, 'Connection Status', d.get('ConnectionState'))
			i = self.addInfoLine(i, 'Last Connection Error', d.get('LastConnectionError'))
			i = self.addInfoLine(i, 'IP Address', d.get('IPAddress'))
			i = self.addInfoLine(i, 'Remote Gateway', d.get('RemoteGateway'))
			i = self.addInfoLine(i, 'DNS Servers', d.get('DNSServers'))
			i = self.addInfoLine(i, 'IPv6 Address', d.get('IPv6Address'))

		try:
			d = self._session.request('NeMo.Intf.data:getFirstParameter', { 'name': 'MTU' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is None:
			i = self.addInfoLine(i, 'MTU', 'NeMo.Intf.data:getFirstParameter query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(i, 'MTU', LmTools.FmtInt(d.get('status')))

		i = self.addTitleLine(i, 'Link to the Livebox')

		try:
			d = self._session.request('UplinkMonitor.DefaultGateway:get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(i, 'Livebox link Infos', 'UplinkMonitor.DefaultGateway:get query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(i, 'IP Address', d.get('IPv4Address'))
			i = self.addInfoLine(i, 'MAC Address', LmTools.FmtStrUpper(d.get('MACAddress')))
			i = self.addInfoLine(i, 'Interface', LmTools.FmtStrCapitalize(d.get('NeMoIntfName')))

		b = None
		try:
			d = self._session.request('NeMo.Intf.lan:getMIBs', { 'mibs': 'base eth' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			b = d.get('base')
			d = d.get('eth')

		if (d is None) or (b is None):
			i = self.addInfoLine(i, 'LAN', 'NeMo.Intf.lan:getMIBs query error', LmTools.ValQual.Error)
			return

		for s in NET_INTF:
			if s['Type'] != 'eth':
				continue
			i = self.addTitleLine(i, s['Name'])

			q = b.get(s['Key'])
			r = d.get(s['Key'])
			if (q is None) or (r is None):
				continue

			i = self.addInfoLine(i, 'Enabled', LmTools.FmtBool(q.get('Enable')))
			i = self.addInfoLine(i, 'Active', LmTools.FmtBool(q.get('Status')))
			i = self.addInfoLine(i, 'Current Bit Rate', LmTools.FmtInt(r.get('CurrentBitRate')))
			i = self.addInfoLine(i, 'Max Bit Rate Supported', LmTools.FmtInt(r.get('MaxBitRateSupported')))
			i = self.addInfoLine(i, 'Current Duplex Mode', r.get('CurrentDuplexMode'))
			i = self.addInfoLine(i, 'Power Saving Supported', LmTools.FmtBool(q.get('PowerSavingSupported')))
			i = self.addInfoLine(i, 'Power Saving Enabled', LmTools.FmtBool(q.get('PowerSavingEnabled')))

		return i


	### Get Wifi statuses (used by ActionsTab)
	def getWifiStatus(self):
		u = {}
		u[WifiKey.AccessPoint] = self._name

		if not self.isActive():
			u[WifiKey.Enable] = WifiStatus.Inactive
			u[WifiKey.Status] = WifiStatus.Inactive
			u[WifiKey.Scheduler] = WifiStatus.Inactive
			u[WifiKey.Wifi2Enable] = WifiStatus.Inactive
			u[WifiKey.Wifi2Status] = WifiStatus.Inactive
			u[WifiKey.Wifi2VAP] = WifiStatus.Inactive
			u[WifiKey.Wifi5Enable] = WifiStatus.Inactive
			u[WifiKey.Wifi5Status] = WifiStatus.Inactive
			u[WifiKey.Wifi5VAP] = WifiStatus.Inactive
			return u

		if not self.isSigned():
			u[WifiKey.Enable] = WifiStatus.Unsigned
			u[WifiKey.Status] = WifiStatus.Unsigned
			u[WifiKey.Scheduler] = WifiStatus.Unsigned
			u[WifiKey.Wifi2Enable] = WifiStatus.Unsigned
			u[WifiKey.Wifi2Status] = WifiStatus.Unsigned
			u[WifiKey.Wifi2VAP] = WifiStatus.Unsigned
			u[WifiKey.Wifi5Enable] = WifiStatus.Unsigned
			u[WifiKey.Wifi5Status] = WifiStatus.Unsigned
			u[WifiKey.Wifi5VAP] = WifiStatus.Unsigned
			return u

		try:
			d = self._session.request('NMC.Wifi:get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('data')
		if d is None:
			u[WifiKey.Enable] = WifiStatus.Error
			u[WifiKey.Status] = WifiStatus.Error
		else:
			u[WifiKey.Enable] = WifiStatus.Enable if d.get('Enable', False) else WifiStatus.Disable
			u[WifiKey.Status] = WifiStatus.Enable if d.get('Status', False) else WifiStatus.Disable

		try:
			d = self._session.request('Scheduler:getCompleteSchedules', { 'type': 'WLAN' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if (d is not None) and (d.get('status', False)):
			d = d.get('data')
		else:
			d = None
		if d is None:
			u[WifiKey.Scheduler] = WifiStatus.Error
		else:
			d = d.get('scheduleInfo', [])
			if len(d):
				u[WifiKey.Scheduler] = WifiStatus.Enable if d[0].get('enable', False) else WifiStatus.Disable
			else:
				u[WifiKey.Scheduler] = WifiStatus.Disable

		b = None
		w = None
		try:
			d = self._session.request('NeMo.Intf.lan:getMIBs', { 'mibs': 'base wlanradio' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			b = d.get('base')
			w = d.get('wlanradio')

		try:
			d = self._session.request('NeMo.Intf.lan:getMIBs', { 'mibs': 'wlanvap', 'flag': 'wlanvap !secondary' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			d = d.get('wlanvap')

		if (d is None) or (b is None) or (w is None):
			u[WifiKey.Wifi2Enable] = WifiStatus.Error
			u[WifiKey.Wifi2Status] = WifiStatus.Error
			u[WifiKey.Wifi2VAP] = WifiStatus.Error
			u[WifiKey.Wifi5Enable] = WifiStatus.Error
			u[WifiKey.Wifi5Status] = WifiStatus.Error
			u[WifiKey.Wifi5VAP] = WifiStatus.Error
		else:
			for s in NET_INTF:
				if s['Type'] != 'wif':
					continue

				if s['Name'] == 'Wifi 2.4GHz':
					aEnableKey = WifiKey.Wifi2Enable
					aStatusKey = WifiKey.Wifi2Status
					aVAPKey = WifiKey.Wifi2VAP
				else:
					aEnableKey = WifiKey.Wifi5Enable
					aStatusKey = WifiKey.Wifi5Status
					aVAPKey = WifiKey.Wifi5VAP

				# Get Wifi interface key in wlanradio list
				aIntfKey = None
				aBase = b.get(s['Key'])
				if aBase is not None:
					u[aEnableKey] = WifiStatus.Enable if aBase.get('Enable', False) else WifiStatus.Disable
					u[aStatusKey] = WifiStatus.Enable if aBase.get('Status', False) else WifiStatus.Disable

					aLowLevelIntf = aBase.get('LLIntf')
					if aLowLevelIntf is not None:
						for aKey in aLowLevelIntf:
							aIntfKey = aKey
							break
				else:
					u[aEnableKey] = WifiStatus.Error
					u[aStatusKey] = WifiStatus.Error

				q = w.get(aIntfKey) if aIntfKey is not None else None
				r = d.get(s['Key'])
				if (q is None) or (r is None):
					u[aVAPKey] = WifiStatus.Error
				else:
					u[aVAPKey] = WifiStatus.Enable if (r.get('VAPStatus', 'Down') == 'Up') else WifiStatus.Disable

		return u



# ############# Repeaters global stats collector thread #############
class RepeaterStatsThread(QtCore.QObject):
	_statsReceived = QtCore.pyqtSignal(dict)
	_resume = QtCore.pyqtSignal()

	def __init__(self, iRepeaters):
		super(RepeaterStatsThread, self).__init__()
		self._repeaters = iRepeaters
		self._timer = None
		self._loop = None
		self._isRunning = False


	def run(self):
		self._timer = QtCore.QTimer()
		self._timer.timeout.connect(self.collectStats)
		self._loop = QtCore.QEventLoop()
		self.resume()


	def resume(self):
		if not self._isRunning:
			self._timer.start(1000)
			self._isRunning = True
			self._loop.exec()
			self._timer.stop()
			self._isRunning = False


	def stop(self):
		if self._isRunning:
			self._loop.exit()


	def collectStats(self):
		for r in self._repeaters:
			if r.isSigned():
				for s in NET_INTF:
					aResult = r._session.request('NeMo.Intf.' + s['Key'] + ':getNetDevStats' , {})
					aStats = aResult.get('status')
					if aStats is not None:
						e = {}
						e['Repeater'] = r
						e['Key'] = s['Key']
						e['Timestamp'] = datetime.datetime.now()
						if s['SwapStats']:
							e['RxBytes'] = aStats.get('TxBytes', 0)
							e['TxBytes'] = aStats.get('RxBytes', 0)
							e['RxErrors'] = aStats.get('TxErrors', 0)
							e['TxErrors'] = aStats.get('RxErrors', 0)
						else:
							e['RxBytes'] = aStats.get('RxBytes', 0)
							e['TxBytes'] = aStats.get('TxBytes', 0)
							e['RxErrors'] = aStats.get('RxErrors', 0)
							e['TxErrors'] = aStats.get('TxErrors', 0)
						self._statsReceived.emit(e)
