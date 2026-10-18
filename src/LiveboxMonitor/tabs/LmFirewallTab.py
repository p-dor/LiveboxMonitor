### Livebox Monitor Firewall tab module ###

import json

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmConfig, LmFwlTools
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmTableWidget import LmTableWidget, NumericSortItem, CenteredIconsDelegate
from LiveboxMonitor.dlg.LmFirewallLevels import FirewallLevelsDialog
from LiveboxMonitor.dlg.LmPingResponse import PingResponseDialog
from LiveboxMonitor.dlg.LmFirewallRule import FirewallRuleDialog, ACTIONS
from LiveboxMonitor.dlg.LmFirewallRuleType import FirewallRuleTypeDialog
from LiveboxMonitor.lang.LmLanguages import get_firewall_label as lx, get_firewall_message as mx
from LiveboxMonitor.tools import LmTools

from LiveboxMonitor.__init__ import __build__


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = "firewallTab"

# Static Config
BUTTON_WIDTH = 150

# List columns
class FwlCol(IntEnum):
    Key = 0
    Enabled = 1
    RuleType = 2
    Direction = 3
    ID = 4
    Description = 5
    Protocols = 6
    SourceIP = 7
    SourcePort = 8
    DestIP = 9
    DestPort = 10
    Device = 11
    Action = 12
FWL_ICON_COLUMNS = [FwlCol.Enabled]



# ################################ LmFirewall class ################################
class LmFirewall:

    ### Create Firewall tab
    def create_firewall_tab(self):
        self._firewall_tab = QtWidgets.QWidget(objectName=TAB_NAME)

        # Setup layout
        setup_layout = QtWidgets.QHBoxLayout()
        setup_layout.setSpacing(20)
        setup_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        # Levels box
        ipv4_fwl_level_label = QtWidgets.QLabel(lx("IPv4 Level:"), objectName="ipV4LevelLabel")
        self._ipv4_fwl_level = QtWidgets.QLabel("", objectName="ipV4Level")
        ipv6_fwl_level_label = QtWidgets.QLabel(lx("IPv6 Level:"), objectName="ipV6LevelLabel")
        self._ipv6_fwl_level = QtWidgets.QLabel("", objectName="ipV6Level")
        change_levels_button = QtWidgets.QPushButton(lx("Change..."), objectName="changeLevels")
        change_levels_button.setFixedWidth(BUTTON_WIDTH)
        change_levels_button.clicked.connect(self.change_levels_button_click)

        levels_grid = QtWidgets.QGridLayout()
        levels_grid.setSpacing(10)
        levels_grid.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        levels_grid.setColumnMinimumWidth(1, 100)

        levels_grid.addWidget(ipv4_fwl_level_label, 0, 0)
        levels_grid.addWidget(self._ipv4_fwl_level, 0, 1)
        levels_grid.addWidget(ipv6_fwl_level_label, 1, 0)
        levels_grid.addWidget(self._ipv6_fwl_level, 1, 1)
        levels_grid.addWidget(change_levels_button, 0, 2, 2, 2, alignment=QtCore.Qt.AlignmentFlag.AlignRight)

        levels_group_box = QtWidgets.QGroupBox(lx("Firewall Levels"), objectName="levelGroup")
        levels_group_box.setLayout(levels_grid)
        levels_group_box.setFixedWidth(350)
        setup_layout.addWidget(levels_group_box, 0)

        # Ping response button
        ping_response_button = QtWidgets.QPushButton(lx("Ping Responses..."), objectName="pingResponse")
        ping_response_button.setFixedWidth(BUTTON_WIDTH)
        ping_response_button.clicked.connect(self.ping_response_button_click)
        setup_layout.addWidget(ping_response_button, 0)

        # Rule warning
        warning_label = QtWidgets.QLabel(mx("The rules below apply only if the firewall level is set to \"Custom\".", "warning"))
        setup_layout.addWidget(warning_label, 1, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)

        # Firewall rule list
        self._fwl_list = LmTableWidget(objectName="fwlList")
        self._fwl_list.set_columns({FwlCol.Key: ["Key", 0, None],
                                    FwlCol.Enabled: [lx("A"), 10, "flist_Enabled"],
                                    FwlCol.RuleType: [lx("Type"), 55, "flist_Type"],
                                    FwlCol.Direction: [lx("Direction"), 65, "flist_Direction"],
                                    FwlCol.ID: [lx("Name"), 120, "flist_ID"],
                                    FwlCol.Description: [lx("Description"), 150, "flist_Description"],
                                    FwlCol.Protocols: [lx("Protocols"), 70, "flist_Protocols"],
                                    FwlCol.SourceIP: [lx("Source IP"), 110, "flist_SourceIP"],
                                    FwlCol.SourcePort: [lx("Source Port"), 95, "flist_SourcePort"],
                                    FwlCol.DestIP: [lx("Dest IP"), 110, "flist_DestIP"],
                                    FwlCol.DestPort: [lx("Dest Port"), 95, "flist_DestPort"],
                                    FwlCol.Device: [lx("Device"), 180, "flist_Device"],
                                    FwlCol.Action: [lx("Action"), 60, "flist_Action"]})
        self._fwl_list.set_header_resize([FwlCol.Description])
        self._fwl_list.set_standard_setup(self)
        self._fwl_list.setItemDelegate(CenteredIconsDelegate(self, FWL_ICON_COLUMNS))
        self._fwl_list.itemSelectionChanged.connect(self.fwl_list_click)
        self._fwl_list.doubleClicked.connect(self.edit_fwl_rule_button_click)

        # Button bar
        fwl_buttons_box = QtWidgets.QHBoxLayout()
        fwl_buttons_box.setSpacing(30)
        refresh_fwl_button = QtWidgets.QPushButton(lx("Refresh"), objectName="refreshFwl")
        refresh_fwl_button.clicked.connect(self.refresh_fwl_button_click)
        fwl_buttons_box.addWidget(refresh_fwl_button)
        self._fwl_enable_button = QtWidgets.QPushButton(lx("Enable"), objectName="enableFwl")
        self._fwl_enable_button.clicked.connect(self.enable_fwl_button_click)
        fwl_buttons_box.addWidget(self._fwl_enable_button)
        add_rule_button = QtWidgets.QPushButton(lx("Add..."), objectName="addFwl")
        add_rule_button.clicked.connect(self.add_fwl_rule_button_click)
        fwl_buttons_box.addWidget(add_rule_button)
        self._fwl_edit_rule_button = QtWidgets.QPushButton(lx("Edit..."), objectName="editFwl")
        self._fwl_edit_rule_button.clicked.connect(self.edit_fwl_rule_button_click)
        fwl_buttons_box.addWidget(self._fwl_edit_rule_button)
        self._fwl_del_rule_button = QtWidgets.QPushButton(lx("Delete"), objectName="deleteFwl")
        self._fwl_del_rule_button.clicked.connect(self.del_fwl_rule_button_click)
        fwl_buttons_box.addWidget(self._fwl_del_rule_button)
        del_all_rules_button = QtWidgets.QPushButton(lx("Delete All..."), objectName="deleteAllFwl")
        del_all_rules_button.clicked.connect(self.del_all_fwl_rules_button_click)
        fwl_buttons_box.addWidget(del_all_rules_button)
        export_fwl_rules_button = QtWidgets.QPushButton(lx("Export..."), objectName="exportFwl")
        export_fwl_rules_button.clicked.connect(self.export_fwl_rules_button_click)
        fwl_buttons_box.addWidget(export_fwl_rules_button)
        import_fwl_rules_button = QtWidgets.QPushButton(lx("Import..."), objectName="importFwl")
        import_fwl_rules_button.clicked.connect(self.import_fwl_rules_button_click)
        fwl_buttons_box.addWidget(import_fwl_rules_button)

        # Layout
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

        vbox = QtWidgets.QVBoxLayout()
        vbox.setSpacing(12)
        vbox.addLayout(setup_layout, 0)
        vbox.insertSpacing(-1, 3)
        vbox.addWidget(separator)
        vbox.insertSpacing(-1, 3)
        vbox.addWidget(self._fwl_list, 0)
        vbox.addLayout(fwl_buttons_box, 0)
        self._firewall_tab.setLayout(vbox)

        LmConfig.set_tooltips(self._firewall_tab, "firewall")
        self._tab_widget.addTab(self._firewall_tab, lx("Firewall"))

        # Init context
        self.firewall_tab_init()


    ### Init firewall tab context
    def firewall_tab_init(self):
        self._firewall_data_loaded = False
        self._fwl_list_refresh = False


    ### Click on firewall tab
    def firewall_tab_click(self):
        if not self._firewall_data_loaded:
            self._firewall_data_loaded = True       # Must be first to avoid reentrency during tab drag&drop
            self.load_firewall_levels()
            self.load_protocol_numbers()
            self.load_device_ip_name_map()
            self.load_firewall_rules()


    ### Click on the change levels buttons
    def change_levels_button_click(self):
        try:
            firewall_ipv4_level = self._api._firewall.get_ipv4_firewall_level()
            firewall_ipv6_level = self._api._firewall.get_ipv6_firewall_level()
        except Exception as e:
            self.display_error(str(e))
            return

        firewall_level_dialog = FirewallLevelsDialog(firewall_ipv4_level, firewall_ipv6_level, self)
        if firewall_level_dialog.exec():
            self._task.start(lx("Setting Firewall Levels..."))
            try:
                # Set new IPv4 firewall level if changed
                new_firewall_ipv4_level = firewall_level_dialog.get_ipv4_level()
                if new_firewall_ipv4_level != firewall_ipv4_level:
                    try:
                        self._api._firewall.set_ipv4_firewall_level(new_firewall_ipv4_level)
                    except Exception as e:
                        self.display_error(str(e))
                    else:
                        # Update directly in case the update event is missed
                        self.process_firewall_v4_level_change(new_firewall_ipv4_level)

                # Set new IPv6 firewall level if changed
                new_firewall_ipv6_level = firewall_level_dialog.get_ipv6_level()
                if new_firewall_ipv6_level != firewall_ipv6_level:
                    try:
                        self._api._firewall.set_ipv6_firewall_level(new_firewall_ipv6_level)
                    except Exception as e:
                        self.display_error(str(e))
                    else:
                        # Update directly in case the update event is missed
                        self.process_firewall_v6_level_change(new_firewall_ipv6_level)
            finally:
                self._task.end()


    ### Click on Ping Response button
    def ping_response_button_click(self):
        # Get current ping reponses
        try:
            d = self._api._firewall.get_respond_to_ping()
        except Exception as e:
            self.display_error(str(e))
            return
        ipv4_ping = d.get("enableIPv4")
        ipv6_ping = d.get("enableIPv6")
        if (ipv4_ping is None) or (ipv6_ping is None):
            LmTools.error("Cannot get respond to ping setup")

        ping_response_dialog = PingResponseDialog(ipv4_ping, ipv6_ping, self)
        if ping_response_dialog.exec():
            # Set new ping responses level if changed
            new_ipv4_ping = ping_response_dialog.get_ipv4()
            new_ipv6_ping = ping_response_dialog.get_ipv6()
            if (new_ipv4_ping != ipv4_ping) or (new_ipv6_ping != ipv6_ping):
                self._task.start(lx("Set Ping Responses..."))
                try:
                    p = {"enableIPv4": new_ipv4_ping, "enableIPv6": new_ipv6_ping}
                    try:
                        self._api._firewall.set_respond_to_ping(p)
                    except Exception as e:
                        self.display_error(str(e))
                finally:
                    self._task.end()


    ### Click on firewall list item
    def fwl_list_click(self):
        current_selection = self._fwl_list.currentRow()
        if current_selection >= 0:
            self._fwl_enable_button.setEnabled(True)
            self._fwl_edit_rule_button.setEnabled(True)
            self._fwl_del_rule_button.setEnabled(True)
            enable = self._fwl_list.item(current_selection, FwlCol.Enabled).data(QtCore.Qt.ItemDataRole.UserRole)
            self._fwl_enable_button.setText(lx("Disable") if enable else lx("Enable"))
        else:
            self._fwl_enable_button.setEnabled(False)
            self._fwl_edit_rule_button.setEnabled(False)
            self._fwl_del_rule_button.setEnabled(False)


    ### Click on refresh firewall rules button
    def refresh_fwl_button_click(self):
        self.refresh_fwl_list()


    ### Click on enable/disable firewall rule button
    def enable_fwl_button_click(self):
        r = self.get_selected_fwl_rule()
        if r:
            r["Enable"] = not r["Enable"]
            self._task.start(lx("Saving rule..."))
            try:
                if self.save_firewall_rule(r):
                    self.commit_firewall_rule_change()
                    # Update directly in case the update event is missed
                    i = self._fwl_list.currentRow()
                    self._fwl_list.setItem(i, FwlCol.Enabled, self.format_active_table_widget(r["Enable"]))
                    self.fwl_list_click()
            finally:
                self._task.end()



    ### Click on add firewall rule button
    def add_fwl_rule_button_click(self):
        dialog = FirewallRuleDialog(None, self)
        if dialog.exec():
            self._task.start(lx("Saving rule..."))
            try:
                r = dialog.get_rule()
                if self.save_firewall_rule(r):
                    self.commit_firewall_rule_change()
                    # Update directly in case the add event is missed
                    self.firewall_rule_list_add(r)
            finally:
                self._task.end()


    ### Click on edit firewall rule button
    def edit_fwl_rule_button_click(self):
        rule = self.get_selected_fwl_rule()
        if rule:
            dialog = FirewallRuleDialog(rule, self)
            if dialog.exec():
                self._task.start(lx("Saving rule..."))
                try:
                    new_rule = dialog.get_rule()

                    # Save
                    if self.save_firewall_rule(new_rule):
                        # Update directly in case the add event is missed
                        self.firewall_rule_list_update(new_rule)

                        # Delete old rule if ID, type or direction changed
                        if ((rule["Name"] != new_rule["Name"]) or
                            (rule["Type"] != new_rule["Type"]) or
                            (rule["Outbound"] != new_rule["Outbound"])):
                            if self.del_firewall_rule(rule):
                                self.firewall_rule_list_delete(rule)

                        self.commit_firewall_rule_change()
                finally:
                    self._task.end()


    ### Click on delete firewall rule rules button
    def del_fwl_rule_button_click(self):
        r = self.get_selected_fwl_rule()
        if r:
            self._task.start(lx("Deleting rule..."))
            try:
                if self.del_firewall_rule(r):
                    self.commit_firewall_rule_change()
                    # Update directly in case the delete event is missed
                    self.firewall_rule_list_delete(r)
            finally:
                self._task.end()


    ### Click on delete all firewall rules button
    def del_all_fwl_rules_button_click(self):
        dialog = FirewallRuleTypeDialog(False, self)
        if dialog.exec():
            self._task.start(lx("Deleting rules..."))
            try:
                t = dialog.get_types()

                # Delete one by one all selected rules
                c = 0
                for i in range(self._fwl_list.rowCount()):
                    r = self.get_fwl_rule_from_list(i)
                    if r and t[r["Type"]]:
                        self.del_firewall_rule(r)
                        c += 1

                # Commit & refresh
                self.commit_firewall_rule_change()
                self.refresh_fwl_list()
            finally:
                self._task.end()

            self.display_status(mx("{} rule(s) deleted.", "delAllFwl").format(c))


    ### Click on export firewall rules button
    def export_fwl_rules_button_click(self):
        dialog = FirewallRuleTypeDialog(False, self)
        if dialog.exec():
            t = dialog.get_types()

            file_name = QtWidgets.QFileDialog.getSaveFileName(self, lx("Export File"), lx("Firewall Rules") + ".txt", "*.txt")[0]
            if not file_name:
                return

            try:
                export_file = open(file_name, "w")
            except Exception as e:
                LmTools.error(str(e))
                self.display_error(mx("Cannot create the file.", "createFileErr"))
                return

            self._task.start(lx("Exporting firewall rules..."))
            try:
                c = 0
                rules = []
                for i in range(self._fwl_list.rowCount()):
                    r = self.get_fwl_rule_from_list(i)
                    if r and t[r["Type"]]:
                        rules.append(r)
                        c += 1

                file = {"Version": __build__,
                        "Type": "FWL",
                        "Rules": rules}
                json.dump(file, export_file, indent=4)
            finally:
                self._task.end()

            try:
                export_file.close()
            except Exception as e:
                LmTools.error(str(e))
                self.display_error(mx("Cannot save the file.", "saveFileErr"))

            self.display_status(mx("{} rule(s) exported.", "ruleExport").format(c))


    ### Click on import firewall rules button
    def import_fwl_rules_button_click(self):
        file_name = QtWidgets.QFileDialog.getOpenFileName(self, lx("Select file to import"), "", "*.txt")[0]
        if not file_name:
            return

        try:
            import_file = open(file_name, "r")
        except Exception as e:
            LmTools.error(str(e))
            self.display_error(mx("Cannot open the file.", "openFileErr"))
            return

        error = False
        try:
            file = json.load(import_file)
        except Exception as e:
            LmTools.error(f"Error loading file: {e}")
            self.display_error(mx("Wrong file format.", "fileFormatErr"))
            error = True

        if not error:
            rules = file.get("Rules")

            if (file.get("Type", "") != "FWL") or (rules is None):
                self.display_error(mx("Wrong file type.", "fileTypeErr"))
                error = True

        if not error:
            self._task.start(lx("Importing firewall rules..."))
            self._fwl_list_refresh = True
            try:
                c = 0
                for r in rules:
                    if self.check_firewall_rule(r) and self.save_firewall_rule(r):
                        c += 1
            finally:
                self._task.end()
                self._fwl_list_refresh = False

        try:
            import_file.close()
        except Exception as e:
            LmTools.error(str(e))
            self.display_error(mx("Cannot close the file.", "closeFileErr"))

        if not error:
            self.commit_firewall_rule_change()
            self.refresh_fwl_list()

            self.display_status(mx("{} rule(s) imported.", "ruleImport").format(c))


    ### Load the firewall levels field
    def load_firewall_levels(self):
        try:
            firewall_ipv4_level = self._api._firewall.get_ipv4_firewall_level()
        except Exception as e:
            self.display_error(str(e))
            self._ipv4_fwl_level.setText(lx("Error"))
            self._ipv4_fwl_level.setStyleSheet("font-weight: bold; color: red;")
        else:
            self.process_firewall_v4_level_change(firewall_ipv4_level)

        try:
            firewall_ipv6_level = self._api._firewall.get_ipv6_firewall_level()
        except Exception as e:
            self.display_error(str(e))
            self._ipv6_fwl_level.setText(lx("Error"))
            self._ipv6_fwl_level.setStyleSheet("font-weight: bold; color: red;")
        else:
            self.process_firewall_v6_level_change(firewall_ipv6_level)


    ### Process a IPv4 firewall level change event
    def process_firewall_v4_level_change(self, level):
        if self._firewall_data_loaded:
            self._ipv4_fwl_level.setText(lx(level))
            self._ipv4_fwl_level.setStyleSheet("font-weight: bold; color: black;")


    ### Process a IPv6 firewall level change event
    def process_firewall_v6_level_change(self, level):
        if self._firewall_data_loaded:
            self._ipv6_fwl_level.setText(lx(level))
            self._ipv6_fwl_level.setStyleSheet("font-weight: bold; color: black;")


    ### Load protocol name to number reverse map from number to name
    def load_protocol_numbers(self):
        # Build reverse map
        if not self._protocol_numbers:
            self._protocol_numbers = {v: k for k, v in LmFwlTools.PROTOCOL_NAMES.items()}


    ### Refresh firewall list
    def refresh_fwl_list(self):
        self._fwl_list_refresh = True
        try:
            self._fwl_list.clearContents()
            self._fwl_list.setRowCount(0)
            self.load_device_ip_name_map()
            self.load_firewall_rules()
        finally:
            self._fwl_list_refresh = False


    ### Load firewall custom rules
    def load_firewall_rules(self):
        self._task.start(lx("Loading firewall rules..."))
        try:
            self._fwl_list.setSortingEnabled(False)

            # IPv4 outbound (there are NO custom IPv4 inbound rule)
            self.load_ipv4_outbound_fwl_rules()

            # IPv6 types
            self.load_ipv6_inbound_fwl_rules()
            self.load_ipv6_outbound_fwl_rules()

            self._fwl_list.sortItems(FwlCol.RuleType, QtCore.Qt.SortOrder.AscendingOrder)
            self._fwl_list.setSortingEnabled(True)

            self._fwl_list.setCurrentCell(-1, -1)
            self.fwl_list_click()
        finally:
            self._task.end()


    ### Load IPv4 custom outbound firewall rules
    def load_ipv4_outbound_fwl_rules(self):
        try:
            d = self._api._firewall.get_firewall_rules()
        except Exception as e:
            LmTools.error(str(e))
            self.display_error(mx("Cannot load IPv4 firewall rules.", "fwlv4LoadErr"))
            return

        i = self._fwl_list.rowCount()
        for r in d.values():
            self._fwl_list.insertRow(i)
            self.display_ipv4_outbound_fwl_rule(i, r)
            i += 1


    ### Display a IPv4 custom firewall rule at the given list line
    def display_ipv4_outbound_fwl_rule(self, line, rule):
        self.display_fwl_rule_line(line, rule, "v4o", LmFwlTools.RULE_TYPE_IPv4, True)


    ### Load IPv6 custom inbound firewall rules
    def load_ipv6_inbound_fwl_rules(self):
        try:
            d = self._api._firewall.get_firewall_rules(chain="Custom_V6In")
        except Exception as e:
            LmTools.error(str(e))
            self.display_error(mx("Cannot load IPv6 inbound firewall rules.", "fwlv6iLoadErr"))
            return

        i = self._fwl_list.rowCount()
        for r in d.values():
            self._fwl_list.insertRow(i)
            self.display_ipv6_inbound_fwl_rule(i, r)
            i += 1


    ### Display a IPv6 custom inbound firewall rule at the given list line
    def display_ipv6_inbound_fwl_rule(self, line, rule):
        self.display_fwl_rule_line(line, rule, "v6i", LmFwlTools.RULE_TYPE_IPv6, False)


    ### Load IPv6 custom outbound firewall rules
    def load_ipv6_outbound_fwl_rules(self):
        try:
            d = self._api._firewall.get_firewall_rules(chain="Custom_V6Out")
        except Exception as e:
            LmTools.error(str(e))
            self.display_error(mx("Cannot load IPv6 outbound firewall rules.", "fwlv6oLoadErr"))
            return

        i = self._fwl_list.rowCount()
        for r in d.values():
            self._fwl_list.insertRow(i)
            self.display_ipv6_outbound_fwl_rule(i, r)
            i += 1


    ### Display a IPv6 custom outbound firewall rule at the given list line
    def display_ipv6_outbound_fwl_rule(self, line, rule):
        self.display_fwl_rule_line(line, rule, "v6o", LmFwlTools.RULE_TYPE_IPv6, True)


    ### Display a firewall rule at the given list line
    def display_fwl_rule_line(self, line, rule, prefix, type, outbound):
        active_status = rule.get("Enable", False)
        self._fwl_list.setItem(line, FwlCol.Enabled, self.format_active_table_widget(active_status))

        self._fwl_list.setItem(line, FwlCol.RuleType, QtWidgets.QTableWidgetItem(type))
        self._fwl_list.setItem(line, FwlCol.Direction, self.format_direction_table_widget(outbound))

        rule_id = rule.get("Id", "")
        self._fwl_list.setItem(line, FwlCol.Key, QtWidgets.QTableWidgetItem(f"{prefix}_{rule_id}"))
        self._fwl_list.setItem(line, FwlCol.ID, QtWidgets.QTableWidgetItem(rule_id))

        self._fwl_list.setItem(line, FwlCol.Description, QtWidgets.QTableWidgetItem(rule.get("Description", "")))

        protocols = rule.get("Protocol", "")
        self._fwl_list.setItem(line, FwlCol.Protocols, self.format_protocols_table_widget(protocols))

        source_ip = rule.get("SourcePrefix", "")
        self._fwl_list.setItem(line, FwlCol.SourceIP, QtWidgets.QTableWidgetItem(source_ip))
        self._fwl_list.setItem(line, FwlCol.SourcePort, self.format_port_table_widget(rule.get("SourcePort", "")))

        destination_ip = rule.get("DestinationPrefix", "")
        self._fwl_list.setItem(line, FwlCol.DestIP, QtWidgets.QTableWidgetItem(destination_ip))
        self._fwl_list.setItem(line, FwlCol.DestPort, self.format_port_table_widget(rule.get("DestinationPort", "")))

        device_ip = source_ip if outbound else destination_ip
        self._fwl_list.setItem(line, FwlCol.Device, QtWidgets.QTableWidgetItem(self.get_device_name_from_ip(device_ip)))

        self._fwl_list.setItem(line, FwlCol.Action, self.format_action_table_widget(rule.get("Target", "")))


    ### Display a firewall rule at the given list line. If line is <0 a new is created.
    def display_fwl_rule(self, line, rule, ip_version, outbound):
        self._fwl_list.setSortingEnabled(False)
        if line < 0:
            line = self._fwl_list.rowCount()
            self._fwl_list.insertRow(line)
        if ip_version == 4:
            self.display_ipv4_outbound_fwl_rule(line, rule)
        elif outbound:
            self.display_ipv6_outbound_fwl_rule(line, rule)
        else:
            self.display_ipv6_inbound_fwl_rule(line, rule)
        self._fwl_list.setSortingEnabled(True)
        self.fwl_list_click()


    ### Get the firewall rule object selected in the list
    def get_selected_fwl_rule(self):
        return self.get_fwl_rule_from_list(self._fwl_list.currentRow())


    ### Get a firewall rule object from list row index
    def get_fwl_rule_from_list(self, index):
        if (index >= 0) and (index < self._fwl_list.rowCount()):
            r = {}
            r["Enable"] = self._fwl_list.item(index, FwlCol.Enabled).data(QtCore.Qt.ItemDataRole.UserRole) != 0
            r["Type"] = self._fwl_list.item(index, FwlCol.RuleType).text()
            r["Outbound"] = self._fwl_list.item(index, FwlCol.Direction).data(QtCore.Qt.ItemDataRole.UserRole) != 0
            r["Name"] = self._fwl_list.item(index, FwlCol.ID).text()
            r["Desc"] = self._fwl_list.item(index, FwlCol.Description).text()
            p = self._fwl_list.item(index, FwlCol.Protocols).text()
            r["ProtoNames"] = p
            r["ProtoNumbers"] = self.translate_firewall_protocols(p)
            r["SourceIP"] = self._fwl_list.item(index, FwlCol.SourceIP).text()
            r["SourcePort"] = self._fwl_list.item(index, FwlCol.SourcePort).text()
            r["DestIP"] = self._fwl_list.item(index, FwlCol.DestIP).text()
            r["DestPort"] = self._fwl_list.item(index, FwlCol.DestPort).text()
            r["Action"] = self._fwl_list.item(index, FwlCol.Action).data(QtCore.Qt.ItemDataRole.UserRole)
            return r
        return None


    ### Convert a fireware rule from internal to Livebox model for display
    @staticmethod
    def convert_fwl_rule_to_livebox(rule):
        r = {}
        r["Id"] = rule["Name"]
        r["Enable"] = rule["Enable"]
        r["Description"] = rule["Desc"]
        r["Protocol"] = rule["ProtoNumbers"]
        r["Target"] = rule["Action"]
        r["DestinationPort"] = rule["DestPort"]
        r["DestinationPrefix"] = rule["DestIP"]
        r["SourcePort"] = rule["SourcePort"]
        r["SourcePrefix"] = rule["SourceIP"]
        return r


    ### Process a firewall custom rule add event
    def process_firewall_rule_add_event(self, rule_id, chain):
        # process as an update in case the rule has been added manually already
        self.process_firewall_rule_change_event(rule_id, chain)


    ### Add a rule in the list
    def firewall_rule_list_add(self, rule):
        # process as an update in case the rule has been added by an event already
        self.firewall_rule_list_update(rule)


    ### Process a firewall custom rule change event
    def process_firewall_rule_change_event(self, rule_id, chain):
        if self._firewall_data_loaded and not self._fwl_list_refresh:
            key, ip_version, outbound = self.get_firewall_rule_key(rule_id, chain)

            # Find the rule in the list
            # If not found line will be created by display_fwl_rule()
            i = self.find_firewall_rule_line(key)

            # Retrieve the rule data
            try:
                d = self._api._firewall.get_firewall_rules(rule_id, chain)
            except Exception as e:
                LmTools.error(str(e))
                return

            r = next(iter(d.values()))  # Take the first rule
            self.display_fwl_rule(i, r, ip_version, outbound)


    ### Update a rule in the list
    def firewall_rule_list_update(self, rule):
        # Determine the key
        chain = self.get_firewall_rule_chain(rule)
        key, ip_version, outbound = self.get_firewall_rule_key(rule["Name"], chain)

        # Find the rule in the list
        # If not found line will be created by display_fwl_rule()
        i = self.find_firewall_rule_line(key)

        # Update at the found line
        r = self.convert_fwl_rule_to_livebox(rule)
        self.display_fwl_rule(i, r, ip_version, outbound)


    ### Process a firewall custom rule delete event
    def process_firewall_rule_delete_event(self, rule_id, chain):
        if self._firewall_data_loaded and not self._fwl_list_refresh:
            key, ip_version, outbound = self.get_firewall_rule_key(rule_id, chain)

            # Find the rule in the list
            i = self.find_firewall_rule_line(key)
            if i >= 0:
                self._fwl_list.removeRow(i)


    ### Delete a rule from the list
    def firewall_rule_list_delete(self, rule):
        # Determine the key
        chain = self.get_firewall_rule_chain(rule)
        key, ip_version, outbound = self.get_firewall_rule_key(rule["Name"], chain)

        # Find the rule in the list
        i = self.find_firewall_rule_line(key)
        if i >= 0:
            self._fwl_list.removeRow(i)


    ### Find firewall rule line from rule key, returns -1 if not found
    def find_firewall_rule_line(self, rule_key):
        if not rule_key:
            return -1
        return next((i for i in range(self._fwl_list.rowCount()) if self._fwl_list.item(i, FwlCol.Key).text() == rule_key), -1)


    ### Check a firewall rule object consistency
    def check_firewall_rule(self, rule):
        if rule.get("Enable") is None:
            LmTools.error("Rule as no Enable tag.")
            return False

        t = rule.get("Type", "UNK")
        if t not in LmFwlTools.RULE_FWL_TYPES:
            LmTools.error(f"Rule has unknown {t} type.")
            return False

        o = rule.get("Outbound")
        if type(o) is not bool:
            LmTools.error(f"Rule has wrong or no outbound field: {o}.")
            return False

        if not rule.get("Name"):
            LmTools.error("Rule has no name.")
            return False

        protocols = rule.get("ProtoNumbers")
        if not protocols:
            LmTools.error("Rule has no protocol.")
            return False

        for p in protocols.split(","):
            if LmFwlTools.PROTOCOL_NAMES.get(p) is None:
                LmTools.error(f"Rule has wrong protocol {p} set.")
                return False

        ip = rule.get("SourceIP")
        if ip:
            if t == LmFwlTools.RULE_TYPE_IPv6:
                if not LmTools.is_ipv6_pfix(ip):
                    LmTools.error(f"Rule has wrong source IPv6 {ip} set.")
                    return False
            else:
                if not LmTools.is_ipv4_pfix(ip):
                    LmTools.error(f"Rule has wrong source IPv4 {ip} set.")
                    return False

        n = rule.get("SourcePort")
        if n:
            if not LmTools.is_tcp_udp_port(n, True):
                LmTools.error(f"Rule has wrong source port {n} set.")
                return False

        ip = rule.get("DestIP")
        if ip:
            if t == LmFwlTools.RULE_TYPE_IPv6:
                if not LmTools.is_ipv6_pfix(ip):
                    LmTools.error(f"Rule has wrong destination IPv6 {ip} set.")
                    return False
            else:
                if not LmTools.is_ipv4_pfix(ip):
                    LmTools.error(f"Rule has wrong destination IPv4 {ip} set.")
                    return False

        n = rule.get("DestPort")
        if n:
            if not LmTools.is_tcp_udp_port(n, True):
                LmTools.error(f"Rule has wrong destination port {n} set.")
                return False

        a = rule.get("Action", "UNK")
        if a not in ACTIONS:
            LmTools.error(f"Rule has unknown {a} action.")
            return False

        return True


    ### Get the Livebox firewall chain corresponding to a rule
    @staticmethod
    def get_firewall_rule_chain(rule):
        if rule["Type"] == LmFwlTools.RULE_TYPE_IPv4:
            return "Custom"
        return "Custom_V6Out" if rule["Outbound"] else "Custom_V6In"


    ### Get the key, ip version and direction assigned to a rule according to its chain
    @staticmethod
    def get_firewall_rule_key(rule_id, chain):
        match chain:
            case "Custom":
                prefix = "v4o"
                ip_version = 4
                outbound = True
            case "Custom_V6In":
                prefix = "v6i"
                ip_version = 6
                outbound = False
            case "Custom_V6Out":
                prefix = "v6o"
                ip_version = 6
                outbound = True
            case _:
                prefix = "err"
                ip_version = 4
                outbound = True
        return f"{prefix}_{rule_id}", ip_version, outbound


    ### Save a firewall rule in Livebox, return True if successful
    def save_firewall_rule(self, rule):
        # Map rule to Livebox model
        r = {}
        r["id"] = rule["Name"]
        r["enable"] = rule["Enable"]
        r["description"] = rule["Desc"]
        r["protocol"] = rule["ProtoNumbers"]
        r["action"] = rule["Action"]
        r["destinationPort"] = rule["DestPort"]
        r["destinationPrefix"] = rule["DestIP"]
        r["sourcePort"] = rule["SourcePort"]
        r["sourcePrefix"] = rule["SourceIP"]
        r["persistent"] = True
        r["ipversion"] = 4 if rule["Type"] == LmFwlTools.RULE_TYPE_IPv4 else 6
        r["chain"] = self.get_firewall_rule_chain(rule)

        # Call Livebox API
        try:
            self._api._firewall.set_firewall_rule(r)
        except Exception as e:
            self.display_error(str(e))
            return False

        return True
 

    ### Delete a firewall rule from Livebox, return True if successful
    def del_firewall_rule(self, rule):
        try:
            self._api._firewall.del_firewall_rule(rule["Name"], self.get_firewall_rule_chain(rule))
        except Exception as e:
            self.display_error(str(e))
            return False
        return True


    ### Commit Firewall rule changes, return True if successful
    def commit_firewall_rule_change(self):
        try:
            self._api._firewall.commit()
        except Exception as e:
            LmTools.error(str(e))
            return False
        return True


    ### Translate Protocols for Livebox API
    def translate_firewall_protocols(self, protocols):
        t = [self._protocol_numbers[p] for p in protocols.split("/") if p in self._protocol_numbers]
        return ",".join(t)


    ### Format Protocols cell
    @staticmethod
    def format_protocols_table_widget(protocols):
        names = [LmFwlTools.PROTOCOL_NAMES.get(p, "UNK") for p in protocols.split(",")]
        return QtWidgets.QTableWidgetItem("/".join(names))


    ### Format Port cell
    @staticmethod
    def format_port_table_widget(port):
        port_item = NumericSortItem(port)
        p = port.split("-")[0]     # If range is used, sort with the first port
        try:
            i = int(p)
        except ValueError:
            i = 0
        port_item.setData(QtCore.Qt.ItemDataRole.UserRole, i)
        return port_item


    ### Format Direction cell
    @staticmethod
    def format_direction_table_widget(outbound):
        if outbound:
            direction_item = NumericSortItem(lx("Outbound"))
            direction_item.setData(QtCore.Qt.ItemDataRole.UserRole, 1)
        else:
            direction_item = NumericSortItem(lx("Inbound"))
            direction_item.setData(QtCore.Qt.ItemDataRole.UserRole, 0)
        return direction_item


    ### Format Action cell
    @staticmethod
    def format_action_table_widget(action):
        action_item = QtWidgets.QTableWidgetItem(lx(action))
        action_item.setData(QtCore.Qt.ItemDataRole.UserRole, action)
        return action_item
