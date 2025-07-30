### Livebox Monitor DynDNS setup dialog ###

from enum import IntEnum

from PyQt6 import QtCore, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmTableWidget import LmTableWidget
from LiveboxMonitor.lang.LmLanguages import get_dyndns_label as lx, get_actions_message as mx


# ################################ VARS & DEFS ################################

# Host list columns
class HostCol(IntEnum):
    Service = 0
    HostName = 1
    UserName = 2
    Password = 3
    LastUpdate = 4
    Status = 5


# ################################ DynDNS setup dialog ################################
class DynDnsSetupDialog(QtWidgets.QDialog):
    ### Constructor
    def __init__(self, parent):
        super().__init__(parent)
        self.resize(720, 400)

        self._app = parent
        self._api = parent._api
        self._host_selection = -1
        self._init = True
        self._show_passwords = False

        # Host box
        host_layout = QtWidgets.QHBoxLayout()
        host_layout.setSpacing(30)

        host_list_layout = QtWidgets.QVBoxLayout()
        host_list_layout.setSpacing(5)

        # Host list columns
        self._host_list = LmTableWidget(objectName="hostList")
        self._host_list.set_columns({HostCol.Service: [lx("Service"), 90, "hlist_Service"],
                                     HostCol.HostName: [lx("Host Name"), 80, "hlist_HostName"],
                                     HostCol.UserName: [lx("User Email"), 80, "hlist_UserName"],
                                     HostCol.Password: [lx("Password"), 130, "hlist_Password"],
                                     HostCol.LastUpdate: [lx("Last Update"), 120, "hlist_LastUpdate"],
                                     HostCol.Status: [lx("Status"), 120, "hlist_Status"]})
        self._host_list.set_header_resize([HostCol.HostName, HostCol.UserName])
        self._host_list.set_standard_setup(parent, allow_sort=False)
        self._host_list.setMinimumWidth(880)
        self._host_list.setMinimumHeight(LmConfig.table_height(4))
        self._host_list.itemSelectionChanged.connect(self.host_list_click)

        host_list_layout.addWidget(self._host_list, 1)

        host_button_box = QtWidgets.QHBoxLayout()
        host_button_box.setSpacing(5)

        refresh_button = QtWidgets.QPushButton(lx("Refresh"), objectName="refresh")
        refresh_button.clicked.connect(self.refresh_button_click)
        host_button_box.addWidget(refresh_button)
        self._show_password_button = QtWidgets.QPushButton(lx("Show Passwords"), objectName="showPassword")
        self._show_password_button.clicked.connect(self.show_password_button_click)
        host_button_box.addWidget(self._show_password_button)
        self._del_host_button = QtWidgets.QPushButton(lx("Delete"), objectName="delHost")
        self._del_host_button.clicked.connect(self.del_host_button_click)
        host_button_box.addWidget(self._del_host_button)
        host_list_layout.addLayout(host_button_box, 0)
        host_layout.addLayout(host_list_layout, 0)

        host_group_box = QtWidgets.QGroupBox(lx("Hosts"), objectName="hostGroup")
        host_group_box.setLayout(host_layout)

        # Add host box
        service_label = QtWidgets.QLabel(lx("Service"), objectName="serviceLabel")
        self._service_combo = QtWidgets.QComboBox(objectName="serviceCombo")
        self.load_service_combo()
        hostname_label = QtWidgets.QLabel(lx("Host Name"), objectName="hostNameLabel")
        self._hostname = QtWidgets.QLineEdit(objectName="hostNameEdit")
        self._hostname.textChanged.connect(self.host_typed)
        username_label = QtWidgets.QLabel(lx("User Email"), objectName="userNameLabel")
        self._username = QtWidgets.QLineEdit(objectName="userNameEdit")
        self._username.textChanged.connect(self.host_typed)
        password_label = QtWidgets.QLabel(lx("Password"), objectName="passwordLabel")
        self._password = QtWidgets.QLineEdit(objectName="passwordEdit")
        self._password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self._password.textChanged.connect(self.host_typed)
        self._add_host_button = QtWidgets.QPushButton(lx("Add"), objectName="addHost")
        self._add_host_button.clicked.connect(self.add_host_button_click)
        self._add_host_button.setDisabled(True)

        host_edit_grid = QtWidgets.QGridLayout()
        host_edit_grid.setSpacing(10)

        host_edit_grid.addWidget(service_label, 0, 0)
        host_edit_grid.addWidget(self._service_combo, 0, 1)
        host_edit_grid.addWidget(hostname_label, 0, 2)
        host_edit_grid.addWidget(self._hostname, 0, 3)
        host_edit_grid.addWidget(username_label, 1, 0)
        host_edit_grid.addWidget(self._username, 1, 1)
        host_edit_grid.addWidget(password_label, 1, 2)
        host_edit_grid.addWidget(self._password, 1, 3)
        host_edit_grid.addWidget(self._add_host_button, 0, 4, 2, 2)

        host_edit_group_box = QtWidgets.QGroupBox(lx("Add Host"), objectName="addHostGroup")
        host_edit_group_box.setLayout(host_edit_grid)

        # Button bar
        self._disable_button = QtWidgets.QPushButton(self.get_disable_button_title(), objectName="disableAll")
        self._disable_button.setStyleSheet("padding-left: 15px; padding-right: 15px; padding-top: 3px; padding-bottom: 3px;")
        self._disable_button.clicked.connect(self.disable_button_click)
        ok_button = QtWidgets.QPushButton(lx("OK"), objectName="ok")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        button_bar = QtWidgets.QHBoxLayout()
        button_bar.setSpacing(10)
        button_bar.addWidget(self._disable_button, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        button_bar.addWidget(ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)

        # Final layout
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(20)
        vbox.addWidget(host_group_box, 1)
        vbox.addWidget(host_edit_group_box, 0)
        vbox.addLayout(button_bar, 0)

        self._hostname.setFocus()

        LmConfig.set_tooltips(self, "dyndns")

        self.setWindowTitle(lx("DynDNS"))
        self.setModal(True)
        self.load_hosts()
        self.show()

        self._init = False


    ### Load host list
    def load_hosts(self):
        self._app._task.start(lx("Loading DynDNS hosts..."))

        try:
            try:
                d = self._api._dyndns.get_hosts()
            except Exception as e:
                LmTools.error(str(e))
                self._app.display_error(mx("Cannot load DynDNS host list.", "dynDnsLoadErr"))
                return

            for i, h in enumerate(d):
                self._host_list.insertRow(i)
                self._host_list.setItem(i, HostCol.Service, QtWidgets.QTableWidgetItem(h.get("service", "")))
                self._host_list.setItem(i, HostCol.HostName, QtWidgets.QTableWidgetItem(h.get("hostname", "")))
                self._host_list.setItem(i, HostCol.UserName, QtWidgets.QTableWidgetItem(h.get("username", "")))
                if self._show_passwords:
                    self._host_list.setItem(i, HostCol.Password, QtWidgets.QTableWidgetItem(h.get("password", "")))
                else:
                    self._host_list.setItem(i, HostCol.Password, QtWidgets.QTableWidgetItem("******"))
                self._host_list.setItem(i, HostCol.LastUpdate, QtWidgets.QTableWidgetItem(LmTools.fmt_livebox_timestamp(h.get("last_update"))))
                self._host_list.setItem(i, HostCol.Status, QtWidgets.QTableWidgetItem(h.get("status", "")))

            self.host_list_click()

        finally:
            self._app._task.end()


    ### Click on host list item
    def host_list_click(self):
        new_selection = self._host_list.currentRow()

        # Check if selection really changed
        if not self._init and self._host_selection == new_selection:
            return
        self._host_selection = new_selection

        self._del_host_button.setDisabled(new_selection < 0)


    ### Load service combo box
    def load_service_combo(self):
        try:
            d = self._api._dyndns.get_services()
        except Exception as e:
            LmTools.error(str(e))
            self._app.display_error(mx("Cannot load DynDNS services.", "dynDnsSvcErr"))
            return

        for s in d:
            self._service_combo.addItem(s)


    ### Text changed in host edit box field
    def host_typed(self, text):
        h = self._hostname.text()
        u = self._username.text()
        p = self._password.text()
        self._add_host_button.setDisabled(not len(h) or not len(u) or not len(p))


    ### Click on refresh button
    def refresh_button_click(self):
        self._host_list.clearContents()
        self._host_list.setRowCount(0)
        self._host_selection = -1
        self._init = True
        self.load_hosts()
        self._init = False


    ### Click on show password button
    def show_password_button_click(self):
        if self._show_passwords:
            self._show_password_button.setText(lx("Show Passwords"))
            self._show_passwords = False
        else:
            self._show_password_button.setText(lx("Hide Passwords"))
            self._show_passwords = True
        self.refresh_button_click()


    ### Click on delete host button
    def del_host_button_click(self):
        i = self._host_selection
        if i < 0:
            return

        # Delete the host entry
        hostname = self._host_list.item(i, HostCol.HostName).text()
        try:
            self._api._dyndns.delete_host(hostname)
        except Exception as e:
            LmTools.error(str(e))
            self._app.display_error(mx("Cannot delete DynDNS host.", "dynDnsDelErr"))
            return

        # Delete the list line
        self._host_selection = -1
        self._init = True
        self._host_list.removeRow(i)
        self._init = False

        # Update selection
        self._host_list.setFocus()  # To ensure new selection is highlighted with focus
        self._host_selection = self._host_list.currentRow()


    ### Click on add host button
    def add_host_button_click(self):
        # Hostname has to be unique
        hostname = self._hostname.text()
        if not len(hostname):
            return

        for i in range(self._host_list.rowCount()):
            if self._host_list.item(i, HostCol.HostName).text() == hostname:
                self._app.display_error(mx("Host name {} is already used.", "dynDnsHostName").format(hostname))
                return

        # Set parameters
        service = self._service_combo.currentText()
        username = self._username.text()
        password = self._password.text()

        # Call Livebox API
        try:
            self._api._dyndns.add_host(service, username, hostname, password)
        except Exception as e:
            self._app.display_error(str(e))
            return

        self.refresh_button_click()
        self._username.setText("")
        self._hostname.setText("")
        self._password.setText("")


    ### Get global enable status
    def get_global_enable_status(self):
        try:
            d = self._api._dyndns.get_enable()
        except Exception as e:
            LmTools.error(str(e))
            return False
        if d is None:
            LmTools.error(mx("Cannot get DynDNS global enable status.", "dynDnsEnableErr"))
            return False
        return d


    ### Click on enable/disable button
    def disable_button_click(self):
        enable = not self.get_global_enable_status()
        try:
            self._api._dyndns.set_enable(enable)
        except Exception as e:
            LmTools.error(str(e))

        self._disable_button.setText(self.get_disable_button_title())
        self.refresh_button_click()


    ### get disable all button title
    def get_disable_button_title(self):
        if self.get_global_enable_status():
            return lx("Disable All")
        else:
            return lx("Enable All")
