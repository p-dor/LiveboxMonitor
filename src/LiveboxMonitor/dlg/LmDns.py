### Livebox Monitor DNS dialog ###

from enum import IntEnum

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmConfig
from LiveboxMonitor.app.LmTableWidget import LmTableWidget, CenteredIconsDelegate
from LiveboxMonitor.lang.LmLanguages import get_dns_label as lx
from LiveboxMonitor.tools import LmTools


# ################################ VARS & DEFS ################################

# List columns
class DnsCol(IntEnum):
    Key = 0     # Must be the same as DevCol.Key
    Name = 1
    LBName = 2
    MAC = 3
    Active = 4
    IP = 5
    DNS = 6
DNS_ICON_COLUMNS = [DnsCol.Active]


# ################################ DNS dialog ################################
class DnsDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(850, 56 + LmConfig.dialog_height(12))

        # Device table
        self._device_table = LmTableWidget(objectName="dnsTable")
        self._device_table.set_columns({DnsCol.Key: ["Key", 0, None],
                                        DnsCol.Name: [lx("Name"), 300, "dns_Name"],
                                        DnsCol.LBName: [lx("Livebox Name"), 300, "dns_LBName"],
                                        DnsCol.MAC: [lx("MAC"), 120, "dns_MAC"],
                                        DnsCol.Active: [lx("A"), 10, "dns_Active"],
                                        DnsCol.IP: [lx("IP"), 105, "dns_IP"],
                                        DnsCol.DNS: [lx("DNS"), 250, "dns_DNS"]})
        self._device_table.set_header_resize([DnsCol.Name, DnsCol.LBName])
        self._device_table.set_standard_setup(parent, allow_sel=False)
        self._device_table.setItemDelegate(CenteredIconsDelegate(self, DNS_ICON_COLUMNS))

        # Button bar
        hbox = QtWidgets.QHBoxLayout()
        ok_button = QtWidgets.QPushButton(lx("OK"), objectName="ok")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        hbox.addWidget(ok_button, 1, QtCore.Qt.AlignmentFlag.AlignRight)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addWidget(self._device_table, 1)
        vbox.addLayout(hbox, 1)

        LmConfig.set_tooltips(self, "dns")

        self.setWindowTitle(lx("Devices DNS"))
        self.setModal(True)
        self.show()


    ### Load device list
    def load_device_list(self, devices):
        if devices is not None:
            self._device_table.setSortingEnabled(False)
            i = 0
            app = self.parent()
            for d in devices:
                if app.displayable_device(d):
                    # First collect DNS name
                    dns_name = None
                    name_list = d.get("Names", [])
                    if len(name_list):
                        for name in name_list:
                            if name.get("Source", "") == "dns":
                                dns_name = name.get("Name", "")
                                break
                    if dns_name is None:
                        continue

                    # Display data
                    key = d.get("Key", "")
                    app.add_device_line_key(self._device_table, i, key)

                    app.format_name_widget(self._device_table, i, key, DnsCol.Name)

                    lb_name = QtWidgets.QTableWidgetItem(d.get("Name", ""))
                    self._device_table.setItem(i, DnsCol.LBName, lb_name)

                    app.format_mac_widget(self._device_table, i, d.get("PhysAddress", ""), DnsCol.MAC)

                    active_status = d.get("Active", False)
                    active_icon = app.format_active_table_widget(active_status)
                    self._device_table.setItem(i, DnsCol.Active, active_icon)

                    ip_struct = LmTools.determine_ip(d)
                    if ip_struct is None:
                        ipv4 = ""
                        ipv4_reacheable = ""
                        ipv4_reserved = False
                    else:
                        ipv4 = ip_struct.get("Address", "")
                        ipv4_reacheable = ip_struct.get("Status", "")
                        ipv4_reserved = ip_struct.get("Reserved", False)
                    ip = app.format_ipv4_table_widget(ipv4, ipv4_reacheable, ipv4_reserved)
                    self._device_table.setItem(i, DnsCol.IP, ip)

                    self._device_table.setItem(i, DnsCol.DNS, QtWidgets.QTableWidgetItem(dns_name))

                    i += 1

            self._device_table.sortItems(DnsCol.Active, QtCore.Qt.SortOrder.DescendingOrder)
            self._device_table.setSortingEnabled(True)
