### Livebox Monitor events tab module ###

import json
import datetime

from enum import IntEnum

from PyQt6 import QtGui
from PyQt6 import QtCore
from PyQt6 import QtWidgets

from src import LmTools
from src import LmConfig
from src.LmDeviceListTab import DSelCol


# ################################ VARS & DEFS ################################

# Static Config
MAX_EVENT_BUFFER_PER_DEVICE = 100

# List columns
class EventCol(IntEnum):
	Key = 0
	Time = 1
	Reason = 2
	Attribute = 3
	Count = 4


# ################################ LmEvents class ################################
class LmEvents:

	### Create events tab
	def createEventsTab(self):
		self._eventsTab = QtWidgets.QWidget()

		# Device list
		self._eventDList = QtWidgets.QTableWidget()
		self._eventDList.setColumnCount(DSelCol.Count)
		self._eventDList.setHorizontalHeaderLabels(('Key', 'Name', 'MAC'))
		self._eventDList.setColumnHidden(DSelCol.Key, True)
		self._eventDList.horizontalHeader().setSectionResizeMode(DSelCol.Name, QtWidgets.QHeaderView.ResizeMode.Stretch)
		self._eventDList.horizontalHeader().setSectionResizeMode(DSelCol.MAC, QtWidgets.QHeaderView.ResizeMode.Fixed)
		self._eventDList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._eventDList.setColumnWidth(DSelCol.Name, 200)
		self._eventDList.setColumnWidth(DSelCol.MAC, 120 + LmConfig.DUAL_PANE_ADJUST)
		self._eventDList.verticalHeader().hide()
		self._eventDList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self._eventDList.setSortingEnabled(True)
		self._eventDList.setGridStyle(QtCore.Qt.PenStyle.SolidLine)
		self._eventDList.setStyleSheet(LmConfig.LIST_STYLESHEET)
		self._eventDList.horizontalHeader().setStyleSheet(LmConfig.LIST_HEADER_STYLESHEET)
		self._eventDList.horizontalHeader().setFont(LmTools.BOLD_FONT)
		self._eventDList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		self._eventDList.setMinimumWidth(350 + LmConfig.DUAL_PANE_ADJUST)
		self._eventDList.itemSelectionChanged.connect(self.eventDeviceListClick)

		# Event list
		self._eventList = QtWidgets.QTableWidget()
		self._eventList.setColumnCount(EventCol.Count)
		self._eventList.setHorizontalHeaderLabels(('Key', 'Time', 'Reason', 'Attributes'))
		self._eventList.setColumnHidden(EventCol.Key, True)
		self._eventList.horizontalHeader().setSectionResizeMode(EventCol.Time, QtWidgets.QHeaderView.ResizeMode.Fixed)
		self._eventList.horizontalHeader().setSectionResizeMode(EventCol.Reason, QtWidgets.QHeaderView.ResizeMode.Fixed)
		self._eventList.horizontalHeader().setSectionResizeMode(EventCol.Attribute, QtWidgets.QHeaderView.ResizeMode.Stretch)
		self._eventList.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
		self._eventList.setColumnWidth(EventCol.Time, 80)
		self._eventList.setColumnWidth(EventCol.Reason, 150)
		self._eventList.setColumnWidth(EventCol.Attribute, 600)
		self._eventList.verticalHeader().hide()
		self._eventList.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self._eventList.setSortingEnabled(True)
		self._eventList.setGridStyle(QtCore.Qt.PenStyle.SolidLine)
		self._eventList.setStyleSheet(LmConfig.LIST_STYLESHEET)
		self._eventList.horizontalHeader().setStyleSheet(LmConfig.LIST_HEADER_STYLESHEET)
		self._eventList.horizontalHeader().setFont(LmTools.BOLD_FONT)
		self._eventList.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		self._eventList.doubleClicked.connect(self.displayEventButtonClick)

		# Lists layout
		aListBox = QtWidgets.QHBoxLayout()
		aListBox.setSpacing(10)
		aListBox.addWidget(self._eventDList, 0)
		aListBox.addWidget(self._eventList, 1)

		# Button bar
		aButtonsBox = QtWidgets.QHBoxLayout()
		aButtonsBox.setSpacing(30)
		aDisplayEventButton = QtWidgets.QPushButton('Display Event')
		aDisplayEventButton.clicked.connect(self.displayEventButtonClick)
		aButtonsBox.addWidget(aDisplayEventButton)

		# Layout
		aVBox = QtWidgets.QVBoxLayout()
		aVBox.setSpacing(10)
		aVBox.addLayout(aListBox, 0)
		aVBox.addLayout(aButtonsBox, 1)
		self._eventsTab.setLayout(aVBox)

		self._tabWidget.addTab(self._eventsTab, 'Events')


	### Init the Livebox event collector thread
	def initEventLoop(self):
		self._lastEventDeviceKey = ''
		self._statsMap = {}
		self._eventBuffer = {}
		self._liveboxEventThread = None
		self._liveboxEventLoop = None


	### Start the Livebox event collector thread
	def startEventLoop(self):
		self._liveboxEventThread = QtCore.QThread()
		self._liveboxEventLoop = LiveboxEventThread(self._session)
		self._liveboxEventLoop.moveToThread(self._liveboxEventThread)
		self._liveboxEventThread.started.connect(self._liveboxEventLoop.run)
		self._liveboxEventLoop._eventReceived.connect(self.processLiveboxEvent)
		self._liveboxEventThread.start()


	### Suspend the Livebox stats collector thread
	def suspendEventLoop(self):
		if self._liveboxEventThread is not None:
			self._liveboxEventLoop.stop()


	### Resume the Livebox stats collector thread
	def resumeEventLoop(self):
		if self._liveboxEventThread is None:
			self.startEventLoop()
		else:
			self._liveboxEventLoop.run()


	### Stop the Livebox event collector thread
	def stopEventLoop(self):
		if self._liveboxEventThread is not None:
			self._liveboxEventLoop.stop()
			self._liveboxEventThread.quit()
			self._liveboxEventThread.wait()
			self._liveboxEventThread = None
			self._liveboxEventLoop = None


	### Click on event device list
	def eventDeviceListClick(self):
		self._eventList.clearContents()
		self._eventList.setRowCount(0)

		aCurrentSelection = self._eventDList.currentRow()
		if aCurrentSelection >= 0:
			aKey = self._eventDList.item(aCurrentSelection, DSelCol.Key).text()
			self._eventList.setSortingEnabled(False)
			self.updateEventList(aKey)
			self._eventList.setSortingEnabled(True)


	### Click on display event button
	def displayEventButtonClick(self):
		aCurrDeviceSelection = self._eventDList.currentRow()
		if aCurrDeviceSelection < 0:
			LmTools.DisplayError('Please select a device.')
			return

		aDeviceKey = self._eventDList.item(aCurrDeviceSelection, DSelCol.Key).text()

		aCurrEventSelection = self._eventList.currentRow()
		if aCurrEventSelection < 0:
			LmTools.DisplayError('No event selected.')
			return

		aEventKey = int(self._eventList.item(aCurrEventSelection, EventCol.Key).text())
		aDeviceEventDict = self._eventBuffer.get(aDeviceKey, {})
		aEventArray = aDeviceEventDict.get('Events', [])

		# Retrieve event entry in the array
		e = None
		for aEvent in aEventArray:
			if aEvent['Key'] == aEventKey:
				e = aEvent
				break

		if e is None:
			LmTools.DisplayError('Event entry not found.')
			return

		# Display event entry
		aTextDoc = QtGui.QTextDocument()
		aStandardFont = QtGui.QFont('Courier New', 9)
		aBoldFont = QtGui.QFont('Tahoma', 9, QtGui.QFont.Weight.Bold)
		aTextDoc.setDefaultFont(aStandardFont)
		aStandardFormat = QtGui.QTextCharFormat()
		aStandardFormat.setFont(aStandardFont)
		aBoldFormat = QtGui.QTextCharFormat()
		aBoldFormat.setFont(aBoldFont)

		aCursor = QtGui.QTextCursor(aTextDoc)
		aCursor.beginEditBlock()
		aCursor.insertText('Raised: ', aBoldFormat)
		aCursor.insertText(str(e['Timestamp']) + '\n', aStandardFormat)
		aCursor.insertText('Handler: ', aBoldFormat)
		aCursor.insertText(e['Handler'] + '\n', aStandardFormat)
		aCursor.insertText('Reason: ', aBoldFormat)
		aCursor.insertText(e['Reason'] + '\n\n', aStandardFormat)
		aCursor.insertText('Attributes:\n', aBoldFormat)
		aCursor.insertText(json.dumps(e['Attributes'], indent=2), aStandardFormat)
		aCursor.endEditBlock()

		LmTools.DisplayInfos('Event Entry', None, aTextDoc)


	### Update event list
	def updateEventList(self, iDeviceKey):
		aDeviceEventDict = self._eventBuffer.get(iDeviceKey, {})
		aEventArray = aDeviceEventDict.get('Events', [])

		i = 0
		for e in aEventArray:
			self._eventList.insertRow(i)
			self.setEventListLine(i, e)
			i += 1


	### Set event list line
	def setEventListLine(self, iLine, iEvent):
		self._eventList.setItem(iLine, EventCol.Key, QtWidgets.QTableWidgetItem(str(iEvent['Key'])))
		aTime = iEvent['Timestamp']
		aTimeStamp = '{:02d}:{:02d}:{:02d}'.format(aTime.hour, aTime.minute, aTime.second)
		aTimeItem = QtWidgets.QTableWidgetItem(aTimeStamp)
		aTimeItem.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self._eventList.setItem(iLine, EventCol.Time, aTimeItem)
		self._eventList.setItem(iLine, EventCol.Reason, QtWidgets.QTableWidgetItem(iEvent['Reason']))
		aAttribute = str(iEvent['Attributes'])[0:256]
		self._eventList.setItem(iLine, EventCol.Attribute, QtWidgets.QTableWidgetItem(aAttribute))


	### Process a new Livebox event
	def processLiveboxEvent(self, iEvent):
		d = iEvent.get('data')
		if d is not None:
			h = d.get('handler', '')
			o = d.get('object')
			if o is not None:
				r = o.get('reason', '')
				a = o.get('attributes')
			else:
				r = ''
				a = None
			# Try to guess device key from handler
			aDeviceKey = LmTools.ExtractMacAddrFromString(h)
			if len(aDeviceKey):
				self.updateEventIndicator(aDeviceKey)
				if r == 'Statistics':
					e = a.get(aDeviceKey)
					if e is not None:
						self.processStatisticsEvent(aDeviceKey, e)
						self.bufferizeEvent(aDeviceKey, h, r, e)
					else:
						self.bufferizeEvent(aDeviceKey, h, r, a)
				elif r == 'changed':
					self.processChangedEvent(aDeviceKey, h, a)
					self.bufferizeEvent(aDeviceKey, h, r, a)
				elif r == 'device_name_changed':
					e = a.get(aDeviceKey)
					if e is not None:
						self.processDeviceNameChangedEvent(aDeviceKey, e)
						self.bufferizeEvent(aDeviceKey, h, r, e)
					else:
						self.bufferizeEvent(aDeviceKey, h, r, a)
				elif (r == 'device_updated') or (r == 'eth_device_updated') or (r == 'wifi_device_updated'):
					e = a.get(aDeviceKey)
					if e is not None:
						self.processDeviceUpdatedEvent(aDeviceKey, e)
						self.bufferizeEvent(aDeviceKey, h, r, e)
					else:
						self.bufferizeEvent(aDeviceKey, h, r, a)
				elif r == 'ip_address_added':
					e = a.get(aDeviceKey)
					if e is not None:
						self.processIPAddressAddedEvent(aDeviceKey, a[aDeviceKey])
						self.bufferizeEvent(aDeviceKey, h, r, a[aDeviceKey])
					else:
						self.bufferizeEvent(aDeviceKey, h, r, a)
				elif (r == 'device_added') or (r == 'eth_device_added') or (r == 'wifi_device_added'):
					e = a.get(aDeviceKey)
					if e is not None:
						self.processDeviceAddedEvent(aDeviceKey, a[aDeviceKey])
						self.bufferizeEvent(aDeviceKey, h, r, a[aDeviceKey])
					else:
						self.bufferizeEvent(aDeviceKey, h, r, a)
				else:
					# Check if device is in the list, otherwise put the event in the None list
					if (self.findDeviceLine(self._eventDList, aDeviceKey) >= 0):
						self.bufferizeEvent(aDeviceKey, h, r, a)
					else:
						self.bufferizeEvent(None, h, r, a)
			else:
				self.bufferizeEvent(None, h, r, a)


	### Store event in buffer, for the UI
	def bufferizeEvent(self, iDeviceKey, iHandler, iReason, iAttributes):
		# Find event dict for the device
		if iDeviceKey is None:
			iDeviceKey = '#NONE#'
		aDeviceEventDict = self._eventBuffer.get(iDeviceKey)
		if aDeviceEventDict is None:
			aDeviceEventDict = {}
			aDeviceEventDict['Sequence'] = 1
			aDeviceEventDict['Events'] = []
			self._eventBuffer[iDeviceKey] = aDeviceEventDict
		aDeviceSequence = aDeviceEventDict['Sequence']
		aEventArray = aDeviceEventDict['Events']

		# Create event entry
		aEntry = {}
		aEntry['Key'] = aDeviceSequence
		aEntry['Timestamp'] = datetime.datetime.now()
		aEntry['Handler'] = iHandler
		aEntry['Reason'] = iReason
		aEntry['Attributes'] = iAttributes

		# Insert front, limit total size and update sequence
		aEventArray.insert(0, aEntry)
		if len(aEventArray) > MAX_EVENT_BUFFER_PER_DEVICE:
			aEventArray.pop()
		aDeviceEventDict['Sequence'] = aDeviceSequence + 1

		# Update UI if device is selected in event tab
		aCurrDeviceSelection = self._eventDList.currentRow()
		if aCurrDeviceSelection >= 0:
			aSelectedDeviceKey = self._eventDList.item(aCurrDeviceSelection, DSelCol.Key).text()
			if aSelectedDeviceKey == iDeviceKey:
				self._eventList.insertRow(0)
				self.setEventListLine(0, aEntry)



# ############# Livebox events collector thread #############
class LiveboxEventThread(QtCore.QObject):
	_eventReceived = QtCore.pyqtSignal(dict)

	def __init__(self, iSession):
		super(LiveboxEventThread, self).__init__()
		self._isRunning = False
		self._channelID = 0
		self._session = iSession


	def run(self):
		self._isRunning = True
		while (self._isRunning):
			aResult = self._session.eventRequest(['Devices.Device'], self._channelID)
			if aResult is not None:
				self._channelID = aResult.get('channelid', 0)
				aEvents = aResult.get('events')
				if aEvents is not None:
					for e in aEvents:
						self._eventReceived.emit(e)


	def stop(self):
		self._isRunning = False

