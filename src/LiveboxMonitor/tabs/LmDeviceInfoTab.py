### Livebox Monitor device info tab module ###

import requests
import json

from PyQt6 import QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmTableWidget import LmTableWidget
from LiveboxMonitor.tabs.LmDeviceListTab import DSelCol
from LiveboxMonitor.tabs.LmInfoTab import InfoCol
from LiveboxMonitor.dlg.LmDeviceName import SetDeviceNameDialog
from LiveboxMonitor.dlg.LmDeviceType import SetDeviceTypeDialog
from LiveboxMonitor.lang.LmLanguages import get_device_info_label as lx, get_device_info_message as mx


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'deviceInfoTab'

# Static Config
MACADDR_URL = 'https://api.macaddress.io/v1?apiKey={0}&output=json&search={1}'



# ################################ LmDeviceInfo class ################################
class LmDeviceInfo:

    ### Create device info tab
    def create_device_info_tab(self):
        self._device_info_tab = QtWidgets.QWidget(objectName=TAB_NAME)

        # Device list
        self._info_dlist = LmTableWidget(objectName='infoDList')
        self._info_dlist.set_columns({DSelCol.Key: ['Key', 0, None],
                                     DSelCol.Name: [lx('Name'), 200, 'dlist_Name'],
                                     DSelCol.MAC: [lx('MAC'), 120, 'dlist_MAC']})
        self._info_dlist.set_header_resize([DSelCol.MAC])
        self._info_dlist.set_standard_setup(self)
        self._info_dlist.setMinimumWidth(350)
        self._info_dlist.itemSelectionChanged.connect(self.info_device_list_click)

        # Attribute list
        self._info_alist = LmTableWidget(objectName='infoAList')
        self._info_alist.set_columns({InfoCol.Attribute: [lx('Attribute'), 200, 'alist_Attribute'],
                                     InfoCol.Value: [lx('Value'), 600, 'alist_Value']})
        self._info_alist.set_header_resize([InfoCol.Value])
        self._info_alist.set_standard_setup(self, allow_sel=False, allow_sort=False)

        # Lists layout
        list_box = QtWidgets.QHBoxLayout()
        list_box.setSpacing(10)
        list_box.addWidget(self._info_dlist, 0)
        list_box.addWidget(self._info_alist, 1)

        # Button bar
        buttons_box = QtWidgets.QHBoxLayout()
        buttons_box.setSpacing(30)
        refresh_device_info_button = QtWidgets.QPushButton(lx('Refresh'), objectName='refresh')
        refresh_device_info_button.clicked.connect(self.refresh_device_info_button_click)
        buttons_box.addWidget(refresh_device_info_button)
        assign_name_button = QtWidgets.QPushButton(lx('Assign Name...'), objectName='assignName')
        assign_name_button.clicked.connect(self.assign_name_button_click)
        buttons_box.addWidget(assign_name_button)
        assign_type_button = QtWidgets.QPushButton(lx('Assign Type...'), objectName='assignType')
        assign_type_button.clicked.connect(self.assign_type_button_click)
        buttons_box.addWidget(assign_type_button)
        forget_button = QtWidgets.QPushButton(lx('Forget...'), objectName='forget')
        forget_button.clicked.connect(self.forget_button_click)
        buttons_box.addWidget(forget_button)
        wol_button = QtWidgets.QPushButton(lx('WakeOnLAN'), objectName='wol')
        wol_button.clicked.connect(self.wol_button_click)
        buttons_box.addWidget(wol_button)
        block_device_button = QtWidgets.QPushButton(lx('Block'), objectName='block')
        block_device_button.clicked.connect(self.block_device_button_click)
        buttons_box.addWidget(block_device_button)
        unblock_device_button = QtWidgets.QPushButton(lx('Unblock'), objectName='unblock')
        unblock_device_button.clicked.connect(self.unblock_device_button_click)
        buttons_box.addWidget(unblock_device_button)

        # Layout
        vbox = QtWidgets.QVBoxLayout()
        vbox.setSpacing(10)
        vbox.addLayout(list_box, 0)
        vbox.addLayout(buttons_box, 1)
        self._device_info_tab.setLayout(vbox)

        LmConfig.set_tooltips(self._device_info_tab, 'dinfo')
        self._tab_widget.addTab(self._device_info_tab, lx('Device Infos'))

        # Init context
        self.init_device_context()


    ### Init selected device context
    def init_device_context(self):
        self._current_device_livebox_name = None
        self._current_device_dns_name = None
        self._current_device_type = ''


    ### Get selected device key - returns None if no selection
    def get_selected_device_key(self, display_error=True):
        current_selection = self._info_dlist.currentRow()
        if current_selection >= 0:
            return self._info_dlist.item(current_selection, DSelCol.Key).text()
        if display_error:
            self.display_error(mx('Please select a device.', 'devSelect'))
        return None


    ### Click on info device list
    def info_device_list_click(self):
        self._info_alist.clearContents()
        self._info_alist.setRowCount(0)

        key = self.get_selected_device_key(False)
        if key:
            self.update_device_info(key)


    ### Click on device infos refresh button
    def refresh_device_info_button_click(self):
        self.info_device_list_click()


    ### Click on assign device name button
    def assign_name_button_click(self):
        key = self.get_selected_device_key()
        if key:
            name = LmConf.MacAddrTable.get(key)

            set_device_name_dialog = SetDeviceNameDialog(key, name, self._current_device_livebox_name, self._current_device_dns_name, self)
            if set_device_name_dialog.exec():
                # Updade local name
                name = set_device_name_dialog.get_name()
                if name is None:
                    self.del_device_name(key)
                else:
                    self.set_device_name(key, name)

                try:
                    # Update Livebox name
                    name = set_device_name_dialog.get_livebox_name()
                    if name is None:
                        self._api._device.del_name(key)
                    else:
                        self._api._device.set_name(key, name)

                    # Update DNS name
                    name = set_device_name_dialog.get_dns_name()
                    if name is None:
                        if self._current_device_dns_name is not None:
                            self._api._device.del_dns_name(key)
                    else:
                        self._api._device.set_dns_name(key, name)
                except BaseException as e:
                    self.display_error(str(e))


    ### Refresh device info if the passed key is the selected one
    def refresh_device_if_selected(self, device_key):
        key = self.get_selected_device_key(False)
        if key and (key == device_key):
            self.info_device_list_click()


    ### Set a device name stored in the the MacAddr table
    def set_device_name(self, device_key, device_name):
        current_name = LmConf.MacAddrTable.get(device_key)
        if current_name != device_name:
            LmConf.MacAddrTable[device_key] = device_name
            LmConf.save_mac_addr_table()
            self.updateDeviceName(device_key)


    ### Delete a device name from the MacAddr table
    def del_device_name(self, device_key):
        try:
            del LmConf.MacAddrTable[device_key]
        except:
            pass
        else:
            LmConf.save_mac_addr_table()
            self.updateDeviceName(device_key)


    ### Click on assign device type button
    def assign_type_button_click(self):
        key = self.get_selected_device_key()
        if key:
            self._task.start(lx('Loading device icons...'))
            LmConf.load_device_icons(self._api._info.get_software_version())
            self._task.end()

            set_device_type_dialog = SetDeviceTypeDialog(key, self._current_device_type, self)
            if set_device_type_dialog.exec():
                type = set_device_type_dialog.get_type_key()
                try:
                    self._api._device.set_type(key, type)
                except BaseException as e:
                    self.display_error(str(e))
                else:
                    self.info_device_list_click()
                    self._current_device_type = type     # LB device type update is async and refresh screen might be too fast


    ### Click on WakeOnLAN button
    def wol_button_click(self):
        key = self.get_selected_device_key()
        if key:
            try:
                self._api._device.wake_on_lan(key)
            except BaseException as e:
                self.display_error(str(e))
            else:
                self.display_status(mx('Wake on LAN signal sent to device [{}].', 'devWOL').format(key))


    ### Click on forget device button
    def forget_button_click(self):
        key = self.get_selected_device_key()
        if key:
            if self.ask_question(mx('Are you sure you want to forget device [{}]?', 'devForget').format(key)):
                try:
                    self._api._device.delete(key)
                except BaseException as e:
                    self.display_error(str(e))
                else:
                    self._info_dlist.setCurrentCell(-1, -1)
                    # Call event handler directly - in some (unknown) cases, the event is not raised
                    self.processDeviceDeletedEvent(key)


    ### Click on block device button
    def block_device_button_click(self):
        key = self.get_selected_device_key()
        if key:
            try:
                self._api._device.block(key)
            except BaseException as e:
                self.display_error(str(e))
            else:
                self.display_status(mx('Device [{}] now blocked.', 'devBlocked').format(key))


    ### Click on unblock device button
    def unblock_device_button_click(self):
        key = self.get_selected_device_key()
        if key:
            try:
                r = self._api._device.unblock(key)
            except BaseException as e:
                self.display_error(str(e))
            else:
                if r:
                    self.display_status(mx('Device [{}] now unblocked.', 'devUnblocked').format(key))
                else:
                    self.display_status(mx('Device [{}] is not blocked.', 'devNotBlocked').format(key))


    ### Update device infos list
    def update_device_info(self, device_key):
        self._task.start(lx('Getting device information...'))

        try:
            d = self._api._device.get_info(device_key)
        except BaseException as e:
            LmTools.error(str(e))
            self._task.end()
            self.display_error(mx('Error getting device information.', 'devInfoErr'))
            return

        i = 0
        i = self.addInfoLine(self._info_alist, i, lx('Key'), device_key)
        i = self.addInfoLine(self._info_alist, i, lx('Active'), LmTools.fmt_bool(d.get('Active')))
        i = self.addInfoLine(self._info_alist, i, lx('Authenticated'), LmTools.fmt_bool(d.get('AuthenticationState')))

        try:
            blocked = self._api._device.is_blocked(device_key)
            i = self.addInfoLine(self._info_alist, i, lx('Blocked'), LmTools.fmt_bool(blocked))
        except BaseException as e:
            LmTools.error(str(e))
            i = self.addInfoLine(self._info_alist, i, lx('Blocked'), 'Scheduler:getSchedule query error', LmTools.ValQual.Error)

        i = self.addInfoLine(self._info_alist, i, lx('First connection'), LmTools.fmt_livebox_timestamp(d.get('FirstSeen')))
        i = self.addInfoLine(self._info_alist, i, lx('Last connection'), LmTools.fmt_livebox_timestamp(d.get('LastConnection')))
        i = self.addInfoLine(self._info_alist, i, lx('Last changed'), LmTools.fmt_livebox_timestamp(d.get('LastChanged')))
        i = self.addInfoLine(self._info_alist, i, lx('Source'), d.get('DiscoverySource'))

        self._current_device_livebox_name = d.get('Name')
        i = self.addInfoLine(self._info_alist, i, lx('Livebox Name'), self._current_device_livebox_name)

        self._current_device_dns_name = None
        name_list = d.get('Names', [])
        if len(name_list):
            for name in name_list:
                name_str = name.get('Name', '')
                source = name.get('Source', '')
                if source == 'dns':
                    self._current_device_dns_name = name_str
                i = self.addInfoLine(self._info_alist, i, lx('Name'), name_str + ' (' + source + ')')
        
        dns_list = d.get('mDNSService', [])
        if len(dns_list):
            for dns_name in dns_list:
                i = self.addInfoLine(self._info_alist, i, lx('DNS Name'), dns_name.get('Name', '') + ' (' + dns_name.get('ServiceName', '') + ')')

        self._current_device_type = d.get('DeviceType', '')

        type_list = d.get('DeviceTypes', [])
        if len(type_list):
            for type in type_list:
                i = self.addInfoLine(self._info_alist, i, lx('Type'), type.get('Type', '') + ' (' + type.get('Source', '') + ')')

        active_ip_struct = LmTools.determine_ip(d)
        if active_ip_struct is not None:
            active_ip = active_ip_struct.get('Address', '')
        else:
            active_ip = ''
        ipv4_list = d.get('IPv4Address', [])
        if len(ipv4_list):
            for ipv4 in ipv4_list:
                ip = ipv4.get('Address', '')
                s = ip + ' ('
                if (len(active_ip) > 0) and (active_ip == ip):
                    s += 'active, '
                s += ipv4.get('Status', '') + ')'

                if ipv4.get('Reserved', False):
                    s += ' - Reserved'
                i = self.addInfoLine(self._info_alist, i, lx('IPv4 Address'), s)

        ipv6_list = d.get('IPv6Address', [])
        if len(ipv6_list):
            for ipv6 in ipv6_list:
                i = self.addInfoLine(self._info_alist, i, lx('IPv6 Address'), ipv6.get('Address', '') +
                                                                              ' [' + ipv6.get('Scope', '') + ']' +
                                                                              ' (' + ipv6.get('Status', '') + ')')

        mac_addr = d.get('PhysAddress', '')
        if len(mac_addr) == 0:
            mac_addr = device_key
        manufacturer = ''
        if (len(LmConf.MacAddrApiKey)) and (len(mac_addr)):
            try:
                data = requests.get(MACADDR_URL.format(LmConf.MacAddrApiKey, mac_addr), timeout=2)
                data = json.loads(data.content)
                comp_details = data.get('vendorDetails')
                if comp_details is not None:
                    manufacturer = comp_details.get('companyName', '') + ' - ' + comp_details.get('countryCode', '')
                i = self.addInfoLine(self._info_alist, i, lx('Manufacturer'), manufacturer)
            except BaseException as e:
                LmTools.error(str(e))
                i = self.addInfoLine(self._info_alist, i, lx('Manufacturer'), 'Web query error', LmTools.ValQual.Error)

        i = self.addInfoLine(self._info_alist, i, lx('Vendor ID'), d.get('VendorClassID'))
        i = self.addInfoLine(self._info_alist, i, lx('Serial Number'), d.get('SerialNumber'))
        i = self.addInfoLine(self._info_alist, i, lx('Product Class'), d.get('ProductClass'))
        i = self.addInfoLine(self._info_alist, i, lx('Model Name'), d.get('ModelName'))
        i = self.addInfoLine(self._info_alist, i, lx('Software Version'), d.get('SoftwareVersion'))
        i = self.addInfoLine(self._info_alist, i, lx('Hardware Version'), d.get('HardwareVersion'))
        i = self.addInfoLine(self._info_alist, i, lx('DHCP Option 55'), d.get('DHCPOption55'))

        sys_software = d.get('SSW')
        if sys_software is not None:
            i = self.addInfoLine(self._info_alist, i, lx('Full Software Version'), sys_software.get('SoftwareVersion'))
            i = self.addInfoLine(self._info_alist, i, lx('State'), sys_software.get('State'))
            i = self.addInfoLine(self._info_alist, i, lx('Protocol'), sys_software.get('Protocol'))
            i = self.addInfoLine(self._info_alist, i, lx('Current Mode'), sys_software.get('CurrentMode'))
            i = self.addInfoLine(self._info_alist, i, lx('Pairing Time'), LmTools.fmt_livebox_timestamp(sys_software.get('PairingTime')))
            i = self.addInfoLine(self._info_alist, i, lx('Uplink Type'), sys_software.get('UplinkType'))

        signal_strength = LmTools.fmt_int(d.get('SignalStrength'))
        if len(signal_strength):
            signal_strength += ' dBm'
        i = self.addInfoLine(self._info_alist, i, lx('Wifi Signal Strength'), signal_strength)
        i = self.addInfoLine(self._info_alist, i, lx('Wifi Signal Noise Ratio'), LmTools.fmt_int(d.get('SignalNoiseRatio')))
        i = self.addInfoLine(self._info_alist, i, lx('Encryption Mode'), d.get('EncryptionMode'))
        i = self.addInfoLine(self._info_alist, i, lx('Security Mode'), d.get('SecurityModeEnabled'))
        i = self.addInfoLine(self._info_alist, i, lx('Link Bandwidth'), d.get('LinkBandwidth'))
        i = self.addInfoLine(self._info_alist, i, lx('Operating Standard'), d.get('OperatingStandard'))
        i = self.addInfoLine(self._info_alist, i, lx('Operating Band'), d.get('OperatingFrequencyBand'))


        sys_software_std = d.get('SSWSta')
        if sys_software_std is not None:
            i = self.addInfoLine(self._info_alist, i, lx('Supported Standards'), sys_software_std.get('SupportedStandards'))
            i = self.addInfoLine(self._info_alist, i, lx('Supports 2.4GHz'), LmTools.fmt_bool(sys_software_std.get('Supports24GHz')))
            i = self.addInfoLine(self._info_alist, i, lx('Supports 5GHz'), LmTools.fmt_bool(sys_software_std.get('Supports5GHz')))
            i = self.addInfoLine(self._info_alist, i, lx('Supports 6GHz'), LmTools.fmt_bool(sys_software_std.get('Supports6GHz')))

        self._task.end()
