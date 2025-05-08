### Livebox Monitor Wifi Configuration setup dialog ###

import copy

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.lang.LmLanguages import get_wifi_config_label as lx


# ################################ VARS & DEFS ################################

# Wifi MAC Filtering modes
MAC_FILTERING_MODES = ['Off', 'WhiteList', 'BlackList']


# ################################ Wifi Configuration dialog ################################
class WifiConfigDialog(QtWidgets.QDialog):
    def __init__(self, parent, config, guest):
        super(WifiConfigDialog, self).__init__(parent)

        self._guest = guest
        if self._guest:
            self.resize(390, 350)
        else:
            self.resize(390, 380)

        self._enable_checkbox = QtWidgets.QCheckBox(lx('Enabled'), objectName='enableCheckbox')
        self._enable_checkbox.clicked.connect(self.enable_click)

        if self._guest:
            duration_label = QtWidgets.QLabel(lx('Duration'), objectName='durationLabel')
            int_validator = QtGui.QIntValidator()
            int_validator.setRange(0, 999)
            self._duration_edit = QtWidgets.QLineEdit(objectName='durationEdit')
            self._duration_edit.setValidator(int_validator)
            duration_unit = QtWidgets.QLabel(lx('hours (0 = unlimited).'), objectName='durationUnit')

        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

        freq_label = QtWidgets.QLabel(lx('Radio Band'), objectName='freqLabel')
        self._freq_combo = QtWidgets.QComboBox(objectName='freqCombo')
        self._freq_combo.activated.connect(self.freq_selected)

        ssid_label = QtWidgets.QLabel(lx('SSID'), objectName='ssidLabel')
        self._ssid_edit = QtWidgets.QLineEdit(objectName='ssidEdit')

        options_label = QtWidgets.QLabel(lx('Options'), objectName='optionsLabel')
        self._freq_enabled_checkbox = QtWidgets.QCheckBox(lx('Enabled'), objectName='freqEnabledCheckbox')
        self._broadcast_checkbox = QtWidgets.QCheckBox(lx('SSID Broadcast'), objectName='broadcastCheckbox')
        self._wps_checkbox = QtWidgets.QCheckBox(lx('WPS'), objectName='wpsCheckbox')
        options_box = QtWidgets.QHBoxLayout()
        options_box.setSpacing(10)
        options_box.addWidget(self._freq_enabled_checkbox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        options_box.addWidget(self._broadcast_checkbox, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
        options_box.addWidget(self._wps_checkbox, 1, QtCore.Qt.AlignmentFlag.AlignLeft)

        mac_filtering_label = QtWidgets.QLabel(lx('MAC Filtering'), objectName='macFilteringLabel')
        self._mac_filtering_combo = QtWidgets.QComboBox(objectName='macFilteringCombo')
        self._mac_filtering_combo.addItems(MAC_FILTERING_MODES)

        secu_label = QtWidgets.QLabel(lx('Security'), objectName='secuLabel')
        self._secu_combo = QtWidgets.QComboBox(objectName='secuCombo')
        self._secu_combo.activated.connect(self.secu_selected)

        pass_label = QtWidgets.QLabel(lx('Password'), objectName='passLabel')
        self._pass_edit = QtWidgets.QLineEdit(objectName='passEdit')
        self._pass_edit.textChanged.connect(self.pass_typed)

        if not self._guest:
            chan_label = QtWidgets.QLabel(lx('Channel'), objectName='chanLabel')
            self._chan_combo = QtWidgets.QComboBox(objectName='chanCombo')

            mode_label = QtWidgets.QLabel(lx('Mode'), objectName='modeLabel')
            self._mode_combo = QtWidgets.QComboBox(objectName='modeCombo')

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(10)

        if self._guest:
            grid.addWidget(self._enable_checkbox, 0, 0, 1, 4)
            grid.addWidget(duration_label, 1, 0)
            grid.addWidget(self._duration_edit, 1, 1)
            grid.addWidget(duration_unit, 1, 2, 1, 3)
            grid.addWidget(separator, 2, 0, 1, 5)
            grid.addWidget(freq_label, 3, 0)
            grid.addWidget(self._freq_combo, 3, 1, 1, 4)
            grid.addWidget(ssid_label, 4, 0)
            grid.addWidget(self._ssid_edit, 4, 1, 1, 4)
            grid.addWidget(options_label, 5, 0)
            grid.addLayout(options_box, 5, 1, 1, 4)
            grid.addWidget(mac_filtering_label, 6, 0)
            grid.addWidget(self._mac_filtering_combo, 6, 1, 1, 4)            
            grid.addWidget(secu_label, 7, 0)
            grid.addWidget(self._secu_combo, 7, 1, 1, 4)
            grid.addWidget(pass_label, 8, 0)
            grid.addWidget(self._pass_edit, 8, 1, 1, 4)

            # Cannot be changed on guest interfaces
            self._broadcast_checkbox.setEnabled(False)
            self._wps_checkbox.setEnabled(False)
            self._mac_filtering_combo.setEnabled(False)
        else:
            grid.addWidget(self._enable_checkbox, 0, 0, 1, 2)
            grid.addWidget(separator, 1, 0, 1, 2)
            grid.addWidget(freq_label, 2, 0)
            grid.addWidget(self._freq_combo, 2, 1)
            grid.addWidget(ssid_label, 3, 0)
            grid.addWidget(self._ssid_edit, 3, 1)
            grid.addWidget(options_label, 4, 0)
            grid.addLayout(options_box, 4, 1)
            grid.addWidget(mac_filtering_label, 5, 0)
            grid.addWidget(self._mac_filtering_combo, 5, 1)          
            grid.addWidget(secu_label, 6, 0)
            grid.addWidget(self._secu_combo, 6, 1)
            grid.addWidget(pass_label, 7, 0)
            grid.addWidget(self._pass_edit, 7, 1)
            grid.addWidget(chan_label, 8, 0)
            grid.addWidget(self._chan_combo, 8, 1)
            grid.addWidget(mode_label, 9, 0)
            grid.addWidget(self._mode_combo, 9, 1)

        self._ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
        self._ok_button.clicked.connect(self.accept)
        self._ok_button.setDefault(True)
        cancel_button = QtWidgets.QPushButton(lx('Cancel'), objectName='cancel')
        cancel_button.clicked.connect(self.reject)
        hbox = QtWidgets.QHBoxLayout()
        hbox.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        hbox.setSpacing(10)
        hbox.addWidget(self._ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
        hbox.addWidget(cancel_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)

        vbox = QtWidgets.QVBoxLayout(self)
        vbox.addLayout(grid, 0)
        vbox.addLayout(hbox, 1)

        LmConfig.SetToolTips(self, 'wconfig')

        if self._guest:
            self.setWindowTitle(lx('Guest Wifi Configuration'))
        else:
            self.setWindowTitle(lx('Wifi Configuration'))

        self.set_config(config)

        self._ssid_edit.setFocus()
        self.setModal(True)
        self.show()


    def set_config(self, config):
        self._config = copy.deepcopy(config)
        self._current_freq = None

        if self._config['Enable']:
            self._enable_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self._enable_checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)

        if self._guest:
            self._duration_edit.setText(str(self._config['Duration'] // 3600))
            timer = self._config['Timer']
            if timer:
                self._enable_checkbox.setText(lx(f'Enabled for {LmTools.fmt_time(timer, True)}'))

        self.enable_click()      
        self.load_freq_combo()
        self.freq_selected(0)


    def enable_click(self):
        if self._guest:
            if self._enable_checkbox.checkState() == QtCore.Qt.CheckState.Checked:
                self._duration_edit.setText(str(self._config['Duration'] // 3600))
                self._duration_edit.setEnabled(True)
            else:
                self._duration_edit.setText('0')
                self._duration_edit.setEnabled(False)


    def load_freq_combo(self):
        c = self._config['Intf']
        for f in c:
            self._freq_combo.addItem(f['Name'], userData = f['Key'])


    def freq_selected(self, index):
        # First save config of previously selected freq
        self.save_freq_config()

        # Retrieve interface in config according to selection
        key, i = self.get_current_key_intf()
        if i is None:
            return
        self._current_freq = key

        self._ssid_edit.setText(i['SSID'])
        self._pass_edit.setText(i['KeyPass'])

        if i['Enable']:
            self._freq_enabled_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self._freq_enabled_checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)

        if i['Broadcast']:
            self._broadcast_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self._broadcast_checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)

        if i['WPS']:
            self._wps_checkbox.setCheckState(QtCore.Qt.CheckState.Checked)
        else:
            self._wps_checkbox.setCheckState(QtCore.Qt.CheckState.Unchecked)

        try:
            new_index = MAC_FILTERING_MODES.index(i['MACFiltering'])
        except:
            MAC_FILTERING_MODES.append(i['MACFiltering'])
            self._mac_filtering_combo.addItem(i['MACFiltering'])
            new_index = self._mac_filtering_combo.count() - 1
        self._mac_filtering_combo.setCurrentIndex(new_index)

        self.load_secu_combo()

        if not self._guest:
            self.load_chan_combo()
            self.load_mode_combo()


    def save_freq_config(self):
        if self._current_freq is not None:
            i = next((i for i in self._config['Intf'] if i['Key'] == self._current_freq), None)
            if i is None:
                LmTools.error('Internal error, unconsistent configuration - intf not found')
                self.reject()
                return
            i['SSID'] = self._ssid_edit.text()
            i['Enable'] = self._freq_enabled_checkbox.checkState() == QtCore.Qt.CheckState.Checked
            i['Broadcast'] = self._broadcast_checkbox.checkState() == QtCore.Qt.CheckState.Checked
            i['WPS'] = self._wps_checkbox.checkState() == QtCore.Qt.CheckState.Checked
            i['MACFiltering'] = self._mac_filtering_combo.currentText()
            i['Secu'] = self._secu_combo.currentText()
            if i['Secu'] != 'None':
                i['KeyPass'] = self._pass_edit.text()

            if not self._guest:
                chan = self._chan_combo.currentText()
                if chan == 'Auto':
                    i['ChannelAuto'] = True
                else:
                    i['ChannelAuto'] = False
                    i['Channel'] = int(chan)
                i['Mode'] = self._mode_combo.currentText()


    def pass_typed(self, text):
        self.set_ok_button_state()


    def load_secu_combo(self):
        key, i = self.get_current_key_intf()
        if i is None:
            return
        secu = i['Secu']
        secu_list = i['SecuAvail']
        if secu_list is None:
            LmTools.error('Internal error, unconsistent configuration - no security list')
            self.reject()
        secu_list = secu_list.split(',')
        self._secu_combo.clear()
        n = 0
        selection = -1
        for s in secu_list:
            if not 'WEP' in s:
                if s == secu:
                    selection = n
                self._secu_combo.addItem(s)
                n += 1

        if selection == -1:
            if secu is not None:
                self._secu_combo.addItem(secu)
                selection = n
                LmTools.log_debug(1, f'Warning - security {secu} not in list')
            elif n == 0:
                LmTools.error('Internal error, unconsistent configuration - no security')
                self.reject()
            else:
                LmTools.log_debug(1, 'Warning - no security, defaulting to first')
                selection = 0

        if selection >= 0:
            self._secu_combo.setCurrentIndex(selection)
            self.secu_selected(selection)


    def secu_selected(self, index):
        key, i = self.get_current_key_intf()
        if i is None:
            return

        secu = self._secu_combo.currentText()
        if secu == 'None':
            # Save pass key in case secu is reselected
            i['KeyPass'] = self._pass_edit.text()
            self._pass_edit.setEnabled(False)
            self._pass_edit.setText('')
        else:
            self._pass_edit.setEnabled(True)
            if len(self._pass_edit.text()) == 0:
                self._pass_edit.setText(i['KeyPass'])

        self.set_ok_button_state()


    def load_chan_combo(self):
        key, i = self.get_current_key_intf()
        if i is None:
            return
        intf = i['LLIntf']

        modes = self._config['Modes'].get(intf)
        if modes is not None:
            channels = modes.get('Channels')
            channels_in_use = modes.get('ChannelsInUse')
        else:
            channels = None
            channels_in_use = None
        if channels is None:
            LmTools.error('Internal error, unconsistent configuration - no channel list')
            self.reject()
            return
        channels = channels.split(',')
        if channels_in_use is None:
            channels_in_use = []
        else:
            channels_in_use = channels_in_use.split(',')

        current_channel = str(i['Channel'])

        self._chan_combo.clear()
        n = 0
        selection = -1
        if i['ChannelAutoSupport']:
            self._chan_combo.addItem('Auto')
            if i['ChannelAuto']:
                selection = n
            n += 1
        for c in channels:
            if (not c in channels_in_use) or (c == current_channel):
                self._chan_combo.addItem(c)
                if (c == current_channel) and (selection == -1):
                    selection = n
                n += 1

        if selection == -1:
            if current_channel != 'None':
                self._chan_combo.addItem(current_channel)
                selection = n
                LmTools.log_debug(1, f'Warning - channel {secu} not in list')
            elif n == 0:
                LmTools.error('Internal error, unconsistent configuration - no channel')
                self.reject()
            else:
                LmTools.log_debug(1, 'Warning - no channel, defaulting to first')
                selection = 0

        if selection >= 0:
            self._chan_combo.setCurrentIndex(selection)


    def load_mode_combo(self):
        key, i = self.get_current_key_intf()
        if i is None:
            return
        intf = i['LLIntf']

        modes = self._config['Modes'].get(intf)
        if modes is not None:
            modes = modes.get('Modes')
        if modes is None:
            LmTools.error('Internal error, unconsistent configuration - no mode list')
            self.reject()
            return
        modes = modes.split(',')

        current_mode = i['Mode']

        self._mode_combo.clear()
        n = 0
        selection = -1
        for m in modes:
            self._mode_combo.addItem(m)
            if m == current_mode:
                selection = n
            n += 1

        if selection == -1:
            if current_mode is not None:
                self._mode_combo.addItem(current_mode)
                selection = n
                LmTools.log_debug(1, f'Warning - mode {current_mode} not in list')
            elif n == 0:
                LmTools.error('Internal error, unconsistent configuration - no mode')
                self.reject()
            else:
                LmTools.log_debug(1, 'Warning - no mode, defaulting to first')
                selection = 0

        if selection >= 0:
            self._mode_combo.setCurrentIndex(selection)


    def get_current_key_intf(self):
        key = self._freq_combo.currentData()
        i = next((i for i in self._config['Intf'] if i['Key'] == key), None)
        if i is None:
            LmTools.error(f'Internal error, unconsistent configuration - intf {key} not found')
            self.reject()
        return key, i


    def get_config(self):
        self._config['Enable'] = self._enable_checkbox.checkState() == QtCore.Qt.CheckState.Checked
        if self._guest:
            self._config['Duration'] = int(self._duration_edit.text()) * 3600
        self.save_freq_config()
        return self._config


    def set_ok_button_state(self):
        # Check if another frequency is in background with no passkey
        disable = False
        for i in self._config['Intf']:
            if i['Key'] == self._current_freq:
                continue
            if (i['Secu'] != 'None') and (len(i['KeyPass']) == 0):
                disable = True
                break

        # Check current frequency
        if not disable:
            if (self._secu_combo.currentText() != 'None') and (len(self._pass_edit.text()) == 0):
                disable = True

        self._ok_button.setDisabled(disable)
