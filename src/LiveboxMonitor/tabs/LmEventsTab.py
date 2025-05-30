### Livebox Monitor events tab module ###

import os
import json
import datetime
import time
import csv

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmTableWidget import LmTableWidget, CenteredIconHeaderView, CenteredIconsDelegate
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.tabs.LmDeviceListTab import DSelCol
from LiveboxMonitor.lang.LmLanguages import (get_events_label as lx,
											 get_events_message as mx,
											 get_notification_rules_label as lnx)


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'eventsTab'

# Static Config
MAX_EVENT_BUFFER_PER_DEVICE = 100

NOTIF_EVENT_DEVICE_ALL = 'ALL'
NOTIF_EVENT_DEVICE_UNKNOWN = 'UNK'

NOTIF_EVENT_TYPE_ADD = 'ADD'
NOTIF_EVENT_TYPE_DELETE = 'DEL'
NOTIF_EVENT_TYPE_ACTIVE = 'ACT'
NOTIF_EVENT_TYPE_INACTIVE = 'INA'
NOTIF_EVENT_TYPE_LINK_CHANGE = 'LNK'
NOTIF_EVENT_HUMAN_TYPE = {
	NOTIF_EVENT_TYPE_ADD: 			'Added',
	NOTIF_EVENT_TYPE_DELETE:		'Deleted',
	NOTIF_EVENT_TYPE_ACTIVE:		'Connected',
	NOTIF_EVENT_TYPE_INACTIVE:		'Disconnected',
	NOTIF_EVENT_TYPE_LINK_CHANGE:	'Access change'
}

NOTIF_EVENT_RULE_FILE = 'FIL'
NOTIF_EVENT_RULE_EMAIL = 'EMA'


# List columns
class EventCol(IntEnum):
	Key = 0
	Time = 1
	Reason = 2
	Attribute = 3

class RuleCol(IntEnum):
	Key = 0
	Add = 1
	Delete = 2
	Active = 3
	Inactive = 4
	Link = 5
	File = 6
	Email = 7
ICON_COLUMNS = [RuleCol.Add, RuleCol.Delete, RuleCol.Active, RuleCol.Inactive, RuleCol.Link, RuleCol.File, RuleCol.Email]



# ################################ LmEvents class ################################
class LmEvents:

	### Create events tab
	def createEventsTab(self):
		self._eventsTab = QtWidgets.QWidget(objectName = TAB_NAME)

		# Device list
		self._eventDList = LmTableWidget(objectName = 'eventDList')
		self._eventDList.set_columns({DSelCol.Key: ['Key', 0, None],
									  DSelCol.Name: [lx('Name'), 200, 'dlist_Name'],
									  DSelCol.MAC: [lx('MAC'), 120, 'dlist_MAC']})
		self._eventDList.set_header_resize([DSelCol.MAC])
		self._eventDList.set_standard_setup(self)
		self._eventDList.setMinimumWidth(350)
		self._eventDList.itemSelectionChanged.connect(self.eventDeviceListClick)

		# Event list
		self._eventList = LmTableWidget(objectName = 'eventList')
		self._eventList.set_columns({EventCol.Key: ['Key', 0, None],
									 EventCol.Time: [lx('Time'), 80, 'elist_Time'],
									 EventCol.Reason: [lx('Reason'), 150, 'elist_Reason'],
									 EventCol.Attribute: [lx('Attributes'), 600, 'elist_Attribute']})
		self._eventList.set_header_resize([EventCol.Attribute])
		self._eventList.set_standard_setup(self)
		self._eventList.doubleClicked.connect(self.displayEventButtonClick)

		# Lists layout
		aListBox = QtWidgets.QHBoxLayout()
		aListBox.setSpacing(10)
		aListBox.addWidget(self._eventDList, 0)
		aListBox.addWidget(self._eventList, 1)

		# Button bar
		aButtonsBox = QtWidgets.QHBoxLayout()
		aButtonsBox.setSpacing(30)
		aNotificationsButton = QtWidgets.QPushButton(lx('Notifications...'), objectName = 'notifications')
		aNotificationsButton.clicked.connect(self.notificationsButtonClick)
		aButtonsBox.addWidget(aNotificationsButton)
		aDisplayEventButton = QtWidgets.QPushButton(lx('Display Event...'), objectName = 'displayEvent')
		aDisplayEventButton.clicked.connect(self.displayEventButtonClick)
		aButtonsBox.addWidget(aDisplayEventButton)

		# Layout
		aVBox = QtWidgets.QVBoxLayout()
		aVBox.setSpacing(10)
		aVBox.addLayout(aListBox, 0)
		aVBox.addLayout(aButtonsBox, 1)
		self._eventsTab.setLayout(aVBox)

		LmConfig.set_tooltips(self._eventsTab, 'events')
		self._tab_widget.addTab(self._eventsTab, lx('Events'))


	### Init the Livebox event collector thread
	def initEventLoop(self):
		self._last_event_device_key = ''
		self._stats_map = {}
		self._eventBuffer = {}
		self._liveboxEventThread = None
		self._liveboxEventLoop = None
		self._notifyRawEventLog = []
		self._notificationTimer = QtCore.QTimer()
		self._notificationTimer.timeout.connect(self.notifyFlushEvents)


	### Start the Livebox event collector thread
	def startEventLoop(self):
		self._liveboxEventThread = QtCore.QThread()
		self._liveboxEventLoop = LiveboxEventThread(self._session)
		self._liveboxEventLoop.moveToThread(self._liveboxEventThread)
		self._liveboxEventThread.started.connect(self._liveboxEventLoop.run)
		self._liveboxEventLoop._eventReceived.connect(self.processLiveboxEvent)
		self._liveboxEventLoop._resume.connect(self._liveboxEventLoop.resume)
		self._liveboxEventThread.start()
		self.startNotificationTimer()


	### Suspend the Livebox event collector thread
	def suspendEventLoop(self):
		if self._liveboxEventThread is not None:
			self._liveboxEventLoop.stop()
		self.stopNotificationTimer()


	### Resume the Livebox event collector thread
	def resumeEventLoop(self):
		if self._liveboxEventThread is None:
			self.startEventLoop()
		else:
			self._liveboxEventLoop._resume.emit()
		self.startNotificationTimer()


	### Stop the Livebox event collector thread
	def stopEventLoop(self):
		if self._liveboxEventThread is not None:
			self._liveboxEventThread.quit()
			self._liveboxEventThread.wait()
			self._liveboxEventThread = None
			self._liveboxEventLoop = None
		self.stopNotificationTimer()


	### Start the regular notification collector tasks
	def startNotificationTimer(self):
		if LmConf.NotificationRules is not None:
			self._notificationTimer.start(LmConf.NotificationFlushFrequency * 1000)


	### Stop the regular notification collector tasks
	def stopNotificationTimer(self):
		self._notificationTimer.stop()


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


	### Click on notifications button
	def notificationsButtonClick(self):
		aNotificationSetupDialog = NotificationSetupDialog(self)
		if aNotificationSetupDialog.exec():
			LmConf.save()
			self.stopNotificationTimer()
			self.startNotificationTimer()
			if LmEvents.notifyHasEmailRule() and (LmConf.Email is None):
				if LmTools.ask_question(mx('You have configured at least one rule with sending emails as an action but '
										   'you have not configured how to send emails. '
										   'Do you want to configure how to send emails?', 'email')):
					self.emailSetupButtonClick()


	### Click on display event button
	def displayEventButtonClick(self):
		aCurrDeviceSelection = self._eventDList.currentRow()
		if aCurrDeviceSelection < 0:
			self.display_error(mx('Please select a device.', 'devSelect'))
			return

		aDeviceKey = self._eventDList.item(aCurrDeviceSelection, DSelCol.Key).text()

		aCurrEventSelection = self._eventList.currentRow()
		if aCurrEventSelection < 0:
			self.display_error(mx('No event selected.', 'evtSelect'))
			return

		aEventKey = int(self._eventList.item(aCurrEventSelection, EventCol.Key).text())
		aDeviceEventDict = self._eventBuffer.get(aDeviceKey, {})
		aEventArray = aDeviceEventDict.get('Events', [])

		# Retrieve event entry in the array
		e = next((e for e in aEventArray if e['Key'] == aEventKey), None)
		if e is None:
			self.display_error(mx('Event entry not found.', 'evtNotFound'))
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

		self.display_infos(lx('Event Entry'), None, aTextDoc)


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
		aTimeStamp = f'{aTime.hour:02d}:{aTime.minute:02d}:{aTime.second:02d}'
		aTimeItem = QtWidgets.QTableWidgetItem(aTimeStamp)
		aTimeItem.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self._eventList.setItem(iLine, EventCol.Time, aTimeItem)
		self._eventList.setItem(iLine, EventCol.Reason, QtWidgets.QTableWidgetItem(iEvent['Reason']))
		aAttribute = str(iEvent['Attributes'])[0:256]
		aAttributeItem = QtWidgets.QTableWidgetItem(aAttribute)
		aAttributeItem.setData(LmTools.ItemDataRole.ExportRole, iEvent['Attributes'])
		self._eventList.setItem(iLine, EventCol.Attribute, aAttributeItem)


	### Process a new Livebox event
	def processLiveboxEvent(self, iEvent):
		d = iEvent.get('data')
		if d is not None:
			h = d.get('handler', '')
			if h.startswith('Devices'):
				self.processDeviceEvent(d)
			elif h.startswith('HomeLan'):
				self.processHomeLanEvent(d)


	### Process a new Device event
	def processDeviceEvent(self, iEventData):
		h = iEventData.get('handler', '')
		o = iEventData.get('object')
		if o is not None:
			r = o.get('reason', '')
			a = o.get('attributes')
		else:
			r = ''
			a = None

		# Try to guess device key from handler
		aDeviceKey = LmTools.extract_mac_addr_from_string(h)
		if len(aDeviceKey):
			self.update_event_indicator(aDeviceKey)
			if r == 'Statistics':
				e = a.get(aDeviceKey)
				if e is not None:
					self.process_statistics_event(aDeviceKey, e)
					self.bufferizeEvent(aDeviceKey, h, r, e)
				else:
					self.bufferizeEvent(aDeviceKey, h, r, a)
			elif r == 'changed':
				self.process_changed_event(aDeviceKey, h, a)
				self.bufferizeEvent(aDeviceKey, h, r, a)
			elif r == 'device_name_changed':
				e = a.get(aDeviceKey)
				if e is not None:
					self.process_device_name_changed_event(aDeviceKey, e)
					self.bufferizeEvent(aDeviceKey, h, r, e)
				else:
					self.bufferizeEvent(aDeviceKey, h, r, a)
			elif (r == 'device_updated') or (r == 'eth_device_updated') or (r == 'wifi_device_updated'):
				e = a.get(aDeviceKey)
				if e is not None:
					self.process_device_updated_event(aDeviceKey, e)
					self.bufferizeEvent(aDeviceKey, h, r, e)
				else:
					self.bufferizeEvent(aDeviceKey, h, r, a)
			elif r == 'ip_address_added':
				e = a.get(aDeviceKey)
				if e is not None:
					self.process_ip_address_added_event(aDeviceKey, a[aDeviceKey])
					self.bufferizeEvent(aDeviceKey, h, r, a[aDeviceKey])
				else:
					self.bufferizeEvent(aDeviceKey, h, r, a)
			elif (r == 'device_added') or (r == 'eth_device_added') or (r == 'wifi_device_added'):
				e = a.get(aDeviceKey)
				if e is not None:
					self.process_device_added_event(aDeviceKey, a[aDeviceKey])
					self.bufferizeEvent(aDeviceKey, h, r, a[aDeviceKey])
				else:
					self.bufferizeEvent(aDeviceKey, h, r, a)
			elif (r == 'device_deleted') or (r == 'eth_device_deleted') or (r == 'wifi_device_deleted'):
				self.process_device_deleted_event(aDeviceKey)
			else:
				# Check if device is in the list, otherwise put the event in the None list
				if (self.find_device_line(self._eventDList, aDeviceKey) >= 0):
					self.bufferizeEvent(aDeviceKey, h, r, a)
				else:
					self.bufferizeEvent(None, h, r, a)
		else:
			self.bufferizeEvent(None, h, r, a)


	### Process a new HomeLan event
	def processHomeLanEvent(self, iEventData):
		h = iEventData.get('handler', '')
		o = iEventData.get('object')
		if o is not None:
			a = o.get('attributes')
		else:
			return

		if h.startswith('HomeLan.Interface.') and h.endswith('.Stats'):
			aIntf = h[18:-6]
			self.processIntfStatisticsEvent(aIntf, a)


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


	### Notify about a device added event
	def notifyDeviceAddedEvent(self, iMac):
		self.notifyAddRawEvent({ 'Key': iMac, 'Timestamp': datetime.datetime.now(), 'Type': NOTIF_EVENT_TYPE_ADD})


	### Notify about a device deleted event
	def notifyDeviceDeletedEvent(self, iMac):
		self.notifyAddRawEvent({ 'Key': iMac, 'Timestamp': datetime.datetime.now(), 'Type': NOTIF_EVENT_TYPE_DELETE})


	### Notify about a device active event
	def notifyDeviceActiveEvent(self, iMac, iLink):
		self.notifyAddRawEvent({ 'Key': iMac, 'Timestamp': datetime.datetime.now(), 'Type': NOTIF_EVENT_TYPE_ACTIVE,
							     'Link': iLink})


	### Notify about a device inactive event
	def notifyDeviceInactiveEvent(self, iMac):
		self.notifyAddRawEvent({ 'Key': iMac, 'Timestamp': datetime.datetime.now(), 'Type': NOTIF_EVENT_TYPE_INACTIVE})


	### Notify about a device access link change event
	def notifyDeviceAccessLinkEvent(self, iMac, iOldLink, iNewLink):
		self.notifyAddRawEvent({ 'Key': iMac, 'Timestamp': datetime.datetime.now(), 'Type': NOTIF_EVENT_TYPE_LINK_CHANGE,
								 'OldLink': iOldLink, 'NewLink': iNewLink})


	### Add a raw event notification in cache log
	def notifyAddRawEvent(self, iEvent):
		t = iEvent['Type']

		### Debug logs
		if LmTools.get_verbosity() >= 1:
			ts = iEvent['Timestamp'].strftime('%d/%m/%Y - %H:%M:%S')
			k = iEvent['Key']
			if t == NOTIF_EVENT_TYPE_ACTIVE:
				LmTools.log_debug(1, f'RAW EVT = {ts} - {k} DEV {t} -> {iEvent["Link"]}.')
			elif t == NOTIF_EVENT_TYPE_LINK_CHANGE:
				LmTools.log_debug(1, f'RAW EVT = {ts} - {k} DEV {t} -> from {iEvent["OldLink"]} to {iEvent["NewLink"]}.')
			else:
				LmTools.log_debug(1, f'RAW EVT = {ts} - {k} DEV {t}.')

		# If DELETE event look for a recent DELETE event, if too close (duplicates) don't add
		if t == NOTIF_EVENT_TYPE_DELETE:
			if not self.notifyMergeDeleteEvent(iEvent):
				self._notifyRawEventLog.append(iEvent)

		# If ACTIVE event look for a recent INACTIVE event, if too close (micro-cuts) remove both
		elif t == NOTIF_EVENT_TYPE_ACTIVE:
			if not self.notifyMergeActiveEvent(iEvent):
				self._notifyRawEventLog.append(iEvent)

		# If LINK_CHANGE event look for a match with a recent LINK_CHANGE event, if too close (micro-changes) remove both or merge them
		elif t == NOTIF_EVENT_TYPE_LINK_CHANGE:
			if not self.notifyMergeLinkChangeEvent(iEvent):
				self._notifyRawEventLog.append(iEvent)

		# Add any other event straight
		else:
			self._notifyRawEventLog.append(iEvent)


	### Find recent DELETE event matching DELETE event on input, returns true if found
	def notifyMergeDeleteEvent(self, iEvent):
		k = iEvent['Key']
		ts = iEvent['Timestamp']
		for e in reversed(self._notifyRawEventLog):
			ets = e['Timestamp']
			if (ts - ets).total_seconds() > LmConf.NotificationFlushFrequency:
				return False
			if (e['Key'] == k) and (e['Type'] == NOTIF_EVENT_TYPE_DELETE):
				return True
		return False


	### Find and remove a recent INACTIVE event matching ACTIVE event on input, returns true if found
	def notifyMergeActiveEvent(self, iEvent):
		k = iEvent['Key']
		ts = iEvent['Timestamp']
		for e in reversed(self._notifyRawEventLog):
			ets = e['Timestamp']
			if (ts - ets).total_seconds() > LmConf.NotificationFlushFrequency:
				return False
			if (e['Key'] == k) and (e['Type'] == NOTIF_EVENT_TYPE_INACTIVE):
				self._notifyRawEventLog.remove(e)
				return True
		return False


	### Find a matching recent LINK_CHANGE and either remove it or merge it, returns true if no need to add new event
	def notifyMergeLinkChangeEvent(self, ioEvent):
		k = ioEvent['Key']
		ts = ioEvent['Timestamp']
		ol = ioEvent['OldLink']
		nl = ioEvent['NewLink']

		for e in reversed(self._notifyRawEventLog):
			ets = e['Timestamp']
			if (ts - ets).total_seconds() > LmConf.NotificationFlushFrequency:
				# Reach time limit -> Add
				return False
			if (e['Key'] == k) and (e['Type'] == NOTIF_EVENT_TYPE_LINK_CHANGE):
				# Match found
				if (e['OldLink'] == nl):
					# Item old link matches new link -> Merge means cancel both
					self._notifyRawEventLog.remove(e)
					return True
				if (e['NewLink'] == ol):
					# Item new link matches old link -> Remove item, merge old
					ioEvent['OldLink'] = e['OldLink']
					self._notifyRawEventLog.remove(e)
					return False
		# No match -> Add
		return False


	### Flush events in the frequency window, triggering user notifications when matching configured rules
	def notifyFlushEvents(self):
		n = datetime.datetime.now()
		for e in self._notifyRawEventLog:

			# Always keep the most recent events that are within the frequency window
			ets = e['Timestamp']
			if (n - ets).total_seconds() <= LmConf.NotificationFlushFrequency:
				break

			# User notifications matching configured rules
			r = LmEvents.notifyGetMatchingRule(e)
			if isinstance(r, list):
				if NOTIF_EVENT_RULE_FILE in r:
					self.notifyUserFile(e)
				if NOTIF_EVENT_RULE_EMAIL in r:
					self.notifyUserEmail(e)

			self._notifyRawEventLog.remove(e)


	### Generate a user notification for an event in a CSV file
	def notifyUserFile(self, iEvent):
		LmTools.log_debug(1, 'Logging event in file:', str(iEvent))

		k = iEvent['Key']
		n = LmConf.MacAddrTable.get(k, lx('### UNKNOWN ###'))
		ts = iEvent['Timestamp']
		t = iEvent['Type']

		if LmConf.NotificationFilePath is None:
			aPath = LmConf.get_config_directory()
		else:
			aPath = LmConf.NotificationFilePath
		aFileName = f'LiveboxMonitor_Events_{ts.strftime("%Y-%m-%d")}.csv'
		aFilePath = os.path.join(aPath, aFileName)

		try:
			with open(aFilePath, 'a', newline = '') as f:
				# No translation to have CSV file readable on any platform without encoding issue
				# (by default Excel opens CSV files with local charset, not UTF-8)
				aType = NOTIF_EVENT_HUMAN_TYPE[t]

				r = [ts.strftime('%H:%M:%S'), k, n, aType]

				if t == NOTIF_EVENT_TYPE_ACTIVE:
					r.append(iEvent['Link'])
				elif t == NOTIF_EVENT_TYPE_LINK_CHANGE:
					r.append(iEvent['OldLink'])
					r.append(iEvent['NewLink'])

				aCsvWriter = csv.writer(f, dialect = 'excel', delimiter = LmConf.CsvDelimiter)
				aCsvWriter.writerow(r)
		except BaseException as e:
			LmTools.error(f'Cannot log event. Error: {e}')


	### Generate a user notification for an event via configured email
	def notifyUserEmail(self, iEvent):
		LmTools.log_debug(1, 'Emailing event:', str(iEvent))

		c = LmConf.load_email_setup()
		if c is None:
			LmTools.error('No email setup to notify event by email.')
			return

		k = iEvent['Key']
		n = LmConf.MacAddrTable.get(k, lx('### UNKNOWN ###'))
		ts = iEvent['Timestamp']
		t = iEvent['Type']

		aType = lx(NOTIF_EVENT_HUMAN_TYPE[t])
		aSubject = n + ' - ' + aType

		m = lx('Date:') + ' ' + ts.strftime('%d/%m/%Y') + '\n'
		m += lx('Time:') + ' ' + ts.strftime('%H:%M:%S') + '\n'
		m += lx('Device:') + ' ' + n + '\n'
		m += lx('MAC:') + ' ' + k + '\n'
		m += lx('Event:') + ' ' + aType + '\n'

		if t == NOTIF_EVENT_TYPE_ACTIVE:
			m += lx('Access link:') + ' ' + iEvent['Link'] + '\n'
		elif t == NOTIF_EVENT_TYPE_LINK_CHANGE:
			m += lx('Old access link:') + ' ' + iEvent['OldLink'] + '\n'
			m += lx('New access link:') + ' ' + iEvent['NewLink'] + '\n'

		LmTools.async_send_email(c, aSubject, m)


	### Check if a notification event match any configured notification rules
	@staticmethod
	def notifyGetMatchingRule(iEvent):
		rr = []
		t = iEvent['Type']

		# Find a matching general rule for ALL
		for r in LmConf.NotificationRules:
			if r.get('Key') == NOTIF_EVENT_DEVICE_ALL:
				e = r.get('Events')
				if isinstance(e, list) and (t in e):
					rr += r.get('Rules')

		# Find a matching rule for unknown devices in case device is unknown
		k = iEvent['Key']
		n = LmConf.MacAddrTable.get(k)
		if n is None:
			for r in LmConf.NotificationRules:
				if r.get('Key') == NOTIF_EVENT_DEVICE_UNKNOWN:
					e = r.get('Events')
					if isinstance(e, list) and (t in e):
						rr += r.get('Rules')

		# Find a matching specific rule for this device
		for r in LmConf.NotificationRules:
			if r.get('Key') == k:
				e = r.get('Events')
				if isinstance(e, list) and (t in e):
					rr += r.get('Rules')

		return rr


	### Check if a notification rule uses email action, returns True if yes
	@staticmethod
	def notifyHasEmailRule():
		if LmConf.NotificationRules is not None:
			r = next((r for r in LmConf.NotificationRules if NOTIF_EVENT_RULE_EMAIL in r['Rules']), None)
			return r is not None
		return False



# ################################ Notification rules setup dialog ################################
class NotificationSetupDialog(QtWidgets.QDialog):
	DeviceComboSeparatorIndex = 2

	### Constructor
	def __init__(self, iParent = None):
		super(NotificationSetupDialog, self).__init__(iParent)
		self.resize(720, 400)

		self._ruleSelection = -1
		self._ignoreSignal = False
		self._init = True

		# Rule box
		aRuleLayout = QtWidgets.QHBoxLayout()
		aRuleLayout.setSpacing(30)

		aRuleListLayout = QtWidgets.QVBoxLayout()
		aRuleListLayout.setSpacing(5)

		# Device list columns
		self._ruleList = LmTableWidget(objectName = 'ruleList')
		self._ruleList.setHorizontalHeader(CenteredIconHeaderView(self, ICON_COLUMNS))
		self._ruleList.set_columns({RuleCol.Key: [lnx('Device'), 390, 'rlist_Key'],
									RuleCol.Add: [lnx('Added'), 10, 'rlist_Add'],
									RuleCol.Delete: [lnx('Deleted'), 10, 'rlist_Delete'],
									RuleCol.Active: [lnx('Connected'), 10, 'rlist_Active'],
									RuleCol.Inactive: [lnx('Disconnected'), 10, 'rlist_Inactive'],
									RuleCol.Link: [lnx('Link Changed'), 10, 'rlist_Link'],
									RuleCol.File: [lnx('File'), 10, 'rlist_File'],
									RuleCol.Email: [lnx('Email'), 10, 'rlist_Email']})
		self._ruleList.set_header_resize([RuleCol.Key])
		self._ruleList.set_standard_setup(iParent)

		# Assign icon headers - drawn by CenteredIconHeaderView
		aModel = self._ruleList.horizontalHeader().model()
		aModel.setHeaderData(RuleCol.Add, QtCore.Qt.Orientation.Horizontal, QtGui.QIcon(LmIcon.AddCirclePixmap), LmTools.ItemDataRole.IconRole)
		aModel.setHeaderData(RuleCol.Delete, QtCore.Qt.Orientation.Horizontal, QtGui.QIcon(LmIcon.DelCirclePixmap), LmTools.ItemDataRole.IconRole)
		aModel.setHeaderData(RuleCol.Active, QtCore.Qt.Orientation.Horizontal, QtGui.QIcon(LmIcon.ActiveCirclePixmap), LmTools.ItemDataRole.IconRole)
		aModel.setHeaderData(RuleCol.Inactive, QtCore.Qt.Orientation.Horizontal, QtGui.QIcon(LmIcon.InactiveCirclePixmap), LmTools.ItemDataRole.IconRole)
		aModel.setHeaderData(RuleCol.Link, QtCore.Qt.Orientation.Horizontal, QtGui.QIcon(LmIcon.LocChangePixmap), LmTools.ItemDataRole.IconRole)
		aModel.setHeaderData(RuleCol.File, QtCore.Qt.Orientation.Horizontal, QtGui.QIcon(LmIcon.ExcelDocPixmap), LmTools.ItemDataRole.IconRole)
		aModel.setHeaderData(RuleCol.Email, QtCore.Qt.Orientation.Horizontal, QtGui.QIcon(LmIcon.MailSendPixmap), LmTools.ItemDataRole.IconRole)

		self._ruleList.setItemDelegate(CenteredIconsDelegate(self, ICON_COLUMNS))
		self._ruleList.setMinimumWidth(460)
		self._ruleList.itemSelectionChanged.connect(self.ruleListClick)

		aRuleListLayout.addWidget(self._ruleList, 1)

		aRuleButtonBox = QtWidgets.QHBoxLayout()
		aRuleButtonBox.setSpacing(5)

		aAddRuleButton = QtWidgets.QPushButton(lnx('Add'), objectName = 'addRule')
		aAddRuleButton.clicked.connect(self.addRuleButtonClick)
		aRuleButtonBox.addWidget(aAddRuleButton)
		self._delRuleButton = QtWidgets.QPushButton(lnx('Delete'), objectName = 'delRule')
		self._delRuleButton.clicked.connect(self.delRuleButtonClick)
		aRuleButtonBox.addWidget(self._delRuleButton)
		aRuleListLayout.addLayout(aRuleButtonBox, 0)
		aRuleLayout.addLayout(aRuleListLayout, 0)

		aDeviceLabel = QtWidgets.QLabel(lnx('Device'), objectName = 'deviceLabel')
		self._deviceCombo = QtWidgets.QComboBox(objectName = 'deviceCombo')
		self.loadDeviceList()
		self._deviceCombo.addItem(lnx('Any device'))
		self._deviceCombo.addItem(lnx('Any unknown device'))
		self._deviceCombo.insertSeparator(NotificationSetupDialog.DeviceComboSeparatorIndex)
		for d in self._comboDeviceList:
			self._deviceCombo.addItem(d['Name'])
		self._deviceCombo.currentIndexChanged.connect(self.deviceSelected)

		aMacLabel = QtWidgets.QLabel(lnx('MAC address'), objectName = 'macLabel')
		self._macEdit = QtWidgets.QLineEdit(objectName = 'macEdit')
		aMacRegExp = QtCore.QRegularExpression('^' + LmTools.MAC_RS + '$')
		aMacValidator = QtGui.QRegularExpressionValidator(aMacRegExp)
		self._macEdit.setValidator(aMacValidator)
		self._macEdit.textChanged.connect(self.macTyped)

		aEventsLabel = QtWidgets.QLabel(lnx('Events:'), objectName = 'eventsLabel')
		self._addEvent = QtWidgets.QCheckBox(lnx('Device Added'), objectName = 'addEvent')
		self._addEvent.stateChanged.connect(self.addEventChanged)
		self._delEvent = QtWidgets.QCheckBox(lnx('Device Deleted'), objectName = 'delEvent')
		self._delEvent.stateChanged.connect(self.delEventChanged)
		self._actEvent = QtWidgets.QCheckBox(lnx('Device Connected'), objectName = 'actEvent')
		self._actEvent.stateChanged.connect(self.actEventChanged)
		self._inaEvent = QtWidgets.QCheckBox(lnx('Device Disconnected'), objectName = 'inaEvent')
		self._inaEvent.stateChanged.connect(self.inaEventChanged)
		self._lnkEvent = QtWidgets.QCheckBox(lnx('Device Access Link Changed'), objectName = 'lnkEvent')
		self._lnkEvent.stateChanged.connect(self.lnkEventChanged)

		aActionsLabel = QtWidgets.QLabel(lnx('Actions:'), objectName = 'actionsLabel')
		self._fileAction = QtWidgets.QCheckBox(lnx('Log in CSV file'), objectName = 'fileAction')
		self._fileAction.stateChanged.connect(self.fileActionChanged)
		self._emailAction = QtWidgets.QCheckBox(lnx('Send Email'), objectName = 'emailAction')
		self._emailAction.stateChanged.connect(self.emailActionChanged)

		aRuleEditGrid = QtWidgets.QGridLayout()
		aRuleEditGrid.setSpacing(10)
		aRuleEditGrid.addWidget(aDeviceLabel, 0, 0)
		aRuleEditGrid.addWidget(self._deviceCombo, 0, 1, 1, 2)
		aRuleEditGrid.addWidget(aMacLabel, 1, 0)
		aRuleEditGrid.addWidget(self._macEdit, 1, 1, 1, 2)
		aRuleEditGrid.addWidget(aEventsLabel, 2, 0)
		aRuleEditGrid.addWidget(self._addEvent, 2, 1)
		aRuleEditGrid.addWidget(self._delEvent, 2, 2)
		aRuleEditGrid.addWidget(self._actEvent, 3, 1)
		aRuleEditGrid.addWidget(self._inaEvent, 3, 2)
		aRuleEditGrid.addWidget(self._lnkEvent, 4, 1, 1, 2)
		aRuleEditGrid.addWidget(aActionsLabel, 5, 0)
		aRuleEditGrid.addWidget(self._fileAction, 5, 1, 1, 2)
		aRuleEditGrid.addWidget(self._emailAction, 6, 1, 1, 2)

		aRuleLayout.addLayout(aRuleEditGrid, 0)

		aRuleGroupBox = QtWidgets.QGroupBox(lnx('Rules'), objectName = 'ruleGroup')
		aRuleGroupBox.setLayout(aRuleLayout)

		# General preferences box
		aIntValidator = QtGui.QIntValidator()
		aIntValidator.setRange(1, 99)

		aFlushFrequencyLabel = QtWidgets.QLabel(lnx('Event Resolution Frequency'), objectName = 'flushFrequencyLabel')
		self._flushFrequency = QtWidgets.QLineEdit(objectName = 'flushFrequencyEdit')
		self._flushFrequency.setValidator(aIntValidator)
		self._flushFrequency.setMaximumWidth(60)
		aFlushFrequencySecLabel = QtWidgets.QLabel(lnx('seconds'), objectName = 'flushFrequencySecLabel')

		aEventFilePathLabel = QtWidgets.QLabel(lnx('CSV Files Path'), objectName = 'eventFilePathLabel')
		self._eventFilePath = QtWidgets.QLineEdit(objectName = 'eventFilePathEdit')
		self._eventFilePath.textChanged.connect(self.eventFilePathTyped)
		self._eventFilePathSelectButton = QtWidgets.QPushButton(lnx('Select'), objectName = 'eventFilePathSelectButton')
		self._eventFilePathSelectButton.clicked.connect(self.eventFilePathSelectButtonClic)
		self._defaultFilePath = QtWidgets.QCheckBox(lnx('Default'), objectName = 'defaultFilePath')
		self._defaultFilePath.stateChanged.connect(self.defaultFilePathChanged)

		aPrefsEditGrid = QtWidgets.QGridLayout()
		aPrefsEditGrid.setSpacing(10)

		aPrefsEditGrid.addWidget(aFlushFrequencyLabel, 0, 0)
		aPrefsEditGrid.addWidget(self._flushFrequency, 0, 1, 1, 1)
		aPrefsEditGrid.addWidget(aFlushFrequencySecLabel, 0, 2)
		aPrefsEditGrid.addWidget(aEventFilePathLabel, 1, 0)
		aPrefsEditGrid.addWidget(self._eventFilePath, 1, 1, 1, 5)
		aPrefsEditGrid.addWidget(self._eventFilePathSelectButton, 1, 7)
		aPrefsEditGrid.addWidget(self._defaultFilePath, 1, 8)

		aPrefsGroupBox = QtWidgets.QGroupBox(lnx('Preferences'), objectName = 'prefsGroup')
		aPrefsGroupBox.setLayout(aPrefsEditGrid)

		# Button bar
		aButtonBar = QtWidgets.QHBoxLayout()
		self._okButton = QtWidgets.QPushButton(lnx('OK'), objectName = 'ok')
		self._okButton.clicked.connect(self.okButtonClick)
		self._okButton.setDefault(True)
		aButtonBar.addWidget(self._okButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aCancelButton = QtWidgets.QPushButton(lnx('Cancel'), objectName = 'cancel')
		aCancelButton.clicked.connect(self.reject)
		aButtonBar.addWidget(aCancelButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aButtonBar.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aButtonBar.setSpacing(10)

		# Final layout
		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.setSpacing(20)
		aVBox.addWidget(aRuleGroupBox, 1)
		aVBox.addWidget(aPrefsGroupBox, 0)
		aVBox.addLayout(aButtonBar, 0)

		self._flushFrequency.setFocus()

		LmConfig.set_tooltips(self, 'evnrules')

		self.setWindowTitle(lnx('Notification Rules Setup'))
		self.setModal(True)
		self.loadPrefs()
		self.show()

		self._init = False


	### Load preferences data
	def loadPrefs(self):
		self._rules = []

		# Load rule list
		if LmConf.NotificationRules is not None:
			i = 0
			for r in LmConf.NotificationRules:
				self._rules.append(r.copy())
				self._ruleList.insertRow(i)
				self.setRuleRow(i, r)
				i += 1
		self.ruleListClick()

		# Load paramaters
		self._flushFrequency.setText(str(int(LmConf.NotificationFlushFrequency)))
		if LmConf.NotificationFilePath is None:
			self._defaultFilePath.setCheckState(QtCore.Qt.CheckState.Checked)
			self._eventFilePath.setText(LmConf.get_config_directory())
			self._eventFilePath.setDisabled(True)
			self._eventFilePathSelectButton.setDisabled(True)
		else:
			self._defaultFilePath.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._eventFilePath.setText(LmConf.NotificationFilePath)


	### Set a row rule to a rule item
	def setRuleRow(self, iRow, iRule):
		# Set rule device name
		k = iRule['Key']
		if k == NOTIF_EVENT_DEVICE_ALL:
			aName = lnx('Any device')
		elif k == NOTIF_EVENT_DEVICE_UNKNOWN:
		 	aName = lnx('Any unknown device')
		else:
			aName = None
			for d in self._comboDeviceList:
				if d['MAC'] == k:
					aName = d['Name']
					break
			if aName is None:
				aName = k
		self._ruleList.setItem(iRow, RuleCol.Key, QtWidgets.QTableWidgetItem(aName))

		# Set event flags
		e = iRule['Events']
		i = QtWidgets.QTableWidgetItem()
		if NOTIF_EVENT_TYPE_ADD in e:
			i.setIcon(QtGui.QIcon(LmIcon.BlueLightPixmap))
			i.setData(QtCore.Qt.ItemDataRole.UserRole, True)
		self._ruleList.setItem(iRow, RuleCol.Add, i)
		i = QtWidgets.QTableWidgetItem()
		if NOTIF_EVENT_TYPE_DELETE in e:
			i.setIcon(QtGui.QIcon(LmIcon.BlueLightPixmap))
			i.setData(QtCore.Qt.ItemDataRole.UserRole, True)
		self._ruleList.setItem(iRow, RuleCol.Delete, i)
		i = QtWidgets.QTableWidgetItem()
		if NOTIF_EVENT_TYPE_ACTIVE in e:
			i.setIcon(QtGui.QIcon(LmIcon.BlueLightPixmap))
			i.setData(QtCore.Qt.ItemDataRole.UserRole, True)
		self._ruleList.setItem(iRow, RuleCol.Active, i)
		i = QtWidgets.QTableWidgetItem()
		if NOTIF_EVENT_TYPE_INACTIVE in e:
			i.setIcon(QtGui.QIcon(LmIcon.BlueLightPixmap))
			i.setData(QtCore.Qt.ItemDataRole.UserRole, True)
		self._ruleList.setItem(iRow, RuleCol.Inactive, i)
		i = QtWidgets.QTableWidgetItem()
		if NOTIF_EVENT_TYPE_LINK_CHANGE in e:
			i.setIcon(QtGui.QIcon(LmIcon.BlueLightPixmap))
			i.setData(QtCore.Qt.ItemDataRole.UserRole, True)
		self._ruleList.setItem(iRow, RuleCol.Link, i)

		# Set rule action flags
		r = iRule['Rules']
		i = QtWidgets.QTableWidgetItem()
		if NOTIF_EVENT_RULE_FILE in r:
			i.setIcon(QtGui.QIcon(LmIcon.GreenLightPixmap))
			i.setData(QtCore.Qt.ItemDataRole.UserRole, True)
		self._ruleList.setItem(iRow, RuleCol.File, i)
		i = QtWidgets.QTableWidgetItem()
		if NOTIF_EVENT_RULE_EMAIL in r:
			i.setIcon(QtGui.QIcon(LmIcon.GreenLightPixmap))
			i.setData(QtCore.Qt.ItemDataRole.UserRole, True)
		self._ruleList.setItem(iRow, RuleCol.Email, i)


	### Save preferences data
	def savePrefs(self):
		# Save rule data
		if len(self._rules):
			LmConf.NotificationRules = self._rules
		else:
			LmConf.NotificationRules = None

		# Save parameters
		LmConf.NotificationFlushFrequency = int(self._flushFrequency.text())
		if self._defaultFilePath.isChecked():
			LmConf.NotificationFilePath = None
		else:
			LmConf.NotificationFilePath = self._eventFilePath.text()


	### Click on rule list item
	def ruleListClick(self):
		aNewSelection = self._ruleList.currentRow()

		# Check of selection really changed
		if not self._init and self._ruleSelection == aNewSelection:
			return

		# Check if current rule is OK
		if not self.checkRule():
			self._ruleList.selectRow(self._ruleSelection)
			return

		aWithinDialogInit = self._init
		if not aWithinDialogInit:
			self._init = True

		self._ruleSelection = aNewSelection

		# Load new values
		if aNewSelection >= 0:
			self._delRuleButton.setDisabled(False)

			r = self._rules[aNewSelection]

			# Device data
			k = r['Key']
			self._deviceCombo.setDisabled(False)
			if k == NOTIF_EVENT_DEVICE_ALL:
				self._deviceCombo.setCurrentIndex(0)
			elif k == NOTIF_EVENT_DEVICE_UNKNOWN:
				self._deviceCombo.setCurrentIndex(1)
			else:
				self._macEdit.setDisabled(False)
				self._macEdit.setText(k)

			# Event data
			e = r['Events']
			self._addEvent.setDisabled(False)
			if NOTIF_EVENT_TYPE_ADD in e:
				self._addEvent.setCheckState(QtCore.Qt.CheckState.Checked)
			else:
				self._addEvent.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._delEvent.setDisabled(False)
			if NOTIF_EVENT_TYPE_DELETE in e:
				self._delEvent.setCheckState(QtCore.Qt.CheckState.Checked)
			else:
				self._delEvent.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._actEvent.setDisabled(False)
			if NOTIF_EVENT_TYPE_ACTIVE in e:
				self._actEvent.setCheckState(QtCore.Qt.CheckState.Checked)
			else:
				self._actEvent.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._inaEvent.setDisabled(False)
			if NOTIF_EVENT_TYPE_INACTIVE in e:
				self._inaEvent.setCheckState(QtCore.Qt.CheckState.Checked)
			else:
				self._inaEvent.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._lnkEvent.setDisabled(False)
			if NOTIF_EVENT_TYPE_LINK_CHANGE in e:
				self._lnkEvent.setCheckState(QtCore.Qt.CheckState.Checked)
			else:
				self._lnkEvent.setCheckState(QtCore.Qt.CheckState.Unchecked)

			# Set rule action flags
			a = r['Rules']
			self._fileAction.setDisabled(False)
			if NOTIF_EVENT_RULE_FILE in a:
				self._fileAction.setCheckState(QtCore.Qt.CheckState.Checked)
			else:
				self._fileAction.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._emailAction.setDisabled(False)
			if NOTIF_EVENT_RULE_EMAIL in a:
				self._emailAction.setCheckState(QtCore.Qt.CheckState.Checked)
			else:
				self._emailAction.setCheckState(QtCore.Qt.CheckState.Unchecked)
		else:
			self._delRuleButton.setDisabled(True)
			self._deviceCombo.setCurrentIndex(0)
			self._deviceCombo.setDisabled(True)
			self._macEdit.setText('')
			self._macEdit.setDisabled(True)
			self._addEvent.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._addEvent.setDisabled(True)
			self._delEvent.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._delEvent.setDisabled(True)
			self._actEvent.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._actEvent.setDisabled(True)
			self._inaEvent.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._inaEvent.setDisabled(True)
			self._lnkEvent.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._lnkEvent.setDisabled(True)
			self._fileAction.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._fileAction.setDisabled(True)
			self._emailAction.setCheckState(QtCore.Qt.CheckState.Unchecked)
			self._emailAction.setDisabled(True)

		if not aWithinDialogInit:
			self._init = False


	def loadDeviceList(self):
		aDeviceList = self.parent().get_device_list()
		self._comboDeviceList = []

		# Load from MacAddrTable file
		for d in LmConf.MacAddrTable:
			aDevice = {}
			aDevice['Name'] = LmConf.MacAddrTable[d]
			aDevice['MAC'] = d
			self._comboDeviceList.append(aDevice)

		# Load from device list if not already loaded
		for d in aDeviceList:
			if (len(d['MAC'])) and (not any(e['MAC'] == d['MAC'] for e in self._comboDeviceList)):
				aDevice = {}
				aDevice['Name'] = d['LBName']
				aDevice['MAC'] = d['MAC']
				self._comboDeviceList.append(aDevice)

		# Sort by name
		self._comboDeviceList = sorted(self._comboDeviceList, key = lambda x: x['Name'])

		# Insert unknown device at the beginning
		aDevice = {}
		aDevice['Name'] = lnx('-Unknown-')
		aDevice['MAC'] = ''
		self._comboDeviceList.insert(0, aDevice)


	def deviceSelected(self, iIndex):
		if not self._ignoreSignal:
			if iIndex == 0:
				self._ignoreSignal = True
				self._macEdit.setText('')
				self._ignoreSignal = False
				self._macEdit.setDisabled(True)
			elif iIndex == 1:
				self._ignoreSignal = True
				self._macEdit.setText('')
				self._ignoreSignal = False
				self._macEdit.setDisabled(True)
			elif iIndex > NotificationSetupDialog.DeviceComboSeparatorIndex:
				self._macEdit.setDisabled(False)
				self._ignoreSignal = True
				self._macEdit.setText(self._comboDeviceList[iIndex - (NotificationSetupDialog.DeviceComboSeparatorIndex + 1)]['MAC'])
				self._ignoreSignal = False

			if not self._init:
				self.saveRule()


	def macTyped(self, iMac):
		if not self._ignoreSignal:
			self._ignoreSignal = True

			aIndex = 0
			i = 0
			for d in self._comboDeviceList:
				if d['MAC'] == iMac:
					aIndex = i
					break
				i += 1

			self._deviceCombo.setCurrentIndex(aIndex + (NotificationSetupDialog.DeviceComboSeparatorIndex + 1))
			self._ignoreSignal = False

			if not self._init:
				self.saveRule()


	### Add event checkbox option changed
	def addEventChanged(self, iState):
		self.eventOptionChanged(self._addEvent)


	### Delete event checkbox option changed
	def delEventChanged(self, iState):
		self.eventOptionChanged(self._delEvent)


	### Active event checkbox option changed
	def actEventChanged(self, iState):
		self.eventOptionChanged(self._actEvent)


	### Inactive event checkbox option changed
	def inaEventChanged(self, iState):
		self.eventOptionChanged(self._inaEvent)


	### Link change event checkbox option changed
	def lnkEventChanged(self, iState):
		self.eventOptionChanged(self._lnkEvent)


	### An event checkbox option changed
	def eventOptionChanged(self, iCheckbox):
		if not self._init:
			# Check if at least one event is checked
			if (not self._addEvent.isChecked() and
				not self._delEvent.isChecked() and
				not self._actEvent.isChecked() and
				not self._inaEvent.isChecked() and
				not self._lnkEvent.isChecked()):
				self._init = True
				iCheckbox.setCheckState(QtCore.Qt.CheckState.Checked)
				self._init = False
			else:
				self.saveRule()


	### File action checkbox option changed
	def fileActionChanged(self, iState):
		self.actionOptionChanged(self._fileAction)


	### Email action checkbox option changed
	def emailActionChanged(self, iState):
		self.actionOptionChanged(self._emailAction)


	### An action checkbox option changed
	def actionOptionChanged(self, iCheckbox):
		if not self._init:
			# Check if at least one action is checked
			if (not self._fileAction.isChecked() and
				not self._emailAction.isChecked()):
				self._init = True
				iCheckbox.setCheckState(QtCore.Qt.CheckState.Checked)
				self._init = False
			else:
				self.saveRule()


	### Notification event file path changed
	def eventFilePathTyped(self, iPath):
		self._okButton.setDisabled(len(iPath) == 0)


	### Check if current rule is OK, returns True if yes
	def checkRule(self):
		if self._ruleSelection >= 0:
			r = self._rules[self._ruleSelection]
			k = r['Key']
			if k != NOTIF_EVENT_DEVICE_ALL and k != NOTIF_EVENT_DEVICE_UNKNOWN:
				m = self._macEdit.text()
				if not LmTools.is_mac_addr(m):
						self.parent().display_error(mx('{} is not a valid MAC address.', 'macErr').format(m))
						self._macEdit.setFocus()
						return False
		return True


	### Save current rule in rules buffer
	def saveRule(self):
		r = self._rules[self._ruleSelection]

		# Key
		i = self._deviceCombo.currentIndex()
		if i == 0:
			r['Key'] = NOTIF_EVENT_DEVICE_ALL
		elif i == 1:
			r['Key'] = NOTIF_EVENT_DEVICE_UNKNOWN
		else:
			aMac = self._macEdit.text()
			if not len(aMac):
				r['Key'] = NOTIF_EVENT_DEVICE_UNKNOWN
			else:
				r['Key'] = self._macEdit.text()

		# Events
		e = []
		if self._addEvent.isChecked():
			e.append(NOTIF_EVENT_TYPE_ADD)
		if self._delEvent.isChecked():
			e.append(NOTIF_EVENT_TYPE_DELETE)
		if self._actEvent.isChecked():
			e.append(NOTIF_EVENT_TYPE_ACTIVE)
		if self._inaEvent.isChecked():
			e.append(NOTIF_EVENT_TYPE_INACTIVE)
		if self._lnkEvent.isChecked():
			e.append(NOTIF_EVENT_TYPE_LINK_CHANGE)
		r['Events'] = e

		# Rule action flags
		a = []
		if self._fileAction.isChecked():
			a.append(NOTIF_EVENT_RULE_FILE)
		if self._emailAction.isChecked():
			a.append(NOTIF_EVENT_RULE_EMAIL)
		r['Rules'] = a

		# Display rule
		self.setRuleRow(self._ruleSelection, r)


	### Click on add rule button
	def addRuleButtonClick(self):
		# Add new default rule in buffer
		r = {}
		r['Key'] = NOTIF_EVENT_DEVICE_ALL
		r['Events'] = [ NOTIF_EVENT_TYPE_ACTIVE, NOTIF_EVENT_TYPE_INACTIVE]
		r['Rules'] = [ NOTIF_EVENT_RULE_FILE ]
		self._rules.append(r)

		# Add new item in list and select it
		i = self._ruleList.rowCount()
		self._ruleList.insertRow(i)
		self.setRuleRow(i, r)
		self._ruleList.selectRow(i)


	### Click on delete rule button
	def delRuleButtonClick(self):
		i = self._ruleSelection

		# Delete the list line
		self._ruleSelection = -1
		self._init = True
		self._ruleList.removeRow(i)
		self._init = False

		# Remove the rule from rules buffer
		self._rules.pop(i)

		# Update selection
		self._ruleSelection = self._ruleList.currentRow()


	### Select event file path button click
	def eventFilePathSelectButtonClic(self):
		aFolder = QtWidgets.QFileDialog.getExistingDirectory(self, lnx('Select Folder'))
		if len(aFolder):
			aFolder = QtCore.QDir.toNativeSeparators(aFolder)
			self._eventFilePath.setText(aFolder)


	### Default file path checkbox changed
	def defaultFilePathChanged(self, iState):
		if not self._init:
			if self._defaultFilePath.isChecked():
				self._eventFilePath.setText(LmConf.get_config_directory())
				self._eventFilePath.setDisabled(True)
				self._eventFilePathSelectButton.setDisabled(True)
			else:
				if LmConf.NotificationFilePath is None:
					self._eventFilePath.setText(LmConf.get_config_directory())
				else:
					self._eventFilePath.setText(LmConf.NotificationFilePath)
				self._eventFilePath.setDisabled(False)
				self._eventFilePathSelectButton.setDisabled(False)


	### Check if file path is OK, return True if yes
	def checkFilePath(self):
		if self._defaultFilePath.isChecked():
			return True

		# Create directory if doesn't exist
		p = self._eventFilePath.text()
		if not os.path.isdir(p):
			if LmTools.ask_question(mx('Configured log file directory does not exist. Do you want to create it?', 'logDirExist')):
				try:
					os.makedirs(p)
				except BaseException as e:
					LmTools.error(f'Cannot create log file directory. Error: {e}')
					LmTools.display_error(mx('Cannot create log file directory.\nError: {}.', 'logDirErr').format(e))
					return False
			else:
				return False
		return True


	### Click on OK button
	def okButtonClick(self):
		# Accept only if current rule & file path are OK
		if self.checkRule() and self.checkFilePath():
			self.savePrefs()
			self.accept()



# ############# Livebox events collector thread #############
class LiveboxEventThread(QtCore.QObject):
	_eventReceived = QtCore.pyqtSignal(dict)
	_resume = QtCore.pyqtSignal()

	def __init__(self, iSession):
		super(LiveboxEventThread, self).__init__()
		self._session = iSession
		self._timer = None
		self._loop = None
		self._isRunning = False


	def run(self):
		self._timer = QtCore.QTimer()
		self._timer.timeout.connect(self.collectEvents)
		self._loop = QtCore.QEventLoop()
		self.resume()


	def resume(self):
		if not self._isRunning:
			self._timer.start(0)
			self._isRunning = True
			self._loop.exec()
			self._timer.stop()
			self._isRunning = False


	def stop(self):
		if self._isRunning:
			self._loop.exit()


	def collectEvents(self):
		aResult = self._session.event_request(['Devices.Device', 'HomeLan'], timeout=2)
		if aResult is not None:
			if aResult.get('errors') is not None:
				# Session has probably timed out on Livebox side, resign
				LmTools.log_debug(1, 'Errors in event request, resign')
				if self._session.signin(LmConf.LiveboxUser, LmConf.LiveboxPassword) <= 0:
					time.sleep(1)  # Avoid looping too quickly in case LB is unreachable
			else:
				aEvents = aResult.get('events')
				if aEvents is not None:
					for e in aEvents:
						self._eventReceived.emit(e)


