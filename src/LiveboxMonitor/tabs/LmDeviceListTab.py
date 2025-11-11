### Livebox Monitor device list tab module ###

import datetime

from enum import IntEnum
from ipaddress import IPv4Address

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmThread import LmThread
from LiveboxMonitor.app.LmTableWidget import LmTableWidget, NumericSortItem, CenteredIconsDelegate
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.tabs.LmDhcpTab import DhcpCol
from LiveboxMonitor.tabs.LmRepeaterTab import INTF_NAME_MAP_WR
from LiveboxMonitor.dlg.LmIPv6 import IPv6Dialog
from LiveboxMonitor.dlg.LmDns import DnsDialog
from LiveboxMonitor.lang.LmLanguages import get_device_list_label as lx, get_device_list_message as mx
from LiveboxMonitor.util import LmUtils


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = "deviceListTab"

# List columns
class DevCol(IntEnum):
    Key = 0
    Type = 1
    Name = 2
    LBName = 3
    MAC = 4
    IP = 5
    Link = 6
    Active = 7
    Wifi = 8
    Event = 9
    Down = 10
    Up = 11
    DownRate = 12
    UpRate = 13
ICON_COLUMNS = [DevCol.Type, DevCol.Active, DevCol.Wifi, DevCol.Event]

class DSelCol(IntEnum):
    Key = 0     # Must be the same as DevCol.Key
    Name = 1
    MAC = 2


# ################################ LmDeviceList class ################################
class LmDeviceList:

    ### Create device list tab
    def create_device_list_tab(self):
        self._device_list_tab = QtWidgets.QWidget(objectName=TAB_NAME)

        # Device list columns
        self._device_list = LmTableWidget(objectName="deviceList")
        self._device_list.set_columns({DevCol.Key: ["Key", 0, None],
                                       DevCol.Type: [lx("T"), 48, "dlist_Type"],
                                       DevCol.Name: [lx("Name"), 400, "dlist_Name"],
                                       DevCol.LBName: [lx("Livebox Name"), 400, "dlist_LBName"],
                                       DevCol.MAC: [lx("MAC"), 120, "dlist_MAC"],
                                       DevCol.IP: [lx("IP"), 105, "dlist_IP"],
                                       DevCol.Link: [lx("Link"), 150, "dlist_Link"],
                                       DevCol.Active: [lx("A"), 10, "dlist_Active"],
                                       DevCol.Wifi: [lx("Wifi"), 70, "dlist_Wifi"],
                                       DevCol.Event: [lx("E"), 10, "dlist_Event"],
                                       DevCol.Down: [lx("Rx"), 75, "dlist_Rx"],
                                       DevCol.Up: [lx("Tx"), 75, "dlist_Tx"],
                                       DevCol.DownRate: [lx("RxRate"), 75, "dlist_RxRate"],
                                       DevCol.UpRate: [lx("TxRate"), 75, "dlist_TxRate"]})
        self._device_list.set_header_resize([DevCol.Name, DevCol.LBName, DevCol.Link])
        self._device_list.set_standard_setup(self)
        self._device_list.setItemDelegate(CenteredIconsDelegate(self, ICON_COLUMNS))

        # Button bar
        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(30)
        refresh_device_list_button = QtWidgets.QPushButton(lx("Refresh"), objectName="refresh")
        refresh_device_list_button.clicked.connect(self.refresh_device_list_button_click)
        hbox.addWidget(refresh_device_list_button)
        assign_names_button = QtWidgets.QPushButton(lx("Assign Names..."), objectName="assignNames")
        assign_names_button.clicked.connect(self.assign_names_button_click)
        hbox.addWidget(assign_names_button)
        device_info_button = QtWidgets.QPushButton(lx("Device Infos"), objectName="deviceInfo")
        device_info_button.clicked.connect(self.device_info_button_click)
        hbox.addWidget(device_info_button)
        device_events_button = QtWidgets.QPushButton(lx("Device Events"), objectName="deviceEvents")
        device_events_button.clicked.connect(self.device_events_button_click)
        hbox.addWidget(device_events_button)
        ipv6_button = QtWidgets.QPushButton(lx("IPv6..."), objectName="ipv6")
        ipv6_button.clicked.connect(self.ipv6_button_click)
        hbox.addWidget(ipv6_button)
        dns_button = QtWidgets.QPushButton(lx("DNS..."), objectName="dns")
        dns_button.clicked.connect(self.dns_button_click)
        hbox.addWidget(dns_button)

        # Layout
        vbox = QtWidgets.QVBoxLayout()
        vbox.setSpacing(10)
        vbox.addWidget(self._device_list, 0)
        vbox.addLayout(hbox, 1)
        self._device_list_tab.setLayout(vbox)

        LmConfig.set_tooltips(self._device_list_tab, "dlist")
        self._tab_widget.addTab(self._device_list_tab, lx("Device List"))


    ### Init the Livebox Wifi stats collector thread
    def init_wifi_stats_loop(self):
        if LmConf.RealtimeWifiStats:
            self._livebox_wifi_stats_map = {}
            self._livebox_wifi_stats_loop = None


    ### Start the Livebox Wifi stats collector thread
    def start_wifi_stats_loop(self):
        if LmConf.RealtimeWifiStats:
            self._livebox_wifi_stats_loop = LiveboxWifiStatsThread(self._api)
            self._livebox_wifi_stats_loop.connect_processor(self.process_livebox_wifi_stats)


    ### Suspend the Livebox Wifi stats collector thread
    def suspend_wifi_stats_loop(self):
        if LmConf.RealtimeWifiStats:
            if self._livebox_wifi_stats_loop is not None:
                self._livebox_wifi_stats_loop.stop()


    ### Resume the Livebox Wifi stats collector thread
    def resume_wifi_stats_loop(self):
        if LmConf.RealtimeWifiStats:
            if self._livebox_wifi_stats_loop is None:
                self.start_wifi_stats_loop()
            else:
                self._livebox_wifi_stats_loop._resume.emit()


    ### Stop the Livebox Wifi stats collector thread
    def stop_wifi_stats_loop(self):
        if LmConf.RealtimeWifiStats:
            if self._livebox_wifi_stats_loop is not None:
                self._livebox_wifi_stats_loop.quit()
                self._livebox_wifi_stats_loop = None


    ### Click on refresh device list button
    def refresh_device_list_button_click(self):
        self._device_list.clearContents()
        self._device_list.setRowCount(0)
        self._info_dlist.clearContents()
        self._info_dlist.setRowCount(0)
        self._info_alist.clearContents()
        self._info_alist.setRowCount(0)
        self._event_dlist.clearContents()
        self._event_dlist.setRowCount(0)
        self._event_list.clearContents()
        self._event_list.setRowCount(0)
        LmConf.load_mac_addr_table()
        self.load_device_list()


    ### Click on assign names button
    def assign_names_button_click(self):
        if self.ask_question(mx("This will assign the Livebox name as the local name for all unknown devices. Continue?", "aName")):
            self.assign_lb_names_to_unkown_devices()


    ### Click on device infos button
    def device_info_button_click(self):
        current_selection = self._device_list.currentRow()
        if current_selection >= 0:
            key = self._device_list.item(current_selection, DevCol.Key).text()
            line = self.find_device_line(self._info_dlist, key)
            self._info_dlist.selectRow(line)
        self.switch_to_device_infos_tab()


    ### Click on device events button
    def device_events_button_click(self):
        current_selection = self._device_list.currentRow()
        if current_selection >= 0:
            key = self._device_list.item(current_selection, DevCol.Key).text()
            line = self.find_device_line(self._event_dlist, key)
            self._event_dlist.selectRow(line)
        self.switch_to_device_events_tab()


    ### Click on IPv6 button
    def ipv6_button_click(self):
        self._task.start(lx("Getting IPv6 Information..."))
        try:
            # Get IPv6 status
            try:
                d = self._api._info.get_ipv6_status()
            except Exception as e:
                self.display_error(str(e))
                ipv6_enabled = None
            else:
                ipv6_enabled = d.get("Enable")

            # Get CGNat status
            try:
                d = self._api._info.get_cgnat_status()
            except Exception as e:
                LmUtils.error(str(e))
                cgnat = None
            else:
                cgnat = d.get("Demand")

            # Get IPv6Mode
            try:
                d = self._api._info.get_ipv6_mode()
            except Exception as e:
                LmUtils.error(str(e))
                mode = None
            else:
                mode = d.get("IPv6Mode")

            # Get IPv6 address and prefix
            try:
                d = self._api._info.get_wan_status()
            except Exception as e:
                LmUtils.error(str(e))
                ipv6_addr = None
                ipv6_prefix = None
                gateway = None
            else:
                ipv6_addr = d.get("IPv6Address")
                ipv6_prefix = d.get("IPv6DelegatedPrefix")
                gateway = d.get("RemoteGatewayIPv6")

            # Get IPv6 prefix leases delegation list
            try:
                prefixes = self._api._dhcp.get_v6_prefix_leases()
            except Exception as e:
                self.display_error(str(e))
                prefixes = None

            self.load_device_ip_name_map()
        finally:
            self._task.end()

        ipv6_dialog = IPv6Dialog(ipv6_enabled, cgnat, mode, ipv6_addr, ipv6_prefix, gateway, self)
        ipv6_dialog.load_device_list(self._livebox_devices, prefixes)
        ipv6_dialog.exec()


    ### Click on DNS button
    def dns_button_click(self):
        self._task.start(lx("Getting DNS Information..."))
        try:
            self.load_device_ip_name_map()
        finally:
            self._task.end()

        dns_dialog = DnsDialog(self)
        dns_dialog.load_device_list(self._livebox_devices)
        dns_dialog.exec()


    ### Load device list
    def load_device_list(self):
        self._task.start(lx("Loading device list..."))
        try:
            self._device_list.setSortingEnabled(False)
            self._info_dlist.setSortingEnabled(False)
            self._event_dlist.setSortingEnabled(False)
            self._event_list.setSortingEnabled(False)

            # Init
            self._interface_map = []
            self._device_map = []
            self._device_ip_name_map = {}
            self._device_ip_name_map_dirty = True

            # Get device infos from Livebox & build IP -> name map
            try:
                self._livebox_devices = self._api._device.get_list()
            except Exception as e:
                LmUtils.error(str(e))
                self.display_error(mx("Error getting device list.", "dlistErr"))
                self._livebox_devices = None            
            else:
                self.build_device_ip_name_map()
                self._device_ip_name_map_dirty = False

            # Get topology infos from Livebox & build link & device maps
            try:
                topology = self._api._device.get_topology()
            except Exception as e:
                LmUtils.error(str(e))
                self.display_error(mx("Error getting device topology.", "topoErr"))
            else:
                self.build_link_maps(topology)

            # Load devices in list, trying to identify Wifi repeaters & TV Decoders on the fly
            i = 0
            if self._livebox_devices is not None:
                for d in self._livebox_devices:
                    if self.displayable_device(d):
                        self.identify_repeater(d)
                        self.identify_tvdecoder(d)
                        self.add_device_line(i, d)
                        self.update_device_line(i, d, False)
                        i += 1

            self._device_list.sortItems(DevCol.Active, QtCore.Qt.SortOrder.DescendingOrder)

            self._event_dlist.insertRow(i)
            self._event_dlist.setItem(i, DSelCol.Key, QtWidgets.QTableWidgetItem("#NONE#"))
            self._event_dlist.setItem(i, DSelCol.Name, QtWidgets.QTableWidgetItem(lx("<None>")))

            self._device_list.setCurrentCell(-1, -1)
            self._info_dlist.setCurrentCell(-1, -1)
            self._event_dlist.setCurrentCell(-1, -1)

            self.init_device_context()      # Init selected device context for DeviceInfo tab

            self._device_list.setSortingEnabled(True)
            self._info_dlist.setSortingEnabled(True)
            self._event_dlist.setSortingEnabled(True)
            self._event_list.setSortingEnabled(True)
        finally:
            self._task.end()


    ### Check if device is displayable
    def displayable_device(self, device):
        # If Filter Devices option is on, do not display active devices without Layer2Intf
        if LmConf.FilterDevices and device.get("Active", False):
            return len(device.get("Layer2Interface", "")) > 0
        return True


    ### Add device line
    def add_device_line(self, line, device):
        key = device.get("Key", "")
        self.add_device_line_key(self._device_list, line, key)
        self.add_device_line_key(self._info_dlist, line, key)
        self.add_device_line_key(self._event_dlist, line, key)

        mac_addr = device.get("PhysAddress", "")
        self.format_name_widget(self._device_list, line, key, DevCol.Name)
        self.format_mac_widget(self._device_list, line, mac_addr, DevCol.MAC)
        self.format_name_widget(self._info_dlist, line, key, DSelCol.Name)
        self.format_mac_widget(self._info_dlist, line, mac_addr, DSelCol.MAC)
        self.format_name_widget(self._event_dlist, line, key, DSelCol.Name)
        self.format_mac_widget(self._event_dlist, line, mac_addr, DSelCol.MAC)


    ### Add a line with a device key
    @staticmethod
    def add_device_line_key(table, line, key):
        table.insertRow(line)
        table.setItem(line, DevCol.Key, QtWidgets.QTableWidgetItem(key))


    ### Update device line
    def update_device_line(self, line, device, notify):
        device_type = device.get("DeviceType", "")
        device_type_icon = self.format_device_type_table_widget(device_type, self._api._info.get_software_version())
        self._device_list.setItem(line, DevCol.Type, device_type_icon)

        lb_name = QtWidgets.QTableWidgetItem(device.get("Name", ""))
        self._device_list.setItem(line, DevCol.LBName, lb_name)

        ip_struct = LmUtils.determine_ip(device)
        if ip_struct is None:
            ipv4 = ""
            ipv4_reacheable = ""
            ipv4_reserved = False
        else:
            ipv4 = ip_struct.get("Address", "")
            ipv4_reacheable = ip_struct.get("Status", "")
            ipv4_reserved = ip_struct.get("Reserved", False)
        ip = self.format_ipv4_table_widget(ipv4, ipv4_reacheable, ipv4_reserved)
        self._device_list.setItem(line, DevCol.IP, ip)

        link_intf = self.find_device_link(device.get("Key", ""))
        if link_intf is None:
            link_name = lx("Unknown")
            link_type = ""
        else:
            link_name = link_intf["Name"]
            link_type = link_intf["Type"]
        curr_link = self._device_list.item(line, DevCol.Link)
        if curr_link is None:
            curr_link_name = ""
        else:
            curr_link_name = curr_link.text()
        link = QtWidgets.QTableWidgetItem(link_name)
        self._device_list.setItem(line, DevCol.Link, link)

        # Notify
        if notify and (link_name != curr_link_name):
            mac_addr = device.get("PhysAddress", None)
            if mac_addr is not None:
                self.notify_device_access_link_event(mac_addr, curr_link_name, link_name)

        active_status = device.get("Active", False)
        active_icon = self.format_active_table_widget(active_status)
        self._device_list.setItem(line, DevCol.Active, active_icon)

        wifi_icon = None
        if active_status and (link_type == "wif"):
            wifi_signal = device.get("SignalNoiseRatio")
            if wifi_signal is not None:
                wifi_icon = NumericSortItem()
                if wifi_signal >= 40:
                    wifi_icon.setIcon(QtGui.QIcon(LmIcon.WifiSignal5Pixmap))
                elif wifi_signal >= 32:
                    wifi_icon.setIcon(QtGui.QIcon(LmIcon.WifiSignal4Pixmap))
                elif wifi_signal >= 25:
                    wifi_icon.setIcon(QtGui.QIcon(LmIcon.WifiSignal3Pixmap))
                elif wifi_signal >= 15:
                    wifi_icon.setIcon(QtGui.QIcon(LmIcon.WifiSignal2Pixmap))
                elif wifi_signal >= 10:
                    wifi_icon.setIcon(QtGui.QIcon(LmIcon.WifiSignal1Pixmap))
                elif wifi_signal == 0:      # Case when system doesn't know, like for Guest interface
                    wifi_icon.setIcon(QtGui.QIcon(LmIcon.WifiSignal5Pixmap))
                else:
                    wifi_icon.setIcon(QtGui.QIcon(LmIcon.WifiSignal0Pixmap))
                wifi_icon.setData(QtCore.Qt.ItemDataRole.UserRole, wifi_signal)
        self._device_list.setItem(line, DevCol.Wifi, wifi_icon)


    ### Update device name in all lists & tabs
    def update_device_name(self, device_key):
        line = self.find_device_line(self._device_list, device_key)
        if line >= 0:
            self.format_name_widget(self._device_list, line, device_key, DevCol.Name)

        line = self.find_device_line(self._info_dlist, device_key)
        if line >= 0:
            self.format_name_widget(self._info_dlist, line, device_key, DSelCol.Name)

        line = self.find_device_line(self._event_dlist, device_key)
        if line >= 0:
            self.format_name_widget(self._event_dlist, line, device_key, DSelCol.Name)

        line = self.find_device_line(self._dhcp_dlist, device_key)
        if line >= 0:
            self.format_name_widget(self._dhcp_dlist, line, device_key, DhcpCol.Name)

        self.graph_update_device_name(device_key)
        self.repeater_update_device_name(device_key)
        self.tvdecoder_update_device_name(device_key)


    ### Format device type cell
    @staticmethod
    def format_device_type_table_widget(device_type, lb_soft_version):
        device_type_icon = NumericSortItem()
        device_type_name = device_type

        for i, d in enumerate(LmConfig.DEVICE_TYPES):
            if device_type == d["Key"]:
                device_type_icon.setIcon(QtGui.QIcon(LmConf.get_device_icon(d, lb_soft_version)))
                device_type_name = d["Name"]
                break

        device_type_icon.setData(QtCore.Qt.ItemDataRole.UserRole, i)
        device_type_icon.setData(LmTools.ItemDataRole.ExportRole, device_type_name)

        return device_type_icon


    ### Format Name cell
    @staticmethod
    def format_name_widget(table, line, mac_addr, name_col):
        try:
            name = QtWidgets.QTableWidgetItem(LmConf.MacAddrTable[mac_addr])
        except KeyError:
            name = QtWidgets.QTableWidgetItem(lx("UNKNOWN"))
            name.setBackground(QtCore.Qt.GlobalColor.red)
        table.setItem(line, name_col, name)
        

    ### Format MAC address cell
    @staticmethod
    def format_mac_widget(table, line, mac_addr, mac_col):
        mac = QtWidgets.QTableWidgetItem(mac_addr)
        mac.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        table.setItem(line, mac_col, mac)


    ### Format Active status cell
    @staticmethod
    def format_active_table_widget(active_status):
        active_icon_item = NumericSortItem()
        if active_status:
            active_icon_item.setIcon(QtGui.QIcon(LmIcon.TickPixmap))
            active_icon_item.setData(QtCore.Qt.ItemDataRole.UserRole, 1)
            active_icon_item.setData(LmTools.ItemDataRole.ExportRole, True)
        else:
            active_icon_item.setIcon(QtGui.QIcon(LmIcon.CrossPixmap))
            active_icon_item.setData(QtCore.Qt.ItemDataRole.UserRole, 0)
            active_icon_item.setData(LmTools.ItemDataRole.ExportRole, False)
        return active_icon_item


    ### Format IPv4 cell
    @staticmethod
    def format_ipv4_table_widget(ipv4, reacheable_status, reserved):
        ip = NumericSortItem(ipv4)
        if len(ipv4):
            ip.setData(QtCore.Qt.ItemDataRole.UserRole, int(IPv4Address(ipv4)))
        else:
            ip.setData(QtCore.Qt.ItemDataRole.UserRole, 0)
        if reacheable_status != "reachable":
            ip.setForeground(QtCore.Qt.GlobalColor.red)
        if reserved:
            ip.setFont(LmTools.BOLD_FONT)
        return ip


    ### Find device line from device key
    @staticmethod
    def find_device_line(table, device_key):
        if not device_key:
            return -1
        return next((i for i in range(table.rowCount()) if table.item(i, DevCol.Key).text() == device_key), -1)


    ### Get list of devices MAC, Livebox name, IPv4 and Active from currently displayed device list
    def get_device_list(self):
        return [
            {
                "MAC": self._device_list.item(i, DevCol.MAC).text(),
                "LBName": self._device_list.item(i, DevCol.LBName).text(),
                "IP": self._device_list.item(i, DevCol.IP).text(),
                "Active": self._device_list.item(i, DevCol.Active).data(QtCore.Qt.ItemDataRole.UserRole) == 1
            }
            for i in range(self._device_list.rowCount())
        ]


    ### Propose to assign LB names to all unknown devices
    def propose_to_assign_names_to_unkown_devices(self):
        if not LmConf.MacAddrTable:
            if self.ask_question(mx("Do you trust all connected devices and do you want to name them all based on their Livebox name?\n"
                                    "You can still do that action later.", "aNameStartup")):
                self.assign_lb_names_to_unkown_devices()


    ### Assign LB names to all unknown devices
    def assign_lb_names_to_unkown_devices(self):
        self._task.start(lx("Assigning names to unknown devices..."))
        try:
            for d in self.get_device_list():
                if not LmConf.MacAddrTable.get(d["MAC"]):
                    self.set_device_name(d["MAC"], d["LBName"])
        finally:
            self._task.end()


    ### Load device IPv4 & IPv6 -> MAC/LBName/Active/IPVers map if need to be refreshed
    def load_device_ip_name_map(self):
        if self._device_ip_name_map_dirty:
            self._task.start(lx("Loading devices information..."))
            try:
                try:
                    self._livebox_devices = self._api._device.get_list()
                except Exception as e:
                    LmUtils.error(str(e))
                    self.display_error(mx("Error getting device list.", "dlistErr"))
                    return

                self.build_device_ip_name_map()
                self._device_ip_name_map_dirty = False
            finally:
                self._task.end()


    # Build device IPv4 & IPv6 -> MAC/LBName/Active/IPVers map from currently loaded device list
    def build_device_ip_name_map(self):
        # Init
        self._device_ip_name_map = {}

        for d in self._livebox_devices:
            # Skip non displayable devices
            if not self.displayable_device(d):
                continue

            # Base device infos to map for all its IP entries
            base_info = {
                "MAC": d.get("PhysAddress", ""),
                "LBName": d.get("Name", ""),
                "Active": d.get("Active", False)
            }

            # Map IPv4 address to device infos
            ipv4_struct = LmUtils.determine_ip(d)
            if ipv4_struct:
                ipv4 = ipv4_struct.get("Address", "")
                if ipv4:
                    self._device_ip_name_map[ipv4] = {**base_info, "IPVers": "IPv4"}

            # Map IPv6 address(es) to device infos
            for ipv6_entry in d.get("IPv6Address") or []:
                if ipv6_entry.get("Scope", "link") != "link":
                    ipv6 = ipv6_entry.get("Address", "")
                    if ipv6:
                        self._device_ip_name_map[ipv6] = {**base_info, "IPVers": "IPv6"}           


    ### Get device name from IPv4 or IPv6
    # Depends on DeviceIpNameMap correct load
    # Returns local name in priority then LB name, then default to IP
    def get_device_name_from_ip(self, ip):
        if ip:
            device_info = self._device_ip_name_map.get(ip)
            if device_info is None:
                return ip
            try:
                return LmConf.MacAddrTable[device_info["MAC"]]
            except KeyError:
                return device_info["LBName"]
        return ""


    ### Returns True if device uses a Wifi connection
    def is_wifi_device(self, device_key):
        link_intf = self.find_device_link(device_key)
        if link_intf:
            return link_intf["Type"] == "wif"
        return False


    ### Build link map
    def build_link_maps(self, topology):
        root_node = topology[0]
        device_key = root_node.get("Key", "")
        self.build_links_map_node(root_node.get("Children", []), device_key, "Livebox", "", "")
#DBG    self.display_infos('Interface map', str(self._interface_map))
#DBG    self.display_infos('Device map', str(self._device_map))


    ### Handle a topology node to build links map
    def build_links_map_node(self, node, device_key, device_name, interface_key, interface_name):
        intf_list = self._api._intf.get_list()
        for d in node:
            tags = d.get("Tags", "").split()

            # Init
            node_device_key = device_key
            node_device_name = device_name
            node_interface_key = interface_key
            node_interface_name = interface_name

            # Handle interface end points
            if "interface" in tags:
                node_interface_key = d.get("Key", "")
                interface_type = d.get("InterfaceType", "")
                if interface_type == "Ethernet":
                    interface_type = "eth"
                    node_interface_name = d.get("Name", "").capitalize()
                    if len(node_interface_name) == 0:
                        node_interface_name = d.get("NetDevName", "").capitalize()
                    if device_name == "Livebox":
                        name_map = LmConfig.INTF_NAME_MAP
                    else:
                        name_map = INTF_NAME_MAP_WR
                    mapped_name = name_map.get(node_interface_name)
                    if mapped_name is not None:
                        node_interface_name = mapped_name
                else:
                    interface_type = "wif"
                    if device_name == "Livebox":
                        i = next((i for i in intf_list if i["Key"] == node_interface_key), None)
                        if i is None:
                            node_interface_name = d.get("Name", node_interface_key)
                        else:
                            node_interface_name = i["Name"]
                    else:
                        wifi_band = d.get("OperatingFrequencyBand", "")
                        if len(wifi_band):
                            node_interface_name = f"Wifi {wifi_band}"
                        else:
                            node_interface_name = d.get("Name", node_interface_key)

                map_entry = {
                    "Key": node_interface_key,
                    "Type": interface_type,
                    "DevKey": node_device_key,
                    "DevName": node_device_name,
                    "IntName": node_interface_name,
                    "Name": f"{node_device_name} {lx(node_interface_name)}"
                }
                self._interface_map.append(map_entry)

            # Handle devices
            if "physical" in tags:
                node_device_key = d.get("Key", "")
                node_device_name = d.get("Name", "")
                map_entry = {
                    "Key": node_device_key,
                    "InterfaceKey": node_interface_key
                }
                self._device_map.append(map_entry)

            self.build_links_map_node(d.get("Children", []), node_device_key, node_device_name, node_interface_key, node_interface_name)


    ### Find device link name from device key
    def find_device_link(self, device_key):
        # Find the interface key for the device
        device = next((d for d in self._device_map if d["Key"] == device_key), None)
        if not device:
            return None
        interface_key = device["InterfaceKey"]

        # Find and return the interface map entry
        return next((i for i in self._interface_map if i["Key"] == interface_key), None)


    ### Update device link interface key
    def update_device_link_interface(self, device_key, interface_key):
        device = next((d for d in self._device_map if d["Key"] == device_key), None)
        if device:
            device["InterfaceKey"] = interface_key


    ### Update interface map when a device name changes, and refresh the UI
    def update_interface_map(self, device_key, device_name):
        # Loop on interface map and update each matching entries
        for i in self._interface_map:
            if i["DevKey"] == device_key:
                i["DevName"] = device_name
                link_name = f"{device_name} {i['IntName']}"
                i["Name"] = link_name

                # Then update each device connected to that interface
                for d in self._device_map:
                    if d["InterfaceKey"] == i["Key"]:
                        line = self.find_device_line(self._device_list, d["Key"])
                        if line >= 0:
                            self._device_list.setItem(line, DevCol.Link, QtWidgets.QTableWidgetItem(link_name))


    ### Indicate visually the reception of an event for a device
    def update_event_indicator(self, device_key):
        # First remove last event indicator
        list_line = self.find_device_line(self._device_list, self._last_event_device_key)
        if list_line >= 0:
            self._device_list.setItem(list_line, DevCol.Event, None)

        # Set indicator on new device
        list_line = self.find_device_line(self._device_list, device_key)
        if list_line >= 0:
            event_indicator = NumericSortItem()
            event_indicator.setIcon(QtGui.QIcon(LmIcon.NotifPixmap))
            event_indicator.setData(QtCore.Qt.ItemDataRole.UserRole, 1)
            self._device_list.setItem(list_line, DevCol.Event, event_indicator)

        self._last_event_device_key = device_key


    ### Process a new statistics event
    def process_statistics_event(self, device_key, event):
        # Get event data
        down_bytes = event.get("RxBytes", 0)
        up_bytes = event.get("TxBytes", 0)
        down_errors = event.get("RxErrors", 0)
        up_errors = event.get("TxErrors", 0)
        down_rate_bytes = 0
        up_rate_bytes = 0
        down_delta_errors = event.get("DeltaRxErrors", 0)
        up_delta_errors = event.get("DeltaTxErrors", 0)
        timestamp = LmUtils.livebox_timestamp(event.get("Timestamp", ""))

        # Try to find a previously received statistic record
        prev_stats = self._stats_map.get(device_key)
        if prev_stats is not None:
            prev_down_bytes = prev_stats["Rx"]
            prev_up_bytes = prev_stats["Tx"]
            prev_timestamp = prev_stats["Time"]
            elapsed = int((timestamp - prev_timestamp).total_seconds())
            if elapsed > 0:
                down_rate_bytes = int((down_bytes - prev_down_bytes) / elapsed)
                up_rate_bytes = int((up_bytes - prev_up_bytes) / elapsed)

            # Update potential running graph
            self.graph_update_device_event(device_key, int(timestamp.timestamp()),
                                           down_bytes - prev_down_bytes,
                                           up_bytes - prev_up_bytes)

        # Remember current stats
        stats = {}
        stats["Rx"] = down_bytes
        stats["Tx"] = up_bytes
        stats["Time"] = timestamp
        self._stats_map[device_key] = stats

        # Update UI
        list_line = self.find_device_line(self._device_list, device_key)
        if list_line >= 0:
            # Prevent device line to change due to sorting
            self._device_list.setSortingEnabled(False)

            down = NumericSortItem(LmUtils.fmt_bytes(down_bytes))
            down.setData(QtCore.Qt.ItemDataRole.UserRole, down_bytes)
            down.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
            if down_errors:
                down.setForeground(QtCore.Qt.GlobalColor.red)
            self._device_list.setItem(list_line, DevCol.Down, down)

            up = NumericSortItem(LmUtils.fmt_bytes(up_bytes))
            up.setData(QtCore.Qt.ItemDataRole.UserRole, up_bytes)
            up.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
            if up_errors:
                up.setForeground(QtCore.Qt.GlobalColor.red)
            self._device_list.setItem(list_line, DevCol.Up, up)

            if down_rate_bytes:
                down_rate = NumericSortItem(LmUtils.fmt_bytes(down_rate_bytes) + "/s")
                down_rate.setData(QtCore.Qt.ItemDataRole.UserRole, down_rate_bytes)
                if down_delta_errors:
                    down_rate.setForeground(QtCore.Qt.GlobalColor.red)
                down_rate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
            else:
                down_rate = QtWidgets.QTableWidgetItem("")
            self._device_list.setItem(list_line, DevCol.DownRate, down_rate)

            if up_rate_bytes:
                up_rate = NumericSortItem(LmUtils.fmt_bytes(up_rate_bytes) + "/s")
                up_rate.setData(QtCore.Qt.ItemDataRole.UserRole, up_rate_bytes)
                if up_delta_errors:
                    up_rate.setForeground(QtCore.Qt.GlobalColor.red)
                up_rate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
            else:
                up_rate = QtWidgets.QTableWidgetItem("")
            self._device_list.setItem(list_line, DevCol.UpRate, up_rate)

            # Restore sorting
            self._device_list.setSortingEnabled(True)


    ### Process a new changed event
    def process_changed_event(self, device_key, handler, event):
        # Refresh if current selected one in device info
        self.refresh_device_if_selected(device_key)

        # Check if device is in the UI list
        list_line = self.find_device_line(self._device_list, device_key)
        if list_line >= 0:
            # Prevent device line to change due to sorting
            self._device_list.setSortingEnabled(False)

            # Check if active status changed
            active_status = event.get("Active")
            if active_status is not None:
                self._device_ip_name_map_dirty = True
                is_active = active_status != "0"
                curr_active = self._device_list.item(list_line, DevCol.Active)
                if curr_active is not None:
                    is_currently_active = curr_active.data(QtCore.Qt.ItemDataRole.UserRole) == 1
                else:
                    is_currently_active = False
                if is_active != is_currently_active:
                    if is_active:
                        curr_link = self._device_list.item(list_line, DevCol.Link)
                        curr_link_name = curr_link.text() if curr_link is not None else ""
                        self.notify_device_active_event(device_key, curr_link_name)
                    else:
                        self.notify_device_inactive_event(device_key)
                active_icon = self.format_active_table_widget(is_active)
                self._device_list.setItem(list_line, DevCol.Active, active_icon)
                self.repeater_active_event(device_key, is_active)
                self.tvdecoder_active_event(device_key, is_active)

            # Check if IP reachable status changed
            ipv4_reacheable = event.get("Status")
            if (ipv4_reacheable is not None) and ("IPv4Address" in handler):
                curr_ip = self._device_list.item(list_line, DevCol.IP)
                reserved = curr_ip.font().bold()
                ip = self.format_ipv4_table_widget(curr_ip.text(), ipv4_reacheable, reserved)
                self._device_list.setItem(list_line, DevCol.IP, ip)

            # Check if IPv4 changed
            ipv4 = event.get("IPAddress")
            if (ipv4 is not None) and (LmUtils.is_ipv4(ipv4)):
                self._device_ip_name_map_dirty = True
                ip = self._device_list.item(list_line, DevCol.IP)
                ip.setText(ipv4)
                ip.setData(QtCore.Qt.ItemDataRole.UserRole, int(IPv4Address(ipv4)))
                self.repeater_ip_address_event(device_key, ipv4)
                self.tvdecoder_ip_address_event(device_key, ipv4)

            # Check if name changed
            name = event.get("Name")
            if name is not None:
                self._device_ip_name_map_dirty = True
                self._device_list.setItem(list_line, DevCol.LBName, QtWidgets.QTableWidgetItem(name))
                self.update_interface_map(device_key, name)

            # Check if MAC address assigned
            mac_addr = event.get("PhysAddress")
            if mac_addr is not None:
                self._device_ip_name_map_dirty = True

                self.format_name_widget(self._device_list, list_line, mac_addr, DevCol.Name)
                self.format_mac_widget(self._device_list, list_line, mac_addr, DevCol.MAC)

                line = self.find_device_line(self._info_dlist, device_key)
                if line >= 0:
                    self.format_name_widget(self._info_dlist, line, mac_addr, DSelCol.Name)
                    self.format_mac_widget(self._info_dlist, line, mac_addr, DSelCol.MAC)

                line = self.find_device_line(self._event_dlist, device_key)
                if line >= 0:
                    self.format_name_widget(self._event_dlist, line, mac_addr, DSelCol.Name)
                    self.format_mac_widget(self._event_dlist, line, mac_addr, DSelCol.MAC)

            # Restore sorting
            self._device_list.setSortingEnabled(True)


    ### Process a new device_name_changed event
    def process_device_name_changed_event(self, device_key, event):
        self._device_ip_name_map_dirty = True

        # Check if device is in the UI list
        list_line = self.find_device_line(self._device_list, device_key)
        if list_line >= 0:
            name = event.get("NewName")
            if name is not None:
                self._device_list.setItem(list_line, DevCol.LBName, QtWidgets.QTableWidgetItem(name))
                self.update_interface_map(device_key, name)

        # Refresh if the device is the selected one in the device info tab
        self.refresh_device_if_selected(device_key)


    ### Process a new device_updated, eth_device_updated or wifi_device_updated event
    def process_device_updated_event(self, device_key, event):
        # Check if device is in the UI list
        list_line = self.find_device_line(self._device_list, device_key)
        if list_line >= 0:
            self._device_ip_name_map_dirty = True

            # Prevent device line to change due to sorting
            self._device_list.setSortingEnabled(False)

            # Update the link interface
            link = event.get("ULinks")
            if link:
                self.update_device_link_interface(device_key, link[0])

            # Update the device line
            self.update_device_line(list_line, event, True)

            # Update potential repeater infos
            self.repeater_device_updated_event(device_key, event)

            # Update potential TV Decoder infos
            self.tvdecoder_device_updated_event(device_key, event)

            # Restore sorting
            self._device_list.setSortingEnabled(True)

        # Refresh if the device is the selected one in the device info tab
        self.refresh_device_if_selected(device_key)


    ### Process a new ip_address_added event
    def process_ip_address_added_event(self, device_key, event):
        self._device_ip_name_map_dirty = True

        # Check if device is in the UI list
        list_line = self.find_device_line(self._device_list, device_key)
        if list_line >= 0:
            if event.get("Family") == "ipv4":
                # Get IP known by the program
                known_ip_item = self._device_list.item(list_line, DevCol.IP)
                known_ip = known_ip_item.text() if known_ip_item is not None else ""

                # Get current device IP
                try:
                    curr_ip = self._api._device.get_ip_addr(device_key)
                except Exception as e:
                    LmUtils.error(str(e))
                    curr_ip = known_ip

                # Proceed only if there is a change
                if known_ip != curr_ip:
                    # If current IP is the one of the event, take it, overwise wait for next device update event
                    ipv4 = event.get("Address", "")
                    if LmUtils.is_ipv4(ipv4) and (curr_ip == ipv4):
                        ipv4_reacheable = event.get("Status", "")
                        ipv4_reserved = event.get("Reserved", False)
                        ip = self.format_ipv4_table_widget(ipv4, ipv4_reacheable, ipv4_reserved)
                        self._device_list.setItem(list_line, DevCol.IP, ip)
                        self.repeater_ip_address_event(device_key, ipv4)
                        self.tvdecoder_ip_address_event(device_key, ipv4)


    ### Process a new device_added, eth_device_added or wifi_device_added event
    def process_device_added_event(self, device_key, event):
        # Check if device is not already in the UI list
        list_line = self.find_device_line(self._device_list, device_key)
        if list_line >= 0:
            return

        tags = event.get("Tags", "").split()
        if ("physical" in tags) and (not "self" in tags) and (not "voice" in tags) and self.displayable_device(event):
            self._device_ip_name_map_dirty = True

            # Notify
            self.notify_device_added_event(device_key)

            # Prevent device lines to change due to sorting
            self._device_list.setSortingEnabled(False)
            self._info_dlist.setSortingEnabled(False)
            self._event_dlist.setSortingEnabled(False)

            # Update device map
            map_entry = {}
            map_entry["Key"] = device_key
            map_entry["InterfaceKey"] = None
            self._device_map.append(map_entry)

            # Update UI
            self.add_device_line(0, event)
            self.update_device_line(0, event, True)

            # Add as repeater if it is one
            self.add_potential_repeater(event)

            # Add as TV Decoder if it is one
            self.add_potential_tvdecoder(event)

            # Restore sorting
            self._device_list.setSortingEnabled(True)
            self._info_dlist.setSortingEnabled(True)
            self._event_dlist.setSortingEnabled(True)


    ### Process a new device_deleted, eth_device_deleted or wifi_device_deleted event
    def process_device_deleted_event(self, device_key):
        self._device_ip_name_map_dirty = True

        # Notify
        self.notify_device_deleted_event(device_key)

        # Remove from all UI lists
        list_line = self.find_device_line(self._device_list, device_key)
        if list_line >= 0:
            self._device_list.removeRow(list_line)
        list_line = self.find_device_line(self._info_dlist, device_key)
        if list_line >= 0:
            self._info_dlist.removeRow(list_line)
        list_line = self.find_device_line(self._event_dlist, device_key)
        if list_line >= 0:
            self._event_dlist.removeRow(list_line)

        # Remove repeater if it is one
        self.remove_potential_repeater(device_key)

        # Remove TV Decoder if it is one
        self.remove_potential_tvdecoder(device_key)

        # Cleanup device map
        for d in self._device_map:
            if d["Key"] == device_key:
                self._device_map.remove(d)

        # Cleanup event buffer
        try:
            del self._event_buffer[device_key]
        except KeyError:
            pass


    ### Process a new Livebox Wifi stats
    def process_livebox_wifi_stats(self, stats):
        # Get stats data
        key = stats["Key"]
        device_key = stats["DeviceKey"]
        timestamp = stats["Timestamp"]
        down_bytes = stats["RxBytes"]
        up_bytes = stats["TxBytes"]
        down_errors = stats["RxErrors"]
        up_errors = stats["TxErrors"]
        down_rate_bytes = 0
        up_rate_bytes = 0
        down_delta_errors = 0
        up_delta_errors = 0

        # Try to find a previously received statistic record
        prev_stats = self._livebox_wifi_stats_map.get(key)
        if prev_stats is not None:
            prev_timestamp = prev_stats["Timestamp"]
            prev_down_bytes = prev_stats["RxBytes"]
            prev_up_bytes = prev_stats["TxBytes"]
            elapsed = int((timestamp - prev_timestamp).total_seconds())
            if elapsed > 0:
                if down_bytes > prev_down_bytes:
                    down_rate_bytes = int((down_bytes - prev_down_bytes) / elapsed)
                if up_bytes > prev_up_bytes:
                    up_rate_bytes = int((up_bytes - prev_up_bytes) / elapsed)
            down_delta_errors = down_errors - prev_stats["RxErrors"]
            up_delta_errors = up_errors - prev_stats["TxErrors"]

        # Remember current stats
        self._livebox_wifi_stats_map[key] = stats

        # Update UI
        list_line = self.find_device_line(self._device_list, device_key)
        if (list_line >= 0) and (prev_stats is not None):
            # Prevent device line to change due to sorting
            self._device_list.setSortingEnabled(False)

            if down_rate_bytes:
                down_rate = NumericSortItem(LmUtils.fmt_bytes(down_rate_bytes) + "/s")
                down_rate.setData(QtCore.Qt.ItemDataRole.UserRole, down_rate_bytes)
                if down_delta_errors:
                    down_rate.setForeground(QtCore.Qt.GlobalColor.red)
                else:
                    down_rate.setForeground(QtCore.Qt.GlobalColor.blue)
                down_rate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
            else:
                down_rate = QtWidgets.QTableWidgetItem("")
            self._device_list.setItem(list_line, DevCol.DownRate, down_rate)

            if up_rate_bytes:
                up_rate = NumericSortItem(LmUtils.fmt_bytes(up_rate_bytes) + "/s")
                up_rate.setData(QtCore.Qt.ItemDataRole.UserRole, up_rate_bytes)
                if up_delta_errors:
                    up_rate.setForeground(QtCore.Qt.GlobalColor.red)
                else:
                    up_rate.setForeground(QtCore.Qt.GlobalColor.blue)
                up_rate.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
            else:
                up_rate = QtWidgets.QTableWidgetItem("")
            self._device_list.setItem(list_line, DevCol.UpRate, up_rate)

            # Restore sorting
            self._device_list.setSortingEnabled(True)



# ############# Livebox Wifi device stats collector thread #############
# WARNING: for an unknown reason, moving this class to a submodule causes the application to hang
class LiveboxWifiStatsThread(LmThread):
    _wifi_stats_received = QtCore.pyqtSignal(dict)
    _resume = QtCore.pyqtSignal()

    def __init__(self, api):
        super().__init__(api, LmConf.StatsFrequency)


    def connect_processor(self, processor):
        self._wifi_stats_received.connect(processor)


    def task(self):
        for s in self._api._intf.get_list():
            if s["Type"] != "wif":
                continue
            try:
                d = self._api._stats.get_wifi_intf(s["Key"])
            except Exception as e:
                LmUtils.error(str(e))
            else:
                if isinstance(d, list):
                    for stat in d:
                        mac_addr = stat.get("MACAddress", "")
                        event = {
                            "DeviceKey": mac_addr,
                            "Key": f"{mac_addr}_{s['Key']}",
                            "Timestamp": datetime.datetime.now(),
                            "RxBytes": stat.get("TxBytes", 0),      # Must be swapped
                            "TxBytes": stat.get("RxBytes", 0),      # Must be swapped
                            "RxErrors": stat.get("TxErrors", 0),    # Must be swapped
                            "TxErrors": stat.get("RxErrors", 0)     # Must be swapped
                        }
                        self._wifi_stats_received.emit(event)
