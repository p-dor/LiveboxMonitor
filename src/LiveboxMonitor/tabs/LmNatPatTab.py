### Livebox Monitor NAT/PAT tab module ###

import json

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmConfig, LmFwlTools
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmTableWidget import LmTableWidget, NumericSortItem, CenteredIconsDelegate
from LiveboxMonitor.dlg.LmPatRule import PatRuleDialog
from LiveboxMonitor.dlg.LmPtfRule import PtfRuleDialog
from LiveboxMonitor.dlg.LmFirewallRuleType import FirewallRuleTypeDialog
from LiveboxMonitor.lang.LmLanguages import get_nat_pat_label as lx, get_nat_pat_message as mx
from LiveboxMonitor.tools import LmTools

from LiveboxMonitor.__init__ import __build__


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = "natPatTab"

# List columns
class PatCol(IntEnum):
    Key = 0
    Enabled = 1
    RuleType = 2
    ID = 3
    Description = 4
    Protocols = 5
    ExtPort = 6
    IntPort = 7
    Device = 8
    DestIP = 9
    ExtIPs = 10
PAT_ICON_COLUMNS = [PatCol.Enabled]

class PtfCol(IntEnum):
    Key = 0
    Enabled = 1
    RuleType = 2
    ID = 3
    Description = 4
    Protocols = 5
    Device = 6
    DestIP = 7
    ExtIPs = 8
PTF_ICON_COLUMNS = [PtfCol.Enabled]



# ################################ LmNatPat class ################################
class LmNatPat:

    ### Create NAT/PAT tab
    def create_nat_pat_tab(self):
        self._nat_pat_tab = QtWidgets.QWidget(objectName=TAB_NAME)

        # PAT - port forwarding list
        self._pat_list = LmTableWidget(objectName="patList")
        self._pat_list.set_columns({PatCol.Key: ["Key", 0, None],
                                    PatCol.Enabled: [lx("A"), 10, "plist_Enabled"],
                                    PatCol.RuleType: [lx("Type"), 55, "plist_Type"],
                                    PatCol.ID: [lx("Name"), 120, "plist_ID"],
                                    PatCol.Description: [lx("Port Forwarding Rule Description"), 400, "plist_Description"],
                                    PatCol.Protocols: [lx("Protocols"), 70, "plist_Protocols"],
                                    PatCol.ExtPort: [lx("External Port"), 95, "plist_ExtPort"],
                                    PatCol.IntPort: [lx("Internal Port"), 95, "plist_IntPort"],
                                    PatCol.Device: [lx("Device"), 180, "plist_Device"],
                                    PatCol.DestIP: ["DestIP", 0, None],
                                    PatCol.ExtIPs: [lx("External IPs"), 250, "plist_ExtIPs"]})
        self._pat_list.set_header_resize([PatCol.Description])
        self._pat_list.set_standard_setup(self)
        self._pat_list.setItemDelegate(CenteredIconsDelegate(self, PAT_ICON_COLUMNS))
        self._pat_list.itemSelectionChanged.connect(self.pat_list_click)
        self._pat_list.doubleClicked.connect(self.edit_pat_rule_button_click)

        # PAT - port forwarding button bar
        pat_buttons_box = QtWidgets.QHBoxLayout()
        pat_buttons_box.setSpacing(30)
        refresh_pat_button = QtWidgets.QPushButton(lx("Refresh"), objectName="refreshPat")
        refresh_pat_button.clicked.connect(self.refresh_pat_button_click)
        pat_buttons_box.addWidget(refresh_pat_button)
        self._pat_enable_button = QtWidgets.QPushButton(lx("Enable"), objectName="enablePat")
        self._pat_enable_button.clicked.connect(self.enable_pat_button_click)
        pat_buttons_box.addWidget(self._pat_enable_button)
        add_rule_button = QtWidgets.QPushButton(lx("Add..."), objectName="addPat")
        add_rule_button.clicked.connect(self.add_pat_rule_button_click)
        pat_buttons_box.addWidget(add_rule_button)
        self._pat_edit_rule_button = QtWidgets.QPushButton(lx("Edit..."), objectName="editPat")
        self._pat_edit_rule_button.clicked.connect(self.edit_pat_rule_button_click)
        pat_buttons_box.addWidget(self._pat_edit_rule_button)
        self._pat_del_rule_button = QtWidgets.QPushButton(lx("Delete"), objectName="deletePat")
        self._pat_del_rule_button.clicked.connect(self.del_pat_rule_button_click)
        pat_buttons_box.addWidget(self._pat_del_rule_button)
        del_all_rules_button = QtWidgets.QPushButton(lx("Delete All..."), objectName="deleteAllPat")
        del_all_rules_button.clicked.connect(self.del_all_pat_rules_button_click)
        pat_buttons_box.addWidget(del_all_rules_button)
        export_pat_rules_button = QtWidgets.QPushButton(lx("Export..."), objectName="exportPat")
        export_pat_rules_button.clicked.connect(self.export_pat_rules_button_click)
        pat_buttons_box.addWidget(export_pat_rules_button)
        import_pat_rules_button = QtWidgets.QPushButton(lx("Import..."), objectName="importPat")
        import_pat_rules_button.clicked.connect(self.import_pat_rules_button_click)
        pat_buttons_box.addWidget(import_pat_rules_button)

        # PTF - Layer 3 protocol forwarding list
        self._ptf_list = LmTableWidget(objectName="ptfList")
        self._ptf_list.set_columns({PtfCol.Key: ["Key", 0, None],
                                    PtfCol.Enabled: [lx("A"), 10, "tlist_Enabled"],
                                    PtfCol.RuleType: [lx("Type"), 55, "tlist_Type"],
                                    PtfCol.ID: [lx("Name"), 120, "tlist_ID"],
                                    PtfCol.Description: [lx("Protocol Forwarding Rule Description"), 360, "tlist_Description"],
                                    PtfCol.Protocols: [lx("Protocols"), 180, "tlist_Protocols"],
                                    PtfCol.Device: [lx("Device"), 220, "tlist_Device"],
                                    PtfCol.DestIP: ["DestIP", 0, None],
                                    PtfCol.ExtIPs: [lx("External IPs"), 250, "tlist_ExtIPs"]})
        self._ptf_list.set_header_resize([PtfCol.Description])
        self._ptf_list.set_standard_setup(self)
        self._ptf_list.setItemDelegate(CenteredIconsDelegate(self, PTF_ICON_COLUMNS))
        self._ptf_list.itemSelectionChanged.connect(self.ptf_list_click)
        self._ptf_list.doubleClicked.connect(self.edit_ptf_rule_button_click)
        list_size = LmConfig.table_height(5)
        self._ptf_list.setMinimumHeight(list_size)
        self._ptf_list.setMaximumHeight(list_size)

        # PTF - Layer 3 protocol forwarding button bar
        ptf_buttons_box = QtWidgets.QHBoxLayout()
        ptf_buttons_box.setSpacing(30)
        refresh_ptf_button = QtWidgets.QPushButton(lx("Refresh"), objectName="refreshPtf")
        refresh_ptf_button.clicked.connect(self.refresh_ptf_button_click)
        ptf_buttons_box.addWidget(refresh_ptf_button)
        self._ptf_enable_button = QtWidgets.QPushButton(lx("Enable"), objectName="enablePtf")
        self._ptf_enable_button.clicked.connect(self.enable_ptf_button_click)
        ptf_buttons_box.addWidget(self._ptf_enable_button)
        add_rule_button = QtWidgets.QPushButton(lx("Add..."), objectName="addPtf")
        add_rule_button.clicked.connect(self.add_ptf_rule_button_click)
        ptf_buttons_box.addWidget(add_rule_button)
        self._ptf_edit_rule_button = QtWidgets.QPushButton(lx("Edit..."), objectName="editPtf")
        self._ptf_edit_rule_button.clicked.connect(self.edit_ptf_rule_button_click)
        ptf_buttons_box.addWidget(self._ptf_edit_rule_button)
        self._ptf_del_rule_button = QtWidgets.QPushButton(lx("Delete"), objectName="deletePtf")
        self._ptf_del_rule_button.clicked.connect(self.del_ptf_rule_button_click)
        ptf_buttons_box.addWidget(self._ptf_del_rule_button)
        del_all_rules_button = QtWidgets.QPushButton(lx("Delete All..."), objectName="deleteAllPtf")
        del_all_rules_button.clicked.connect(self.del_all_ptf_rules_button_click)
        ptf_buttons_box.addWidget(del_all_rules_button)
        export_ptf_rules_button = QtWidgets.QPushButton(lx("Export..."), objectName="exportPtf")
        export_ptf_rules_button.clicked.connect(self.export_ptf_rules_button_click)
        ptf_buttons_box.addWidget(export_ptf_rules_button)
        import_ptf_rules_button = QtWidgets.QPushButton(lx("Import..."), objectName="importPtf")
        import_ptf_rules_button.clicked.connect(self.import_ptf_rules_button_click)
        ptf_buttons_box.addWidget(import_ptf_rules_button)

        # Layout
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

        vbox = QtWidgets.QVBoxLayout()
        vbox.setSpacing(10)
        vbox.addWidget(self._pat_list, 1)
        vbox.addLayout(pat_buttons_box, 0)
        vbox.insertSpacing(-1, 3)
        vbox.addWidget(separator)
        vbox.insertSpacing(-1, 3)
        vbox.addWidget(self._ptf_list, 0)
        vbox.addLayout(ptf_buttons_box, 0)
        self._nat_pat_tab.setLayout(vbox)

        LmConfig.set_tooltips(self._nat_pat_tab, "natpat")
        self._tab_widget.addTab(self._nat_pat_tab, lx("NAT/PAT"))

        # Init context
        self.nat_pat_tab_init()


    ### Init NAT/PAT tab context
    def nat_pat_tab_init(self):
        self._nat_pat_data_loaded = False
        self._pat_list_refresh = False
        self._ptf_list_refresh = False


    ### Click on NAT/PAT tab
    def nat_pat_tab_click(self):
        if not self._nat_pat_data_loaded:
            self._nat_pat_data_loaded = True       # Must be first to avoid reentrency during tab drag&drop
            self.load_protocol_numbers()
            self.load_device_ip_name_map()
            self.load_pat_rules()
            self.load_ptf_rules()


    ### Click on PAT list item
    def pat_list_click(self):
        current_selection = self._pat_list.currentRow()
        if current_selection >= 0:
            self._pat_enable_button.setEnabled(True)
            self._pat_edit_rule_button.setEnabled(True)
            self._pat_del_rule_button.setEnabled(True)
            enable = self._pat_list.item(current_selection, PatCol.Enabled).data(QtCore.Qt.ItemDataRole.UserRole)
            self._pat_enable_button.setText(lx("Disable") if enable else lx("Enable"))
        else:
            self._pat_enable_button.setEnabled(False)
            self._pat_edit_rule_button.setEnabled(False)
            self._pat_del_rule_button.setEnabled(False)


    ### Click on refresh PAT rules button
    def refresh_pat_button_click(self):
        self.refresh_pat_list()


    ### Click on enable/disable PAT rule button
    def enable_pat_button_click(self):
        r = self.get_selected_pat_rule()
        if r:
            r["Enable"] = not r["Enable"]
            self._task.start(lx("Saving rule..."))
            try:
                if self.save_pat_rule(r):
                    self.commit_firewall_rule_change()
                    # Update directly in case the update event is missed
                    i = self._pat_list.currentRow()
                    self._pat_list.setItem(i, PatCol.Enabled, self.format_active_table_widget(r["Enable"]))
                    self.pat_list_click()
            finally:
                self._task.end()


    ### Click on add PAT rule button
    def add_pat_rule_button_click(self):
        dialog = PatRuleDialog(None, self)
        if dialog.exec():
            self._task.start(lx("Saving rule..."))
            try:
                r = dialog.get_rule()
                if self.save_pat_rule(r):
                    self.commit_firewall_rule_change()
                    # Update directly in case the add event is missed
                    self.pat_rule_list_add(r)
            finally:
                self._task.end()


    ### Click on edit PAT rule button
    def edit_pat_rule_button_click(self):
        rule = self.get_selected_pat_rule()
        if rule:
            dialog = PatRuleDialog(rule, self)
            if dialog.exec():
                self._task.start(lx("Saving rule..."))
                try:
                    new_rule = dialog.get_rule()

                    # Delete old rule if ID or type changed
                    # Need to be done first to avoid overlap error with new rule
                    if (rule["Name"] != new_rule["Name"]) or (rule["Type"] != new_rule["Type"]):
                        if self.del_pat_rule(rule):
                            self.pat_rule_list_delete(rule)

                    # Save rule
                    if self.save_pat_rule(new_rule):
                        # Update directly in case the add event is missed
                        self.pat_rule_list_update(new_rule)

                    self.commit_firewall_rule_change()
                finally:
                    self._task.end()


    ### Click on delete PAT rule rules button
    def del_pat_rule_button_click(self):
        r = self.get_selected_pat_rule()
        if r:
            self._task.start(lx("Deleting rule..."))
            try:
                if self.del_pat_rule(r):
                    self.commit_firewall_rule_change()
                    # Update directly in case the delete event is missed
                    self.pat_rule_list_delete(r)
            finally:
                self._task.end()


    ### Click on delete all PAT rules button
    def del_all_pat_rules_button_click(self):
        dialog = FirewallRuleTypeDialog(True, self)
        if dialog.exec():
            self._task.start(lx("Deleting rules..."))
            try:
                t = dialog.get_types()

                # Delete all IPv4 rules if selected
                if t[LmFwlTools.RULE_TYPE_IPv4]:
                    self.del_all_ipv4_pat_rule(False)

                # Delete all UPnP rules if selected
                if t[LmFwlTools.RULE_TYPE_UPnP]:
                    self.del_all_ipv4_pat_rule(True)

                # Delete one by one IPv6 rules if selected
                if t[LmFwlTools.RULE_TYPE_IPv6]:
                    for i in range(self._pat_list.rowCount()):
                        r = self.get_pat_rule_from_list(i)
                        if r and (r["Type"] == LmFwlTools.RULE_TYPE_IPv6):
                            self.del_pat_rule(r)

                # Commit & refresh
                self.commit_firewall_rule_change()
                self.refresh_pat_list()
            finally:
                self._task.end()

            self.display_status(mx("All selected rule(s) deleted.", "delAllPat"))


    ### Click on export PAT rules button
    def export_pat_rules_button_click(self):
        dialog = FirewallRuleTypeDialog(True, self)
        if dialog.exec():
            t = dialog.get_types()

            file_name = QtWidgets.QFileDialog.getSaveFileName(self, lx("Export File"), lx("Port Forwarding Rules") + ".txt", "*.txt")[0]
            if not file_name:
                return

            try:
                export_file = open(file_name, "w")
            except Exception as e:
                LmTools.error(str(e))
                self.display_error(mx("Cannot create the file.", "createFileErr"))
                return

            self._task.start(lx("Exporting port forwarding rules..."))
            try:
                c = 0
                rules = []
                for i in range(self._pat_list.rowCount()):
                    r = self.get_pat_rule_from_list(i)
                    if r and t[r["Type"]]:
                        rules.append(r)
                        c += 1

                file = {"Version": __build__,
                        "Type": "PAT",
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


    ### Click on import PAT rules button
    def import_pat_rules_button_click(self):
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

            if (file.get("Type", "") != "PAT") or (rules is None):
                self.display_error(mx("Wrong file type.", "fileTypeErr"))
                error = True

        if not error:
            self._task.start(lx("Importing port forwarding rules..."))
            try:
                c = 0
                for r in rules:
                    if self.check_pat_rule(r) and self.save_pat_rule(r):
                        c += 1
            finally:
                self._task.end()

        try:
            import_file.close()
        except Exception as e:
            LmTools.error(str(e))
            self.display_error(mx("Cannot close the file.", "closeFileErr"))

        if not error:
            self.commit_firewall_rule_change()
            self.refresh_pat_list()

            self.display_status(mx("{} rule(s) imported.", "ruleImport").format(c))


    ### Click on PTF list item
    def ptf_list_click(self):
        current_selection = self._ptf_list.currentRow()
        if current_selection >= 0:
            self._ptf_enable_button.setEnabled(True)
            self._ptf_edit_rule_button.setEnabled(True)
            self._ptf_del_rule_button.setEnabled(True)
            enable = self._ptf_list.item(current_selection, PtfCol.Enabled).data(QtCore.Qt.ItemDataRole.UserRole)
            self._ptf_enable_button.setText(lx("Disable") if enable else lx("Enable"))
        else:
            self._ptf_enable_button.setEnabled(False)
            self._ptf_edit_rule_button.setEnabled(False)
            self._ptf_del_rule_button.setEnabled(False)


    ### Click on refresh PTF rules button
    def refresh_ptf_button_click(self):
        self.refresh_ptf_list()


    ### Click on enable/disable PTF rule button
    def enable_ptf_button_click(self):
        r = self.get_selected_ptf_rule()
        if r:
            r["Enable"] = not r["Enable"]
            self._task.start(lx("Saving rule..."))
            try:
                if self.save_ptf_rule(r):
                    self.commit_firewall_rule_change()
                    # Update directly in case the update event is missed
                    i = self._ptf_list.currentRow()
                    self._ptf_list.setItem(i, PtfCol.Enabled, self.format_active_table_widget(r["Enable"]))
                    self.ptf_list_click()
            finally:
                self._task.end()


    ### Click on add PTF rule button
    def add_ptf_rule_button_click(self):
        dialog = PtfRuleDialog(None, self)
        if dialog.exec():
            self._task.start(lx("Saving rule..."))
            try:
                r = dialog.get_rule()
                if self.save_ptf_rule(r):
                    self.commit_firewall_rule_change()
                    # Update directly in case the add event is missed
                    self.ptf_rule_list_add(r)
            finally:
                self._task.end()


    ### Click on edit PTF rule button
    def edit_ptf_rule_button_click(self):
        rule = self.get_selected_ptf_rule()
        if rule:
            dialog = PtfRuleDialog(rule, self)
            if dialog.exec():
                self._task.start(lx("Saving rule..."))
                try:
                    new_rule = dialog.get_rule()

                    # Delete old rule if ID or type changed
                    # Need to be done first to avoid overlap error with new rule
                    if (rule["Name"] != new_rule["Name"]) or (rule["Type"] != new_rule["Type"]):
                        if self.del_ptf_rule(rule):
                            self.ptf_rule_list_delete(rule)

                    # Save rule
                    if self.save_ptf_rule(new_rule):
                        # Update directly in case the add event is missed
                        self.ptf_rule_list_update(new_rule)

                    self.commit_firewall_rule_change()
                finally:
                    self._task.end()


    ### Click on delete PTF rule rules button
    def del_ptf_rule_button_click(self):
        r = self.get_selected_ptf_rule()
        if r:
            self._task.start(lx("Deleting rule..."))
            try:
                if self.del_ptf_rule(r):
                    self.commit_firewall_rule_change()
                    # Update directly in case the delete event is missed
                    self.ptf_rule_list_delete(r)
            finally:
                self._task.end()


    ### Click on delete all PTF rules button
    def del_all_ptf_rules_button_click(self):
        dialog = FirewallRuleTypeDialog(False, self)
        if dialog.exec():
            self._task.start(lx("Deleting rules..."))
            try:
                t = dialog.get_types()

                # Delete one by one all selected rules
                c = 0
                for i in range(self._ptf_list.rowCount()):
                    r = self.get_ptf_rule_from_list(i)
                    if r and t[r["Type"]]:
                        self.del_ptf_rule(r)
                        c += 1

                # Commit & refresh
                self.commit_firewall_rule_change()
                self.refresh_ptf_list()
            finally:
                self._task.end()

            self.display_status(mx("{} rule(s) deleted.", "ruleDel").format(c))


    ### Click on export PTF rules button
    def export_ptf_rules_button_click(self):
        dialog = FirewallRuleTypeDialog(False, self)
        if dialog.exec():
            t = dialog.get_types()

            file_name = QtWidgets.QFileDialog.getSaveFileName(self, lx("Export File"), lx("Protocol Forwarding Rules") + ".txt", "*.txt")[0]
            if not file_name:
                return

            try:
                export_file = open(file_name, "w")
            except Exception as e:
                LmTools.error(str(e))
                self.display_error(mx("Cannot create the file.", "createFileErr"))
                return

            self._task.start(lx("Exporting protocol forwarding rules..."))
            try:
                c = 0
                rules = []
                for i in range(self._ptf_list.rowCount()):
                    r = self.get_ptf_rule_from_list(i)
                    if r and t[r["Type"]]:
                        rules.append(r)
                        c += 1

                file = {"Version": __build__,
                        "Type": "PTF",
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


    ### Click on import PTF rules button
    def import_ptf_rules_button_click(self):
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
            rules = file.get("Rules", None)

            if (file.get("Type", "") != "PTF") or (rules is None):
                self.display_error(mx("Wrong file type.", "fileTypeErr"))
                error = True

        if not error:
            self._task.start(lx("Importing protocol forwarding rules..."))
            try:
                c = 0
                for r in rules:
                    if self.check_ptf_rule(r) and self.save_ptf_rule(r):
                        c += 1
            finally:
                self._task.end()

        try:
            import_file.close()
        except Exception as e:
            LmTools.error(str(e))
            self.display_error(mx("Cannot close the file.", "closeFileErr"))

        if not error:
            self.commit_firewall_rule_change()
            self.refresh_ptf_list()

            self.display_status(mx("{} rule(s) imported.", "ruleImport").format(c))


    ### Refresh PAT list
    def refresh_pat_list(self):
        self._pat_list_refresh = True
        try:
            self._pat_list.clearContents()
            self._pat_list.setRowCount(0)
            self.load_device_ip_name_map()
            self.load_pat_rules()
        finally:
            self._pat_list_refresh = False


    ### Load PAT rules
    def load_pat_rules(self):
        self._task.start(lx("Loading port forwarding rules..."))
        try:
            self._pat_list.setSortingEnabled(False)

            # IPv4 types (webui / upnp / others?)
            self.load_ipv4_pat_rules()

            # IPv6 types
            self.load_ipv6_pat_rules()

            self._pat_list.sortItems(PatCol.RuleType, QtCore.Qt.SortOrder.AscendingOrder)
            self._pat_list.setSortingEnabled(True)

            self._pat_list.setCurrentCell(-1, -1)
            self.pat_list_click()
        finally:
            self._task.end()


    ### Load IPv4 (webui / upnp / others?) PAT rules
    def load_ipv4_pat_rules(self):
        try:
            d = self._api._firewall.get_ipv4_port_forwarding()
        except Exception as e:
            LmTools.error(str(e))
            self.display_error(mx("Cannot load IPv4 port forwarding rules.", "patLoadErr"))
            return

        i = self._pat_list.rowCount()
        for r in d.values():
            self._pat_list.insertRow(i)
            self.display_ipv4_pat_rule(i, r)
            i += 1


    ### Display a IPv4 PAT rule at the given list line
    def display_ipv4_pat_rule(self, line, rule):
        self.display_pat_rule_line(line, rule, "v4", LmFwlTools.RULE_TYPE_IPv4)


    ### Load IPv6 PAT rules
    def load_ipv6_pat_rules(self):
        try:
            d = self._api._firewall.get_ipv6_pinhole()
        except Exception as e:
            LmTools.error(str(e))
            LmTools.error("Cannot load IPv6 port forwarding rules.")    # Do not display a dialog as not all LB models have this API
            return

        i = self._pat_list.rowCount()
        for r in d.values():
            if not self.pinhole_is_pat_rule(r):
                continue
            self._pat_list.insertRow(i)
            self.display_ipv6_pat_rule(i, r)
            i += 1


    ### Display a IPv6 PAT rule at the given list line
    def display_ipv6_pat_rule(self, line, rule):
        self.display_pat_rule_line(line, rule, "v6", LmFwlTools.RULE_TYPE_IPv6)


    ### Display a PAT rule at the given list line
    def display_pat_rule_line(self, line, rule, prefix, type):
        active_status = rule.get("Enable", False)
        self._pat_list.setItem(line, PatCol.Enabled, self.format_active_table_widget(active_status))

        origin = rule.get("Origin", "")
        self._pat_list.setItem(line, PatCol.RuleType, self.format_origin_table_widget(origin, type == LmFwlTools.RULE_TYPE_IPv6))

        rule_id = rule.get("Id", "")
        self._pat_list.setItem(line, PatCol.Key, QtWidgets.QTableWidgetItem(f"{prefix}_{rule_id}"))

        if len(rule_id) > len(origin) + 1:
            rule_id = rule_id[len(origin) + 1:]
        self._pat_list.setItem(line, PatCol.ID, QtWidgets.QTableWidgetItem(rule_id))

        self._pat_list.setItem(line, PatCol.Description, QtWidgets.QTableWidgetItem(rule.get("Description", "")))

        protocols = rule.get("Protocol", "")
        self._pat_list.setItem(line, PatCol.Protocols, self.format_protocols_table_widget(protocols))

        if type == LmFwlTools.RULE_TYPE_IPv4:
            self._pat_list.setItem(line, PatCol.IntPort, self.format_port_table_widget(rule.get("InternalPort", "")))
            self._pat_list.setItem(line, PatCol.ExtPort, self.format_port_table_widget(rule.get("ExternalPort", "")))
        else:
            self._pat_list.setItem(line, PatCol.IntPort, self.format_port_table_widget(rule.get("DestinationPort", "")))
            self._pat_list.setItem(line, PatCol.ExtPort, self.format_port_table_widget(rule.get("SourcePort", "")))

        destination_ip = rule.get("DestinationIPAddress", "")
        self._pat_list.setItem(line, PatCol.DestIP, QtWidgets.QTableWidgetItem(destination_ip))
        self._pat_list.setItem(line, PatCol.Device, QtWidgets.QTableWidgetItem(self.get_device_name_from_ip(destination_ip)))

        external_ips = rule.get("SourcePrefix", "")
        if len(external_ips) == 0:
            external_ips = lx("All")
        self._pat_list.setItem(line, PatCol.ExtIPs, QtWidgets.QTableWidgetItem(external_ips))


    ### Display a PAT rule at the given list line. If line is <0 a new is created.
    def display_pat_rule(self, line, rule, ip_version):
        self._pat_list.setSortingEnabled(False)
        if line < 0:
            line = self._pat_list.rowCount()
            self._pat_list.insertRow(line)
        if ip_version == 4:
            self.display_ipv4_pat_rule(line, rule)
        else:
            self.display_ipv6_pat_rule(line, rule)
        self._pat_list.setSortingEnabled(True)
        self.pat_list_click()


    ### Get the PAT rule object selected in the list
    def get_selected_pat_rule(self):
        return self.get_pat_rule_from_list(self._pat_list.currentRow())


    ### Get a PAT rule object from list row index
    def get_pat_rule_from_list(self, index):
        if (index >= 0) and (index < self._pat_list.rowCount()):
            r = {}
            r["Enable"] = self._pat_list.item(index, PatCol.Enabled).data(QtCore.Qt.ItemDataRole.UserRole) != 0
            r["Type"] = self._pat_list.item(index, PatCol.RuleType).text()
            r["Name"] = self._pat_list.item(index, PatCol.ID).text()
            r["Desc"] = self._pat_list.item(index, PatCol.Description).text()
            p = self._pat_list.item(index, PatCol.Protocols).text()
            r["ProtoNames"] = p
            r["ProtoNumbers"] = self.translate_firewall_protocols(p)
            p = self._pat_list.item(index, PatCol.IntPort).text()
            r["IntPort"] = p if len(p) else None
            p = self._pat_list.item(index, PatCol.ExtPort).text()
            r["ExtPort"] = p if len(p) else None
            r["IP"] = self._pat_list.item(index, PatCol.DestIP).text()
            e = self._pat_list.item(index, PatCol.ExtIPs).text()
            r["ExtIPs"] = "" if e == lx("All") else e
            return r
        return None


    ### Convert a PAT rule from internal to Livebox model for display
    @staticmethod
    def convert_pat_rule_to_livebox(rule):
        r = {}
        origin = "upnp" if rule["Type"] == LmFwlTools.RULE_TYPE_UPnP else "webui"
        r["Id"] = f"{origin}_{rule['Name']}"
        r["Enable"] = rule["Enable"]
        r["Origin"] = origin
        r["Description"] = rule["Desc"]
        r["Protocol"] = rule["ProtoNumbers"]
        int_port = rule["IntPort"]
        ext_port = rule["ExtPort"]
        if rule["Type"] == LmFwlTools.RULE_TYPE_IPv6:
            if int_port is not None:
                r["DestinationPort"] = int_port
            if ext_port is not None:
                r["SourcePort"] = ext_port
        else:
            if int_port is not None:
                r["InternalPort"] = int_port
            if ext_port is not None:
                r["ExternalPort"] = ext_port
        r["DestinationIPAddress"] = rule["IP"]
        r["SourcePrefix"] = rule["ExtIPs"]
        return r


    ### Process a IPv4 PAT rule add event
    def process_ipv4_pat_rule_add_event(self, rule_id):
        # process as an update in case the rule has been added manually already
        self.process_ipv4_pat_rule_change_event(rule_id)


    ### Add a PAT rule in the list
    def pat_rule_list_add(self, rule):
        # process as an update in case the rule has been added by an event already
        self.pat_rule_list_update(rule)


    ### Process a IPv4 PAT rule change event
    def process_ipv4_pat_rule_change_event(self, rule_id):
        if self._nat_pat_data_loaded and not self._pat_list_refresh:
            ip_version = 4
            key, rule_id, origin = self.get_pat_rule_key(rule_id, ip_version)

            # Find the rule in the list
            # If not found line will be created by display_pat_rule()
            i = self.find_pat_rule_line(key)

            # Retrieve the rule data
            try:
                d = self._api._firewall.get_ipv4_port_forwarding(rule_id, origin)
            except Exception as e:
                LmTools.error(str(e))
                return

            r = next(iter(d.values()))  # Take the first rule
            self.display_pat_rule(i, r, ip_version)


    ### Update a PAT rule in the list
    def pat_rule_list_update(self, rule):
        # Determine the key
        origin = "upnp" if rule["Type"] == LmFwlTools.RULE_TYPE_UPnP else "webui"
        ip_version = 6 if rule["Type"] == LmFwlTools.RULE_TYPE_IPv6 else 4
        key, rule_id, origin = self.get_pat_rule_key(f"{origin}_{rule['Name']}", ip_version)

        # Find the rule in the list
        # If not found line will be created by display_pat_rule()
        i = self.find_pat_rule_line(key)

        # Update at the found line
        r = self.convert_pat_rule_to_livebox(rule)
        self.display_pat_rule(i, r, ip_version)


    ### Process a IPv4 PAT rule delete event
    def process_ipv4_pat_rule_delete_event(self, rule_id):
        if self._nat_pat_data_loaded and not self._pat_list_refresh:
            ip_version = 4
            key, rule_id, origin = self.get_pat_rule_key(rule_id, ip_version)

            # Find the rule in the list
            i = self.find_pat_rule_line(key)
            if i >= 0:
                self._pat_list.removeRow(i)


    ### Delete a PAT rule from the list
    def pat_rule_list_delete(self, rule):
        # Determine the key
        origin = "upnp" if rule["Type"] == LmFwlTools.RULE_TYPE_UPnP else "webui"
        ip_version = 6 if rule["Type"] == LmFwlTools.RULE_TYPE_IPv6 else 4
        key, rule_id, origin = self.get_pat_rule_key(f"{origin}_{rule['Name']}", ip_version)

        # Find the rule in the list
        i = self.find_pat_rule_line(key)
        if i >= 0:
            self._pat_list.removeRow(i)


    ### Process a Pinhole rule add event
    def process_pinhole_rule_add_event(self, rule_id):
        # process as an update in case the rule has been added manually already
        self.process_pinhole_rule_change_event(rule_id)


    ### Process a Pinhole rule change event
    def process_pinhole_rule_change_event(self, rule_id):
        if self._nat_pat_data_loaded:
            key, rule_id, origin = self.get_pinhole_rule_key(rule_id)

            # Retrieve the rule data
            try:
                d = self._api._firewall.get_ipv6_pinhole(rule_id, origin)
            except Exception as e:
                LmTools.error(str(e))
                return

            r = next(iter(d.values()))  # Take the first rule
            if self.pinhole_is_pat_rule(r):
                if not self._pat_list_refresh:
                    # Find the rule in the list
                    # If not found line will be created by display_pat_rule()
                    i = self.find_pat_rule_line(key)
                    self.display_pat_rule(i, r, 6)
            else:
                if not self._ptf_list_refresh:
                    # Find the rule in the list
                    # If not found line will be created by display_ptf_rule()
                    i = self.find_ptf_rule_line(key)
                    self.display_ptf_rule(i, r, 6)


    ### Process a Pinhole rule delete event
    def process_pinhole_rule_delete_event(self, rule_id):
        if self._nat_pat_data_loaded:
            key, rule_id, origin = self.get_pinhole_rule_key(rule_id)

            # Cannot retrieve the rule data as deleted
            # No other means than searching on the two lists...

            if not self._pat_list_refresh:
                i = self.find_pat_rule_line(key)
                if i >= 0:
                    self._pat_list.removeRow(i)
                    return

            if not self._ptf_list_refresh:
                i = self.find_ptf_rule_line(key)
                if i >= 0:
                    self._ptf_list.removeRow(i)
 

    ### Find PAT rule line from rule key, returns -1 if not found
    def find_pat_rule_line(self, rule_key):
        if not rule_key:
            return -1
        return next((i for i in range(self._pat_list.rowCount()) if self._pat_list.item(i, PatCol.Key).text() == rule_key), -1)


    ### Check a PAT rule object consistency
    def check_pat_rule(self, rule):
        if rule.get("Enable") is None:
            LmTools.error("Rule as no Enable tag.")
            return False

        t = rule.get("Type", "UNK")
        if t not in LmFwlTools.RULE_PAT_TYPES:
            LmTools.error(f"Rule has unknown {t} type.")
            return False

        if len(rule.get("Name", "")) == 0:
            LmTools.error("Rule has no Name.")
            return False

        protocols = rule.get("ProtoNumbers", "")
        if len(protocols) == 0:
            LmTools.error("Rule has no protocol.")
            return False

        for p in protocols.split(","):
            n = LmFwlTools.PROTOCOL_NAMES.get(p)
            if n is None:
                LmTools.error(f"Rule has wrong protocol {p} set.")
                return False
            n = int(p)
            if (n != LmFwlTools.Protocols.TCP) and (n != LmFwlTools.Protocols.UDP):
                LmTools.error(f"Rule has wrong protocol {p} set.")
                return False

        n = rule.get("IntPort", "")
        if n:
            if not LmTools.is_tcp_udp_port(n):
                LmTools.error(f"Rule has wrong internal port {n} set.")
                return False

        n = rule.get("ExtPort", "")
        if n:
            if not LmTools.is_tcp_udp_port(n):
                LmTools.error(f"Rule has wrong external port {n} set.")
                return False

        ip = rule.get("IP", "")
        if len(ip) == 0:
            return False
        if t == LmFwlTools.RULE_TYPE_IPv6:
            if not LmTools.is_ipv6(ip):
                LmTools.error(f"Rule has wrong IPv6 {ip} set.")
                return False
        else:
            if not LmTools.is_ipv4(ip):
                LmTools.error(f"Rule has wrong IPv4 {ip} set.")
                return False

        e = rule.get("ExtIPs", "")
        if len(e):
            ext_ips = e.split(",")
            for ip in ext_ips:
                if len(ip) == 0:
                    LmTools.error("Rule external IPs has an empty IP address.")
                    return False

                if t == LmFwlTools.RULE_TYPE_IPv6:
                    if not LmTools.is_ipv6(ip):
                        LmTools.error(f"Rule external IPs has a wrong IPv6 {ip} set.")
                        return False
                else:
                    if not LmTools.is_ipv4(ip):
                        LmTools.error(f"Rule external IPs has a wrong IPv4 {ip} set.")
                        return False

        return True


    ### Get the key, ID and origin of a PAT rule from its ID in origin_id format
    @staticmethod
    def get_pat_rule_key(rule_id, ip_version):
        prefix = "v4" if ip_version == 4 else "v6"
        origin, _, unique_id = rule_id.partition("_")
        return f"{prefix}_{rule_id}", unique_id, origin


    ### Get the key, ID and origin of a Pinhole rule from its ID in origin_id format
    @staticmethod
    def get_pinhole_rule_key(rule_id):
        origin, _, unique_id = rule_id.partition("_")
        return f"v6_{rule_id}", unique_id, origin


    ### Check if a Pinhole is a PAT or PTX rule
    @staticmethod
    def pinhole_is_pat_rule(pinhole):
        # If destination port is not set, this is a protocol forwarding rule
        return True if pinhole.get("DestinationPort") else False


    ### Save a PAT rule in Livebox, return True if successful
    def save_pat_rule(self, rule):
        if rule["Type"] == LmFwlTools.RULE_TYPE_IPv6:
            return self.save_ipv6_pat_rule(rule)
        return self.save_ipv4_pat_rule(rule)


    ### Save a IPv4 PAT rule in Livebox, return True if successful
    def save_ipv4_pat_rule(self, rule):
        # Map rule to Livebox model
        r = {}
        r["id"] = rule["Name"]
        r["internalPort"] = rule["IntPort"]
        p = rule["ExtPort"]
        if p is not None:
            r["externalPort"] = p
        r["destinationIPAddress"] = rule["IP"]
        r["enable"] = rule["Enable"]
        r["persistent"] = True
        r["protocol"] = rule["ProtoNumbers"]
        r["description"] = rule["Desc"]
        r["sourceInterface"] = "data"
        r["origin"] = "webui" if rule["Type"] == LmFwlTools.RULE_TYPE_IPv4 else "upnp"
        r["destinationMACAddress"] = ""
        external_ips = rule["ExtIPs"]
        if len(external_ips):
            r["sourcePrefix"] = external_ips

        # Call Livebox API
        try:
            self._api._firewall.set_ipv4_port_forwarding(r)
        except Exception as e:
            self.display_error(str(e))
            return False

        return True
 

    ### Save a IPv6 PAT rule in Livebox, return True if successful
    def save_ipv6_pat_rule(self, rule):
        # Map rule to Livebox model
        r = {}
        r["id"] = rule["Name"]
        r["origin"] = "webui"
        r["sourceInterface"] = "data"
        p = rule["ExtPort"]
        r["sourcePort"] = p if LmFwlTools.IPV6_SOURCE_PORT_WORKING and (p is not None) else ""
        r["destinationPort"] = rule["IntPort"]
        r["destinationIPAddress"] = rule["IP"]
        r["sourcePrefix"] = rule["ExtIPs"]
        r["protocol"] = rule["ProtoNumbers"]
        r["ipversion"] = 6
        r["enable"] = rule["Enable"]
        r["persistent"] = True
        r["description"] = rule["Desc"]
        r["destinationMACAddress"] = ""

        # Call Livebox API
        try:
            self._api._firewall.set_ipv6_pinhole(r)
        except Exception as e:
            self.display_error(str(e))
            return False

        return True


    ### Delete a PAT rule from Livebox, return True if successful
    def del_pat_rule(self, rule):
        if rule["Type"] == LmFwlTools.RULE_TYPE_IPv6:
            return self.del_ipv6_pat_rule(rule)
        return self.del_ipv4_pat_rule(rule)


    ### Delete a IPv4 PAT rule from Livebox, return True if successful
    def del_ipv4_pat_rule(self, rule):
        origin = "webui" if rule["Type"] == LmFwlTools.RULE_TYPE_IPv4 else "upnp"
        try:
            self._api._firewall.del_ipv4_port_forwarding(rule["Name"], rule["IP"], origin)
        except Exception as e:
            self.display_error(str(e))
            return False
        return True


    ### Delete a IPv6 PAT rule from Livebox, return True if successful
    def del_ipv6_pat_rule(self, rule):
        try:
            self._api._firewall.del_ipv6_pinhole(rule["Name"], "webui")
        except Exception as e:
            self.display_error(str(e))
            return False
        return True


    ### Delete all IPv4 or UPnP PAT rules from Livebox, return True if successful
    def del_all_ipv4_pat_rule(self, upnp):
        origin = "upnp" if upnp else "webui"
        try:
            self._api._firewall.del_all_ipv4_port_forwarding(origin)
        except Exception as e:
            self.display_error(str(e))
            return False
        return True


    ### Refresh PTF list
    def refresh_ptf_list(self):
        self._ptf_list_refresh = True
        try:
            self._ptf_list.clearContents()
            self._ptf_list.setRowCount(0)
            self.load_device_ip_name_map()
            self.load_ptf_rules()
        finally:
            self._ptf_list_refresh = False


    ### Load PTF rules
    def load_ptf_rules(self):
        self._task.start(lx("Loading protocol forwarding rules..."))
        try:
            self._ptf_list.setSortingEnabled(False)

            # IPv4 types
            self.load_ipv4_ptf_rules()

            # IPv6 types
            self.load_ipv6_ptf_rules()

            self._ptf_list.sortItems(PtfCol.RuleType, QtCore.Qt.SortOrder.AscendingOrder)
            self._ptf_list.setSortingEnabled(True)

            self._ptf_list.setCurrentCell(-1, -1)
            self.ptf_list_click()
        finally:
            self._task.end()


    ### Load IPv4 PTF rules
    def load_ipv4_ptf_rules(self):
        try:
            d = self._api._firewall.get_ipv4_protocol_forwarding()
        except Exception as e:
            LmTools.error(str(e))
            self.display_error(mx("Cannot load IPv4 protocol forwarding rules.", "ptfLoadErr"))
            return

        i = self._ptf_list.rowCount()
        for r in d.values():
            self._ptf_list.insertRow(i)
            self.display_ipv4_ptf_rule(i, r)
            i += 1


    ### Display a IPv4 PTF rule at the given list line
    def display_ipv4_ptf_rule(self, line, rule):
        self.display_ptf_rule_line(line, rule, "v4", LmFwlTools.RULE_TYPE_IPv4)


    ### Load IPv6 PTF rules
    def load_ipv6_ptf_rules(self):
        try:
            d = self._api._firewall.get_ipv6_pinhole()
        except Exception as e:
            LmTools.error(str(e))
            LmTools.error("Cannot load IPv6 protocol forwarding rules.")    # Do not display a dialog as not all LB models have this API
            return

        i = self._ptf_list.rowCount()
        for r in d.values():
            if self.pinhole_is_pat_rule(r):
                continue
            self._ptf_list.insertRow(i)
            self.display_ipv6_ptf_rule(i, r)
            i += 1


    ### Display a IPv6 PTF rule at the given list line
    def display_ipv6_ptf_rule(self, line, rule):
        self.display_ptf_rule_line(line, rule, "v6", LmFwlTools.RULE_TYPE_IPv6)


    ### Display a PTF rule at the given list line
    def display_ptf_rule_line(self, line, rule, prefix, type):
        active_status = rule.get("Status", "Disabled") == "Enabled"
        self._ptf_list.setItem(line, PtfCol.Enabled, self.format_active_table_widget(active_status))

        if type == LmFwlTools.RULE_TYPE_IPv4:
            origin = rule.get("SourceInterface", "")
            rule_type = LmFwlTools.RULE_TYPE_IPv4 if origin == "data" else origin
            self._ptf_list.setItem(line, PtfCol.RuleType, QtWidgets.QTableWidgetItem(rule_type))
        else:
            origin = rule.get("Origin", "")
            self._ptf_list.setItem(line, PtfCol.RuleType, self.format_origin_table_widget(origin, True))

        rule_id = rule.get("Id", "")
        self._ptf_list.setItem(line, PtfCol.Key, QtWidgets.QTableWidgetItem(f"{prefix}_{rule_id}"))

        if (type == LmFwlTools.RULE_TYPE_IPv6) and (len(rule_id) > len(origin) + 1):
            rule_id = rule_id[len(origin) + 1:]
        self._ptf_list.setItem(line, PtfCol.ID, QtWidgets.QTableWidgetItem(rule_id))

        self._ptf_list.setItem(line, PtfCol.Description, QtWidgets.QTableWidgetItem(rule.get("Description", "")))

        protocols = rule.get("Protocol", "")
        self._ptf_list.setItem(line, PtfCol.Protocols, self.format_protocols_table_widget(protocols))

        destination_ip = rule.get("DestinationIPAddress", "")
        self._ptf_list.setItem(line, PtfCol.DestIP, QtWidgets.QTableWidgetItem(destination_ip))
        self._ptf_list.setItem(line, PtfCol.Device, QtWidgets.QTableWidgetItem(self.get_device_name_from_ip(destination_ip)))

        external_ips = rule.get("SourcePrefix", "")
        if len(external_ips) == 0:
            external_ips = lx("All")
        self._ptf_list.setItem(line, PtfCol.ExtIPs, QtWidgets.QTableWidgetItem(external_ips))


    ### Display a PTF rule at the given list line. If line is <0 a new is created.
    def display_ptf_rule(self, line, rule, ip_version):
        self._ptf_list.setSortingEnabled(False)
        if line < 0:
            line = self._ptf_list.rowCount()
            self._ptf_list.insertRow(line)
        if ip_version == 4:
            self.display_ipv4_ptf_rule(line, rule)
        else:
            self.display_ipv6_ptf_rule(line, rule)
        self._ptf_list.setSortingEnabled(True)
        self.ptf_list_click()


    ### Get the PTF rule object selected in the list
    def get_selected_ptf_rule(self):
        return self.get_ptf_rule_from_list(self._ptf_list.currentRow())


    ### Get a PTF rule object from list row index
    def get_ptf_rule_from_list(self, index):
        if (index >= 0) and (index < self._ptf_list.rowCount()):
            r = {}
            r["Enable"] = self._ptf_list.item(index, PtfCol.Enabled).data(QtCore.Qt.ItemDataRole.UserRole) != 0
            r["Type"] = self._ptf_list.item(index, PtfCol.RuleType).text()
            r["Name"] = self._ptf_list.item(index, PtfCol.ID).text()
            r["Desc"] = self._ptf_list.item(index, PtfCol.Description).text()
            p = self._ptf_list.item(index, PtfCol.Protocols).text()
            r["ProtoNames"] = p
            r["ProtoNumbers"] = self.translate_firewall_protocols(p)
            r["IP"] = self._ptf_list.item(index, PtfCol.DestIP).text()
            e = self._ptf_list.item(index, PtfCol.ExtIPs).text()
            r["ExtIPs"] = "" if e == lx("All") else e
            return r
        return None
 

    ### Convert a PTF rule from internal to Livebox model for display
    @staticmethod
    def convert_ptf_rule_to_livebox(rule):
        r = {}
        if rule["Type"] == LmFwlTools.RULE_TYPE_IPv6:
            origin = "webui"
            r["Id"] = f"{origin}_{rule['Name']}"
            r["Origin"] = origin
        else:
            r["Id"] = rule["Name"]
            r["SourceInterface"] = "data"
        r["Status"] = "Enabled" if rule["Enable"] else "Disabled"
        r["Description"] = rule["Desc"]
        r["Protocol"] = rule["ProtoNumbers"]
        r["DestinationIPAddress"] = rule["IP"]
        external_ips = rule["ExtIPs"]
        if external_ips:
            r["SourcePrefix"] = external_ips
        return r


    ### Process a IPv4 PTF rule add event
    def process_ipv4_ptf_rule_add_event(self, rule_id):
        # process as an update in case the rule has been added manually already
        self.process_ipv4_ptf_rule_change_event(rule_id)


    ### Add a PTF rule in the list
    def ptf_rule_list_add(self, rule):
        # process as an update in case the rule has been added by an event already
        self.ptf_rule_list_update(rule)


    ### Process a IPv4 PTF rule change event
    def process_ipv4_ptf_rule_change_event(self, rule_id):
        if self._nat_pat_data_loaded and not self._ptf_list_refresh:
            ip_version = 4
            key, rule_id = self.get_ptf_rule_key(rule_id, ip_version)

            # Find the rule in the list
            # If not found line will be created by display_ptf_rule()
            i = self.find_ptf_rule_line(key)

            # Retrieve the rule data
            try:
                d = self._api._firewall.get_ipv4_protocol_forwarding(rule_id)
            except Exception as e:
                LmTools.error(str(e))
                return

            r = next(iter(d.values()))  # Take the first rule
            self.display_ptf_rule(i, r, ip_version)


    ### Update a PTF rule in the list
    def ptf_rule_list_update(self, rule):
        # Determine the key
        if rule["Type"] == LmFwlTools.RULE_TYPE_IPv4:
            ip_version = 4
            rule_id = rule["Name"]
        else:
            ip_version = 6
            rule_id = f"webui_{rule['Name']}"
        key, rule_id = self.get_ptf_rule_key(rule_id, ip_version)

        # Find the rule in the list
        # If not found line will be created by display_ptf_rule()
        i = self.find_ptf_rule_line(key)

        # Update at the found line
        r = self.convert_ptf_rule_to_livebox(rule)
        self.display_ptf_rule(i, r, ip_version)


    ### Process a IPv4 PTF rule delete event
    def process_ipv4_ptf_rule_delete_event(self, rule_id):
        if self._nat_pat_data_loaded and not self._ptf_list_refresh:
            ip_version = 4
            key, rule_id = self.get_ptf_rule_key(rule_id, ip_version)

            # Find the rule in the list
            i = self.find_ptf_rule_line(key)
            if i >= 0:
                self._ptf_list.removeRow(i)


    ### Delete a PTF rule from the list
    def ptf_rule_list_delete(self, rule):
        # Determine the key
        if rule["Type"] == LmFwlTools.RULE_TYPE_IPv4:
            ip_version = 4
            rule_id = rule["Name"]
        else:
            ip_version = 6
            rule_id = f"webui_{rule['Name']}"
        key, rule_id = self.get_ptf_rule_key(rule_id, ip_version)

        # Find the rule in the list
        i = self.find_ptf_rule_line(key)
        if i >= 0:
            self._ptf_list.removeRow(i)


    ### Find PTF rule line from rule key, returns -1 if not found
    def find_ptf_rule_line(self, rule_key):
        if not rule_key:
            return -1
        return next((i for i in range(self._ptf_list.rowCount()) if self._ptf_list.item(i, PtfCol.Key).text() == rule_key), -1)


    ### Check a PTF rule object consistency
    def check_ptf_rule(self, rule):
        if rule.get("Enable") is None:
            LmTools.error("Rule as no Enable tag.")
            return False

        t = rule.get("Type", "UNK")
        if t not in LmFwlTools.RULE_PTF_TYPES:
            LmTools.error(f"Rule has unknown {t} type.")
            return False

        if len(rule.get("Name", "")) == 0:
            LmTools.error("Rule has no Name.")
            return False

        protocols = rule.get("ProtoNumbers", "")
        if len(protocols) == 0:
            LmTools.error("Rule has no protocol.")
            return False

        for p in protocols.split(","):
            if LmFwlTools.PROTOCOL_NAMES.get(p) is None:
                LmTools.error(f"Rule has wrong protocol {p} set.")
                return False

        ip = rule.get("IP", "")
        if len(ip) == 0:
            return False
        if t == LmFwlTools.RULE_TYPE_IPv6:
            if not LmTools.is_ipv6_pfix(ip):
                LmTools.error(f"Rule has wrong IPv6 {ip} set.")
                return False
        else:
            if not LmTools.is_ipv4(ip):
                LmTools.error(f"Rule has wrong IPv4 {ip} set.")
                return False

        e = rule.get("ExtIPs", "")
        if len(e):
            ext_ips = e.split(",")
            for ip in ext_ips:
                if len(ip) == 0:
                    LmTools.error("Rule external IPs has an empty IP address.")
                    return False

                if t == LmFwlTools.RULE_TYPE_IPv6:
                    if not LmTools.is_ipv6(ip):
                        LmTools.error(f"Rule external IPs has a wrong IPv6 {ip} set.")
                        return False
                else:
                    if not LmTools.is_ipv4(ip):
                        LmTools.error(f"Rule external IPs has a wrong IPv4 {ip} set.")
                        return False

        return True


    ### Get the key and ID of a PTF rule from its ID in origin_id format
    @staticmethod
    def get_ptf_rule_key(rule_id, ip_version):
        if ip_version == 4:
            prefix = "v4"
            unique_id = rule_id
        else:
            prefix = "v6"
            origin, _, unique_id = rule_id.partition("_")
        return f"{prefix}_{rule_id}", unique_id


    ### Save a PTF rule in Livebox, return True if successful
    def save_ptf_rule(self, rule):
        if rule["Type"] == LmFwlTools.RULE_TYPE_IPv6:
            return self.save_ipv6_ptf_rule(rule)
        return self.save_ipv4_ptf_rule(rule)


    ### Save a IPv4 PTF rule in Livebox, return True if successful
    def save_ipv4_ptf_rule(self, rule):
        # Map rule to Livebox model
        r = {}
        r["id"] = rule["Name"]
        r["enable"] = rule["Enable"]
        r["destinationIPAddress"] = rule["IP"]
        r["protocol"] = rule["ProtoNumbers"]
        r["persistent"] = True
        r["description"] = rule["Desc"]
        external_ips = rule["ExtIPs"]
        if len(external_ips):
            r["sourcePrefix"] = external_ips

        # Call Livebox API
        try:
            self._api._firewall.set_ipv4_protocol_forwarding(r)
        except Exception as e:
            self.display_error(str(e))
            return False

        return True


    ### Save a IPv6 PTF rule in Livebox, return True if successful
    def save_ipv6_ptf_rule(self, rule):
        # Map rule to Livebox model
        r = {}
        r["id"] = rule["Name"]
        r["origin"] = "webui"
        r["sourceInterface"] = "data"
        r["sourcePort"] = ""
        r["destinationPort"] = ""
        r["destinationIPAddress"] = rule["IP"]
        r["sourcePrefix"] = rule["ExtIPs"]
        r["protocol"] = rule["ProtoNumbers"]
        r["ipversion"] = 6
        r["enable"] = rule["Enable"]
        r["persistent"] = True
        r["description"] = rule["Desc"]
        r["destinationMACAddress"] = ""

        # Call Livebox API
        try:
            self._api._firewall.set_ipv6_pinhole(r)
        except Exception as e:
            self.display_error(str(e))
            return False

        return True


    ### Delete a PTF rule from Livebox, return True if successful
    def del_ptf_rule(self, rule):
        if rule["Type"] == LmFwlTools.RULE_TYPE_IPv6:
            return self.del_ipv6_ptf_rule(rule)
        return self.del_ipv4_ptf_rule(rule)


    ### Delete a IPv4 PTF rule from Livebox, return True if successful
    def del_ipv4_ptf_rule(self, rule):
        # Call Livebox API
        try:
            self._api._firewall.del_ipv4_protocol_forwarding(rule["Name"])
        except Exception as e:
            self.display_error(str(e))
            return False
        return True


    ### Delete a IPv6 PTF rule from Livebox, return True if successful
    def del_ipv6_ptf_rule(self, rule):
        try:
            self._api._firewall.del_ipv6_pinhole(rule["Name"], "webui")
        except Exception as e:
            self.display_error(str(e))
            return False
        return True


    ### Format Origin cell
    @staticmethod
    def format_origin_table_widget(origin, ipv6):
        ###WARNING### : names must match those set by FirewallRuleTypeDialog.get_types() method
        match origin:
            case "webui":
                if ipv6:
                    return QtWidgets.QTableWidgetItem(LmFwlTools.RULE_TYPE_IPv6)
                return QtWidgets.QTableWidgetItem(LmFwlTools.RULE_TYPE_IPv4)
            case "upnp":
                return QtWidgets.QTableWidgetItem(LmFwlTools.RULE_TYPE_UPnP)
            case _:
                return QtWidgets.QTableWidgetItem(origin)
