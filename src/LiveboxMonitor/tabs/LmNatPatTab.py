### Livebox Monitor NAT/PAT tab module ###

import json

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig, LmPatPtf
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmTableWidget import LmTableWidget, NumericSortItem, CenteredIconsDelegate
from LiveboxMonitor.dlg.LmPatRule import PatRuleDialog
from LiveboxMonitor.dlg.LmPtfRule import PtfRuleDialog
from LiveboxMonitor.dlg.LmNatPatRuleType import NatPatRuleTypeDialog
from LiveboxMonitor.lang.LmLanguages import get_nat_pat_label as lx, get_nat_pat_message as mx

from LiveboxMonitor.__init__ import __build__


# ################################ VARS & DEFS ################################

# Tab name
TAB_NAME = "natPatTab"

# List columns
class PatCol(IntEnum):
    Key = 0
    Enabled = 1
    Type = 2
    ID = 3
    Description = 4
    Protocols = 5
    IntPort = 6
    ExtPort = 7
    Device = 8
    DestIP = 9
    ExtIPs = 10
PAT_ICON_COLUMNS = [PatCol.Enabled]

class PtfCol(IntEnum):
    Key = 0
    Enabled = 1
    Type = 2
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
                                    PatCol.Type: [lx("Type"), 55, "plist_Type"],
                                    PatCol.ID: [lx("Name"), 120, "plist_ID"],
                                    PatCol.Description: [lx("Port Forwarding Rule Description"), 400, "plist_Description"],
                                    PatCol.Protocols: [lx("Protocols"), 70, "plist_Protocols"],
                                    PatCol.IntPort: [lx("Internal Port"), 95, "plist_IntPort"],
                                    PatCol.ExtPort: [lx("External Port"), 95, "plist_ExtPort"],
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
                                    PtfCol.Type: [lx("Type"), 55, "tlist_Type"],
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
        self._protocol_numbers = {}


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
                    self.commit_nat_pat_rule_change()
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
                    self.commit_nat_pat_rule_change()
                    self.refresh_pat_list()
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

                    # Delete old rule if ID changed
                    if rule["Name"] != new_rule["Name"]:
                        self.del_pat_rule(rule)

                    # Then save new one
                    if self.save_pat_rule(new_rule):
                        self.commit_nat_pat_rule_change()
                    self.refresh_pat_list()
                finally:
                    self._task.end()


    ### Click on delete PAT rule rules button
    def del_pat_rule_button_click(self):
        r = self.get_selected_pat_rule()
        if r:
            self._task.start(lx("Deleting rule..."))
            try:
                if self.del_pat_rule(r):
                    self.commit_nat_pat_rule_change()
                    self.refresh_pat_list()
            finally:
                self._task.end()


    ### Click on delete all PAT rules button
    def del_all_pat_rules_button_click(self):
        dialog = NatPatRuleTypeDialog(True, self)
        if dialog.exec():
            self._task.start(lx("Deleting rules..."))
            try:
                t = dialog.get_types()

                # Delete all IPv4 rules if selected
                if t[LmPatPtf.RULE_TYPE_IPv4]:
                    self.del_all_ipv4_pat_rule(False)

                # Delete all UPnP rules if selected
                if t[LmPatPtf.RULE_TYPE_UPnP]:
                    self.del_all_ipv4_pat_rule(True)

                # Delete one by one IPv6 rules if selected
                if t[LmPatPtf.RULE_TYPE_IPv6]:
                    for i in range(self._pat_list.rowCount()):
                        r = self.get_pat_rule_from_list(i)
                        if r and (r["Type"] == LmPatPtf.RULE_TYPE_IPv6):
                            self.del_pat_rule(r)

                # Commit & refresh
                self.commit_nat_pat_rule_change()
                self.refresh_pat_list()
            finally:
                self._task.end()

            self.display_status(mx("All selected rule(s) deleted.", "delAllPat"))


    ### Click on export PAT rules button
    def export_pat_rules_button_click(self):
        dialog = NatPatRuleTypeDialog(True, self)
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
            self.commit_nat_pat_rule_change()
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
                    self.commit_nat_pat_rule_change()
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
                    self.commit_nat_pat_rule_change()
                    self.refresh_ptf_list()
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

                    # Delete old rule if ID changed
                    if rule["Name"] != new_rule["Name"]:
                        self.del_ptf_rule(rule)

                    # Then save new one
                    if self.save_ptf_rule(new_rule):
                        self.commit_nat_pat_rule_change()
                    self.refresh_ptf_list()
                finally:
                    self._task.end()


    ### Click on delete PTF rule rules button
    def del_ptf_rule_button_click(self):
        r = self.get_selected_ptf_rule()
        if r:
            self._task.start(lx("Deleting rule..."))
            try:
                if self.del_ptf_rule(r):
                    self.commit_nat_pat_rule_change()
                    self.refresh_ptf_list()
            finally:
                self._task.end()


    ### Click on delete all PTF rules button
    def del_all_ptf_rules_button_click(self):
        dialog = NatPatRuleTypeDialog(False, self)
        if dialog.exec():
            self._task.start(lx("Deleting rules..."))
            try:
                t = dialog.get_types()
                c = 0
                for i in range(self._ptf_list.rowCount()):
                    r = self.get_ptf_rule_from_list(i)
                    if r and t[r["Type"]]:
                        self.del_ptf_rule(r)
                        c += 1
                self.commit_nat_pat_rule_change()
                self.refresh_ptf_list()
            finally:
                self._task.end()

            self.display_status(mx("{} rule(s) deleted.", "ruleDel").format(c))


    ### Click on export PTF rules button
    def export_ptf_rules_button_click(self):
        dialog = NatPatRuleTypeDialog(False, self)
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
            self.commit_nat_pat_rule_change()
            self.refresh_ptf_list()

            self.display_status(mx("{} rule(s) imported.", "ruleImport").format(c))


    ### Load protocol name to number reverse map from number to name
    def load_protocol_numbers(self):
       # Build reverse map
        self._protocol_numbers = {v: k for k, v in LmPatPtf.PROTOCOL_NAMES.items()}


    ### Refresh PAT list
    def refresh_pat_list(self):
        self._pat_list.clearContents()
        self._pat_list.setRowCount(0)
        self.load_device_ip_name_map()
        self.load_pat_rules()


    ### Load PAT rules
    def load_pat_rules(self):
        self._task.start(lx("Loading port forwarding rules..."))
        try:
            self._pat_list.setSortingEnabled(False)

            # IPv4 types (webui / upnp / others?)
            self.load_ipv4_pat_rules()

            # IPv6 types
            self.load_ipv6_pat_rules()

            self._pat_list.sortItems(PatCol.Type, QtCore.Qt.SortOrder.AscendingOrder)
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
        for k in d:
            self._pat_list.insertRow(i)
            r = d[k]

            active_status = r.get("Enable", False)
            self._pat_list.setItem(i, PatCol.Enabled, self.format_active_table_widget(active_status))

            origin = r.get("Origin", "")
            self._pat_list.setItem(i, PatCol.Type, self.format_nat_pat_origin_table_widget(origin, False))

            rule_id = r.get("Id", "")
            self._pat_list.setItem(i, PatCol.Key, QtWidgets.QTableWidgetItem("v4_" + rule_id))

            if len(rule_id) > len(origin) + 1:
                rule_id = rule_id[len(origin) + 1:]
            self._pat_list.setItem(i, PatCol.ID, QtWidgets.QTableWidgetItem(rule_id))

            self._pat_list.setItem(i, PatCol.Description, QtWidgets.QTableWidgetItem(r.get("Description", "")))

            protocols = r.get("Protocol", "")
            self._pat_list.setItem(i, PatCol.Protocols, self.format_nat_pat_protocols_table_widget(protocols))

            self._pat_list.setItem(i, PatCol.IntPort, self.format_port_table_widget(r.get("InternalPort", "")))
            self._pat_list.setItem(i, PatCol.ExtPort, self.format_port_table_widget(r.get("ExternalPort", "")))

            destination_ip = r.get("DestinationIPAddress", "")
            self._pat_list.setItem(i, PatCol.DestIP, QtWidgets.QTableWidgetItem(destination_ip))
            self._pat_list.setItem(i, PatCol.Device, QtWidgets.QTableWidgetItem(self.get_device_name_from_ip(destination_ip)))

            external_ips = r.get("SourcePrefix", "")
            if len(external_ips) == 0:
                external_ips = lx("All")
            self._pat_list.setItem(i, PatCol.ExtIPs, QtWidgets.QTableWidgetItem(external_ips))

            i += 1


    ### Load IPv6 PAT rules
    def load_ipv6_pat_rules(self):
        try:
            d = self._api._firewall.get_ipv6_pinhole()
        except Exception as e:
            LmTools.error(str(e))
            LmTools.error("Cannot load IPv6 port forwarding rules.")    # Do not display a dialog as not all LB models have this API
            return

        i = self._pat_list.rowCount()
        for k in d:
            r = d[k]

            # If destination port is not set, this is a protocol forwarding rule -> skip
            destination_port = r.get("DestinationPort", "")
            if len(destination_port) == 0:
                continue

            self._pat_list.insertRow(i)

            active_status = r.get("Enable", False)
            self._pat_list.setItem(i, PatCol.Enabled, self.format_active_table_widget(active_status))

            origin = r.get("Origin", "")
            self._pat_list.setItem(i, PatCol.Type, self.format_nat_pat_origin_table_widget(origin, True))

            rule_id = r.get("Id", "")
            self._pat_list.setItem(i, PatCol.Key, QtWidgets.QTableWidgetItem("v6_" + rule_id))

            if len(rule_id) > len(origin) + 1:
                rule_id = rule_id[len(origin) + 1:]
            self._pat_list.setItem(i, PatCol.ID, QtWidgets.QTableWidgetItem(rule_id))

            self._pat_list.setItem(i, PatCol.Description, QtWidgets.QTableWidgetItem(r.get("Description", "")))

            protocols = r.get("Protocol", "")
            self._pat_list.setItem(i, PatCol.Protocols, self.format_nat_pat_protocols_table_widget(protocols))

            self._pat_list.setItem(i, PatCol.IntPort, self.format_port_table_widget(destination_port))
            self._pat_list.setItem(i, PatCol.ExtPort, self.format_port_table_widget(r.get("SourcePort", "")))

            destination_ip = r.get("DestinationIPAddress", "")
            self._pat_list.setItem(i, PatCol.DestIP, QtWidgets.QTableWidgetItem(destination_ip))
            self._pat_list.setItem(i, PatCol.Device, QtWidgets.QTableWidgetItem(self.get_device_name_from_ip(destination_ip)))

            external_ips = r.get("SourcePrefix", "")
            if len(external_ips) == 0:
                external_ips = lx("All")
            self._pat_list.setItem(i, PatCol.ExtIPs, QtWidgets.QTableWidgetItem(external_ips))

            i += 1


    ### Get the PAT rule object selected in the list
    def get_selected_pat_rule(self):
        return self.get_pat_rule_from_list(self._pat_list.currentRow())


    ### Get a PAT rule object from list row index
    def get_pat_rule_from_list(self, index):
        if (index >= 0) and (index < self._pat_list.rowCount()):
            r = {}
            r["Enable"] = self._pat_list.item(index, PatCol.Enabled).data(QtCore.Qt.ItemDataRole.UserRole) != 0
            r["Type"] = self._pat_list.item(index, PatCol.Type).text()
            r["Name"] = self._pat_list.item(index, PatCol.ID).text()
            r["Desc"] = self._pat_list.item(index, PatCol.Description).text()
            p = self._pat_list.item(index, PatCol.Protocols).text()
            r["ProtoNames"] = p
            r["ProtoNumbers"] = self.translate_nat_pat_protocols(p)
            p = self._pat_list.item(index, PatCol.IntPort).text()
            r["IntPort"] = p if len(p) else None
            p = self._pat_list.item(index, PatCol.ExtPort).text()
            r["ExtPort"] = p if len(p) else None
            r["IP"] = self._pat_list.item(index, PatCol.DestIP).text()
            e = self._pat_list.item(index, PatCol.ExtIPs).text()
            r["ExtIPs"] = "" if e == lx("All") else e
            return r
        return None


    ### Check a PAT rule object consistency
    def check_pat_rule(self, rule):
        if rule.get("Enable") is None:
            LmTools.error("Rule as no Enable tag.")
            return False

        t = rule.get("Type", "UNK")
        if t not in LmPatPtf.RULE_PAT_TYPES:
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
            n = LmPatPtf.PROTOCOL_NAMES.get(p)
            if n is None:
                LmTools.error(f"Rule has wrong protocol {p} set.")
                return False
            n = int(p)
            if (n != LmPatPtf.Protocols.TCP) and (n != LmPatPtf.Protocols.UDP):
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
        if t == LmPatPtf.RULE_TYPE_IPv6:
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

                if t == LmPatPtf.RULE_TYPE_IPv6:
                    if not LmTools.is_ipv6(ip):
                        LmTools.error(f"Rule external IPs has a wrong IPv6 {ip} set.")
                        return False
                else:
                    if not LmTools.is_ipv4(ip):
                        LmTools.error(f"Rule external IPs has a wrong IPv4 {ip} set.")
                        return False

        return True


    ### Save a PAT rule in Livebox, return True if successful
    def save_pat_rule(self, rule, silent=False):
        if rule["Type"] == LmPatPtf.RULE_TYPE_IPv6:
            return self.save_ipv6_pat_rule(rule, silent)
        return self.save_ipv4_pat_rule(rule, silent)


    ### Save a IPv4 PAT rule in Livebox, return True if successful
    def save_ipv4_pat_rule(self, rule, silent=False):
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
        r["origin"] = "webui" if rule["Type"] == LmPatPtf.RULE_TYPE_IPv4 else "upnp"
        r["destinationMACAddress"] = ""
        external_ips = rule["ExtIPs"]
        if len(external_ips):
            r["sourcePrefix"] = external_ips

        # Call Livebox API
        try:
            self._api._firewall.set_ipv4_port_forwarding(r)
        except Exception as e:
            self.display_error(str(e), silent)
            return False

        return True
 

    ### Save a IPv6 PAT rule in Livebox, return True if successful
    def save_ipv6_pat_rule(self, rule, silent=False):
        # Map rule to Livebox model
        r = {}
        r["id"] = rule["Name"]
        r["origin"] = "webui"
        r["sourceInterface"] = "data"
        p = rule["ExtPort"]
        r["sourcePort"] = p if LmPatPtf.IPV6_SOURCE_PORT_WORKING and (p is not None) else ""
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
            self.display_error(str(e), silent)
            return False

        return True


    ### Delete a PAT rule from Livebox, return True if successful
    def del_pat_rule(self, rule):
        if rule["Type"] == LmPatPtf.RULE_TYPE_IPv6:
            return self.del_ipv6_pat_rule(rule)
        return self.del_ipv4_pat_rule(rule)


    ### Delete a IPv4 PAT rule from Livebox, return True if successful
    def del_ipv4_pat_rule(self, rule):
        origin = "webui" if rule["Type"] == LmPatPtf.RULE_TYPE_IPv4 else "upnp"
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
        self._ptf_list.clearContents()
        self._ptf_list.setRowCount(0)
        self.load_device_ip_name_map()
        self.load_ptf_rules()


    ### Load PTF rules
    def load_ptf_rules(self):
        self._task.start(lx("Loading protocol forwarding rules..."))
        try:
            self._ptf_list.setSortingEnabled(False)

            # IPv4 types
            self.load_ipv4_ptf_rules()

            # IPv6 types
            self.load_ipv6_ptf_rules()

            self._ptf_list.sortItems(PtfCol.Type, QtCore.Qt.SortOrder.AscendingOrder)
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
        for k in d:
            self._ptf_list.insertRow(i)
            r = d[k]

            active_status = r.get("Status", "Disabled") == "Enabled"
            self._ptf_list.setItem(i, PtfCol.Enabled, self.format_active_table_widget(active_status))

            origin = r.get("SourceInterface", "")
            rule_type = LmPatPtf.RULE_TYPE_IPv4 if origin == "data" else origin
            self._ptf_list.setItem(i, PtfCol.Type, QtWidgets.QTableWidgetItem(rule_type))

            rule_id = r.get("Id", "")
            self._ptf_list.setItem(i, PtfCol.Key, QtWidgets.QTableWidgetItem(f"v4_{rule_id}"))
            self._ptf_list.setItem(i, PtfCol.ID, QtWidgets.QTableWidgetItem(rule_id))

            self._ptf_list.setItem(i, PtfCol.Description, QtWidgets.QTableWidgetItem(r.get("Description", "")))

            protocols = r.get("Protocol", "")
            self._ptf_list.setItem(i, PtfCol.Protocols, self.format_nat_pat_protocols_table_widget(protocols))

            destination_ip = r.get("DestinationIPAddress", "")
            self._ptf_list.setItem(i, PtfCol.DestIP, QtWidgets.QTableWidgetItem(destination_ip))
            self._ptf_list.setItem(i, PtfCol.Device, QtWidgets.QTableWidgetItem(self.get_device_name_from_ip(destination_ip)))

            external_ips = r.get("SourcePrefix", "")
            if len(external_ips) == 0:
                external_ips = lx("All")
            self._ptf_list.setItem(i, PtfCol.ExtIPs, QtWidgets.QTableWidgetItem(external_ips))

            i += 1


    ### Load IPv6 PTF rules
    def load_ipv6_ptf_rules(self):
        try:
            d = self._api._firewall.get_ipv6_pinhole()
        except Exception as e:
            LmTools.error(str(e))
            LmTools.error("Cannot load IPv6 protocol forwarding rules.")    # Do not display a dialog as not all LB models have this API
            return

        i = self._ptf_list.rowCount()
        for k in d:
            r = d[k]

            # If destination port is set, this is a port forwarding rule -> skip
            destination_port = r.get("DestinationPort", "")
            if len(destination_port):
                continue

            self._ptf_list.insertRow(i)

            active_status = r.get("Status", "Disabled") == "Enabled"
            self._ptf_list.setItem(i, PtfCol.Enabled, self.format_active_table_widget(active_status))

            origin = r.get("Origin", "")
            self._ptf_list.setItem(i, PtfCol.Type, self.format_nat_pat_origin_table_widget(origin, True))

            rule_id = r.get("Id", "")
            self._ptf_list.setItem(i, PtfCol.Key, QtWidgets.QTableWidgetItem("v6_" + rule_id))

            if len(rule_id) > len(origin) + 1:
                rule_id = rule_id[len(origin) + 1:]
            self._ptf_list.setItem(i, PtfCol.ID, QtWidgets.QTableWidgetItem(rule_id))

            self._ptf_list.setItem(i, PtfCol.Description, QtWidgets.QTableWidgetItem(r.get("Description", "")))

            protocols = r.get("Protocol", "")
            self._ptf_list.setItem(i, PtfCol.Protocols, self.format_nat_pat_protocols_table_widget(protocols))

            destination_ip = r.get("DestinationIPAddress", "")
            self._ptf_list.setItem(i, PtfCol.DestIP, QtWidgets.QTableWidgetItem(destination_ip))
            self._ptf_list.setItem(i, PtfCol.Device, QtWidgets.QTableWidgetItem(self.get_device_name_from_ip(destination_ip)))

            external_ips = r.get("SourcePrefix", "")
            if len(external_ips) == 0:
                external_ips = lx("All")
            self._ptf_list.setItem(i, PtfCol.ExtIPs, QtWidgets.QTableWidgetItem(external_ips))

            i += 1


    ### Get the PTF rule object selected in the list
    def get_selected_ptf_rule(self):
        return self.get_ptf_rule_from_list(self._ptf_list.currentRow())


    ### Get a PTF rule object from list row index
    def get_ptf_rule_from_list(self, index):
        if (index >= 0) and (index < self._ptf_list.rowCount()):
            r = {}
            r["Enable"] = self._ptf_list.item(index, PtfCol.Enabled).data(QtCore.Qt.ItemDataRole.UserRole) != 0
            r["Type"] = self._ptf_list.item(index, PtfCol.Type).text()
            r["Name"] = self._ptf_list.item(index, PtfCol.ID).text()
            r["Desc"] = self._ptf_list.item(index, PtfCol.Description).text()
            p = self._ptf_list.item(index, PtfCol.Protocols).text()
            r["ProtoNames"] = p
            r["ProtoNumbers"] = self.translate_nat_pat_protocols(p)
            r["IP"] = self._ptf_list.item(index, PtfCol.DestIP).text()
            e = self._ptf_list.item(index, PtfCol.ExtIPs).text()
            r["ExtIPs"] = "" if e == lx("All") else e
            return r
        return None


    ### Check a PTF rule object consistency
    def check_ptf_rule(self, rule):
        if rule.get("Enable") is None:
            LmTools.error("Rule as no Enable tag.")
            return False

        t = rule.get("Type", "UNK")
        if t not in LmPatPtf.RULE_PTF_TYPES:
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
            n = LmPatPtf.PROTOCOL_NAMES.get(p)
            if n is None:
                LmTools.error(f"Rule has wrong protocol {p} set.")
                return False
            n = int(p)
            if t == LmPatPtf.RULE_TYPE_IPv6:
                icmp = LmPatPtf.Protocols.ICMPv6
            else:
                icmp = LmPatPtf.Protocols.ICMP
            if ((n != LmPatPtf.Protocols.TCP) and
                (n != LmPatPtf.Protocols.UDP) and
                (n != LmPatPtf.Protocols.AH) and
                (n != LmPatPtf.Protocols.GRE) and
                (n != LmPatPtf.Protocols.ESP) and
                (n != icmp)):
                LmTools.error(f"Rule has wrong protocol {p} set.")
                return False

        ip = rule.get("IP", "")
        if len(ip) == 0:
            return False
        if t == LmPatPtf.RULE_TYPE_IPv6:
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

                if t == LmPatPtf.RULE_TYPE_IPv6:
                    if not LmTools.is_ipv6(ip):
                        LmTools.error(f"Rule external IPs has a wrong IPv6 {ip} set.")
                        return False
                else:
                    if not LmTools.is_ipv4(ip):
                        LmTools.error(f"Rule external IPs has a wrong IPv4 {ip} set.")
                        return False

        return True


    ### Save a PTF rule in Livebox, return True if successful
    def save_ptf_rule(self, rule, silent=False):
        if rule["Type"] == LmPatPtf.RULE_TYPE_IPv6:
            return self.save_ipv6_ptf_rule(rule, silent)
        return self.save_ipv4_ptf_rule(rule, silent)


    ### Save a IPv4 PTF rule in Livebox, return True if successful
    def save_ipv4_ptf_rule(self, rule, silent=False):
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
            self.display_error(str(e), silent)
            return False

        return True


    ### Save a IPv6 PTF rule in Livebox, return True if successful
    def save_ipv6_ptf_rule(self, rule, silent=False):
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
            self.display_error(str(e), silent)
            return False

        return True


    ### Delete a PTF rule from Livebox, return True if successful
    def del_ptf_rule(self, rule):
        if rule["Type"] == LmPatPtf.RULE_TYPE_IPv6:
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


    ### Commit Firewall rule changes, return True if successful
    def commit_nat_pat_rule_change(self):
        try:
            self._api._firewall.commit()
        except Exception as e:
            LmTools.error(str(e))
            return False
        return True


    ### Translate Protocols for Livebox API
    def translate_nat_pat_protocols(self, protocols):
        t = [self._protocol_numbers[p] for p in protocols.split("/") if p in self._protocol_numbers]
        return ",".join(t)


    ### Format Origin cell
    @staticmethod
    def format_nat_pat_origin_table_widget(origin, ipv6):
        ###WARNING### : names must match those set by NatPatRuleTypeDialog.get_types() method
        match origin:
            case "webui":
                if ipv6:
                    return QtWidgets.QTableWidgetItem(LmPatPtf.RULE_TYPE_IPv6)
                return QtWidgets.QTableWidgetItem(LmPatPtf.RULE_TYPE_IPv4)
            case "upnp":
                return QtWidgets.QTableWidgetItem(LmPatPtf.RULE_TYPE_UPnP)
            case _:
                return QtWidgets.QTableWidgetItem(origin)


    ### Format Protocols cell
    @staticmethod
    def format_nat_pat_protocols_table_widget(protocols):
        names = [LmPatPtf.PROTOCOL_NAMES.get(p, "UNK") for p in protocols.split(",")]
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
