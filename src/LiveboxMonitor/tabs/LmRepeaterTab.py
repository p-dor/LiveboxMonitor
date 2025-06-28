### Livebox Monitor Wifi Repeater info tab module ###

import datetime
import re
import json

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmThread import LmThread
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmTableWidget import LmTableWidget
from LiveboxMonitor.api.LmSession import LmSession
from LiveboxMonitor.api.LmApiRegistry import ApiRegistry
from LiveboxMonitor.dlg.LmRebootHistory import RebootHistoryDialog
from LiveboxMonitor.tabs.LmInfoTab import InfoCol, StatsCol
from LiveboxMonitor.lang.LmLanguages import get_repeater_label as lx, get_repeater_message as mx


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'repeaterTab'    # 'Key' dynamic property indicates the MAC addr

# Static Config
WIFI_REPEATER_TYPES = {'repeteurwifi', 'repeteurwifi6', 'sah ap'}
WIFI_REPEATER_5 = 'WIFIREPARCFR'
WIFI_REPEATER_6 = 'WIFI6REPSERCOMM'
WIFI_REPEATER_PRODUCT_CLASSES = [WIFI_REPEATER_5, WIFI_REPEATER_6]
WIFI_REPEATER_MODEL_MAP = {WIFI_REPEATER_5: 5, WIFI_REPEATER_6: 6}
WIFI_REPEATER_DEFAULT_MODEL = 6
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
    def create_repeater_tab(self, repeater):
        repeater._tab = QtWidgets.QWidget(objectName=TAB_NAME)
        repeater._tab.setProperty('Key', repeater._key)

        # Statistics list
        stats_list = LmTableWidget(objectName='statsList')
        stats_list.set_columns({StatsCol.Key: ['Key', 0, None],
                                StatsCol.Name: [lx('Name'), 100, 'stats_Name'],
                                StatsCol.Down: [lx('Rx'), 65, 'stats_Rx'],
                                StatsCol.Up: [lx('Tx'), 65, 'stats_Tx'],
                                StatsCol.DownRate: [lx('RxRate'), 65, 'stats_RxRate'],
                                StatsCol.UpRate: [lx('TxRate'), 65, 'stats_TxRate']})
        stats_list.set_header_resize([StatsCol.Down, StatsCol.Up, StatsCol.DownRate, StatsCol.UpRate])
        stats_list.set_standard_setup(self, allow_sel=False, allow_sort=False)
        stats_list.setMinimumWidth(450)

        for i, s in enumerate(repeater._netIntf):
            stats_list.insertRow(i)
            stats_list.setItem(i, StatsCol.Key, QtWidgets.QTableWidgetItem(s['Key']))
            stats_list.setItem(i, StatsCol.Name, QtWidgets.QTableWidgetItem(s['Name']))
        stats_list_size = LmConfig.table_height(len(repeater._netIntf))
        stats_list.setMinimumHeight(stats_list_size)
        stats_list.setMaximumHeight(stats_list_size)

        repeater._stats_list = stats_list

        # 1st action buttons line
        buttons_set1 = QtWidgets.QHBoxLayout()
        buttons_set1.setSpacing(20)

        wifi_on_button = QtWidgets.QPushButton(lx('Wifi ON'), objectName='wifiOn')
        wifi_on_button.clicked.connect(repeater.wifi_on_button_click)
        buttons_set1.addWidget(wifi_on_button)

        wifi_off_button = QtWidgets.QPushButton(lx('Wifi OFF'), objectName='wifiOff')
        wifi_off_button.clicked.connect(repeater.wifi_off_button_click)
        buttons_set1.addWidget(wifi_off_button)

        # 2nd action buttons line
        if repeater._model >= 6:     # Scheduler available only starting WR6
            buttons_set2 = QtWidgets.QHBoxLayout()
            buttons_set2.setSpacing(20)

            scheduler_on_button = QtWidgets.QPushButton(lx('Wifi Scheduler ON'), objectName='schedulerOn')
            scheduler_on_button.clicked.connect(repeater.scheduler_on_button_click)
            buttons_set2.addWidget(scheduler_on_button)

            scheduler_off_button = QtWidgets.QPushButton(lx('Wifi Scheduler OFF'), objectName='schedulerOff')
            scheduler_off_button.clicked.connect(repeater.scheduler_off_button_click)
            buttons_set2.addWidget(scheduler_off_button)

        # 3nd action buttons line
        buttons_set3 = QtWidgets.QHBoxLayout()
        buttons_set3.setSpacing(20)

        reboot_repeater_button = QtWidgets.QPushButton(lx('Reboot Repeater...'), objectName='rebootRepeater')
        reboot_repeater_button.clicked.connect(repeater.reboot_repeater_button_click)
        buttons_set3.addWidget(reboot_repeater_button)

        if repeater._model >= 6:     # Reboot history available only starting WR6
            reboot_history_button = QtWidgets.QPushButton(lx('Reboot History...'), objectName='rebootHistory')
            reboot_history_button.clicked.connect(repeater.reboot_history_button_click)
            buttons_set3.addWidget(reboot_history_button)

        # 4nd action buttons line
        buttons_set4 = QtWidgets.QHBoxLayout()
        buttons_set4.setSpacing(20)

        resign_button = QtWidgets.QPushButton(lx('Resign...'), objectName='resign')
        resign_button.clicked.connect(repeater.resign_button_click)
        buttons_set4.addWidget(resign_button)

        # Debug Button
        if DEBUG_BUTTON:
            debug_button = QtWidgets.QPushButton('Debug...', objectName='debug')
            debug_button.clicked.connect(repeater.debug_button_click)

        # Action buttons group box
        group_box = QtWidgets.QGroupBox(lx('Actions'), objectName='actionsGroup')
        group_box_layout = QtWidgets.QVBoxLayout()
        group_box_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        group_box_layout.setSpacing(20)
        group_box_layout.addLayout(buttons_set1, 0)
        if repeater._model >= 6:     # Scheduler available only starting WR6
            group_box_layout.addLayout(buttons_set2, 0)
        group_box_layout.addLayout(buttons_set3, 0)
        group_box_layout.addLayout(buttons_set4, 0)
        if DEBUG_BUTTON:
            group_box_layout.addWidget(debug_button)
        group_box.setLayout(group_box_layout)

        # Stats & actions box
        left_box = QtWidgets.QVBoxLayout()
        left_box.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        left_box.setSpacing(20)
        left_box.addWidget(repeater._stats_list, 0, QtCore.Qt.AlignmentFlag.AlignTop)
        left_box.addWidget(group_box, 0, QtCore.Qt.AlignmentFlag.AlignTop)

        # Attribute list
        alist = LmTableWidget(objectName='repeaterAList')
        alist.set_columns({InfoCol.Attribute: [lx('Attribute'), 200, 'alist_Attribute'],
                           InfoCol.Value: [lx('Value'), 600, 'alist_Value']})
        alist.set_header_resize([InfoCol.Value])
        alist.set_standard_setup(self, allow_sel=False, allow_sort=False)
        repeater._alist = alist

        # Lists layout
        list_box = QtWidgets.QHBoxLayout()
        list_box.setSpacing(10)
        list_box.addLayout(left_box, 0)
        list_box.addWidget(repeater._alist, 1)

        # Button bar
        buttons_box = QtWidgets.QHBoxLayout()
        buttons_box.setSpacing(10)

        repeater_info_button = QtWidgets.QPushButton(lx('Repeater Infos'), objectName='repeaterInfo')
        repeater_info_button.clicked.connect(repeater.repeater_info_button_click)
        buttons_box.addWidget(repeater_info_button)

        wifi_info_button = QtWidgets.QPushButton(lx('Wifi Infos'), objectName='wifiInfo')
        wifi_info_button.clicked.connect(repeater.wifi_info_button_click)
        buttons_box.addWidget(wifi_info_button)

        lan_info_button = QtWidgets.QPushButton(lx('LAN Infos'), objectName='lanInfo')
        lan_info_button.clicked.connect(repeater.lan_info_button_click)
        buttons_box.addWidget(lan_info_button)

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        buttons_box.addWidget(separator)

        export_info_button = QtWidgets.QPushButton(lx('Export...'), objectName='exportInfo')
        export_info_button.clicked.connect(repeater.export_info_button_click)
        buttons_box.addWidget(export_info_button)

        # Layout
        vbox = QtWidgets.QVBoxLayout()
        vbox.setSpacing(10)
        vbox.addLayout(list_box, 0)
        vbox.addLayout(buttons_box, 1)
        repeater._tab.setLayout(vbox)

        LmConfig.set_tooltips(repeater._tab, 'repeater')
        self._tab_widget.insertTab(repeater.tab_index_from_config(), repeater._tab, repeater._name)
        repeater.set_tab_icon()


    ### Identify potential Wifi Repeater device & add it to the list
    # PowerManagement:getElements() method returns a "REPEATER_DEVICES" entry that suggests that a generic way to
    # identify repeaters could be to check the tags with the expression "ssw and (wifi or eth)"
    def identify_repeater(self, device):
        device_type = device.get('DeviceType', '')
        prod_class = device.get('ProductClass', '')

        if (device_type.lower() in WIFI_REPEATER_TYPES) or (prod_class in WIFI_REPEATER_PRODUCT_CLASSES):
            key = device.get('Key', '')

            # Check if not already there
            for r in self._repeaters:
                if r._key == key:
                    return None

            index = len(self._repeaters)

            mac_addr = device.get('PhysAddress', '')
            try:
                name = LmConf.MacAddrTable[mac_addr]
            except KeyError:
                name = DEFAULT_REPEATER_NAME + str(index + 1)

            # Determine model
            model_name = None
            ssw = device.get('SSW')
            if isinstance(ssw, dict):
                model_name = ssw.get('ModelName')
            if model_name is None:
                model_name = prod_class     # In some cases the model name is indicated in product class
            try:
                model = WIFI_REPEATER_MODEL_MAP[model_name]
            except KeyError:
                model = WIFI_REPEATER_DEFAULT_MODEL

            ip_struct = LmTools.determine_ip(device)
            ip_address = ip_struct.get('Address') if ip_struct else None

            active = device.get('Active', False)

            repeater = LmRepHandler(self, index, key, mac_addr, name, model, model_name, ip_address, active)
            self._repeaters.append(repeater)

            return repeater

        return None


    ### Add and setup a potential new Wifi Repeater device
    def add_potential_repeater(self, device):
        repeater = self.identify_repeater(device)
        if repeater:
            self.create_repeater_tab(repeater)
            repeater.signin()


    ### Find a repeater in the list from device key
    def find_repeater(self, device_key):
        return next((r for r in self._repeaters if r._key == device_key), None)


    ### Remove a potential Wifi Repeater device - not really remove, rather desactivate
    def remove_potential_repeater(self, device_key):
        repeater = self.find_repeater(device_key)
        if repeater:
            repeater.process_active_event(False)


    ### Init repeater tabs & sessions
    def init_repeaters(self):
        for r in self._repeaters:
            self.create_repeater_tab(r)
        self.signin_repeaters()


    ### Sign in to all repeaters
    def signin_repeaters(self):
        self._task.start(lx('Signing in to repeaters...'))
        try:
            for r in self._repeaters:
                r.signin()
        finally:
            self._task.end()


    ### Sign out for all repeaters
    def signout_repeaters(self):
        for r in self._repeaters:
            r.signout()


    ### React to device a name update
    def repeater_update_device_name(self, device_key):
        repeater = self.find_repeater(device_key)
        if repeater:
            repeater.process_update_device_name()


    ### React to device updated event
    def repeater_device_updated_event(self, device_key, event):
        repeater = self.find_repeater(device_key)
        if repeater:
            repeater.process_device_updated_event(event)


    ### React to active status change event
    def repeater_active_event(self, device_key, is_active):
        repeater = self.find_repeater(device_key)
        if repeater:
            repeater.process_active_event(is_active)


    ### React to IP Address change event
    def repeater_ip_address_event(self, device_key, ipv4):
        repeater = self.find_repeater(device_key)
        if repeater:
            repeater.process_ip_address_event(ipv4)


    ### Get Repeaters Wifi statuses (used by ActionsTab)
    def get_repeaters_wifi_status(self):
        return [r.get_wifi_status() for r in self._repeaters]


    ### Init the Repeater stats collector thread
    def init_repeater_stats_loop(self):
        self._repeater_stats_loop = None


    ### Start the Repeater stats collector thread
    def start_repeater_stats_loop(self):
        self._repeater_stats_loop = RepeaterStatsThread(self._repeaters)
        self._repeater_stats_loop.connect_processor(self.process_repeater_stats)


    ### Suspend the Repeater stats collector thread
    def suspend_repeater_stats_loop(self):
        if self._repeater_stats_loop:
            self._repeater_stats_loop.stop()


    ### Resume the Repeater stats collector thread
    def resume_repeater_stats_loop(self):
        if self._repeater_stats_loop:
            self._repeater_stats_loop._resume.emit()
        else:
            self.start_repeater_stats_loop()


    ### Stop the Repeater stats collector thread
    def stop_repeater_stats_loop(self):
        if self._repeater_stats_loop:
            self._repeater_stats_loop.quit()
            self._repeater_stats_loop = None


    ### Process a new Repeater stats
    def process_repeater_stats(self, stats):
        # Get stats data
        r = stats['Repeater']
        key = stats['Key']
        timestamp = stats['Timestamp']
        down_bytes = stats['RxBytes']
        up_bytes = stats['TxBytes']
        down_errors = stats['RxErrors']
        up_errors = stats['TxErrors']
        down_rate_bytes = 0
        up_rate_bytes = 0
        down_delta_errors = 0
        up_delta_errors = 0

        # Try to find a previously received statistic record
        prev_stats = r._stats_map.get(key)
        if prev_stats:
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
        r._stats_map[key] = stats

        # Update UI
        list_line = r.find_stats_line(key)
        if list_line >= 0:
            down = QtWidgets.QTableWidgetItem(LmTools.fmt_bytes(down_bytes))
            down.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
            if down_errors:
                down.setForeground(QtCore.Qt.GlobalColor.red)
            r._stats_list.setItem(list_line, StatsCol.Down, down)

            up = QtWidgets.QTableWidgetItem(LmTools.fmt_bytes(up_bytes))
            up.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
            if up_errors:
                up.setForeground(QtCore.Qt.GlobalColor.red)
            r._stats_list.setItem(list_line, StatsCol.Up, up)

            if down_rate_bytes:
                down_rate = QtWidgets.QTableWidgetItem(LmTools.fmt_bytes(down_rate_bytes) + '/s')
                if down_delta_errors:
                    down_rate.setForeground(QtCore.Qt.GlobalColor.red)
                down_rate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
            else:
                down_rate = QtWidgets.QTableWidgetItem('')
            r._stats_list.setItem(list_line, StatsCol.DownRate, down_rate)

            if up_rate_bytes:
                up_rate = QtWidgets.QTableWidgetItem(LmTools.fmt_bytes(up_rate_bytes) + '/s')
                if up_delta_errors:
                    up_rate.setForeground(QtCore.Qt.GlobalColor.red)
                up_rate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
            else:
                up_rate = QtWidgets.QTableWidgetItem('')
            r._stats_list.setItem(list_line, StatsCol.UpRate, up_rate)



# ################################ LmRepHandler class ################################
class LmRepHandler:

    ### Init handler
    def __init__(self, app, index, key, mac_addr, name, model, model_name, ip_address, active):
        self._app = app
        self._key = key
        self._mac_addr = mac_addr
        self._name = name
        self._model = model
        self._model_name = model_name
        self._ip_addr = ip_address
        self._active = active
        self._api = None
        self._signed = False
        self._tab = None
        self._index = index
        self._stats_list = None
        self._stats_map = {}
        self._alist = None
        self.set_net_intf()


    ### Set Net Interfaces according to Repeater model
    def set_net_intf(self):
        if self._model == 5:
            self._netIntf = NET_INTF_WR5
        elif self._model == 6:
            self._netIntf = NET_INTF_WR6
        else:
            self._netIntf = []


    ### Sign in to repeater
    def signin(self, force=False, silent=False):
        if (not force) and (not self.is_active()):
            return

        self.signout()

        user, password = LmConf.get_repeater_user_password(self._mac_addr)

        while True:
            session = LmSession('http://' + self._ip_addr + '/', self._name)
            try:
                # Need to ignore cookie as sessions opened with >1h cookie generate errors
                r = session.signin(user, password, True)
            except Exception as e:
                LmTools.error(str(e))
                r = -1
            if r > 0:
                self._signed = True
                break

            if r < 0:
                if not silent:
                    self._app.display_error(mx('Cannot connect to repeater {} ({}).', 'cnxErr').format(self._name, self._ip_addr))
                session = None
                self._signed = False
                break

            if silent:
                ok = False
            else:
                self._app._task.suspend()
                password, ok = QtWidgets.QInputDialog.getText(self._app, lx('Wrong repeater password'),
                                                              lx('Please enter password for repeater {0} ({1}):').format(self._name, self._ip_addr),
                                                              QtWidgets.QLineEdit.EchoMode.Password,
                                                              text=password)
                self._app._task.resume()
            if ok:
                # Remove unwanted characters from password (can be set via Paste action)
                password = re.sub('[\n\t]', '', password)
                LmConf.set_repeater_password(self._mac_addr, password)
            else:
                session = None
                self._signed = False
                break

        self._api = ApiRegistry(session, is_repeater=True) if session else None
        if self._api:
            self._api._info.set_mac(self._mac_addr)
            self._api._info.set_model(self._model)
            self._api._info.set_model_name(self._model_name)
            self._api._intf.set_list(self._netIntf)
        self.set_tab_icon()


    ### Check if signed to repeater
    def is_signed(self):
        return self._signed


    ### Sign out from repeater
    def signout(self):
        if self.is_signed():
            self._signed = False
            if self._api:
                self._api._session.close()
                self._api = None
            self.set_tab_icon()


    ### Check if active
    def is_active(self):
        return (self._ip_addr is not None) and self._active


    ### Get tab index from configuration at creation time
    def tab_index_from_config(self):
        # If no config, append
        n = self._app._tab_widget.count()
        if LmConf.Tabs is None:
            return n

        # If not in config, append
        entry_name = f'{TAB_NAME}_{self._key}'
        try:
            i = LmConf.Tabs.index(entry_name)
        except ValueError:
            return n

        # Try to find the tab immediately on the left
        for j in range(i - 1, -1, -1):
            t = LmConf.Tabs[j]
            if t.startswith(f'{TAB_NAME}_'):
                k = t[len(TAB_NAME) + 1:]
                t = TAB_NAME
            else:
                k = None

            left_tab_index = self._app.get_tab_index(t, k)
            if left_tab_index != -1:
                return left_tab_index + 1

        # No left tab found, must be the first
        return 0


    ### Get tab index
    def tab_index(self):
        if self._tab:
            return self._app._tab_widget.indexOf(self._tab)
        return -1


    ### Set tab icon according to connection status
    def set_tab_icon(self):
        if self._tab:
            if self.is_signed():
                self._app._tab_widget.setTabIcon(self.tab_index(), QtGui.QIcon(LmIcon.TickPixmap))
            elif self.is_active():
                self._app._tab_widget.setTabIcon(self.tab_index(), QtGui.QIcon(LmIcon.DenyPixmap))
            else:
                self._app._tab_widget.setTabIcon(self.tab_index(), QtGui.QIcon(LmIcon.CrossPixmap))


    ### Find Repeater stats line from stat key
    def find_stats_line(self, stats_key):
        if self._stats_list and stats_key:
            for i in range(self._stats_list.rowCount()):
                if self._stats_list.item(i, StatsCol.Key).text() == stats_key:
                    return i
        return -1


    ### Process an update of the device name
    def process_update_device_name(self):
        new_name = LmConf.MacAddrTable.get(self._key, None)
        if new_name is None:
            new_name = DEFAULT_REPEATER_NAME + str(self._index + 1)
        self._name = new_name
        self._app._tab_widget.setTabText(self.tab_index(), self._name)


    ### Process a device updated event
    def process_device_updated_event(self, event):
        ipv4_struct = LmTools.determine_ip(event)
        ipv4 = ipv4_struct.get('Address') if ipv4_struct else None
        if self._ip_addr != ipv4:
            self.process_ip_address_event(ipv4)

        self.process_active_event(event.get('Active', False))


    ### Process an active status change event
    def process_active_event(self, is_active):
        if self._active != is_active:
            if is_active:
                self._active = True
                self.signin()
            else:
                self._active = False
                self._signed = False
                self._api = None
                self.set_tab_icon()


    ### Process a IP Address change event
    def process_ip_address_event(self, ipv4):
        self._signed = False
        self._api = None
        self._ip_addr = ipv4
        self.set_tab_icon()
        self.signin()


    ### Click on Repeater infos button
    def repeater_info_button_click(self):
        if self.is_signed():
            self._app._task.start(lx('Getting repeater information...'))
            try:
                self._alist.clearContents()
                self._alist.setRowCount(0)
                self.load_repeater_info()
            finally:
                self._app._task.end()
        else:
            self._app.display_error(mx('Not signed to repeater.', 'noSign'))


    ### Click on Wifi infos button
    def wifi_info_button_click(self):
        if self.is_signed():
            self._app._task.start(lx('Getting Wifi information...'))
            try:
                self._alist.clearContents()
                self._alist.setRowCount(0)
                self.load_wifi_info()
            finally:
                self._app._task.end()
        else:
            self._app.display_error(mx('Not signed to repeater.', 'noSign'))


    ### Click on LAN infos button
    def lan_info_button_click(self):
        if self.is_signed():
            self._app._task.start(lx('Getting LAN information...'))
            try:
                self._alist.clearContents()
                self._alist.setRowCount(0)
                self.load_lan_info()
            finally:
                self._app._task.end()
        else:
            self._app.display_error(mx('Not signed to repeater.', 'noSign'))


    ### Click on Export infos button
    def export_info_button_click(self):
        if self.is_signed():
            file_name = QtWidgets.QFileDialog.getSaveFileName(self._app, lx('Save File'), lx('{} Infos.txt').format(self._name), '*.txt')[0]
            if not file_name:
                return

            try:
                self._app._export_file = open(file_name, 'w')
            except Exception as e:
                LmTools.error(str(e))
                self._app.display_error(mx('Cannot create the file.', 'createFileErr'))
                return

            self._app._task.start(lx('Exporting all information...'))

            try:
                i = 0
                i = self.load_repeater_info(i)
                i = self.load_wifi_info(i)
                i = self.load_lan_info(i)

            finally:
                self._app._task.end()

                try:
                    self._app._export_file.close()
                except Exception as e:
                    LmTools.error(str(e))
                    self._app.display_error(mx('Cannot save the file.', 'saveFileErr'))

                self._app._export_file = None
        else:
            self._app.display_error(mx('Not signed to repeater.', 'noSign'))


    ### Click on Wifi ON button
    def wifi_on_button_click(self):
        if self.is_signed():
            self._app._task.start(lx('Activating Repeater Wifi...'))
            try:
                self._api._wifi.set_enable(True)
            except Exception as e:
                self._app.display_error(str(e))
            else:
                self._app.display_status(mx('Wifi activated.', 'wifiOn'))
            finally:
                self._app._task.end()
        else:
            self._app.display_error(mx('Not signed to repeater.', 'noSign'))


    ### Click on Wifi OFF button
    def wifi_off_button_click(self):
        if self.is_signed():
            self._app._task.start(lx('Deactivating Repeater Wifi...'))
            try:
                self._api._wifi.set_enable(False)
            except Exception as e:
                self._app.display_error(str(e))
            else:
                self._app.display_status(mx('Wifi deactivated.', 'wifiOff'))
            finally:
                self._app._task.end()
        else:
            self._app.display_error(mx('Not signed to repeater.', 'noSign'))


    ### Click on Wifi Scheduler ON button
    def scheduler_on_button_click(self):
        if self.is_signed():
            self._app._task.start(lx('Activating Repeater Scheduler...'))
            try:
                self._api._wifi.set_scheduler_enable(True)
            except Exception as e:
                self._app.display_error(str(e))
            else:
                self._app.display_status(mx('Scheduler activated.', 'schedOn'))
            finally:
                self._app._task.end()
        else:
            self._app.display_error(mx('Not signed to repeater.', 'noSign'))


    ### Click on Wifi Scheduler OFF button
    def scheduler_off_button_click(self):
        if self.is_signed():
            self._app._task.start(lx('Deactivating Repeater Scheduler...'))
            try:
                self._api._wifi.set_scheduler_enable(False)
            except Exception as e:
                self._app.display_error(str(e))
            else:
                self._app.display_status(mx('Scheduler deactivated.', 'schedOff'))
            finally:
                self._app._task.end()
        else:
            self._app.display_error(mx('Not signed to repeater.', 'noSign'))


    ### Click on Reboot Repeater button
    def reboot_repeater_button_click(self):
        if self.is_signed():
            if self._app.ask_question(mx('Are you sure you want to reboot the Repeater?', 'reboot')):
                self._app._task.start(lx('Rebooting Repeater...'))
                try:
                    self._api._reboot.reboot_device(reason='WebUI reboot')
                except Exception as e:
                    self._app.display_error(str(e))
                else:
                    self._app.display_status(mx('Repeater is now restarting.', 'rebooting'))
                finally:
                    self._app._task.end()
        else:
            self._app.display_error(mx('Not signed to repeater.', 'noSign'))


    ### Click on Reboot History button
    def reboot_history_button_click(self):
        if self.is_signed():
            self._app._task.start(lx('Getting Reboot History...'))
            try:
                d = self._api._reboot.get_history()
            except Exception as e:
                self._app.display_error(str(e))
                return
            finally:
                self._app._task.end()

            history_dialog = RebootHistoryDialog('Repeater', self._app)
            history_dialog.load_history(d)
            history_dialog.exec()
        else:
            self._app.display_error(mx('Not signed to repeater.', 'noSign'))


    ### Click on Resign button
    def resign_button_click(self):
        do_it = False
        force_it = False
        if self.is_active():
            do_it = self._app.ask_question(mx('Are you sure you want to resign to the Repeater?', 'resign'))
        else:
            do_it = self._app.ask_question(mx('Repeater is inactive. Do you want to force signin?', 'forceResign'))
            force_it = True
        if do_it:
            self._app._task.start(lx('Signing in to repeater...'))
            try:
                self.signin(force_it)
            finally:
                self._app._task.end()

            # Sometimes the active event isn't raised
            if self.is_signed():
                self._active = True


    ### Click on Debug button
    def debug_button_click(self):
        if self.is_signed():
            self._app._task.start()
            try:
                d = self._api._intf.get_raw_mibs_data()
            except Exception as e:
                self._app.display_error(str(e))
            else:
                self._app.display_infos('NeMo.Intf.data:getMIBs', json.dumps(d, indent=2))
            finally:
                self._app._task.end()

            self._app._task.start()
            try:
                d = self._api._intf.get_raw_mibs_lan()
            except Exception as e:
                self._app.display_error(str(e))
            else:
                self._app.display_infos('NeMo.Intf.lan:getMIBs', json.dumps(d, indent=2))
            finally:
                self._app._task.end()
        else:
            self._app.display_error(mx('Not signed to repeater.', 'noSign'))


    ### Add a title line in an info attribute/value list
    def add_title_line(self, line, title):
        return self._app.add_title_line(self._alist, line, title)


    ### Add a line in an info attribute/value list
    def add_info_line(self, line, attribute, value, qualifier=LmTools.ValQual.Default):
        return self._app.add_info_line(self._alist, line, attribute, value, qualifier)


    ### Load Repeater infos
    def load_repeater_info(self, index=0):
        i = self.add_title_line(index, lx('Repeater Information'))

        try:
            d = self._api._info.get_device_info()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(i, lx('Repeater Infos'), 'DeviceInfo:get query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(i, lx('Model Name'), d.get('ModelName'))
            i = self.add_info_line(i, lx('Repeater Up Time'), LmTools.fmt_time(d.get('UpTime')))
            i = self.add_info_line(i, lx('Serial Number'), d.get('SerialNumber'))
            i = self.add_info_line(i, lx('Hardware Version'), d.get('HardwareVersion'))
            i = self.add_info_line(i, lx('Software Version'), d.get('SoftwareVersion'))
            i = self.add_info_line(i, lx('Orange Firmware Version'), d.get('AdditionalSoftwareVersion'))
            i = self.add_info_line(i, lx('Country'), LmTools.fmt_str_upper(d.get('Country')))

        try:
            d = self._api._reboot.get_info()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(i, lx('Repeater Infos'), 'NMC.Reboot:get query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(i, lx('Total Number Of Reboots'), LmTools.fmt_int(d.get('BootCounter')))

        try:
            d = self._api._info.get_time()
        except Exception as e:
            i = self.add_info_line(i, lx('Time'), 'Time:getTime query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(i, lx('Time'), d.get('time'))

        # Unfortunately DeviceInfo.MemoryStatus:get service access is denied.

        return i


    ### Load Wifi infos
    def load_wifi_info(self, index=0):
        i = self.add_title_line(index, lx('Wifi Information'))

        try:
            d = self._api._wifi.get_status()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(i, lx('Wifi'), 'NMC.Wifi:get query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(i, lx('Enabled'), LmTools.fmt_bool(d.get('Enable')))
            i = self.add_info_line(i, lx('Active'), LmTools.fmt_bool(d.get('Status')))
            i = self.add_info_line(i, lx('Mode'), d.get('EnableTarget'))
            i = self.add_info_line(i, lx('WPS Mode'), d.get('WPSMode'))
            i = self.add_info_line(i, lx('Link Type'), d.get('CurrentBackhaul'))
            i = self.add_info_line(i, lx('Read Only'), LmTools.fmt_bool(d.get('ReadOnlyStatus')))
            i = self.add_info_line(i, lx('Pairing Status'), d.get('PairingStatus'))
            i = self.add_info_line(i, lx('PIN Code'), d.get('PINCode'))

        if self._api._wifi.has_scheduler():
            try:
                d = self._api._wifi.get_scheduler_enable()
            except Exception as e:
                LmTools.error(str(e))
                i = self.add_info_line(i, lx('Scheduler Enabled'), 'Scheduler:getCompleteSchedules query error', LmTools.ValQual.Error)
            else:
                 i = self.add_info_line(i, lx('Scheduler Enabled'), LmTools.fmt_bool(d))


        try:
            b, w, d = self._api._intf.get_wifi_mibs()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(i, lx('Wifi'), 'NeMo.Intf.lan:getMIBs query error', LmTools.ValQual.Error)
        else:
            for s in self._netIntf:
                if s['Type'] != 'wif':
                    continue
                i = self.add_title_line(i, s['Name'])

                # Get Wifi interface key in wlanradio list
                intf_key = None
                base = b.get(s['Key'])
                if base is not None:
                    i = self.add_info_line(i, lx('Enabled'), LmTools.fmt_bool(base.get('Enable')))
                    i = self.add_info_line(i, lx('Active'), LmTools.fmt_bool(base.get('Status')))
                    low_level_intf = base.get('LLIntf')
                    if low_level_intf is not None:
                        intf_key = next(iter(low_level_intf))

                q = w.get(intf_key) if intf_key is not None else None
                r = d.get(s['Key'])
                if (q is None) or (r is None):
                    continue

                i = self.add_info_line(i, lx('Radio Status'), q.get('RadioStatus'))
                i = self.add_info_line(i, lx('VAP Status'), r.get('VAPStatus'))
                i = self.add_info_line(i, lx('Vendor Name'), LmTools.fmt_str_upper(q.get('VendorName')))
                i = self.add_info_line(i, lx('MAC Address'), LmTools.fmt_str_upper(r.get('MACAddress')))
                i = self.add_info_line(i, lx('SSID'), r.get('SSID'))
                i = self.add_info_line(i, lx('SSID Advertisement'), LmTools.fmt_bool(r.get('SSIDAdvertisementEnabled')))

                t = r.get('Security')
                if t is not None:
                    i = self.add_info_line(i, lx('Security Mode'), t.get('ModeEnabled'))
                    i = self.add_info_line(i, lx('WEP Key'), t.get('WEPKey'))
                    i = self.add_info_line(i, lx('PreShared Key'), t.get('PreSharedKey'))
                    i = self.add_info_line(i, lx('Key Pass Phrase'), t.get('KeyPassPhrase'))

                t = r.get('WPS')
                if t is not None:
                    i = self.add_info_line(i, lx('WPS Enabled'), LmTools.fmt_bool(t.get('Enable')))
                    i = self.add_info_line(i, lx('WPS Methods'), t.get('ConfigMethodsEnabled'))
                    i = self.add_info_line(i, lx('WPS Self PIN'), t.get('SelfPIN'))
                    i = self.add_info_line(i, lx('WPS Pairing In Progress'), LmTools.fmt_bool(t.get('PairingInProgress')))

                t = r.get('MACFiltering')
                if t is not None:
                    i = self.add_info_line(i, lx('MAC Filtering'), t.get('Mode'))

                i = self.add_info_line(i, lx('Max Bitrate'), LmTools.fmt_int(q.get('MaxBitRate')))
                i = self.add_info_line(i, lx('AP Mode'), LmTools.fmt_bool(q.get('AP_Mode')))
                i = self.add_info_line(i, lx('STA Mode'), LmTools.fmt_bool(q.get('STA_Mode')))
                i = self.add_info_line(i, lx('WDS Mode'), LmTools.fmt_bool(q.get('WDS_Mode')))
                i = self.add_info_line(i, lx('WET Mode'), LmTools.fmt_bool(q.get('WET_Mode')))
                i = self.add_info_line(i, lx('Frequency Band'), q.get('OperatingFrequencyBand'))
                i = self.add_info_line(i, lx('Channel Bandwidth'), q.get('CurrentOperatingChannelBandwidth'))
                i = self.add_info_line(i, lx('Standard'), q.get('OperatingStandards'))
                i = self.add_info_line(i, lx('Channel'), LmTools.fmt_int(q.get('Channel')))
                i = self.add_info_line(i, lx('Auto Channel Supported'), LmTools.fmt_bool(q.get('AutoChannelSupported')))
                i = self.add_info_line(i, lx('Auto Channel Enabled'), LmTools.fmt_bool(q.get('AutoChannelEnable')))
                i = self.add_info_line(i, lx('Channel Change Reason'), q.get('ChannelChangeReason'))
                i = self.add_info_line(i, lx('Max Associated Devices'), LmTools.fmt_int(q.get('MaxAssociatedDevices')))
                i = self.add_info_line(i, lx('Active Associated Devices'), LmTools.fmt_int(q.get('ActiveAssociatedDevices')))
                i = self.add_info_line(i, lx('Noise'), LmTools.fmt_int(q.get('Noise')))
                i = self.add_info_line(i, lx('Antenna Defect'), LmTools.fmt_bool(q.get('AntennaDefect')))

        return i


    ### Load LAN infos
    def load_lan_info(self, index=0):
        i = self.add_title_line(index, lx('LAN Information'))

        try:
            d = self._api._info.get_wan_status()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(i, lx('LAN Infos'), 'NMC:getWANStatus query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(i, lx('MAC Address'), LmTools.fmt_str_upper(d.get('MACAddress')))
            i = self.add_info_line(i, lx('Link Status'), LmTools.fmt_str_capitalize(d.get('LinkState')))
            i = self.add_info_line(i, lx('Link Type'), LmTools.fmt_str_upper(d.get('LinkType')))
            i = self.add_info_line(i, lx('Protocol'), LmTools.fmt_str_upper(d.get('Protocol')))
            i = self.add_info_line(i, lx('Connection Status'), d.get('ConnectionState'))
            i = self.add_info_line(i, lx('Last Connection Error'), d.get('LastConnectionError'))
            i = self.add_info_line(i, lx('IP Address'), d.get('IPAddress'))
            i = self.add_info_line(i, lx('Remote Gateway'), d.get('RemoteGateway'))
            i = self.add_info_line(i, lx('DNS Servers'), d.get('DNSServers'))
            i = self.add_info_line(i, lx('IPv6 Address'), d.get('IPv6Address'))

        try:
            d = self._api._info.get_mtu()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(i, lx('MTU'), 'NeMo.Intf.data:getFirstParameter query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(i, lx('MTU'), LmTools.fmt_int(d))

        i = self.add_title_line(i, lx('Link to the Livebox'))

        try:
            d = self._api._info.get_uplink_info()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(i, lx('Livebox link Infos'), 'UplinkMonitor.DefaultGateway:get query error', LmTools.ValQual.Error)
        else:
            i = self.add_info_line(i, lx('IP Address'), d.get('IPv4Address'))
            i = self.add_info_line(i, lx('MAC Address'), LmTools.fmt_str_upper(d.get('MACAddress')))
            i = self.add_info_line(i, lx('Interface'), LmTools.fmt_str_capitalize(d.get('NeMoIntfName')))

        try:
            b, d = self._api._intf.get_eth_mibs()
        except Exception as e:
            LmTools.error(str(e))
            i = self.add_info_line(i, lx('LAN'), 'NeMo.Intf.lan:getMIBs query error', LmTools.ValQual.Error)
        else:
            for s in self._netIntf:
                if s['Type'] != 'eth':
                    continue
                i = self.add_title_line(i, s['Name'])

                q = b.get(s['Key'])
                r = d.get(s['Key'])
                if (q is None) or (r is None):
                    continue

                i = self.add_info_line(i, lx('Enabled'), LmTools.fmt_bool(q.get('Enable')))
                i = self.add_info_line(i, lx('Active'), LmTools.fmt_bool(q.get('Status')))
                i = self.add_info_line(i, lx('Current Bit Rate'), LmTools.fmt_int(r.get('CurrentBitRate')))
                i = self.add_info_line(i, lx('Max Bit Rate Supported'), LmTools.fmt_int(r.get('MaxBitRateSupported')))
                i = self.add_info_line(i, lx('Current Duplex Mode'), r.get('CurrentDuplexMode'))
                i = self.add_info_line(i, lx('Power Saving Supported'), LmTools.fmt_bool(q.get('PowerSavingSupported')))
                i = self.add_info_line(i, lx('Power Saving Enabled'), LmTools.fmt_bool(q.get('PowerSavingEnabled')))

        return i


    ### Get Wifi statuses (used by ActionsTab)
    def get_wifi_status(self):
        return self._api._wifi.get_global_wifi_status(self._name, self.is_active(), self.is_signed())



# ############# Repeaters global stats collector thread #############
class RepeaterStatsThread(LmThread):
    _stats_received = QtCore.pyqtSignal(dict)
    _resume = QtCore.pyqtSignal()

    def __init__(self, repeaters):
        super().__init__(None, LmConf.StatsFrequency)
        self._repeaters = repeaters


    def connect_processor(self, processor):
        self._stats_received.connect(processor)


    def task(self):
        for r in self._repeaters:
            if r.is_signed():
                for s in r._netIntf:
                    if r._api is not None:
                        try:
                            d = r._api._stats.get_intf(s['Key'])
                        except Exception as e:
                            LmTools.error(str(e))
                            # If session has timed out on Repeater side, resign
                            r.signin(silent=True)
                        else:
                            if isinstance(d, dict):
                                e = {'Repeater': r,
                                     'Key': s['Key'],
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
 