### Livebox Monitor Notification rules setup dialog ###

import os

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig, LmNotif
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.app.LmIcons import LmIcon
from LiveboxMonitor.app.LmTableWidget import LmTableWidget, CenteredIconHeaderView, CenteredIconsDelegate
from LiveboxMonitor.lang.LmLanguages import get_notification_rules_label as lx, get_events_message as mx


# ################################ VARS & DEFS ################################

# Rule list columns
class RuleCol(IntEnum):
    Key = 0
    Add = 1
    Delete = 2
    Active = 3
    Inactive = 4
    Link = 5
    File = 6
    Email = 7
ICON_COLUMNS = [RuleCol.Add, RuleCol.Delete, RuleCol.Active, RuleCol.Inactive, RuleCol.Link, RuleCol.File, RuleCol.Email]


# ################################ Notification rules setup dialog ################################
class NotificationSetupDialog(QtWidgets.QDialog):
    device_combo_separator_index = 2

    ### Constructor
    def __init__(self, parent=None):
        super(NotificationSetupDialog, self).__init__(parent)
        self.resize(720, 400)

        self._rule_selection = -1
        self._ignore_signal = False
        self._init = True

        # Rule box
        rule_layout = QtWidgets.QHBoxLayout()
        rule_layout.setSpacing(30)

        rule_list_layout = QtWidgets.QVBoxLayout()
        rule_list_layout.setSpacing(5)

        # Device list columns
        self._rule_list = LmTableWidget(objectName='ruleList')
        self._rule_list.setHorizontalHeader(CenteredIconHeaderView(self, ICON_COLUMNS))
        self._rule_list.set_columns({RuleCol.Key: [lx('Device'), 390, 'rlist_Key'],
                                     RuleCol.Add: [lx('Added'), 10, 'rlist_Add'],
                                     RuleCol.Delete: [lx('Deleted'), 10, 'rlist_Delete'],
                                     RuleCol.Active: [lx('Connected'), 10, 'rlist_Active'],
                                     RuleCol.Inactive: [lx('Disconnected'), 10, 'rlist_Inactive'],
                                     RuleCol.Link: [lx('Link Changed'), 10, 'rlist_Link'],
                                     RuleCol.File: [lx('File'), 10, 'rlist_File'],
                                     RuleCol.Email: [lx('Email'), 10, 'rlist_Email']})
        self._rule_list.set_header_resize([RuleCol.Key])
        self._rule_list.set_standard_setup(parent)

        # Assign icon headers - drawn by CenteredIconHeaderView
        model = self._rule_list.horizontalHeader().model()
        model.setHeaderData(RuleCol.Add, QtCore.Qt.Orientation.Horizontal, QtGui.QIcon(LmIcon.AddCirclePixmap), LmTools.ItemDataRole.IconRole)
        model.setHeaderData(RuleCol.Delete, QtCore.Qt.Orientation.Horizontal, QtGui.QIcon(LmIcon.DelCirclePixmap), LmTools.ItemDataRole.IconRole)
        model.setHeaderData(RuleCol.Active, QtCore.Qt.Orientation.Horizontal, QtGui.QIcon(LmIcon.ActiveCirclePixmap), LmTools.ItemDataRole.IconRole)
        model.setHeaderData(RuleCol.Inactive, QtCore.Qt.Orientation.Horizontal, QtGui.QIcon(LmIcon.InactiveCirclePixmap), LmTools.ItemDataRole.IconRole)
        model.setHeaderData(RuleCol.Link, QtCore.Qt.Orientation.Horizontal, QtGui.QIcon(LmIcon.LocChangePixmap), LmTools.ItemDataRole.IconRole)
        model.setHeaderData(RuleCol.File, QtCore.Qt.Orientation.Horizontal, QtGui.QIcon(LmIcon.ExcelDocPixmap), LmTools.ItemDataRole.IconRole)
        model.setHeaderData(RuleCol.Email, QtCore.Qt.Orientation.Horizontal, QtGui.QIcon(LmIcon.MailSendPixmap), LmTools.ItemDataRole.IconRole)

        self._rule_list.setItemDelegate(CenteredIconsDelegate(self, ICON_COLUMNS))
        self._rule_list.setMinimumWidth(460)
        self._rule_list.itemSelectionChanged.connect(self.rule_list_click)

        rule_list_layout.addWidget(self._rule_list, 1)

        rule_button_box = QtWidgets.QHBoxLayout()
        rule_button_box.setSpacing(5)

        add_rule_button = QtWidgets.QPushButton(lx('Add'), objectName='addRule')
        add_rule_button.clicked.connect(self.add_rule_button_click)
        rule_button_box.addWidget(add_rule_button)
        self._del_rule_button = QtWidgets.QPushButton(lx('Delete'), objectName='delRule')
        self._del_rule_button.clicked.connect(self.del_rule_button_click)
        rule_button_box.addWidget(self._del_rule_button)
        rule_list_layout.addLayout(rule_button_box, 0)
        rule_layout.addLayout(rule_list_layout, 0)

        device_label = QtWidgets.QLabel(lx('Device'), objectName='deviceLabel')
        self._device_combo = QtWidgets.QComboBox(objectName='deviceCombo')
        self.load_device_list()
        self._device_combo.addItem(lx('Any device'))
        self._device_combo.addItem(lx('Any unknown device'))
        self._device_combo.insertSeparator(NotificationSetupDialog.device_combo_separator_index)
        for d in self._combo_device_list:
            self._device_combo.addItem(d['Name'])
        self._device_combo.currentIndexChanged.connect(self.device_selected)

        mac_label = QtWidgets.QLabel(lx('MAC address'), objectName='macLabel')
        self._mac_edit = QtWidgets.QLineEdit(objectName='macEdit')
        mac_reg_exp = QtCore.QRegularExpression('^' + LmTools.MAC_RS + '$')
        mac_validator = QtGui.QRegularExpressionValidator(mac_reg_exp)
        self._mac_edit.setValidator(mac_validator)
        self._mac_edit.textChanged.connect(self.mac_typed)

        events_label = QtWidgets.QLabel(lx('Events:'), objectName='eventsLabel')
        self._add_event = QtWidgets.QCheckBox(lx('Device Added'), objectName='addEvent')
        self._add_event.stateChanged.connect(self.add_event_changed)
        self._del_event = QtWidgets.QCheckBox(lx('Device Deleted'), objectName='delEvent')
        self._del_event.stateChanged.connect(self.del_event_changed)
        self._act_event = QtWidgets.QCheckBox(lx('Device Connected'), objectName='actEvent')
        self._act_event.stateChanged.connect(self.act_event_changed)
        self._ina_event = QtWidgets.QCheckBox(lx('Device Disconnected'), objectName='inaEvent')
        self._ina_event.stateChanged.connect(self.ina_event_changed)
        self._lnk_event = QtWidgets.QCheckBox(lx('Device Access Link Changed'), objectName='lnkEvent')
        self._lnk_event.stateChanged.connect(self.lnk_event_changed)

        actions_label = QtWidgets.QLabel(lx('Actions:'), objectName='actionsLabel')
        self._file_action = QtWidgets.QCheckBox(lx('Log in CSV file'), objectName='fileAction')
        self._file_action.stateChanged.connect(self.file_action_changed)
        self._email_action = QtWidgets.QCheckBox(lx('Send Email'), objectName='emailAction')
        self._email_action.stateChanged.connect(self.email_action_changed)

        rule_edit_grid = QtWidgets.QGridLayout()
        rule_edit_grid.setSpacing(10)
        rule_edit_grid.addWidget(device_label, 0, 0)
        rule_edit_grid.addWidget(self._device_combo, 0, 1, 1, 2)
        rule_edit_grid.addWidget(mac_label, 1, 0)
        rule_edit_grid.addWidget(self._mac_edit, 1, 1, 1, 2)
        rule_edit_grid.addWidget(events_label, 2, 0)
        rule_edit_grid.addWidget(self._add_event, 2, 1)
        rule_edit_grid.addWidget(self._del_event, 2, 2)
        rule_edit_grid.addWidget(self._act_event, 3, 1)
        rule_edit_grid.addWidget(self._ina_event, 3, 2)
        rule_edit_grid.addWidget(self._lnk_event, 4, 1, 1, 2)
        rule_edit_grid.addWidget(actions_label, 5, 0)
        rule_edit_grid.addWidget(self._file_action, 5, 1, 1, 2)
        rule_edit_grid.addWidget(self._email_action, 6, 1, 1, 2)

        rule_layout.addLayout(rule_edit_grid, 0)

        rule_group_box = QtWidgets.QGroupBox(lx('Rules'), objectName='ruleGroup')
        rule_group_box.setLayout(rule_layout)

        # General preferences box
        int_validator = QtGui.QIntValidator()
        int_validator.setRange(1, 99)

        flush_frequency_label = QtWidgets.QLabel(lx('Event Resolution Frequency'), objectName='flushFrequencyLabel')
        self._flush_frequency = QtWidgets.QLineEdit(objectName='flushFrequencyEdit')
        self._flush_frequency.setValidator(int_validator)
        self._flush_frequency.setMaximumWidth(60)
        flush_frequency_sec_label = QtWidgets.QLabel(lx('seconds'), objectName='flushFrequencySecLabel')

        event_file_path_label = QtWidgets.QLabel(lx('CSV Files Path'), objectName='eventFilePathLabel')
        self._event_file_path = QtWidgets.QLineEdit(objectName='eventFilePathEdit')
        self._event_file_path.textChanged.connect(self.event_file_path_typed)
        self._event_file_path_select_button = QtWidgets.QPushButton(lx('Select'), objectName='eventFilePathSelectButton')
        self._event_file_path_select_button.clicked.connect(self.event_file_path_select_button_clic)
        self._default_file_path = QtWidgets.QCheckBox(lx('Default'), objectName='defaultFilePath')
        self._default_file_path.stateChanged.connect(self.default_file_path_changed)

        prefs_edit_grid = QtWidgets.QGridLayout()
        prefs_edit_grid.setSpacing(10)

        prefs_edit_grid.addWidget(flush_frequency_label, 0, 0)
        prefs_edit_grid.addWidget(self._flush_frequency, 0, 1, 1, 1)
        prefs_edit_grid.addWidget(flush_frequency_sec_label, 0, 2)
        prefs_edit_grid.addWidget(event_file_path_label, 1, 0)
        prefs_edit_grid.addWidget(self._event_file_path, 1, 1, 1, 5)
        prefs_edit_grid.addWidget(self._event_file_path_select_button, 1, 7)
        prefs_edit_grid.addWidget(self._default_file_path, 1, 8)

        prefs_group_box = QtWidgets.QGroupBox(lx('Preferences'), objectName='prefsGroup')
        prefs_group_box.setLayout(prefs_edit_grid)

        # Button bar
        button_bar = QtWidgets.QHBoxLayout()
        self._ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
        self._ok_button.clicked.connect(self.ok_button_click)
        self._ok_button.setDefault(True)
        button_bar.addWidget(self._ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        cancel_button = QtWidgets.QPushButton(lx('Cancel'), objectName='cancel')
        cancel_button.clicked.connect(self.reject)
        button_bar.addWidget(cancel_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        button_bar.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        button_bar.setSpacing(10)

        # Final layout
        vbox = QtWidgets.QVBoxLayout(self)
        vbox.setSpacing(20)
        vbox.addWidget(rule_group_box, 1)
        vbox.addWidget(prefs_group_box, 0)
        vbox.addLayout(button_bar, 0)

        self._flush_frequency.setFocus()

        LmConfig.set_tooltips(self, 'evnrules')

        self.setWindowTitle(lx('Notification Rules Setup'))
        self.setModal(True)
        self.load_prefs()
        self.show()

        self._init = False


    ### Load preferences data
    def load_prefs(self):
        self._rules = []

        # Load rule list
        if LmConf.NotificationRules:
            for i, r in enumerate(LmConf.NotificationRules):
                self._rules.append(r.copy())
                self._rule_list.insertRow(i)
                self.set_rule_row(i, r)
        self.rule_list_click()

        # Load paramaters
        self._flush_frequency.setText(str(int(LmConf.NotificationFlushFrequency)))
        if LmConf.NotificationFilePath is None:
            self._default_file_path.setChecked(True)
            self._event_file_path.setText(LmConf.get_config_directory())
            self._event_file_path.setDisabled(True)
            self._event_file_path_select_button.setDisabled(True)
        else:
            self._default_file_path.setChecked(False)
            self._event_file_path.setText(LmConf.NotificationFilePath)


    ### Set a row rule to a rule item
    def set_rule_row(self, row, rule):
        # Set rule device name
        rule_name = self.lookup_rule_name(rule['Key'])
        self._rule_list.setItem(row, RuleCol.Key, QtWidgets.QTableWidgetItem(rule_name))

        # Set event flags
        event_flags = [(LmNotif.TYPE_ADD, RuleCol.Add),
                       (LmNotif.TYPE_DELETE, RuleCol.Delete),
                       (LmNotif.TYPE_ACTIVE, RuleCol.Active),
                       (LmNotif.TYPE_INACTIVE, RuleCol.Inactive),
                       (LmNotif.TYPE_LINK_CHANGE, RuleCol.Link)]
        self.set_item_flags(row, rule['Events'], event_flags, LmIcon.BlueLightPixmap)


        # Set rule action flags
        rule_flags = [(LmNotif.RULE_FILE, RuleCol.File),
                      (LmNotif.RULE_EMAIL, RuleCol.Email)]
        self.set_item_flags(row, rule['Rules'], rule_flags, LmIcon.GreenLightPixmap)


    ### Look rule name from device key
    def lookup_rule_name(self, device_key):
        if device_key == LmNotif.DEVICE_ALL:
            return lx('Any device')
        elif device_key == LmNotif.DEVICE_UNKNOWN:
            return lx('Any unknown device')
        for device in self._combo_device_list:
            if device['MAC'] == device_key:
                return device['Name']
        return device_key


    ### Set table icons for each flag if present in active_types
    def set_item_flags(self, row, active_types, flag_defs, icon_pixmap):
        for flag_type, col in flag_defs:
            item = QtWidgets.QTableWidgetItem()
            if flag_type in active_types:
                item.setIcon(QtGui.QIcon(icon_pixmap))
                item.setData(QtCore.Qt.ItemDataRole.UserRole, True)
            self._rule_list.setItem(row, col, item)


    ### Save preferences data
    def save_prefs(self):
        # Save rule data
        if len(self._rules):
            LmConf.NotificationRules = self._rules
        else:
            LmConf.NotificationRules = None

        # Save parameters
        LmConf.NotificationFlushFrequency = int(self._flush_frequency.text())
        if self._default_file_path.isChecked():
            LmConf.NotificationFilePath = None
        else:
            LmConf.NotificationFilePath = self._event_file_path.text()


    ### Click on rule list item
    def rule_list_click(self):
        new_selection = self._rule_list.currentRow()

        # Check of selection really changed
        if not self._init and self._rule_selection == new_selection:
            return

        # Check if current rule is OK
        if not self.check_rule():
            self._rule_list.selectRow(self._rule_selection)
            return

        within_dialog_init = self._init
        if not within_dialog_init:
            self._init = True

        self._rule_selection = new_selection

        # Load new values
        if new_selection >= 0:
            self._del_rule_button.setDisabled(False)

            r = self._rules[new_selection]

            # Device data
            k = r['Key']
            self._device_combo.setDisabled(False)
            if k == LmNotif.DEVICE_ALL:
                self._device_combo.setCurrentIndex(0)
            elif k == LmNotif.DEVICE_UNKNOWN:
                self._device_combo.setCurrentIndex(1)
            else:
                self._mac_edit.setDisabled(False)
                self._mac_edit.setText(k)

            # Event data
            e = r['Events']
            self._add_event.setDisabled(False)
            self._add_event.setChecked(LmNotif.TYPE_ADD in e)
            self._del_event.setDisabled(False)
            self._del_event.setChecked(LmNotif.TYPE_DELETE in e)
            self._act_event.setDisabled(False)
            self._act_event.setChecked(LmNotif.TYPE_ACTIVE in e)
            self._ina_event.setDisabled(False)
            self._ina_event.setChecked(LmNotif.TYPE_INACTIVE in e)
            self._lnk_event.setDisabled(False)
            self._lnk_event.setChecked(LmNotif.TYPE_LINK_CHANGE in e)

            # Set rule action flags
            a = r['Rules']
            self._file_action.setDisabled(False)
            self._file_action.setChecked(LmNotif.RULE_FILE in a)
            self._email_action.setDisabled(False)
            self._email_action.setChecked(LmNotif.RULE_EMAIL in a)
        else:
            self._del_rule_button.setDisabled(True)
            self._device_combo.setCurrentIndex(0)
            self._device_combo.setDisabled(True)
            self._mac_edit.setText('')
            self._mac_edit.setDisabled(True)
            self._add_event.setChecked(False)
            self._add_event.setDisabled(True)
            self._del_event.setChecked(False)
            self._del_event.setDisabled(True)
            self._act_event.setChecked(False)
            self._act_event.setDisabled(True)
            self._ina_event.setChecked(False)
            self._ina_event.setDisabled(True)
            self._lnk_event.setChecked(False)
            self._lnk_event.setDisabled(True)
            self._file_action.setChecked(False)
            self._file_action.setDisabled(True)
            self._email_action.setChecked(False)
            self._email_action.setDisabled(True)

        if not within_dialog_init:
            self._init = False


    def load_device_list(self):
        device_list = self.parent().get_device_list()
        self._combo_device_list = []

        # Load from MacAddrTable file
        for d in LmConf.MacAddrTable:
            device = {'Name': LmConf.MacAddrTable[d], 'MAC': d}
            self._combo_device_list.append(device)

        # Load from device list if not already loaded
        for d in device_list:
            if (len(d['MAC'])) and (not any(e['MAC'] == d['MAC'] for e in self._combo_device_list)):
                device = {'Name': d['LBName'], 'MAC': d['MAC']}
                self._combo_device_list.append(device)

        # Sort by name
        self._combo_device_list = sorted(self._combo_device_list, key = lambda x: x['Name'])

        # Insert unknown device at the beginning
        device = {'Name': lx('-Unknown-'), 'MAC': ''}
        self._combo_device_list.insert(0, device)


    def device_selected(self, index):
        if not self._ignore_signal:
            if index == 0:
                self._ignore_signal = True
                self._mac_edit.setText('')
                self._ignore_signal = False
                self._mac_edit.setDisabled(True)
            elif index == 1:
                self._ignore_signal = True
                self._mac_edit.setText('')
                self._ignore_signal = False
                self._mac_edit.setDisabled(True)
            elif index > NotificationSetupDialog.device_combo_separator_index:
                self._mac_edit.setDisabled(False)
                self._ignore_signal = True
                self._mac_edit.setText(self._combo_device_list[index - (NotificationSetupDialog.device_combo_separator_index + 1)]['MAC'])
                self._ignore_signal = False

            if not self._init:
                self.save_rule()


    def mac_typed(self, mac_addr):
        if not self._ignore_signal:
            self._ignore_signal = True

            index = 0
            for i, d in enumerate(self._combo_device_list):
                if d['MAC'] == mac_addr:
                    index = i
                    break

            self._device_combo.setCurrentIndex(index + (NotificationSetupDialog.device_combo_separator_index + 1))
            self._ignore_signal = False

            if not self._init:
                self.save_rule()


    ### Add event checkbox option changed
    def add_event_changed(self, state):
        self.event_option_changed(self._add_event)


    ### Delete event checkbox option changed
    def del_event_changed(self, state):
        self.event_option_changed(self._del_event)


    ### Active event checkbox option changed
    def act_event_changed(self, state):
        self.event_option_changed(self._act_event)


    ### Inactive event checkbox option changed
    def ina_event_changed(self, state):
        self.event_option_changed(self._ina_event)


    ### Link change event checkbox option changed
    def lnk_event_changed(self, state):
        self.event_option_changed(self._lnk_event)


    ### An event checkbox option changed
    def event_option_changed(self, checkbox):
        if not self._init:
            # Check if at least one event is checked
            if (not self._add_event.isChecked() and
                not self._del_event.isChecked() and
                not self._act_event.isChecked() and
                not self._ina_event.isChecked() and
                not self._lnk_event.isChecked()):
                self._init = True
                checkbox.setChecked(True)
                self._init = False
            else:
                self.save_rule()


    ### File action checkbox option changed
    def file_action_changed(self, state):
        self.action_option_changed(self._file_action)


    ### Email action checkbox option changed
    def email_action_changed(self, state):
        self.action_option_changed(self._email_action)


    ### An action checkbox option changed
    def action_option_changed(self, checkbox):
        if not self._init:
            # Check if at least one action is checked
            if (not self._file_action.isChecked() and
                not self._email_action.isChecked()):
                self._init = True
                checkbox.setChecked(True)
                self._init = False
            else:
                self.save_rule()


    ### Notification event file path changed
    def event_file_path_typed(self, path):
        self._ok_button.setDisabled(len(path) == 0)


    ### Check if current rule is OK, returns True if yes
    def check_rule(self):
        if self._rule_selection >= 0:
            r = self._rules[self._rule_selection]
            k = r['Key']
            if k != LmNotif.DEVICE_ALL and k != LmNotif.DEVICE_UNKNOWN:
                m = self._mac_edit.text()
                if not LmTools.is_mac_addr(m):
                        self.parent().display_error(mx('{} is not a valid MAC address.', 'macErr').format(m))
                        self._mac_edit.setFocus()
                        return False
        return True


    ### Save current rule in rules buffer
    def save_rule(self):
        r = self._rules[self._rule_selection]

        # Key
        i = self._device_combo.currentIndex()
        if i == 0:
            r['Key'] = LmNotif.DEVICE_ALL
        elif i == 1:
            r['Key'] = LmNotif.DEVICE_UNKNOWN
        else:
            mac_addr = self._mac_edit.text()
            if not len(mac_addr):
                r['Key'] = LmNotif.DEVICE_UNKNOWN
            else:
                r['Key'] = mac_addr

        # Events
        e = []
        if self._add_event.isChecked():
            e.append(LmNotif.TYPE_ADD)
        if self._del_event.isChecked():
            e.append(LmNotif.TYPE_DELETE)
        if self._act_event.isChecked():
            e.append(LmNotif.TYPE_ACTIVE)
        if self._ina_event.isChecked():
            e.append(LmNotif.TYPE_INACTIVE)
        if self._lnk_event.isChecked():
            e.append(LmNotif.TYPE_LINK_CHANGE)
        r['Events'] = e

        # Rule action flags
        a = []
        if self._file_action.isChecked():
            a.append(LmNotif.RULE_FILE)
        if self._email_action.isChecked():
            a.append(LmNotif.RULE_EMAIL)
        r['Rules'] = a

        # Display rule
        self.set_rule_row(self._rule_selection, r)


    ### Click on add rule button
    def add_rule_button_click(self):
        # Add new default rule in buffer
        r = {'Key': LmNotif.DEVICE_ALL,
             'Events': [ LmNotif.TYPE_ACTIVE, LmNotif.TYPE_INACTIVE],
             'Rules': [ LmNotif.RULE_FILE ]}
        self._rules.append(r)

        # Add new item in list and select it
        i = self._rule_list.rowCount()
        self._rule_list.insertRow(i)
        self.set_rule_row(i, r)
        self._rule_list.selectRow(i)


    ### Click on delete rule button
    def del_rule_button_click(self):
        i = self._rule_selection

        # Delete the list line
        self._rule_selection = -1
        self._init = True
        self._rule_list.removeRow(i)
        self._init = False

        # Remove the rule from rules buffer
        self._rules.pop(i)

        # Update selection
        self._rule_selection = self._rule_list.currentRow()


    ### Select event file path button click
    def event_file_path_select_button_clic(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, lx('Select Folder'))
        if len(folder):
            folder = QtCore.QDir.toNativeSeparators(folder)
            self._event_file_path.setText(folder)


    ### Default file path checkbox changed
    def default_file_path_changed(self, state):
        if not self._init:
            if self._default_file_path.isChecked():
                self._event_file_path.setText(LmConf.get_config_directory())
                self._event_file_path.setDisabled(True)
                self._event_file_path_select_button.setDisabled(True)
            else:
                if LmConf.NotificationFilePath is None:
                    self._event_file_path.setText(LmConf.get_config_directory())
                else:
                    self._event_file_path.setText(LmConf.NotificationFilePath)
                self._event_file_path.setDisabled(False)
                self._event_file_path_select_button.setDisabled(False)


    ### Check if file path is OK, return True if yes
    def check_file_path(self):
        if self._default_file_path.isChecked():
            return True

        # Create directory if doesn't exist
        p = self._event_file_path.text()
        if not os.path.isdir(p):
            if LmTools.ask_question(mx('Configured log file directory does not exist. Do you want to create it?', 'logDirExist')):
                try:
                    os.makedirs(p)
                except Exception as e:
                    LmTools.error(f'Cannot create log file directory. Error: {e}')
                    LmTools.display_error(mx('Cannot create log file directory.\nError: {}.', 'logDirErr').format(e))
                    return False
            else:
                return False
        return True


    ### Click on OK button
    def ok_button_click(self):
        # Accept only if current rule & file path are OK
        if self.check_rule() and self.check_file_path():
            self.save_prefs()
            self.accept()
