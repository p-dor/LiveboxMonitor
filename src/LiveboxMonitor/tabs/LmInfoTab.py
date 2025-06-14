### Livebox Monitor Livebox info tab module ###

import datetime

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmThread import LmThread
from LiveboxMonitor.app.LmTableWidget import LmTableWidget
from LiveboxMonitor.lang.LmLanguages import get_info_label as lx, get_info_message as mx


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'liveboxInfoTab'

# List columns
class InfoCol(IntEnum):
    Attribute = 0
    Value = 1

class StatsCol(IntEnum):
    Key = 0
    Name = 1
    Down = 2
    Up = 3
    DownRate = 4
    UpRate = 5


# ################################ LmInfo class ################################
class LmInfo:

    ### Create Livebox info tab
    def create_livebox_info_tab(self):
        self._livebox_info_tab = QtWidgets.QWidget(objectName=TAB_NAME)

        # Statistics list
        self._stats_list = LmTableWidget(objectName='statsList')
        self._stats_list.set_columns({StatsCol.Key: ['Key', 0, None],
                                      StatsCol.Name: [lx('Name'), 100, 'stats_Name'],
                                      StatsCol.Down: [lx('Rx'), 65, 'stats_Rx'],
                                      StatsCol.Up: [lx('Tx'), 65, 'stats_Tx'],
                                      StatsCol.DownRate: [lx('RxRate'), 65, 'stats_RxRate'],
                                      StatsCol.UpRate: [lx('TxRate'), 65, 'stats_TxRate']})
        self._stats_list.set_header_resize([StatsCol.Down, StatsCol.Up, StatsCol.DownRate, StatsCol.UpRate])
        self._stats_list.set_standard_setup(self, allow_sel=False, allow_sort=False)
        self._stats_list.setMinimumWidth(450)

        intf_list = self._api._intf.get_list()
        for i, s in enumerate(intf_list):
            self._stats_list.insertRow(i)
            self._stats_list.setItem(i, StatsCol.Key, QtWidgets.QTableWidgetItem(s['Key']))
            self._stats_list.setItem(i, StatsCol.Name, QtWidgets.QTableWidgetItem(lx(s['Name'])))
        stats_list_size = LmConfig.table_height(len(intf_list))
        self._stats_list.setMinimumHeight(stats_list_size)
        self._stats_list.setMaximumHeight(stats_list_size)

        # Attribute list
        self._livebox_alist = LmTableWidget(objectName='liveboxAList')
        self._livebox_alist.set_columns({InfoCol.Attribute: [lx('Attribute'), 200, 'alist_Attribute'],
                                         InfoCol.Value: [lx('Value'), 600, 'alist_Value']})
        self._livebox_alist.set_header_resize([InfoCol.Value])
        self._livebox_alist.set_standard_setup(self, allow_sel=False, allow_sort=False)

        # Lists layout
        list_box = QtWidgets.QHBoxLayout()
        list_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        list_box.setSpacing(10)
        list_box.addWidget(self._stats_list, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        list_box.addWidget(self._livebox_alist, 1)

        # Button bar
        buttons_box = QtWidgets.QHBoxLayout()
        buttons_box.setSpacing(10)

        livebox_info_button = QtWidgets.QPushButton(lx('Livebox Infos'), objectName='liveboxInfo')
        livebox_info_button.clicked.connect(self.livebox_info_button_click)
        buttons_box.addWidget(livebox_info_button)

        internet_info_button = QtWidgets.QPushButton(lx('Internet Infos'), objectName='internetInfo')
        internet_info_button.clicked.connect(self.internet_info_button_click)
        buttons_box.addWidget(internet_info_button)

        wifi_info_button = QtWidgets.QPushButton(lx('Wifi Infos'), objectName='wifiInfo')
        wifi_info_button.clicked.connect(self.wifi_info_button_click)
        buttons_box.addWidget(wifi_info_button)

        lan_info_button = QtWidgets.QPushButton(lx('LAN Infos'), objectName='lanInfo')
        lan_info_button.clicked.connect(self.lan_info_button_click)
        buttons_box.addWidget(lan_info_button)

        ont_info_button = QtWidgets.QPushButton(lx('ONT Infos'), objectName='ontInfo')
        ont_info_button.clicked.connect(self.ont_info_button_click)
        if self._fiber_link:
            buttons_box.addWidget(ont_info_button)

        voip_info_button = QtWidgets.QPushButton(lx('VoIP Infos'), objectName='voipInfo')
        voip_info_button.clicked.connect(self.voip_info_button_click)
        buttons_box.addWidget(voip_info_button)

        iptv_info_button = QtWidgets.QPushButton(lx('IPTV Infos'), objectName='iptvInfo')
        iptv_info_button.clicked.connect(self.iptv_info_button_click)
        buttons_box.addWidget(iptv_info_button)

        usb_info_button = QtWidgets.QPushButton(lx('USB Infos'), objectName='usbInfo')
        usb_info_button.clicked.connect(self.usb_info_button_click)
        buttons_box.addWidget(usb_info_button)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        buttons_box.addWidget(separator)

        export_info_button = QtWidgets.QPushButton(lx('Export...'), objectName='exportInfo')
        export_info_button.clicked.connect(self.export_info_button_click)
        buttons_box.addWidget(export_info_button)
        self._export_file = None

        # Layout
        vbox = QtWidgets.QVBoxLayout()
        vbox.setSpacing(10)
        vbox.addLayout(list_box, 0)
        vbox.addLayout(buttons_box, 1)
        self._livebox_info_tab.setLayout(vbox)

        # Init context
        self._home_lan_intf_stats_map = {}
        self._livebox_stats_map_home_lan = {}

        LmConfig.set_tooltips(self._livebox_info_tab, 'info')
        self._tab_widget.addTab(self._livebox_info_tab, lx('Livebox Stats/Infos'))


    ### Init the Livebox stats collector thread
    def init_stats_loop(self):
        self._livebox_stats_map = {}
        self._livebox_stats_loop = None


    ### Start the Livebox stats collector thread
    def start_stats_loop(self):
        self._livebox_stats_loop = LiveboxStatsThread(self._api)
        self._livebox_stats_loop.connect_processor(self.process_livebox_stats)


    ### Suspend the Livebox stats collector thread
    def suspend_stats_loop(self):
        if self._livebox_stats_loop is not None:
            self._livebox_stats_loop.stop()


    ### Resume the Livebox stats collector thread
    def resume_stats_loop(self):
        if self._livebox_stats_loop is None:
            self.start_stats_loop()
        else:
            self._livebox_stats_loop._resume.emit()


    ### Stop the Livebox stats collector thread
    def stop_stats_loop(self):
        if self._livebox_stats_loop is not None:
            self._livebox_stats_loop.quit()
            self._livebox_stats_loop = None


    ### Process a HomeLan interface stats event
    def process_intf_statistics_event(self, intf, attributes):
        for s in self._api._intf.get_list():
            if s['Key'] == intf:
                e = {'Key': intf,
                     'Source': 'hls',     # HomeLanStats
                     'Timestamp': datetime.datetime.now()}

                # Only one value among the two is present per event
                bytes_sent = attributes.get('BytesSent')
                bytes_received = attributes.get('BytesReceived')

                if bytes_sent is None:
                    if s['SwapStats']:
                        e['RxBytes'] = None
                    else:
                        e['TxBytes'] = None
                else:
                    if s['SwapStats']:
                        e['RxBytes'] = int(bytes_sent)
                    else:
                        e['TxBytes'] = int(bytes_sent)

                if bytes_received is None:
                    if s['SwapStats']:
                        e['TxBytes'] = None
                    else:
                        e['RxBytes'] = None
                else:
                    if s['SwapStats']:
                        e['TxBytes'] = int(bytes_received)
                    else:
                        e['RxBytes'] = int(bytes_received)

                e['RxErrors'] = 0
                e['TxErrors'] = 0

                # Update UI
                self.process_livebox_stats(e)

                # Update potential running graph
                bytes_received = e['RxBytes']
                delta_received = None
                bytes_sent = e['TxBytes']
                delta_sent = None

                # Try to find a previously received statistic record
                prev_stats = self._home_lan_intf_stats_map.get(intf)
                if prev_stats is not None:
                    prev_down_bytes = prev_stats['RxBytes']
                    if bytes_received is not None:
                        if (prev_down_bytes is not None) and (bytes_received > prev_down_bytes):
                            delta_received = bytes_received - prev_down_bytes
                    else:
                        bytes_received = prev_down_bytes

                    prev_up_bytes = prev_stats['TxBytes']
                    if bytes_sent is not None:
                        if (prev_up_bytes is not None) and (bytes_sent > prev_up_bytes):
                            delta_sent = bytes_sent - prev_up_bytes
                    else:
                        bytes_sent = prev_up_bytes

                # Remember current stats
                s = {'RxBytes': bytes_received,
                     'TxBytes': bytes_sent}
                self._home_lan_intf_stats_map[intf] = s

                self.graph_update_interface_event(intf, int(e['Timestamp'].timestamp()), delta_received, delta_sent)
                break


    ### Find stats line from stat key
    def find_stats_line(self, istats_key):
        if istats_key:
            for i in range(self._stats_list.rowCount()):
                if self._stats_list.item(i, StatsCol.Key).text() == istats_key:
                    return i
        return -1


    ### Process a new Livebox stats
    # Stats can come from two sources, indicated in the 'Source' value: NetDevStats ('nds') or HomeLan ('hls').
    # nds stats are realtime but recycling at 4Gb max / hls stats are raised every 30s but recycling at much higher numbers
    # nds stats come will all values / hls stats come with either down or up bytes values, other is None, and errors are at zero
    # Strategy is to display realime rates from nds events and to update the counters from the hls events
    def process_livebox_stats(self, stats):
        # Get stats data
        key = stats['Key']
        source = stats['Source']
        timestamp = stats['Timestamp']
        down_bytes = stats.get('RxBytes')
        up_bytes = stats.get('TxBytes')
        down_errors = stats['RxErrors']
        up_errors = stats['TxErrors']
        down_rate_bytes = 0
        up_rate_bytes = 0
        down_delta_errors = 0
        up_delta_errors = 0

        match source:
            # If event source is HomeLan update the counters only and remember it
            case 'hls':
                self._livebox_stats_map_home_lan[key] = True

            # If event source is NetDevStats update all and remember last nds stats
            case 'nds':
                # Try to find a previously received statistic record
                prev_stats = self._livebox_stats_map.get(key)
                if prev_stats is not None:
                    prev_timestamp = prev_stats['Timestamp']
                    prev_down_bytes = prev_stats['RxBytes']
                    prev_up_bytes = prev_stats['TxBytes']
                    elapsed = int((timestamp - prev_timestamp).total_seconds())
                    if elapsed > 0:
                        if down_bytes > prev_down_bytes:
                            down_rate_bytes = int((down_bytes - prev_down_bytes) / elapsed)
                        if up_bytes > prev_up_bytes:
                            up_rate_bytes = int((up_bytes - prev_up_bytes) / elapsed)
                    down_delta_errors = down_errors - prev_stats['RxErrors']
                    up_delta_errors = up_errors - prev_stats['TxErrors']

                # Remember current stats
                self._livebox_stats_map[key] = stats

                # Don't erase previously received HomeLan counters
                if self._livebox_stats_map_home_lan.get(key, False):
                    down_bytes = None
                    up_bytes = None

        # Update UI
        list_line = self.find_stats_line(key)
        if list_line >= 0:
            if down_bytes is not None:
                down = QtWidgets.QTableWidgetItem(LmTools.fmt_bytes(down_bytes))
                down.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
                if down_errors:
                    down.setForeground(QtCore.Qt.GlobalColor.red)
                self._stats_list.setItem(list_line, StatsCol.Down, down)

            if up_bytes is not None:
                up = QtWidgets.QTableWidgetItem(LmTools.fmt_bytes(up_bytes))
                up.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
                if up_errors:
                    up.setForeground(QtCore.Qt.GlobalColor.red)
                self._stats_list.setItem(list_line, StatsCol.Up, up)

            if source == 'nds':
                if down_rate_bytes:
                    down_rate = QtWidgets.QTableWidgetItem(LmTools.fmt_bytes(down_rate_bytes) + '/s')
                    if down_delta_errors:
                        down_rate.setForeground(QtCore.Qt.GlobalColor.red)
                    down_rate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
                else:
                    down_rate = QtWidgets.QTableWidgetItem('')
                self._stats_list.setItem(list_line, StatsCol.DownRate, down_rate)

                if up_rate_bytes:
                    up_rate = QtWidgets.QTableWidgetItem(LmTools.fmt_bytes(up_rate_bytes) + '/s')
                    if up_delta_errors:
                        up_rate.setForeground(QtCore.Qt.GlobalColor.red)
                    up_rate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
                else:
                    up_rate = QtWidgets.QTableWidgetItem('')
                self._stats_list.setItem(list_line, StatsCol.UpRate, up_rate)


    ### Add a title line in an info attribute/value list
    def add_title_line(self, list_widget, line, title):
        if title:
            if self._export_file is not None:
                if line > 0:
                    line += 1
                    self._export_file.write('\n')
                self._export_file.write(f'### {title}\n')
            else:
                list_widget.insertRow(line)
                if line > 0:
                    line += 1
                    list_widget.insertRow(line)
                attribute_item = QtWidgets.QTableWidgetItem('')
                attribute_item.setBackground(QtCore.Qt.GlobalColor.cyan)
                title_item = QtWidgets.QTableWidgetItem(title)
                title_item.setFont(LmTools.BOLD_FONT)
                title_item.setBackground(QtCore.Qt.GlobalColor.cyan)
                list_widget.setItem(line, InfoCol.Attribute, attribute_item)
                list_widget.setItem(line, InfoCol.Value, title_item)
            return line + 1
        return line


    ### Add a line in an info attribute/value list
    def add_info_line(self, list_widget, line, attribute, value, qualifier=LmTools.ValQual.Default):
        if value:
            if self._export_file is not None:
                self._export_file.write(f'{attribute} = {value}\n')
            else:
                list_widget.insertRow(line)
                attribute_item = QtWidgets.QTableWidgetItem(attribute)
                attribute_item.setFont(LmTools.BOLD_FONT)
                list_widget.setItem(line, InfoCol.Attribute, attribute_item)
                if qualifier != LmTools.ValQual.Default:
                    value_item = QtWidgets.QTableWidgetItem(value)
                    match qualifier:
                        case LmTools.ValQual.Good:
                            value_item.setForeground(QtGui.QBrush(QtGui.QColor(0, 190, 0)))
                        case LmTools.ValQual.Warn:
                            value_item.setForeground(QtGui.QBrush(QtGui.QColor(255, 191, 0)))
                        case LmTools.ValQual.Error:
                            value_item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                    list_widget.setItem(line, InfoCol.Value, value_item)
                else:
                    list_widget.setItem(line, InfoCol.Value, QtWidgets.QTableWidgetItem(value))
            return line + 1
        return line


    ### Click on Livebox infos button
    def livebox_info_button_click(self):
        self._task.start(lx('Getting Livebox information...'))

        try:
            self._livebox_alist.clearContents()
            self._livebox_alist.setRowCount(0)

            self.load_livebox_info()

        finally:
            self._task.end()


    ### Click on Internet infos button
    def internet_info_button_click(self):
        self._task.start(lx('Getting Internet information...'))

        try:
            self._livebox_alist.clearContents()
            self._livebox_alist.setRowCount(0)

            self.load_internet_info()

        finally:
            self._task.end()


    ### Click on Wifi infos button
    def wifi_info_button_click(self):
        self._task.start(lx('Getting Wifi information...'))

        try:
            self._livebox_alist.clearContents()
            self._livebox_alist.setRowCount(0)

            self.load_wifi_info()

        finally:
            self._task.end()


    ### Click on LAN infos button
    def lan_info_button_click(self):
        self._task.start(lx('Getting LAN information...'))

        try:
            self._livebox_alist.clearContents()
            self._livebox_alist.setRowCount(0)

            self.load_lan_info()

        finally:
            self._task.end()


    ### Click on ONT infos button
    def ont_info_button_click(self):
        self._task.start(lx('Getting ONT information...'))

        try:
            self._livebox_alist.clearContents()
            self._livebox_alist.setRowCount(0)

            self.load_ont_info()

        finally:
            self._task.end()


    ### Click on VoIP infos button
    def voip_info_button_click(self):
        self._task.start(lx('Getting VoIP information...'))

        try:
            self._livebox_alist.clearContents()
            self._livebox_alist.setRowCount(0)

            self.load_voip_info()

        finally:
            self._task.end()


    ### Click on IPTV infos button
    def iptv_info_button_click(self):
        self._task.start(lx('Getting IPTV information...'))

        try:
            self._livebox_alist.clearContents()
            self._livebox_alist.setRowCount(0)

            self.load_iptv_info()

        finally:
            self._task.end()


    ### Click on USB infos button
    def usb_info_button_click(self):
        self._task.start(lx('Getting USB information...'))

        try:
            self._livebox_alist.clearContents()
            self._livebox_alist.setRowCount(0)

            self.load_usb_info()

        finally:
            self._task.end()


    ### Click on Export infos button
    def export_info_button_click(self):
        file_name = QtWidgets.QFileDialog.getSaveFileName(self, lx('Save File'), lx('Livebox Infos') + '.txt', '*.txt')[0]
        if not file_name:
            return

        try:
            self._export_file = open(file_name, 'w')
        except Exception as e:
            LmTools.error(f'File creation error: {e}')
            self.display_error(mx('Cannot create the file.', 'createFileErr'))
            return

        self._task.start(lx('Exporting all information...'))

        try:
            i = 0
            i = self.load_livebox_info(i)
            i = self.load_internet_info(i)
            i = self.load_wifi_info(i)
            i = self.load_lan_info(i)
            if self._fiber_link:
                i = self.load_ont_info(i)
            i = self.load_voip_info(i)
            i = self.load_iptv_info(i)
            i = self.load_usb_info(i)

        finally:
            self._task.end()

        try:
            self._export_file.close()
        except Exception as e:
            LmTools.error(f'File saving error: {e}')
            self.display_error(mx('Cannot save the file.', 'saveFileErr'))

        self._export_file = None


    ### Load Livebox infos
    def load_livebox_info(self, index=0):
        i = self.add_title_line(self._livebox_alist, index, lx('Livebox Information'))

        try:
            d = self._api._info.get_model_info()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Livebox Infos'), 'UPnP-IGD:get query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('Provider'), d.get('WANAccessProvider'))
            i = self.add_info_line(self._livebox_alist, i, lx('Model Number'), d.get('ModelNumber'))
            i = self.add_info_line(self._livebox_alist, i, lx('Model Name'), d.get('ModelName'))
            i = self.add_info_line(self._livebox_alist, i, lx('Friendly Name'), d.get('FriendlyName'))
            i = self.add_info_line(self._livebox_alist, i, lx('Allowed Host Headers'), d.get('AllowedHostHeader'))

        try:
            d = self._api._info.get_reboot_info()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Livebox Infos'), 'NMC.Reboot:get query error', LmTools.ValQual.Error)
            total_reboot = None
        else:
            total_reboot = d.get('BootCounter')

        try:
            d = self._api._info.get_livebox_info()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Livebox Infos'), 'DeviceInfo:get query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('Model'), d.get('ProductClass'))
            i = self.add_info_line(self._livebox_alist, i, lx('Status'), LmTools.fmt_str_capitalize(d.get('DeviceStatus')))
            i = self.add_info_line(self._livebox_alist, i, lx('Livebox Up Time'), LmTools.fmt_time(d.get('UpTime')))
            i = self.add_info_line(self._livebox_alist, i, lx('Manufacturer'), d.get('Manufacturer'))
            i = self.add_info_line(self._livebox_alist, i, lx('Manufacturer Model Name'), d.get('ModelName'))
            i = self.add_info_line(self._livebox_alist, i, lx('Description'), d.get('Description'))
            i = self.add_info_line(self._livebox_alist, i, lx('Serial Number'), d.get('SerialNumber'))
            i = self.add_info_line(self._livebox_alist, i, lx('Hardware Version'), d.get('HardwareVersion'))
            i = self.add_info_line(self._livebox_alist, i, lx('Software Version'), d.get('SoftwareVersion'))
            i = self.add_info_line(self._livebox_alist, i, lx('Rescue Version'), d.get('RescueVersion'))
            i = self.add_info_line(self._livebox_alist, i, lx('Modem Firmware Version'), d.get('ModemFirmwareVersion'))
            i = self.add_info_line(self._livebox_alist, i, lx('Orange Firmware Version'), d.get('AdditionalSoftwareVersion'))
            i = self.add_info_line(self._livebox_alist, i, lx('Spec Version'), d.get('SpecVersion'))
            i = self.add_info_line(self._livebox_alist, i, lx('Provisioning Code'), d.get('ProvisioningCode'))
            i = self.add_info_line(self._livebox_alist, i, lx('Country'), LmTools.fmt_str_upper(d.get('Country')))
            i = self.add_info_line(self._livebox_alist, i, lx('MAC Address'), self._api._info.get_livebox_mac())
            i = self.add_info_line(self._livebox_alist, i, lx('External IP Address'), d.get('ExternalIPAddress'))
            if total_reboot is not None:
                i = self.add_info_line(self._livebox_alist, i, lx('Total Number Of Reboots'), LmTools.fmt_int(total_reboot))
            i = self.add_info_line(self._livebox_alist, i, lx('Number Of Reboots'), LmTools.fmt_int(d.get('NumberOfReboots')))
            i = self.add_info_line(self._livebox_alist, i, lx('Upgrade Occurred'), LmTools.fmt_bool(d.get('UpgradeOccurred')))
            i = self.add_info_line(self._livebox_alist, i, lx('Reset Occurred'), LmTools.fmt_bool(d.get('ResetOccurred')))
            i = self.add_info_line(self._livebox_alist, i, lx('Restore Occurred'), LmTools.fmt_bool(d.get('RestoreOccurred')))

        try:
            d = self._api._info.get_device_info()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Livebox Infos'), 'Devices.Device:get query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('Name'), d.get('Name'))
            i = self.add_info_line(self._livebox_alist, i, lx('Active'), LmTools.fmt_bool(d.get('Active')))
            i = self.add_info_line(self._livebox_alist, i, lx('First Boot'), LmTools.fmt_livebox_timestamp(d.get('FirstSeen')))
            i = self.add_info_line(self._livebox_alist, i, lx('Boot Loader Version'), d.get('BootLoaderVersion'))
            i = self.add_info_line(self._livebox_alist, i, lx('Firewall Level'), d.get('FirewallLevel'))
            i = self.add_info_line(self._livebox_alist, i, lx('Internet Active'), LmTools.fmt_bool(d.get('Internet')))
            i = self.add_info_line(self._livebox_alist, i, lx('IPTV Active'), LmTools.fmt_bool(d.get('IPTV')))
            i = self.add_info_line(self._livebox_alist, i, lx('Telephony Active'), LmTools.fmt_bool(d.get('Telephony')))

        try:
            d = self._api._info.get_time()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Time'), 'Time:getTime query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('Time'), d.get('time'))

        try:
            d = self._api._info.get_memory_status()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Memory'), 'DeviceInfo.MemoryStatus:get query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('Total Memory'), LmTools.fmt_int(d.get('Total')))
            i = self.add_info_line(self._livebox_alist, i, lx('Free Memory'), LmTools.fmt_int(d.get('Free')))

        return i


    ### Load Internet infos
    def load_internet_info(self, index=0):
        i = self.add_title_line(self._livebox_alist, index, lx('Internet Information'))

        try:
            d = self._api._info.get_connection_status()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Connection'), 'NMC:get query error', LmTools.ValQual.Error)
        else:
            access_type = d.get('WanMode')
            if access_type is not None:
                if self._fiber_link:
                    i = self.add_info_line(self._livebox_alist, i, lx('Access Type'), f'Fiber ({access_type})')
                else:
                    i = self.add_info_line(self._livebox_alist, i, lx('Access Type'), f'ADSL ({access_type})')

            i = self.add_info_line(self._livebox_alist, i, lx('Username'), d.get('Username'))
            i = self.add_info_line(self._livebox_alist, i, lx('Factory Reset Scheduled'), LmTools.fmt_bool(d.get('FactoryResetScheduled')))
            i = self.add_info_line(self._livebox_alist, i, lx('Connection Error'), LmTools.fmt_bool(d.get('ConnectionError')))
            i = self.add_info_line(self._livebox_alist, i, lx('Offer Type'), d.get('OfferType'))
            i = self.add_info_line(self._livebox_alist, i, lx('Offer Name'), d.get('OfferName'))
            i = self.add_info_line(self._livebox_alist, i, lx('IPTV Mode'), d.get('IPTVMode'))

        try:
            d = self._api._info.get_wan_status()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Internet Infos'), 'NMC:getWANStatus query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('WAN Status'), LmTools.fmt_str_capitalize(d.get('WanState')))
            i = self.add_info_line(self._livebox_alist, i, lx('Link Status'), LmTools.fmt_str_capitalize(d.get('LinkState')))
            i = self.add_info_line(self._livebox_alist, i, lx('Link Type'), LmTools.fmt_str_upper(d.get('LinkType')))
            i = self.add_info_line(self._livebox_alist, i, lx('Protocol'), LmTools.fmt_str_upper(d.get('Protocol')))
            i = self.add_info_line(self._livebox_alist, i, lx('GPON State'), d.get('GponState'))
            i = self.add_info_line(self._livebox_alist, i, lx('Connection Status'), d.get('ConnectionState'))
            i = self.add_info_line(self._livebox_alist, i, lx('Last Connection Error'), d.get('LastConnectionError'))
            i = self.add_info_line(self._livebox_alist, i, lx('IP Address'), d.get('IPAddress'))
            i = self.add_info_line(self._livebox_alist, i, lx('Remote Gateway'), d.get('RemoteGateway'))
            i = self.add_info_line(self._livebox_alist, i, lx('DNS Servers'), d.get('DNSServers'))
            i = self.add_info_line(self._livebox_alist, i, lx('IPv6 Address'), d.get('IPv6Address'))
            i = self.add_info_line(self._livebox_alist, i, lx('IPv6 Prefix'), d.get('IPv6DelegatedPrefix'))

        try:
            d = self._api._info.get_device_info()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Internet Infos'), 'Devices.Device:get query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('Last Connection'), LmTools.fmt_livebox_timestamp(d.get('LastConnection')))
            i = self.add_info_line(self._livebox_alist, i, lx('Firewall Level'), d.get('FirewallLevel'))
            rate = d.get('DownstreamMaxBitRate')
            if rate is not None:
                rate *= 1048576
                i = self.add_info_line(self._livebox_alist, i, lx('Max Down Bit Rate'), LmTools.fmt_bytes(rate))
            rate = d.get('UpstreamMaxBitRate')
            if rate is not None:
                rate *= 1048576
                i = self.add_info_line(self._livebox_alist, i, lx('Max Up Bit Rate'), LmTools.fmt_bytes(rate))

        try:
            d = self._api._dhcp.get_mibs(True, False)
        except Exception as e:
            LmTools.error(str(e))
            d = None
        if d is not None:
            d = d.get('dhcp')
        if d is not None:
            d = d.get('dhcp_data')
        if d is None:
            i = self.add_info_line(self._livebox_alist, i, lx('Connection'), 'NeMo.Intf.data:getMIBs query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('DHCP Status'), d.get('DHCPStatus'))
            i = self.add_info_line(self._livebox_alist, i, lx('Subnet Mask'), d.get('SubnetMask'))
            i = self.add_info_line(self._livebox_alist, i, lx('IP Routers'), d.get('IPRouters'))
            i = self.add_info_line(self._livebox_alist, i, lx('DHCP Server'), d.get('DHCPServer'))
            i = self.add_info_line(self._livebox_alist, i, lx('Renew'), LmTools.fmt_bool(d.get('Renew')))
            i = self.add_info_line(self._livebox_alist, i, lx('Authentication'), LmTools.fmt_bool(d.get('CheckAuthentication')))
            i = self.add_info_line(self._livebox_alist, i, lx('Authentication Information'), d.get('AuthenticationInformation'))
            i = self.add_info_line(self._livebox_alist, i, lx('Connection Up Time'), LmTools.fmt_time(d.get('Uptime')))
            i = self.add_info_line(self._livebox_alist, i, lx('Lease Time'), LmTools.fmt_time(d.get('LeaseTime')))
            i = self.add_info_line(self._livebox_alist, i, lx('Lease Time Remaining'), LmTools.fmt_time(d.get('LeaseTimeRemaining')))

        try:
            d = self._api._info.get_vlan_id()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('VLAN ID'), 'NeMo.Intf.data:getFirstParameter query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('VLAN ID'), LmTools.fmt_int(d))

        try:
            d = self._api._info.get_mtu()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('MTU'), 'NeMo.Intf.data:getFirstParameter query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('MTU'), LmTools.fmt_int(d))

        return i


    ### Load Wifi infos
    def load_wifi_info(self, index=0):
        i = self.add_title_line(self._livebox_alist, index, lx('Wifi Information'))
        intf_list = self._api._intf.get_list()

        # General infos
        try:
            d = self._api._wifi.get_status()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Wifi'), 'NMC.Wifi:get query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('Enabled'), LmTools.fmt_bool(d.get('Enable')))
            i = self.add_info_line(self._livebox_alist, i, lx('Active'), LmTools.fmt_bool(d.get('Status')))
            i = self.add_info_line(self._livebox_alist, i, lx('BGN User Bandwidth'), d.get('BGNUserBandwidth'))

        # Wifi scheduler
        try:
            d = self._api._wifi.get_scheduler_enable()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Scheduler Enabled'), 'Scheduler query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('Scheduler Enabled'), LmTools.fmt_bool(d))

        # Wifi 7 MLO
        if self._api._wifi.has_mlo():
            try:
                d = self._api._wifi.get_mlo_config()
            except Exception as e:
                LmTools.error(str(e))
                i = self.add_info_line(self._livebox_alist, i, lx('MLO'), 'MLO query error', LmTools.ValQual.Error)
            else:
                i = self.add_info_line(self._livebox_alist, i, lx('MLO'), LmTools.fmt_bool(d.get('MLOEnable')))
                i = self.add_info_line(self._livebox_alist, i, lx('MLO Single MLD Unit'), LmTools.fmt_int(d.get('SingleMLDUnit')))
                i = self.add_info_line(self._livebox_alist, i, lx('MLO EMLSR'), LmTools.fmt_bool(d.get('EMLSREnable')))
                i = self.add_info_line(self._livebox_alist, i, lx('MLO EMLMR'), LmTools.fmt_bool(d.get('EMLMREnable')))
                i = self.add_info_line(self._livebox_alist, i, lx('MLO STR'), LmTools.fmt_bool(d.get('STREnable')))
                i = self.add_info_line(self._livebox_alist, i, lx('MLO Split MLD Mode'), d.get('SplitMLDMode'))

        # Wifi interfaces
        try:
            b, w, d = self._api._intf.get_wifi_mibs()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Wifi'), 'NeMo.Intf.lan:getMIBs query error', LmTools.ValQual.Error)
        else:
            for s in intf_list:
                if s['Type'] != 'wif':
                    continue
                i = self.add_title_line(self._livebox_alist, i, s['Name'])

                # Get Wifi interface key in wlanradio list
                intf_key = None
                base = b.get(s['Key'])
                if base is not None:
                    i = self.add_info_line(self._livebox_alist, i, lx('Enabled'), LmTools.fmt_bool(base.get('Enable')))
                    i = self.add_info_line(self._livebox_alist, i, lx('Active'), LmTools.fmt_bool(base.get('Status')))
                    low_level_intf = base.get('LLIntf')
                    if low_level_intf is not None:
                        intf_key = next(iter(low_level_intf))

                q = w.get(intf_key) if intf_key is not None else None
                r = d.get(s['Key'])
                if (q is None) or (r is None):
                    continue

                i = self.add_info_line(self._livebox_alist, i, lx('Radio Status'), q.get('RadioStatus'))
                i = self.add_info_line(self._livebox_alist, i, lx('VAP Status'), r.get('VAPStatus'))
                i = self.add_info_line(self._livebox_alist, i, lx('Vendor Name'), LmTools.fmt_str_upper(q.get('VendorName')))
                i = self.add_info_line(self._livebox_alist, i, lx('MAC Address'), LmTools.fmt_str_upper(r.get('MACAddress')))
                i = self.add_info_line(self._livebox_alist, i, lx('SSID'), r.get('SSID'))
                i = self.add_info_line(self._livebox_alist, i, lx('SSID Advertisement'), LmTools.fmt_bool(r.get('SSIDAdvertisementEnabled')))

                t = r.get('Security')
                if t is not None:
                    i = self.add_info_line(self._livebox_alist, i, lx('Security Mode'), t.get('ModeEnabled'))
                    i = self.add_info_line(self._livebox_alist, i, lx('WEP Key'), t.get('WEPKey'))
                    i = self.add_info_line(self._livebox_alist, i, lx('PreShared Key'), t.get('PreSharedKey'))
                    i = self.add_info_line(self._livebox_alist, i, lx('Key Pass Phrase'), t.get('KeyPassPhrase'))

                t = r.get('WPS')
                if t is not None:
                    i = self.add_info_line(self._livebox_alist, i, lx('WPS Enabled'), LmTools.fmt_bool(t.get('Enable')))
                    i = self.add_info_line(self._livebox_alist, i, lx('WPS Methods'), t.get('ConfigMethodsEnabled'))
                    i = self.add_info_line(self._livebox_alist, i, lx('WPS Self PIN'), t.get('SelfPIN'))
                    i = self.add_info_line(self._livebox_alist, i, lx('WPS Pairing In Progress'), LmTools.fmt_bool(t.get('PairingInProgress')))

                t = r.get('MACFiltering')
                if t is not None:
                    i = self.add_info_line(self._livebox_alist, i, lx('MAC Filtering'), t.get('Mode'))

                i = self.add_info_line(self._livebox_alist, i, lx('Max Bitrate'), LmTools.fmt_int(q.get('MaxBitRate')))
                i = self.add_info_line(self._livebox_alist, i, lx('AP Mode'), LmTools.fmt_bool(q.get('AP_Mode')))
                i = self.add_info_line(self._livebox_alist, i, lx('STA Mode'), LmTools.fmt_bool(q.get('STA_Mode')))
                i = self.add_info_line(self._livebox_alist, i, lx('WDS Mode'), LmTools.fmt_bool(q.get('WDS_Mode')))
                i = self.add_info_line(self._livebox_alist, i, lx('WET Mode'), LmTools.fmt_bool(q.get('WET_Mode')))
                i = self.add_info_line(self._livebox_alist, i, lx('Frequency Band'), q.get('OperatingFrequencyBand'))
                i = self.add_info_line(self._livebox_alist, i, lx('Channel Bandwidth'), q.get('CurrentOperatingChannelBandwidth'))
                i = self.add_info_line(self._livebox_alist, i, lx('Standard'), q.get('OperatingStandards'))
                i = self.add_info_line(self._livebox_alist, i, lx('Channel'), LmTools.fmt_int(q.get('Channel')))
                i = self.add_info_line(self._livebox_alist, i, lx('Auto Channel Supported'), LmTools.fmt_bool(q.get('AutoChannelSupported')))
                i = self.add_info_line(self._livebox_alist, i, lx('Auto Channel Enabled'), LmTools.fmt_bool(q.get('AutoChannelEnable')))
                i = self.add_info_line(self._livebox_alist, i, lx('Channel Change Reason'), q.get('ChannelChangeReason'))
                i = self.add_info_line(self._livebox_alist, i, lx('Max Associated Devices'), LmTools.fmt_int(q.get('MaxAssociatedDevices')))
                i = self.add_info_line(self._livebox_alist, i, lx('Active Associated Devices'), LmTools.fmt_int(q.get('ActiveAssociatedDevices')))
                i = self.add_info_line(self._livebox_alist, i, lx('Noise'), LmTools.fmt_int(q.get('Noise')))
                i = self.add_info_line(self._livebox_alist, i, lx('Antenna Defect'), LmTools.fmt_bool(q.get('AntennaDefect')))

        try:
            b, w, d = self._api._intf.get_wifi_mibs(True)
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Wifi'), 'NeMo.Intf.guest:getMIBs query error', LmTools.ValQual.Error)
        else:
            for s in intf_list:
                if s['Type'] != 'wig':
                    continue
                i = self.add_title_line(self._livebox_alist, i, s['Name'])

                base = b.get(s['Key'])
                if base is not None:
                    i = self.add_info_line(self._livebox_alist, i, lx('Enabled'), LmTools.fmt_bool(base.get('Enable')))
                    i = self.add_info_line(self._livebox_alist, i, lx('Active'), LmTools.fmt_bool(base.get('Status')))

                r = d.get(s['Key'])
                if r is None:
                    continue

                i = self.add_info_line(self._livebox_alist, i, lx('VAP Status'), r.get('VAPStatus'))
                i = self.add_info_line(self._livebox_alist, i, lx('MAC Address'), LmTools.fmt_str_upper(r.get('MACAddress')))
                i = self.add_info_line(self._livebox_alist, i, lx('SSID'), r.get('SSID'))
                i = self.add_info_line(self._livebox_alist, i, lx('SSID Advertisement'), LmTools.fmt_bool(r.get('SSIDAdvertisementEnabled')))

                t = r.get('Security')
                if t is not None:
                    i = self.add_info_line(self._livebox_alist, i, lx('Security Mode'), t.get('ModeEnabled'))
                    i = self.add_info_line(self._livebox_alist, i, lx('WEP Key'), t.get('WEPKey'))
                    i = self.add_info_line(self._livebox_alist, i, lx('PreShared Key'), t.get('PreSharedKey'))
                    i = self.add_info_line(self._livebox_alist, i, lx('Key Pass Phrase'), t.get('KeyPassPhrase'))

                t = r.get('WPS')
                if t is not None:
                    i = self.add_info_line(self._livebox_alist, i, lx('WPS Enabled'), LmTools.fmt_bool(t.get('Enable')))
                    i = self.add_info_line(self._livebox_alist, i, lx('WPS Methods'), t.get('ConfigMethodsEnabled'))
                    i = self.add_info_line(self._livebox_alist, i, lx('WPS Self PIN'), t.get('SelfPIN'))
                    i = self.add_info_line(self._livebox_alist, i, lx('WPS Pairing In Progress'), LmTools.fmt_bool(t.get('PairingInProgress')))

                t = r.get('MACFiltering')
                if t is not None:
                    i = self.add_info_line(self._livebox_alist, i, lx('MAC Filtering'), t.get('Mode'))

        return i


    ### Load LAN infos
    def load_lan_info(self, index=0):
        i = self.add_title_line(self._livebox_alist, index, lx('LAN Information'))

        try:
            d = self._api._dhcp.get_info('default')
        except Exception as e:
            LmTools.error(str(e))
            d = None
        else:
            d = d.get('default')
        if d is None:
            i = self.add_info_line(self._livebox_alist, i, lx('DHCPv4'), 'DHCPv4.Server:getDHCPServerPool query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('DHCPv4 Enabled'), LmTools.fmt_bool(d.get('Enable')))
            i = self.add_info_line(self._livebox_alist, i, lx('DHCPv4 Status'), d.get('Status'))
            i = self.add_info_line(self._livebox_alist, i, lx('DHCPv4 Gateway'), d.get('Server'))
            i = self.add_info_line(self._livebox_alist, i, lx('Subnet Mask'), d.get('SubnetMask'))
            i = self.add_info_line(self._livebox_alist, i, lx('DHCPv4 Start'), d.get('MinAddress'))
            i = self.add_info_line(self._livebox_alist, i, lx('DHCPv4 End'), d.get('MaxAddress'))
            i = self.add_info_line(self._livebox_alist, i, lx('DHCPv4 Lease Time'), LmTools.fmt_time(d.get('LeaseTime')))

        try:
            d = self._api._dhcp.get_v6_server_status()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('DHCPv6'), 'DHCPv6.Server:getDHCPv6ServerStatus query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('DHCPv6 Status'), d)

        try:
            b, d = self._api._intf.get_eth_mibs()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('LAN'), 'NeMo.Intf.lan:getMIBs query error', LmTools.ValQual.Error)
        else:
            for s in self._api._intf.get_list():
                if s['Type'] != 'eth':
                    continue
                i = self.add_title_line(self._livebox_alist, i, s['Name'])

                q = b.get(s['Key'])
                r = d.get(s['Key'])
                if (q is None) or (r is None):
                    continue

                i = self.add_info_line(self._livebox_alist, i, lx('Enabled'), LmTools.fmt_bool(q.get('Enable')))
                i = self.add_info_line(self._livebox_alist, i, lx('Active'), LmTools.fmt_bool(q.get('Status')))
                i = self.add_info_line(self._livebox_alist, i, lx('Current Bit Rate'), LmTools.fmt_int(r.get('CurrentBitRate')))
                i = self.add_info_line(self._livebox_alist, i, lx('Max Bit Rate Supported'), LmTools.fmt_int(r.get('MaxBitRateSupported')))
                i = self.add_info_line(self._livebox_alist, i, lx('Current Duplex Mode'), r.get('CurrentDuplexMode'))
                i = self.add_info_line(self._livebox_alist, i, lx('Power Saving Supported'), LmTools.fmt_bool(q.get('PowerSavingSupported')))
                i = self.add_info_line(self._livebox_alist, i, lx('Power Saving Enabled'), LmTools.fmt_bool(q.get('PowerSavingEnabled')))

        return i


    ### Load ONT infos
    def load_ont_info(self, index=0):
        i = self.add_title_line(self._livebox_alist, index, lx('ONT Information'))

        # Call SFP module for LB4
        if self._api._info.get_livebox_model() == 4:
            try:
                d = self._api._intf.get_sfp_info()
            except Exception as e:
                LmTools.error(str(e))
                i = self.add_info_line(self._livebox_alist, i, lx('ONT'), 'SFP:get query error', LmTools.ValQual.Error)
            else:
                i = self.add_info_line(self._livebox_alist, i, lx('Status'), d.get('Status'))
                i = self.add_info_line(self._livebox_alist, i, lx('Connection Status'), LmTools.fmt_bool(d.get('ONTReady')))
                i = self.add_info_line(self._livebox_alist, i, lx('SFP Status'), LmTools.fmt_int(d.get('DeviceState')))
                i = self.add_info_line(self._livebox_alist, i, lx('Operating State'), LmTools.fmt_int(d.get('OperatingState')))
                i = self.add_info_line(self._livebox_alist, i, lx('Orange'), LmTools.fmt_bool(d.get('Orange')))
                i = self.add_info_line(self._livebox_alist, i, lx('Serial Number'), d.get('SerialNumber'))
                i = self.add_info_line(self._livebox_alist, i, lx('Registration ID'), d.get('RegistrationID'))
                i = self.add_info_line(self._livebox_alist, i, lx('Local Registration ID'), d.get('LocalRegistrationID'))
                v = d.get('OpticalSignalLevel')
                if v is not None:
                    v /= 1000
                    i = self.add_info_line(self._livebox_alist, i, lx('Signal RxPower'), str(v) + ' dBm')
                v = d.get('TransmitOpticalLevel')
                if v is not None:
                    v /= 1000
                    i = self.add_info_line(self._livebox_alist, i, lx('Signal TxPower'), str(v) + ' dBm')
                i = self.add_info_line(self._livebox_alist, i, lx('Temperature'), LmTools.fmt_int(d.get('ChipsetTemperature')) + '°')
                i = self.add_info_line(self._livebox_alist, i, lx('Model Name'), d.get('ModelName'))
                i = self.add_info_line(self._livebox_alist, i, lx('Manufacturer'), d.get('Manufacturer'))
                i = self.add_info_line(self._livebox_alist, i, lx('Hardware Version'), d.get('HardwareVersion'))
                i = self.add_info_line(self._livebox_alist, i, lx('Firmware 1 Version'), d.get('Software1Version'))
                i = self.add_info_line(self._livebox_alist, i, lx('Firmware 1 State'), LmTools.fmt_int(d.get('Software1Status')))
                i = self.add_info_line(self._livebox_alist, i, lx('Firmware 2 Version'), d.get('Software2Version'))
                i = self.add_info_line(self._livebox_alist, i, lx('Firmware 2 State'), LmTools.fmt_int(d.get('Software2Status')))
            return i

        # Get ONT info
        try:
            d = self._api._intf.get_ont_mibs()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('ONT'), 'ONT MIBs query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('VEIP PPTP UNI'), LmTools.fmt_bool(d.get('VeipPptpUni')))
            i = self.add_info_line(self._livebox_alist, i, lx('OMCI Is Tm Owner'), LmTools.fmt_bool(d.get('OmciIsTmOwner')))
            v = d.get('MaxBitRateSupported')
            if v is not None:
                i = self.add_info_line(self._livebox_alist, i, lx('Max Bit Rate Supported'), str(v / 1000) + ' Gbps')

            v = d.get('SignalRxPower')
            if v is not None:
                v /= 1000
                if self._link_type == 'XGS-PON':
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
                i = self.add_info_line(self._livebox_alist, i, lx('Signal RxPower'), str(v) + ' dBm', aQual)

            v = d.get('SignalTxPower')
            if v is not None:
                v /= 1000
                if self._link_type == 'XGS-PON':
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
                i = self.add_info_line(self._livebox_alist, i, lx('Signal TxPower'), str(v) + ' dBm', aQual)

            v = d.get('Temperature')
            if v is not None:
                if (v < -40) or (v > 100):
                    aQual = LmTools.ValQual.Error
                elif (v < -10) or (v > 70):
                    aQual = LmTools.ValQual.Warn
                else:
                    aQual = LmTools.ValQual.Good
                i = self.add_info_line(self._livebox_alist, i, lx('Temperature'), str(v) + '°', aQual)

            v = d.get('Voltage')
            if v is not None:
                v /= 10000
                if (v < 3.2) or (v > 3.4):
                    aQual = LmTools.ValQual.Error
                elif (v < 3.25) or (v > 3.35):
                    aQual = LmTools.ValQual.Warn
                else:
                    aQual = LmTools.ValQual.Good
                i = self.add_info_line(self._livebox_alist, i, lx('Voltage'), str(round(v, 2)) + ' V', aQual)

            v = d.get('Bias')
            if v is not None:
                if self._api._info.get_livebox_model() >= 6:
                    v /= 10000
                if (v < 0) or (v > 150):
                    aQual = LmTools.ValQual.Error
                elif v > 75:
                    aQual = LmTools.ValQual.Warn
                else:
                    aQual = LmTools.ValQual.Good
                i = self.add_info_line(self._livebox_alist, i, lx('BIAS'), str(v) + ' mA', aQual)

            i = self.add_info_line(self._livebox_alist, i, lx('Serial Number'), d.get('SerialNumber'))
            i = self.add_info_line(self._livebox_alist, i, lx('Hardware Version'), d.get('HardwareVersion'))
            i = self.add_info_line(self._livebox_alist, i, lx('Equipment ID'), d.get('EquipmentId'))
            i = self.add_info_line(self._livebox_alist, i, lx('Vendor ID'), d.get('VendorId'))
            i = self.add_info_line(self._livebox_alist, i, lx('Vendor Product Code'), LmTools.fmt_int(d.get('VendorProductCode')))
            i = self.add_info_line(self._livebox_alist, i, lx('Pon ID'), d.get('PonId'))
            i = self.add_info_line(self._livebox_alist, i, lx('Registration ID'), d.get('RegistrationID'))
            i = self.add_info_line(self._livebox_alist, i, lx('ONT Software Version 0'), d.get('ONTSoftwareVersion0'))
            i = self.add_info_line(self._livebox_alist, i, lx('ONT Software Version 1'), d.get('ONTSoftwareVersion1'))
            i = self.add_info_line(self._livebox_alist, i, lx('ONT Software Version Active'), LmTools.fmt_int(d.get('ONTSoftwareVersionActive')))
            i = self.add_info_line(self._livebox_alist, i, lx('ONU State'), d.get('ONUState'))
            rate = d.get('DownstreamMaxRate')
            if rate is not None:
                rate *= 1024
                i = self.add_info_line(self._livebox_alist, i, lx('Max Down Bit Rate'), LmTools.fmt_bytes(rate))
            rate = d.get('UpstreamMaxRate')
            if rate is not None:
                rate *= 1024
                i = self.add_info_line(self._livebox_alist, i, lx('Max Up Bit Rate'), LmTools.fmt_bytes(rate))
            rate = d.get('DownstreamCurrRate')
            if rate is not None:
                rate *= 1024
                i = self.add_info_line(self._livebox_alist, i, lx('Current Down Bit Rate'), LmTools.fmt_bytes(rate))
            rate = d.get('UpstreamCurrRate')
            if rate is not None:
                rate *= 1024
                i = self.add_info_line(self._livebox_alist, i, lx('Current Up Bit Rate'), LmTools.fmt_bytes(rate))

        return i


    ### Load VoIP infos
    def load_voip_info(self, index=0):
        i = self.add_title_line(self._livebox_alist, index, lx('VoIP Information'))

        try:
            d = self._api._voip.get_info()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('VoIP'), 'VoiceService.VoiceApplication:listTrunks query error', LmTools.ValQual.Error)
        else:
            for q in d:
                i = self.add_info_line(self._livebox_alist, i, lx('VoIP Enabled'), q.get('enable'))
                i = self.add_info_line(self._livebox_alist, i, lx('Protocol'), q.get('signalingProtocol'))
                aLines = q.get('trunk_lines')
                if aLines is not None:
                    for l in aLines:
                        aName = l.get('name', 'Line')
                        i = self.add_info_line(self._livebox_alist, i, lx('{} Enabled').format(aName), l.get('enable'))
                        i = self.add_info_line(self._livebox_alist, i, lx('{} Status').format(aName), l.get('status'))
                        i = self.add_info_line(self._livebox_alist, i, lx('{} Status Info').format(aName), l.get('statusInfo'))
                        i = self.add_info_line(self._livebox_alist, i, lx('{} Number').format(aName), l.get('directoryNumber'))

        # No DECT from Livebox 6
        if self._api._info.get_livebox_model() >= 6:
            return i

        i = self.add_title_line(self._livebox_alist, i, lx('DECT Information'))

        try:
            d = self._api._voip.get_dect_name()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Name'), 'DECT:getName query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('Name'), d)

        try:
            d = self._api._voip.get_dect_pin()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('PIN'), 'DECT:getPIN query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('PIN'), d)

        try:
            d = self._api._voip.get_dect_rfpi()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('RFPI'), 'DECT:getRFPI query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('RFPI'), d)

        try:
            d = self._api._voip.get_dect_software_version()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Software Version'), 'DECT:getVersion query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('Software Version'), d)

        try:
            d = self._api._voip.get_dect_catiq_version()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('CAT-iq Version'), 'DECT:getStandardVersion query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('CAT-iq Version'), d)

        try:
            d = self._api._voip.get_dect_pairing_status()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Pairing Status'), 'DECT:getPairingStatus query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('Pairing Status'), d)

        try:
            d = self._api._voip.get_dect_radio_state()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Radio State'), 'DECT:getRadioState query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('Radio State'), LmTools.fmt_bool(d))

        try:
            d = self._api._voip.get_dect_repeater_status()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Repeater Status'), 'DECT.Repeater:get query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('Repeater Status'), d.get('Status'))

        return i


    ### Load IPTV infos
    def load_iptv_info(self, index=0):
        i = self.add_title_line(self._livebox_alist, index, lx('IPTV Information'))

        try:
            d = self._api._iptv.get_status()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('IPTV Status'), 'NMC.OrangeTV:getIPTVStatus query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('IPTV Status'), d)

        try:
            d = self._api._iptv.get_multi_screens_status()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('Multi Screens Status'), 'NMC.OrangeTV:getIPTVMultiScreens query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(self._livebox_alist, i, lx('Multi Screens Status'), lx('Available') if d else lx('Disabled'))

        try:
            d = self._api._iptv.get_config()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('IPTV Config'), 'NMC.OrangeTV:IPTVConfig query error', LmTools.ValQual.Error)
        else:
            for q in d:
                names_str = ', '.join(q.get('ChannelFlags', '').split())

                status = q.get('ChannelStatus', False)
                value = lx('Available') if status else lx('Disabled')

                channel_type = q.get('ChannelType')
                if channel_type is not None:
                    value += f' - {channel_type}'
                    channel_number = q.get('ChannelNumber')
                    if channel_number is not None:
                        value += f' : {channel_number}'

                i = self.add_info_line(self._livebox_alist, i, names_str, value)

        return i


    ### Load USB infos
    def load_usb_info(self, index=0):
        i = self.add_title_line(self._livebox_alist, index, lx('USB Information'))

        try:
            d = self._api._device.get_usb()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(self._livebox_alist, i, lx('USB'), 'Devices:get query error', LmTools.ValQual.Error)
        else:
            for q in d:
                source = q.get('DiscoverySource')
                match source:
                    case 'selfusb':
                        active = lx('Active') if q.get('Active', False) else lx('Inactive')
                        i = self.add_info_line(self._livebox_alist, i, q.get('Name', lx('Unknown USB')), active)

                    case 'usb_storage':
                        i = self.add_title_line(self._livebox_alist, i, lx('USB Device Storage'))
                        i = self.add_info_line(self._livebox_alist, i, lx('Key'), q.get('Key'))
                        i = self.add_info_line(self._livebox_alist, i, lx('Device Type'), q.get('DeviceType'))
                        i = self.add_info_line(self._livebox_alist, i, lx('Active'), LmTools.fmt_bool(q.get('Active')))
                        i = self.add_info_line(self._livebox_alist, i, lx('First Seen'), LmTools.fmt_livebox_timestamp(q.get('FirstSeen')))
                        i = self.add_info_line(self._livebox_alist, i, lx('Last Connection'), LmTools.fmt_livebox_timestamp(q.get('LastConnection')))
                        i = self.add_info_line(self._livebox_alist, i, lx('File System'), q.get('FileSystem'))
                        n = q.get('Capacity')
                        if n is not None:
                            n *= 1024 * 1024
                            i = self.add_info_line(self._livebox_alist, i, lx('Capacity'), LmTools.fmt_bytes(n))
                        n = q.get('UsedSpace')
                        if n is not None:
                            n *= 1024 * 1024
                            i = self.add_info_line(self._livebox_alist, i, lx('Used Space'), LmTools.fmt_bytes(n))

                        names = q.get('Names')
                        if names:
                            name_list = ', '.join((n.get('Name', '') for n in names))
                            i = self.add_info_line(self._livebox_alist, i, lx('Names'), name_list)

                    case 'usb_dev':
                        i = self.add_title_line(self._livebox_alist, i, lx('USB Device'))
                        i = self.add_info_line(self._livebox_alist, i, lx('Name'), q.get('Name'))
                        i = self.add_info_line(self._livebox_alist, i, lx('Device Type'), q.get('DeviceType'))
                        i = self.add_info_line(self._livebox_alist, i, lx('Active'), LmTools.fmt_bool(q.get('Active')))
                        i = self.add_info_line(self._livebox_alist, i, lx('Last Connection'), LmTools.fmt_livebox_timestamp(q.get('LastConnection')))
                        i = self.add_info_line(self._livebox_alist, i, lx('Location'), q.get('Location'))
                        i = self.add_info_line(self._livebox_alist, i, lx('Owner'), q.get('Owner'))
                        i = self.add_info_line(self._livebox_alist, i, lx('USB Version'), q.get('USBVersion'))
                        i = self.add_info_line(self._livebox_alist, i, lx('Device Version'), LmTools.fmt_int(q.get('DeviceVersion')))
                        i = self.add_info_line(self._livebox_alist, i, lx('Product ID'), LmTools.fmt_int(q.get('ProductID')))
                        i = self.add_info_line(self._livebox_alist, i, lx('Vendor ID'), LmTools.fmt_int(q.get('VendorID')))
                        i = self.add_info_line(self._livebox_alist, i, lx('Manufacturer'), q.get('Manufacturer'))
                        i = self.add_info_line(self._livebox_alist, i, lx('Serial Number'), q.get('SerialNumber'))
                        i = self.add_info_line(self._livebox_alist, i, lx('Port'), LmTools.fmt_int(q.get('Port')))
                        i = self.add_info_line(self._livebox_alist, i, lx('Rate'), q.get('Rate'))

        return i



# ############# Livebox global stats collector thread #############
class LiveboxStatsThread(LmThread):
    _stats_received = QtCore.pyqtSignal(dict)
    _resume = QtCore.pyqtSignal()

    def __init__(self, api):
        super(LiveboxStatsThread, self).__init__(api, LmConf.StatsFrequency)


    def connect_processor(self, processor):
        self._stats_received.connect(processor)


    def task(self):
        # WARNING counters are recycling at 4Gb only:
        for s in self._api._intf.get_list():
            try:
                d = self._api._stats.get_intf(s['Key'])
            except Exception as e:
                LmTools.error(str(e))
            else:
                if isinstance(d, dict):
                    e = {'Key': s['Key'],
                         'Source': 'nds',     # NetDevStats
                         'Timestamp': datetime.datetime.now()}
                    if s['SwapStats']:
                        e['RxBytes'] = d.get('TxBytes', 0)
                        e['TxBytes'] = d.get('RxBytes', 0)
                        e['RxErrors'] = d.get('TxErrors', 0)
                        e['TxErrors'] = d.get('RxErrors', 0)
                    else:
                        e['RxBytes'] = d.get('RxBytes', 0)
                        e['TxBytes'] = d.get('TxBytes', 0)
                        e['RxErrors'] = d.get('RxErrors', 0)
                        e['TxErrors'] = d.get('TxErrors', 0)
                    self._stats_received.emit(e)


'''
        # EXPERIMENTAL - not successful:
        # - HomeLan:getWANCounters generates wrong HomeLan veip0 stats events
        # - HomeLan events do not cover all interfaces -> need to keep getNetDevStats()
        for s in self._api._intf.get_list():
            if s['Type'] == 'wan':
                stats = self._api._stats.get_wan_counters()    # WARNING: Works but generates wrong HomeLan veip0 stats events
                if isinstance(stats, dict):
                    e = {}
                    e['Key'] = s['Key']
                    e['Timestamp'] = datetime.datetime.now()        # WARNING - can use timestamp coming from stat itself
                    if s['SwapStats']:
                        e['RxBytes'] = stats.get('BytesSent', 0)
                        e['TxBytes'] = stats.get('BytesReceived', 0)
                        e['RxErrors'] = 0
                        e['TxErrors'] = 0
                    else:
                        e['RxBytes'] = stats.get('BytesReceived', 0)
                        e['TxBytes'] = stats.get('BytesSent', 0)
                        e['RxErrors'] = 0
                        e['TxErrors'] = 0
                    self._stats_received.emit(e)
                break

'''

'''
        # EXPERIMENTAL - not successful:
        # - Stats are not real time, not relevant.
        # - Counters look 64bits but are recycling chaotically, after 512Gb, or 3Gb, ...
        for s in self._api._intf.get_list():
            if s['Type'] == 'wan':
                stats = self._api._stats.get_wan_counters()
            else:
                stats = self._api._stats.get_intf_counters(s['Key'])
            if isinstance(stats, dict):
                e = {}
                e['Key'] = s['Key']
                e['Timestamp'] = datetime.datetime.now()
                if s['SwapStats']:
                    e['RxBytes'] = stats.get('BytesSent', 0)
                    e['TxBytes'] = stats.get('BytesReceived', 0)
                    e['RxErrors'] = 0
                    e['TxErrors'] = 0
                else:
                    e['RxBytes'] = stats.get('BytesReceived', 0)
                    e['TxBytes'] = stats.get('BytesSent', 0)
                    e['RxErrors'] = 0
                    e['TxErrors'] = 0
                self._stats_received.emit(e)
'''




