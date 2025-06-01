### Livebox Monitor events tab module ###

import os
import json
import datetime
import time
import csv

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig, LmNotif
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmTableWidget import LmTableWidget
from LiveboxMonitor.tabs.LmDeviceListTab import DSelCol
from LiveboxMonitor.dlg.LmNotificationSetup import NotificationSetupDialog
from LiveboxMonitor.lang.LmLanguages import get_events_label as lx, get_events_message as mx


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'eventsTab'

# Static Config
MAX_EVENT_BUFFER_PER_DEVICE = 100

# List columns
class EventCol(IntEnum):
    Key = 0
    Time = 1
    Reason = 2
    Attribute = 3


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
        self._liveboxEventLoop = None
        self._notifyRawEventLog = []
        self._notificationTimer = QtCore.QTimer()
        self._notificationTimer.timeout.connect(self.notifyFlushEvents)


    ### Start the Livebox event collector thread
    def startEventLoop(self):
        self._liveboxEventLoop = LiveboxEventThread(self._api)
        self._liveboxEventLoop.connect_processor(self.processLiveboxEvent)
        self.startNotificationTimer()


    ### Suspend the Livebox event collector thread
    def suspendEventLoop(self):
        if self._liveboxEventLoop is not None:
            self._liveboxEventLoop.stop()
        self.stopNotificationTimer()


    ### Resume the Livebox event collector thread
    def resumeEventLoop(self):
        if self._liveboxEventLoop is None:
            self.startEventLoop()
        else:
            self._liveboxEventLoop._resume.emit()
        self.startNotificationTimer()


    ### Stop the Livebox event collector thread
    def stopEventLoop(self):
        if self._liveboxEventLoop is not None:
            self._liveboxEventLoop.quit()
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
        dialog = NotificationSetupDialog(self)
        if dialog.exec():
            LmConf.save()
            self.stopNotificationTimer()
            self.startNotificationTimer()
            if LmEvents.notifyHasEmailRule() and (LmConf.Email is None):
                if LmTools.ask_question(mx('You have configured at least one rule with sending emails as an action but '
                                           'you have not configured how to send emails. '
                                           'Do you want to configure how to send emails?', 'email')):
                    self.email_setup_button_click()


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
        self.notifyAddRawEvent({ 'Key': iMac, 'Timestamp': datetime.datetime.now(), 'Type': LmNotif.TYPE_ADD})


    ### Notify about a device deleted event
    def notifyDeviceDeletedEvent(self, iMac):
        self.notifyAddRawEvent({ 'Key': iMac, 'Timestamp': datetime.datetime.now(), 'Type': LmNotif.TYPE_DELETE})


    ### Notify about a device active event
    def notifyDeviceActiveEvent(self, iMac, iLink):
        self.notifyAddRawEvent({ 'Key': iMac, 'Timestamp': datetime.datetime.now(), 'Type': LmNotif.TYPE_ACTIVE,
                                 'Link': iLink})


    ### Notify about a device inactive event
    def notifyDeviceInactiveEvent(self, iMac):
        self.notifyAddRawEvent({ 'Key': iMac, 'Timestamp': datetime.datetime.now(), 'Type': LmNotif.TYPE_INACTIVE})


    ### Notify about a device access link change event
    def notifyDeviceAccessLinkEvent(self, iMac, iOldLink, iNewLink):
        self.notifyAddRawEvent({ 'Key': iMac, 'Timestamp': datetime.datetime.now(), 'Type': LmNotif.TYPE_LINK_CHANGE,
                                 'OldLink': iOldLink, 'NewLink': iNewLink})


    ### Add a raw event notification in cache log
    def notifyAddRawEvent(self, iEvent):
        t = iEvent['Type']

        ### Debug logs
        if LmTools.get_verbosity() >= 1:
            ts = iEvent['Timestamp'].strftime('%d/%m/%Y - %H:%M:%S')
            k = iEvent['Key']
            if t == LmNotif.TYPE_ACTIVE:
                LmTools.log_debug(1, f'RAW EVT = {ts} - {k} DEV {t} -> {iEvent["Link"]}.')
            elif t == LmNotif.TYPE_LINK_CHANGE:
                LmTools.log_debug(1, f'RAW EVT = {ts} - {k} DEV {t} -> from {iEvent["OldLink"]} to {iEvent["NewLink"]}.')
            else:
                LmTools.log_debug(1, f'RAW EVT = {ts} - {k} DEV {t}.')

        # If DELETE event look for a recent DELETE event, if too close (duplicates) don't add
        if t == LmNotif.TYPE_DELETE:
            if not self.notifyMergeDeleteEvent(iEvent):
                self._notifyRawEventLog.append(iEvent)

        # If ACTIVE event look for a recent INACTIVE event, if too close (micro-cuts) remove both
        elif t == LmNotif.TYPE_ACTIVE:
            if not self.notifyMergeActiveEvent(iEvent):
                self._notifyRawEventLog.append(iEvent)

        # If LINK_CHANGE event look for a match with a recent LINK_CHANGE event, if too close (micro-changes) remove both or merge them
        elif t == LmNotif.TYPE_LINK_CHANGE:
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
            if (e['Key'] == k) and (e['Type'] == LmNotif.TYPE_DELETE):
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
            if (e['Key'] == k) and (e['Type'] == LmNotif.TYPE_INACTIVE):
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
            if (e['Key'] == k) and (e['Type'] == LmNotif.TYPE_LINK_CHANGE):
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
                if LmNotif.RULE_FILE in r:
                    self.notifyUserFile(e)
                if LmNotif.RULE_EMAIL in r:
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
                aType = LmNotif.HUMAN_TYPE[t]

                r = [ts.strftime('%H:%M:%S'), k, n, aType]

                if t == LmNotif.TYPE_ACTIVE:
                    r.append(iEvent['Link'])
                elif t == LmNotif.TYPE_LINK_CHANGE:
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

        aType = lx(LmNotif.HUMAN_TYPE[t])
        aSubject = n + ' - ' + aType

        m = lx('Date:') + ' ' + ts.strftime('%d/%m/%Y') + '\n'
        m += lx('Time:') + ' ' + ts.strftime('%H:%M:%S') + '\n'
        m += lx('Device:') + ' ' + n + '\n'
        m += lx('MAC:') + ' ' + k + '\n'
        m += lx('Event:') + ' ' + aType + '\n'

        if t == LmNotif.TYPE_ACTIVE:
            m += lx('Access link:') + ' ' + iEvent['Link'] + '\n'
        elif t == LmNotif.TYPE_LINK_CHANGE:
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
            if r.get('Key') == LmNotif.DEVICE_ALL:
                e = r.get('Events')
                if isinstance(e, list) and (t in e):
                    rr += r.get('Rules')

        # Find a matching rule for unknown devices in case device is unknown
        k = iEvent['Key']
        n = LmConf.MacAddrTable.get(k)
        if n is None:
            for r in LmConf.NotificationRules:
                if r.get('Key') == LmNotif.DEVICE_UNKNOWN:
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
            r = next((r for r in LmConf.NotificationRules if LmNotif.RULE_EMAIL in r['Rules']), None)
            return r is not None
        return False



# ############# Livebox events collector thread #############
class LiveboxEventThread(QtCore.QObject):
    _event_received = QtCore.pyqtSignal(dict)
    _resume = QtCore.pyqtSignal()

    def __init__(self, api):
        super(LiveboxEventThread, self).__init__()
        self._session = api._session
        self._timer = None
        self._loop = None
        self._is_running = False
        self._thread = QtCore.QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self.run)
        self._resume.connect(self.resume)
        self._thread.start()


    def connect_processor(self, processor):
        self._event_received.connect(processor)


    def run(self):
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self.collect_events)
        self._loop = QtCore.QEventLoop()
        self.resume()


    def resume(self):
        if not self._is_running:
            self._timer.start(0)
            self._is_running = True
            self._loop.exec()
            self._timer.stop()
            self._is_running = False


    def stop(self):
        if self._is_running:
            self._loop.exit()


    def quit(self):
        self._thread.quit()
        self._thread.wait()
        self._thread = None


    def collect_events(self):
        d = self._session.event_request(['Devices.Device', 'HomeLan'], timeout=2)
        if d:
            if d.get('errors'):
                # Session has probably timed out on Livebox side, resign
                LmTools.log_debug(1, 'Errors in event request, resign')
                if self._session.signin(LmConf.LiveboxUser, LmConf.LiveboxPassword) <= 0:
                    time.sleep(1)  # Avoid looping too quickly in case LB is unreachable
            else:
                events = d.get('events')
                if events:
                    for e in events:
                        self._event_received.emit(e)
