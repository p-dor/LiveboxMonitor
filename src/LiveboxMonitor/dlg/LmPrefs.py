### Livebox Monitor Preferences dialog ###

from PyQt6 import QtCore, QtGui, QtWidgets

from LiveboxMonitor.app import LmTools, LmConfig
from LiveboxMonitor.app.LmConfig import LmConf
from LiveboxMonitor.lang import LmLanguages
from LiveboxMonitor.lang.LmLanguages import get_config_prefs_label as lx,  get_config_message as mx


# ################################ Preferences dialog ################################
class PrefsDialog(QtWidgets.QDialog):
	def __init__(self, parent=None):
		super(PrefsDialog, self).__init__(parent)
		self.resize(620, 510)

		# Profiles box
		profile_layout = QtWidgets.QHBoxLayout()
		profile_layout.setSpacing(30)

		profile_list_layout = QtWidgets.QVBoxLayout()
		profile_list_layout.setSpacing(5)

		self._profile_selection = -1
		self._profile_list = QtWidgets.QListWidget(objectName='profileList')
		self._profile_list.setMaximumWidth(190)
		self._profile_list.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
		self._profile_list.itemSelectionChanged.connect(self.profile_list_click)
		profile_list_layout.addWidget(self._profile_list, 0)

		profile_button_box = QtWidgets.QHBoxLayout()
		profile_button_box.setSpacing(5)

		add_profile_button = QtWidgets.QPushButton(lx('Add'), objectName='addProfile')
		add_profile_button.clicked.connect(self.add_profile_button_click)
		profile_button_box.addWidget(add_profile_button)
		del_profile_button = QtWidgets.QPushButton(lx('Delete'), objectName='delProfile')
		del_profile_button.clicked.connect(self.del_profile_button_click)
		profile_button_box.addWidget(del_profile_button)
		profile_list_layout.addLayout(profile_button_box, 0)
		profile_layout.addLayout(profile_list_layout, 0)

		profile_name_label = QtWidgets.QLabel(lx('Name'), objectName='profileNameLabel')
		self._profile_name = QtWidgets.QLineEdit(objectName='profileNameEdit')
		self._profile_name.textChanged.connect(self.profile_name_changed)

		livebox_url_label = QtWidgets.QLabel(lx('Livebox URL'), objectName='liveboxUrlLabel')
		self._livebox_url = QtWidgets.QLineEdit(objectName='liveboxUrlEdit')

		livebox_user_label = QtWidgets.QLabel(lx('Livebox User'), objectName='liveboxUserLabel')
		self._livebox_user = QtWidgets.QLineEdit(objectName='liveboxUserEdit')

		self._filter_devices = QtWidgets.QCheckBox(lx('Filter Devices'), objectName='filterDevices')

		mac_addr_table_file_label = QtWidgets.QLabel(lx('MacAddr Table File'), objectName='macAddrTableFileLabel')
		self._mac_addr_table_file = QtWidgets.QLineEdit(objectName='macAddrTableFileEdit')

		self._default_profile = QtWidgets.QCheckBox(lx('Default'), objectName='defaultProfile')

		profile_edit_grid = QtWidgets.QGridLayout()
		profile_edit_grid.setSpacing(10)
		profile_edit_grid.addWidget(profile_name_label, 0, 0)
		profile_edit_grid.addWidget(self._profile_name, 0, 1)
		profile_edit_grid.addWidget(livebox_url_label, 1, 0)
		profile_edit_grid.addWidget(self._livebox_url, 1, 1)
		profile_edit_grid.addWidget(livebox_user_label, 2, 0)
		profile_edit_grid.addWidget(self._livebox_user, 2, 1)
		profile_edit_grid.addWidget(self._filter_devices, 3, 0, 1, 2)
		profile_edit_grid.addWidget(mac_addr_table_file_label, 4, 0)
		profile_edit_grid.addWidget(self._mac_addr_table_file, 4, 1)
		profile_edit_grid.addWidget(self._default_profile, 5, 0, 1, 2)
		profile_layout.addLayout(profile_edit_grid, 1)

		profile_group_box = QtWidgets.QGroupBox(lx('Profiles'), objectName='profileGroup')
		profile_group_box.setLayout(profile_layout)

		# General preferences box
		language_label = QtWidgets.QLabel(lx('Language'), objectName='languageLabel')
		self._language_combo = QtWidgets.QComboBox(objectName='languageCombo')
		for i in range(len(LmLanguages.LANGUAGES_KEY)):
			self._language_combo.addItem(LmLanguages.LANGUAGES_KEY[i] + ' - ' + LmLanguages.LANGUAGES_NAME[i])

		self._tooltips = QtWidgets.QCheckBox(lx('Tooltips'), objectName='tooltips')

		mac_addr_api_key_label = QtWidgets.QLabel(lx('macaddress.io API Key'), objectName='macAddrApiKeyLabel')
		self._mac_addr_api_key = QtWidgets.QLineEdit(objectName='macAddrApiKeyEdit')

		call_filter_api_key_label = QtWidgets.QLabel(lx('CallFilter API Key'), objectName='callFilterApiKeyLabel')
		self._call_filter_api_key = QtWidgets.QLineEdit(objectName='callFilterApiKeyEdit')

		int_validator = QtGui.QIntValidator()
		int_validator.setRange(1, 99)

		stats_frequency_label = QtWidgets.QLabel(lx('Stats Frequency'), objectName='statsFrequencyLabel')
		self._stats_frequency = QtWidgets.QLineEdit(objectName='statsFrequencyEdit')
		self._stats_frequency.setValidator(int_validator)

		phone_code_label = QtWidgets.QLabel(lx('Intl Phone Code'), objectName='phoneCodeLabel')
		self._phone_code = QtWidgets.QLineEdit(objectName='phoneCodeEdit')
		phone_code_validator = QtGui.QIntValidator()
		phone_code_validator.setRange(1, 999999)
		self._phone_code.setValidator(phone_code_validator)

		list_header_height_label = QtWidgets.QLabel(lx('List Header Height'), objectName='listHeaderHeightLabel')
		self._list_header_height = QtWidgets.QLineEdit(objectName='listHeaderHeightEdit')
		self._list_header_height.setValidator(int_validator)

		list_header_font_size_label = QtWidgets.QLabel(lx('List Header Font Size'), objectName='listHeaderFontSizeLabel')
		self._list_header_font_size = QtWidgets.QLineEdit(objectName='listHeaderFontSizeEdit')
		self._list_header_font_size.setValidator(int_validator)

		list_line_height_label = QtWidgets.QLabel(lx('List Line Height'), objectName='listLineHeightLabel')
		self._list_line_height = QtWidgets.QLineEdit(objectName='listLineHeightEdit')
		self._list_line_height.setValidator(int_validator)

		list_line_font_size_label = QtWidgets.QLabel(lx('List Line Font Size'), objectName='listLineFontSizeLabel')
		self._list_line_font_size = QtWidgets.QLineEdit(objectName='listLineFontSize')
		self._list_line_font_size.setValidator(int_validator)

		timeout_margin_validator = QtGui.QIntValidator()
		timeout_margin_validator.setRange(0, 240)
		timeout_margin_label = QtWidgets.QLabel(lx('Timeout Margin'), objectName='timeoutMarginLabel')
		self._timeout_margin = QtWidgets.QLineEdit(objectName='timeoutMarginEdit')
		self._timeout_margin.setValidator(timeout_margin_validator)

		csv_delimiter_label = QtWidgets.QLabel(lx('CSV Delimiter'), objectName='csvDelimiterLabel')
		self._csv_delimiter = QtWidgets.QLineEdit(objectName='csvDelimiterEdit')
		self._csv_delimiter.setMaxLength(1);
		self._csv_delimiter.setMaximumWidth(25)

		self._realtime_wifi_stats = QtWidgets.QCheckBox(lx('Realtime wifi device statistics'), objectName='realtimeWifiStats')
		self._prevent_sleep = QtWidgets.QCheckBox(lx('Prevent sleep mode'), objectName='preventSleepMode')
		self._native_ui_style = QtWidgets.QCheckBox(lx('Use native graphical interface style'), objectName='nativeUIStyle')
		self._save_passwords = QtWidgets.QCheckBox(lx('Save passwords'), objectName='savePasswords')

		prefs_edit_grid = QtWidgets.QGridLayout()
		prefs_edit_grid.setSpacing(10)

		prefs_edit_grid.addWidget(language_label, 0, 0)
		prefs_edit_grid.addWidget(self._language_combo, 0, 1)
		prefs_edit_grid.addWidget(self._tooltips, 0, 3)

		prefs_edit_grid.addWidget(mac_addr_api_key_label, 1, 0)
		prefs_edit_grid.addWidget(self._mac_addr_api_key, 1, 1, 1, 3)
		prefs_edit_grid.addWidget(call_filter_api_key_label, 2, 0)
		prefs_edit_grid.addWidget(self._call_filter_api_key, 2, 1, 1, 3)
		prefs_edit_grid.addWidget(stats_frequency_label, 3, 0)
		prefs_edit_grid.addWidget(self._stats_frequency, 3, 1)
		prefs_edit_grid.addWidget(phone_code_label, 3, 2)
		prefs_edit_grid.addWidget(self._phone_code, 3, 3)
		prefs_edit_grid.addWidget(list_header_height_label, 4, 0)
		prefs_edit_grid.addWidget(self._list_header_height, 4, 1)
		prefs_edit_grid.addWidget(list_header_font_size_label, 4, 2)
		prefs_edit_grid.addWidget(self._list_header_font_size, 4, 3)
		prefs_edit_grid.addWidget(list_line_height_label, 5, 0)
		prefs_edit_grid.addWidget(self._list_line_height, 5, 1)
		prefs_edit_grid.addWidget(list_line_font_size_label, 5, 2)
		prefs_edit_grid.addWidget(self._list_line_font_size, 5, 3)
		prefs_edit_grid.addWidget(timeout_margin_label, 6, 0)
		prefs_edit_grid.addWidget(self._timeout_margin, 6, 1)
		prefs_edit_grid.addWidget(csv_delimiter_label, 6, 2)
		prefs_edit_grid.addWidget(self._csv_delimiter, 6, 3)
		prefs_edit_grid.addWidget(self._realtime_wifi_stats, 7, 0, 1, 2)
		prefs_edit_grid.addWidget(self._prevent_sleep, 7, 2, 1, 2)
		prefs_edit_grid.addWidget(self._native_ui_style, 8, 0, 1, 2)
		prefs_edit_grid.addWidget(self._save_passwords, 8, 2, 1, 2)

		prefs_group_box = QtWidgets.QGroupBox(lx('Preferences'), objectName='prefsGroup')
		prefs_group_box.setLayout(prefs_edit_grid)

		# Button bar
		button_bar = QtWidgets.QHBoxLayout()
		ok_button = QtWidgets.QPushButton(lx('OK'), objectName='ok')
		ok_button.clicked.connect(self.ok_button_click)
		ok_button.setDefault(True)
		button_bar.addWidget(ok_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		cancel_button = QtWidgets.QPushButton(lx('Cancel'), objectName='cancel')
		cancel_button.clicked.connect(self.reject)
		button_bar.addWidget(cancel_button, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		button_bar.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		button_bar.setSpacing(10)

		# Final layout
		vbox = QtWidgets.QVBoxLayout(self)
		vbox.setSpacing(20)
		vbox.addWidget(profile_group_box, 0, QtCore.Qt.AlignmentFlag.AlignTop)
		vbox.addWidget(prefs_group_box, 0, QtCore.Qt.AlignmentFlag.AlignTop)
		vbox.addLayout(button_bar, 1)

		LmConfig.SetToolTips(self, 'prefs')

		self.setWindowTitle(lx('Preferences'))
		self.setModal(True)
		self.load_prefs()
		self.show()


	### Load preferences data
	def load_prefs(self):
		self._profiles = []

		# Load profile list
		for p in LmConf.Profiles:
			self._profiles.append(p.copy())
			i = QtWidgets.QListWidgetItem(p['Name'], self._profile_list)
			if p == LmConf.CurrProfile:
				self._profile_list.setCurrentItem(i)

		# Load paramaters
		try:
			i = LmLanguages.LANGUAGES_KEY.index(LmConf.Language)
		except:
			i = 0
		self._language_combo.setCurrentIndex(i)
		self._tooltips.setChecked(LmConf.Tooltips)
		self._stats_frequency.setText(str(int(LmConf.StatsFrequency / 1000)))
		self._mac_addr_api_key.setText(LmConf.MacAddrApiKey)
		self._call_filter_api_key.setText(LmConf.CallFilterApiKey)
		self._phone_code.setText(LmConf.PhoneCode)
		self._list_header_height.setText(str(LmConf.ListHeaderHeight))
		self._list_header_font_size.setText(str(LmConf.ListHeaderFontSize))
		self._list_line_height.setText(str(LmConf.ListLineHeight))
		self._list_line_font_size.setText(str(LmConf.ListLineFontSize))
		self._timeout_margin.setText(str(LmConf.TimeoutMargin))
		self._csv_delimiter.setText(LmConf.CsvDelimiter)
		self._realtime_wifi_stats.setChecked(LmConf.RealtimeWifiStats_save)
		self._prevent_sleep.setChecked(LmConf.PreventSleep)
		self._native_ui_style.setChecked(LmConf.NativeUIStyle)
		self._save_passwords.setChecked(LmConf.SavePasswords)


	### Save preferences data
	def save_prefs(self):
		# Save profile data
		LmConf.Profiles = self._profiles

		# Try to restore current profile by name
		curr_profile_name = LmConf.CurrProfile.get('Name')
		p = next((p for p in LmConf.Profiles if p['Name'] == curr_profile_name), None)
		if p is None:
			# Otherwise take the default
			p = next((p for p in LmConf.Profiles if p['Default']), None)
		if p is None:
			# If not default take the first
			p = LmConf.Profiles[0]
		LmConf.CurrProfile = p

		# Save parameters
		LmConf.Language = LmLanguages.LANGUAGES_KEY[self._language_combo.currentIndex()]
		LmConf.Tooltips = self._tooltips.isChecked()
		LmConf.StatsFrequency = int(self._stats_frequency.text()) * 1000
		LmConf.MacAddrApiKey = self._mac_addr_api_key.text()
		LmConf.CallFilterApiKey = self._call_filter_api_key.text()
		LmConf.PhoneCode = self._phone_code.text()
		LmConf.ListHeaderHeight = int(self._list_header_height.text())
		LmConf.ListHeaderFontSize = int(self._list_header_font_size.text())
		LmConf.ListLineHeight = int(self._list_line_height.text())
		LmConf.ListLineFontSize = int(self._list_line_font_size.text())
		LmConf.TimeoutMargin = int(self._timeout_margin.text())
		LmConf.CsvDelimiter = self._csv_delimiter.text()
		LmConf.RealtimeWifiStats_save = self._realtime_wifi_stats.isChecked()
		LmConf.PreventSleep = self._prevent_sleep.isChecked()
		LmConf.NativeUIStyle = self._native_ui_style.isChecked()
		LmConf.SavePasswords = self._save_passwords.isChecked()


	### Click on profile list item
	def profile_list_click(self):
		new_selection = self._profile_list.currentRow()

		# Save previous values before switch to new
		if self._profile_selection >= 0:
			# Check of selection really changed
			if self._profile_selection == new_selection:
				return

			# Save values
			if not self.save_profile():
				self._profile_list.setCurrentRow(self._profile_selection)
				return

		# Load new values
		self._profile_selection = -1		# To inhibit name text change event
		p = self._profiles[new_selection]
		self._profile_name.setText(p['Name'])
		self._livebox_url.setText(p['Livebox URL'])
		self._livebox_user.setText(p['Livebox User'])
		self._filter_devices.setChecked(p['Filter Devices'])
		self._mac_addr_table_file.setText(p['MacAddr Table File'])
		self._default_profile.setChecked(p['Default'])
		self._profile_selection = new_selection


	### Save current profile in profiles buffer, returns False if failed
	def save_profile(self):
		# Check if name is not duplicated
		profile_name = self._profile_name.text()
		if len(profile_name) == 0:
			LmTools.display_error(mx('Please set profile name.', 'profileName'))
			return False

		if self.count_profile_name(profile_name) > 1:
			LmTools.display_error(mx('Duplicated name.', 'profileDup'))
			return False

		# If default profile is selected, set all others to false
		default = self._default_profile.isChecked()
		if default:
			for p in self._profiles:
				p['Default'] = False

		# Save in profiles buffer
		p = self._profiles[self._profile_selection]
		p['Name'] = self._profile_name.text()
		p['Livebox URL'] = LmTools.clean_url(self._livebox_url.text())
		p['Livebox User'] = self._livebox_user.text()
		p['Filter Devices'] = self._filter_devices.isChecked()
		p['MacAddr Table File'] = self._mac_addr_table_file.text()
		p['Default'] = default
		return True


	### Profile name text changed
	def profile_name_changed(self, text):
		if self._profile_selection >= 0:
			self._profile_list.item(self._profile_selection).setText(text)


	### Find number of profiles in list matching a name
	def count_profile_name(self, name):
		return len(self._profile_list.findItems(name, QtCore.Qt.MatchFlag.MatchExactly))


	### Click on add profile button
	def add_profile_button_click(self):
		# First try to save current profile adding one
		if not self.save_profile():
			return

		# Add new empty profile in buffer
		p = {}
		p['Name'] = ''
		p['Livebox URL'] = LmConfig.DCFG_LIVEBOX_URL
		p['Livebox User'] = LmConfig.DCFG_LIVEBOX_USER
		p['Filter Devices'] = LmConfig.DCFG_FILTER_DEVICES
		p['MacAddr Table File'] = LmConfig.DCFG_MACADDR_TABLE_FILE
		p['Default'] = False
		self._profiles.append(p)

		# Add new item in list and select it
		i = QtWidgets.QListWidgetItem(p['Name'], self._profile_list)
		self._profile_list.setCurrentItem(i)

		# Set focus on profile's name
		self._profile_name.setFocus()


	### Click on delete profile button
	def del_profile_button_click(self):
		if len(self._profiles) == 1:
			LmTools.display_error(mx('You must have at least one profile.', 'profileOne'))
			return

		# Delete the list line
		i = self._profile_selection
		self._profile_selection = -1 	# Inhibit event handling
		self._profile_list.takeItem(i)

		# Remove the profile from profiles buffer
		self._profiles.pop(i)

		# Update selection
		self._profile_selection = self._profile_list.currentRow()


	### Click on OK button
	def ok_button_click(self):
		# First try to save current profile before leaving
		if self.save_profile():
			self.save_prefs()
			self.accept()
