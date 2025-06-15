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
from LiveboxMonitor.app.LmThread import LmThread
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
    def create_events_tab(self):
        self._events_tab = QtWidgets.QWidget(objectName=TAB_NAME)

        # Device list
        self._event_dlist = LmTableWidget(objectName='eventDList')
        self._event_dlist.set_columns({DSelCol.Key: ['Key', 0, None],
                                       DSelCol.Name: [lx('Name'), 200, 'dlist_Name'],
                                       DSelCol.MAC: [lx('MAC'), 120, 'dlist_MAC']})
        self._event_dlist.set_header_resize([DSelCol.MAC])
        self._event_dlist.set_standard_setup(self)
        self._event_dlist.setMinimumWidth(350)
        self._event_dlist.itemSelectionChanged.connect(self.event_device_list_click)

        # Event list
        self._event_list = LmTableWidget(objectName='eventList')
        self._event_list.set_columns({EventCol.Key: ['Key', 0, None],
                                      EventCol.Time: [lx('Time'), 80, 'elist_Time'],
                                      EventCol.Reason: [lx('Reason'), 150, 'elist_Reason'],
                                      EventCol.Attribute: [lx('Attributes'), 600, 'elist_Attribute']})
        self._event_list.set_header_resize([EventCol.Attribute])
        self._event_list.set_standard_setup(self)
        self._event_list.doubleClicked.connect(self.display_event_button_click)

        # Lists layout
        list_box = QtWidgets.QHBoxLayout()
        list_box.setSpacing(10)
        list_box.addWidget(self._event_dlist, 0)
        list_box.addWidget(self._event_list, 1)

        # Button bar
        buttons_box = QtWidgets.QHBoxLayout()
        buttons_box.setSpacing(30)
        notifications_button = QtWidgets.QPushButton(lx('Notifications...'), objectName='notifications')
        notifications_button.clicked.connect(self.notifications_button_click)
        buttons_box.addWidget(notifications_button)
        display_event_button = QtWidgets.QPushButton(lx('Display Event...'), objectName='displayEvent')
        display_event_button.clicked.connect(self.display_event_button_click)
        buttons_box.addWidget(display_event_button)

        # Layout
        vbox = QtWidgets.QVBoxLayout()
        vbox.setSpacing(10)
        vbox.addLayout(list_box, 0)
        vbox.addLayout(buttons_box, 1)
        self._events_tab.setLayout(vbox)

        LmConfig.set_tooltips(self._events_tab, 'events')
        self._tab_widget.addTab(self._events_tab, lx('Events'))


    ### Init the Livebox event collector thread
    def init_event_loop(self):
        self._last_event_device_key = ''
        self._stats_map = {}
        self._event_buffer = {}
        self._livebox_event_loop = None
        self._notify_raw_event_log = []
        self._notification_timer = QtCore.QTimer()
        self._notification_timer.timeout.connect(self.notify_flush_events)


    ### Start the Livebox event collector thread
    def start_event_loop(self):
        self._livebox_event_loop = LiveboxEventThread(self._api)
        self._livebox_event_loop.connect_processor(self.process_livebox_event)
        self.start_notification_timer()


    ### Suspend the Livebox event collector thread
    def suspend_event_loop(self):
        if self._livebox_event_loop is not None:
            self._livebox_event_loop.stop()
        self.stop_notification_timer()


    ### Resume the Livebox event collector thread
    def resumeEventLoop(self):
        if self._livebox_event_loop is None:
            self.start_event_loop()
        else:
            self._livebox_event_loop._resume.emit()
        self.start_notification_timer()


    ### Stop the Livebox event collector thread
    def stop_event_loop(self):
        if self._livebox_event_loop is not None:
            self._livebox_event_loop.quit()
            self._livebox_event_loop = None
        self.stop_notification_timer()


    ### Start the regular notification collector tasks
    def start_notification_timer(self):
        if LmConf.NotificationRules is not None:
            self._notification_timer.start(LmConf.NotificationFlushFrequency * 1000)


    ### Stop the regular notification collector tasks
    def stop_notification_timer(self):
        self._notification_timer.stop()


    ### Click on event device list
    def event_device_list_click(self):
        self._event_list.clearContents()
        self._event_list.setRowCount(0)

        current_selection = self._event_dlist.currentRow()
        if current_selection >= 0:
            aKey = self._event_dlist.item(current_selection, DSelCol.Key).text()
            self._event_list.setSortingEnabled(False)
            self.update_event_list(aKey)
            self._event_list.setSortingEnabled(True)


    ### Click on notifications button
    def notifications_button_click(self):
        dialog = NotificationSetupDialog(self)
        if dialog.exec():
            LmConf.save()
            self.stop_notification_timer()
            self.start_notification_timer()
            if LmEvents.notify_has_email_rule() and (LmConf.Email is None):
                if LmTools.ask_question(mx('You have configured at least one rule with sending emails as an action but '
                                           'you have not configured how to send emails. '
                                           'Do you want to configure how to send emails?', 'email')):
                    self.email_setup_button_click()


    ### Click on display event button
    def display_event_button_click(self):
        curr_device_selection = self._event_dlist.currentRow()
        if curr_device_selection < 0:
            self.display_error(mx('Please select a device.', 'devSelect'))
            return

        device_key = self._event_dlist.item(curr_device_selection, DSelCol.Key).text()

        curr_event_selection = self._event_list.currentRow()
        if curr_event_selection < 0:
            self.display_error(mx('No event selected.', 'evtSelect'))
            return

        event_key = int(self._event_list.item(curr_event_selection, EventCol.Key).text())
        device_event_dict = self._event_buffer.get(device_key, {})
        event_array = device_event_dict.get('Events', [])

        # Retrieve event entry in the array
        e = next((e for e in event_array if e['Key'] == event_key), None)
        if e is None:
            self.display_error(mx('Event entry not found.', 'evtNotFound'))
            return

        # Display event entry
        text_doc = QtGui.QTextDocument()
        standard_font = QtGui.QFont('Courier New', 9)
        bold_font = QtGui.QFont('Tahoma', 9, QtGui.QFont.Weight.Bold)
        text_doc.setDefaultFont(standard_font)
        standard_format = QtGui.QTextCharFormat()
        standard_format.setFont(standard_font)
        bold_format = QtGui.QTextCharFormat()
        bold_format.setFont(bold_font)

        cursor = QtGui.QTextCursor(text_doc)
        cursor.beginEditBlock()
        cursor.insertText('Raised: ', bold_format)
        cursor.insertText(str(e['Timestamp']) + '\n', standard_format)
        cursor.insertText('Handler: ', bold_format)
        cursor.insertText(e['Handler'] + '\n', standard_format)
        cursor.insertText('Reason: ', bold_format)
        cursor.insertText(e['Reason'] + '\n\n', standard_format)
        cursor.insertText('Attributes:\n', bold_format)
        cursor.insertText(json.dumps(e['Attributes'], indent=2), standard_format)
        cursor.endEditBlock()

        self.display_infos(lx('Event Entry'), None, text_doc)


    ### Update event list
    def update_event_list(self, device_key):
        device_event_dict = self._event_buffer.get(device_key, {})
        event_array = device_event_dict.get('Events', [])
        for i, e in enumerate(event_array):
            self._event_list.insertRow(i)
            self.set_event_list_line(i, e)


    ### Set event list line
    def set_event_list_line(self, line, event):
        self._event_list.setItem(line, EventCol.Key, QtWidgets.QTableWidgetItem(str(event['Key'])))
        time = event['Timestamp']
        time_stamp = f'{time.hour:02d}:{time.minute:02d}:{time.second:02d}'
        time_item = QtWidgets.QTableWidgetItem(time_stamp)
        time_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self._event_list.setItem(line, EventCol.Time, time_item)
        self._event_list.setItem(line, EventCol.Reason, QtWidgets.QTableWidgetItem(event['Reason']))
        attribute = str(event['Attributes'])[0:256]
        attribute_item = QtWidgets.QTableWidgetItem(attribute)
        attribute_item.setData(LmTools.ItemDataRole.ExportRole, event['Attributes'])
        self._event_list.setItem(line, EventCol.Attribute, attribute_item)


    ### Process a new Livebox event
    def process_livebox_event(self, event):
        d = event.get('data')
        if d:
            h = d.get('handler', '')
            if h.startswith('Devices'):
                self.process_device_event(d)
            elif h.startswith('HomeLan'):
                self.process_home_lan_event(d)


    ### Process a new Device event
    def process_device_event(self, event_data):
        h = event_data.get('handler', '')
        o = event_data.get('object')
        if o:
            r = o.get('reason', '')
            a = o.get('attributes')
        else:
            r = ''
            a = None

        # Try to guess device key from handler
        device_key = LmTools.extract_mac_addr_from_string(h)
        if len(device_key):
            self.update_event_indicator(device_key)
            if r == 'Statistics':
                e = a.get(device_key)
                if e:
                    self.process_statistics_event(device_key, e)
                    self.bufferize_event(device_key, h, r, e)
                else:
                    self.bufferize_event(device_key, h, r, a)
            elif r == 'changed':
                self.process_changed_event(device_key, h, a)
                self.bufferize_event(device_key, h, r, a)
            elif r == 'device_name_changed':
                e = a.get(device_key)
                if e is not None:
                    self.process_device_name_changed_event(device_key, e)
                    self.bufferize_event(device_key, h, r, e)
                else:
                    self.bufferize_event(device_key, h, r, a)
            elif (r == 'device_updated') or (r == 'eth_device_updated') or (r == 'wifi_device_updated'):
                e = a.get(device_key)
                if e is not None:
                    self.process_device_updated_event(device_key, e)
                    self.bufferize_event(device_key, h, r, e)
                else:
                    self.bufferize_event(device_key, h, r, a)
            elif r == 'ip_address_added':
                e = a.get(device_key)
                if e is not None:
                    self.process_ip_address_added_event(device_key, a[device_key])
                    self.bufferize_event(device_key, h, r, a[device_key])
                else:
                    self.bufferize_event(device_key, h, r, a)
            elif (r == 'device_added') or (r == 'eth_device_added') or (r == 'wifi_device_added'):
                e = a.get(device_key)
                if e is not None:
                    self.process_device_added_event(device_key, a[device_key])
                    self.bufferize_event(device_key, h, r, a[device_key])
                else:
                    self.bufferize_event(device_key, h, r, a)
            elif (r == 'device_deleted') or (r == 'eth_device_deleted') or (r == 'wifi_device_deleted'):
                self.process_device_deleted_event(device_key)
            else:
                # Check if device is in the list, otherwise put the event in the None list
                if (self.find_device_line(self._event_dlist, device_key) >= 0):
                    self.bufferize_event(device_key, h, r, a)
                else:
                    self.bufferize_event(None, h, r, a)
        else:
            self.bufferize_event(None, h, r, a)


    ### Process a new HomeLan event
    def process_home_lan_event(self, event_data):
        h = event_data.get('handler', '')
        o = event_data.get('object')
        if o:
            a = o.get('attributes')
        else:
            return

        if h.startswith('HomeLan.Interface.') and h.endswith('.Stats'):
            intf = h[18:-6]
            self.process_intf_statistics_event(intf, a)


    ### Store event in buffer, for the UI
    def bufferize_event(self, device_key, handler, reason, attributes):
        # Find event dict for the device
        if device_key is None:
            device_key = '#NONE#'
        device_event_dict = self._event_buffer.get(device_key)
        if device_event_dict is None:
            device_event_dict = {}
            device_event_dict['Sequence'] = 1
            device_event_dict['Events'] = []
            self._event_buffer[device_key] = device_event_dict
        device_sequence = device_event_dict['Sequence']
        event_array = device_event_dict['Events']

        # Create event entry
        entry = {'Key': device_sequence,
                 'Timestamp': datetime.datetime.now(),
                 'Handler': handler,
                 'Reason': reason,
                 'Attributes': attributes}

        # Insert front, limit total size and update sequence
        event_array.insert(0, entry)
        if len(event_array) > MAX_EVENT_BUFFER_PER_DEVICE:
            event_array.pop()
        device_event_dict['Sequence'] = device_sequence + 1

        # Update UI if device is selected in event tab
        curr_device_selection = self._event_dlist.currentRow()
        if curr_device_selection >= 0:
            selected_device_key = self._event_dlist.item(curr_device_selection, DSelCol.Key).text()
            if selected_device_key == device_key:
                self._event_list.insertRow(0)
                self.set_event_list_line(0, entry)


    ### Notify about a device added event
    def notify_device_added_event(self, mac):
        self.notify_add_raw_event({'Key': mac, 'Timestamp': datetime.datetime.now(), 'Type': LmNotif.TYPE_ADD})


    ### Notify about a device deleted event
    def notify_device_deleted_event(self, mac):
        self.notify_add_raw_event({'Key': mac, 'Timestamp': datetime.datetime.now(), 'Type': LmNotif.TYPE_DELETE})


    ### Notify about a device active event
    def notify_device_active_event(self, mac, link):
        self.notify_add_raw_event({'Key': mac, 'Timestamp': datetime.datetime.now(), 'Type': LmNotif.TYPE_ACTIVE,
                                   'Link': link})


    ### Notify about a device inactive event
    def notify_device_inactive_event(self, mac):
        self.notify_add_raw_event({'Key': mac, 'Timestamp': datetime.datetime.now(), 'Type': LmNotif.TYPE_INACTIVE})


    ### Notify about a device access link change event
    def notify_device_access_link_event(self, mac, old_link, new_link):
        self.notify_add_raw_event({'Key': mac, 'Timestamp': datetime.datetime.now(), 'Type': LmNotif.TYPE_LINK_CHANGE,
                                   'OldLink': old_link, 'NewLink': new_link})


    ### Add a raw event notification in cache log
    def notify_add_raw_event(self, event):
        t = event['Type']

        ### Debug logs
        if LmTools.get_verbosity() >= 1:
            ts = event['Timestamp'].strftime('%d/%m/%Y - %H:%M:%S')
            k = event['Key']
            if t == LmNotif.TYPE_ACTIVE:
                LmTools.log_debug(1, f'RAW EVT = {ts} - {k} DEV {t} -> {event["Link"]}.')
            elif t == LmNotif.TYPE_LINK_CHANGE:
                LmTools.log_debug(1, f'RAW EVT = {ts} - {k} DEV {t} -> from {event["OldLink"]} to {event["NewLink"]}.')
            else:
                LmTools.log_debug(1, f'RAW EVT = {ts} - {k} DEV {t}.')

        # If DELETE event look for a recent DELETE event, if too close (duplicates) don't add
        match t:
            case LmNotif.TYPE_DELETE:
                if not self.notify_merge_delete_event(event):
                    self._notify_raw_event_log.append(event)

            # If ACTIVE event look for a recent INACTIVE event, if too close (micro-cuts) remove both
            case LmNotif.TYPE_ACTIVE:
                if not self.notify_merge_active_event(event):
                    self._notify_raw_event_log.append(event)

            # If LINK_CHANGE event look for a match with a recent LINK_CHANGE event, if too close (micro-changes) remove both or merge them
            case LmNotif.TYPE_LINK_CHANGE:
                if not self.notify_merge_link_change_event(event):
                    self._notify_raw_event_log.append(event)

            # Add any other event straight
            case _:
                self._notify_raw_event_log.append(event)


    ### Find recent DELETE event matching DELETE event on input, returns true if found
    def notify_merge_delete_event(self, event):
        k = event['Key']
        ts = event['Timestamp']
        for e in reversed(self._notify_raw_event_log):
            ets = e['Timestamp']
            if (ts - ets).total_seconds() > LmConf.NotificationFlushFrequency:
                return False
            if (e['Key'] == k) and (e['Type'] == LmNotif.TYPE_DELETE):
                return True
        return False


    ### Find and remove a recent INACTIVE event matching ACTIVE event on input, returns true if found
    def notify_merge_active_event(self, event):
        k = event['Key']
        ts = event['Timestamp']
        for e in reversed(self._notify_raw_event_log):
            ets = e['Timestamp']
            if (ts - ets).total_seconds() > LmConf.NotificationFlushFrequency:
                return False
            if (e['Key'] == k) and (e['Type'] == LmNotif.TYPE_INACTIVE):
                self._notify_raw_event_log.remove(e)
                return True
        return False


    ### Find a matching recent LINK_CHANGE and either remove it or merge it, returns true if no need to add new event
    def notify_merge_link_change_event(self, event):
        k = event['Key']
        ts = event['Timestamp']
        ol = event['OldLink']
        nl = event['NewLink']

        for e in reversed(self._notify_raw_event_log):
            ets = e['Timestamp']
            if (ts - ets).total_seconds() > LmConf.NotificationFlushFrequency:
                # Reach time limit -> Add
                return False
            if (e['Key'] == k) and (e['Type'] == LmNotif.TYPE_LINK_CHANGE):
                # Match found
                if (e['OldLink'] == nl):
                    # Item old link matches new link -> Merge means cancel both
                    self._notify_raw_event_log.remove(e)
                    return True
                if (e['NewLink'] == ol):
                    # Item new link matches old link -> Remove item, merge old
                    event['OldLink'] = e['OldLink']
                    self._notify_raw_event_log.remove(e)
                    return False
        # No match -> Add
        return False


    ### Flush events in the frequency window, triggering user notifications when matching configured rules
    def notify_flush_events(self):
        n = datetime.datetime.now()
        for e in self._notify_raw_event_log:

            # Always keep the most recent events that are within the frequency window
            ets = e['Timestamp']
            if (n - ets).total_seconds() <= LmConf.NotificationFlushFrequency:
                break

            # User notifications matching configured rules
            r = LmEvents.notify_get_matching_rule(e)
            if isinstance(r, list):
                if LmNotif.RULE_FILE in r:
                    self.notify_user_file(e)
                if LmNotif.RULE_EMAIL in r:
                    self.notify_user_email(e)

            self._notify_raw_event_log.remove(e)


    ### Generate a user notification for an event in a CSV file
    def notify_user_file(self, event):
        LmTools.log_debug(1, 'Logging event in file:', str(event))

        k = event['Key']
        n = LmConf.MacAddrTable.get(k, lx('### UNKNOWN ###'))
        ts = event['Timestamp']
        t = event['Type']

        if LmConf.NotificationFilePath is None:
            path = LmConf.get_config_directory()
        else:
            path = LmConf.NotificationFilePath
        file_name = f'LiveboxMonitor_Events_{ts.strftime("%Y-%m-%d")}.csv'
        file_path = os.path.join(path, file_name)

        try:
            with open(file_path, 'a', newline = '') as f:
                # No translation to have CSV file readable on any platform without encoding issue
                # (by default Excel opens CSV files with local charset, not UTF-8)
                type = LmNotif.HUMAN_TYPE[t]

                r = [ts.strftime('%H:%M:%S'), k, n, type]

                if t == LmNotif.TYPE_ACTIVE:
                    r.append(event['Link'])
                elif t == LmNotif.TYPE_LINK_CHANGE:
                    r.append(event['OldLink'])
                    r.append(event['NewLink'])

                csv_writer = csv.writer(f, dialect = 'excel', delimiter = LmConf.CsvDelimiter)
                csv_writer.writerow(r)
        except Exception as e:
            LmTools.error(f'Cannot log event. Error: {e}')


    ### Generate a user notification for an event via configured email
    def notify_user_email(self, event):
        LmTools.log_debug(1, 'Emailing event:', str(event))

        c = LmConf.load_email_setup()
        if c is None:
            LmTools.error('No email setup to notify event by email.')
            return

        k = event['Key']
        n = LmConf.MacAddrTable.get(k, lx('### UNKNOWN ###'))
        ts = event['Timestamp']
        t = event['Type']

        type = lx(LmNotif.HUMAN_TYPE[t])
        subject = n + ' - ' + type

        m = lx('Date:') + ' ' + ts.strftime('%d/%m/%Y') + '\n'
        m += lx('Time:') + ' ' + ts.strftime('%H:%M:%S') + '\n'
        m += lx('Device:') + ' ' + n + '\n'
        m += lx('MAC:') + ' ' + k + '\n'
        m += lx('Event:') + ' ' + type + '\n'

        if t == LmNotif.TYPE_ACTIVE:
            m += lx('Access link:') + ' ' + event['Link'] + '\n'
        elif t == LmNotif.TYPE_LINK_CHANGE:
            m += lx('Old access link:') + ' ' + event['OldLink'] + '\n'
            m += lx('New access link:') + ' ' + event['NewLink'] + '\n'

        LmTools.async_send_email(c, subject, m)


    ### Check if a notification event match any configured notification rules
    @staticmethod
    def notify_get_matching_rule(event):
        rr = []
        t = event['Type']

        # Find a matching general rule for ALL
        for r in LmConf.NotificationRules:
            if r.get('Key') == LmNotif.DEVICE_ALL:
                e = r.get('Events')
                if isinstance(e, list) and (t in e):
                    rr += r.get('Rules')

        # Find a matching rule for unknown devices in case device is unknown
        k = event['Key']
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
    def notify_has_email_rule():
        if LmConf.NotificationRules is not None:
            r = next((r for r in LmConf.NotificationRules if LmNotif.RULE_EMAIL in r['Rules']), None)
            return r is not None
        return False



# ############# Livebox events collector thread #############
class LiveboxEventThread(LmThread):
    _event_received = QtCore.pyqtSignal(dict)
    _resume = QtCore.pyqtSignal()

    def __init__(self, api):
        super().__init__(api)


    def connect_processor(self, processor):
        self._event_received.connect(processor)


    def task(self):
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
