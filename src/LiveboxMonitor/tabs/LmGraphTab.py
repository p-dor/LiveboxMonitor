### Livebox Monitor graph tab module ###

import os
import time
import csv
from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmTableWidget import LmTableWidget
from LiveboxMonitor.dlg.LmAddGraph import AddGraphDialog, GraphType
from LiveboxMonitor.lang.LmLanguages import get_graph_label as lx, get_graph_message as mx


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'graphTab'

# Config default
DCFG_WINDOW = 24	# 1 day
DCFG_BACKGROUND_COLOR = '#000000' 		# (0, 0, 0)
DCFG_STAT_FREQUENCY = 30	# In case the service doesn't work, 30 secs is the normal value

# Constants
UNIT_DIVIDER = 1048576		# To convert bytes in megabytes
WIND_UPDATE_FREQ = 60000	# 1mn - frequency of the window update task, cutting old values

# List columns
class GraphCol(IntEnum):
	Key = 0		# type constant + '_' + ID
	Name = 1
	Type = 2
	ID = 3
	Color = 4


# ################################ LmGraph class ################################
class LmGraph:

	### Create Graph tab
	def createGraphTab(self):
		self._graphTab = QtWidgets.QWidget(objectName = TAB_NAME)

		# Graph list box
		aGraphListLayout = QtWidgets.QVBoxLayout()
		aGraphListLayout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
		aGraphListLayout.setSpacing(5)

		aSelectLabel = QtWidgets.QLabel(lx('Interfaces and devices to display'), objectName = 'selectLabel')
		aGraphListLayout.addWidget(aSelectLabel, 0, QtCore.Qt.AlignmentFlag.AlignTop)

		# Interface / device graph list
		self._graphList = LmTableWidget(objectName = 'graphList')
		self._graphList.set_columns({GraphCol.Key: ['Key', 0, None],
									 GraphCol.Name: [lx('Name'), 150, 'graphList_Name'],
									 GraphCol.Type: [lx('Type'), 55, 'graphList_Type'],
									 GraphCol.ID: [lx('ID'), 120, 'graphList_ID'],
									 GraphCol.Color: [lx('Color'), 55, 'graphList_Color']})
		self._graphList.set_header_resize([GraphCol.Name])
		self._graphList.set_standard_setup(self)

		aGraphListSize = LmConfig.table_height(8)
		self._graphList.setMinimumHeight(aGraphListSize)
		self._graphList.setMaximumHeight(aGraphListSize)
		self._graphList.setMinimumWidth(380)
		aGraphListLayout.addWidget(self._graphList, 0, QtCore.Qt.AlignmentFlag.AlignTop)

		# Interface / device graph list button bar
		aGraphListButtonBox = QtWidgets.QHBoxLayout()
		aGraphListButtonBox.setSpacing(5)
		aAddGraphButton = QtWidgets.QPushButton(lx('Add...'), objectName = 'addGraph')
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

		# To inhibit useless "skipping QEventPoint" logs on MacOS when moving the mouse on graphs
		# -> https://stackoverflow.com/questions/75746637/how-to-suppress-qt-pointer-dispatch-warning
		self._downGraph.viewport().setAttribute(QtCore.Qt.WidgetAttribute.WA_AcceptTouchEvents, False)
		self._upGraph.viewport().setAttribute(QtCore.Qt.WidgetAttribute.WA_AcceptTouchEvents, False)

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

		LmConfig.set_tooltips(self._graphTab, 'graph')
		self._tab_widget.addTab(self._graphTab, lx('Graph'))

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
		self._graphWindowTimer = None


	### Click on graph tab
	def graphTabClick(self):
		if not self._graphDataLoaded:
			self._graphDataLoaded = True	# Must be first to avoid reentrency during tab drag&drop

			# Load config & data
			self._task.start(lx('Loading configuration...'))
			self.loadStatParams()
			self.loadHomeLanInterfaces()
			self.loadHomeLanDevices()
			self.loadGraphConfig()
			self._task.end()

			# Plot data
			self._task.start(lx('Plotting graphes...'))
			self.plotGraph()
			self._task.end()

			# Start graph time window update timer, to cut regularly old values
			self._graphWindowTimer = QtCore.QTimer()
			self._graphWindowTimer.timeout.connect(self.graphWindowUpdate)
			self._graphWindowTimer.start(WIND_UPDATE_FREQ)


	### Click on add graph button
	def addGraphButtonClick(self):
		dialog = AddGraphDialog(self)
		if dialog.exec():
			self.addGraphObject(dialog.get_type(),
								dialog.get_object_key(),
								dialog.get_object_name(),
								dialog.get_object_id(),
								dialog.get_color())


	### Add a graph object in the list
	def addGraphObject(self, iType, iKey, iName, iID, iColor):
		iKey = iType + '_' + iKey

		i = self._graphList.rowCount()
		self._graphList.insertRow(i)
		self._graphList.setItem(i, GraphCol.Key, QtWidgets.QTableWidgetItem(iKey))
		self._graphList.setItem(i, GraphCol.Name, QtWidgets.QTableWidgetItem(iName))

		if iType == GraphType.INTERFACE:
			iType = lx('Interface')
		else:
			iType = lx('Device')
		self._graphList.setItem(i, GraphCol.Type, QtWidgets.QTableWidgetItem(iType))

		self._graphList.setItem(i, GraphCol.ID, QtWidgets.QTableWidgetItem(iID))

		aColorItem = QtWidgets.QTableWidgetItem()
		aColorItem.setBackground(QtGui.QColor(iColor))
		aColorItem.setData(QtCore.Qt.ItemDataRole.UserRole, iColor)
		self._graphList.setItem(i, GraphCol.Color, aColorItem)


	### Click on delete graph button
	def delGraphButtonClick(self):
		aCurrentSelection = self._graphList.currentRow()
		if aCurrentSelection >= 0:
			self._graphList.removeRow(aCurrentSelection)
		else:
			self.display_error(mx('Please select a line.', 'lineSelect'))


	### Click on apply button
	def applyGraphButtonClick(self):
		# Load current setup
		self._graphWindow = int(self._graphWindowEdit.text())
		if self._graphWindow < 0:
			self._graphWindow = 0
		elif self._graphWindow > 99:
			self._graphWindow = 99
		self._graphBackColor = self._graphBackColorEdit.get_color()

		# Save setup
		self.saveGraphConfig()

		# Refresh interface & device lists
		self._task.start(lx('Plotting graphes...'))
		self.loadHomeLanInterfaces()
		self.loadHomeLanDevices()

		# Plot the graphs
		self.plotGraph()
		self._task.end()


	### Click on export button
	def exportGraphButtonClick(self):
		if len(self._graphData):
			aFolder = QtWidgets.QFileDialog.getExistingDirectory(self, lx('Select Export Folder'))
			if len(aFolder):
				aFolder = QtCore.QDir.toNativeSeparators(aFolder)
				for o in self._graphData:
					self.exportGraphObject(aFolder, o)
		else:
			self.display_error(mx('No graph to export.', 'noGraph'))


	### Export a graph object to a file
	def exportGraphObject(self, iFolder, iObject):
		aSuffix = ''
		n = 0

		while True:
			aFilePath = os.path.join(iFolder, 'StatExport_' + iObject['Name'] + aSuffix + '.csv')
			try:
				aExportFile = open(aFilePath, 'x', newline = '')
			except FileExistsError:
				n += 1
				aSuffix = '_' + str(n)
				continue
			except Exception as e:
				LmTools.error(str(e))
				self.display_error(mx('Cannot create the file.', 'createFileErr'))
				return
			break

		self._task.start(lx('Exporting statistics...'))

		# Write header line
		aCsvWriter = csv.writer(aExportFile, dialect = 'excel', delimiter = LmConf.CsvDelimiter)
		aCsvWriter.writerow(['Download Timestamp', 'Download Bytes', 'Upload Timestamp', 'Upload Bytes'])

		dt = iObject['DownTime']
		d = iObject['Down']
		ut = iObject['UpTime']
		u = iObject['Up']

		n =  min(len(dt), len(ut))
		i = 0
		while i < n:
			aCsvWriter.writerow([str(dt[i]), str(int(d[i] * UNIT_DIVIDER)),
								 str(ut[i]), str(int(u[i] * UNIT_DIVIDER))])
			i += 1

		self._task.end()

		try:
			aExportFile.close()
		except Exception as e:
			LmTools.error(str(e))
			self.display_error(mx('Cannot save the file.', 'saveFileErr'))


	### Load stats parameters
	def loadStatParams(self):
		try:
			aReply = self._session.request('HomeLan', 'getReadingInterval')
		except Exception as e:
			LmTools.error(str(e))
			self.display_error('HomeLan:getReadingInterval query error.')
			aReply = None

		if aReply is not None:
			aReply = aReply.get('status')
			if aReply is not None:
				self._statFrequencyInterfaces = int(aReply)

		try:
			aReply = self._session.request('HomeLan', 'getDevicesReadingInterval')
		except Exception as e:
			LmTools.error(str(e))
			self.display_error('HomeLan:getDevicesReadingInterval query error.')
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
				if aType == GraphType.INTERFACE:
					e = next((e for e in self._graphValidInterfaces if e[0] == aKey), None)
					if e is None:
						continue
					i = next((i for i in self._api._intf.get_list() if i['Key'] == aKey), None)
					if i is None:
						continue
					self.addGraphObject(aType, aKey, i['Name'], e[2], aColor)
				elif aType == GraphType.DEVICE:
					e = next((e for e in self._graphValidDevices if e[0] == aKey), None)
					if e is None:
						continue
					try:
						aName = LmConf.MacAddrTable[aKey]
					except Exception:
						aName = aKey
					self.addGraphObject(aType, aKey, aName, e[2], aColor)
				else:
					continue

		self._graphWindowEdit.setText(str(self._graphWindow))
		self._graphBackColorEdit.set_color(self._graphBackColor)


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
		self._downGraph.showGrid(x = True, y = True, alpha = 0.4)
		self._upGraph.setBackground(self._graphBackColor)
		self._upGraph.showGrid(x = True, y = True, alpha = 0.4)

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
		if iType == GraphType.INTERFACE:
			aStatsData = self.loadStatsInterface(iID, aStartTime, aEndTime)
			aIntf = next((i for i in self._api._intf.get_list() if i['Key'] == iKey), None)
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
		o = next((o for o in self._graphData if (o['Type'] == GraphType.INTERFACE) and (o['Key'] == iIntfKey)), None)
		if o is not None:
			self.graphUpdateObjectEvent(o, iTimestamp, iDownBytes, iUpBytes)


	### Update graph according to device stats event
	def graphUpdateDeviceEvent(self, iDeviceKey, iTimestamp, iDownBytes, iUpBytes):
		# Lookup for a stat object matching interface
		o = next((o for o in self._graphData if (o['Type'] == GraphType.DEVICE) and (o['Key'] == iDeviceKey)), None)
		if o is not None:
			self.graphUpdateObjectEvent(o, iTimestamp, iDownBytes, iUpBytes)


	### Update graph according to stats event
	def graphUpdateObjectEvent(self, iObject, iTimestamp, iDownBytes, iUpBytes):
		# Update download part
		if iDownBytes is not None:
			# Update timestamp array
			dt = iObject['DownTime']
			dt.append(iTimestamp)

			# Update data
			d = iObject['Down']
			d.append(iDownBytes / UNIT_DIVIDER)		# Convert to MBs

			# Update graph
			iObject['DownLine'].setData(dt, d)

		# Update upload part
		if iUpBytes is not None:
			# Update timestamp array
			ut = iObject['UpTime']
			ut.append(iTimestamp)

			# Update data
			u = iObject['Up']
			u.append(iUpBytes / UNIT_DIVIDER)		# Convert to MBs

			# Update graph
			iObject['UpLine'].setData(ut, u)


	# Cut old values to match graph time window
	def graphWindowUpdate(self):
		# Determine older allowed timestamp
		if self._graphWindow:
			aWindow = self._graphWindow
		else:
			# If no window cut after 5 days
			aWindow = 5 * 24
		aMaxOlderValue = int(time.time()) - (aWindow * 3600)

		# Loop on each drawn object
		for o in self._graphData:
			self.graphWindowUpdateLine(o['DownLine'], o['DownTime'], o['Down'], aMaxOlderValue)
			self.graphWindowUpdateLine(o['UpLine'], o['UpTime'], o['Up'], aMaxOlderValue)


	# Cut old values to match graph time window
	def graphWindowUpdateLine(self, iLine, iTimeArray, iDataArray, iMaxOlderValue):
		aNeedRefresh = False

		while(len(iTimeArray) and (iTimeArray[0] <= iMaxOlderValue)):
			aNeedRefresh = True
			iTimeArray.pop(0)
			iDataArray.pop(0)

		if aNeedRefresh:
			iLine.setData(iTimeArray, iDataArray)


	### Update graph list with new device name
	def graphUpdateDeviceName(self, iDeviceKey):
		i = self.findGraphObjectLine(GraphType.DEVICE, iDeviceKey)
		if i > -1:
			try:
				aName = LmConf.MacAddrTable[iDeviceKey]
			except Exception:
				aName = iDeviceKey
			self._graphList.setItem(i, GraphCol.Name, QtWidgets.QTableWidgetItem(aName))


	### Load the current valid interfaces
	def loadHomeLanInterfaces(self):
		try:
			aReply = self._session.request('HomeLan.Interface', 'get')
		except Exception as e:
			LmTools.error(str(e))
			self.display_error('HomeLan interfaces query error.')
			return

		if aReply is not None:
			aInterfaces = aReply.get('status')
		else:
			aInterfaces = None
		if aInterfaces is not None:
			# Reset
			self._graphValidInterfaces = []

			# Iterate over all configured interfaces
			for i in self._api._intf.get_list():
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
			self.display_error('HomeLan interfaces query failed.')


	### Load the current valid devices
	def loadHomeLanDevices(self):
		try:
			aReply = self._session.request('HomeLan.Device', 'get')
		except Exception as e:
			LmTools.error(str(e))
			self.display_error('HomeLan devices query error.')
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
			self.display_error('HomeLan devices query failed.')


	### Load the stats for the given interface ID
	def loadStatsInterface(self, iID, iStart, iEnd):
		try:
			if iStart:
				aReply = self._session.request('HomeLan', 'getResults',
											   { 'InterfaceName': iID, 'BeginTrafficTimestamp': iStart, 'EndTrafficTimestamp': iEnd },
											   timeout=15)
			else:
				aReply = self._session.request('HomeLan', 'getResults', { 'InterfaceName': iID }, timeout=15)
		except Exception as e:
			LmTools.error(str(e))
			self.display_error('Interface statistics query error.')
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
				aReply = self._session.request('HomeLan', 'getDeviceResults',
											   { 'DeviceName': iID, 'BeginTrafficTimestamp': iStart, 'EndTrafficTimestamp': iEnd },
											   timeout=15)
			else:
				aReply = self._session.request('HomeLan', 'getDeviceResults', { 'DeviceName': iID }, timeout=15)				
		except Exception as e:
			LmTools.error(str(e))
			self.display_error('Device statistics query error.')
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
