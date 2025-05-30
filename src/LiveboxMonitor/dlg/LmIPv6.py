### Livebox Monitor IPv6 dialog ###

from enum import IntEnum

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmTableWidget import LmTableWidget, CenteredIconsDelegate
from LiveboxMonitor.lang.LmLanguages import get_ipv6_label as lx


# ################################ VARS & DEFS ################################

# List columns
class IPv6Col(IntEnum):
    Key = 0     # Must be the same as DevCol.Key
    Name = 1
    LBName = 2
    MAC = 3
    Active = 4
    IPv4 = 5
    IPv6 = 6
    Prefix = 7
IPV6_ICON_COLUMNS = [IPv6Col.Active]


# ################################ IPv6 dialog ################################
class IPv6Dialog(QtWidgets.QDialog):
    def __init__(self, enabled, cgnat, mode, addr, prefix, gateway, parent=None):
        super(IPv6Dialog, self).__init__(parent)
        self.resize(1005, 110 + LmConfig.dialog_height(12))

        # IPv6 info box
        ipv6_enabled_label = QtWidgets.QLabel(lx('IPv6 enabled:'), objectName='ipv6EnabledLabel')
        ipv6_enabled = QtWidgets.QLabel(objectName='ipv6Enabled')
        if enabled:
            ipv6_enabled.setPixmap(LmIcon.TickPixmap)
        else:
            ipv6_enabled.setPixmap(LmIcon.CrossPixmap)

        cgnat_enabled_label = QtWidgets.QLabel(lx('CGNat:'), objectName='cgNatLabel')
        cgnat_icon = QtWidgets.QLabel(objectName='cgNat')
        if cgnat:
            cgnat_icon.setPixmap(LmIcon.TickPixmap)
        else:
            cgnat_icon.setPixmap(LmIcon.CrossPixmap)

        ipv6_mode_label = QtWidgets.QLabel(lx('Mode:'), objectName='ipv6ModeLabel')
        ipv6_mode = QtWidgets.QLabel(mode, objectName='ipv6Mode')

        addr_label = QtWidgets.QLabel(lx('IPv6 address:'), objectName='addrLabel')
        addr_edit = QtWidgets.QLineEdit(addr, objectName='addr')
        addr_edit.setReadOnly(True)

        prefix_label = QtWidgets.QLabel(lx('IPv6 prefix:'), objectName='prefixLabel')
        prefix_edit = QtWidgets.QLineEdit(prefix, objectName='prefix')
        prefix_edit.setReadOnly(True)

        gateway_label = QtWidgets.QLabel(lx('IPv6 gateway:'), objectName='gatewayLabel')
        gateway_edit = QtWidgets.QLineEdit(gateway, objectName='gateway')
        gateway_edit.setReadOnly(True)

        ipv6_info_grid = QtWidgets.QGridLayout()
        ipv6_info_grid.setSpacing(10)
        ipv6_info_grid.addWidget(ipv6_enabled_label, 0, 0)
        ipv6_info_grid.addWidget(ipv6_enabled, 0, 1)
        ipv6_info_grid.addWidget(cgnat_enabled_label, 0, 2)
        ipv6_info_grid.addWidget(cgnat_icon, 0, 3)
        ipv6_info_grid.addWidget(ipv6_mode_label, 0, 4)
        ipv6_info_grid.addWidget(ipv6_mode, 0, 5)
        ipv6_info_grid.addWidget(addr_label, 1, 0)
        ipv6_info_grid.addWidget(addr_edit, 1, 1)
        ipv6_info_grid.addWidget(prefix_label, 1, 2)
        ipv6_info_grid.addWidget(prefix_edit, 1, 3)
        ipv6_info_grid.addWidget(gateway_label, 1, 4)
        ipv6_info_grid.addWidget(gateway_edit, 1, 5)

        # Device table
        self._device_table = LmTableWidget(objectName='ipv6Table')
        self._device_table.set_columns({IPv6Col.Key: ['Key', 0, None],
                                        IPv6Col.Name: [lx('Name'), 300, 'ipv6_Name'],
                                        IPv6Col.LBName: [lx('Livebox Name'), 300, 'ipv6_LBName'],
                                        IPv6Col.MAC: [lx('MAC'), 120, 'ipv6_MAC'],
                                        IPv6Col.Active: [lx('A'), 10, 'ipv6_Active'],
                                        IPv6Col.IPv4: [lx('IPv4'), 105, 'ipv6_IPv4'],
                                        IPv6Col.IPv6: [lx('IPv6'), 250, 'ipv6_IPv6'],
                                        IPv6Col.Prefix: [lx('Prefix'), 155, 'ipv6_Prefix']})
        self._device_table.set_header_resize([IPv6Col.Name, IPv6Col.LBName])
        self._device_table.set_standard_setup(parent, allow_sel=False)
        self._device_table.setItemDelegate(CenteredIconsDelegate(self, IPV6_ICON_COLUMNS))

        # Button bar
        hbox = QtWidgets.QHBoxLayout()
        ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        hbox.addWidget(ok_button, 1, QtCore.Qt.AlignmentFlag.AlignRight)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(ipv6_info_grid, 0)
        vbox.addWidget(self._device_table, 1)
        vbox.addLayout(hbox, 1)

        LmConfig.set_tooltips(self, 'ipv6')

        self.setWindowTitle(lx('IPv6 Devices'))
        self.setModal(True)
        self.show()


    def load_device_list(self, devices, prefixes):
        if devices is not None:
            self._device_table.setSortingEnabled(False)
            app = self.parent()
            i = 0
            for d in devices:
                if app.displayable_device(d):
                    # First collect global IPv6 addresses
                    ipv6_struct = d.get('IPv6Address')
                    ipv6_addr = []
                    if ipv6_struct is not None:
                        for a in ipv6_struct:
                            scope = a.get('Scope', 'link')
                            if scope != 'link':
                                addr = a.get('Address')
                                if addr is not None:
                                    ipv6_addr.append(addr)

                    # Get prefixes
                    mac = d.get('PhysAddress', '')
                    device_prefixes = []
                    if isinstance(prefixes, list):
                        for m in prefixes:
                            if m.get('MacAddress') == mac:
                                prefix_list = m.get('PDPrefixList')
                                if isinstance(prefix_list, list):
                                    for n in prefix_list:
                                        prefix = n.get('Prefix')
                                        if prefix is not None:
                                            prefix_len = n.get('PrefixLen')
                                            if prefix_len is not None:
                                                prefix += '/' + str(prefix_len)
                                            device_prefixes.append(prefix)

                    if not len(ipv6_addr) and not len(device_prefixes):
                        continue

                    # Display data
                    key = d.get('Key', '')
                    app.add_device_line_key(self._device_table, i, key)

                    app.format_name_widget(self._device_table, i, key, IPv6Col.Name)

                    lb_name = QtWidgets.QTableWidgetItem(d.get('Name', ''))
                    self._device_table.setItem(i, IPv6Col.LBName, lb_name)

                    app.format_mac_widget(self._device_table, i, mac, IPv6Col.MAC)

                    active_status = d.get('Active', False)
                    active_icon = app.format_active_table_widget(active_status)
                    self._device_table.setItem(i, IPv6Col.Active, active_icon)

                    ip_struct = LmTools.determine_ip(d)
                    if ip_struct is None:
                        ipv4 = ''
                        ipv4_reacheable = ''
                        ipv4_reserved = False
                    else:
                        ipv4 = ip_struct.get('Address', '')
                        ipv4_reacheable = ip_struct.get('Status', '')
                        ipv4_reserved = ip_struct.get('Reserved', False)
                    ip = app.format_ipv4_table_widget(ipv4, ipv4_reacheable, ipv4_reserved)
                    self._device_table.setItem(i, IPv6Col.IPv4, ip)

                    ipv6_str = ''
                    resize = False
                    for a in ipv6_addr:
                        if len(ipv6_str):
                            ipv6_str += '\n'
                            resize = True
                        ipv6_str += a
                    self._device_table.setItem(i, IPv6Col.IPv6, QtWidgets.QTableWidgetItem(ipv6_str))
                    if resize:
                        self._device_table.resizeRowToContents(i)

                    prefix_str = ''
                    resize = False
                    for a in device_prefixes:
                        if len(prefix_str):
                            prefix_str += '\n'
                            resize = True
                        prefix_str += a
                    self._device_table.setItem(i, IPv6Col.Prefix, QtWidgets.QTableWidgetItem(prefix_str))
                    if resize:
                        self._device_table.resizeRowToContents(i)

                    i += 1

            self._device_table.sortItems(IPv6Col.Active, QtCore.Qt.SortOrder.DescendingOrder)
            self._device_table.setSortingEnabled(True)