### Livebox Monitor graph tab module ###

import os
import time
from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

from src import LmTools, LmConfig
from src.LmConfig import LmConf
from src.LmLanguages import (GetGraphLabel as lx,
							 GetAddGraphDialogLabel as lgx)


# ################################ VARS & DEFS ################################

# Config default
DCFG_WINDOW = 24	# 1 day
DCFG_BACKGROUND_COLOR = '#000000' 		# (0, 0, 0)
DCFG_OBJECT_COLOR = [ '#E26043',		# (226, 96, 67)
					  '#626DF4',		# (98, 109, 244)
					  '#65F4B4',		# (101, 244, 180)
					  '#EDF465',		# (237, 244, 101)
					  '#B474F4',		# (180, 116, 244)
					  '#42F4F4',		# (66, 244, 244)
					  '#FF0000',		# (255, 0, 0)
					  '#00FF00',		# (0, 255, 0)
					  '#0000FF',		# (0, 0, 255)
					  '#FFFF00',		# (255, 255, 0)
					  '#FF00FF' ]		# (255, 0, 255)
DCFG_STAT_FREQUENCY = 30	# In case the service doesn't work, 30 secs is the normal value

# Constants
TYPE_INTERFACE = 'inf'	# must be 3 chars
TYPE_DEVICE = 'dvc'		# must be 3 chars
UNIT_DIVIDER = 1048576	# To convert bytes in megabytes

# List columns
class GraphCol(IntEnum):
	Key = 0		# type constant + '_' + ID
	Name = 1
	Type = 2
	ID = 3
	Color = 4
	Count = 5


# ################################ LmGraph class ################################
class LmGraph:

	### Create Graph tab
	def createGraphTab(self):
		self._graphTab = QtWidgets.QWidget(objectName = 'graphTab')

		# Graph list box
		aGraphListLayout = QtWidgets.QVBoxLayout()
		aGraphListLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aGraphListLayout.setSpacing(5)

		aSelectLabel = QtWidgets.QLabel(lx('Interfaces and devices to display'), objectName = 'selectLabel')
		aGraphListLayout.addWidget(aSelectLabel, 0, QtCore.Qt.AlignmentFlag.AlignTop)

		# Interface / device graph list
		self._graphList = QtWidgets.QTableWidget(objectName = 'graphList')
		self._graphList.setColumnCount(GraphCol.Count)
		self._graphList.setHorizontalHeaderLabels(('Key', lx('Name'), lx('Type'), lx('ID'), lx('Color')))
		self._graphList.setColumnHidden(GraphCol.Key, True)
		aHeader = self._graphList.horizontalHeader()
		aHeader.setSectionsMovable(False)
		aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Interactive)
		aHeader.setSectionResizeMode(GraphCol.Name, QtWidgets.QHeaderView.ResizeMode.Stretch)
		aModel = aHeader.model()
		aModel.setHeaderData(GraphCol.Name, QtCore.Qt.Orientation.Horizontal, 'graphList_Name', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(GraphCol.Type, QtCore.Qt.Orientation.Horizontal, 'graphList_Type', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(GraphCol.ID, QtCore.Qt.Orientation.Horizontal, 'graphList_ID', QtCore.Qt.ItemDataRole.UserRole)
		aModel.setHeaderData(GraphCol.Color, QtCore.Qt.Orientation.Horizontal, 'graphList_Color', QtCore.Qt.ItemDataRole.UserRole)
		self._graphList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._graphList.setColumnWidth(GraphCol.Name, 150)
		self._graphList.setColumnWidth(GraphCol.Type, 55)
		self._graphList.setColumnWidth(GraphCol.ID, 120)
		self._graphList.setColumnWidth(GraphCol.Color, 55)
		self._graphList.verticalHeader().hide()
		self._graphList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self._graphList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
		self._graphList.setSortingEnabled(True)
		self._graphList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		LmConfig.SetTableStyle(self._graphList)
		aGraphListSize = LmConfig.TableHeight(8)
		self._graphList.setMinimumHeight(aGraphListSize)
		self._graphList.setMaximumHeight(aGraphListSize)
		self._graphList.setMinimumWidth(380)
		aGraphListLayout.addWidget(self._graphList, 0, QtCore.Qt.AlignmentFlag.AlignTop)

		# Interface / device graph list button bar
		aGraphListButtonBox = QtWidgets.QHBoxLayout()
		aGraphListButtonBox.setSpacing(5)
		aAddGraphButton = QtWidgets.QPushButton(lx('Add'), objectName = 'addGraph')
		aAddGraphButton.clicked.connect(self.addGraphButtonClick)
		aGraphListButtonBox.addWidget(aAddGraphButton)
		aDelGraphButton = QtWidgets.QPushButton(lx('Delete'), objectName = 'delGraph')
		aDelGraphButton.clicked.connect(self.delGraphButtonClick)
		aGraphListButtonBox.addWidget(aDelGraphButton)
		aGraphListLayout.addLayout(aGraphListButtonBox, 0)

		# Setup grid
		aWindowLabel = QtWidgets.QLabel(lx('Window:'), objectName = 'windowLabel')
		aIntValidator = QtGui.QIntValidator()
		aIntValidator.setRange(0, 99)
		self._graphWindowEdit = QtWidgets.QLineEdit(objectName = 'windowEdit')
		self._graphWindowEdit.setValidator(aIntValidator)
		aWindowUnit = QtWidgets.QLabel(lx('hours (0 = max)'), objectName = 'windowUnit')

		aBackColorLabel = QtWidgets.QLabel(lx('Background color:'), objectName = 'backColorLabel')
		self._graphBackColorEdit = LmTools.ColorButton(objectName = 'backColor')

		aSetupGrid = QtWidgets.QGridLayout()
		aSetupGrid.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aSetupGrid.setSpacing(10)
		aSetupGrid.addWidget(aWindowLabel, 0, 0)
		aSetupGrid.addWidget(self._graphWindowEdit, 0, 1)
		aSetupGrid.addWidget(aWindowUnit, 0, 2)
		aSetupGrid.addWidget(aBackColorLabel, 1, 0)
		aSetupGrid.addWidget(self._graphBackColorEdit, 1, 1)
		aSetupGrid.setColumnStretch(2, 1)

		# Apply button
		aApplyButton = QtWidgets.QPushButton(lx('Apply'), objectName = 'apply')
		aApplyButton.clicked.connect(self.applyGraphButtonClick)

		# Export button
		aExportButton = QtWidgets.QPushButton(lx('Export...'), objectName = 'export')
		aExportButton.clicked.connect(self.exportGraphButtonClick)

		# Control box
		aControlBox = QtWidgets.QVBoxLayout()
		aControlBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aControlBox.setSpacing(20)
		aControlBox.addLayout(aGraphListLayout, 0)
		aControlBox.addLayout(aSetupGrid, 0)
		aControlBox.addWidget(aApplyButton, QtCore.Qt.AlignmentFlag.AlignTop)
		aControlBox.addWidget(aExportButton, QtCore.Qt.AlignmentFlag.AlignTop)

		# Graph box
		aGraphBox = QtWidgets.QVBoxLayout()
		aStyles = {'color': '#FF0000', 'font-size': '11px'}

		self._downGraph = pg.PlotWidget()	# Setting objectName on input doesn't work
		self._downGraph.setObjectName('downGraph')
		self._downGraph.setTitle(lx('Download'))
		self._downGraph.setLabel('left', lx('Traffic (MB)'), **aStyles)
		self._downGraph.setLabel('bottom', lx('Time'), **aStyles)
		aDownAxis = pg.DateAxisItem()
		self._downGraph.setAxisItems({'bottom':aDownAxis})

		self._upGraph = pg.PlotWidget()		# Setting objectName on input doesn't work
		self._upGraph.setObjectName('upGraph')
		self._upGraph.setTitle(lx('Upload'))
		self._upGraph.setLabel('left', lx('Traffic (MB)'), **aStyles)
		self._upGraph.setLabel('bottom', lx('Time'), **aStyles)
		aUpAxis = pg.DateAxisItem()
		self._upGraph.setAxisItems({'bottom':aUpAxis})

		aGraphBox.addWidget(self._downGraph)
		aGraphBox.addWidget(self._upGraph)

		# Layout
		aSeparator = QtWidgets.QFrame()
		aSeparator.setFrameShape(QtWidgets.QFrame.Shape.VLine)
		aSeparator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

		aHBox = QtWidgets.QHBoxLayout()
		aHBox.setSpacing(10)
		aHBox.addLayout(aControlBox, 0)
		aHBox.addWidget(aSeparator)
		aHBox.addLayout(aGraphBox, 1)
		self._graphTab.setLayout(aHBox)

		LmConfig.SetToolTips(self._graphTab, 'graph')
		self._tabWidget.addTab(self._graphTab, lx('Graph'))

		# Init context
		self.graphTabInit()


	### Init graph tab context
	def graphTabInit(self):
		self._graphDataLoaded = False
		self._statFrequencyInterfaces = DCFG_STAT_FREQUENCY
		self._statFrequencyDevices = DCFG_STAT_FREQUENCY
		self._graphValidInterfaces = []		# Array of [Key, MeasureNb, ID]	- ID is the FriendlyName
		self._graphValidDevices = []		# Arrray of [Key, MeasureNb, ID] - ID is the Key
		self._graphData = []


	### Click on graph tab
	def graphTabClick(self):
		if not self._graphDataLoaded:
			self.startTask(lx('Loading configuration...'))
			self.loadStatParams()
			self.loadHomeLanInterfaces()
			self.loadHomeLanDevices()
			self.loadGraphConfig()
			self.endTask()

			self.startTask(lx('Plotting graphes...'))
			self.plotGraph()
			self._graphDataLoaded = True
			self.endTask()


	### Click on add graph button
	def addGraphButtonClick(self):
		aAddGraphDialog = AddGraphDialog(self)
		if aAddGraphDialog.exec():
			self.addGraphObject(aAddGraphDialog.getType(),
								aAddGraphDialog.getObjectKey(),
								aAddGraphDialog.getObjectName(),
								aAddGraphDialog.getObjectID(),
								aAddGraphDialog.getColor())


	### Add a graph object in the list
	def addGraphObject(self, iType, iKey, iName, iID, iColor):
		iKey = iType + '_' + iKey

		i = self._graphList.rowCount()
		self._graphList.insertRow(i)
		self._graphList.setItem(i, GraphCol.Key, QtWidgets.QTableWidgetItem(iKey))
		self._graphList.setItem(i, GraphCol.Name, QtWidgets.QTableWidgetItem(iName))

		if iType == TYPE_INTERFACE:
			iType = lx('Interface')
		else:
			iType = lx('Device')
		self._graphList.setItem(i, GraphCol.Type, QtWidgets.QTableWidgetItem(iType))

		self._graphList.setItem(i, GraphCol.ID, QtWidgets.QTableWidgetItem(iID))

		aColorItem = QtWidgets.QTableWidgetItem()
		aColorItem.setBackground(QtGui.QColor(iColor))
		self._graphList.setItem(i, GraphCol.Color, aColorItem)


	### Click on delete graph button
	def delGraphButtonClick(self):
		aCurrentSelection = self._graphList.currentRow()
		if aCurrentSelection >= 0:
			self._graphList.removeRow(aCurrentSelection)
		else:
			LmTools.DisplayError('Please select a line.')


	### Click on apply button
	def applyGraphButtonClick(self):
		# Load current setup
		self._graphWindow = int(self._graphWindowEdit.text())
		if self._graphWindow < 0:
			self._graphWindow = 0
		elif self._graphWindow > 99:
			self._graphWindow = 99
		self._graphBackColor = self._graphBackColorEdit.getColor()

		# Save setup
		self.saveGraphConfig()

		# Refresh interface & device lists
		self.startTask(lx('Plotting graphes...'))
		self.loadHomeLanInterfaces()
		self.loadHomeLanDevices()

		# Plot the graphs
		self.plotGraph()
		self.endTask()


	### Click on export button
	def exportGraphButtonClick(self):
		if len(self._graphData):
			aFolder = QtWidgets.QFileDialog.getExistingDirectory(self, lx('Select Export Folder'))
			if len(aFolder):
				for o in self._graphData:
					self.exportGraphObject(aFolder, o)
		else:
			LmTools.DisplayError('No graph to export.')


	### Export a graph object to a file
	def exportGraphObject(self, iFolder, iObject):
		aSuffix = ''
		n = 0

		while True:
			aFilePath = os.path.join(iFolder, 'StatExport_' + iObject['Name'] + aSuffix + '.csv')
			try:
				aExportFile = open(aFilePath, 'x')
			except FileExistsError:
				n += 1
				aSuffix = '_' + str(n)
				continue
			except BaseException as e:
				LmTools.Error('Error: {}'.format(e))
				LmTools.DisplayError('Cannot create the file.')
				return
			break

		self.startTask(lx('Exporting statistics...'))

		# Write header line
		aExportFile.write('Download Timestamp, Download Bytes, Upload Timestamp, Upload Bytes\n')

		dt = iObject['DownTime']
		d = iObject['Down']
		ut = iObject['UpTime']
		u = iObject['Up']

		n =  min(len(dt), len(ut))
		i = 0
		while i < n:
			aExportFile.write('{}, {}, {}, {}\n'.format(str(dt[i]),
														str(int(d[i] * UNIT_DIVIDER)),
														str(ut[i]),
														str(int(u[i] * UNIT_DIVIDER))))
			i += 1

		self.endTask()

		try:
			aExportFile.close()
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			LmTools.DisplayError('Cannot save the file.')


	### Load stats parameters
	def loadStatParams(self):
		try:
			aReply = self._session.request('HomeLan:getReadingInterval')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			LmTools.DisplayError('HomeLan getReadingInterval query error.')
			aReply = None

		if aReply is not None:
			aReply = aReply.get('status')
			if aReply is not None:
				self._statFrequencyInterfaces = int(aReply)

		try:
			aReply = self._session.request('HomeLan:getDevicesReadingInterval')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			LmTools.DisplayError('HomeLan getDevicesReadingInterval query error.')
			aReply = None

		if aReply is not None:
			aReply = aReply.get('status')
			if aReply is not None:
				self._statFrequencyDevices = int(aReply)


	### Load configuration
	def loadGraphConfig(self):
		self._graphWindow = DCFG_WINDOW
		self._graphBackColor = DCFG_BACKGROUND_COLOR
		if LmConf.Graph is not None:
			c = LmConf.Graph
			p = c.get('Window')
			if p is not None:
				self._graphWindow = int(p)
			p = c.get('BackColor')
			if p is not None:
				self._graphBackColor = p

			t = c['Objects']
			for o in t:
				p = o.get('Type')
				if p is None:
					continue
				else:
					aType = p
				p = o.get('Key')
				if p is None:
					continue
				else:
					aKey = p
				p = o.get('Color')
				if p is None:
					continue
				else:
					aColor = p
				if aType == TYPE_INTERFACE:
					e = next((e for e in self._graphValidInterfaces if e[0] == aKey), None)
					if e is None:
						continue
					i = next((i for i in LmConfig.NET_INTF if i['Key'] == aKey), None)
					if i is None:
						continue
					self.addGraphObject(aType, aKey, i['Name'], e[2], aColor)
				elif aType == TYPE_DEVICE:
					e = next((e for e in self._graphValidDevices if e[0] == aKey), None)
					if e is None:
						continue
					try:
						aName = LmConf.MacAddrTable[aKey]
					except:
						aName = aKey
					self.addGraphObject(aType, aKey, aName, e[2], aColor)
				else:
					continue

		self._graphWindowEdit.setText(str(self._graphWindow))
		self._graphBackColorEdit.setColor(self._graphBackColor)


	### Save configuration
	def saveGraphConfig(self):
		c = {}
		c['Window'] = self._graphWindow
		c['BackColor'] = self._graphBackColor

		t = []
		i = 0
		n = self._graphList.rowCount()
		while (i < n):
			o = {}
			aKey = self._graphList.item(i, GraphCol.Key).text()
			o['Type'] = aKey[0:3]
			o['Key'] = aKey[4:]
			o['Color']  = self._graphList.item(i, GraphCol.Color).background().color().name()
			t.append(o)
			i += 1
		c['Objects'] = t

		LmConf.Graph = c
		LmConf.save()


	### Plot the graphs
	def plotGraph(self):
		# Apply current setup
		self._downGraph.setBackground(self._graphBackColor)
		self._upGraph.setBackground(self._graphBackColor)

		# Reset
		self._graphData = []
		self._downGraph.clear()
		self._upGraph.clear()

		# Loop over the selected objects
		i = 0
		n = self._graphList.rowCount()
		while (i < n):
			aKey = self._graphList.item(i, GraphCol.Key).text()
			aName = self._graphList.item(i, GraphCol.Name).text()
			aID = self._graphList.item(i, GraphCol.ID).text()
			aColor = self._graphList.item(i, GraphCol.Color).background().color()
			self.plotObject(aKey[0:3], aKey[4:], aName, aID, aColor)
			i += 1


	### Plot an object
	def plotObject(self, iType, iKey, iName, iID, iColor):
		o = {}
		o['Type'] = iType
		o['Key'] = iKey
		o['Name'] = iName
		o['ID'] = iID

		# Set time window
		if self._graphWindow:
			aEndTime = int(time.time())
			aStartTime = aEndTime - (self._graphWindow * 3600)
		else:
			aStartTime = 0
			aEndTime = 0

		aSwapStats = False
		if iType == TYPE_INTERFACE:
			aStatsData = self.loadStatsInterface(iID, aStartTime, aEndTime)
			aIntf = next((i for i in LmConfig.NET_INTF if i['Key'] == iKey), None)
			if aIntf is not None:
				aSwapStats = aIntf['SwapStats']
		else:
			aStatsData = self.loadStatsDevice(iID, aStartTime, aEndTime)

		dt = []	# Download time data
		d = []	# Download data
		ut = [] # Upload time data
		u = [] 	# Upload data

		for e in reversed(aStatsData):
			aTime = e.get('Timestamp')
			if aTime is not None:
				dt.append(aTime)
				ut.append(aTime)

				if aSwapStats:
					aDownBits = e.get('Tx_Counter')
				else:
					aDownBits = e.get('Rx_Counter')
				if aDownBits is None:
					aDownBits = 0
				d.append((aDownBits / 8) / UNIT_DIVIDER)	# Convert bits to MBytes

				if aSwapStats:
					aUpBits = e.get('Rx_Counter')
				else:
					aUpBits = e.get('Tx_Counter')
				if aUpBits is None:
					aUpBits = 0
				u.append((aUpBits / 8) / UNIT_DIVIDER)		# Convert bits to MBytes

		o['DownTime'] = dt
		o['Down'] = d
		o['UpTime'] = ut
		o['Up'] = u

		aPen = pg.mkPen(color = iColor, width = 1)
		o['DownLine'] = self._downGraph.plot(dt, d, name = iID, pen = aPen)
		o['UpLine'] = self._upGraph.plot(ut, u, name = iID, pen = aPen)

		self._graphData.append(o)


	### Update graph according to interface stats event
	def graphUpdateInterfaceEvent(self, iIntfKey, iTimestamp, iDownBytes, iUpBytes):
		# Lookup for a stat object matching interface
		o = next((o for o in self._graphData if (o['Type'] == TYPE_INTERFACE) and (o['Key'] == iIntfKey)), None)
		if o is not None:
			self.graphUpdateObjectEvent(o, iTimestamp, iDownBytes, iUpBytes)


	### Update graph according to device stats event
	def graphUpdateDeviceEvent(self, iDeviceKey, iTimestamp, iDownBytes, iUpBytes):
		# Lookup for a stat object matching interface
		o = next((o for o in self._graphData if (o['Type'] == TYPE_DEVICE) and (o['Key'] == iDeviceKey)), None)
		if o is not None:
			self.graphUpdateObjectEvent(o, iTimestamp, iDownBytes, iUpBytes)


	### Update graph according to stats event
	def graphUpdateObjectEvent(self, iObject, iTimestamp, iDownBytes, iUpBytes):
		# Update download part
		if iDownBytes is not None:
			# Update timestamp array
			dt = iObject['DownTime']
			dt = dt[1:]
			dt.append(iTimestamp)
			iObject['DownTime'] = dt

			# Update data
			d = iObject['Down']
			d = d[1:]
			d.append(iDownBytes / UNIT_DIVIDER)		# Convert to MBs
			iObject['Down'] = d

			# Update graph
			iObject['DownLine'].setData(dt, d)

		# Update upload part
		if iUpBytes is not None:
			# Update timestamp array
			ut = iObject['UpTime']
			ut = ut[1:]
			ut.append(iTimestamp)
			iObject['UpTime'] = ut

			# Update data
			u = iObject['Up']
			u = u[1:]
			u.append(iUpBytes / UNIT_DIVIDER)		# Convert to MBs
			iObject['Up'] = u

			# Update graph
			iObject['UpLine'].setData(ut, u)


	### Load the current valid devices
	def loadHomeLanInterfaces(self):
		try:
			aReply = self._session.request('HomeLan.Interface:get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			LmTools.DisplayError('HomeLan interfaces query error.')
			return

		if aReply is not None:
			aInterfaces = aReply.get('status')
		else:
			aInterfaces = None
		if aInterfaces is not None:
			# Reset
			self._graphValidInterfaces = []

			# Iterate over all configured interfaces
			for i in LmConfig.NET_INTF:
				# Check if key exists in the returned interfaces
				k = i['Key']
				aIntfData = aInterfaces.get(k)
				if aIntfData is not None:
					m = aIntfData.get('NumberOfStoredMeasures')
					if m is not None:
						m = int(m)
					else:
						m = 0
					id = aIntfData.get('FriendlyName')
					if id is None:
						id = k
					self._graphValidInterfaces.append([k, m, id])
		else:
			LmTools.DisplayError('HomeLan interfaces query failed.')


	### Load the current valid devices
	def loadHomeLanDevices(self):
		try:
			aReply = self._session.request('HomeLan.Device:get')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			LmTools.DisplayError('HomeLan devices query error.')
			return

		if aReply is not None:
			aDevices = aReply.get('status')
		else:
			aDevices = None
		if aDevices is not None:
			# Reset
			self._graphValidDevices = []

			for d in aDevices:
				d = aDevices[d]
				a = d.get('MacAddress')
				if (a is not None) and (len(a)):
					m = d.get('NumberOfStoredMeasures')
					if m is not None:
						m = int(m)
					else:
						m = 0
					self._graphValidDevices.append([a, m, a])
		else:
			LmTools.DisplayError('HomeLan devices query failed.')


	### Load the stats for the given interface ID
	def loadStatsInterface(self, iID, iStart, iEnd):
		try:
			if iStart:
				aReply = self._session.request('HomeLan:getResults',
											   { 'InterfaceName': iID, 'BeginTrafficTimestamp': iStart, 'EndTrafficTimestamp': iEnd },
											   iTimeout = 15)
			else:
				aReply = self._session.request('HomeLan:getResults', { 'InterfaceName': iID }, iTimeout = 15)
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			LmTools.DisplayError('Interface statistics query error.')
			return

		if aReply is not None:
			aReply = aReply.get('status')
		if aReply is not None:
			aReply = aReply.get(iID)
		if aReply is not None:
			aReply = aReply.get('Traffic')
		if aReply is None:
			aReply = []
		return aReply


	### Load the stats for the given device ID
	def loadStatsDevice(self, iID, iStart, iEnd):
		try:
			if iStart:
				aReply = self._session.request('HomeLan:getDeviceResults',
											   { 'DeviceName': iID, 'BeginTrafficTimestamp': iStart, 'EndTrafficTimestamp': iEnd },
											   iTimeout = 15)
			else:
				aReply = self._session.request('HomeLan:getDeviceResults', { 'DeviceName': iID }, iTimeout = 15)				
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			LmTools.DisplayError('Device statistics query error.')
			return

		if aReply is not None:
			aReply = aReply.get('status')
		if aReply is not None:
			aReply = aReply.get(iID)
		if aReply is not None:
			aReply = aReply.get('Traffic')
		if aReply is None:
			aReply = []
		return aReply


	### Find object line in graph list from object type & key, return -1 if not found
	def findGraphObjectLine(self, iType, iKey):
		aKey = iType + '_' + iKey
		i = 0
		n = self._graphList.rowCount()
		while (i < n):
			if self._graphList.item(i, GraphCol.Key).text() == aKey:
				return i
			i += 1
		return -1



# ############# Add Graph dialog #############
class AddGraphDialog(QtWidgets.QDialog):
	def __init__(self, iParent):
		super(AddGraphDialog, self).__init__(iParent)
		self.resize(250, 150)

		self._app = iParent

		aTypeLabel = QtWidgets.QLabel(lgx('Type:'), objectName = 'typeLabel')
		self._typeCombo = QtWidgets.QComboBox(objectName = 'typeCombo')
		self._typeCombo.addItem(lgx('Interface'))
		self._typeCombo.addItem(lgx('Device'))
		self._typeCombo.activated.connect(self.typeSelected)

		aObjectLabel = QtWidgets.QLabel(lgx('Object:'), objectName = 'objectLabel')
		self._objectCombo = QtWidgets.QComboBox(objectName = 'objectCombo')
		self._objectCombo.activated.connect(self.objectSelected)
		self.loadObjectList()

		aColorLabel = QtWidgets.QLabel(lgx('Color:'), objectName = 'colorLabel')
		self._colorEdit = LmTools.ColorButton(objectName = 'colorEdit')
		self._colorEdit.setColor(DCFG_OBJECT_COLOR[self._app._graphList.rowCount() % len(DCFG_OBJECT_COLOR)])
		self._colorEdit._colorChanged.connect(self.colorSelected)

		aGrid = QtWidgets.QGridLayout()
		aGrid.setSpacing(10)
		aGrid.addWidget(aTypeLabel, 0, 0)
		aGrid.addWidget(self._typeCombo, 0, 1)
		aGrid.addWidget(aObjectLabel, 1, 0)
		aGrid.addWidget(self._objectCombo, 1, 1)
		aGrid.addWidget(aColorLabel, 2, 0)
		aGrid.addWidget(self._colorEdit, 2, 1)
		aGrid.setColumnStretch(1, 1)

		aSeparator = QtWidgets.QFrame()
		aSeparator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
		aSeparator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

		aIDLabel = QtWidgets.QLabel(lgx('ID:'), objectName = 'IDLabel')
		self._id = QtWidgets.QLabel(objectName = 'IDValue')
		aMeasureNbLabel = QtWidgets.QLabel(lgx('Measures number:'), objectName = 'measureLabel')
		self._measureNb = QtWidgets.QLabel(objectName = 'measureValue')
		aHistoryLabel = QtWidgets.QLabel(lgx('History:'), objectName = 'historyLabel')
		self._history = QtWidgets.QLabel(objectName = 'historyValue')

		aInfoGrid = QtWidgets.QGridLayout()
		aInfoGrid.setSpacing(8)
		aInfoGrid.addWidget(aIDLabel, 0, 0)
		aInfoGrid.addWidget(self._id, 0, 1)
		aInfoGrid.addWidget(aMeasureNbLabel, 1, 0)
		aInfoGrid.addWidget(self._measureNb, 1, 1)
		aInfoGrid.addWidget(aHistoryLabel, 2, 0)
		aInfoGrid.addWidget(self._history, 2, 1)
		aInfoGrid.setColumnStretch(1, 1)

		self._okButton = QtWidgets.QPushButton(lgx('OK'), objectName = 'ok')
		self._okButton.clicked.connect(self.accept)
		self._okButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton(lgx('Cancel'), objectName = 'cancel')
		aCancelButton.clicked.connect(self.reject)
		aHBox = QtWidgets.QHBoxLayout()
		aHBox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.setSpacing(10)
		aHBox.addWidget(self._okButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aHBox.addWidget(aCancelButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.setSpacing(18)
		aVBox.addLayout(aGrid, 0)
		aVBox.addWidget(aSeparator)
		aVBox.addLayout(aInfoGrid, 0)
		aVBox.addLayout(aHBox, 1)

		LmConfig.SetToolTips(self, 'addgraph')

		self.setWindowTitle(lgx('Add a graph'))
		self.udpdateInfos()
		self.setOkButtonState()
		self.setModal(True)
		self.show()


	def loadObjectList(self):
		self._objectCombo.clear()

		if self.getType() == TYPE_DEVICE:
			self.loadDeviceList()
		else:
			self.loadInterfaceList()


	def loadInterfaceList(self):
		for i in self._app._graphValidInterfaces:
			k = i[0]
			# Look if not already in the graph list
			if self._app.findGraphObjectLine(TYPE_INTERFACE, k) == -1:
				aIntf = next((j for j in LmConfig.NET_INTF if j['Key'] == k), None)
				if aIntf is not None:
					self._objectCombo.addItem(aIntf['Name'], userData = k)


	def loadDeviceList(self):
		for d in self._app._graphValidDevices:
			k = d[0]
			# Look if not already in the graph list
			if self._app.findGraphObjectLine(TYPE_DEVICE, k) == -1:
				try:
					aName = LmConf.MacAddrTable[k]
				except:
					aName = k
				self._objectCombo.addItem(aName, userData = k)


	def typeSelected(self, iIndex):
		self.loadObjectList()
		self.udpdateInfos()
		self.setOkButtonState()


	def objectSelected(self, iIndex):
		self.udpdateInfos()


	def colorSelected(self, iColor):
		self.setOkButtonState()


	def udpdateInfos(self):
		# Update infos according to selected object
		aType = self.getType()
		aKey = self.getObjectKey()
		if aType == TYPE_INTERFACE:
			aTable = self._app._graphValidInterfaces
			aFrequency = self._app._statFrequencyInterfaces
		else:
			aTable = self._app._graphValidDevices
			aFrequency = self._app._statFrequencyDevices

		# Search key in the table
		aEntry = next((o for o in aTable if o[0] == aKey), ['', 0, ''])
		aMeasureNb = aEntry[1]
		aHistory = aMeasureNb / ( 60 / aFrequency) / 60

		# Update infos
		self._id.setText(aEntry[2])
		self._measureNb.setText(str(aMeasureNb))
		self._history.setText(lgx('{:.1f} hours').format(aHistory))


	def setOkButtonState(self):
		self._okButton.setDisabled((self._objectCombo.count() == 0) or (self.getColor() is None))


	def getType(self):
		if self._typeCombo.currentIndex():
			return TYPE_DEVICE
		return TYPE_INTERFACE


	def getObjectKey(self):
		return self._objectCombo.currentData()


	def getObjectID(self):
		return self._id.text()


	def getObjectName(self):
		return self._objectCombo.currentText()


	def getColor(self):
		return self._colorEdit.getColor()
