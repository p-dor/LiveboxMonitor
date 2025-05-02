### Livebox Monitor DynDNS setup dialog ###

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.lang.LmLanguages import GetDmzDialogLabel as lx, GetActionsMessage as mx


# ################################ VARS & DEFS ################################

# DMZ device list columns
class DmzCol(IntEnum):
    ID = 0
    IP = 1
    Device = 2
    ExtIPs = 3
    Count = 4


# ################################ DMZ setup dialog ################################
class DmzSetupDialog(QtWidgets.QDialog):
    ### Constructor
    def __init__(self, parent=None):
        super(DmzSetupDialog, self).__init__(parent)
        self.resize(720, 400)

        self._app = parent
        self._api = parent._api
        self._dmz_selection = -1
        self._init = True
        self._ignore_signal = False

        # DMZ box
        dmz_layout = QtWidgets.QHBoxLayout()
        dmz_layout.setSpacing(30)

        dmz_list_layout = QtWidgets.QVBoxLayout()
        dmz_list_layout.setSpacing(5)

        # DMZ list columns
        self._dmz_list = QtWidgets.QTableWidget(objectName='dmzList')
        self._dmz_list.setColumnCount(DmzCol.Count)

        # Set columns
        self._dmz_list.setHorizontalHeaderLabels((lx('ID'), lx('IP'), lx('Device'), lx('External IPs')))

        header = self._dmz_list.horizontalHeader()
        header.setSectionsMovable(False)
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(DmzCol.Device, QtWidgets.QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(DmzCol.ExtIPs, QtWidgets.QHeaderView.ResizeMode.Stretch)

        # Assign tags for tooltips
        model = header.model()
        model.setHeaderData(DmzCol.ID, QtCore.Qt.Orientation.Horizontal, 'zlist_ID', QtCore.Qt.ItemDataRole.UserRole)
        model.setHeaderData(DmzCol.IP, QtCore.Qt.Orientation.Horizontal, 'zlist_IP', QtCore.Qt.ItemDataRole.UserRole)
        model.setHeaderData(DmzCol.Device, QtCore.Qt.Orientation.Horizontal, 'zlist_Device', QtCore.Qt.ItemDataRole.UserRole)
        model.setHeaderData(DmzCol.ExtIPs, QtCore.Qt.Orientation.Horizontal, 'zlist_ExtIPs', QtCore.Qt.ItemDataRole.UserRole)

        self._dmz_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self._dmz_list.setColumnWidth(DmzCol.ID, 100)
        self._dmz_list.setColumnWidth(DmzCol.IP, 100)
        self._dmz_list.setColumnWidth(DmzCol.Device, 150)
        self._dmz_list.setColumnWidth(DmzCol.ExtIPs, 150)
        self._dmz_list.verticalHeader().hide()
        self._dmz_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        self._dmz_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
        self._dmz_list.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self._dmz_list.setMinimumWidth(680)
        self._dmz_list.itemSelectionChanged.connect(self.dmz_list_click)
        LmConfig.SetTableStyle(self._dmz_list)
        self._dmz_list.setMinimumHeight(LmConfig.TableHeight(4))

        dmz_list_layout.addWidget(self._dmz_list, 1)

        dmz_button_box = QtWidgets.QHBoxLayout()
        dmz_button_box.setSpacing(5)

        refresh_button = QtWidgets.QPushButton(lx('Refresh'), objectName='refresh')
        refresh_button.clicked.connect(self.refresh_button_click)
        dmz_button_box.addWidget(refresh_button)
        self._del_dmz_button = QtWidgets.QPushButton(lx('Delete'), objectName='delDmz')
        self._del_dmz_button.clicked.connect(self.del_dmz_button_click)
        dmz_button_box.addWidget(self._del_dmz_button)
        dmz_list_layout.addLayout(dmz_button_box, 0)
        dmz_layout.addLayout(dmz_list_layout, 0)

        dmz_group_box = QtWidgets.QGroupBox(lx('DMZ Devices'), objectName='dmzGroup')
        dmz_group_box.setLayout(dmz_layout)

        # Add DMZ box
        id_label = QtWidgets.QLabel(lx('ID'), objectName='idLabel')
        self._id = QtWidgets.QLineEdit(objectName='id')
        self._id.setText('webui')
        self._id.textChanged.connect(self.id_typed)
        device_label = QtWidgets.QLabel(lx('Device'), objectName='deviceLabel')
        self._device_combo = QtWidgets.QComboBox(objectName='deviceCombo')
        self._device_combo.activated.connect(self.device_selected)
        ip_label = QtWidgets.QLabel(lx('IP Address'), objectName='ipLabel')
        self._ip = QtWidgets.QLineEdit(objectName='ipEdit')
        self._ip.textChanged.connect(self.ip_typed)
        ip_validator = QtGui.QRegularExpressionValidator(QtCore.QRegularExpression('^' + LmTools.IPv4_RS + '$'))
        self._ip.setValidator(ip_validator)
        ext_ips_label = QtWidgets.QLabel(lx('External IPs'), objectName='extIPsLabel')
        self._ext_ips = LmTools.MultiLinesEdit(objectName='extIPsEdit')
        self._ext_ips.setTabChangesFocus(True)
        self._ext_ips.setLineNumber(2)
        self._add_dmz_button = QtWidgets.QPushButton(lx('Add'), objectName='addDmz')
        self._add_dmz_button.clicked.connect(self.add_dmz_button_click)
        self._add_dmz_button.setDisabled(True)

        dmz_edit_grid = QtWidgets.QGridLayout()
        dmz_edit_grid.setSpacing(10)

        dmz_edit_grid.addWidget(id_label, 0, 0)
        dmz_edit_grid.addWidget(self._id, 0, 1)
        dmz_edit_grid.addWidget(device_label, 1, 0)
        dmz_edit_grid.addWidget(self._device_combo, 1, 1)
        dmz_edit_grid.addWidget(ip_label, 2, 0)
        dmz_edit_grid.addWidget(self._ip, 2, 1)
        dmz_edit_grid.addWidget(ext_ips_label, 0, 2)
        dmz_edit_grid.addWidget(self._ext_ips, 0, 3, 1, 2)
        dmz_edit_grid.addWidget(self._add_dmz_button, 2, 4)

        dmz_edit_group_box = QtWidgets.QGroupBox(lx('Add DMZ'), objectName='addDmzGroup')
        dmz_edit_group_box.setLayout(dmz_edit_grid)

        # Button bar
        ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        button_bar = QtWidgets.QHBoxLayout()
        button_bar.setSpacing(10)
        button_bar.addWidget(ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)

        # Final layout
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(20)
        vbox.addWidget(dmz_group_box, 1)
        vbox.addWidget(dmz_edit_group_box, 0)
        vbox.addLayout(button_bar, 0)

        self._ip.setFocus()

        LmConfig.SetToolTips(self, 'dmz')

        self.setWindowTitle(lx('DMZ'))
        self.setModal(True)
        self._app.loadDeviceIpNameMap()
        self.load_device_list()
        self.load_dmz()
        self.show()

        self._init = False


    ### Load DMZ list
    def load_dmz(self):
        self._app.startTask(lx('Loading DMZ devices...'))

        try:
            d = self._api._firewall.get_dmz_devices()
        except BaseException as e:
            self._app.displayError(str(e))
            self._app.endTask()
            return

        if d:
            if not isinstance(d, dict):
                self._app.displayError(mx('Cannot load DMZ device list.', 'dmzLoadErr'))
                self._app.endTask()
                return

            i = 0
            for k in d:
                self._dmz_list.insertRow(i)
                self._dmz_list.setItem(i, DmzCol.ID, QtWidgets.QTableWidgetItem(k))

                z = d[k]
                ip = z.get('DestinationIPAddress', '')
                self._dmz_list.setItem(i, DmzCol.IP, QtWidgets.QTableWidgetItem(ip))
                self._dmz_list.setItem(i, DmzCol.Device, QtWidgets.QTableWidgetItem(self._app.getDeviceNameFromIp(ip)))

                external_ips = z.get('SourcePrefix', '')
                if len(external_ips) == 0:
                    external_ips = lx('All')
                self._dmz_list.setItem(i, DmzCol.ExtIPs, QtWidgets.QTableWidgetItem(external_ips))

                i += 1

            self.dmz_list_click()
        self._app.endTask()


    ### Click on DMZ list item
    def dmz_list_click(self):
        new_selection = self._dmz_list.currentRow()

        # Check if selection really changed
        if not self._init and self._dmz_selection == new_selection:
            return
        self._dmz_selection = new_selection

        self._del_dmz_button.setDisabled(new_selection < 0)


    ### Click on refresh button
    def refresh_button_click(self):
        self._dmz_list.clearContents()
        self._dmz_list.setRowCount(0)
        self._dmz_selection = -1
        self._init = True
        self._app.loadDeviceIpNameMap()
        self.load_dmz()
        self._init = False


    ### Click on delete DMZ button
    def del_dmz_button_click(self):
        i = self._dmz_selection
        if i < 0:
            return

        # Delete the DMZ entry
        dmz_id = self._dmz_list.item(i, DmzCol.ID).text()
        try:
            self._api._firewall.delete_dmz(dmz_id)
        except BaseException as e:
            LmTools.Error(str(e))
            self._app.displayError(mx('Cannot delete DMZ device.', 'dmzDelErr'))
            return

        # Delete the list line
        self._dmz_selection = -1
        self._init = True
        self._dmz_list.removeRow(i)
        self._init = False

        # Update selection
        self._dmz_selection = self._dmz_list.currentRow()


    ### Click on add DMZ button
    def add_dmz_button_click(self):
        # Set parameters
        dmz_id = self._id.text()
        dest_ip = self._ip.text()
        ext_ips = self._ext_ips.toPlainText()

        # Call Livebox API
        try:
            self._api._firewall.add_dmz(dmz_id, dest_ip, ext_ips=ext_ips)
        except BaseException as e:
            self._app.displayError(str(e))
            return

        self.refresh_button_click()
        self._id.setText('webui')
        self._ip.setText('')
        self._ext_ips.setPlainText('')
 

    def load_device_list(self):
        device_map = self._app._deviceIpNameMap
        self._device_combo.clear()

        # Load IPv4 devices
        for i in device_map:
            if device_map[i]['IPVers'] == 'IPv4':
                self._device_combo.addItem(self._app.getDeviceNameFromIp(i), userData=i)

        # Sort by name
        self._device_combo.model().sort(0)

        # Insert unknown device at the beginning
        self._device_combo.insertItem(0, lx('-Unknown-'), userData='')
        self._device_combo.setCurrentIndex(0)


    def id_typed(self, iText):
        self.set_add_button_state()


    def device_selected(self, index):
        if not self._ignore_signal:
            self._ignore_signal = True
            self._ip.setText(self._device_combo.currentData())
            self._ignore_signal = False


    def ip_typed(self, text):
        if not self._ignore_signal:
            self._ignore_signal = True
            i = self._device_combo.findData(text)
            if i < 0:
                i = 0
            self._device_combo.setCurrentIndex(i)
            self._ignore_signal = False

        self.set_add_button_state()


    def set_add_button_state(self):
        self._add_dmz_button.setDisabled((len(self._id.text()) == 0) or
                                         (len(self._ip.text()) == 0))
