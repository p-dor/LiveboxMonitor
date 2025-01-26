### Livebox Monitor Livebox info tab module ###

import datetime

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.tabs.LmActionsTab import WifiKey, WifiStatus
from LiveboxMonitor.lang.LmLanguages import GetInfoLabel as lx, GetInfoMessage as mx


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'liveboxInfoTab'

# List columns
class InfoCol(IntEnum):
	Attribute = 0
	Value = 1
	Count = 2

class StatsCol(IntEnum):
	Key = 0
	Name = 1
	Down = 2
	Up = 3
	DownRate = 4
	UpRate = 5
	Count = 6


# ################################ LmInfo class ################################
class LmInfo:

	### Create Livebox info tab
	def createLiveboxInfoTab(self):
		self._liveboxInfoTab = QtWidgets.QWidget(objectName = TAB_NAME)

		# Statistics list
		self._statsList = QtWidgets.QTableWidget(objectName = 'statsList')
		self._statsList.setColumnCount(StatsCol.Count)
		self._statsList.setHorizontalHeaderLabels(('Key', lx('Name'),
														  lx('Rx'),
														  lx('Tx'),
														  lx('RxRate'),
														  lx('TxRate')))
		self._statsList.setColumnHidden(StatsCol.Key, True)
		aHeader = self._statsList.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aHeader.setSectionResizeMode(StatsCol.Down, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aHeader.setSectionResizeMode(StatsCol.Up, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aHeader.setSectionResizeMode(StatsCol.DownRate, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aHeader.setSectionResizeMode(StatsCol.UpRate, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aModel = aHeader.model()
		aModel.setHeaderData(StatsCol.Name, QtCore.Qt.Orientation.Horizontal, 'stats_Name', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(StatsCol.Down, QtCore.Qt.Orientation.Horizontal, 'stats_Rx', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(StatsCol.Up, QtCore.Qt.Orientation.Horizontal, 'stats_Tx', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(StatsCol.DownRate, QtCore.Qt.Orientation.Horizontal, 'stats_RxRate', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(StatsCol.UpRate, QtCore.Qt.Orientation.Horizontal, 'stats_TxRate', QtCore.Qt.ItemDataRole.UserRole)
		self._statsList.setColumnWidth(StatsCol.Name, 100)
		self._statsList.setColumnWidth(StatsCol.Down, 65)
		self._statsList.setColumnWidth(StatsCol.Up, 65)
		self._statsList.setColumnWidth(StatsCol.DownRate, 65)
		self._statsList.setColumnWidth(StatsCol.UpRate, 65)
		self._statsList.verticalHeader().hide()
		self._statsList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
		self._statsList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		self._statsList.setMinimumWidth(450)
		LmConfig.SetTableStyle(self._statsList)

		i = 0
		for s in LmConfig.NET_INTF:
			self._statsList.insertRow(i)
			self._statsList.setItem(i, StatsCol.Key, QtWidgets.QTableWidgetItem(s['Key']))
			self._statsList.setItem(i, StatsCol.Name, QtWidgets.QTableWidgetItem(lx(s['Name'])))
			i += 1
		aStatsListSize = LmConfig.TableHeight(i)
		self._statsList.setMinimumHeight(aStatsListSize)
		self._statsList.setMaximumHeight(aStatsListSize)

		# Attribute list
		self._liveboxAList = QtWidgets.QTableWidget(objectName = 'liveboxAList')
		self._liveboxAList.setColumnCount(InfoCol.Count)
		self._liveboxAList.setHorizontalHeaderLabels((lx('Attribute'), lx('Value')))
		aHeader = self._liveboxAList.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aHeader.setSectionResizeMode(InfoCol.Value, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aModel = aHeader.model()
		aModel.setHeaderData(InfoCol.Attribute, QtCore.Qt.Orientation.Horizontal, 'alist_Attribute', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(InfoCol.Value, QtCore.Qt.Orientation.Horizontal, 'alist_Value', QtCore.Qt.ItemDataRole.UserRole)
		self._liveboxAList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._liveboxAList.setColumnWidth(InfoCol.Attribute, 200)
		self._liveboxAList.setColumnWidth(InfoCol.Value, 600)
		self._liveboxAList.verticalHeader().hide()
		self._liveboxAList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
		self._liveboxAList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		LmConfig.SetTableStyle(self._liveboxAList)

		# Lists layout
		aListBox = QtWidgets.QHBoxLayout()
		aListBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aListBox.setSpacing(10)
		aListBox.addWidget(self._statsList, 0, QtCore.Qt.AlignmentFlag.AlignTop)
		aListBox.addWidget(self._liveboxAList, 1)

		# Button bar
		aButtonsBox = QtWidgets.QHBoxLayout()
		aButtonsBox.setSpacing(10)

		aLiveboxInfoButton = QtWidgets.QPushButton(lx('Livebox Infos'), objectName = 'liveboxInfo')
		aLiveboxInfoButton.clicked.connect(self.liveboxInfoButtonClick)
		aButtonsBox.addWidget(aLiveboxInfoButton)

		aInternetInfoButton = QtWidgets.QPushButton(lx('Internet Infos'), objectName = 'internetInfo')
		aInternetInfoButton.clicked.connect(self.internetInfoButtonClick)
		aButtonsBox.addWidget(aInternetInfoButton)

		aWifiInfoButton = QtWidgets.QPushButton(lx('Wifi Infos'), objectName = 'wifiInfo')
		aWifiInfoButton.clicked.connect(self.wifiInfoButtonClick)
		aButtonsBox.addWidget(aWifiInfoButton)

		aLanInfoButton = QtWidgets.QPushButton(lx('LAN Infos'), objectName = 'lanInfo')
		aLanInfoButton.clicked.connect(self.lanInfoButtonClick)
		aButtonsBox.addWidget(aLanInfoButton)

		aOntInfoButton = QtWidgets.QPushButton(lx('ONT Infos'), objectName = 'ontInfo')
		aOntInfoButton.clicked.connect(self.ontInfoButtonClick)
		if self._fiberLink:
			aButtonsBox.addWidget(aOntInfoButton)

		aVoiPInfoButton = QtWidgets.QPushButton(lx('VoIP Infos'), objectName = 'voipInfo')
		aVoiPInfoButton.clicked.connect(self.voipInfoButtonClick)
		aButtonsBox.addWidget(aVoiPInfoButton)

		aIptvInfoButton = QtWidgets.QPushButton(lx('IPTV Infos'), objectName = 'iptvInfo')
		aIptvInfoButton.clicked.connect(self.iptvInfoButtonClick)
		aButtonsBox.addWidget(aIptvInfoButton)

		aUsbInfoButton = QtWidgets.QPushButton(lx('USB Infos'), objectName = 'usbInfo')
		aUsbInfoButton.clicked.connect(self.usbInfoButtonClick)
		aButtonsBox.addWidget(aUsbInfoButton)

		aSeparator = QtWidgets.QFrame()
		aSeparator.setFrameShape(QtWidgets.QFrame.Shape.VLine)
		aSeparator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
		aButtonsBox.addWidget(aSeparator)

		aExportInfoButton = QtWidgets.QPushButton(lx('Export...'), objectName = 'exportInfo')
		aExportInfoButton.clicked.connect(self.exportInfoButtonClick)
		aButtonsBox.addWidget(aExportInfoButton)
		self._exportFile = None

		# Layout
		aVBox = QtWidgets.QVBoxLayout()
		aVBox.setSpacing(10)
		aVBox.addLayout(aListBox, 0)
		aVBox.addLayout(aButtonsBox, 1)
		self._liveboxInfoTab.setLayout(aVBox)

		# Init context
		self._homeLanIntfStatsMap = {}
		self._liveboxStatsMapHomeLan = {}

		LmConfig.SetToolTips(self._liveboxInfoTab, 'info')
		self._tabWidget.addTab(self._liveboxInfoTab, lx('Livebox Stats/Infos'))


	### Init the Livebox stats collector thread
	def initStatsLoop(self):
		self._liveboxStatsMap = {}
		self._liveboxStatsThread = None
		self._liveboxStatsLoop = None


	### Start the Livebox stats collector thread
	def startStatsLoop(self):
		self._liveboxStatsThread = QtCore.QThread()
		self._liveboxStatsLoop = LiveboxStatsThread(self._session)
		self._liveboxStatsLoop.moveToThread(self._liveboxStatsThread)
		self._liveboxStatsThread.started.connect(self._liveboxStatsLoop.run)
		self._liveboxStatsLoop._statsReceived.connect(self.processLiveboxStats)
		self._liveboxStatsLoop._resume.connect(self._liveboxStatsLoop.resume)
		self._liveboxStatsThread.start()


	### Suspend the Livebox stats collector thread
	def suspendStatsLoop(self):
		if self._liveboxStatsThread is not None:
			self._liveboxStatsLoop.stop()


	### Resume the Livebox stats collector thread
	def resumeStatsLoop(self):
		if self._liveboxStatsThread is None:
			self.startStatsLoop()
		else:
			self._liveboxStatsLoop._resume.emit()


	### Stop the Livebox stats collector thread
	def stopStatsLoop(self):
		if self._liveboxStatsThread is not None:
			self._liveboxStatsThread.quit()
			self._liveboxStatsThread.wait()
			self._liveboxStatsThread = None
			self._liveboxStatsLoop = None


	### Process a HomeLan interface stats event
	def processIntfStatisticsEvent(self, iIntf, iAttributes):
		for s in LmConfig.NET_INTF:
			if s['Key'] == iIntf:
				e = {}
				e['Key'] = iIntf
				e['Source'] = 'hls'		# HomeLanStats
				e['Timestamp'] = datetime.datetime.now()

				# Only one value among the two is present per event
				aBytesSent = iAttributes.get('BytesSent')
				aBytesReceived = iAttributes.get('BytesReceived')

				if aBytesSent is None:
					if s['SwapStats']:
						e['RxBytes'] = None
					else:
						e['TxBytes'] = None
				else:
					if s['SwapStats']:
						e['RxBytes'] = int(aBytesSent)
					else:
						e['TxBytes'] = int(aBytesSent)

				if aBytesReceived is None:
					if s['SwapStats']:
						e['TxBytes'] = None
					else:
						e['RxBytes'] = None
				else:
					if s['SwapStats']:
						e['TxBytes'] = int(aBytesReceived)
					else:
						e['RxBytes'] = int(aBytesReceived)

				e['RxErrors'] = 0
				e['TxErrors'] = 0

				# Update UI
				self.processLiveboxStats(e)

				# Update potential running graph
				aBytesReceived = e['RxBytes']
				aDeltaReceived = None
				aBytesSent = e['TxBytes']
				aDeltaSent = None

				# Try to find a previously received statistic record
				aPrevStats = self._homeLanIntfStatsMap.get(iIntf)
				if aPrevStats is not None:
					aPrevDownBytes = aPrevStats['RxBytes']
					if aBytesReceived is not None:
						if (aPrevDownBytes is not None) and (aBytesReceived > aPrevDownBytes):
							aDeltaReceived = aBytesReceived - aPrevDownBytes
					else:
						aBytesReceived = aPrevDownBytes

					aPrevUpBytes = aPrevStats['TxBytes']
					if aBytesSent is not None:
						if (aPrevUpBytes is not None) and (aBytesSent > aPrevUpBytes):
							aDeltaSent = aBytesSent - aPrevUpBytes
					else:
						aBytesSent = aPrevUpBytes

				# Remember current stats
				s = {}
				s['RxBytes'] = aBytesReceived
				s['TxBytes'] = aBytesSent
				self._homeLanIntfStatsMap[iIntf] = s

				self.graphUpdateInterfaceEvent(iIntf, int(e['Timestamp'].timestamp()), aDeltaReceived, aDeltaSent)
				break


	### Find stats line from stat key
	def findStatsLine(self, iStatsKey):
		if len(iStatsKey):
			i = 0
			n = self._statsList.rowCount()
			while (i < n):
				aItem = self._statsList.item(i, StatsCol.Key)
				if aItem.text() == iStatsKey:
					return i
				i += 1
		return -1


	### Process a new Livebox stats
	# Stats can come from two sources, indicated in the 'Source' value: NetDevStats ('nds') or HomeLan ('hls').
	# nds stats are realtime but recycling at 4Gb max / hls stats are raised every 30s but recycling at much higher numbers
	# nds stats come will all values / hls stats come with either down or up bytes values, other is None, and errors are at zero
	# Strategy is to display realime rates from nds events and to update the counters from the hls events
	def processLiveboxStats(self, iStats):
		# Get stats data
		aKey = iStats['Key']
		aSource = iStats['Source']
		aTimestamp = iStats['Timestamp']
		aDownBytes = iStats.get('RxBytes')
		aUpBytes = iStats.get('TxBytes')
		aDownErrors = iStats['RxErrors']
		aUpErrors = iStats['TxErrors']
		aDownRateBytes = 0
		aUpRateBytes = 0
		aDownDeltaErrors = 0
		aUpDeltaErrors = 0

		# If event source is HomeLan update the counters only and remember it
		if aSource == 'hls':
			self._liveboxStatsMapHomeLan[aKey] = True

		# If event source is NetDevStats update all and remember last nds stats
		elif aSource == 'nds':
			# Try to find a previously received statistic record
			aPrevStats = self._liveboxStatsMap.get(aKey)
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
			self._liveboxStatsMap[aKey] = iStats

			# Don't erase previously received HomeLan counters
			if self._liveboxStatsMapHomeLan.get(aKey, False):
				aDownBytes = None
				aUpBytes = None

		# Update UI
		aListLine = self.findStatsLine(aKey)
		if aListLine >= 0:
			if aDownBytes is not None:
				aDown = QtWidgets.QTableWidgetItem(LmTools.FmtBytes(aDownBytes))
				aDown.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVertical_Mask)
				if aDownErrors:
					aDown.setForeground(QtCore.Qt.GlobalColor.red)
				self._statsList.setItem(aListLine, StatsCol.Down, aDown)

			if aUpBytes is not None:
				aUp = QtWidgets.QTableWidgetItem(LmTools.FmtBytes(aUpBytes))
				aUp.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVertical_Mask)
				if aUpErrors:
					aUp.setForeground(QtCore.Qt.GlobalColor.red)
				self._statsList.setItem(aListLine, StatsCol.Up, aUp)

			if aSource == 'nds':
				if aDownRateBytes:
					aDownRate = QtWidgets.QTableWidgetItem(LmTools.FmtBytes(aDownRateBytes) + '/s')
					if aDownDeltaErrors:
						aDownRate.setForeground(QtCore.Qt.GlobalColor.red)
					aDownRate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVertical_Mask)
				else:
					aDownRate = QtWidgets.QTableWidgetItem('')
				self._statsList.setItem(aListLine, StatsCol.DownRate, aDownRate)

				if aUpRateBytes:
					aUpRate = QtWidgets.QTableWidgetItem(LmTools.FmtBytes(aUpRateBytes) + '/s')
					if aUpDeltaErrors:
						aUpRate.setForeground(QtCore.Qt.GlobalColor.red)
					aUpRate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVertical_Mask)
				else:
					aUpRate = QtWidgets.QTableWidgetItem('')
				self._statsList.setItem(aListLine, StatsCol.UpRate, aUpRate)


	### Add a title line in an info attribute/value list
	def addTitleLine(self, iList, iLine, iTitle):
		if (iTitle is not None) and (len(iTitle)):
			if self._exportFile is not None:
				if iLine > 0:
					iLine += 1
					self._exportFile.write('\n')
				self._exportFile.write('### ' + iTitle + '\n')
			else:
				iList.insertRow(iLine)
				if iLine > 0:
					iLine += 1
					iList.insertRow(iLine)
				aAttribute = QtWidgets.QTableWidgetItem('')
				aAttribute.setBackground(QtCore.Qt.GlobalColor.cyan)
				aTitle = QtWidgets.QTableWidgetItem(iTitle)
				aTitle.setFont(LmTools.BOLD_FONT)
				aTitle.setBackground(QtCore.Qt.GlobalColor.cyan)
				iList.setItem(iLine, InfoCol.Attribute, aAttribute)
				iList.setItem(iLine, InfoCol.Value, aTitle)
			return iLine + 1
		else:
			return iLine


	### Add a line in an info attribute/value list
	def addInfoLine(self, iList, iLine, iAttribute, iValue, iQualifier = LmTools.ValQual.Default):
		if (iValue is not None) and (len(iValue)):
			if self._exportFile is not None:
				self._exportFile.write(iAttribute + ' = ' + iValue + '\n')
			else:
				iList.insertRow(iLine)
				aAttribute = QtWidgets.QTableWidgetItem(iAttribute)
				aAttribute.setFont(LmTools.BOLD_FONT)
				iList.setItem(iLine, InfoCol.Attribute, aAttribute)
				if iQualifier != LmTools.ValQual.Default:
					aValue = QtWidgets.QTableWidgetItem(iValue)
					if iQualifier == LmTools.ValQual.Good:
						aValue.setForeground(QtGui.QBrush(QtGui.QColor(0, 190, 0)))
					elif iQualifier == LmTools.ValQual.Warn:
						aValue.setForeground(QtGui.QBrush(QtGui.QColor(255, 191, 0)))
					elif iQualifier == LmTools.ValQual.Error:
						aValue.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
					iList.setItem(iLine, InfoCol.Value, aValue)
				else:
					iList.setItem(iLine, InfoCol.Value, QtWidgets.QTableWidgetItem(iValue))
			return iLine + 1
		else:
			return iLine


	### Click on Livebox infos button
	def liveboxInfoButtonClick(self):
		self.startTask(lx('Getting Livebox information...'))

		self._liveboxAList.clearContents()
		self._liveboxAList.setRowCount(0)

		self.loadLiveboxInfo()

		self.endTask()


	### Click on Internet infos button
	def internetInfoButtonClick(self):
		self.startTask(lx('Getting Internet information...'))

		self._liveboxAList.clearContents()
		self._liveboxAList.setRowCount(0)

		self.loadInternetInfo()

		self.endTask()


	### Click on Wifi infos button
	def wifiInfoButtonClick(self):
		self.startTask(lx('Getting Wifi information...'))

		self._liveboxAList.clearContents()
		self._liveboxAList.setRowCount(0)

		self.loadWifiInfo()

		self.endTask()


	### Click on LAN infos button
	def lanInfoButtonClick(self):
		self.startTask(lx('Getting LAN information...'))

		self._liveboxAList.clearContents()
		self._liveboxAList.setRowCount(0)

		self.loadLanInfo()

		self.endTask()


	### Click on ONT infos button
	def ontInfoButtonClick(self):
		self.startTask(lx('Getting ONT information...'))

		self._liveboxAList.clearContents()
		self._liveboxAList.setRowCount(0)

		self.loadOntInfo()

		self.endTask()


	### Click on VoIP infos button
	def voipInfoButtonClick(self):
		self.startTask(lx('Getting VoIP information...'))

		self._liveboxAList.clearContents()
		self._liveboxAList.setRowCount(0)

		self.loadVoipInfo()

		self.endTask()


	### Click on IPTV infos button
	def iptvInfoButtonClick(self):
		self.startTask(lx('Getting IPTV information...'))

		self._liveboxAList.clearContents()
		self._liveboxAList.setRowCount(0)

		self.loadIptvInfo()

		self.endTask()


	### Click on USB infos button
	def usbInfoButtonClick(self):
		self.startTask(lx('Getting USB information...'))

		self._liveboxAList.clearContents()
		self._liveboxAList.setRowCount(0)

		self.loadUsbInfo()

		self.endTask()


	### Click on Export infos button
	def exportInfoButtonClick(self):
		aFileName = QtWidgets.QFileDialog.getSaveFileName(self, lx('Save File'), lx('Livebox Infos') + '.txt', '*.txt')
		aFileName = aFileName[0]
		if aFileName == '':
			return

		try:
			self._exportFile = open(aFileName, 'w')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError(mx('Cannot create the file.', 'createFileErr'))
			return

		self.startTask(lx('Exporting all information...'))

		i = 0
		i = self.loadLiveboxInfo(i)
		i = self.loadInternetInfo(i)
		i = self.loadWifiInfo(i)
		i = self.loadLanInfo(i)
		if self._liveboxModel >= 5:
			i = self.loadOntInfo(i)
		i = self.loadVoipInfo(i)
		i = self.loadIptvInfo(i)
		i = self.loadUsbInfo(i)

		self.endTask()

		try:
			self._exportFile.close()
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			self.displayError(mx('Cannot save the file.', 'saveFileErr'))

		self._exportFile = None


	### Load Livebox infos
	def loadLiveboxInfo(self, iIndex = 0):
		aLiveboxMAC = ''
		i = self.addTitleLine(self._liveboxAList, iIndex, lx('Livebox Information'))

		try:
			d = self._session.request('UPnP-IGD', 'get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('Livebox Infos'), 'UPnP-IGD:get query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('Provider'), d.get('WANAccessProvider'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Model Number'), d.get('ModelNumber'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Model Name'), d.get('ModelName'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Friendly Name'), d.get('FriendlyName'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Allowed Host Headers'), d.get('AllowedHostHeader'))

		aTotalReboot = None
		try:
			d = self._session.request('NMC.Reboot', 'get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('Livebox Infos'), 'NMC.Reboot:get query error', LmTools.ValQual.Error)
		else:
			aTotalReboot = d.get('BootCounter')

		try:
			d = self._session.request('DeviceInfo', 'get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('Livebox Infos'), 'DeviceInfo:get query error', LmTools.ValQual.Error)
		else:
			aLiveboxMAC = d.get('BaseMAC', '').upper()
			i = self.addInfoLine(self._liveboxAList, i, lx('Model'), d.get('ProductClass'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Status'), LmTools.FmtStrCapitalize(d.get('DeviceStatus')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Livebox Up Time'), LmTools.FmtTime(d.get('UpTime')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Manufacturer'), d.get('Manufacturer'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Manufacturer Model Name'), d.get('ModelName'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Description'), d.get('Description'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Serial Number'), d.get('SerialNumber'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Hardware Version'), d.get('HardwareVersion'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Software Version'), d.get('SoftwareVersion'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Rescue Version'), d.get('RescueVersion'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Modem Firmware Version'), d.get('ModemFirmwareVersion'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Orange Firmware Version'), d.get('AdditionalSoftwareVersion'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Spec Version'), d.get('SpecVersion'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Provisioning Code'), d.get('ProvisioningCode'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Country'), LmTools.FmtStrUpper(d.get('Country')))
			i = self.addInfoLine(self._liveboxAList, i, lx('MAC Address'), aLiveboxMAC)
			i = self.addInfoLine(self._liveboxAList, i, lx('External IP Address'), d.get('ExternalIPAddress'))
			if aTotalReboot is not None:
				i = self.addInfoLine(self._liveboxAList, i, lx('Total Number Of Reboots'), LmTools.FmtInt(aTotalReboot))
			i = self.addInfoLine(self._liveboxAList, i, lx('Number Of Reboots'), LmTools.FmtInt(d.get('NumberOfReboots')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Upgrade Occurred'), LmTools.FmtBool(d.get('UpgradeOccurred')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Reset Occurred'), LmTools.FmtBool(d.get('ResetOccurred')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Restore Occurred'), LmTools.FmtBool(d.get('RestoreOccurred')))

		if len(aLiveboxMAC):
			try:
				d = self._session.request('Devices.Device.' + aLiveboxMAC, 'get')
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				d = None
			if d is not None:
				d = d.get('status')
			if d is None:
				i = self.addInfoLine(self._liveboxAList, i, lx('Livebox Infos'), 'Devices.Device:get query error', LmTools.ValQual.Error)
			else:
				i = self.addInfoLine(self._liveboxAList, i, lx('Name'), d.get('Name'))
				i = self.addInfoLine(self._liveboxAList, i, lx('Active'), LmTools.FmtBool(d.get('Active')))
				i = self.addInfoLine(self._liveboxAList, i, lx('Last Boot'), LmTools.FmtLiveboxTimestamp(d.get('FirstSeen')))
				i = self.addInfoLine(self._liveboxAList, i, lx('Boot Loader Version'), d.get('BootLoaderVersion'))
				i = self.addInfoLine(self._liveboxAList, i, lx('Firewall Level'), d.get('FirewallLevel'))
				i = self.addInfoLine(self._liveboxAList, i, lx('Internet Active'), LmTools.FmtBool(d.get('Internet')))
				i = self.addInfoLine(self._liveboxAList, i, lx('IPTV Active'), LmTools.FmtBool(d.get('IPTV')))
				i = self.addInfoLine(self._liveboxAList, i, lx('Telephony Active'), LmTools.FmtBool(d.get('Telephony')))

		try:
			d = self._session.request('Time', 'getTime')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			s = d.get('status', False)
			d = d.get('data')
		if (not s) or (d is None):
			i = self.addInfoLine(self._liveboxAList, i, lx('Time'), 'Time:getTime query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('Time'), d.get('time'))

		try:
			d = self._session.request('DeviceInfo.MemoryStatus', 'get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('Memory'), 'DeviceInfo.MemoryStatus:get query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('Total Memory'), LmTools.FmtInt(d.get('Total')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Free Memory'), LmTools.FmtInt(d.get('Free')))

		return i


	### Load Internet infos
	def loadInternetInfo(self, iIndex = 0):
		aLiveboxMAC = ''
		i = self.addTitleLine(self._liveboxAList, iIndex, lx('Internet Information'))

		try:
			d = self._session.request('NMC', 'get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('Connection'), 'NMC:get query error', LmTools.ValQual.Error)
		else:
			aAccessType = d.get('WanMode')
			if aAccessType is not None:
				if self._fiberLink:
					i = self.addInfoLine(self._liveboxAList, i, lx('Access Type'), 'Fiber (' + aAccessType + ')')
				else:
					i = self.addInfoLine(self._liveboxAList, i, lx('Access Type'), 'ADSL (' + aAccessType + ')')
			
			i = self.addInfoLine(self._liveboxAList, i, lx('Username'), d.get('Username'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Factory Reset Scheduled'), LmTools.FmtBool(d.get('FactoryResetScheduled')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Connection Error'), LmTools.FmtBool(d.get('ConnectionError')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Offer Type'), d.get('OfferType'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Offer Name'), d.get('OfferName'))
			i = self.addInfoLine(self._liveboxAList, i, lx('IPTV Mode'), d.get('IPTVMode'))

		d = None
		try:
			q = self._session.request('NMC', 'getWANStatus')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			q = None
		if q is not None:
			d = q.get('status')
		if (d is None) or (not d):
			i = self.addInfoLine(self._liveboxAList, i, lx('Internet Infos'), 'NMC:getWANStatus query error', LmTools.ValQual.Error)
		if q is not None:
			d = q.get('data')
		else:
			d = None
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('Internet Infos'), 'NMC:getWANStatus data error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('WAN Status'), LmTools.FmtStrCapitalize(d.get('WanState')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Link Status'), LmTools.FmtStrCapitalize(d.get('LinkState')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Link Type'), LmTools.FmtStrUpper(d.get('LinkType')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Protocol'), LmTools.FmtStrUpper(d.get('Protocol')))
			i = self.addInfoLine(self._liveboxAList, i, lx('GPON State'), d.get('GponState'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Connection Status'), d.get('ConnectionState'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Last Connection Error'), d.get('LastConnectionError'))
			i = self.addInfoLine(self._liveboxAList, i, lx('IP Address'), d.get('IPAddress'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Remote Gateway'), d.get('RemoteGateway'))
			i = self.addInfoLine(self._liveboxAList, i, lx('DNS Servers'), d.get('DNSServers'))
			i = self.addInfoLine(self._liveboxAList, i, lx('IPv6 Address'), d.get('IPv6Address'))
			i = self.addInfoLine(self._liveboxAList, i, lx('IPv6 Prefix'), d.get('IPv6DelegatedPrefix'))

		try:
			d = self._session.request('DeviceInfo', 'get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('Internet Infos'), 'DeviceInfo:get query error', LmTools.ValQual.Error)
		else:
			aLiveboxMAC = d.get('BaseMAC', '').upper()

		if len(aLiveboxMAC):
			try:
				d = self._session.request('Devices.Device.' + aLiveboxMAC, 'get')
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				d = None
			if d is not None:
				d = d.get('status')
			if d is None:
				i = self.addInfoLine(self._liveboxAList, i, lx('Internet Infos'), 'Devices.Device:get query error', LmTools.ValQual.Error)
			else:
				i = self.addInfoLine(self._liveboxAList, i, lx('Last Connection'), LmTools.FmtLiveboxTimestamp(d.get('LastConnection')))
				i = self.addInfoLine(self._liveboxAList, i, lx('Firewall Level'), d.get('FirewallLevel'))
				aRate = d.get('DownstreamMaxBitRate')
				if aRate is not None:
					aRate *= 1048576
					i = self.addInfoLine(self._liveboxAList, i, lx('Max Down Bit Rate'), LmTools.FmtBytes(aRate))
				aRate = d.get('UpstreamMaxBitRate')
				if aRate is not None:
					aRate *= 1048576
					i = self.addInfoLine(self._liveboxAList, i, lx('Max Up Bit Rate'), LmTools.FmtBytes(aRate))

		try:
			d = self._session.request('NeMo.Intf.data', 'getMIBs', { 'mibs': 'dhcp' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			d = d.get('dhcp')
		if d is not None:
			d = d.get('dhcp_data')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('Connection'), 'NeMo.Intf.data:getMIBs query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('DHCP Status'), d.get('DHCPStatus'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Subnet Mask'), d.get('SubnetMask'))
			i = self.addInfoLine(self._liveboxAList, i, lx('IP Routers'), d.get('IPRouters'))
			i = self.addInfoLine(self._liveboxAList, i, lx('DHCP Server'), d.get('DHCPServer'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Renew'), LmTools.FmtBool(d.get('Renew')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Authentication'), LmTools.FmtBool(d.get('CheckAuthentication')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Authentication Information'), d.get('AuthenticationInformation'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Connection Up Time'), LmTools.FmtTime(d.get('Uptime')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Lease Time'), LmTools.FmtTime(d.get('LeaseTime')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Lease Time Remaining'), LmTools.FmtTime(d.get('LeaseTimeRemaining')))

		try:
			d = self._session.request('NeMo.Intf.data', 'getFirstParameter', { 'name': 'VLANID' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('VLAN ID'), 'NeMo.Intf.data:getFirstParameter query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('VLAN ID'), LmTools.FmtInt(d.get('status')))

		try:
			d = self._session.request('NeMo.Intf.data', 'getFirstParameter', { 'name': 'MTU' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('MTU'), 'NeMo.Intf.data:getFirstParameter query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('MTU'), LmTools.FmtInt(d.get('status')))

		return i


	### Load Wifi infos
	def loadWifiInfo(self, iIndex = 0):
		i = self.addTitleLine(self._liveboxAList, iIndex, lx('Wifi Information'))

		try:
			d = self._session.request('NMC.Wifi', 'get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('Wifi'), 'NMC.Wifi:get query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('Enabled'), LmTools.FmtBool(d.get('Enable')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Active'), LmTools.FmtBool(d.get('Status')))
			i = self.addInfoLine(self._liveboxAList, i, lx('BGN User Bandwidth'), d.get('BGNUserBandwidth'))

		try:
			d = self._session.request('Scheduler', 'getCompleteSchedules', { 'type': 'WLAN' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if (d is not None) and (d.get('status', False)):
			d = d.get('data')
		else:
			d = None
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('Scheduler Enabled'), 'Scheduler:getCompleteSchedules query error', LmTools.ValQual.Error)
		else:
			d = d.get('scheduleInfo', [])
			if len(d):
				aActive = d[0].get('enable', False)
			else:
				aActive = False
			i = self.addInfoLine(self._liveboxAList, i, lx('Scheduler Enabled'), LmTools.FmtBool(aActive))

		b = None
		w = None
		try:
			d = self._session.request('NeMo.Intf.lan', 'getMIBs', { 'mibs': 'base wlanradio' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			b = d.get('base')
			w = d.get('wlanradio')

		try:
			d = self._session.request('NeMo.Intf.lan', 'getMIBs', { 'mibs': 'wlanvap', 'flag': 'wlanvap !secondary' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			d = d.get('wlanvap')

		if (d is None) or (b is None) or (w is None):
			i = self.addInfoLine(self._liveboxAList, i, lx('Wifi'), 'NeMo.Intf.lan:getMIBs query error', LmTools.ValQual.Error)
			return i 

		for s in LmConfig.NET_INTF:
			if s['Type'] != 'wif':
				continue
			i = self.addTitleLine(self._liveboxAList, i, s['Name'])

			# Get Wifi interface key in wlanradio list
			aIntfKey = None
			aBase = b.get(s['Key'])
			if aBase is not None:
				i = self.addInfoLine(self._liveboxAList, i, lx('Enabled'), LmTools.FmtBool(aBase.get('Enable')))
				i = self.addInfoLine(self._liveboxAList, i, lx('Active'), LmTools.FmtBool(aBase.get('Status')))
				aLowLevelIntf = aBase.get('LLIntf')
				if aLowLevelIntf is not None:
					for aKey in aLowLevelIntf:
						aIntfKey = aKey
						break

			q = w.get(aIntfKey) if aIntfKey is not None else None
			r = d.get(s['Key'])
			if (q is None) or (r is None):
				continue

			i = self.addInfoLine(self._liveboxAList, i, lx('Radio Status'), q.get('RadioStatus'))
			i = self.addInfoLine(self._liveboxAList, i, lx('VAP Status'), r.get('VAPStatus'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Vendor Name'), LmTools.FmtStrUpper(q.get('VendorName')))
			i = self.addInfoLine(self._liveboxAList, i, lx('MAC Address'), LmTools.FmtStrUpper(r.get('MACAddress')))
			i = self.addInfoLine(self._liveboxAList, i, lx('SSID'), r.get('SSID'))
			i = self.addInfoLine(self._liveboxAList, i, lx('SSID Advertisement'), LmTools.FmtBool(r.get('SSIDAdvertisementEnabled')))

			t = r.get('Security')
			if t is not None:
				i = self.addInfoLine(self._liveboxAList, i, lx('Security Mode'), t.get('ModeEnabled'))
				i = self.addInfoLine(self._liveboxAList, i, lx('WEP Key'), t.get('WEPKey'))
				i = self.addInfoLine(self._liveboxAList, i, lx('PreShared Key'), t.get('PreSharedKey'))
				i = self.addInfoLine(self._liveboxAList, i, lx('Key Pass Phrase'), t.get('KeyPassPhrase'))

			t = r.get('WPS')
			if t is not None:
				i = self.addInfoLine(self._liveboxAList, i, lx('WPS Enabled'), LmTools.FmtBool(t.get('Enable')))
				i = self.addInfoLine(self._liveboxAList, i, lx('WPS Methods'), t.get('ConfigMethodsEnabled'))
				i = self.addInfoLine(self._liveboxAList, i, lx('WPS Self PIN'), t.get('SelfPIN'))
				i = self.addInfoLine(self._liveboxAList, i, lx('WPS Pairing In Progress'), LmTools.FmtBool(t.get('PairingInProgress')))

			t = r.get('MACFiltering')
			if t is not None:
				i = self.addInfoLine(self._liveboxAList, i, lx('MAC Filtering'), t.get('Mode'))

			i = self.addInfoLine(self._liveboxAList, i, lx('Max Bitrate'), LmTools.FmtInt(q.get('MaxBitRate')))
			i = self.addInfoLine(self._liveboxAList, i, lx('AP Mode'), LmTools.FmtBool(q.get('AP_Mode')))
			i = self.addInfoLine(self._liveboxAList, i, lx('STA Mode'), LmTools.FmtBool(q.get('STA_Mode')))
			i = self.addInfoLine(self._liveboxAList, i, lx('WDS Mode'), LmTools.FmtBool(q.get('WDS_Mode')))
			i = self.addInfoLine(self._liveboxAList, i, lx('WET Mode'), LmTools.FmtBool(q.get('WET_Mode')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Frequency Band'), q.get('OperatingFrequencyBand'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Channel Bandwidth'), q.get('CurrentOperatingChannelBandwidth'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Standard'), q.get('OperatingStandards'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Channel'), LmTools.FmtInt(q.get('Channel')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Auto Channel Supported'), LmTools.FmtBool(q.get('AutoChannelSupported')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Auto Channel Enabled'), LmTools.FmtBool(q.get('AutoChannelEnable')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Channel Change Reason'), q.get('ChannelChangeReason'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Max Associated Devices'), LmTools.FmtInt(q.get('MaxAssociatedDevices')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Active Associated Devices'), LmTools.FmtInt(q.get('ActiveAssociatedDevices')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Noise'), LmTools.FmtInt(q.get('Noise')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Antenna Defect'), LmTools.FmtBool(q.get('AntennaDefect')))

		try:
			d = self._session.request('NeMo.Intf.guest', 'getMIBs', { 'mibs': 'wlanvap' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			d = d.get('wlanvap')

		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('Wifi'), 'NeMo.Intf.guest:getMIBs query error', LmTools.ValQual.Error)
			return i

		for s in LmConfig.NET_INTF:
			if s['Type'] != 'wig':
				continue
			i = self.addTitleLine(self._liveboxAList, i, s['Name'])

			r = d.get(s['Key'])
			if r is None:
				continue

			i = self.addInfoLine(self._liveboxAList, i, lx('VAP Status'), r.get('VAPStatus'))
			i = self.addInfoLine(self._liveboxAList, i, lx('MAC Address'), LmTools.FmtStrUpper(r.get('MACAddress')))
			i = self.addInfoLine(self._liveboxAList, i, lx('SSID'), r.get('SSID'))
			i = self.addInfoLine(self._liveboxAList, i, lx('SSID Advertisement'), LmTools.FmtBool(r.get('SSIDAdvertisementEnabled')))

			t = r.get('Security')
			if t is not None:
				i = self.addInfoLine(self._liveboxAList, i, lx('Security Mode'), t.get('ModeEnabled'))
				i = self.addInfoLine(self._liveboxAList, i, lx('WEP Key'), t.get('WEPKey'))
				i = self.addInfoLine(self._liveboxAList, i, lx('PreShared Key'), t.get('PreSharedKey'))
				i = self.addInfoLine(self._liveboxAList, i, lx('Key Pass Phrase'), t.get('KeyPassPhrase'))

			t = r.get('WPS')
			if t is not None:
				i = self.addInfoLine(self._liveboxAList, i, lx('WPS Enabled'), LmTools.FmtBool(t.get('Enable')))
				i = self.addInfoLine(self._liveboxAList, i, lx('WPS Methods'), t.get('ConfigMethodsEnabled'))
				i = self.addInfoLine(self._liveboxAList, i, lx('WPS Self PIN'), t.get('SelfPIN'))
				i = self.addInfoLine(self._liveboxAList, i, lx('WPS Pairing In Progress'), LmTools.FmtBool(t.get('PairingInProgress')))

			t = r.get('MACFiltering')
			if t is not None:
				i = self.addInfoLine(self._liveboxAList, i, lx('MAC Filtering'), t.get('Mode'))

		return i


	### Load LAN infos
	def loadLanInfo(self, iIndex = 0):
		i = self.addTitleLine(self._liveboxAList, iIndex, lx('LAN Information'))

		try:
			d = self._session.request('DHCPv4.Server', 'getDHCPServerPool', { 'id': 'default' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			d = d.get('default')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('DHCPv4'), 'DHCPv4.Server:getDHCPServerPool query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('DHCPv4 Enabled'), LmTools.FmtBool(d.get('Enable')))
			i = self.addInfoLine(self._liveboxAList, i, lx('DHCPv4 Status'), d.get('Status'))
			i = self.addInfoLine(self._liveboxAList, i, lx('DHCPv4 Gateway'), d.get('Server'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Subnet Mask'), d.get('SubnetMask'))
			i = self.addInfoLine(self._liveboxAList, i, lx('DHCPv4 Start'), d.get('MinAddress'))
			i = self.addInfoLine(self._liveboxAList, i, lx('DHCPv4 End'), d.get('MaxAddress'))
			i = self.addInfoLine(self._liveboxAList, i, lx('DHCPv4 Lease Time'), LmTools.FmtTime(d.get('LeaseTime')))

		try:
			d = self._session.request('DHCPv6.Server', 'getDHCPv6ServerStatus')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('DHCPv6'), 'DHCPv6.Server:getDHCPv6ServerStatus query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('DHCPv6 Status'), d)

		b = None
		try:
			d = self._session.request('NeMo.Intf.lan', 'getMIBs', { 'mibs': 'base eth' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			b = d.get('base')
			d = d.get('eth')

		if (d is None) or (b is None):
			i = self.addInfoLine(self._liveboxAList, i, lx('LAN'), 'NeMo.Intf.lan:getMIBs query error', LmTools.ValQual.Error)
			return

		for s in LmConfig.NET_INTF:
			if s['Type'] != 'eth':
				continue
			i = self.addTitleLine(self._liveboxAList, i, s['Name'])

			q = b.get(s['Key'])
			r = d.get(s['Key'])
			if (q is None) or (r is None):
				continue

			i = self.addInfoLine(self._liveboxAList, i, lx('Enabled'), LmTools.FmtBool(q.get('Enable')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Active'), LmTools.FmtBool(q.get('Status')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Current Bit Rate'), LmTools.FmtInt(r.get('CurrentBitRate')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Max Bit Rate Supported'), LmTools.FmtInt(r.get('MaxBitRateSupported')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Current Duplex Mode'), r.get('CurrentDuplexMode'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Power Saving Supported'), LmTools.FmtBool(q.get('PowerSavingSupported')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Power Saving Enabled'), LmTools.FmtBool(q.get('PowerSavingEnabled')))

		return i


	### Load ONT infos
	def loadOntInfo(self, iIndex = 0):
		i = self.addTitleLine(self._liveboxAList, iIndex, lx('ONT Information'))

		# Call SFP module for LB4
		if self._liveboxModel == 4:
			try:
				d = self._session.request('SFP', 'get')
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				d = None
			if d is not None:
				d = d.get('status')
			if d is None:
				i = self.addInfoLine(self._liveboxAList, i, lx('ONT'), 'SFP:get query error', LmTools.ValQual.Error)
			else:
				i = self.addInfoLine(self._liveboxAList, i, lx('Status'), d.get('Status'))
				i = self.addInfoLine(self._liveboxAList, i, lx('Connection Status'), LmTools.FmtBool(d.get('ONTReady')))
				i = self.addInfoLine(self._liveboxAList, i, lx('SFP Status'), LmTools.FmtInt(d.get('DeviceState')))
				i = self.addInfoLine(self._liveboxAList, i, lx('Operating State'), LmTools.FmtInt(d.get('OperatingState')))
				i = self.addInfoLine(self._liveboxAList, i, lx('Orange'), LmTools.FmtBool(d.get('Orange')))
				i = self.addInfoLine(self._liveboxAList, i, lx('Serial Number'), d.get('SerialNumber'))
				i = self.addInfoLine(self._liveboxAList, i, lx('Registration ID'), d.get('RegistrationID'))
				i = self.addInfoLine(self._liveboxAList, i, lx('Local Registration ID'), d.get('LocalRegistrationID'))
				v = d.get('OpticalSignalLevel')
				if v is not None:
					v /= 1000
					i = self.addInfoLine(self._liveboxAList, i, lx('Signal RxPower'), str(v) + ' dBm')
				v = d.get('TransmitOpticalLevel')
				if v is not None:
					v /= 1000
					i = self.addInfoLine(self._liveboxAList, i, lx('Signal TxPower'), str(v) + ' dBm')
				i = self.addInfoLine(self._liveboxAList, i, lx('Temperature'), LmTools.FmtInt(d.get('ChipsetTemperature')) + '°')
				i = self.addInfoLine(self._liveboxAList, i, lx('Model Name'), d.get('ModelName'))
				i = self.addInfoLine(self._liveboxAList, i, lx('Manufacturer'), d.get('Manufacturer'))
				i = self.addInfoLine(self._liveboxAList, i, lx('Hardware Version'), d.get('HardwareVersion'))
				i = self.addInfoLine(self._liveboxAList, i, lx('Firmware 1 Version'), d.get('Software1Version'))
				i = self.addInfoLine(self._liveboxAList, i, lx('Firmware 1 State'), LmTools.FmtInt(d.get('Software1Status')))
				i = self.addInfoLine(self._liveboxAList, i, lx('Firmware 2 Version'), d.get('Software2Version'))
				i = self.addInfoLine(self._liveboxAList, i, lx('Firmware 2 State'), LmTools.FmtInt(d.get('Software2Status')))
			return i

		aOntIntf = None
		for s in LmConfig.NET_INTF:
			if s['Type'] == 'ont':
				aOntIntf = s['Key']
				break
		if aOntIntf is None:
			return i

		try:
			d = self._session.request('NeMo.Intf.' + aOntIntf, 'getMIBs', { 'mibs': 'gpon' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			d = d.get('gpon')
		if d is not None:
			d = d.get(aOntIntf)
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('ONT'), 'NeMo.Intf.' + aOntIntf + ':getMIBs query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('VEIP PPTP UNI'), LmTools.FmtBool(d.get('VeipPptpUni')))
			i = self.addInfoLine(self._liveboxAList, i, lx('OMCI Is Tm Owner'), LmTools.FmtBool(d.get('OmciIsTmOwner')))
			v = d.get('MaxBitRateSupported')
			if v is not None:
				i = self.addInfoLine(self._liveboxAList, i, lx('Max Bit Rate Supported'), str(v / 1000) + ' Gbps')

			v = d.get('SignalRxPower')
			if v is not None:
				v /= 1000
				if self._linkType == 'XGS-PON':
					if (v < -28.0) or (v > -9.0):
						aQual = LmTools.ValQual.Error
					elif (v < -24.0) or (v > -13.0):
						aQual = LmTools.ValQual.Warn
					else:
						aQual = LmTools.ValQual.Good					
				else:
					if (v < -30.0) or (v > -8.0):
						aQual = LmTools.ValQual.Error
					elif (v < -26.0) or (v > -12.0):
						aQual = LmTools.ValQual.Warn
					else:
						aQual = LmTools.ValQual.Good
				i = self.addInfoLine(self._liveboxAList, i, lx('Signal RxPower'), str(v) + ' dBm', aQual)

			v = d.get('SignalTxPower')
			if v is not None:
				v /= 1000
				if self._linkType == 'XGS-PON':
					if (v < 4.0) or (v > 9.0):
						aQual = LmTools.ValQual.Error
					elif (v < 4.5) or (v > 8.5):
						aQual = LmTools.ValQual.Warn
					else:
						aQual = LmTools.ValQual.Good
				else:
					if (v < 0.5) or (v > 5.0):
						aQual = LmTools.ValQual.Error
					elif (v < 1.0) or (v > 4.5):
						aQual = LmTools.ValQual.Warn
					else:
						aQual = LmTools.ValQual.Good
				i = self.addInfoLine(self._liveboxAList, i, lx('Signal TxPower'), str(v) + ' dBm', aQual)

			v = d.get('Temperature')
			if v is not None:
				if (v < -40) or (v > 100):
					aQual = LmTools.ValQual.Error
				elif (v < -10) or (v > 70):
					aQual = LmTools.ValQual.Warn
				else:
					aQual = LmTools.ValQual.Good
				i = self.addInfoLine(self._liveboxAList, i, lx('Temperature'), str(v) + '°', aQual)

			v = d.get('Voltage')
			if v is not None:
				v /= 10000
				if (v < 3.2) or (v > 3.4):
					aQual = LmTools.ValQual.Error
				elif (v < 3.25) or (v > 3.35):
					aQual = LmTools.ValQual.Warn
				else:
					aQual = LmTools.ValQual.Good
				i = self.addInfoLine(self._liveboxAList, i, lx('Voltage'), str(round(v, 2)) + ' V', aQual)

			v = d.get('Bias')
			if v is not None:
				if self._liveboxModel >= 6:
					v /= 10000
				if (v < 0) or (v > 150):
					aQual = LmTools.ValQual.Error
				elif v > 75:
					aQual = LmTools.ValQual.Warn
				else:
					aQual = LmTools.ValQual.Good
				i = self.addInfoLine(self._liveboxAList, i, lx('BIAS'), str(v) + ' mA', aQual)

			i = self.addInfoLine(self._liveboxAList, i, lx('Serial Number'), d.get('SerialNumber'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Hardware Version'), d.get('HardwareVersion'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Equipment ID'), d.get('EquipmentId'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Vendor ID'), d.get('VendorId'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Vendor Product Code'), LmTools.FmtInt(d.get('VendorProductCode')))
			i = self.addInfoLine(self._liveboxAList, i, lx('Pon ID'), d.get('PonId'))
			i = self.addInfoLine(self._liveboxAList, i, lx('Registration ID'), d.get('RegistrationID'))
			i = self.addInfoLine(self._liveboxAList, i, lx('ONT Software Version 0'), d.get('ONTSoftwareVersion0'))
			i = self.addInfoLine(self._liveboxAList, i, lx('ONT Software Version 1'), d.get('ONTSoftwareVersion1'))
			i = self.addInfoLine(self._liveboxAList, i, lx('ONT Software Version Active'), LmTools.FmtInt(d.get('ONTSoftwareVersionActive')))
			i = self.addInfoLine(self._liveboxAList, i, lx('ONU State'), d.get('ONUState'))
			aRate = d.get('DownstreamMaxRate')
			if aRate is not None:
				aRate *= 1024
				i = self.addInfoLine(self._liveboxAList, i, lx('Max Down Bit Rate'), LmTools.FmtBytes(aRate))
			aRate = d.get('UpstreamMaxRate')
			if aRate is not None:
				aRate *= 1024
				i = self.addInfoLine(self._liveboxAList, i, lx('Max Up Bit Rate'), LmTools.FmtBytes(aRate))
			aRate = d.get('DownstreamCurrRate')
			if aRate is not None:
				aRate *= 1024
				i = self.addInfoLine(self._liveboxAList, i, lx('Current Down Bit Rate'), LmTools.FmtBytes(aRate))
			aRate = d.get('UpstreamCurrRate')
			if aRate is not None:
				aRate *= 1024
				i = self.addInfoLine(self._liveboxAList, i, lx('Current Up Bit Rate'), LmTools.FmtBytes(aRate))

		return i


	### Load VoIP infos
	def loadVoipInfo(self, iIndex = 0):
		i = self.addTitleLine(self._liveboxAList, iIndex, lx('VoIP Information'))

		try:
			d = self._session.request('VoiceService.VoiceApplication', 'listTrunks')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('VoIP'), 'VoiceService.VoiceApplication:listTrunks query error', LmTools.ValQual.Error)
		else:
			for q in d:
				i = self.addInfoLine(self._liveboxAList, i, lx('VoIP Enabled'), q.get('enable'))
				i = self.addInfoLine(self._liveboxAList, i, lx('Protocol'), q.get('signalingProtocol'))
				aLines = q.get('trunk_lines')
				if aLines is not None:
					for l in aLines:
						aName = l.get('name', 'Line')
						i = self.addInfoLine(self._liveboxAList, i, lx('{} Enabled').format(aName), l.get('enable'))
						i = self.addInfoLine(self._liveboxAList, i, lx('{} Status').format(aName), l.get('status'))
						i = self.addInfoLine(self._liveboxAList, i, lx('{} Status Info').format(aName), l.get('statusInfo'))
						i = self.addInfoLine(self._liveboxAList, i, lx('{} Number').format(aName), l.get('directoryNumber'))

		# No DECT on Livebox 6
		if self._liveboxModel >= 6:
			return i

		i = self.addTitleLine(self._liveboxAList, i, lx('DECT Information'))

		try:
			d = self._session.request('DECT', 'getName')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('Name'), 'DECT:getName query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('Name'), d)

		try:
			d = self._session.request('DECT', 'getPIN')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('PIN'), 'DECT:getPIN query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('PIN'), d)

		try:
			d = self._session.request('DECT', 'getRFPI')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('RFPI'), 'DECT:getRFPI query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('RFPI'), d)

		try:
			d = self._session.request('DECT', 'getVersion')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('Software Version'), 'DECT:getVersion query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('Software Version'), d)

		try:
			d = self._session.request('DECT', 'getStandardVersion')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('CAT-iq Version'), 'DECT:getStandardVersion query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('CAT-iq Version'), d)

		try:
			d = self._session.request('DECT', 'getPairingStatus')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('Pairing Status'), 'DECT:getPairingStatus query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('Pairing Status'), d)

		try:
			d = self._session.request('DECT', 'getRadioState')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('Radio State'), 'DECT:getRadioState query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('Radio State'), LmTools.FmtBool(d))

		try:
			d = self._session.request('DECT.Repeater', 'get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('Repeater Status'), 'DECT.Repeater:get query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('Repeater Status'), d.get('Status'))

		return i


	### Load IPTV infos
	def loadIptvInfo(self, iIndex = 0):
		i = self.addTitleLine(self._liveboxAList, iIndex, lx('IPTV Information'))

		try:
			d = self._session.request('NMC.OrangeTV', 'getIPTVStatus')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('data')
		if d is not None:
			d = d.get('IPTVStatus')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('IPTV Status'), 'NMC.OrangeTV:getIPTVStatus query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('IPTV Status'), d)

		try:
			d = self._session.request('NMC.OrangeTV', 'getIPTVMultiScreens')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('data')
		if d is not None:
			d = d.get('Enable')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('Multi Screens Status'), 'NMC.OrangeTV:getIPTVMultiScreens query error', LmTools.ValQual.Error)
		else:
			i = self.addInfoLine(self._liveboxAList, i, lx('Multi Screens Status'), lx('Available') if d else lx('Disabled'))

		try:
			d = self._session.request('NMC.OrangeTV', 'getIPTVConfig')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('IPTV Config'), 'NMC.OrangeTV:IPTVConfig query error', LmTools.ValQual.Error)
		else:
			for q in d:
				aNames = q.get('ChannelFlags')
				if (aNames is not None):
					aNameList = aNames.split()
					aNamesStr = ''
					for n in aNameList:
						if len(aNamesStr):
							aNamesStr += ', '
						aNamesStr += n
					aStatus = q.get('ChannelStatus', False)
					aValue = lx('Available') if aStatus else lx('Disabled')
					aChannelType = q.get('ChannelType')
					if aChannelType is not None:
						aValue += ' - ' + aChannelType
						aChannelNumber = q.get('ChannelNumber')
						if aChannelNumber is not None:
							aValue += ' : ' + str(aChannelNumber)
					i = self.addInfoLine(self._liveboxAList, i, aNamesStr, aValue)

		return i


	### Load USB infos
	def loadUsbInfo(self, iIndex = 0):
		i = self.addTitleLine(self._liveboxAList, iIndex, lx('USB Information'))

		try:
			d = self._session.request('Devices', 'get', { 'expression': 'usb' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			i = self.addInfoLine(self._liveboxAList, i, lx('USB'), 'Devices:get query error', LmTools.ValQual.Error)
		else:
			aDeviceFound = False
			for q in d:
				aSource = q.get('DiscoverySource')
				if aSource == 'selfusb':
					if q.get('Active', False):
						aActive = lx('Active')
					else:
						aActive = lx('Inactive')
					i = self.addInfoLine(self._liveboxAList, i, q.get('Name', lx('Unknown USB')), aActive)
				elif aSource == 'usb_storage':
					i = self.addTitleLine(self._liveboxAList, i, lx('USB Device Storage'))
					i = self.addInfoLine(self._liveboxAList, i, lx('Key'), q.get('Key'))
					i = self.addInfoLine(self._liveboxAList, i, lx('Device Type'), q.get('DeviceType'))
					i = self.addInfoLine(self._liveboxAList, i, lx('Active'), LmTools.FmtBool(q.get('Active')))
					i = self.addInfoLine(self._liveboxAList, i, lx('First Seen'), LmTools.FmtLiveboxTimestamp(q.get('FirstSeen')))
					i = self.addInfoLine(self._liveboxAList, i, lx('Last Connection'), LmTools.FmtLiveboxTimestamp(q.get('LastConnection')))
					i = self.addInfoLine(self._liveboxAList, i, lx('File System'), q.get('FileSystem'))
					n = q.get('Capacity')
					if n is not None:
						n *= 1024 * 1024
						i = self.addInfoLine(self._liveboxAList, i, lx('Capacity'), LmTools.FmtBytes(n))
					n = q.get('UsedSpace')
					if n is not None:
						n *= 1024 * 1024
						i = self.addInfoLine(self._liveboxAList, i, lx('Used Space'), LmTools.FmtBytes(n))
					aNames = q.get('Names')
					if aNames is not None:
						aStr = ''
						for n in aNames:
							aName = n.get('Name', '')
							if len(aName):
								if len(aStr):
									aStr += ', '
								aStr += aName
						i = self.addInfoLine(self._liveboxAList, i, lx('Names'), aStr)
				elif aSource == 'usb_dev':
					i = self.addTitleLine(self._liveboxAList, i, lx('USB Device'))
					i = self.addInfoLine(self._liveboxAList, i, lx('Name'), q.get('Name'))
					i = self.addInfoLine(self._liveboxAList, i, lx('Device Type'), q.get('DeviceType'))
					i = self.addInfoLine(self._liveboxAList, i, lx('Active'), LmTools.FmtBool(q.get('Active')))
					i = self.addInfoLine(self._liveboxAList, i, lx('Last Connection'), LmTools.FmtLiveboxTimestamp(q.get('LastConnection')))
					i = self.addInfoLine(self._liveboxAList, i, lx('Location'), q.get('Location'))
					i = self.addInfoLine(self._liveboxAList, i, lx('Owner'), q.get('Owner'))
					i = self.addInfoLine(self._liveboxAList, i, lx('USB Version'), q.get('USBVersion'))
					i = self.addInfoLine(self._liveboxAList, i, lx('Device Version'), LmTools.FmtInt(q.get('DeviceVersion')))
					i = self.addInfoLine(self._liveboxAList, i, lx('Product ID'), LmTools.FmtInt(q.get('ProductID')))
					i = self.addInfoLine(self._liveboxAList, i, lx('Vendor ID'), LmTools.FmtInt(q.get('VendorID')))
					i = self.addInfoLine(self._liveboxAList, i, lx('Manufacturer'), q.get('Manufacturer'))
					i = self.addInfoLine(self._liveboxAList, i, lx('Serial Number'), q.get('SerialNumber'))
					i = self.addInfoLine(self._liveboxAList, i, lx('Port'), LmTools.FmtInt(q.get('Port')))
					i = self.addInfoLine(self._liveboxAList, i, lx('Rate'), q.get('Rate'))

		return i


	### Get Livebox Wifi status (used by ActionsTab)
	def getLiveboxWifiStatus(self):
		u = {}
		u[WifiKey.AccessPoint] = 'Livebox'

		# General Wifi status
		aWifiSchedulerStatus = None
		try:
			d = self._session.request('NMC.Wifi', 'get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is None:
			u[WifiKey.Enable] = WifiStatus.Error
			u[WifiKey.Status] = WifiStatus.Error
		else:
			u[WifiKey.Enable] = WifiStatus.Enable if d.get('Enable', False) else WifiStatus.Disable
			u[WifiKey.Status] = WifiStatus.Enable if d.get('Status', False) else WifiStatus.Disable
			aWifiSchedulerStatus = d.get('SchedulingEnabled')

		# Wifi scheduler status
		# First try with PowerManagement services
		aStatus = None
		try:
			d = self._session.request('PowerManagement', 'getProfiles')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			d = d.get('WiFi')
		if d is not None:
			aStatus = d.get('Activate')
		else:
			# Try with Scheduler services if PowerManagement failed
			try:
				d = self._session.request('Scheduler', 'getCompleteSchedules', { 'type': 'WLAN' })
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				d = None
			if (d is not None) and (d.get('status', False)):
				d = d.get('data')
			else:
				d = None
			if d is not None:
				d = d.get('scheduleInfo', [])
				if len(d):
					aStatus = d[0].get('enable')

		# Agregate result
		if aStatus is None:
			if aWifiSchedulerStatus is None:
				u[WifiKey.Scheduler] = WifiStatus.Error
			else:
				u[WifiKey.Scheduler] = WifiStatus.Enable if aWifiSchedulerStatus else WifiStatus.Disable
		else:
			if aWifiSchedulerStatus is None:
				u[WifiKey.Scheduler] = WifiStatus.Enable if aStatus else WifiStatus.Disable
			else:
				u[WifiKey.Scheduler] = WifiStatus.Enable if (aStatus and aWifiSchedulerStatus) else WifiStatus.Disable

		# Wifi interfaces status
		b = None
		w = None
		try:
			d = self._session.request('NeMo.Intf.lan', 'getMIBs', { 'mibs': 'base wlanradio' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			b = d.get('base')
			w = d.get('wlanradio')

		try:
			d = self._session.request('NeMo.Intf.lan', 'getMIBs', { 'mibs': 'wlanvap', 'flag': 'wlanvap !secondary' })
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
			if self._liveboxModel >= 6:
				u[WifiKey.Wifi6Enable] = WifiStatus.Error
				u[WifiKey.Wifi6Status] = WifiStatus.Error
				u[WifiKey.Wifi6VAP] = WifiStatus.Error
		else:
			for s in LmConfig.NET_INTF:
				if s['Type'] != 'wif':
					continue

				if s['Name'] == 'Wifi 2.4GHz':
					aEnableKey = WifiKey.Wifi2Enable
					aStatusKey = WifiKey.Wifi2Status
					aVAPKey = WifiKey.Wifi2VAP
				elif s['Name'] == 'Wifi 5GHz':
					aEnableKey = WifiKey.Wifi5Enable
					aStatusKey = WifiKey.Wifi5Status
					aVAPKey = WifiKey.Wifi5VAP
				else:
					aEnableKey = WifiKey.Wifi6Enable
					aStatusKey = WifiKey.Wifi6Status
					aVAPKey = WifiKey.Wifi6VAP

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

		# Guest Wifi status
		try:
			d = self._session.request('NeMo.Intf.guest', 'getMIBs', { 'mibs': 'wlanvap' })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if d is not None:
			d = d.get('wlanvap')

		if d is None:
			u[WifiKey.Guest2VAP] = WifiStatus.Error
			u[WifiKey.Guest5VAP] = WifiStatus.Error
		else:
			for s in LmConfig.NET_INTF:
				if s['Type'] != 'wig':
					continue

				if s['Name'] == 'Guest 2.4GHz':
					aVAPKey = WifiKey.Guest2VAP
				else:
					aVAPKey = WifiKey.Guest5VAP

				r = d.get(s['Key'])
				if r is None:
					u[aVAPKey] = WifiStatus.Error
				else:
					u[aVAPKey] = WifiStatus.Enable if (r.get('VAPStatus', 'Down') == 'Up') else WifiStatus.Disable

		return u



# ############# Livebox global stats collector thread #############
class LiveboxStatsThread(QtCore.QObject):
	_statsReceived = QtCore.pyqtSignal(dict)
	_resume = QtCore.pyqtSignal()

	def __init__(self, iSession):
		super(LiveboxStatsThread, self).__init__()
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
		# WARNING counters are recycling at 4Gb only:
		for s in LmConfig.NET_INTF:
			aResult = self._session.request('NeMo.Intf.' + s['Key'], 'getNetDevStats')
			if aResult is not None:
				aStats = aResult.get('status')
				if type(aStats).__name__ == 'dict':
					e = {}
					e['Key'] = s['Key']
					e['Source'] = 'nds'		# NetDevStats
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


'''
		# EXPERIMENTAL - not successful:
		# - HomeLan:getWANCounters generates wrong HomeLan veip0 stats events
		# - HomeLan events do not cover all interfaces -> need to keep getNetDevStats()
		for s in LmConfig.NET_INTF:
			if s['Type'] == 'wan':	# WARNING -> need to add a 'wan' line in LmConfig.NET_INTF
				aResult = self._session.request('HomeLan', 'getWANCounters')	# WARNING: Works but generates wrong HomeLan veip0 stats events
				if aResult is not None:
					aStats = aResult.get('status')
					if type(aStats).__name__ == 'dict':
						e = {}
						e['Key'] = s['Key']
						e['Timestamp'] = datetime.datetime.now()		# WARNING - can use timestamp coming from stat itself
						if s['SwapStats']:
							e['RxBytes'] = aStats.get('BytesSent', 0)
							e['TxBytes'] = aStats.get('BytesReceived', 0)
							e['RxErrors'] = 0
							e['TxErrors'] = 0
						else:
							e['RxBytes'] = aStats.get('BytesReceived', 0)
							e['TxBytes'] = aStats.get('BytesSent', 0)
							e['RxErrors'] = 0
							e['TxErrors'] = 0
						self._statsReceived.emit(e)
				break

'''

'''
		# EXPERIMENTAL - not successful:
		# - Stats are not real time, not relevant.
		# - Counters look 64bits but are recycling chaotically, after 512Gb, or 3Gb, ...
		for s in LmConfig.NET_INTF:
			if s['Type'] == 'wan':
				aResult = self._session.request('HomeLan', 'getWANCounters')
			else:
				aResult = self._session.request('HomeLan.Interface.' + s['Key'] + '.Stats', 'get')
			if aResult is not None:
				aStats = aResult.get('status')
				if type(aStats).__name__ == 'dict':
					e = {}
					e['Key'] = s['Key']
					e['Timestamp'] = datetime.datetime.now()
					if s['SwapStats']:
						e['RxBytes'] = aStats.get('BytesSent', 0)
						e['TxBytes'] = aStats.get('BytesReceived', 0)
						e['RxErrors'] = 0
						e['TxErrors'] = 0
					else:
						e['RxBytes'] = aStats.get('BytesReceived', 0)
						e['TxBytes'] = aStats.get('BytesSent', 0)
						e['RxErrors'] = 0
						e['TxErrors'] = 0
					self._statsReceived.emit(e)
'''




