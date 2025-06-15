### Livebox Monitor Wifi Repeater info tab module ###

import datetime
import re
import json

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmTableWidget import LmTableWidget
from LiveboxMonitor.api.LmSession import LmSession
from LiveboxMonitor.dlg.LmRebootHistory import RebootHistoryDialog
from LiveboxMonitor.tabs.LmInfoTab import InfoCol, StatsCol
from LiveboxMonitor.api.LmWifiApi import WifiKey, WifiStatus
from LiveboxMonitor.lang.LmLanguages import get_repeater_label as lx, get_repeater_message as mx


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'repeaterTab'	# 'Key' dynamic property indicates the MAC addr

# Static Config
WIFI_REPEATER_TYPES = {'repeteurwifi', 'repeteurwifi6', 'sah ap'}
WIFI_REPEATER_5 = 'WIFIREPARCFR'
WIFI_REPEATER_6 = 'WIFI6REPSERCOMM'
WIFI_REPEATER_PRODUCT_CLASSES = [WIFI_REPEATER_5, WIFI_REPEATER_6]
WIFI_REPEATER_VERSION_MAP = {WIFI_REPEATER_5: 5, WIFI_REPEATER_6: 6}
DEFAULT_REPEATER_NAME = 'RW #'
DEBUG_BUTTON = False

#  Wifi Repeater 5 Interfaces
NET_INTF_WR5 = [
	{'Key': 'bridge',     'Name': 'LAN',          'Type': 'lan', 'SwapStats': True},
	{'Key': 'eth1_0',     'Name': 'Ethernet 1',   'Type': 'eth', 'SwapStats': True},
	{'Key': 'eth1_1',     'Name': 'Ethernet 2',   'Type': 'eth', 'SwapStats': True},
	{'Key': 'wl0',        'Name': 'Wifi 2.4GHz',  'Type': 'wif', 'SwapStats': True},
	{'Key': 'vap5g0priv', 'Name': 'Wifi 5GHz',    'Type': 'wif', 'SwapStats': True}
]

# Wifi Repeater 6 Interfaces
NET_INTF_WR6 = [
	{'Key': 'bridge',     'Name': 'LAN',          'Type': 'lan', 'SwapStats': True},
	{'Key': 'eth0',       'Name': 'Ethernet 1',   'Type': 'eth', 'SwapStats': True},
	{'Key': 'eth1',       'Name': 'Ethernet 2',   'Type': 'eth', 'SwapStats': True},
	{'Key': 'vap2g0priv', 'Name': 'Wifi 2.4GHz',  'Type': 'wif', 'SwapStats': True},
	{'Key': 'vap5g0priv', 'Name': 'Wifi 5GHz',    'Type': 'wif', 'SwapStats': True}
]

# Interface name mapping
INTF_NAME_MAP_WR = {'Eth0': 'Eth1', 'Eth1': 'Eth2',
					'Eth0-1': 'Eth1', 'Eth1-1': 'Eth2',
					'Eth1_0': 'Eth1', 'Eth1_1': 'Eth2'}


# ################################ LmRepeater class ################################

class LmRepeater:

	### Create Repeater tab
	def createRepeaterTab(self, iRepeater):
		iRepeater._tab = QtWidgets.QWidget(objectName = TAB_NAME)
		iRepeater._tab.setProperty('Key', iRepeater._key)

		# Statistics list
		aStatsList = LmTableWidget(objectName = 'statsList')
		aStatsList.set_columns({StatsCol.Key: ['Key', 0, None],
								StatsCol.Name: [lx('Name'), 100, 'stats_Name'],
								StatsCol.Down: [lx('Rx'), 65, 'stats_Rx'],
								StatsCol.Up: [lx('Tx'), 65, 'stats_Tx'],
								StatsCol.DownRate: [lx('RxRate'), 65, 'stats_RxRate'],
								StatsCol.UpRate: [lx('TxRate'), 65, 'stats_TxRate']})
		aStatsList.set_header_resize([StatsCol.Down, StatsCol.Up, StatsCol.DownRate, StatsCol.UpRate])
		aStatsList.set_standard_setup(self, allow_sel=False, allow_sort=False)
		aStatsList.setMinimumWidth(450)

		i = 0
		for s in iRepeater._netIntf:
			aStatsList.insertRow(i)
			aStatsList.setItem(i, StatsCol.Key, QtWidgets.QTableWidgetItem(s['Key']))
			aStatsList.setItem(i, StatsCol.Name, QtWidgets.QTableWidgetItem(s['Name']))
			i += 1
		aStatsListSize = LmConfig.table_height(i)
		aStatsList.setMinimumHeight(aStatsListSize)
		aStatsList.setMaximumHeight(aStatsListSize)

		iRepeater._statsList = aStatsList

		# 1st action buttons line
		aButtonsSet1 = QtWidgets.QHBoxLayout()
		aButtonsSet1.setSpacing(20)

		aWifiOnButton = QtWidgets.QPushButton(lx('Wifi ON'), objectName = 'wifiOn')
		aWifiOnButton.clicked.connect(iRepeater.wifiOnButtonClick)
		aButtonsSet1.addWidget(aWifiOnButton)

		aWifiOffButton = QtWidgets.QPushButton(lx('Wifi OFF'), objectName = 'wifiOff')
		aWifiOffButton.clicked.connect(iRepeater.wifiOffButtonClick)
		aButtonsSet1.addWidget(aWifiOffButton)

		# 2nd action buttons line
		if iRepeater._version >= 6:		# Scheduler available only starting WR6
			aButtonsSet2 = QtWidgets.QHBoxLayout()
			aButtonsSet2.setSpacing(20)

			aSchedulerOnButton = QtWidgets.QPushButton(lx('Wifi Scheduler ON'), objectName = 'schedulerOn')
			aSchedulerOnButton.clicked.connect(iRepeater.schedulerOnButtonClick)
			aButtonsSet2.addWidget(aSchedulerOnButton)

			aSchedulerOffButton = QtWidgets.QPushButton(lx('Wifi Scheduler OFF'), objectName = 'schedulerOff')
			aSchedulerOffButton.clicked.connect(iRepeater.schedulerOffButtonClick)
			aButtonsSet2.addWidget(aSchedulerOffButton)

		# 3nd action buttons line
		aButtonsSet3 = QtWidgets.QHBoxLayout()
		aButtonsSet3.setSpacing(20)

		aRebootRepeaterButton = QtWidgets.QPushButton(lx('Reboot Repeater...'), objectName = 'rebootRepeater')
		aRebootRepeaterButton.clicked.connect(iRepeater.rebootRepeaterButtonClick)
		aButtonsSet3.addWidget(aRebootRepeaterButton)

		if iRepeater._version >= 6:		# Reboot history available only starting WR6
			aRebootHistoryButton = QtWidgets.QPushButton(lx('Reboot History...'), objectName = 'rebootHistory')
			aRebootHistoryButton.clicked.connect(iRepeater.rebootHistoryButtonClick)
			aButtonsSet3.addWidget(aRebootHistoryButton)

		# 4nd action buttons line
		aButtonsSet4 = QtWidgets.QHBoxLayout()
		aButtonsSet4.setSpacing(20)

		aResignButton = QtWidgets.QPushButton(lx('Resign...'), objectName = 'resign')
		aResignButton.clicked.connect(iRepeater.resignButtonClick)
		aButtonsSet4.addWidget(aResignButton)

		# Debug Button
		if DEBUG_BUTTON:
			aDebugButton = QtWidgets.QPushButton('Debug...', objectName = 'debug')
			aDebugButton.clicked.connect(iRepeater.debugButtonClick)

		# Action buttons group box
		aGroupBox = QtWidgets.QGroupBox(lx('Actions'), objectName = 'actionsGroup')
		aGroupBoxLayout = QtWidgets.QVBoxLayout()
		aGroupBoxLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aGroupBoxLayout.setSpacing(20)
		aGroupBoxLayout.addLayout(aButtonsSet1, 0)
		if iRepeater._version >= 6:		# Scheduler available only starting WR6
			aGroupBoxLayout.addLayout(aButtonsSet2, 0)
		aGroupBoxLayout.addLayout(aButtonsSet3, 0)
		aGroupBoxLayout.addLayout(aButtonsSet4, 0)
		if DEBUG_BUTTON:
			aGroupBoxLayout.addWidget(aDebugButton)
		aGroupBox.setLayout(aGroupBoxLayout)

		# Stats & actions box
		aLeftBox = QtWidgets.QVBoxLayout()
		aLeftBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aLeftBox.setSpacing(20)
		aLeftBox.addWidget(iRepeater._statsList, 0, QtCore.Qt.AlignmentFlag.AlignTop)
		aLeftBox.addWidget(aGroupBox, 0, QtCore.Qt.AlignmentFlag.AlignTop)

		# Attribute list
		aRepeaterAList = LmTableWidget(objectName = 'repeaterAList')
		aRepeaterAList.set_columns({InfoCol.Attribute: [lx('Attribute'), 200, 'alist_Attribute'],
									InfoCol.Value: [lx('Value'), 600, 'alist_Value']})
		aRepeaterAList.set_header_resize([InfoCol.Value])
		aRepeaterAList.set_standard_setup(self, allow_sel=False, allow_sort=False)
		iRepeater._repeaterAList = aRepeaterAList

		# Lists layout
		aListBox = QtWidgets.QHBoxLayout()
		aListBox.setSpacing(10)
		aListBox.addLayout(aLeftBox, 0)
		aListBox.addWidget(iRepeater._repeaterAList, 1)

		# Button bar
		aButtonsBox = QtWidgets.QHBoxLayout()
		aButtonsBox.setSpacing(10)

		aRepeaterInfoButton = QtWidgets.QPushButton(lx('Repeater Infos'), objectName = 'repeaterInfo')
		aRepeaterInfoButton.clicked.connect(iRepeater.repeaterInfoButtonClick)
		aButtonsBox.addWidget(aRepeaterInfoButton)

		aWifiInfoButton = QtWidgets.QPushButton(lx('Wifi Infos'), objectName = 'wifiInfo')
		aWifiInfoButton.clicked.connect(iRepeater.wifiInfoButtonClick)
		aButtonsBox.addWidget(aWifiInfoButton)

		aLanInfoButton = QtWidgets.QPushButton(lx('LAN Infos'), objectName = 'lanInfo')
		aLanInfoButton.clicked.connect(iRepeater.lanInfoButtonClick)
		aButtonsBox.addWidget(aLanInfoButton)

		aSeparator = QtWidgets.QFrame()
		aSeparator.setFrameShape(QtWidgets.QFrame.Shape.VLine)
		aSeparator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
		aButtonsBox.addWidget(aSeparator)

		aExportInfoButton = QtWidgets.QPushButton(lx('Export...'), objectName = 'exportInfo')
		aExportInfoButton.clicked.connect(iRepeater.exportInfoButtonClick)
		aButtonsBox.addWidget(aExportInfoButton)

		# Layout
		aVBox = QtWidgets.QVBoxLayout()
		aVBox.setSpacing(10)
		aVBox.addLayout(aListBox, 0)
		aVBox.addLayout(aButtonsBox, 1)
		iRepeater._tab.setLayout(aVBox)

		LmConfig.set_tooltips(iRepeater._tab, 'repeater')
		self._tab_widget.insertTab(iRepeater.tabIndexFromConfig(), iRepeater._tab, iRepeater._name)
		iRepeater.setTabIcon()


	### Identify potential Wifi Repeater device & add it to the list
	# PowerManagement:getElements() method returns a "REPEATER_DEVICES" entry that suggests that a generic way to
	# identify repeaters could be to check the tags with the expression "ssw and (wifi or eth)"
	def identifyRepeater(self, iDevice):
		aDeviceType = iDevice.get('DeviceType', '')
		aProdClass = iDevice.get('ProductClass', '')

		if (aDeviceType.lower() in WIFI_REPEATER_TYPES) or (aProdClass in WIFI_REPEATER_PRODUCT_CLASSES):
			aKey = iDevice.get('Key', '')

			# Check if not already there
			for r in self._repeaters:
				if r._key == aKey:
					return None

			aIndex = len(self._repeaters)

			aMacAddr = iDevice.get('PhysAddress', '')
			try:
				aName = LmConf.MacAddrTable[aMacAddr]
			except Exception:
				aName = DEFAULT_REPEATER_NAME + str(aIndex + 1)

			# Determine version
			aModelName = None
			aSSW = iDevice.get('SSW')
			if isinstance(aSSW, dict):
				aModelName = aSSW.get('ModelName')
			if aModelName is None:
				aModelName = aProdClass		# In some cases the model name is indicated in product class
			try:
				aVersion = WIFI_REPEATER_VERSION_MAP[aModelName]
			except Exception:
				aVersion = 5	# Default to version 5

			aIPStruct = LmTools.determine_ip(iDevice)
			if aIPStruct is None:
				aIPAddress = None
			else:
				aIPAddress = aIPStruct.get('Address')

			aActive = iDevice.get('Active', False)

			aRepeater = LmRepHandler(self, aIndex, aKey, aMacAddr, aName, aVersion, aIPAddress, aActive)
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


	### Remove a potential Wifi Repeater device - no really remove, rather desactivate
	def removePotentialRepeater(self, iDeviceKey):
		for r in self._repeaters:
			if r._key == iDeviceKey:
				r.processActiveEvent(False)
				break


	### Init repeater tabs & sessions
	def initRepeaters(self):
		for r in self._repeaters:
			self.createRepeaterTab(r)
		self.signinRepeaters()


	### Sign in to all repeaters
	def signinRepeaters(self):
		self._task.start(lx('Signing in to repeaters...'))
		for r in self._repeaters:
			r.signin()
		self._task.end()


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
				r.process_device_updated_event(iEvent)
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
		aPrevStats = r._stats_map.get(aKey)
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
		r._stats_map[aKey] = iStats

		# Update UI
		aListLine = r.findStatsLine(aKey)
		if aListLine >= 0:
			aDown = QtWidgets.QTableWidgetItem(LmTools.fmt_bytes(aDownBytes))
			aDown.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
			if aDownErrors:
				aDown.setForeground(QtCore.Qt.GlobalColor.red)
			r._statsList.setItem(aListLine, StatsCol.Down, aDown)

			aUp = QtWidgets.QTableWidgetItem(LmTools.fmt_bytes(aUpBytes))
			aUp.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
			if aUpErrors:
				aUp.setForeground(QtCore.Qt.GlobalColor.red)
			r._statsList.setItem(aListLine, StatsCol.Up, aUp)

			if aDownRateBytes:
				aDownRate = QtWidgets.QTableWidgetItem(LmTools.fmt_bytes(aDownRateBytes) + '/s')
				if aDownDeltaErrors:
					aDownRate.setForeground(QtCore.Qt.GlobalColor.red)
				aDownRate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
			else:
				aDownRate = QtWidgets.QTableWidgetItem('')
			r._statsList.setItem(aListLine, StatsCol.DownRate, aDownRate)

			if aUpRateBytes:
				aUpRate = QtWidgets.QTableWidgetItem(LmTools.fmt_bytes(aUpRateBytes) + '/s')
				if aUpDeltaErrors:
					aUpRate.setForeground(QtCore.Qt.GlobalColor.red)
				aUpRate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
			else:
				aUpRate = QtWidgets.QTableWidgetItem('')
			r._statsList.setItem(aListLine, StatsCol.UpRate, aUpRate)



# ################################ LmRepHandler class ################################

class LmRepHandler:

	### Init handler
	def __init__(self, iApp, iIndex, iKey, iMacAddr, iName, iVersion, iIPAddress, iActive):
		self._app = iApp
		self._key = iKey
		self._macAddr = iMacAddr
		self._name = iName
		self._version = iVersion
		self._ipAddr = iIPAddress
		self._active = iActive
		self._session = None
		self._signed = False
		self._tab = None
		self._index = iIndex
		self._statsList = None
		self._stats_map = {}
		self._repeaterAList = None
		self.setNetIntf()


	### Set Net Interfaces according to Repeater versions
	def setNetIntf(self):
		if self._version == 5:
			self._netIntf = NET_INTF_WR5
		elif self._version == 6:
			self._netIntf = NET_INTF_WR6
		else:
			self._netIntf = []


	### Sign in to repeater
	def signin(self, iForce = False):
		if (not iForce) and (not self.isActive()):
			return

		self.signout()

		aUser, aPassword = LmConf.get_repeater_user_password(self._macAddr)

		while True:
			self._session = LmSession('http://' + self._ipAddr + '/', self._name)
			try:
				# Need to ignore cookie as sessions opened with >1h cookie generate errors
				r = self._session.signin(aUser, aPassword, True)
			except Exception as e:
				LmTools.error(str(e))
				r = -1
			if r > 0:
				self._signed = True
				break

			if r < 0:
				self._app.display_error(mx('Cannot connect to repeater {} ({}).', 'cnxErr').format(self._name, self._ipAddr))
				self._session = None
				self._signed = False
				break

			self._app._task.suspend()
			aPassword, aOK = QtWidgets.QInputDialog.getText(self._app, lx('Wrong repeater password'),
															lx('Please enter password for repeater {0} ({1}):').format(self._name, self._ipAddr),
															QtWidgets.QLineEdit.EchoMode.Password,
															text = aPassword)
			self._app._task.resume()
			if aOK:
				# Remove unwanted characters from password (can be set via Paste action)
				aPassword = re.sub('[\n\t]', '', aPassword)
				LmConf.set_repeater_password(self._macAddr, aPassword)
			else:
				self._session = None
				self._signed = False
				break

		self.setTabIcon()


	### Check if signed to repeater
	def isSigned(self):
		return self._signed


	### Sign out from repeater
	def signout(self):
		if self.isSigned():
			self._signed = False
			if self._session is not None:
				self._session.close()
			self._session = None
			self.setTabIcon()


	### Check if active
	def isActive(self):
		return (self._ipAddr is not None) and self._active


	### Get tab index from configuration at creation time
	def tabIndexFromConfig(self):
		# If no config, append
		n = self._app._tab_widget.count()
		if LmConf.Tabs is None:
			return n

		# If not in config, append
		aEntryName = TAB_NAME + '_' + self._key
		try:
			i = LmConf.Tabs.index(aEntryName)
		except Exception:
			return n

		# Try to find the tab immediately on the left
		while i:
			j = i
			while j:
				j -= 1
				t = LmConf.Tabs[j]
				if t.startswith(TAB_NAME + '_'):
					k = t[len(TAB_NAME) + 1:]
					t = TAB_NAME
				else:
					k = None

				aLeftTabIndex = self._app.get_tab_index(t, k)
				if aLeftTabIndex != -1:
					return aLeftTabIndex + 1
			i -= 1

		# No left tab found, must be the first then
		return 0


	### Get tab index
	def tabIndex(self):
		if self._tab is not None:
			return self._app._tab_widget.indexOf(self._tab)
		return -1


	### Set tab icon according to connection status
	def setTabIcon(self):
		if self._tab is not None:
			if self.isSigned():
				self._app._tab_widget.setTabIcon(self.tabIndex(), QtGui.QIcon(LmIcon.TickPixmap))
			elif self.isActive():
				self._app._tab_widget.setTabIcon(self.tabIndex(), QtGui.QIcon(LmIcon.DenyPixmap))
			else:
				self._app._tab_widget.setTabIcon(self.tabIndex(), QtGui.QIcon(LmIcon.CrossPixmap))


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
			aNewName = DEFAULT_REPEATER_NAME + str(self._index + 1)
		self._name = aNewName
		self._app._tab_widget.setTabText(self.tabIndex(), self._name)


	### Process a device updated event
	def process_device_updated_event(self, iEvent):
		aIPv4Struct = LmTools.determine_ip(iEvent)
		if aIPv4Struct is None:
			aIPv4 = None
		else:
			aIPv4 = aIPv4Struct.get('Address')
		if self._ipAddr != aIPv4:
			self.processIPAddressEvent(aIPv4)

		self.processActiveEvent(iEvent.get('Active', False))


	### Process an active status change event
	def processActiveEvent(self, iIsActive):
		if self._active != iIsActive:
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
		self.setTabIcon()
		self.signin()


	### Click on Repeater infos button
	def repeaterInfoButtonClick(self):
		if self.isSigned():
			self._app._task.start(lx('Getting repeater information...'))

			self._repeaterAList.clearContents()
			self._repeaterAList.setRowCount(0)

			self.loadRepeaterInfo()

			self._app._task.end()
		else:
			self._app.display_error(mx('Not signed to repeater.', 'noSign'))


	### Click on Wifi infos button
	def wifiInfoButtonClick(self):
		if self.isSigned():
			self._app._task.start(lx('Getting Wifi information...'))

			self._repeaterAList.clearContents()
			self._repeaterAList.setRowCount(0)

			self.loadWifiInfo()

			self._app._task.end()
		else:
			self._app.display_error(mx('Not signed to repeater.', 'noSign'))


	### Click on LAN infos button
	def lanInfoButtonClick(self):
		if self.isSigned():
			self._app._task.start(lx('Getting LAN information...'))

			self._repeaterAList.clearContents()
			self._repeaterAList.setRowCount(0)

			self.loadLanInfo()

			self._app._task.end()
		else:
			self._app.display_error(mx('Not signed to repeater.', 'noSign'))


	### Click on Export infos button
	def exportInfoButtonClick(self):
		if self.isSigned():
			aFileName = QtWidgets.QFileDialog.getSaveFileName(self._app, lx('Save File'), lx('{} Infos.txt').format(self._name), '*.txt')[0]
			if not aFileName:
				return

			try:
				self._app._export_file = open(aFileName, 'w')
			except Exception as e:
				LmTools.error(str(e))
				self._app.display_error(mx('Cannot create the file.', 'createFileErr'))
				return

			self._app._task.start(lx('Exporting all information...'))

			i = 0
			i = self.loadRepeaterInfo(i)
			i = self.loadWifiInfo(i)
			i = self.loadLanInfo(i)

			try:
				self._app._export_file.close()
			except Exception as e:
				LmTools.error(str(e))
				self._app.display_error(mx('Cannot save the file.', 'saveFileErr'))

			self._app._export_file = None

			self._app._task.end()
		else:
			self._app.display_error(mx('Not signed to repeater.', 'noSign'))


	### Click on Wifi ON button
	def wifiOnButtonClick(self):
		if self.isSigned():
			self._app._task.start(lx('Activating Repeater Wifi...'))
			try:
				d = self._session.request('NMC.Wifi', 'set', { 'Enable': True, 'Status' : True })
				if d is None:
					self._app.display_error('NMC.Wifi:set service error')
				else:
					self._app.display_status(mx('Wifi activated (probably only 5GHz).', 'wifiOn'))
			except Exception as e:
				LmTools.error(str(e))
				self._app.display_error('NMC.Wifi:set service error')
			self._app._task.end()
		else:
			self._app.display_error(mx('Not signed to repeater.', 'noSign'))


	### Click on Wifi OFF button
	def wifiOffButtonClick(self):
		if self.isSigned():
			self._app._task.start(lx('Deactivating Repeater Wifi...'))
			try:
				d = self._session.request('NMC.Wifi', 'set', { 'Enable': False, 'Status' : False })
				if d is None:
					self._app.display_error('NMC.Wifi:set service error')
				else:
					self._app.display_status(mx('Wifi deactivated (probably only 5GHz).', 'wifiOff'))
			except Exception as e:
				LmTools.error(str(e))
				self._app.display_error('NMC.Wifi:set service error')
			self._app._task.end()
		else:
			self._app.display_error(mx('Not signed to repeater.', 'noSign'))


	### Click on Wifi Scheduler ON button
	def schedulerOnButtonClick(self):
		if self.isSigned():
			self._app._task.start(lx('Activating Repeater Scheduler...'))

			# ID has to remain 'wl0' - it is NOT corresponding to an intf key
			try:
				d = self._session.request('Scheduler', 'enableSchedule', { 'type' : 'WLAN', 'ID' : 'wl0', 'enable': True })
				aErrors = LmTools.get_errors_from_livebox_reply(d)
				if d is not None:
					d = d.get('status')
				if d:
					self._app.display_status(mx('Scheduler activated.', 'schedOn'))
				else:
					self._app.display_error('Scheduler:enableSchedule service error.\n{}'.format(aErrors))
			except Exception as e:
				LmTools.error(str(e))
				self._app.display_error('Scheduler:enableSchedule service error')
			self._app._task.end()
		else:
			self._app.display_error(mx('Not signed to repeater.', 'noSign'))


	### Click on Wifi Scheduler OFF button
	def schedulerOffButtonClick(self):
		if self.isSigned():
			self._app._task.start(lx('Deactivating Repeater Scheduler...'))

			# ID has to remain 'wl0' - it is NOT corresponding to an intf key
			try:
				d = self._session.request('Scheduler', 'enableSchedule', { 'type' : 'WLAN', 'ID' : 'wl0', 'enable': False })
				aErrors = LmTools.get_errors_from_livebox_reply(d)
				if d is not None:
					d = d.get('status')
				if d:
					self._app.display_status(mx('Scheduler deactivated.', 'schedOff'))
				else:
					self._app.display_error('Scheduler:enableSchedule service error.\n{}'.format(aErrors))
			except Exception as e:
				LmTools.error(str(e))
				self._app.display_error('Scheduler:enableSchedule service error')
			self._app._task.end()
		else:
			self._app.display_error(mx('Not signed to repeater.', 'noSign'))


	### Click on Reboot Repeater button
	def rebootRepeaterButtonClick(self):
		if self.isSigned():
			if self._app.ask_question(mx('Are you sure you want to reboot the Repeater?', 'reboot')):
				self._app._task.start(lx('Rebooting Repeater...'))
				try:
					d = self._session.request('NMC', 'reboot', { 'reason': 'WebUI reboot' })
					if (d is not None) and (d.get('status', False)):
						self._app.display_status(mx('Repeater is now restarting.', 'rebooting'))
					else:
						self._app.display_error('NMC:reboot service failed')
				except Exception as e:
					LmTools.error(str(e))
					self._app.display_error('NMC:reboot service error')
				self._app._task.end()
		else:
			self._app.display_error(mx('Not signed to repeater.', 'noSign'))


	### Click on Reboot History button
	def rebootHistoryButtonClick(self):
		if self.isSigned():
			self._app._task.start(lx('Getting Reboot History...'))

			try:
				d = self._session.request('NMC.Reboot.Reboot', 'get')
			except Exception as e:
				LmTools.error(str(e))
				d = None
			if d is not None:
				d = d.get('status')

			self._app._task.end()

			if d is None:
				self._app.display_error('NMC.Reboot.Reboot:get service error')
				return

			aHistoryDialog = RebootHistoryDialog('Repeater', self._app)
			aHistoryDialog.load_history(d)
			aHistoryDialog.exec()
		else:
			self._app.display_error(mx('Not signed to repeater.', 'noSign'))


	### Click on Resign button
	def resignButtonClick(self):
		aDoIt = False
		aForceIt = False
		if self.isActive():
			aDoIt = self._app.ask_question(mx('Are you sure you want to resign to the Repeater?', 'resign'))
		else:
			aDoIt = self._app.ask_question(mx('Repeater is inactive. Do you want to force signin?', 'forceResign'))
			aForceIt = True
		if aDoIt:
			self._app._task.start(lx('Signing in to repeater...'))
			self.signin(aForceIt)
			self._app._task.end()

			# Sometimes the active event isn't raised
			if self.isSigned():
				self._active = True


	### Click on Debug button
	def debugButtonClick(self):
		if self.isSigned():
			try:
				LmTools.mouse_cursor_busy()
				d = self._session.request('NeMo.Intf.data', 'getMIBs')
				LmTools.mouse_cursor_normal()
				if d is None:
					self._app.display_error('NeMo.Intf.data:getMIBs service failed')
				else:
					self._app.display_infos('NeMo.Intf.data:getMIBs', json.dumps(d, indent=2))
			except Exception as e:
				LmTools.error(str(e))
				LmTools.mouse_cursor_normal()
				self._app.display_error('NeMo.Intf.data:getMIBs service error')

			try:
				LmTools.mouse_cursor_busy()
				d = self._session.request('NeMo.Intf.lan', 'getMIBs')
				LmTools.mouse_cursor_normal()
				if d is None:
					self._app.display_error('NeMo.Intf.lan:getMIBs service failed')
				else:
					self._app.display_infos('NeMo.Intf.lan:getMIBs', json.dumps(d, indent=2))
			except Exception as e:
				LmTools.error(str(e))
				LmTools.mouse_cursor_normal()
				self._app.display_error('NeMo.Intf.lan:getMIBs service error')
		else:
			self._app.display_error(mx('Not signed to repeater.', 'noSign'))


	### Add a title line in an info attribute/value list
	def addTitleLine(self, iLine, iTitle):
		return self._app.add_title_line(self._repeaterAList, iLine, iTitle)


	### Add a line in an info attribute/value list
	def addInfoLine(self, iLine, iAttribute, iValue, iQualifier = LmTools.ValQual.Default):
		return self._app.add_info_line(self._repeaterAList, iLine, iAttribute, iValue, iQualifier)


	### Load Repeater infos
	def loadRepeaterInfo(self, iIndex = 0):
		i = self.addTitleLine(iIndex, lx('Repeater Information'))

		try:
			d = self._session.request('DeviceInfo', 'get')
		except Exception as e:
			LmTools.error(str(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(i, lx('Repeater Infos'), 'DeviceInfo:get query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(i, lx('Model Name'), d.get('ModelName'))
			i = self.addInfoLine(i, lx('Repeater Up Time'), LmTools.fmt_time(d.get('UpTime')))
			i = self.addInfoLine(i, lx('Serial Number'), d.get('SerialNumber'))
			i = self.addInfoLine(i, lx('Hardware Version'), d.get('HardwareVersion'))
			i = self.addInfoLine(i, lx('Software Version'), d.get('SoftwareVersion'))
			i = self.addInfoLine(i, lx('Orange Firmware Version'), d.get('AdditionalSoftwareVersion'))
			i = self.addInfoLine(i, lx('Country'), LmTools.fmt_str_upper(d.get('Country')))

		try:
			d = self._session.request('NMC.Reboot', 'get')
		except Exception as e:
			LmTools.error(str(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(i, lx('Repeater Infos'), 'NMC.Reboot:get query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(i, lx('Total Number Of Reboots'), LmTools.fmt_int(d.get('BootCounter')))

		try:
			d = self._session.request('Time', 'getTime')
		except Exception as e:
			LmTools.error(str(e))
			d = None
		if d is not None:
			s = d.get('status', False)
			d = d.get('data')
		else:
			s = False
		if (not s) or (d is None):
			i = self.addInfoLine(i, lx('Time'), 'Time:getTime query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(i, lx('Time'), d.get('time'))

		# Unfortunately DeviceInfo.MemoryStatus:get service access is denied.

		return i


	### Load Wifi infos
	def loadWifiInfo(self, iIndex = 0):
		i = self.addTitleLine(iIndex, lx('Wifi Information'))

		try:
			d = self._session.request('NMC.Wifi', 'get')
		except Exception as e:
			LmTools.error(str(e))
			d = None
		if d is not None:
			d = d.get('data')
		if d is None:
			i = self.addInfoLine(i, lx('Wifi'), 'NMC.Wifi:get query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(i, lx('Enabled'), LmTools.fmt_bool(d.get('Enable')))
			i = self.addInfoLine(i, lx('Active'), LmTools.fmt_bool(d.get('Status')))
			i = self.addInfoLine(i, lx('Mode'), d.get('EnableTarget'))
			i = self.addInfoLine(i, lx('WPS Mode'), d.get('WPSMode'))
			i = self.addInfoLine(i, lx('Link Type'), d.get('CurrentBackhaul'))
			i = self.addInfoLine(i, lx('Read Only'), LmTools.fmt_bool(d.get('ReadOnlyStatus')))
			i = self.addInfoLine(i, lx('Pairing Status'), d.get('PairingStatus'))
			i = self.addInfoLine(i, lx('PIN Code'), d.get('PINCode'))

		if self._version >= 6:		# Scheduler available only starting WR6
			try:
				d = self._session.request('Scheduler', 'getCompleteSchedules', { 'type': 'WLAN' })
			except Exception as e:
				LmTools.error(str(e))
				d = None
			if (d is not None) and (d.get('status', False)):
				d = d.get('data')
			else:
				d = None
			if d is None:
				i = self.addInfoLine(i, lx('Scheduler Enabled'), 'Scheduler:getCompleteSchedules query error', LmTools.ValQual.Error)
			else:
				d = d.get('scheduleInfo', [])
				if len(d):
					aActive = d[0].get('enable', False)
				else:
					aActive = False
				i = self.addInfoLine(i, lx('Scheduler Enabled'), LmTools.fmt_bool(aActive))

		b = None
		w = None
		try:
			d = self._session.request('NeMo.Intf.lan', 'getMIBs', { 'mibs': 'base wlanradio' })
		except Exception as e:
			LmTools.error(str(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			b = d.get('base')
			w = d.get('wlanradio')

		try:
			d = self._session.request('NeMo.Intf.lan', 'getMIBs', { 'mibs': 'wlanvap', 'flag': 'wlanvap !secondary' })
		except Exception as e:
			LmTools.error(str(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			d = d.get('wlanvap')

		if (d is None) or (b is None) or (w is None):
			i = self.addInfoLine(i, lx('Wifi'), 'NeMo.Intf.lan:getMIBs query error', LmTools.ValQual.Error)
			return i 

		for s in self._netIntf:
			if s['Type'] != 'wif':
				continue
			i = self.addTitleLine(i, s['Name'])

			# Get Wifi interface key in wlanradio list
			aIntfKey = None
			aBase = b.get(s['Key'])
			if aBase is not None:
				i = self.addInfoLine(i, lx('Enabled'), LmTools.fmt_bool(aBase.get('Enable')))
				i = self.addInfoLine(i, lx('Active'), LmTools.fmt_bool(aBase.get('Status')))
				aLowLevelIntf = aBase.get('LLIntf')
				if aLowLevelIntf is not None:
					for aKey in aLowLevelIntf:
						aIntfKey = aKey
						break

			q = w.get(aIntfKey) if aIntfKey is not None else None
			r = d.get(s['Key'])
			if (q is None) or (r is None):
				continue

			i = self.addInfoLine(i, lx('Radio Status'), q.get('RadioStatus'))
			i = self.addInfoLine(i, lx('VAP Status'), r.get('VAPStatus'))
			i = self.addInfoLine(i, lx('Vendor Name'), LmTools.fmt_str_upper(q.get('VendorName')))
			i = self.addInfoLine(i, lx('MAC Address'), LmTools.fmt_str_upper(r.get('MACAddress')))
			i = self.addInfoLine(i, lx('SSID'), r.get('SSID'))
			i = self.addInfoLine(i, lx('SSID Advertisement'), LmTools.fmt_bool(r.get('SSIDAdvertisementEnabled')))

			t = r.get('Security')
			if t is not None:
				i = self.addInfoLine(i, lx('Security Mode'), t.get('ModeEnabled'))
				i = self.addInfoLine(i, lx('WEP Key'), t.get('WEPKey'))
				i = self.addInfoLine(i, lx('PreShared Key'), t.get('PreSharedKey'))
				i = self.addInfoLine(i, lx('Key Pass Phrase'), t.get('KeyPassPhrase'))

			t = r.get('WPS')
			if t is not None:
				i = self.addInfoLine(i, lx('WPS Enabled'), LmTools.fmt_bool(t.get('Enable')))
				i = self.addInfoLine(i, lx('WPS Methods'), t.get('ConfigMethodsEnabled'))
				i = self.addInfoLine(i, lx('WPS Self PIN'), t.get('SelfPIN'))
				i = self.addInfoLine(i, lx('WPS Pairing In Progress'), LmTools.fmt_bool(t.get('PairingInProgress')))

			t = r.get('MACFiltering')
			if t is not None:
				i = self.addInfoLine(i, lx('MAC Filtering'), t.get('Mode'))

			i = self.addInfoLine(i, lx('Max Bitrate'), LmTools.fmt_int(q.get('MaxBitRate')))
			i = self.addInfoLine(i, lx('AP Mode'), LmTools.fmt_bool(q.get('AP_Mode')))
			i = self.addInfoLine(i, lx('STA Mode'), LmTools.fmt_bool(q.get('STA_Mode')))
			i = self.addInfoLine(i, lx('WDS Mode'), LmTools.fmt_bool(q.get('WDS_Mode')))
			i = self.addInfoLine(i, lx('WET Mode'), LmTools.fmt_bool(q.get('WET_Mode')))
			i = self.addInfoLine(i, lx('Frequency Band'), q.get('OperatingFrequencyBand'))
			i = self.addInfoLine(i, lx('Channel Bandwidth'), q.get('CurrentOperatingChannelBandwidth'))
			i = self.addInfoLine(i, lx('Standard'), q.get('OperatingStandards'))
			i = self.addInfoLine(i, lx('Channel'), LmTools.fmt_int(q.get('Channel')))
			i = self.addInfoLine(i, lx('Auto Channel Supported'), LmTools.fmt_bool(q.get('AutoChannelSupported')))
			i = self.addInfoLine(i, lx('Auto Channel Enabled'), LmTools.fmt_bool(q.get('AutoChannelEnable')))
			i = self.addInfoLine(i, lx('Channel Change Reason'), q.get('ChannelChangeReason'))
			i = self.addInfoLine(i, lx('Max Associated Devices'), LmTools.fmt_int(q.get('MaxAssociatedDevices')))
			i = self.addInfoLine(i, lx('Active Associated Devices'), LmTools.fmt_int(q.get('ActiveAssociatedDevices')))
			i = self.addInfoLine(i, lx('Noise'), LmTools.fmt_int(q.get('Noise')))
			i = self.addInfoLine(i, lx('Antenna Defect'), LmTools.fmt_bool(q.get('AntennaDefect')))

		return i


	### Load LAN infos
	def loadLanInfo(self, iIndex = 0):
		i = self.addTitleLine(iIndex, lx('LAN Information'))

		d = None
		try:
			q = self._session.request('NMC', 'getWANStatus')
		except Exception as e:
			LmTools.error(str(e))
			q = None
		if q is not None:
			d = q.get('status')
		if (d is None) or (not d):
			i = self.addInfoLine(i, lx('LAN Infos'), 'NMC:getWANStatus query error', LmTools.ValQual.Error)
		if q is not None:
			d = q.get('data')
		else:
			d = None
		if d is None:
			i = self.addInfoLine(i, lx('LAN Infos'), 'NMC:getWANStatus data error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(i, lx('MAC Address'), LmTools.fmt_str_upper(d.get('MACAddress')))
			i = self.addInfoLine(i, lx('Link Status'), LmTools.fmt_str_capitalize(d.get('LinkState')))
			i = self.addInfoLine(i, lx('Link Type'), LmTools.fmt_str_upper(d.get('LinkType')))
			i = self.addInfoLine(i, lx('Protocol'), LmTools.fmt_str_upper(d.get('Protocol')))
			i = self.addInfoLine(i, lx('Connection Status'), d.get('ConnectionState'))
			i = self.addInfoLine(i, lx('Last Connection Error'), d.get('LastConnectionError'))
			i = self.addInfoLine(i, lx('IP Address'), d.get('IPAddress'))
			i = self.addInfoLine(i, lx('Remote Gateway'), d.get('RemoteGateway'))
			i = self.addInfoLine(i, lx('DNS Servers'), d.get('DNSServers'))
			i = self.addInfoLine(i, lx('IPv6 Address'), d.get('IPv6Address'))

		try:
			d = self._session.request('NeMo.Intf.data', 'getFirstParameter', { 'name': 'MTU' })
		except Exception as e:
			LmTools.error(str(e))
			d = None
		if d is None:
			i = self.addInfoLine(i, lx('MTU'), 'NeMo.Intf.data:getFirstParameter query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(i, lx('MTU'), LmTools.fmt_int(d.get('status')))

		i = self.addTitleLine(i, lx('Link to the Livebox'))

		try:
			d = self._session.request('UplinkMonitor.DefaultGateway', 'get')
		except Exception as e:
			LmTools.error(str(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(i, lx('Livebox link Infos'), 'UplinkMonitor.DefaultGateway:get query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(i, lx('IP Address'), d.get('IPv4Address'))
			i = self.addInfoLine(i, lx('MAC Address'), LmTools.fmt_str_upper(d.get('MACAddress')))
			i = self.addInfoLine(i, lx('Interface'), LmTools.fmt_str_capitalize(d.get('NeMoIntfName')))

		b = None
		try:
			d = self._session.request('NeMo.Intf.lan', 'getMIBs', { 'mibs': 'base eth' })
		except Exception as e:
			LmTools.error(str(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			b = d.get('base')
			d = d.get('eth')

		if (d is None) or (b is None):
			i = self.addInfoLine(i, lx('LAN'), 'NeMo.Intf.lan:getMIBs query error', LmTools.ValQual.Error)
			return

		for s in self._netIntf:
			if s['Type'] != 'eth':
				continue
			i = self.addTitleLine(i, s['Name'])

			q = b.get(s['Key'])
			r = d.get(s['Key'])
			if (q is None) or (r is None):
				continue

			i = self.addInfoLine(i, lx('Enabled'), LmTools.fmt_bool(q.get('Enable')))
			i = self.addInfoLine(i, lx('Active'), LmTools.fmt_bool(q.get('Status')))
			i = self.addInfoLine(i, lx('Current Bit Rate'), LmTools.fmt_int(r.get('CurrentBitRate')))
			i = self.addInfoLine(i, lx('Max Bit Rate Supported'), LmTools.fmt_int(r.get('MaxBitRateSupported')))
			i = self.addInfoLine(i, lx('Current Duplex Mode'), r.get('CurrentDuplexMode'))
			i = self.addInfoLine(i, lx('Power Saving Supported'), LmTools.fmt_bool(q.get('PowerSavingSupported')))
			i = self.addInfoLine(i, lx('Power Saving Enabled'), LmTools.fmt_bool(q.get('PowerSavingEnabled')))

		return i


	### Get Wifi statuses (used by ActionsTab)
	def getWifiStatus(self):
		u = {}
		u[WifiKey.ACCESS_POINT] = self._name

		if not self.isActive():
			u[WifiKey.ENABLE] = WifiStatus.INACTIVE
			u[WifiKey.STATUS] = WifiStatus.INACTIVE
			u[WifiKey.SCHEDULER] = WifiStatus.INACTIVE
			u[WifiKey.WIFI2_ENABLE] = WifiStatus.INACTIVE
			u[WifiKey.WIFI2_STATUS] = WifiStatus.INACTIVE
			u[WifiKey.WIFI2_VAP] = WifiStatus.INACTIVE
			u[WifiKey.WIFI5_ENABLE] = WifiStatus.INACTIVE
			u[WifiKey.WIFI5_STATUS] = WifiStatus.INACTIVE
			u[WifiKey.WIFI5_VAP] = WifiStatus.INACTIVE
			if self._version >= 99:		# To be updated if a repeater supporting 6 GHz is produced
				u[WifiKey.WIFI6_ENABLE] = WifiStatus.INACTIVE
				u[WifiKey.WIFI6_STATUS] = WifiStatus.INACTIVE
				u[WifiKey.WIFI6_VAP] = WifiStatus.INACTIVE
			return u

		if not self.isSigned():
			u[WifiKey.ENABLE] = WifiStatus.UNSIGNED
			u[WifiKey.STATUS] = WifiStatus.UNSIGNED
			u[WifiKey.SCHEDULER] = WifiStatus.UNSIGNED
			u[WifiKey.WIFI2_ENABLE] = WifiStatus.UNSIGNED
			u[WifiKey.WIFI2_STATUS] = WifiStatus.UNSIGNED
			u[WifiKey.WIFI2_VAP] = WifiStatus.UNSIGNED
			u[WifiKey.WIFI5_ENABLE] = WifiStatus.UNSIGNED
			u[WifiKey.WIFI5_STATUS] = WifiStatus.UNSIGNED
			u[WifiKey.WIFI5_VAP] = WifiStatus.UNSIGNED
			if self._version >= 99:		# To be updated if a repeater supporting 6 GHz is produced
				u[WifiKey.WIFI6_ENABLE] = WifiStatus.UNSIGNED
				u[WifiKey.WIFI6_STATUS] = WifiStatus.UNSIGNED
				u[WifiKey.WIFI6_VAP] = WifiStatus.UNSIGNED
			return u

		# General Wifi status
		aWifiSchedulerStatus = None
		try:
			d = self._session.request('NMC.Wifi', 'get')
		except Exception as e:
			LmTools.error(str(e))
			d = None
		if d is not None:
			d = d.get('data')
		if d is None:
			u[WifiKey.ENABLE] = WifiStatus.ERROR
			u[WifiKey.STATUS] = WifiStatus.ERROR
		else:
			u[WifiKey.ENABLE] = WifiStatus.ENABLE if d.get('Enable', False) else WifiStatus.DISABLE
			u[WifiKey.STATUS] = WifiStatus.ENABLE if d.get('Status', False) else WifiStatus.DISABLE
			aWifiSchedulerStatus = d.get('SchedulingEnabled')

		# Wifi scheduler status
		if self._version >= 6:		# Scheduler available only starting WR6
			aStatus = None
			try:
				d = self._session.request('Scheduler', 'getCompleteSchedules', { 'type': 'WLAN' })
			except Exception as e:
				LmTools.error(str(e))
				d = None
			if (d is not None) and (d.get('status', False)):
				d = d.get('data')
			else:
				d = None
			if d is None:
				u[WifiKey.SCHEDULER] = WifiStatus.ERROR
			else:
				d = d.get('scheduleInfo', [])
				if len(d):
					aStatus = d[0].get('enable')

			# Agregate result
			if aStatus is None:
				if aWifiSchedulerStatus is None:
					u[WifiKey.SCHEDULER] = WifiStatus.ERROR
				else:
					u[WifiKey.SCHEDULER] = WifiStatus.ENABLE if aWifiSchedulerStatus else WifiStatus.DISABLE
			else:
				if aWifiSchedulerStatus is None:
					u[WifiKey.SCHEDULER] = WifiStatus.ENABLE if aStatus else WifiStatus.DISABLE
				else:
					u[WifiKey.SCHEDULER] = WifiStatus.ENABLE if (aStatus and aWifiSchedulerStatus) else WifiStatus.DISABLE

		b = None
		w = None
		try:
			d = self._session.request('NeMo.Intf.lan', 'getMIBs', { 'mibs': 'base wlanradio wlanvap' })
		except Exception as e:
			LmTools.error(f'NeMo.Intf.lan:getMIBs error: {e}')
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			b = d.get('base')
			w = d.get('wlanradio')
			d = d.get('wlanvap')

		if (d is None) or (b is None) or (w is None):
			u[WifiKey.WIFI2_ENABLE] = WifiStatus.ERROR
			u[WifiKey.WIFI2_STATUS] = WifiStatus.ERROR
			u[WifiKey.WIFI2_VAP] = WifiStatus.ERROR
			u[WifiKey.WIFI5_ENABLE] = WifiStatus.ERROR
			u[WifiKey.WIFI5_STATUS] = WifiStatus.ERROR
			u[WifiKey.WIFI5_VAP] = WifiStatus.ERROR
			if self._version >= 99:		# To be updated if a repeater supporting 6 GHz is produced
				u[WifiKey.WIFI6_ENABLE] = WifiStatus.ERROR
				u[WifiKey.WIFI6_STATUS] = WifiStatus.ERROR
				u[WifiKey.WIFI6_VAP] = WifiStatus.ERROR
		else:
			for s in self._netIntf:
				if s['Type'] != 'wif':
					continue

				if s['Name'] == 'Wifi 2.4GHz':
					aEnableKey = WifiKey.WIFI2_ENABLE
					aStatusKey = WifiKey.WIFI2_STATUS
					aVAPKey = WifiKey.WIFI2_VAP
				elif s['Name'] == 'Wifi 5GHz':
					aEnableKey = WifiKey.WIFI5_ENABLE
					aStatusKey = WifiKey.WIFI5_STATUS
					aVAPKey = WifiKey.WIFI5_VAP
				else:
					aEnableKey = WifiKey.WIFI6_ENABLE
					aStatusKey = WifiKey.WIFI6_STATUS
					aVAPKey = WifiKey.WIFI6_VAP

				# Get Wifi interface key in wlanradio list
				aIntfKey = None
				aBase = b.get(s['Key'])
				if aBase is not None:
					u[aEnableKey] = WifiStatus.ENABLE if aBase.get('Enable', False) else WifiStatus.DISABLE
					u[aStatusKey] = WifiStatus.ENABLE if aBase.get('Status', False) else WifiStatus.DISABLE

					aLowLevelIntf = aBase.get('LLIntf')
					if aLowLevelIntf is not None:
						for aKey in aLowLevelIntf:
							aIntfKey = aKey
							break
				else:
					u[aEnableKey] = WifiStatus.ERROR
					u[aStatusKey] = WifiStatus.ERROR

				q = w.get(aIntfKey) if aIntfKey is not None else None
				r = d.get(s['Key'])
				if (q is None) or (r is None):
					u[aVAPKey] = WifiStatus.ERROR
				else:
					u[aVAPKey] = WifiStatus.ENABLE if (r.get('VAPStatus', 'Down') == 'Up') else WifiStatus.DISABLE

		return u



# ############# Repeaters global stats collector thread #############
class RepeaterStatsThread(QtCore.QObject):
	_statsReceived = QtCore.pyqtSignal(dict)
	_resume = QtCore.pyqtSignal()

	def __init__(self, iRepeaters):
		super().__init__()
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
			self._timer.start(LmConf.StatsFrequency)
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
				for s in r._netIntf:
					if r._session is not None:
						aResult = r._session.request('NeMo.Intf.' + s['Key'], 'getNetDevStats' , {})
						if aResult is not None:
							if aResult.get('errors') is not None:
								# Session has timed out on Repeater side, resign
								r.signin()
							aStats = aResult.get('status')
							if isinstance(aStats, dict):
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
						else:
							# Session has timed out on Repeater side, resign
							r.signin()

