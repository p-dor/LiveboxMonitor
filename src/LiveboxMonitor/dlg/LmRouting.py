### Livebox Monitor Routing setup dialog ###

from enum import IntEnum
from ipaddress import IPv4Network
import random
import string

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmConfig
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmTableWidget import LmTableWidget, CenteredIconsDelegate, NumericSortItem
from LiveboxMonitor.lang.LmLanguages import get_routing_label as lx, get_actions_message as mx
from LiveboxMonitor.tools import LmTools


# ################################ VARS & DEFS ################################

# Rule list columns
class RuleCol(IntEnum):
    Name = 0
    DestNetwork = 1
    DestMask = 2
    Gateway = 3
    Priority = 4
    Enabled = 5
    Status = 6
ICON_COLUMNS = [RuleCol.Enabled, RuleCol.Status]

# Priority base value
PRIORITY_BASE = 3000


# ################################ Routing setup dialog ################################
class RoutingSetupDialog(QtWidgets.QDialog):
    ### Constructor
    def __init__(self, parent):
        super().__init__(parent)
        self.resize(720, 400)

        self._app = parent
        self._api = parent._api
        self._rule_selection = -1
        self._init = True
        self._load_for_edit = False

        # Rule box
        rule_layout = QtWidgets.QHBoxLayout()
        rule_layout.setSpacing(30)

        rule_list_layout = QtWidgets.QVBoxLayout()
        rule_list_layout.setSpacing(5)

        # Rule list columns
        self._rule_list = LmTableWidget(objectName="ruleList")
        self._rule_list.set_columns({RuleCol.Name: ["Name", 0, None],
                                     RuleCol.DestNetwork: [lx("Destination Network"), 105, "rlist_DestNetwork"],
                                     RuleCol.DestMask: [lx("Mask"), 105, "rlist_DestMask"],
                                     RuleCol.Gateway: [lx("Gateway"), 105, "rlist_Gateway"],
                                     RuleCol.Priority: [lx("Priority"), 60, "rlist_Priority"],
                                     RuleCol.Enabled: [lx("A"), 20, "rlist_Enabled"],
                                     RuleCol.Status: [lx("Status"), 70, "rlist_Status"]})
        self._rule_list.set_header_resize([RuleCol.DestNetwork, RuleCol.DestMask, RuleCol.Gateway])
        self._rule_list.set_standard_setup(parent, allow_sort=False)
        self._rule_list.setItemDelegate(CenteredIconsDelegate(self, ICON_COLUMNS))
        self._rule_list.setMinimumWidth(480)
        self._rule_list.setMinimumHeight(LmConfig.table_height(4))
        self._rule_list.itemSelectionChanged.connect(self.rule_list_click)

        rule_list_layout.addWidget(self._rule_list, 1)

        rule_button_box = QtWidgets.QHBoxLayout()
        rule_button_box.setSpacing(5)

        refresh_button = QtWidgets.QPushButton(lx("Refresh"), objectName="refresh")
        refresh_button.clicked.connect(self.refresh_button_click)
        rule_button_box.addWidget(refresh_button)
        self._enable_button = QtWidgets.QPushButton(lx("Enable"), objectName="enableRule")
        self._enable_button.clicked.connect(self.enable_button_click)
        rule_button_box.addWidget(self._enable_button)
        self._del_rule_button = QtWidgets.QPushButton(lx("Delete"), objectName="delRule")
        self._del_rule_button.clicked.connect(self.del_rule_button_click)
        rule_button_box.addWidget(self._del_rule_button)
        rule_list_layout.addLayout(rule_button_box, 0)
        rule_layout.addLayout(rule_list_layout, 0)

        rule_group_box = QtWidgets.QGroupBox(lx("Rules"), objectName="ruleGroup")
        rule_group_box.setLayout(rule_layout)

        # Add/Modify rule box
        ip_reg_exp = QtCore.QRegularExpression("^" + LmTools.IPv4_RS + "$")
        ip_validator = QtGui.QRegularExpressionValidator(ip_reg_exp)

        dest_network_label = QtWidgets.QLabel(lx("Destination network"), objectName="destNetworkLabel")
        self._dest_network = QtWidgets.QLineEdit(objectName="destNetworkEdit")
        self._dest_network.setValidator(ip_validator)
        self._dest_network.textChanged.connect(self.rule_typed)

        dest_mask_label = QtWidgets.QLabel(lx("Destination mask"), objectName="destMaskLabel")
        self._dest_mask = QtWidgets.QLineEdit(objectName="destMaskEdit")
        self._dest_mask.setValidator(ip_validator)
        self._dest_mask.textChanged.connect(self.rule_typed)

        gateway_label = QtWidgets.QLabel(lx("Gateway"), objectName="gatewayLabel")
        self._gateway = QtWidgets.QLineEdit(objectName="gatewayEdit")
        self._gateway.setValidator(ip_validator)
        self._gateway.textChanged.connect(self.rule_typed)

        priority_label = QtWidgets.QLabel(lx("Priority"), objectName="priorityLabel")
        self._priority = QtWidgets.QSpinBox(objectName="priorityEdit")

        self._add_rule_button = QtWidgets.QPushButton(lx("Add"), objectName="addRule")
        self._add_rule_button.clicked.connect(self.add_rule_button_click)
        self._add_rule_button.setDisabled(True)

        self._edit_rule_button = QtWidgets.QPushButton(lx("Edit"), objectName="editRule")
        self._edit_rule_button.clicked.connect(self.edit_rule_button_click)
        self._edit_rule_button.setDisabled(True)

        self._enabled = QtWidgets.QCheckBox(lx("Enabled"), objectName="enabledCheckbox")

        rule_edit_grid = QtWidgets.QGridLayout()
        rule_edit_grid.setSpacing(10)

        rule_edit_grid.addWidget(dest_network_label, 0, 0)
        rule_edit_grid.addWidget(self._dest_network, 0, 1)
        rule_edit_grid.addWidget(dest_mask_label, 0, 2)
        rule_edit_grid.addWidget(self._dest_mask, 0, 3)
        rule_edit_grid.addWidget(self._add_rule_button, 0, 4)
        rule_edit_grid.addWidget(gateway_label, 1, 0)
        rule_edit_grid.addWidget(self._gateway, 1, 1)
        rule_edit_grid.addWidget(priority_label, 1, 2)
        rule_edit_grid.addWidget(self._priority, 1, 3)
        rule_edit_grid.addWidget(self._edit_rule_button, 1, 4)
        rule_edit_grid.addWidget(self._enabled, 2, 0)

        rule_edit_group_box = QtWidgets.QGroupBox(lx("Add/Edit Rule"), objectName="addEditRuleGroup")
        rule_edit_group_box.setLayout(rule_edit_grid)

        # Button bar
        ok_button = QtWidgets.QPushButton(lx("OK"), objectName="ok")
        ok_button.clicked.connect(self.accept)
        ok_button.setDefault(True)
        button_bar = QtWidgets.QHBoxLayout()
        button_bar.setSpacing(10)
        button_bar.addWidget(ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)

        # Final layout
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(20)
        vbox.addWidget(rule_group_box, 1)
        vbox.addWidget(rule_edit_group_box, 0)
        vbox.addLayout(button_bar, 0)

        self._dest_network.setFocus()

        LmConfig.set_tooltips(self, "routing")

        self.setWindowTitle(lx("Routing Table"))
        self.setModal(True)
        self.load_rules()
        self.show()

        self._init = False


    ### Load rule list
    def load_rules(self):
        self._app._task.start(lx("Loading Routing Table Rules..."))

        try:
            try:
                d = self._api._routing.get_list()
            except Exception as e:
                LmTools.error(str(e))
                self._app.display_error(mx("Cannot load routing table.", "routingLoadErr"))
                return

            for i, name in enumerate(d):
                self._rule_list.insertRow(i)
                self._rule_list.setItem(i, RuleCol.Name, QtWidgets.QTableWidgetItem(name))
                r = d[name]
                self._rule_list.setItem(i, RuleCol.DestNetwork, QtWidgets.QTableWidgetItem(r.get("Dst", "")))
                self._rule_list.setItem(i, RuleCol.DestMask, self.format_dest_mask(r.get("DstLen", 0)))
                self._rule_list.setItem(i, RuleCol.Gateway, QtWidgets.QTableWidgetItem(r.get("Gateway", "")))
                self._rule_list.setItem(i, RuleCol.Priority, self.format_priority(r.get("Priority", PRIORITY_BASE)))
                self._rule_list.setItem(i, RuleCol.Enabled, self.format_enabled(r.get("Enable", False)))
                self._rule_list.setItem(i, RuleCol.Status, self.format_status(r.get("Status", 0)))

            self._rule_list.sortItems(RuleCol.Priority, QtCore.Qt.SortOrder.AscendingOrder)
            self.rule_list_click()

        finally:
            self._app._task.end()


    ### Format destination mask column
    def format_dest_mask(self, mask):
        try:
            mask_str = str(IPv4Network(f"0.0.0.0/{mask}").netmask)
        except Exception:
            mask_str = "0.0.0.0"
        return QtWidgets.QTableWidgetItem(mask_str)


    ### Format priority column
    def format_priority(self, priority):
        value = priority - PRIORITY_BASE
        item = NumericSortItem(str(value))
        item.setData(QtCore.Qt.ItemDataRole.UserRole, value)
        return item


    ### Format enabled column
    def format_enabled(self, enable):
        item = QtWidgets.QTableWidgetItem()
        if enable:
            item.setIcon(QtGui.QIcon(LmIcon.TickPixmap))
            item.setData(QtCore.Qt.ItemDataRole.UserRole, True)
        else:
            item.setIcon(QtGui.QIcon(LmIcon.CrossPixmap))
            item.setData(QtCore.Qt.ItemDataRole.UserRole, False)
        return item


    ### Format status column
    def format_status(self, status):
        match status:
            case "Bound":
                item = QtWidgets.QTableWidgetItem()
                item.setIcon(QtGui.QIcon(LmIcon.TickPixmap))
                item.setData(QtCore.Qt.ItemDataRole.UserRole, status)
            case "Disabled":
                item = QtWidgets.QTableWidgetItem()
                item.setIcon(QtGui.QIcon(LmIcon.CrossPixmap))
                item.setData(QtCore.Qt.ItemDataRole.UserRole, status)
            case _:     # Can be "Error"
                item = QtWidgets.QTableWidgetItem(status)
                item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        return item


    ### Click on rule list item
    def rule_list_click(self):
        new_selection = self._rule_list.currentRow()

        # Check if selection really changed
        if not self._init and self._rule_selection == new_selection:
            return
        self._rule_selection = new_selection

        self.load_rule_edit()
        self.update_buttons_state(True)


    ### Load the rule edit field according to selection
    def load_rule_edit(self):
        if self._rule_selection < 0:
            return

        self._load_for_edit = True
        self._dest_network.setText(self._rule_list.item(self._rule_selection, RuleCol.DestNetwork).text())
        self._dest_mask.setText(self._rule_list.item(self._rule_selection, RuleCol.DestMask).text())
        self._gateway.setText(self._rule_list.item(self._rule_selection, RuleCol.Gateway).text())
        self._priority.setValue(self._rule_list.item(self._rule_selection, RuleCol.Priority).data(QtCore.Qt.ItemDataRole.UserRole))
        self._enabled.setChecked(self._rule_list.item(self._rule_selection, RuleCol.Enabled).data(QtCore.Qt.ItemDataRole.UserRole))
        self._load_for_edit = False


    ### Text changed in rule edit box field
    def rule_typed(self, text):
        if not self._load_for_edit:
            self.update_buttons_state()


    ### Update state of all buttons
    def update_buttons_state(self, select_change=False):
        n = self._dest_network.text()
        m = self._dest_mask.text()
        g = self._gateway.text()
        rule_ready = n and m and g
        self._add_rule_button.setDisabled(not rule_ready)
        self._edit_rule_button.setDisabled((self._rule_selection < 0) or (not rule_ready))

        if select_change:
            self._del_rule_button.setDisabled(self._rule_selection < 0)
            self._enable_button.setDisabled(self._rule_selection < 0)

            if self._rule_selection >= 0:
                enabled = self._rule_list.item(self._rule_selection, RuleCol.Enabled).data(QtCore.Qt.ItemDataRole.UserRole)
                self._enable_button.setText(lx("Disable") if enabled else lx("Enable"))



    ### Click on refresh button
    def refresh_button_click(self):
        self._rule_list.clearContents()
        self._rule_list.setRowCount(0)
        self._rule_selection = -1
        self._init = True
        self.load_rules()
        self._init = False


    ### Click on enable button
    def enable_button_click(self):
        if self._rule_selection < 0:
            return

        rule_name = self._rule_list.item(self._rule_selection, RuleCol.Name).text()
        enabled = self._rule_list.item(self._rule_selection, RuleCol.Enabled).data(QtCore.Qt.ItemDataRole.UserRole)

        self._app._task.start()
        try:
            self._api._routing.set_enable(rule_name, not enabled)
        except Exception as e:
            self._app.display_error(str(e))
            return
        finally:
            self._app._task.end()

        self.refresh_button_click()


    ### Click on delete rule button
    def del_rule_button_click(self):
        i = self._rule_selection
        if i < 0:
            return

        rule_name = self._rule_list.item(i, RuleCol.Name).text()
        self._app._task.start()
        try:
            self._api._routing.delete(rule_name)
        except Exception as e:
            self._app.display_error(str(e))
            return
        finally:
            self._app._task.end()

        # Delete the list line
        self._rule_selection = -1
        self._init = True
        self._rule_list.removeRow(i)
        self._init = False

        # Update selection
        self._rule_list.setFocus()  # To ensure new selection is highlighted with focus
        self.rule_list_click()


    ### Click on add rule button
    def add_rule_button_click(self):
        # Generate a unique random name
        while True:
            rule_name = self.generate_rule_name()

            # Check uniqueness
            is_unique = True
            for i in range(self._rule_list.rowCount()):
                if self._rule_list.item(i, RuleCol.Name).text() == rule_name:
                    is_unique = False
                    break
            if is_unique:
                break

        # Generate Livebox route
        route = self.generate_livebox_route(rule_name)
        if not route:
            return

        # Call Livebox API
        self._app._task.start()
        try:
            self._api._routing.add(route)
        except Exception as e:
            self._app.display_error(str(e))
            return
        finally:
            self._app._task.end()

        # Reset edit fields
        self.reset_edit_fields()

        # Refresh list
        self.refresh_button_click()


    ### Click on edit rule button
    def edit_rule_button_click(self):
        i = self._rule_selection
        if i < 0:
            return

        # Find rule name
        rule_name = self._rule_list.item(i, RuleCol.Name).text()

        # Generate Livebox route with same name
        route = self.generate_livebox_route(rule_name)
        if not route:
            return

        self._app._task.start()
        try:
            # Start by deleting the corresponding rule
            try:
                self._api._routing.delete(rule_name)
            except Exception as e:
                self._app.display_error(str(e))
                return

            # Then create the route
            try:
                self._api._routing.add(route)
            except Exception as e:
                self._app.display_error(str(e))
                return
        finally:
            self._app._task.end()

        # Reset edit fields
        self.reset_edit_fields()

        # Refresh list
        self.refresh_button_click()


    ### Reset edit fields
    def reset_edit_fields(self):
        self._load_for_edit = True
        self._dest_network.setText("")
        self._dest_mask.setText("")
        self._gateway.setText("")
        self._priority.setValue(0)
        self._enabled.setChecked(False)
        self._load_for_edit = False


    ### Generate a Livebox route structure corresponding to entered values - returns None if errors
    def generate_livebox_route(self, rule_name):
        # Validate destination network
        dest_network = self._dest_network.text()
        if not LmTools.is_ipv4(dest_network):
            self._app.display_error(mx("{} is not a valid address.", "addrErr").format(dest_network))
            self._dest_network.setFocus()
            return None

        # Validate destination subnet mask
        dest_mask = self._dest_mask.text()
        try:
            dest_len = IPv4Network(("0.0.0.0", dest_mask)).prefixlen
        except Exception:
            self._app.display_error(mx("{} is not a valid mask.", "maskErr").format(dest_mask))
            self._dest_network.setFocus()
            return None

        # Validate gateway address
        gateway = self._gateway.text()
        if not LmTools.is_ipv4(gateway):
            self._app.display_error(mx("{} is not a valid address.", "addrErr").format(gateway))
            self._gateway.setFocus()
            return None

        return {"Name": rule_name,
                "Dst": dest_network,
                "DstLen": dest_len,
                "Gateway": gateway,
                "Enable": self._enabled.isChecked(),
                "Priority": PRIORITY_BASE + self._priority.value()}


    ### Generate a random rule name following same logic as WebUI
    @staticmethod
    def generate_rule_name():
        # 10 random chars that can be uppercase/lowercase letters and digits
        return ''.join(random.choices(string.ascii_letters + string.digits, k=10))
