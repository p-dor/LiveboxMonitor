### Livebox Monitor device list tab module ###

import datetime

from enum import IntEnum
from ipaddress import IPv4Address

from PyQt6 import QtCore, QtGui, QtWidgets

from src import LmTools, LmConfig
from src.LmConfig import LmConf
from src.LmIcons import LmIcon
from src.LmDhcpTab import DhcpCol
from src.LmLanguages import (GetDeviceListLabel as lx,
							 GetIPv6DialogLabel as lix,
							 GetDnsDialogLabel as ldx)


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'deviceListTab'

# List columns
class DevCol(IntEnum):
	Key = 0
	Type = 1
	Name = 2
	LBName = 3
	MAC = 4
	IP = 5
	Link = 6
	Active = 7
	Wifi = 8
	Event = 9
	Down = 10
	Up = 11
	DownRate = 12
	UpRate = 13
	Count = 14
ICON_COLUMNS = [DevCol.Type, DevCol.Active, DevCol.Wifi, DevCol.Event]

class DSelCol(IntEnum):
	Key = 0		# Must be the same as DevCol.Key
	Name = 1
	MAC = 2
	Count = 3



# ################################ LmDeviceList class ################################
class LmDeviceList:

	### Create device list tab
	def createDeviceListTab(self):
		self._deviceListTab = QtWidgets.QWidget(objectName = TAB_NAME)

		# Device list columns
		self._deviceList = QtWidgets.QTableWidget(objectName = 'deviceList')
		self._deviceList.setColumnCount(DevCol.Count)
		self._deviceList.setHorizontalHeaderLabels(('Key', lx('T'), 
														   lx('Name'),
														   lx('Livebox Name'),
														   lx('MAC'),
														   lx('IP'),
														   lx('Link'),
														   lx('A'),
														   lx('Wifi'),
														   lx('E'),
														   lx('Rx'),
														   lx('Tx'),
														   lx('RxRate'),
														   lx('TxRate')))
		self._deviceList.setColumnHidden(DevCol.Key, True)
		aHeader = self._deviceList.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aHeader.setSectionResizeMode(DevCol.Name, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aHeader.setSectionResizeMode(DevCol.LBName, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aHeader.setSectionResizeMode(DevCol.Link, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aModel = aHeader.model()
		aModel.setHeaderData(DevCol.Type, QtCore.Qt.Orientation.Horizontal, 'dlist_Type', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DevCol.Name, QtCore.Qt.Orientation.Horizontal, 'dlist_Name', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DevCol.LBName, QtCore.Qt.Orientation.Horizontal, 'dlist_LBName', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DevCol.MAC, QtCore.Qt.Orientation.Horizontal, 'dlist_MAC', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DevCol.IP, QtCore.Qt.Orientation.Horizontal, 'dlist_IP', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DevCol.Link, QtCore.Qt.Orientation.Horizontal, 'dlist_Link', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DevCol.Active, QtCore.Qt.Orientation.Horizontal, 'dlist_Active', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DevCol.Wifi, QtCore.Qt.Orientation.Horizontal, 'dlist_Wifi', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DevCol.Event, QtCore.Qt.Orientation.Horizontal, 'dlist_Event', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DevCol.Down, QtCore.Qt.Orientation.Horizontal, 'dlist_Rx', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DevCol.Up, QtCore.Qt.Orientation.Horizontal, 'dlist_Tx', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DevCol.DownRate, QtCore.Qt.Orientation.Horizontal, 'dlist_RxRate', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DevCol.UpRate, QtCore.Qt.Orientation.Horizontal, 'dlist_TxRate', QtCore.Qt.ItemDataRole.UserRole)
		self._deviceList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._deviceList.setColumnWidth(DevCol.Type, 48)
		self._deviceList.setColumnWidth(DevCol.Name, 400)
		self._deviceList.setColumnWidth(DevCol.LBName, 400)
		self._deviceList.setColumnWidth(DevCol.MAC, 120)
		self._deviceList.setColumnWidth(DevCol.IP, 105)
		self._deviceList.setColumnWidth(DevCol.Link, 150)
		self._deviceList.setColumnWidth(DevCol.Active, 10)
		self._deviceList.setColumnWidth(DevCol.Wifi, 70)
		self._deviceList.setColumnWidth(DevCol.Event, 10)
		self._deviceList.setColumnWidth(DevCol.Down, 75)
		self._deviceList.setColumnWidth(DevCol.Up, 75)
		self._deviceList.setColumnWidth(DevCol.DownRate, 75)
		self._deviceList.setColumnWidth(DevCol.UpRate, 75)
		self._deviceList.verticalHeader().hide()
		self._deviceList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self._deviceList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
		self._deviceList.setSortingEnabled(True)
		self._deviceList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		self._deviceList.setItemDelegate(LmTools.CenteredIconsDelegate(self, ICON_COLUMNS))
		LmConfig.SetTableStyle(self._deviceList)

		# Button bar
		aHBox = QtWidgets.QHBoxLayout()
		aHBox.setSpacing(30)
		aRefreshDeviceListButton = QtWidgets.QPushButton(lx('Refresh'), objectName = 'refresh')
		aRefreshDeviceListButton.clicked.connect(self.refreshDeviceListButtonClick)
		aHBox.addWidget(aRefreshDeviceListButton)
		aDeviceInfoButton = QtWidgets.QPushButton(lx('Device Infos'), objectName = 'deviceInfo')
		aDeviceInfoButton.clicked.connect(self.deviceInfoButtonClick)
		aHBox.addWidget(aDeviceInfoButton)
		aDeviceEventsButton = QtWidgets.QPushButton(lx('Device Events'), objectName = 'deviceEvents')
		aDeviceEventsButton.clicked.connect(self.deviceEventsButtonClick)
		aHBox.addWidget(aDeviceEventsButton)
		aIPv6Button = QtWidgets.QPushButton(lx('IPv6...'), objectName = 'ipv6')
		aIPv6Button.clicked.connect(self.ipv6ButtonClick)
		aHBox.addWidget(aIPv6Button)
		aDnsButton = QtWidgets.QPushButton(lx('DNS...'), objectName = 'dns')
		aDnsButton.clicked.connect(self.dnsButtonClick)
		aHBox.addWidget(aDnsButton)

		# Layout
		aVBox = QtWidgets.QVBoxLayout()
		aVBox.setSpacing(10)
		aVBox.addWidget(self._deviceList, 0)
		aVBox.addLayout(aHBox, 1)
		self._deviceListTab.setLayout(aVBox)

		LmConfig.SetToolTips(self._deviceListTab, 'dlist')
		self._tabWidget.addTab(self._deviceListTab, lx('Device List'))


	### Init the Livebox Wifi stats collector thread
	def initWifiStatsLoop(self):
		if LmConf.RealtimeWifiStats:
			self._liveboxWifiStatsMap = {}
			self._liveboxWifiStatsThread = None
			self._liveboxWifiStatsLoop = None


	### Start the Livebox Wifi stats collector thread
	def startWifiStatsLoop(self):
		if LmConf.RealtimeWifiStats:
			self._liveboxWifiStatsThread = QtCore.QThread()
			self._liveboxWifiStatsLoop = LiveboxWifiStatsThread(self._session)
			self._liveboxWifiStatsLoop.moveToThread(self._liveboxWifiStatsThread)
			self._liveboxWifiStatsThread.started.connect(self._liveboxWifiStatsLoop.run)
			self._liveboxWifiStatsLoop._wifiStatsReceived.connect(self.processLiveboxWifiStats)
			self._liveboxWifiStatsLoop._resume.connect(self._liveboxWifiStatsLoop.resume)
			self._liveboxWifiStatsThread.start()


	### Suspend the Livebox Wifi stats collector thread
	def suspendWifiStatsLoop(self):
		if LmConf.RealtimeWifiStats:
			if self._liveboxWifiStatsThread is not None:
				self._liveboxWifiStatsLoop.stop()


	### Resume the Livebox Wifi stats collector thread
	def resumeWifiStatsLoop(self):
		if LmConf.RealtimeWifiStats:
			if self._liveboxWifiStatsThread is None:
				self.startWifiStatsLoop()
			else:
				self._liveboxWifiStatsLoop._resume.emit()


	### Stop the Livebox Wifi stats collector thread
	def stopWifiStatsLoop(self):
		if LmConf.RealtimeWifiStats:
			if self._liveboxWifiStatsThread is not None:
				self._liveboxWifiStatsThread.quit()
				self._liveboxWifiStatsThread.wait()
				self._liveboxWifiStatsThread = None
				self._liveboxWifiStatsLoop = None


	### Click on refresh device list button
	def refreshDeviceListButtonClick(self):
		self._deviceList.clearContents()
		self._deviceList.setRowCount(0)
		self._infoDList.clearContents()
		self._infoDList.setRowCount(0)
		self._infoAList.clearContents()
		self._infoAList.setRowCount(0)
		self._eventDList.clearContents()
		self._eventDList.setRowCount(0)
		self._eventList.clearContents()
		self._eventList.setRowCount(0)
		LmConf.loadMacAddrTable()
		self.loadDeviceList()


	### Click on device infos button
	def deviceInfoButtonClick(self):
		aCurrentSelection = self._deviceList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._deviceList.item(aCurrentSelection, DevCol.Key).text()
			aLine = self.findDeviceLine(self._infoDList, aKey)
			self._infoDList.selectRow(aLine)
		self.switchToDeviceInfosTab()
	

	### Click on device events button
	def deviceEventsButtonClick(self):
		aCurrentSelection = self._deviceList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._deviceList.item(aCurrentSelection, DevCol.Key).text()
			aLine = self.findDeviceLine(self._eventDList, aKey)
			self._eventDList.selectRow(aLine)
		self.switchToDeviceEventsTab()


	### Click on IPv6 button
	def ipv6ButtonClick(self):
		self.startTask(lx('Getting IPv6 Information...'))

		# Get IPv6 status
		aIPv6Enabled = None
		try:
			d = self._session.request('NMC.IPv6:get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('data')
		if d is not None:
			aIPv6Enabled = d.get('Enable')
		if aIPv6Enabled is None:
			self.endTask()
			self.displayError('NMC.IPv6:get service error')
			return

		# Get IPv6 address and prefix
		aIPv6Addr = None
		aIPv6Prefix = None
		try:
			d = self._session.request('NMC:getWANStatus')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			s = d.get('status')
			if (s is None) or (not s):
				d = None
			else:
				d = d.get('data')
		if d is not None:
			aIPv6Addr = d.get('IPv6Address')
			aIPv6Prefix = d.get('IPv6DelegatedPrefix')
		if (aIPv6Addr is None) or (aIPv6Prefix is None):
			self.endTask()
			self.displayError('NMC:getWANStatus service error')
			return

		self.loadDeviceIpNameMap()

		self.endTask()

		aIPv6Dialog = IPv6Dialog(aIPv6Enabled, aIPv6Addr, aIPv6Prefix, self)
		aIPv6Dialog.loadDeviceList(self._liveboxDevices)
		aIPv6Dialog.exec()


	### Click on DNS button
	def dnsButtonClick(self):
		self.startTask(lx('Getting DNS Information...'))
		self.loadDeviceIpNameMap()
		self.endTask()

		aDnsDialog = DnsDialog(self)
		aDnsDialog.loadDeviceList(self._liveboxDevices)
		aDnsDialog.exec()


	### Load device list
	def loadDeviceList(self):
		self.startTask(lx('Loading device list...'))

		self._deviceList.setSortingEnabled(False)
		self._infoDList.setSortingEnabled(False)
		self._eventDList.setSortingEnabled(False)
		self._eventList.setSortingEnabled(False)

		# Init
		self._interfaceMap = []
		self._deviceMap = []
		self._deviceIpNameMap = {}
		self._deviceIpNameMapDirty = True

		# Get device infos from Livebox & build IP -> name map
		try:
			self._liveboxDevices = self._session.request('Devices:get', { 'expression': 'physical and !self and !voice' }, iTimeout = 10)
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self._liveboxDevices = None
		if self._liveboxDevices is not None:
			self._liveboxDevices = self._liveboxDevices.get('status')
		if self._liveboxDevices is None:
			self.displayError('Error getting device list.')
		else:
			self.buildDeviceIpNameMap()
			self._deviceIpNameMapDirty = False

		# Get topology infos from Livebox & build link & device maps
		try:
			self._liveboxTopology = self._session.request('TopologyDiagnostics:buildTopology', { 'SendXmlFile': 'false' }, iTimeout = 20)
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self._liveboxTopology = None
		if self._liveboxTopology is not None:
			self._liveboxTopology = self._liveboxTopology.get('status')
		if self._liveboxTopology is None:
			self.displayError('Error getting device topology.')
		else:
			self.buildLinkMaps()

		# Load devices in list, trying to identify Wifi repeaters on the fly
		i = 0
		if self._liveboxDevices is not None:
			for d in self._liveboxDevices:
				if self.displayableDevice(d):
					self.identifyRepeater(d)
					self.addDeviceLine(i, d)
					self.updateDeviceLine(i, d)
					i += 1

		self._deviceList.sortItems(DevCol.Active, QtCore.Qt.SortOrder.DescendingOrder)

		self._eventDList.insertRow(i)
		self._eventDList.setItem(i, DSelCol.Key, QtWidgets.QTableWidgetItem('#NONE#'))
		self._eventDList.setItem(i, DSelCol.Name, QtWidgets.QTableWidgetItem(lx('<None>')))

		self._deviceList.setCurrentCell(-1, -1)
		self._infoDList.setCurrentCell(-1, -1)
		self._eventDList.setCurrentCell(-1, -1)

		self.initDeviceContext()	# Init selected device context for DeviceInfo tab

		self._deviceList.setSortingEnabled(True)
		self._infoDList.setSortingEnabled(True)
		self._eventDList.setSortingEnabled(True)
		self._eventList.setSortingEnabled(True)

		self.endTask()


	### Check if device is displayable
	def displayableDevice(self, iDevice):
		# If Filter Devices option is on, do not display active devices without Layer2Intf
		if LmConf.FilterDevices:
			aActiveStatus = iDevice.get('Active', False)
			if aActiveStatus:
				aIntf = iDevice.get('Layer2Interface', '')
				if len(aIntf) == 0:
					return False

		return True


	### Add device line
	def addDeviceLine(self, iLine, iDevice):
		aKey = iDevice.get('Key', '')
		self.addDeviceLineKey(self._deviceList, iLine, aKey)
		self.addDeviceLineKey(self._infoDList, iLine, aKey)
		self.addDeviceLineKey(self._eventDList, iLine, aKey)

		aMacAddr = iDevice.get('PhysAddress', '')
		self.formatNameWidget(self._deviceList, iLine, aKey, DevCol.Name)
		self.formatMacWidget(self._deviceList, iLine, aMacAddr, DevCol.MAC)
		self.formatNameWidget(self._infoDList, iLine, aKey, DSelCol.Name)
		self.formatMacWidget(self._infoDList, iLine, aMacAddr, DSelCol.MAC)
		self.formatNameWidget(self._eventDList, iLine, aKey, DSelCol.Name)
		self.formatMacWidget(self._eventDList, iLine, aMacAddr, DSelCol.MAC)


	### Add a line with a device key
	@staticmethod
	def addDeviceLineKey(iList, iLine, iKey):
		iList.insertRow(iLine)
		iList.setItem(iLine, DevCol.Key, QtWidgets.QTableWidgetItem(iKey))


	### Update device line
	def updateDeviceLine(self, iLine, iDevice):
		aDeviceType = iDevice.get('DeviceType', '')
		aDeviceTypeIcon = self.formatDeviceTypeTableWidget(aDeviceType)
		self._deviceList.setItem(iLine, DevCol.Type, aDeviceTypeIcon)

		aLBName = QtWidgets.QTableWidgetItem(iDevice.get('Name', ''))
		self._deviceList.setItem(iLine, DevCol.LBName, aLBName)

		aIPStruct = LmTools.DetermineIP(iDevice)
		if aIPStruct is None:
			aIPv4 = ''
			aIPv4Reacheable = ''
			aIPv4Reserved = False
		else:
			aIPv4 = aIPStruct.get('Address', '')
			aIPv4Reacheable = aIPStruct.get('Status', '')
			aIPv4Reserved = aIPStruct.get('Reserved', False)
		aIP = self.formatIPv4TableWidget(aIPv4, aIPv4Reacheable, aIPv4Reserved)
		self._deviceList.setItem(iLine, DevCol.IP, aIP)

		aLinkIntf = self.findDeviceLink(iDevice.get('Key', ''))
		if aLinkIntf is None:
			aLinkName = lx('Unknown')
			aLinkType = ''
		else:
			aLinkName = aLinkIntf['Name']
			aLinkType = aLinkIntf['Type']
		aLink = QtWidgets.QTableWidgetItem(aLinkName)
		self._deviceList.setItem(iLine, DevCol.Link, aLink)

		aActiveStatus = iDevice.get('Active', False)
		aActiveIcon = self.formatActiveTableWidget(aActiveStatus)
		self._deviceList.setItem(iLine, DevCol.Active, aActiveIcon)

		if aActiveStatus and (aLinkType == 'wif'):
			aWifiSignal = iDevice.get('SignalNoiseRatio')
			if aWifiSignal is not None:
				aWifiIcon = LmTools.NumericSortItem()
				if aWifiSignal >= 40:
					aWifiIcon.setIcon(QtGui.QIcon(LmIcon.WifiSignal5Pixmap))
				elif aWifiSignal >= 32:
					aWifiIcon.setIcon(QtGui.QIcon(LmIcon.WifiSignal4Pixmap))
				elif aWifiSignal >= 25:
					aWifiIcon.setIcon(QtGui.QIcon(LmIcon.WifiSignal3Pixmap))
				elif aWifiSignal >= 15:
					aWifiIcon.setIcon(QtGui.QIcon(LmIcon.WifiSignal2Pixmap))
				elif aWifiSignal >= 10:
					aWifiIcon.setIcon(QtGui.QIcon(LmIcon.WifiSignal1Pixmap))
				elif aWifiSignal == 0:		# Case when system doesn't know, like for Guest interface
					aWifiIcon.setIcon(QtGui.QIcon(LmIcon.WifiSignal5Pixmap))
				else:
					aWifiIcon.setIcon(QtGui.QIcon(LmIcon.WifiSignal0Pixmap))
				aWifiIcon.setData(QtCore.Qt.ItemDataRole.UserRole, aWifiSignal)
				self._deviceList.setItem(iLine, DevCol.Wifi, aWifiIcon)


	### Update device name in all lists & tabs
	def updateDeviceName(self, iDeviceKey):
		aLine = self.findDeviceLine(self._deviceList, iDeviceKey)
		if aLine >= 0:
			self.formatNameWidget(self._deviceList, aLine, iDeviceKey, DevCol.Name)

		aLine = self.findDeviceLine(self._infoDList, iDeviceKey)
		if aLine >= 0:
			self.formatNameWidget(self._infoDList, aLine, iDeviceKey, DSelCol.Name)

		aLine = self.findDeviceLine(self._eventDList, iDeviceKey)
		if aLine >= 0:
			self.formatNameWidget(self._eventDList, aLine, iDeviceKey, DSelCol.Name)

		aLine = self.findDeviceLine(self._dhcpDList, iDeviceKey)
		if aLine >= 0:
			self.formatNameWidget(self._dhcpDList, aLine, iDeviceKey, DhcpCol.Name)

		self.graphUpdateDeviceName(iDeviceKey)
		self.repeaterUpdateDeviceName(iDeviceKey)


	### Format device type cell
	@staticmethod
	def formatDeviceTypeTableWidget(iDeviceType):
		aDeviceTypeIcon = LmTools.NumericSortItem()

		i = 0
		for d in LmConfig.DEVICE_TYPES:
			if iDeviceType == d['Key']:
				aDeviceTypeIcon.setIcon(QtGui.QIcon(LmConf.getDeviceIcon(d)))
				break
			i += 1

		aDeviceTypeIcon.setData(QtCore.Qt.ItemDataRole.UserRole, i)

		return aDeviceTypeIcon


	### Format Name cell
	@staticmethod
	def formatNameWidget(iList, iLine, iMacAddr, iNameCol):
		try:
			aName = QtWidgets.QTableWidgetItem(LmConf.MacAddrTable[iMacAddr])
		except:
			aName = QtWidgets.QTableWidgetItem(lx('UNKNOWN'))
			aName.setBackground(QtCore.Qt.GlobalColor.red)
		iList.setItem(iLine, iNameCol, aName)
		

	### Format MAC address cell
	@staticmethod
	def formatMacWidget(iList, iLine, iMacAddr, iMacCol):
		aMAC = QtWidgets.QTableWidgetItem(iMacAddr)
		aMAC.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		iList.setItem(iLine, iMacCol, aMAC)


	### Format Active status cell
	@staticmethod
	def formatActiveTableWidget(iActiveStatus):
		aActiveIconItem = LmTools.NumericSortItem()
		if iActiveStatus:
			aActiveIconItem.setIcon(QtGui.QIcon(LmIcon.TickPixmap))
			aActiveIconItem.setData(QtCore.Qt.ItemDataRole.UserRole, 1)
		else:
			aActiveIconItem.setIcon(QtGui.QIcon(LmIcon.CrossPixmap))
			aActiveIconItem.setData(QtCore.Qt.ItemDataRole.UserRole, 0)
		return aActiveIconItem


	### Format IPv4 cell
	@staticmethod
	def formatIPv4TableWidget(iIPv4, iReacheableStatus, iReserved):
		aIP = LmTools.NumericSortItem(iIPv4)
		if len(iIPv4):
			aIP.setData(QtCore.Qt.ItemDataRole.UserRole, int(IPv4Address(iIPv4)))
		else:
			aIP.setData(QtCore.Qt.ItemDataRole.UserRole, 0)
		if iReacheableStatus != 'reachable':
			aIP.setForeground(QtCore.Qt.GlobalColor.red)
		if iReserved:
			aIP.setFont(LmTools.BOLD_FONT)
		return aIP


	### Find device line from device key
	@staticmethod
	def findDeviceLine(iList, iDeviceKey):
		if len(iDeviceKey):
			i = 0
			n = iList.rowCount()
			while (i < n):
				if iList.item(i, DevCol.Key).text() == iDeviceKey:
					return i
				i += 1
		return -1


	### Get list of devices MAC, Livebox name, IPv4 and Active from currently displayed device list
	def getDeviceList(self):
		aList = []
		i = 0
		n = self._deviceList.rowCount()
		while (i < n):
			aDevice = {}
			aDevice['MAC'] = self._deviceList.item(i, DevCol.MAC).text()
			aDevice['LBName'] = self._deviceList.item(i, DevCol.LBName).text()
			aDevice['IP'] = self._deviceList.item(i, DevCol.IP).text()
			aDevice['Active'] = self._deviceList.item(i, DevCol.Active).data(QtCore.Qt.ItemDataRole.UserRole) == 1
			aList.append(aDevice)
			i += 1
		return aList


	### Load device IPv4 & IPv6 -> MAC/LBName/Active/IPVers map if need to be refreshed
	def loadDeviceIpNameMap(self):
		if self._deviceIpNameMapDirty:
			self.startTask(lx('Loading devices information...'))

			d = None
			try:
				d = self._session.request('Devices:get', { 'expression': 'physical and !self and !voice' }, iTimeout = 10)
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				d = None
			if d is not None:
				d = d.get('status')
			if d is None:
				self.endTask()
				self.displayError('Error getting device list.')
				return
			self._liveboxDevices = d

			self.buildDeviceIpNameMap()
			self._deviceIpNameMapDirty = False

			self.endTask()


	# Build device IPv4 & IPv6 -> MAC/LBName/Active/IPVers map from currently loaded device list
	def buildDeviceIpNameMap(self):
		# Init
		self._deviceIpNameMap = {}

		for d in self._liveboxDevices:
			if self.displayableDevice(d):
				# Get device infos to map for all its IP entries
				aIPv4DeviceInfo = {}
				aIPv4DeviceInfo['MAC'] = d.get('PhysAddress', '')
				aIPv4DeviceInfo['LBName'] = d.get('Name', '')
				aIPv4DeviceInfo['Active'] = d.get('Active', False)
				aIPv4DeviceInfo['IPVers'] = 'IPv4'

				# Map IPv4 address to device infos
				aIPv4Struct = LmTools.DetermineIP(d)
				if aIPv4Struct is not None:
					aIPv4 = aIPv4Struct.get('Address', '')

					# Add IPv4 entry
					if len(aIPv4):
						self._deviceIpNameMap[aIPv4] = aIPv4DeviceInfo

				# Map IPv6 address(es) to device infos
				aIPv6Struct = d.get('IPv6Address')
				aIPv6DeviceInfo = aIPv4DeviceInfo.copy()
				aIPv6DeviceInfo['IPVers'] = 'IPv6'
				if aIPv6Struct is not None:
					for a in aIPv6Struct:
						aScope = a.get('Scope', 'link')
						if aScope != 'link':
							aIPv6 = a.get('Address', '')
							if len(aIPv6):
								self._deviceIpNameMap[aIPv6] = aIPv6DeviceInfo


	### Get device name from IPv4 or IPv6
	# Depends on DeviceIpNameMap correct load
	# Returns local name in priority then LB name, then default to IP
	def getDeviceNameFromIp(self, iIP):
		if len(iIP):
			aDeviceInfo = self._deviceIpNameMap.get(iIP)
			if aDeviceInfo is None:
				return iIP
			else:
				try:
					return LmConf.MacAddrTable[aDeviceInfo['MAC']]
				except:
					return aDeviceInfo['LBName']
		return ''


	### Build link map
	def buildLinkMaps(self):
		aRootNode = self._liveboxTopology[0]
		aDeviceKey = aRootNode.get('Key', '')
		self.buildLinksMapNode(aRootNode.get('Children', []), aDeviceKey, 'Livebox', '', '')
#DBG	self.displayInfos('Interface map', str(self._interfaceMap))
#DBG	self.displayInfos('Device map', str(self._deviceMap))


	### Handle a topology node to build links map
	def buildLinksMapNode(self, iNode, iDeviceKey, iDeviceName, iInterfaceKey, iInterfaceName):
		for d in iNode:
			aTags = d.get('Tags', '').split()

			# Init
			aDeviceKey = iDeviceKey
			aDeviceName = iDeviceName
			aInterfaceKey = iInterfaceKey
			aInterfaceName = iInterfaceName

			# Handle interface end points
			if 'interface' in aTags:
				aInterfaceKey = d.get('Key', '')
				aInterfaceType = d.get('InterfaceType', '')
				if aInterfaceType == 'Ethernet':
					aInterfaceType = 'eth'
					aInterfaceName = d.get('NetDevName', '')
					if len(aInterfaceName) == 0:
						aInterfaceName = d.get('Name', '')
					if iDeviceName == 'Livebox':
						aNameMap = LmConfig.INTF_NAME_MAP['Livebox']
					else:
						aNameMap = LmConfig.INTF_NAME_MAP['Repeater']
					aMappedName = aNameMap.get(aInterfaceName)
					if aMappedName is not None:
						aInterfaceName = aMappedName
				else:
					aInterfaceType = 'wif'
					if iDeviceName == 'Livebox':
						i = next((i for i in LmConfig.NET_INTF if i['Key'] == aInterfaceKey), None)
						if i is None:
							aInterfaceName = d.get('Name', aInterfaceKey)
						else:
							aInterfaceName = i['Name']
					else:
						aWifiBand = d.get('OperatingFrequencyBand', '')
						if len(aWifiBand):
							aInterfaceName = 'Wifi ' + aWifiBand
						else:
							aInterfaceName = d.get('Name', aInterfaceKey)
				aMapEntry = {}
				aMapEntry['Key'] = aInterfaceKey
				aMapEntry['Type'] = aInterfaceType
				aMapEntry['DevKey'] = aDeviceKey
				aMapEntry['DevName'] = aDeviceName
				aMapEntry['IntName'] = aInterfaceName
				aMapEntry['Name'] = aDeviceName + ' ' + lx(aInterfaceName)
				self._interfaceMap.append(aMapEntry)

			# Handle devices
			if 'physical' in aTags:
				aDeviceKey = d.get('Key', '')
				aDeviceName = d.get('Name', '')
				aMapEntry = {}
				aMapEntry['Key'] = aDeviceKey
				aMapEntry['InterfaceKey'] = aInterfaceKey
				self._deviceMap.append(aMapEntry)

			self.buildLinksMapNode(d.get('Children', []), aDeviceKey, aDeviceName, aInterfaceKey, aInterfaceName)


	### Find device link name from device key
	def findDeviceLink(self, iDeviceKey):
		aInterfaceKey = ''

		# First find device interface
		for d in self._deviceMap:
			if d['Key'] == iDeviceKey:
				aInterfaceKey = d['InterfaceKey']

				# Then find interface name
				for i in self._interfaceMap:
					if i['Key'] == aInterfaceKey:
						return i

		return None


	### Update device link interface key
	def updateDeviceLinkInterface(self, iDeviceKey, iInterfaceKey):
		# Find device interface
		for d in self._deviceMap:
			if d['Key'] == iDeviceKey:
				d['InterfaceKey'] = iInterfaceKey
				return


	### Update interface map when a device name changes, and refresh the UI
	def updateInterfaceMap(self, iDeviceKey, iDeviceName):
		# Loop on interface map and update each matching entries
		for i in self._interfaceMap:
			if i['DevKey'] == iDeviceKey:
				i['DevName'] = iDeviceName
				aLinkName = iDeviceName + ' ' + i['IntName']
				i['Name'] = aLinkName

				# Then update each device connected to that interface
				for d in self._deviceMap:
					if d['InterfaceKey'] == i['Key']:
						aLine = self.findDeviceLine(self._deviceList, d['Key'])
						if aLine >= 0:
							self._deviceList.setItem(aLine, DevCol.Link, QtWidgets.QTableWidgetItem(aLinkName))


	### Indicate visually the reception of an event for a device
	def updateEventIndicator(self, iDeviceKey):
		# First remove last event indicator
		aListLine = self.findDeviceLine(self._deviceList, self._lastEventDeviceKey)
		if aListLine >= 0:
			self._deviceList.setItem(aListLine, DevCol.Event, None)

		# Set indicator on new device
		aListLine = self.findDeviceLine(self._deviceList, iDeviceKey)
		if aListLine >= 0:
			aEventIndicator = LmTools.NumericSortItem()
			aEventIndicator.setIcon(QtGui.QIcon(LmIcon.NotifPixmap))
			aEventIndicator.setData(QtCore.Qt.ItemDataRole.UserRole, 1)
			self._deviceList.setItem(aListLine, DevCol.Event, aEventIndicator)

		self._lastEventDeviceKey = iDeviceKey


	### Process a new statistics event
	def processStatisticsEvent(self, iDeviceKey, iEvent):
		# Get event data
		aDownBytes = iEvent.get('RxBytes', 0)
		aUpBytes = iEvent.get('TxBytes', 0)
		aDownErrors = iEvent.get('RxErrors', 0)
		aUpErrors = iEvent.get('TxErrors', 0)
		aDownRateBytes = 0
		aUpRateBytes = 0
		aDownDeltaErrors = iEvent.get('DeltaRxErrors', 0)
		aUpDeltaErrors = iEvent.get('DeltaTxErrors', 0)
		aTimestamp = LmTools.LiveboxTimestamp(iEvent.get('Timestamp', ''))

		# Try to find a previously received statistic record
		aPrevStats = self._statsMap.get(iDeviceKey)
		if aPrevStats is not None:
			aPrevDownBytes = aPrevStats['Rx']
			aPrevUpBytes = aPrevStats['Tx']
			aPrevTimestamp = aPrevStats['Time']
			aElapsed = int((aTimestamp - aPrevTimestamp).total_seconds())
			if aElapsed > 0:
				aDownRateBytes = int((aDownBytes - aPrevDownBytes) / aElapsed)
				aUpRateBytes = int((aUpBytes - aPrevUpBytes) / aElapsed)

			# Update potential running graph
			self.graphUpdateDeviceEvent(iDeviceKey, int(aTimestamp.timestamp()),
										aDownBytes - aPrevDownBytes,
										aUpBytes  - aPrevUpBytes)

		# Remember current stats
		aStats = {}
		aStats['Rx'] = aDownBytes
		aStats['Tx'] = aUpBytes
		aStats['Time'] = aTimestamp
		self._statsMap[iDeviceKey] = aStats

		# Update UI
		aListLine = self.findDeviceLine(self._deviceList, iDeviceKey)
		if aListLine >= 0:
			# Prevent device line to change due to sorting
			self._deviceList.setSortingEnabled(False)

			aDown = LmTools.NumericSortItem(LmTools.FmtBytes(aDownBytes))
			aDown.setData(QtCore.Qt.ItemDataRole.UserRole, aDownBytes)
			aDown.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVertical_Mask)
			if aDownErrors:
				aDown.setForeground(QtCore.Qt.GlobalColor.red)
			self._deviceList.setItem(aListLine, DevCol.Down, aDown)

			aUp = LmTools.NumericSortItem(LmTools.FmtBytes(aUpBytes))
			aUp.setData(QtCore.Qt.ItemDataRole.UserRole, aUpBytes)
			aUp.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVertical_Mask)
			if aUpErrors:
				aUp.setForeground(QtCore.Qt.GlobalColor.red)
			self._deviceList.setItem(aListLine, DevCol.Up, aUp)

			if aDownRateBytes:
				aDownRate = LmTools.NumericSortItem(LmTools.FmtBytes(aDownRateBytes) + '/s')
				aDownRate.setData(QtCore.Qt.ItemDataRole.UserRole, aDownRateBytes)
				if aDownDeltaErrors:
					aDownRate.setForeground(QtCore.Qt.GlobalColor.red)
				aDownRate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVertical_Mask)
			else:
				aDownRate = QtWidgets.QTableWidgetItem('')
			self._deviceList.setItem(aListLine, DevCol.DownRate, aDownRate)

			if aUpRateBytes:
				aUpRate = LmTools.NumericSortItem(LmTools.FmtBytes(aUpRateBytes) + '/s')
				aUpRate.setData(QtCore.Qt.ItemDataRole.UserRole, aUpRateBytes)
				if aUpDeltaErrors:
					aUpRate.setForeground(QtCore.Qt.GlobalColor.red)
				aUpRate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVertical_Mask)
			else:
				aUpRate = QtWidgets.QTableWidgetItem('')
			self._deviceList.setItem(aListLine, DevCol.UpRate, aUpRate)

			# Restore sorting
			self._deviceList.setSortingEnabled(True)


	### Process a new changed event
	def processChangedEvent(self, iDeviceKey, iHandler, iEvent):
		# Check if device is in the UI list
		aListLine = self.findDeviceLine(self._deviceList, iDeviceKey)
		if aListLine >= 0:
			# Prevent device line to change due to sorting
			self._deviceList.setSortingEnabled(False)

			# Check if active status changed
			aActiveStatus = iEvent.get('Active')
			if aActiveStatus is not None:
				self._deviceIpNameMapDirty = True
				aIsActive = aActiveStatus != '0'
				aActiveIcon = self.formatActiveTableWidget(aIsActive)
				self._deviceList.setItem(aListLine, DevCol.Active, aActiveIcon)
				self.repeaterActiveEvent(iDeviceKey, aIsActive)

			# Check if IP reachable status changed
			aIPv4Reacheable = iEvent.get('Status')
			if (aIPv4Reacheable is not None) and ('IPv4Address' in iHandler):
				aCurrIP = self._deviceList.item(aListLine, DevCol.IP)
				aReserved = aCurrIP.font().bold()
				aIP = self.formatIPv4TableWidget(aCurrIP.text(), aIPv4Reacheable, aReserved)
				self._deviceList.setItem(aListLine, DevCol.IP, aIP)

			# Check if IPv4 changed
			aIPv4 = iEvent.get('IPAddress')
			if (aIPv4 is not None) and (LmTools.IsIPv4(aIPv4)):
				self._deviceIpNameMapDirty = True
				aIP = self._deviceList.item(aListLine, DevCol.IP)
				aIP.setText(aIPv4)
				aIP.setData(QtCore.Qt.ItemDataRole.UserRole, int(IPv4Address(aIPv4)))
				self.repeaterIPAddressEvent(iDeviceKey, aIPv4)

			# Check if name changed
			aName = iEvent.get('Name')
			if aName is not None:
				self._deviceIpNameMapDirty = True
				self._deviceList.setItem(aListLine, DevCol.LBName, QtWidgets.QTableWidgetItem(aName))
				self.updateInterfaceMap(iDeviceKey, aName)

			# Check if MAC address assigned
			aMacAddr = iEvent.get('PhysAddress')
			if aMacAddr is not None:
				self._deviceIpNameMapDirty = True

				self.formatNameWidget(self._deviceList, aListLine, aMacAddr, DevCol.Name)
				self.formatMacWidget(self._deviceList, aListLine, aMacAddr, DevCol.MAC)

				aLine = self.findDeviceLine(self._infoDList, iDeviceKey)
				if aLine >= 0:
					self.formatNameWidget(self._infoDList, aLine, aMacAddr, DSelCol.Name)
					self.formatMacWidget(self._infoDList, aLine, aMacAddr, DSelCol.MAC)

				aLine = self.findDeviceLine(self._eventDList, iDeviceKey)
				if aLine >= 0:
					self.formatNameWidget(self._eventDList, aLine, aMacAddr, DSelCol.Name)
					self.formatMacWidget(self._eventDList, aLine, aMacAddr, DSelCol.MAC)

			# Restore sorting
			self._deviceList.setSortingEnabled(True)


	### Process a new device_name_changed event
	def processDeviceNameChangedEvent(self, iDeviceKey, iEvent):
		self._deviceIpNameMapDirty = True

		# Check if device is in the UI list
		aListLine = self.findDeviceLine(self._deviceList, iDeviceKey)
		if aListLine >= 0:
			aName = iEvent.get('NewName')
			if aName is not None:
				self._deviceList.setItem(aListLine, DevCol.LBName, QtWidgets.QTableWidgetItem(aName))
				self.updateInterfaceMap(iDeviceKey, aName)


	### Process a new device_updated, eth_device_updated or wifi_device_updated event
	def processDeviceUpdatedEvent(self, iDeviceKey, iEvent):
		# Check if device is in the UI list
		aListLine = self.findDeviceLine(self._deviceList, iDeviceKey)
		if aListLine >= 0:
			self._deviceIpNameMapDirty = True

			# Prevent device line to change due to sorting
			self._deviceList.setSortingEnabled(False)

			# Update the link interface
			aLink = iEvent.get('ULinks', [])
			if len(aLink):
				self.updateDeviceLinkInterface(iDeviceKey, aLink[0])

			# Update the device line
			self.updateDeviceLine(aListLine, iEvent)

			# Update potential repeater infos
			self.repeaterDeviceUpdatedEvent(iDeviceKey, iEvent)

			# Restore sorting
			self._deviceList.setSortingEnabled(True)


	### Process a new ip_address_added event
	def processIPAddressAddedEvent(self, iDeviceKey, iEvent):
		self._deviceIpNameMapDirty = True

		# Check if device is in the UI list
		aListLine = self.findDeviceLine(self._deviceList, iDeviceKey)
		if aListLine >= 0:
			if iEvent.get('Family', '') == 'ipv4':
				# Get IP known by the program
				aKnownIPItem = self._deviceList.item(aListLine, DevCol.IP)
				if aKnownIPItem is not None:	# MT safe, can happen with // processing
					aKnownIP = aKnownIPItem.text()
				else:
					aKnownIP = ''

				# Get current device IP
				try:
					aReply = self._session.request('Devices.Device.' + iDeviceKey + ':getFirstParameter', { 'parameter': 'IPAddress' })
				except BaseException as e:
					LmTools.Error('Error: {}'.format(e))
					aReply = None
				if aReply is None:
					aCurrIP = aKnownIP
				else:
					aCurrIP = aReply.get('status', '')

				# Proceed only if there is a change
				if aKnownIP != aCurrIP:
					# If current IP is the one of the event, take it, overwise wait for next device update event
					aIPv4 = iEvent.get('Address', '')
					if (LmTools.IsIPv4(aIPv4)) and (aCurrIP == aIPv4):
						aIPv4Reacheable = iEvent.get('Status', '')
						aIPv4Reserved = iEvent.get('Reserved', False)
						aIP = self.formatIPv4TableWidget(aIPv4, aIPv4Reacheable, aIPv4Reserved)
						self._deviceList.setItem(aListLine, DevCol.IP, aIP)
						self.repeaterIPAddressEvent(iDeviceKey, aIPv4)


	### Process a new device_added, eth_device_added or wifi_device_added event
	def processDeviceAddedEvent(self, iDeviceKey, iEvent):
		# Check if device is not already in the UI list
		aListLine = self.findDeviceLine(self._deviceList, iDeviceKey)
		if aListLine >= 0:
			return

		aTags = iEvent.get('Tags', '').split()
		if ('physical' in aTags) and (not 'self' in aTags) and (not 'voice' in aTags) and self.displayableDevice(iEvent):
			self._deviceIpNameMapDirty = True

			# Prevent device lines to change due to sorting
			self._deviceList.setSortingEnabled(False)
			self._infoDList.setSortingEnabled(False)
			self._eventDList.setSortingEnabled(False)

			# Update device map
			aMapEntry = {}
			aMapEntry['Key'] = iDeviceKey
			aMapEntry['InterfaceKey'] = None
			self._deviceMap.append(aMapEntry)

			# Update UI
			self.addDeviceLine(0, iEvent)
			self.updateDeviceLine(0, iEvent)

			# Add as repeater if it is one
			self.addPotentialRepeater(iEvent)

			# Restore sorting
			self._deviceList.setSortingEnabled(True)
			self._infoDList.setSortingEnabled(True)
			self._eventDList.setSortingEnabled(True)


	### Process a new device_deleted, eth_device_deleted or wifi_device_deleted event
	def processDeviceDeletedEvent(self, iDeviceKey):
		self._deviceIpNameMapDirty = True

		# Remove from all UI lists
		aListLine = self.findDeviceLine(self._deviceList, iDeviceKey)
		if aListLine >= 0:
			self._deviceList.removeRow(aListLine)
		aListLine = self.findDeviceLine(self._infoDList, iDeviceKey)
		if aListLine >= 0:
			self._infoDList.removeRow(aListLine)
		aListLine = self.findDeviceLine(self._eventDList, iDeviceKey)
		if aListLine >= 0:
			self._eventDList.removeRow(aListLine)

		# Remove repeater if it is one
		self.removePotentialRepeater(iDeviceKey)

		# Cleanup device map
		for d in self._deviceMap:
			if d['Key'] == iDeviceKey:
				self._deviceMap.remove(d)

		# Cleanup event buffer
		try:
			del self._eventBuffer[iDeviceKey]
		except:
			pass


	### Process a new Livebox Wifi stats
	def processLiveboxWifiStats(self, iStats):
		# Get stats data
		aKey = iStats['Key']
		aDeviceKey = iStats['DeviceKey']
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
		aPrevStats = self._liveboxWifiStatsMap.get(aKey)
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
		self._liveboxWifiStatsMap[aKey] = iStats

		# Update UI
		aListLine = self.findDeviceLine(self._deviceList, aDeviceKey)
		if (aListLine >= 0) and (aPrevStats is not None):
			# Prevent device line to change due to sorting
			self._deviceList.setSortingEnabled(False)

			if aDownRateBytes:
				aDownRate = LmTools.NumericSortItem(LmTools.FmtBytes(aDownRateBytes) + '/s')
				aDownRate.setData(QtCore.Qt.ItemDataRole.UserRole, aDownRateBytes)
				if aDownDeltaErrors:
					aDownRate.setForeground(QtCore.Qt.GlobalColor.red)
				else:
					aDownRate.setForeground(QtCore.Qt.GlobalColor.blue)
				aDownRate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVertical_Mask)
			else:
				aDownRate = QtWidgets.QTableWidgetItem('')
			self._deviceList.setItem(aListLine, DevCol.DownRate, aDownRate)

			if aUpRateBytes:
				aUpRate = LmTools.NumericSortItem(LmTools.FmtBytes(aUpRateBytes) + '/s')
				aUpRate.setData(QtCore.Qt.ItemDataRole.UserRole, aUpRateBytes)
				if aUpDeltaErrors:
					aUpRate.setForeground(QtCore.Qt.GlobalColor.red)
				else:
					aUpRate.setForeground(QtCore.Qt.GlobalColor.blue)
				aUpRate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVertical_Mask)
			else:
				aUpRate = QtWidgets.QTableWidgetItem('')
			self._deviceList.setItem(aListLine, DevCol.UpRate, aUpRate)

			# Restore sorting
			self._deviceList.setSortingEnabled(True)



# ############# Display IPv6 dialog #############
# List columns
class IPv6Col(IntEnum):
	Key = 0		# Must be the same as DevCol.Key
	Name = 1
	LBName = 2
	MAC = 3
	Active = 4
	IPv4 = 5
	IPv6 = 6
	Count = 7
IPV6_ICON_COLUMNS = [IPv6Col.Active]


class IPv6Dialog(QtWidgets.QDialog):
	def __init__(self, iEnabled, iAddr, iPrefix, iParent = None):
		super(IPv6Dialog, self).__init__(iParent)
		self.resize(850, 110 + LmConfig.DialogHeight(12))

		# IPv6 info box
		aIPv6EnabledLabel = QtWidgets.QLabel(lix('IPv6 enabled:'), objectName = 'ipv6EnabledLabel')
		aIPv6Enabled = QtWidgets.QLabel(objectName = 'ipv6Enabled')
		if iEnabled:
			aIPv6Enabled.setPixmap(LmIcon.TickPixmap)
		else:
			aIPv6Enabled.setPixmap(LmIcon.CrossPixmap)

		aAddrLabel = QtWidgets.QLabel(lix('IPv6 address:'), objectName = 'addrLabel')
		aAddr = QtWidgets.QLineEdit(iAddr, objectName = 'addr')
		aAddr.setReadOnly(True)

		aPrefixLabel = QtWidgets.QLabel(lix('IPv6 prefix:'), objectName = 'prefixLabel')
		aPrefix = QtWidgets.QLineEdit(iPrefix, objectName = 'prefix')
		aPrefix.setReadOnly(True)

		aIPv6InfoGrid = QtWidgets.QGridLayout()
		aIPv6InfoGrid.setSpacing(10)
		aIPv6InfoGrid.addWidget(aIPv6EnabledLabel, 0, 0)
		aIPv6InfoGrid.addWidget(aIPv6Enabled, 0, 1)
		aIPv6InfoGrid.addWidget(aAddrLabel, 1, 0)
		aIPv6InfoGrid.addWidget(aAddr, 1, 1)
		aIPv6InfoGrid.addWidget(aPrefixLabel, 1, 2)
		aIPv6InfoGrid.addWidget(aPrefix, 1, 3)

		# Device table
		self._deviceTable = QtWidgets.QTableWidget(objectName = 'ipv6Table')
		self._deviceTable.setColumnCount(IPv6Col.Count)
		self._deviceTable.setHorizontalHeaderLabels(('Key', lix('Name'),
															lix('Livebox Name'),
															lix('MAC'),
															lix('A'),
															lix('IPv4'),
															lix('IPv6')))
		self._deviceTable.setColumnHidden(IPv6Col.Key, True)
		aHeader = self._deviceTable.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aHeader.setSectionResizeMode(IPv6Col.Name, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aHeader.setSectionResizeMode(IPv6Col.LBName, QtWidgets.QHeaderView.ResizeMode.Stretch)
		self._deviceTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		aModel = aHeader.model()
		aModel.setHeaderData(IPv6Col.Name, QtCore.Qt.Orientation.Horizontal, 'ipv6_Name', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(IPv6Col.LBName, QtCore.Qt.Orientation.Horizontal, 'ipv6_LBName', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(IPv6Col.MAC, QtCore.Qt.Orientation.Horizontal, 'ipv6_MAC', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(IPv6Col.Active, QtCore.Qt.Orientation.Horizontal, 'ipv6_Active', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(IPv6Col.IPv4, QtCore.Qt.Orientation.Horizontal, 'ipv6_IPv4', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(IPv6Col.IPv6, QtCore.Qt.Orientation.Horizontal, 'ipv6_IPv6', QtCore.Qt.ItemDataRole.UserRole)
		self._deviceTable.setColumnWidth(IPv6Col.Name, 300)
		self._deviceTable.setColumnWidth(IPv6Col.LBName, 300)
		self._deviceTable.setColumnWidth(IPv6Col.MAC, 120)
		self._deviceTable.setColumnWidth(IPv6Col.Active, 10)
		self._deviceTable.setColumnWidth(IPv6Col.IPv4, 105)
		self._deviceTable.setColumnWidth(IPv6Col.IPv6, 250)
		self._deviceTable.verticalHeader().hide()
		self._deviceTable.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
		self._deviceTable.setSortingEnabled(True)
		self._deviceTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		self._deviceTable.setItemDelegate(LmTools.CenteredIconsDelegate(self, IPV6_ICON_COLUMNS))
		LmConfig.SetTableStyle(self._deviceTable)

		# Button bar
		aHBox = QtWidgets.QHBoxLayout()
		aOKButton = QtWidgets.QPushButton(lix('OK'), objectName = 'ok')
		aOKButton.clicked.connect(self.accept)
		aOKButton.setDefault(True)
		aHBox.addWidget(aOKButton, 1, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addLayout(aIPv6InfoGrid, 0)
		aVBox.addWidget(self._deviceTable, 1)
		aVBox.addLayout(aHBox, 1)

		LmConfig.SetToolTips(self, 'ipv6')

		self.setWindowTitle(lix('IPv6 Devices'))
		self.setModal(True)
		self.show()


	def loadDeviceList(self, iDevices):
		if (iDevices is not None):
			self._deviceTable.setSortingEnabled(False)
			i = 0
			p = self.parent()
			for d in iDevices:
				if p.displayableDevice(d):
					# First collect global IPv6 addresses
					aIPv6Struct = d.get('IPv6Address')
					aIPv6Addr = []
					if aIPv6Struct is not None:
						for a in aIPv6Struct:
							aScope = a.get('Scope', 'link')
							if aScope != 'link':
								aAddr = a.get('Address')
								if aAddr is not None:
									aIPv6Addr.append(aAddr)
					if not len(aIPv6Addr):
						continue

					# Display data
					aKey = d.get('Key', '')
					p.addDeviceLineKey(self._deviceTable, i, aKey)

					p.formatNameWidget(self._deviceTable, i, aKey, IPv6Col.Name)

					aLBName = QtWidgets.QTableWidgetItem(d.get('Name', ''))
					self._deviceTable.setItem(i, IPv6Col.LBName, aLBName)

					p.formatMacWidget(self._deviceTable, i, d.get('PhysAddress', ''), IPv6Col.MAC)

					aActiveStatus = d.get('Active', False)
					aActiveIcon = p.formatActiveTableWidget(aActiveStatus)
					self._deviceTable.setItem(i, IPv6Col.Active, aActiveIcon)

					aIPStruct = LmTools.DetermineIP(d)
					if aIPStruct is None:
						aIPv4 = ''
						aIPv4Reacheable = ''
						aIPv4Reserved = False
					else:
						aIPv4 = aIPStruct.get('Address', '')
						aIPv4Reacheable = aIPStruct.get('Status', '')
						aIPv4Reserved = aIPStruct.get('Reserved', False)
					aIP = p.formatIPv4TableWidget(aIPv4, aIPv4Reacheable, aIPv4Reserved)
					self._deviceTable.setItem(i, IPv6Col.IPv4, aIP)

					aIPv6Str = ''
					aResize = False
					for a in aIPv6Addr:
						if len(aIPv6Str):
							aIPv6Str += '\n'
							aResize = True
						aIPv6Str += a
					self._deviceTable.setItem(i, IPv6Col.IPv6, QtWidgets.QTableWidgetItem(aIPv6Str))
					if aResize:
						self._deviceTable.resizeRowToContents(i)

					i += 1

			self._deviceTable.sortItems(IPv6Col.Active, QtCore.Qt.SortOrder.DescendingOrder)
			self._deviceTable.setSortingEnabled(True)



# ############# Display DNS dialog #############
# List columns
class DnsCol(IntEnum):
	Key = 0		# Must be the same as DevCol.Key
	Name = 1
	LBName = 2
	MAC = 3
	Active = 4
	IP = 5
	DNS = 6
	Count = 7
DNS_ICON_COLUMNS = [DnsCol.Active]


class DnsDialog(QtWidgets.QDialog):
	def __init__(self, iParent = None):
		super(DnsDialog, self).__init__(iParent)
		self.resize(850, 56 + LmConfig.DialogHeight(12))

		# Device table
		self._deviceTable = QtWidgets.QTableWidget(objectName = 'dnsTable')
		self._deviceTable.setColumnCount(DnsCol.Count)
		self._deviceTable.setHorizontalHeaderLabels(('Key', ldx('Name'),
															ldx('Livebox Name'),
															ldx('MAC'),
															ldx('A'),
															ldx('IP'),
															ldx('DNS')))
		self._deviceTable.setColumnHidden(DnsCol.Key, True)
		aHeader = self._deviceTable.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aHeader.setSectionResizeMode(DnsCol.Name, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aHeader.setSectionResizeMode(DnsCol.LBName, QtWidgets.QHeaderView.ResizeMode.Stretch)
		self._deviceTable.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		aModel = aHeader.model()
		aModel.setHeaderData(DnsCol.Name, QtCore.Qt.Orientation.Horizontal, 'dns_Name', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DnsCol.LBName, QtCore.Qt.Orientation.Horizontal, 'dns_LBName', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DnsCol.MAC, QtCore.Qt.Orientation.Horizontal, 'dns_MAC', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DnsCol.Active, QtCore.Qt.Orientation.Horizontal, 'dns_Active', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DnsCol.IP, QtCore.Qt.Orientation.Horizontal, 'dns_IP', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(DnsCol.DNS, QtCore.Qt.Orientation.Horizontal, 'dns_DNS', QtCore.Qt.ItemDataRole.UserRole)
		self._deviceTable.setColumnWidth(DnsCol.Name, 300)
		self._deviceTable.setColumnWidth(DnsCol.LBName, 300)
		self._deviceTable.setColumnWidth(DnsCol.MAC, 120)
		self._deviceTable.setColumnWidth(DnsCol.Active, 10)
		self._deviceTable.setColumnWidth(DnsCol.IP, 105)
		self._deviceTable.setColumnWidth(DnsCol.DNS, 250)
		self._deviceTable.verticalHeader().hide()
		self._deviceTable.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
		self._deviceTable.setSortingEnabled(True)
		self._deviceTable.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		self._deviceTable.setItemDelegate(LmTools.CenteredIconsDelegate(self, DNS_ICON_COLUMNS))
		LmConfig.SetTableStyle(self._deviceTable)

		# Button bar
		aHBox = QtWidgets.QHBoxLayout()
		aOKButton = QtWidgets.QPushButton(ldx('OK'), objectName = 'ok')
		aOKButton.clicked.connect(self.accept)
		aOKButton.setDefault(True)
		aHBox.addWidget(aOKButton, 1, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addWidget(self._deviceTable, 1)
		aVBox.addLayout(aHBox, 1)

		LmConfig.SetToolTips(self, 'dns')

		self.setWindowTitle(ldx('Devices DNS'))
		self.setModal(True)
		self.show()


	def loadDeviceList(self, iDevices):
		if (iDevices is not None):
			self._deviceTable.setSortingEnabled(False)
			i = 0
			p = self.parent()
			for d in iDevices:
				if p.displayableDevice(d):
					# First collect DNS name
					aDnsName = None
					aNameList = d.get('Names', [])
					if len(aNameList):
						for aName in aNameList:
							if aName.get('Source', '') == 'dns':
								aDnsName = aName.get('Name', '')
								break
					if aDnsName is None:
						continue

					# Display data
					aKey = d.get('Key', '')
					p.addDeviceLineKey(self._deviceTable, i, aKey)

					p.formatNameWidget(self._deviceTable, i, aKey, DnsCol.Name)

					aLBName = QtWidgets.QTableWidgetItem(d.get('Name', ''))
					self._deviceTable.setItem(i, DnsCol.LBName, aLBName)

					p.formatMacWidget(self._deviceTable, i, d.get('PhysAddress', ''), DnsCol.MAC)

					aActiveStatus = d.get('Active', False)
					aActiveIcon = p.formatActiveTableWidget(aActiveStatus)
					self._deviceTable.setItem(i, DnsCol.Active, aActiveIcon)

					aIPStruct = LmTools.DetermineIP(d)
					if aIPStruct is None:
						aIPv4 = ''
						aIPv4Reacheable = ''
						aIPv4Reserved = False
					else:
						aIPv4 = aIPStruct.get('Address', '')
						aIPv4Reacheable = aIPStruct.get('Status', '')
						aIPv4Reserved = aIPStruct.get('Reserved', False)
					aIP = p.formatIPv4TableWidget(aIPv4, aIPv4Reacheable, aIPv4Reserved)
					self._deviceTable.setItem(i, DnsCol.IP, aIP)

					self._deviceTable.setItem(i, DnsCol.DNS, QtWidgets.QTableWidgetItem(aDnsName))

					i += 1

			self._deviceTable.sortItems(DnsCol.Active, QtCore.Qt.SortOrder.DescendingOrder)
			self._deviceTable.setSortingEnabled(True)



# ############# Livebox Wifi device stats collector thread #############
class LiveboxWifiStatsThread(QtCore.QObject):
	_wifiStatsReceived = QtCore.pyqtSignal(dict)
	_resume = QtCore.pyqtSignal()

	def __init__(self, iSession):
		super(LiveboxWifiStatsThread, self).__init__()
		self._session = iSession
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
		for s in LmConfig.NET_INTF:
			if s['Type'] != 'wif':
				continue
			try:
				aResult = self._session.request('NeMo.Intf.' + s['Key'] + ':getStationStats')
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				aResult = None
			if aResult is not None:
				aStats = aResult.get('status')
				if type(aStats).__name__ == 'list':
					for aStat in aStats:
						e = {}
						e['DeviceKey'] = aStat.get('MACAddress', '')
						e['Key'] = e['DeviceKey'] + '_' + s['Key']
						e['Timestamp'] = datetime.datetime.now()
						e['RxBytes'] = aStat.get('TxBytes', 0)
						e['TxBytes'] = aStat.get('RxBytes', 0)
						e['RxErrors'] = aStat.get('TxErrors', 0)
						e['TxErrors'] = aStat.get('RxErrors', 0)
						self._wifiStatsReceived.emit(e)

