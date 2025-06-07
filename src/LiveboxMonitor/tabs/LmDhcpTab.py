### Livebox Monitor DHCP tab module ###

from enum import IntEnum
from ipaddress import IPv4Network
from ipaddress import IPv4Address

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmTableWidget import LmTableWidget, NumericSortItem
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.tabs.LmInfoTab import InfoCol
from LiveboxMonitor.dlg.LmDhcpBinding import AddDhcpBindingDialog
from LiveboxMonitor.dlg.LmDhcpSetup import DhcpSetupDialog
from LiveboxMonitor.lang.LmLanguages import get_dhcp_label as lx, get_dhcp_message as mx


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = 'dhcpTab'

# List columns
class DhcpCol(IntEnum):
    Key = 0     # Must be the same as DevCol.Key
    Name = 1
    Domain = 2
    MAC = 3
    IP = 4


# ################################ LmDhcp class ################################
class LmDhcp:

    ### Create DHCP tab
    def create_dhcp_tab(self):
        self._dhcp_tab = QtWidgets.QWidget(objectName=TAB_NAME)

        # DHCP binding list
        self._dhcp_dlist = LmTableWidget(objectName='dhcpDList')
        self._dhcp_dlist.set_columns({DhcpCol.Key: ['Key', 0, None],
                                      DhcpCol.Name: [lx('Name'), 200, 'dlist_Name'],
                                      DhcpCol.Domain: [lx('Domain'), 60, 'dlist_Domain'],
                                      DhcpCol.MAC: [lx('MAC'), 120, 'dlist_MAC'],
                                      DhcpCol.IP: [lx('IP'), 105, 'dlist_IP']})
        self._dhcp_dlist.set_header_resize([DhcpCol.Name])
        self._dhcp_dlist.set_standard_setup(self)
        self._dhcp_dlist.setMinimumWidth(515)

        # DHCP binding button bar
        binding_buttons_box = QtWidgets.QHBoxLayout()
        binding_buttons_box.setSpacing(30)
        refresh_binding_button = QtWidgets.QPushButton(lx('Refresh'), objectName='refreshBinding')
        refresh_binding_button.clicked.connect(self.refresh_dhcp_binding_button_click)
        binding_buttons_box.addWidget(refresh_binding_button)
        add_binding_button = QtWidgets.QPushButton(lx('Add...'), objectName='addBinding')
        add_binding_button.clicked.connect(self.add_dhcp_binding_button_click)
        binding_buttons_box.addWidget(add_binding_button)
        del_binding_button = QtWidgets.QPushButton(lx('Delete'), objectName='delBinding')
        del_binding_button.clicked.connect(self.del_dhcp_binding_button_click)
        binding_buttons_box.addWidget(del_binding_button)

        # DHCP binding layout
        binding_box = QtWidgets.QVBoxLayout()
        binding_box.setSpacing(10)
        binding_box.addWidget(self._dhcp_dlist, 1)
        binding_box.addLayout(binding_buttons_box, 0)

        # Attribute list
        self._dhcp_alist = LmTableWidget(objectName='dhcpAList')
        self._dhcp_alist.set_columns({InfoCol.Attribute: [lx('Attribute'), 200, 'alist_Attribute'],
                                      InfoCol.Value: [lx('Value'), 500, 'alist_Value']})
        self._dhcp_alist.set_header_resize([InfoCol.Value])
        self._dhcp_alist.set_standard_setup(self, allow_sel=False, allow_sort=False)

        # Attribute button bar
        attribute_buttons_box = QtWidgets.QHBoxLayout()
        attribute_buttons_box.setSpacing(30)
        refresh_dhcp_attribute_button = QtWidgets.QPushButton(lx('Refresh'), objectName='refreshDhcpAttribute')
        refresh_dhcp_attribute_button.clicked.connect(self.refresh_dhcp_attribute_button_click)
        attribute_buttons_box.addWidget(refresh_dhcp_attribute_button)
        dhcp_setup_button = QtWidgets.QPushButton(lx('DHCP Setup...'), objectName='dhcpSetup')
        dhcp_setup_button.clicked.connect(self.dhcp_setup_button_click)
        attribute_buttons_box.addWidget(dhcp_setup_button)

        # DHCP attribute layout
        attribute_box = QtWidgets.QVBoxLayout()
        attribute_box.setSpacing(10)
        attribute_box.addWidget(self._dhcp_alist, 1)
        attribute_box.addLayout(attribute_buttons_box, 0)

        # Layout
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.VLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

        hbox = QtWidgets.QHBoxLayout()
        hbox.setSpacing(10)
        hbox.addLayout(binding_box, 0)
        hbox.addWidget(separator)
        hbox.addLayout(attribute_box, 1)
        self._dhcp_tab.setLayout(hbox)

        LmConfig.set_tooltips(self._dhcp_tab, 'dhcp')
        self._tab_widget.addTab(self._dhcp_tab, lx('DHCP'))

        # Set default values
        self._home_ip_server = '192.168.1.1'
        self._home_ip_start = '192.168.1.2'
        self._home_ip_mask = '255.255.255.0'
        self._guest_ip_server = '192.168.144.1'
        self._guest_ip_start = '192.168.144.2'
        self._guest_ip_mask = '255.255.255.0'

        # Init context
        self.dhcp_tab_init()


    ### Init DHCP tab context
    def dhcp_tab_init(self):
        self._dhcp_data_loaded = False


    ### Click on DHCP tab
    def dhcp_tab_click(self):
        if not self._dhcp_data_loaded:
            self._dhcp_data_loaded = True    # Must be first to avoid reentrency during tab drag&drop
            self.load_dhcp_info()            # Load first as home/guest server, start & mask must be known before DHCP bindings
            self.load_dhcp_bindings()


    ### Click on refresh DHCP binding button
    def refresh_dhcp_binding_button_click(self):
        self._dhcp_dlist.clearContents()
        self._dhcp_dlist.setRowCount(0)
        self.load_dhcp_bindings()


    ### Click on add DHCP binding button
    def add_dhcp_binding_button_click(self):
        # Collect already used IPs from DHCP bindings (as a set for uniqueness)
        used_ips = {
            self._dhcp_dlist.item(i, DhcpCol.IP).text()
            for i in range(self._dhcp_dlist.rowCount())
        }

        # Add IPs from active devices
        device_list = self.get_device_list()
        used_ips.update(d['IP'] for d in device_list if d.get('Active'))

        # Find appropriate IP suggestions
        home_ip_suggest = self.find_first_available_ip('Home', used_ips)
        guest_ip_suggest = self.find_first_available_ip('Guest', used_ips)

        # Show dialog for adding DHCP binding
        dialog = AddDhcpBindingDialog(home_ip_suggest, guest_ip_suggest, self)
        if dialog.exec():
            mac_addr = dialog.get_mac_address()
            ip_addr = dialog.get_ip_address()
            guest = dialog.get_domain() == 'Guest'
            try:
                self._api._dhcp.add_lease(mac_addr, ip_addr, guest)
            except Exception as e:
                self.display_error(str(e))
            self.refresh_dhcp_binding_button_click()


    ### Click on delete DHCP binding button
    def del_dhcp_binding_button_click(self):
        current_selection = self._dhcp_dlist.currentRow()
        if current_selection >= 0:
            mac_addr = self._dhcp_dlist.item(current_selection, DhcpCol.MAC).text()
            guest = self._dhcp_dlist.item(current_selection, DhcpCol.Domain).text() == 'Guest'
            try:
                self._api._dhcp.delete_lease(mac_addr, guest)
            except Exception as e:
                self.display_error(str(e))
            self.refresh_dhcp_binding_button_click()
        else:
            self.display_error(mx('Please select a DHCP binding.', 'dhcpSelect'))


    ### Click on refresh DHCP attributes button
    def refresh_dhcp_attribute_button_click(self):
        self._dhcp_alist.clearContents()
        self._dhcp_alist.setRowCount(0)
        self.load_dhcp_info()


    ### Click on DHCP setup button
    def dhcp_setup_button_click(self):
        # Retrieve current values
        try:
            d = self._api._dhcp.get_setup()
        except Exception as e:
            self.display_error(str(e))
            return

        # Load current values
        dhcp_enabled = d.get('DHCPEnable')
        dhcp_address = d.get('Address')
        dhcp_mask = d.get('Netmask')
        dhcp_min_address = d.get('DHCPMinAddress')
        dhcp_max_address = d.get('DHCPMaxAddress')
        if ((dhcp_enabled is None) or
            (dhcp_address is None) or
            (dhcp_mask is None) or
            (dhcp_min_address is None) or
            (dhcp_max_address is None)):
            self.display_error(mx('Cannot retrieve DHCP information.', 'dhcpLoad'))
            return

        # Ask user
        dialog = DhcpSetupDialog(dhcp_enabled, dhcp_address, dhcp_mask, dhcp_min_address, dhcp_max_address, self)
        if dialog.exec():
            new_dhcp_enabled = dialog.get_enabled()
            new_dhcp_address = dialog.get_address()
            new_dhcp_mask = dialog.get_mask()
            new_dhcp_min_address = dialog.get_min_address()
            new_dhcp_max_address = dialog.get_max_address()

            change = False

            # Warn in case of DHCP disabling
            if (not new_dhcp_enabled) and dhcp_enabled:
                change = True
                if not self.ask_question(mx('Deactivating the DHCP server is likely to disconnect your home devices. Continue?',
                                            'deactiv')):
                    return

            # Warn in case of address changes
            if ((new_dhcp_address != dhcp_address) or
                (new_dhcp_mask != dhcp_mask) or
                (new_dhcp_min_address != dhcp_min_address) or
                (new_dhcp_max_address != dhcp_max_address)):
                change = True
                if not self.ask_question(mx('Modifying the IP address of your Livebox and the other settings of the DHCP server, ' \
                                            'may interrupt all your services. You will need to redefine the static IP addresses ' \
                                            'according to the new addressing plan. Continue?', 'addrChange')):
                    return

            if change:
                # Determine network prefix length
                i = new_dhcp_address.split('.')
                try:
                    network = IPv4Network(i[0] + '.' + i[1] + '.' + i[2] + '.0/' + new_dhcp_mask)
                except Exception as e:
                    LmTools.error(str(e))
                    self.display_error(mx('Wrong values. Error: {}', 'dhcpValErr').format(e))
                    return
                new_dhcp_prefix_len = network.prefixlen

                p = {'Address': new_dhcp_address,
                     'Netmask': new_dhcp_mask,
                     'DHCPEnable': new_dhcp_enabled,
                     'DHCPMinAddress': new_dhcp_min_address,
                     'DHCPMaxAddress': new_dhcp_max_address,
                     'PrefixLength': new_dhcp_prefix_len}
                try:
                    self._api._dhcp.set_setup(p)
                except Exception as e:
                    self.display_error(str(e))


    ### Load DHCP bindings
    def load_dhcp_bindings(self):
        self._task.start(lx('Getting DHCP bindings...'))
        self._dhcp_dlist.setSortingEnabled(False)

        # Home domain
        try:
            d = self._api._dhcp.get_leases()
        except Exception as e:
            LmTools.error(str(e))
            d = None
        self.load_dhcp_bindings_in_list(d, 'Home')

        # Guest domain
        try:
            d = self._api._dhcp.get_leases(True)
        except Exception as e:
            LmTools.error(str(e))
            d = None
        self.load_dhcp_bindings_in_list(d, 'Guest')

        self._dhcp_dlist.sortItems(DhcpCol.IP, QtCore.Qt.SortOrder.AscendingOrder)
        self._dhcp_dlist.setSortingEnabled(True)

        self._task.end()


    ### Load DHCP bindings in the list
    def load_dhcp_bindings_in_list(self, bindings, domain):
        if bindings is None:
            self.display_error(mx('Cannot load {} DHCP bindings.', 'bindLoad').format(domain))
            return

        i = self._dhcp_dlist.rowCount()
        for b in bindings:
            key = b.get('MACAddress', '').upper()
            ip = b.get('IPAddress', '')

            self.add_device_line_key(self._dhcp_dlist, i, key)
            self.format_name_widget(self._dhcp_dlist, i, key, DhcpCol.Name)
            self._dhcp_dlist.setItem(i, DhcpCol.Domain, QtWidgets.QTableWidgetItem(domain))
            self.format_mac_widget(self._dhcp_dlist, i, key, DhcpCol.MAC)

            ip_item = NumericSortItem(ip)
            try:
                ip_item.setData(QtCore.Qt.ItemDataRole.UserRole, int(IPv4Address(ip)))
            except Exception:
                ip_item.setData(QtCore.Qt.ItemDataRole.UserRole, 0)
            self._dhcp_dlist.setItem(i, DhcpCol.IP, ip_item)

            i += 1


    ### First first available IP in the IP range
    def find_first_available_ip(self, domain, used_ips):
        # Get network
        network = self.get_domain_network(domain)
        if network is None:
            return ''

        # Setup minimum address
        if domain == 'Home':
            min_ip = IPv4Address(self._home_ip_start)
        else:
            min_ip = IPv4Address(self._guest_ip_start)

        # Create iterator
        iterator = (ip for ip in network.hosts() if (str(ip) not in used_ips) and (ip >= min_ip))

        return str(next(iterator))


    ### Find if an IP is in domain network
    def is_ip_in_network(self, ip, domain):
        network = self.get_domain_network(domain)
        if network is None:
            return False
        try:    # Due to a LB firmware issue the IP can be empty even if the device is active
            return IPv4Address(ip) in network
        except Exception:
            return False


    ### Get domain network
    def get_domain_network(self, domain):
        # Select parameters
        if domain == 'Home':
            server = self._home_ip_server
            mask = self._home_ip_mask
        else:
            server = self._guest_ip_server
            mask = self._guest_ip_mask

        # Set network
        if LmTools.is_ipv4(server):
            i = server.split('.')
            try:
                return IPv4Network(i[0] + '.' + i[1] + '.' + i[2] + '.0/' + mask)
            except Exception:
                return None
        return None


    ### Load DHCP infos list
    def load_dhcp_info(self):
        self._task.start(lx('Getting DHCP information...'))

        i = 0
        i = self.addTitleLine(self._dhcp_alist, i, lx('DHCP Home Information'))

        # Home domain + DHCPv6 infos
        g = None
        try:
            d = self._api._dhcp.get_info()
        except Exception as e:
            LmTools.error(str(e))
            d = None
        if d:
            g = d.get('guest')
            d = d.get('default')
        if d:
            i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv4 Enabled'), LmTools.fmt_bool(d.get('Enable')))
            i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv4 Status'), d.get('Status'))
            i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv4 Gateway'), d.get('Server'))
            self._home_ip_server = d.get('Server')
            i = self.addInfoLine(self._dhcp_alist, i, lx('Subnet Mask'), d.get('SubnetMask'))
            self._home_ip_mask = d.get('SubnetMask')
            i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv4 Start'), d.get('MinAddress'))
            self._home_ip_start = d.get('MinAddress')
            i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv4 End'), d.get('MaxAddress'))
            i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv4 Lease Time'), LmTools.fmt_time(d.get('LeaseTime')))
            i = self.addInfoLine(self._dhcp_alist, i, lx('DNS Servers'), d.get('DNSServers'))
        else:
            i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv4'), 'DHCPv4.Server:getDHCPServerPool query error', LmTools.ValQual.Error)

        try:
            d = self._api._dhcp.get_v6_server_status()
        except Exception as e:
            LmTools.error(str(e))
            i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv6'), 'DHCPv6.Server:getDHCPv6ServerStatus query error', LmTools.ValQual.Error)
        else:
            i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv6 Status'), d)

        try:
            d = self._api._dhcp.get_v6_prefix()
        except Exception as e:
            LmTools.error(str(e))
            i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv6'), 'DHCPv6.Server:getPDPrefixInformation query error', LmTools.ValQual.Error)
        else:
            if d:
                prefix = d[0].get('Prefix')
                if prefix is not None:
                    prefix_len = d[0].get('PrefixLen')
                    if prefix_len is not None:
                        prefix += '/' + str(prefix_len)
                    i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv6 Prefix'), prefix)

        # Guest domain
        if g is not None:
            i = self.addTitleLine(self._dhcp_alist, i, lx('DHCP Guest Information'))

            i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv4 Enabled'), LmTools.fmt_bool(g.get('Enable')))
            i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv4 Status'), g.get('Status'))
            i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv4 Gateway'), g.get('Server'))
            self._guest_ip_server = g.get('Server')
            i = self.addInfoLine(self._dhcp_alist, i, lx('Subnet Mask'), g.get('SubnetMask'))
            self._guest_ip_mask = g.get('SubnetMask')
            i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv4 Start'), g.get('MinAddress'))
            self._guest_ip_start = g.get('MinAddress')
            i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv4 End'), g.get('MaxAddress'))
            i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv4 Lease Time'), LmTools.fmt_time(g.get('LeaseTime')))
            i = self.addInfoLine(self._dhcp_alist, i, lx('DNS Servers'), g.get('DNSServers'))


        # DHCPv4
        i = self.addTitleLine(self._dhcp_alist, i, lx('DHCPv4'))

        try:
            d = self._api._dhcp.get_mibs(True, True)
        except Exception as e:
            LmTools.error(str(e))
            i = self.addInfoLine(self._dhcp_alist, i, lx('DHCPv4'), 'NeMo.Intf.data:getMIBs query error', LmTools.ValQual.Error)
        else:
            p = d.get('dhcp')

            if p is not None:
                p = p.get('dhcp_data')
            if p is not None:
                i = self.addInfoLine(self._dhcp_alist, i, lx('Status'), p.get('DHCPStatus'))
                i = self.addInfoLine(self._dhcp_alist, i, lx('Lease Time'), LmTools.fmt_time(p.get('LeaseTime')))
                i = self.addInfoLine(self._dhcp_alist, i, lx('Lease Time Remaining'), LmTools.fmt_time(p.get('LeaseTimeRemaining')))
                i = self.addInfoLine(self._dhcp_alist, i, lx('Check Authentication'), LmTools.fmt_bool(p.get('CheckAuthentication')))
                i = self.addInfoLine(self._dhcp_alist, i, lx('Authentication Information'), p.get('AuthenticationInformation'))
                i = self.load_dhcp_info_options(lx('DHCPv4 Sent Options'), i, p.get('SentOption'))
                i = self.load_dhcp_info_options(lx('DHCPv4 Received Options'), i, p.get('ReqOption'))

            # DHCPv6
            i = self.addTitleLine(self._dhcp_alist, i, lx('DHCPv6'))

            p = d.get('dhcpv6')

            if p is not None:
                p = p.get('dhcpv6_data')
            if p is not None:
                i = self.addInfoLine(self._dhcp_alist, i, lx('Status'), p.get('DHCPStatus'))
                i = self.addInfoLine(self._dhcp_alist, i, lx('DUID'), p.get('DUID'))
                i = self.addInfoLine(self._dhcp_alist, i, lx('Request Addresses'), LmTools.fmt_bool(p.get('RequestAddresses')))
                i = self.addInfoLine(self._dhcp_alist, i, lx('Request Prefixes'), LmTools.fmt_bool(p.get('RequestPrefixes')))
                i = self.addInfoLine(self._dhcp_alist, i, lx('Requested Options'), p.get('RequestedOptions'))
                i = self.addInfoLine(self._dhcp_alist, i, lx('Check Authentication'), LmTools.fmt_bool(p.get('CheckAuthentication')))
                i = self.addInfoLine(self._dhcp_alist, i, lx('Authentication Information'), p.get('AuthenticationInfo'))
                i = self.load_dhcp_info_options(lx('DHCPv6 Sent Options'), i, p.get('SentOption'))
                i = self.load_dhcp_info_options(lx('DHCPv6 Received Options'), i, p.get('ReceivedOption'))

        self._task.end()


    ### Update DHCP infos list
    def load_dhcp_info_options(self, title, index, options):
        if options is not None:
            index = self.addTitleLine(self._dhcp_alist, index, title)
            for k in options:
                o = options[k]
                index = self.addInfoLine(self._dhcp_alist, index, str(o.get('Tag', '?')), o.get('Value'))

        return index
