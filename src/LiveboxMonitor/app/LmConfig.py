### Livebox Monitor Configuration module ###

import sys
import os
import platform
import requests
import json
import base64
import hashlib

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets
from cryptography.fernet import Fernet

from LiveboxMonitor.app import LmTools
from LiveboxMonitor.api.LmSession import DEFAULT_TIMEOUT
from LiveboxMonitor.api.LmSession import LmSession
from LiveboxMonitor.api.LmLiveboxInfoApi import LiveboxInfoApi
from LiveboxMonitor.dlg.LmReleaseWarning import ReleaseWarningDialog
from LiveboxMonitor.lang import LmLanguages
from LiveboxMonitor.lang.LmLanguages import get_config_prefs_label as lx, get_config_message as mx

from LiveboxMonitor.__init__ import __build__


# ################################ VARS & DEFS ################################

# Config file name
CONFIG_FILE = 'Config.txt'
KEY_FILE = 'Key.txt'
SPAMCALLS_FILE = 'SpamCalls.txt'
LIVEBOX_CACHE_DIR = 'lbcache_'
LIVEBOX_ICON_CACHE_DIR = 'icons'
CUSTOM_ICON_DIR = 'custom_icons'

# Config default
DCFG_LIVEBOX_URL = 'http://livebox.home/'
DCFG_LIVEBOX_USER = 'admin'
DCFG_LIVEBOX_PASSWORD = ''
DCFG_FILTER_DEVICES = True
DCFG_MACADDR_TABLE_FILE = 'MacAddrTable.txt'
DCFG_LANGUAGE = 'FR'
DCFG_TOOLTIPS = True
DCFG_STATS_FREQUENCY = 3000
DCFG_MACADDR_API_KEY = ''
DCFG_CALLFILTER_API_KEY = ''
DCFG_PHONE_CODE = '33'
DCFG_LIST_HEADER_HEIGHT = 25
DCFG_LIST_HEADER_FONT_SIZE = 0
DCFG_LIST_LINE_HEIGHT = 30
DCFG_LIST_LINE_FONT_SIZE = 0
DCFG_REALTIME_WIFI_STATS = False
DCFG_NATIVE_UI_STYLE = False
DCFG_LOG_LEVEL = 0
DCFG_NO_RELEASE_WARNING = 0
DCFG_REPEATERS = None
DCFG_GRAPH = None
DCFG_TABS = None
DCFG_NOTIFICATION_RULES = None
DCFG_NOTIFICATION_FLUSH_FREQUENCY = 30	# Consolidated notifs flush + time diff between events to merge - in seconds
DCFG_NOTIFICATION_FILE_PATH = None
DCFG_EMAIL = None
DCFG_CSV_DELIMITER = ';'
DCFG_TIMEOUT_MARGIN = 0
DCFG_PREVENT_SLEEP = True
DCFG_SAVE_PASSWORDS = True

# Static config
GIT_REPO = 'p-dor/LiveboxMonitor'
GITRELEASE_URL = 'https://api.github.com/repos/{}/releases/latest'
ICON_URL = 'assets/common/images/app_conf/'

# Graphical config
WIND_HEIGHT_ADJUST = 0		# Space to add to a window height to respect a table wished height inside
DIAG_HEIGHT_ADJUST = 0		# Space to add to a dialog height to respect a table wished height inside
TABLE_ADJUST = 4			# Space to add to a table height to respect a table wished height
LIST_HEADER_FONT_SIZE = 0	# 0 = default system font, value can be overriden by LmConf.ListHeaderFontSize
LIST_HEADER_FONT = None
LIST_LINE_FONT_SIZE = 0		# 0 = default system font, value can be overriden by LmConf.ListLineFontSize
LIST_LINE_FONT = None
LIST_STYLESHEET = ''
LIST_HEADER_STYLESHEET = ''

# Interface name mapping
INTF_NAME_MAP = []

# LB4 Interface name mapping
INTF_NAME_MAP_LB4 = {}

# LB5 Interface name mapping
INTF_NAME_MAP_LB5 = {'Eth0': 'Eth1', 'Eth1': 'Eth2', 'Eth2': 'Eth3', 'Eth3': 'Eth4'}

# LB6 Interface name mapping
INTF_NAME_MAP_LB6 = {'Eth0': 'Eth 2.5G'}

# LB7 Interface name mapping
# With name: Eth0 -> 'Eth 10G', all others is name capitalized
INTF_NAME_MAP_LB7 = {'Eth0': 'Eth 10G'}

# Device types & icons
DEVICE_TYPES = [
	{'Key': 'Unknown',                     'Name': 'Unknown',                    'Icon': 'e_default_device.png'},
	{'Key': 'AC Outlet',                   'Name': 'AC Outlet',                  'Icon': 'e_smart_plug.png'},
	{'Key': 'Acces Point',                 'Name': 'Acces Point',                'Icon': 'e_pointacceswifi.png'},
	{'Key': 'Airbox',                      'Name': 'Airbox',                     'Icon': 'e_airbox_gen.png'},
	{'Key': 'Apple AirPort',               'Name': 'Apple AirPort',              'Icon': 'e_apple_express.png'},
	{'Key': 'Apple AirPort Time Capsule',  'Name': 'Apple AirPort Time Capsule', 'Icon': 'e_apple_extreme_capsule.png'},
	{'Key': 'Apple Time Capsule',          'Name': 'Apple Time Capsule',         'Icon': 'e_apple_extreme_capsule.png'},
	{'Key': 'Apple TV',                    'Name': 'Apple TV',                   'Icon': 'e_apple_tv.png'},
	{'Key': 'Chromecast',                  'Name': 'Chromecast',                 'Icon': 'e_chromecast.png'},
	{'Key': 'Desktop',                     'Name': 'Computer',                   'Icon': 'e_ordibureau.png'},
	{'Key': 'Desktop Linux',               'Name': 'Computer (Linux)',           'Icon': 'e_ordibureau_Linux.png'},
	{'Key': 'Desktop iOS',                 'Name': 'Computer (MacOS)',           'Icon': 'e_ordibureau_ios.png'},
	{'Key': 'Desktop Windows',             'Name': 'Computer (Windows)',         'Icon': 'e_ordibureau_windows.png'},
	{'Key': 'Game Console',                'Name': 'Console',                    'Icon': 'e_consolejeux.png'},
	{'Key': 'Dimmable Color Bulb',         'Name': 'Dimmer Light',               'Icon': 'e_smart_bulb.png'},
	{'Key': 'Djingo Speaker',              'Name': 'Djingo Speaker',             'Icon': 'e_djingospeaker.png'},   # Not (yet?) supported by LB5
	{'Key': 'Domestic Robot',              'Name': 'Domestic Robot',             'Icon': 'e_Homelive.png'},
	{'Key': 'Domino',                      'Name': 'Domino',                     'Icon': 'e_domino.png'},
	{'Key': 'Door Sensor',                 'Name': 'Door Sensor',                'Icon': 'e_door_sensor.png'},
	{'Key': 'ExtenderTV',                  'Name': 'Extender TV',                'Icon': 'e_liveplugsolo.png'},
	{'Key': 'ExtenderWiFiPlus',            'Name': 'Extender Wi-Fi Plus',        'Icon': 'e_pointacceswifi.png'},
	{'Key': 'Femtocell',                   'Name': 'Femtocell',                  'Icon': 'e_femtocell.png'},
	{'Key': 'Google OnHub',                'Name': 'Google OnHub',               'Icon': 'e_google_onhub.png'},
	{'Key': 'HiFi',                        'Name': 'HiFi',                       'Icon': 'e_enceinte_hifi.png'},
	{'Key': 'HomeLibrary',                 'Name': 'Home Library',               'Icon': 'e_homelibrary.png'},
	{'Key': 'HomeLive',                    'Name': 'Home Live',                  'Icon': 'e_Homelive.png'},
	{'Key': 'Homepoint',                   'Name': 'Home Point',                 'Icon': 'e_homepoint.png'},
	{'Key': 'IP Camera',                   'Name': 'IP Camera',                  'Icon': 'e_camera_ip.png'},
	{'Key': 'Laptop',                      'Name': 'Laptop',                     'Icon': 'e_ordiportable.png'},
	{'Key': 'Laptop iOS',                  'Name': 'Laptop (iOS)',               'Icon': 'e_ordiportable_ios.png'},
	{'Key': 'Laptop Linux',                'Name': 'Laptop (Linux)',             'Icon': 'e_ordiportable_Linux.png'},
	{'Key': 'Laptop Windows',              'Name': 'Laptop (Windows)',           'Icon': 'e_ordiportable_windows.png'},
	{'Key': 'leBloc',                      'Name': 'Le Bloc d\'Orange',          'Icon': 'e_leblocdorange.png'},
	{'Key': 'HomePlug',                    'Name': 'Liveplug',                   'Icon': 'e_liveplug_cpl.png'},
	{'Key': 'LivePlugWifi',                'Name': 'Liveplug solo Wi-Fi',        'Icon': 'e_liveplugsolo.png'},
	{'Key': 'WiFiExtender',                'Name': 'Liveplug Wi-Fi Extender',    'Icon': 'e_liveplug_extender.png'},
	{'Key': 'Liveradio',                   'Name': 'LiveRadio',                  'Icon': 'e_liveradio.png'},
	{'Key': 'Motion Sensor',               'Name': 'Motion Sensor',              'Icon': 'e_motion_sensor.png'},
	{'Key': 'Nas',                         'Name': 'NAS',                        'Icon': 'e_nas.png'},
	{'Key': 'Notebook',                    'Name': 'Notebook',                   'Icon': 'e_notebook.png'},
	{'Key': 'Notebook Linux',              'Name': 'Notebook (Linux)',           'Icon': 'e_notebook_Linux.png'},
	{'Key': 'Notebook Windows',            'Name': 'Notebook (Windows)',         'Icon': 'e_notebook_windows.png'},
	{'Key': 'Old Phone',                   'Name': 'Old Handset Phone',          'Icon': 'e_telephoneold.png'},
	{'Key': 'Phone',                       'Name': 'Phone',                      'Icon': 'e_telephonenew.png'},
	{'Key': 'Power Meter',                 'Name': 'Power Meter',                'Icon': 'e_smart_plug.png'},
	{'Key': 'Printer',                     'Name': 'Printer',                    'Icon': 'e_imprimante.png'},
	{'Key': 'Set-top Box',                 'Name': 'Set-top Box',                'Icon': 'e_decodeurTV.png'},
	{'Key': 'Set-top Box TV 4',            'Name': 'Set-top Box 4',              'Icon': 'e_decodeur_tv_4.png'},
	{'Key': 'Set-top Box TV Play',         'Name': 'Set-top Box Play',           'Icon': 'e_decodeur_tv_play.png'},
	{'Key': 'Set-top Box TV UHD',          'Name': 'Set-top Box UHD',            'Icon': 'e_decodeur_tv_uhd.png'},
	{'Key': 'Set-top Box TV Universal',    'Name': 'Set-top Box Universal',      'Icon': 'e_decodeur_tv_universel.png'},
	{'Key': 'Simple Button',               'Name': 'Simple Button',              'Icon': 'e_simple_button.png'},
	{'Key': 'Color Bulb',                  'Name': 'Smart Bulb',                 'Icon': 'e_smart_bulb.png'},
	{'Key': 'Smart Plug',                  'Name': 'Smart Plug',                 'Icon': 'e_smart_plug.png'},
	{'Key': 'Mobile',                      'Name': 'Smartphone',                 'Icon': 'e_mobile.png'},
	{'Key': 'Mobile Android',              'Name': 'Smartphone (Android)',       'Icon': 'e_mobile_android.png'},
	{'Key': 'Mobile iOS',                  'Name': 'Smartphone (iOS)',           'Icon': 'e_mobile_ios.png'},
	{'Key': 'Mobile Windows',              'Name': 'Smartphone (Windows)',       'Icon': 'e_mobile_windows.png'},
	{'Key': 'Smoke Detector',              'Name': 'Smoke Detector',             'Icon': 'e_sensorhome.png'},
	{'Key': 'Disk',                        'Name': 'Storage Device',             'Icon': 'e_periphstockage.png'},
	{'Key': 'Switch4',                     'Name': 'Switch (4 ports)',           'Icon': 'e_switch4.png'},
	{'Key': 'Switch8',                     'Name': 'Switch (8 ports)',           'Icon': 'e_switch8.png'},
	{'Key': 'Tablet',                      'Name': 'Tablet',                     'Icon': 'e_tablette.png'},
	{'Key': 'Tablet Android',              'Name': 'Tablet (Android)',           'Icon': 'e_tablette_android.png'},
	{'Key': 'Tablet iOS',                  'Name': 'Tablet (iOS)',               'Icon': 'e_tablette_ios.png'},
	{'Key': 'Tablet Windows',              'Name': 'Tablet (Windows)',           'Icon': 'e_tablette_windows.png'},
	{'Key': 'TV',                          'Name': 'TV',                         'Icon': 'e_TV.png'},
	{'Key': 'TVKey',                       'Name': 'TV Stick',                   'Icon': 'e_cletv.png'},
	{'Key': 'TVKey v2',                    'Name': 'TV Stick v2',                'Icon': 'e_cletv_v2.png'},
	{'Key': 'USBKey',                      'Name': 'USB Key',                    'Icon': 'e_cleusb.png'},
	{'Key': 'WiFi_Access_Point',           'Name': 'Wi-Fi Access Point',         'Icon': 'e_pointacceswifi.png'},
	{'Key': 'Window Sensor',               'Name': 'Window Sensor',              'Icon': 'e_door_sensor.png'},
	{'Key': 'Computer',                    'Name': 'Windows Computer',           'Icon': 'e_ordibureau_windows.png'},
	{'Key': 'SAH AP',                      'Name': 'Wi-Fi Repeater',             'Icon': 'e_pointacceswifi.png'},
	{'Key': 'repeteurwifi6',               'Name': 'Wi-Fi Repeater 6',           'Icon': 'e_pointacceswifi.png'}
]



# ################################ Tools ################################

### Setting up application style depending on platform
def SetApplicationStyle():
	global WIND_HEIGHT_ADJUST
	global DIAG_HEIGHT_ADJUST
	global TABLE_ADJUST
	global LIST_HEADER_FONT_SIZE
	global LIST_HEADER_FONT
	global LIST_LINE_FONT_SIZE
	global LIST_LINE_FONT
	global LIST_STYLESHEET
	global LIST_HEADER_STYLESHEET

	aKeys = QtWidgets.QStyleFactory.keys()
	aPlatform =  platform.system()
	aStyle = 'Fusion'
	if LmConf.NativeUIStyle:
		if aPlatform == 'Windows':
			aStyle = 'Windows'
		elif aPlatform == 'Darwin':
			aStyle = 'macOS'

	if aStyle == 'Fusion':
		if aPlatform == 'Windows':
			WIND_HEIGHT_ADJUST = 2
			DIAG_HEIGHT_ADJUST = -4
			TABLE_ADJUST = 2
			LIST_HEADER_FONT_SIZE = 0	# Let system default
			LIST_LINE_FONT_SIZE = 0		# Let system default
			LIST_STYLESHEET = 'QTableView { color:black; background-color:#FAFAFA }'
			LIST_HEADER_STYLESHEET = '''
				QHeaderView::section {
					border-width: 0px 0px 1px 0px;
					border-color: grey
				}
				'''
		elif aPlatform == 'Darwin':
			WIND_HEIGHT_ADJUST = 2
			DIAG_HEIGHT_ADJUST = -4
			TABLE_ADJUST = 2
			LIST_HEADER_FONT_SIZE = 11
			LIST_LINE_FONT_SIZE = 10
			LIST_STYLESHEET = 'QTableView { color:black; background-color:#F0F0F0; gridline-color:#FFFFFF }'
			LIST_HEADER_STYLESHEET = '''
				QHeaderView::section {
					border-width: 0px 0px 1px 0px;
					border-color: grey
				}
				'''
		else:
			WIND_HEIGHT_ADJUST = 2
			DIAG_HEIGHT_ADJUST = -4
			TABLE_ADJUST = 4
			LIST_HEADER_FONT_SIZE = 12
			LIST_LINE_FONT_SIZE = 10
			LIST_STYLESHEET = 'QTableView { color:black; background-color:#FAFAFA }'
			LIST_HEADER_STYLESHEET = '''
				QHeaderView::section {
					border-width: 0px 0px 1px 0px;
					border-color: grey
				}
				'''
	elif aStyle == 'Windows':
		WIND_HEIGHT_ADJUST = -1
		DIAG_HEIGHT_ADJUST = 0
		TABLE_ADJUST = 4
		LIST_HEADER_FONT_SIZE = 0	# Let system default
		LIST_LINE_FONT_SIZE = 0		# Let system default
		LIST_STYLESHEET = 'QTableView { color:black; background-color:#FAFAFA }'
		LIST_HEADER_STYLESHEET = '''
			QHeaderView::section {
				border-width: 0px 0px 1px 0px;
				border-style: solid;
				border-color: grey
			}
			'''
	elif aStyle == 'macOS':
		WIND_HEIGHT_ADJUST = -4
		DIAG_HEIGHT_ADJUST = 30
		TABLE_ADJUST = 4
		LIST_HEADER_FONT_SIZE = 11
		LIST_LINE_FONT_SIZE = 10
		LIST_STYLESHEET = 'QTableView { color:black; background-color:#F0F0F0; gridline-color:#FFFFFF }'
		LIST_HEADER_STYLESHEET = '''
			QHeaderView::section {
				color:black;
				background-color:#C0C0C0;
				border: 0px
			}
			'''

	# Setup table's fonts
	LIST_HEADER_FONT = QtGui.QFont()
	LIST_HEADER_FONT.setBold(True)
	if LmConf.ListHeaderFontSize:
		LIST_HEADER_FONT.setPointSize(LmConf.ListHeaderFontSize)
	elif LIST_HEADER_FONT_SIZE:
		LIST_HEADER_FONT.setPointSize(LIST_HEADER_FONT_SIZE)
	LIST_LINE_FONT = QtGui.QFont()
	if LmConf.ListLineFontSize:
		LIST_LINE_FONT.setPointSize(LmConf.ListLineFontSize)
	elif LIST_LINE_FONT_SIZE:
		LIST_LINE_FONT.setPointSize(LIST_LINE_FONT_SIZE)

	if aStyle in aKeys:
		QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create(aStyle))


### Compute table height based on nb of rows
def TableHeight(iRowNb):
	return LmConf.ListHeaderHeight + (LmConf.ListLineHeight * iRowNb) + TABLE_ADJUST


### Compute base height of a window based on nb of rows of a single table
def WindowHeight(iRowNb):
	return TableHeight(iRowNb) + WIND_HEIGHT_ADJUST


### Compute base height of a dialog based on nb of rows of a single table
def DialogHeight(iRowNb):
	return TableHeight(iRowNb) + DIAG_HEIGHT_ADJUST


### Assign Tooltips to all QWidgets in a window/dialog/tab
def SetToolTips(iQtObject, iKey):
	if LmConf.Tooltips:
		aItemList = iQtObject.findChildren(QtWidgets.QWidget, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly)
		for aItem in aItemList:
			k = aItem.objectName()
			if len(k):
				if isinstance(aItem, QtWidgets.QTableWidget):
					h = aItem.horizontalHeader()
					m = h.model()
					for c in range(h.count()):
						k = m.headerData(c, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)
						if k is not None:
							aItem.horizontalHeaderItem(c).setToolTip(LmLanguages.get_tooltip(iKey, k))
				elif isinstance(aItem, QtWidgets.QTabWidget):
					for i in range(aItem.count()):
						k = aItem.widget(i).objectName()
						if len(k):
							aItem.setTabToolTip(i, LmLanguages.get_tooltip(iKey, k))
				elif isinstance(aItem, QtWidgets.QGroupBox):
					# Set tooltip to the group if any
					aItem.setToolTip(LmLanguages.get_tooltip(iKey, k))
					# Recursive call to handle group content
					SetToolTips(aItem, iKey)
				else:
					aItem.setToolTip(LmLanguages.get_tooltip(iKey, k))


### Setup configuration according to Livebox model
def SetLiveboxModel(iModel):
	global INTF_NAME_MAP

	match iModel:
		case 3 | 4:
			INTF_NAME_MAP = INTF_NAME_MAP_LB4
		case 5:
			INTF_NAME_MAP = INTF_NAME_MAP_LB5
		case 6:
			INTF_NAME_MAP = INTF_NAME_MAP_LB6
		case 7 | 7.1 | 7.2:
			INTF_NAME_MAP = INTF_NAME_MAP_LB7
		case _:
			INTF_NAME_MAP = INTF_NAME_MAP_LB7


### Check if latest release
def ReleaseCheck():
	# Call GitHub API to fetch latest release infos
	try:
		d = requests.get(GITRELEASE_URL.format(GIT_REPO), timeout = 1)
		d = json.loads(d.content)
		v = d['tag_name']
	except BaseException as e:
		LmTools.error(f'Cannot get latest release infos. Error: {e}')
		return

	# Convert version string into hex int aligned with __build__ representation
	s = v.split('.')
	l = len(s)
	aMajor = s[0]
	if l >= 2:
		aMinor = s[1]
	else:
		aMinor = '00'
	if l >= 3:
		aPatch = s[2]
	else:
		aPatch = '00'
	try:
		r = int(aMajor.zfill(2) + aMinor.zfill(2) + aPatch.zfill(2), 16)
	except:
		LmTools.error(f'Cannot decode latest release infos. Error: {e}')
		return

	# Warn if this release is not the latest
	if (r > __build__) and (LmConf.NoReleaseWarning != r):
		aReleaseWarningDialog = ReleaseWarningDialog(v)
		if aReleaseWarningDialog.exec():
			return
		# User decided to not be warned again, remember in config
		LmConf.NoReleaseWarning = r
		LmConf.save()


### Get a cross platform 32 bytes unique hardware key as base64 string
def GetHardwareKey():
	# Use platform calls to get a unique string
	aHardwareID = platform.system() + platform.machine() + platform.node() + platform.processor()

	# Hashing to 32 bytes array
	aHardwareHash = hashlib.sha256(aHardwareID.encode('utf-8')).digest()

	# Return as 44-chars base64 string
	return base64.urlsafe_b64encode(aHardwareHash).decode('utf-8')



# ################################ Config Class ################################
class LmConf:
	Secret = None
	Profiles = None
	CurrProfile = None
	LiveboxURL = DCFG_LIVEBOX_URL
	LiveboxUser = DCFG_LIVEBOX_USER
	LiveboxPassword = DCFG_LIVEBOX_PASSWORD
	LiveboxMAC = ''
	FilterDevices = DCFG_FILTER_DEVICES
	MacAddrTableFile = DCFG_MACADDR_TABLE_FILE
	MacAddrTable = {}
	SpamCallsTable = []
	Language = DCFG_LANGUAGE
	Tooltips = DCFG_TOOLTIPS
	StatsFrequency = DCFG_STATS_FREQUENCY
	MacAddrApiKey = DCFG_MACADDR_API_KEY
	CallFilterApiKey = DCFG_CALLFILTER_API_KEY
	PhoneCode = DCFG_PHONE_CODE
	ListHeaderHeight = DCFG_LIST_HEADER_HEIGHT
	ListHeaderFontSize = DCFG_LIST_HEADER_FONT_SIZE
	ListLineHeight = DCFG_LIST_LINE_HEIGHT
	ListLineFontSize = DCFG_LIST_LINE_FONT_SIZE
	RealtimeWifiStats = DCFG_REALTIME_WIFI_STATS
	RealtimeWifiStats_save = RealtimeWifiStats	# Need to decouple saving as master value must not be changed live
	NativeUIStyle = DCFG_NATIVE_UI_STYLE
	LogLevel = DCFG_LOG_LEVEL
	NoReleaseWarning = DCFG_NO_RELEASE_WARNING
	Repeaters = DCFG_REPEATERS
	Graph = DCFG_GRAPH
	Tabs = DCFG_TABS
	AllDeviceIconsLoaded = False
	NotificationRules = DCFG_NOTIFICATION_RULES
	NotificationFlushFrequency = DCFG_NOTIFICATION_FLUSH_FREQUENCY
	NotificationFilePath = DCFG_NOTIFICATION_FILE_PATH
	Email = DCFG_EMAIL
	NativeRun = True	# Run mode - Python script (True) / PyPI package (False)
	CsvDelimiter = DCFG_CSV_DELIMITER
	TimeoutMargin = DCFG_TIMEOUT_MARGIN
	PreventSleep = DCFG_PREVENT_SLEEP
	SavePasswords = DCFG_SAVE_PASSWORDS


	### Load configuration, returns False the program aborts starting
	@staticmethod
	def load():
		# First load secret key
		if not LmConf.loadKey():
			return False

		aConfigFile = None
		aDirtyConfig = False
		aConfigFilePath = os.path.join(LmConf.getConfigDirectory(), CONFIG_FILE)
		LmTools.log_debug(1, 'Reading configuration in', aConfigFilePath)
		try:
			aConfigFile = open(aConfigFilePath)
			aConfig = json.load(aConfigFile)
		except OSError:
			LmTools.error('No configuration file, creating one.')
			aDirtyConfig = True
		except BaseException as e:
			LmTools.error(str(e))
			if LmTools.ask_question(mx('Wrong {} file, fully reset it?', 'wrongFile').format(CONFIG_FILE)):
				aDirtyConfig = True
			else:
				if aConfigFile is not None:
					aConfigFile.close()
				return False
		else:
			# Try to load language as soon as possible
			p = aConfig.get('Language')
			if p is not None:
				LmConf.Language = str(p)
				if LmConf.Language not in LmLanguages.LANGUAGES_KEY:
					LmConf.Language = DCFG_LANGUAGE
			LmLanguages.set_language(LmConf.Language)

			# Check if config version is more recent than the application
			aConfigVersion = aConfig.get('Version', 0)
			if aConfigVersion > __build__:
				if not LmTools.ask_question(mx('This version of the application is older than the configuration file.\n'
											   'If you continue you might lose some setup.\n'
											   'Are you sure you want to continue?', 'configVersion')):
					return False

			# Potentially convert the format to newer version
			aDirtyConfig = LmConf.convert(aConfig)

			# Load all configs
			p = aConfig.get('Profiles')
			if p is not None:
				LmConf.Profiles = p
				aOK, aDirty = LmConf.selectProfile()
				if aOK:
					if aDirty:
						aDirtyConfig = True
				else:
					return False
			if LmConf.CurrProfile is None:
				raise Exception('No profile detected')
			p = aConfig.get('Tooltips')
			if p is not None:
				LmConf.Tooltips = bool(p)
			p = aConfig.get('Stats Frequency')
			if p is not None:
				LmConf.StatsFrequency = int(p)
			p = aConfig.get('MacAddr API Key')
			if p is not None:
				LmConf.MacAddrApiKey = p
			p = aConfig.get('CallFilter API Key')
			if p is not None:
				LmConf.CallFilterApiKey = p
			p = aConfig.get('Phone Code')
			if p is not None:
				LmConf.PhoneCode = str(p)
			p = aConfig.get('List Header Height')
			if p is not None:
				LmConf.ListHeaderHeight = int(p)
			p = aConfig.get('List Header Font Size')
			if p is not None:
				LmConf.ListHeaderFontSize = int(p)
			p = aConfig.get('List Line Height')
			if p is not None:
				LmConf.ListLineHeight = int(p)
			p = aConfig.get('List Line Font Size')
			if p is not None:
				LmConf.ListLineFontSize = int(p)
			p = aConfig.get('Realtime Wifi Stats')
			if p is not None:
				LmConf.RealtimeWifiStats = bool(p)
				LmConf.RealtimeWifiStats_save = LmConf.RealtimeWifiStats
			p = aConfig.get('Native UI Style')
			if p is not None:
				LmConf.NativeUIStyle = bool(p)
			p = aConfig.get('Log Level')
			if p is not None:
				LmConf.LogLevel = int(p)
				if LmConf.LogLevel < 0:
					LmConf.LogLevel = 0
				elif LmConf.LogLevel > 2:
					LmConf.LogLevel = 2
				LmTools.set_verbosity(LmConf.LogLevel)
			p = aConfig.get('No Release Warning')
			if p is not None:
				LmConf.NoReleaseWarning = int(p)
			p = aConfig.get('Repeaters')
			if p is not None:
				LmConf.Repeaters = p
			p = aConfig.get('Graph')
			if p is not None:
				LmConf.Graph = p
			p = aConfig.get('Tabs')
			if p is not None:
				LmConf.Tabs = p
			p = aConfig.get('NotificationRules')
			if p is not None:
				LmConf.NotificationRules = p
			p = aConfig.get('NotificationFlushFrequency')
			if p is not None:
				LmConf.NotificationFlushFrequency = int(p)
			p = aConfig.get('NotificationFilePath')
			if p is not None:
				LmConf.NotificationFilePath = p
			p = aConfig.get('email')
			if p is not None:
				LmConf.Email = p
			p = aConfig.get('CSV Delimiter')
			if p is not None:
				LmConf.CsvDelimiter = str(p)
				if len(LmConf.CsvDelimiter):
					LmConf.CsvDelimiter = LmConf.CsvDelimiter[0]
				else:
					LmConf.CsvDelimiter = DCFG_CSV_DELIMITER
			p = aConfig.get('Timeout Margin')
			if p is not None:
				LmConf.TimeoutMargin = int(p)
				if LmConf.TimeoutMargin < 0:
					LmConf.TimeoutMargin = 0
			p = aConfig.get('Prevent Sleep')
			if p is not None:
				LmConf.PreventSleep = bool(p)
			p = aConfig.get('Save Passwords')
			if p is not None:
				LmConf.SavePasswords = bool(p)

		if aConfigFile is not None:
			aConfigFile.close()

		if aDirtyConfig:
			LmConf.save()

		LmConf.apply()

		return True


	### Load key file, creating one if not present, returns False if fails
	@staticmethod
	def loadKey():
		aConfigPath = LmConf.getConfigDirectory()
		aKeyFile = None
		aKey = None
		aKeyFilePath = os.path.join(aConfigPath, KEY_FILE)

		# Get unique hardware key
		aHWKey = GetHardwareKey()

		# Read file if it exists
		LmTools.log_debug(1, 'Reading key file in', aKeyFilePath)
		try:
			aKeyFile = open(aKeyFilePath, 'rb')
			aKey = aKeyFile.read()
			aKeyFile.close()
		except OSError:
			LmTools.error('No key file, creating one.')
			aKey = None
		except BaseException as e:
			LmTools.error(str(e))
			LmTools.display_error(mx('Cannot read key file.', 'keyFileErr'))
			if aKeyFile is not None:
				aKeyFile.close()
				return False
		else:
			# Decrypt key to get secret
			try:
				LmConf.Secret = Fernet(aHWKey.encode('utf-8')).decrypt(aKey).decode('utf-8')
			except:
				LmTools.error('Invalid key file, recreating it.')
			else:
				return True

		# Create config directory if doesn't exist
		if not os.path.isdir(aConfigPath):
			LmTools.log_debug(1, 'Creating config directory', aConfigPath)
			try:
				os.makedirs(aConfigPath)
			except BaseException as e:
				LmTools.error(f'Cannot create configuration folder. Error: {e}')
				LmTools.display_error(mx('Cannot create configuration folder.', 'configFolderErr'))
				return False

		# Create key file
		LmConf.Secret = Fernet.generate_key().decode()
		aKey = Fernet(aHWKey.encode('utf-8')).encrypt(LmConf.Secret.encode('utf-8'))
		LmTools.log_debug(1, 'Creating key file', aKeyFilePath)
		try:
			with open(aKeyFilePath, 'wb') as aKeyFile:
				aKeyFile.write(aKey)
		except BaseException as e:
			LmTools.error(f'Cannot save key file. Error: {e}')

		return True


	### Apply immediate actions derived from configuration
	@staticmethod
	def apply():
		LmLanguages.set_language(LmConf.Language)
		LmSession.set_timeout_margin(LmConf.TimeoutMargin)


	### Apply decoupled saved values after application auto restarts following pref's change
	@staticmethod
	def applySavedPrefs():
		LmConf.RealtimeWifiStats = LmConf.RealtimeWifiStats_save


	### Select a profile in the profile list depending on default parameters
	#   Returns a tuple of 2 booleans: 1/ False if user cancels, 2/ True if config needs to be saved
	@staticmethod
	def selectProfile():
		# First search for a default profile
		LmConf.CurrProfile = next((p for p in LmConf.Profiles if p['Default']), None)

		# Find dynamically if no default, take the first
		if LmConf.CurrProfile is None:
			# First collect reachable profiles and those matching Livebox's MAC address
			LmTools.mouse_cursor_busy()
			for p in LmConf.Profiles:
				aLiveboxMAC = LiveboxInfoApi.get_livebox_mac_nosign(p.get('Livebox URL'))
				if (aLiveboxMAC is not None) and (aLiveboxMAC == p.get('Livebox MacAddr')):
					LmConf.CurrProfile = p
					break
			LmTools.mouse_cursor_normal()

		# If no match/default found or if Ctrl key pressed, ask for it
		aModifiers = QtGui.QGuiApplication.queryKeyboardModifiers()
		aDirtyConfig = False
		if (LmConf.CurrProfile is None) or (aModifiers == QtCore.Qt.KeyboardModifier.ControlModifier):
			r = LmConf.askProfile()
			if r == 0:
				return False, False
			elif r == 2:
				if LmConf.createProfile():
					aDirtyConfig = True
				else:
					return False, False

		if LmConf.CurrProfile is not None:
			LmConf.assignProfile()

		return True, aDirtyConfig


	### Ask user to choose a profile, returns 0 if user cancels, 1 if one selected, 2 if need to create a new one
	@staticmethod
	def askProfile():
		if len(LmConf.Profiles) == 0:
			return 1

		from LiveboxMonitor.dlg.LmSelectProfile import SelectProfileDialog

		aSelectProfileDialog = SelectProfileDialog()
		if aSelectProfileDialog.exec():
			if aSelectProfileDialog.do_create_profile():
				return 2
			LmConf.CurrProfile = LmConf.Profiles[aSelectProfileDialog.profile_index()]
			return 1
		return 0


	### Create a new profile, return False is user cancelled
	#staticmethod
	def createProfile():
		# Loop until finding a unique name or user cancels
		while True:
			aName, aOK = QtWidgets.QInputDialog.getText(None, lx('Create Profile'), lx('Profile name:'))
			if aOK:
				q = next((p for p in LmConf.Profiles if p['Name'] == aName), None)
				if q is None:
					break
				else:
					LmTools.display_error(mx('This name is already used.', 'profileNameErr'))
			else:
				return False

		# Create a new profile with default values
		p = {}
		p['Name'] = aName
		p['Livebox URL'] = DCFG_LIVEBOX_URL
		p['Livebox User'] = DCFG_LIVEBOX_USER
		p['Filter Devices'] = DCFG_FILTER_DEVICES
		p['MacAddr Table File'] = DCFG_MACADDR_TABLE_FILE
		p['Default'] = False
		LmConf.Profiles.append(p)
		LmConf.CurrProfile = p

		return True


	### Assign parameters depending on current profile
	@staticmethod
	def assignProfile():
		LmConf.LiveboxURL = LmTools.clean_url(LmConf.CurrProfile.get('Livebox URL', DCFG_LIVEBOX_URL))
		LmConf.LiveboxUser = LmConf.CurrProfile.get('Livebox User', DCFG_LIVEBOX_USER)

		p = LmConf.CurrProfile.get('Livebox Password')
		if p is not None:
			try:
				LmConf.LiveboxPassword = Fernet(LmConf.Secret.encode('utf-8')).decrypt(p.encode('utf-8')).decode('utf-8')
			except:
				LmTools.error('Cannot decrypt Livebox password.')
				LmConf.LiveboxPassword = DCFG_LIVEBOX_PASSWORD
		else:
			LmConf.LiveboxPassword = DCFG_LIVEBOX_PASSWORD

		LmConf.LiveboxMAC = LmConf.CurrProfile.get('Livebox MacAddr', '')
		LmConf.FilterDevices = LmConf.CurrProfile.get('Filter Devices', DCFG_FILTER_DEVICES)
		LmConf.MacAddrTableFile = LmConf.CurrProfile.get('MacAddr Table File', DCFG_MACADDR_TABLE_FILE)
		if len(LmConf.MacAddrTableFile) == 0:
			LmConf.MacAddrTableFile = DCFG_MACADDR_TABLE_FILE


	### Adapt config format to latest version, returns True is changes were done
	@staticmethod
	def convert(ioConfig):
		aDirtyConfig = False
		aVersion = ioConfig.get('Version')

		if aVersion is None:
			aVersion = LmConf.convertFor096(ioConfig)
			aDirtyConfig = True

		if aVersion <= 0x010400:
			aVersion = LmConf.convertfor150(ioConfig)

		return aDirtyConfig


	### Adapt config format to 0.9.6 version, return corresponding version number
	@staticmethod
	def convertFor096(ioConfig):
		v = 0x000906
		ioConfig['Version'] = v

		# Convert Livebox parameters into main profile
		aProfiles = []
		aMainProfile = {}

		aMainProfile['Name'] = lx('Main')
		aMainProfile['Livebox URL'] = ioConfig.get('Livebox URL', DCFG_LIVEBOX_URL)
		aMainProfile['Livebox User'] = ioConfig.get('Livebox User', DCFG_LIVEBOX_USER)
		aMainProfile['Livebox Password'] = ioConfig.get('Livebox Password', DCFG_LIVEBOX_PASSWORD)
		aMainProfile['Filter Devices'] = ioConfig.get('Filter Devices', DCFG_FILTER_DEVICES)
		aMainProfile['MacAddr Table File'] = ioConfig.get('MacAddr Table File', DCFG_MACADDR_TABLE_FILE)
		aMainProfile['Default'] = True
		aProfiles.append(aMainProfile)

		ioConfig['Profiles'] = aProfiles

		return v


	### Adapt config format to 1.5.0 version, return corresponding version number
	@staticmethod
	def convertfor150(ioConfig):
		v = 0x010500
		ioConfig['Version'] = v

		# Remove all profile passwords following security key management evolution
		aProfiles = ioConfig.get('Profiles')
		if aProfiles is not None:
			for p in aProfiles:
				p['Livebox Password'] = None

		# Remove all repeaters passwords following security key management evolution
		aRepeaters = ioConfig.get('Repeaters')
		if aRepeaters is not None:
			for r in aRepeaters:
				aRepeaters[r]['Password'] = None

		return v


	### Save configuration file
	@staticmethod
	def save():
		aConfigPath = LmConf.getConfigDirectory()

		# Create config directory if doesn't exist
		if not os.path.isdir(aConfigPath):
			LmTools.log_debug(1, 'Creating config directory', aConfigPath)
			try:
				os.makedirs(aConfigPath)
			except BaseException as e:
				LmTools.error(f'Cannot create configuration folder. Error: {e}')
				return

		aConfigFilePath = os.path.join(aConfigPath, CONFIG_FILE)
		LmTools.log_debug(1, 'Saving configuration in', aConfigFilePath)
		try:
			with open(aConfigFilePath, 'w') as aConfigFile:
				aConfig = {}
				aConfig['Version'] = __build__
				if LmConf.CurrProfile is None:
					LmConf.CurrProfile = {}
					LmConf.CurrProfile['Name'] = lx('Main')
					LmConf.CurrProfile['Default'] = True
				LmConf.CurrProfile['Livebox URL'] = LmConf.LiveboxURL
				LmConf.CurrProfile['Livebox User'] = LmConf.LiveboxUser
				if LmConf.SavePasswords:
					LmConf.CurrProfile['Livebox Password'] = Fernet(LmConf.Secret.encode('utf-8')).encrypt(LmConf.LiveboxPassword.encode('utf-8')).decode('utf-8')
				else:
					LmConf.CurrProfile['Livebox Password'] = None
				LmConf.CurrProfile['Livebox MacAddr'] = LmConf.LiveboxMAC
				LmConf.CurrProfile['Filter Devices'] = LmConf.FilterDevices
				LmConf.CurrProfile['MacAddr Table File'] = LmConf.MacAddrTableFile
				if LmConf.Profiles is None:
					LmConf.Profiles = []
					LmConf.Profiles.append(LmConf.CurrProfile)
				aConfig['Profiles'] = LmConf.Profiles
				aConfig['Language'] = LmConf.Language
				aConfig['Tooltips'] = LmConf.Tooltips
				aConfig['Stats Frequency'] = LmConf.StatsFrequency
				aConfig['MacAddr API Key'] = LmConf.MacAddrApiKey
				aConfig['CallFilter API Key'] = LmConf.CallFilterApiKey
				aConfig['Phone Code'] = LmConf.PhoneCode
				aConfig['List Header Height'] = LmConf.ListHeaderHeight
				aConfig['List Header Font Size'] = LmConf.ListHeaderFontSize
				aConfig['List Line Height'] = LmConf.ListLineHeight
				aConfig['List Line Font Size'] = LmConf.ListLineFontSize
				aConfig['Realtime Wifi Stats'] = LmConf.RealtimeWifiStats_save
				aConfig['Native UI Style'] = LmConf.NativeUIStyle
				aConfig['Log Level'] = LmConf.LogLevel
				aConfig['No Release Warning'] = LmConf.NoReleaseWarning
				aConfig['Repeaters'] = LmConf.Repeaters
				aConfig['Graph'] = LmConf.Graph
				aConfig['Tabs'] = LmConf.Tabs
				aConfig['NotificationRules'] = LmConf.NotificationRules
				aConfig['NotificationFlushFrequency'] = LmConf.NotificationFlushFrequency
				aConfig['NotificationFilePath'] = LmConf.NotificationFilePath
				aConfig['email'] = LmConf.Email
				aConfig['CSV Delimiter'] = LmConf.CsvDelimiter
				aConfig['Timeout Margin'] = LmConf.TimeoutMargin
				aConfig['Prevent Sleep'] = LmConf.PreventSleep
				aConfig['Save Passwords'] = LmConf.SavePasswords
				json.dump(aConfig, aConfigFile, indent = 4)
		except BaseException as e:
			LmTools.error(f'Cannot save configuration file. Error: {e}')


	### Set Livebox password
	@staticmethod
	def setLiveboxURL(iURL):
		LmConf.LiveboxURL = iURL
		LmConf.save()


	### Set Livebox password
	@staticmethod
	def setLiveboxUserPassword(iUser, iPassword):
		LmConf.LiveboxUser = iUser
		LmConf.LiveboxPassword = iPassword
		LmConf.save()


	### Set Livebox MAC address
	@staticmethod
	def setLiveboxMAC(iMacAddr):
		if LmConf.LiveboxMAC != iMacAddr:
			LmConf.LiveboxMAC = iMacAddr
			LmConf.save()


	### Set log level
	@staticmethod
	def setLogLevel(iLevel):
		if iLevel < 0:
			iLevel = 0
		elif iLevel > 2:
			iLevel = 2
		LmConf.LogLevel = iLevel
		LmTools.set_verbosity(iLevel)
		LmConf.save()


	### Get password of a repeater given its MAC address
	@staticmethod
	def getRepeaterUserPassword(iMacAddr):
		# First look up for a specific password
		if LmConf.Repeaters is not None:
			aRepeaterConf = LmConf.Repeaters.get(iMacAddr, None)
			if aRepeaterConf is not None:
				aUser = aRepeaterConf.get('User', '')
				p = aRepeaterConf.get('Password')
				if p is None:
					aPassword = LmConf.LiveboxPassword
				else:
					try:
						aPassword = Fernet(LmConf.Secret.encode('utf-8')).decrypt(p.encode('utf-8')).decode('utf-8')
					except:
						LmTools.error('Cannot decrypt repeater password.')
						aPassword = LmConf.LiveboxPassword
				return aUser, aPassword

		# Defaut to Livebox user & password
		return LmConf.LiveboxUser, LmConf.LiveboxPassword


	### Set password of a repeater given its MAC address
	@staticmethod
	def setRepeaterPassword(iMacAddr, iPassword):
		# Init repeater conf root if not present
		if LmConf.Repeaters is None:
			LmConf.Repeaters = {}

		# Retrieve conf of given repeater, init it if not present
		aRepeaterConf = LmConf.Repeaters.get(iMacAddr, None)
		if aRepeaterConf is None:
			aRepeaterConf = {}
			LmConf.Repeaters[iMacAddr] = aRepeaterConf

		# Init user name if not present
		aUser = aRepeaterConf.get('User')
		if aUser is None:
			aRepeaterConf['User'] = LmConf.LiveboxUser

		# Setup password
		if LmConf.SavePasswords:
			aRepeaterConf['Password'] = Fernet(LmConf.Secret.encode('utf-8')).encrypt(iPassword.encode('utf-8')).decode('utf-8')
		else:
			aRepeaterConf['Password'] = None

		# Save to config file
		LmConf.save()


	### Load MAC address table
	@staticmethod
	def loadMacAddrTable():
		aMacAddrTableFilePath = os.path.join(LmConf.getConfigDirectory(), LmConf.MacAddrTableFile)
		try:
			with open(aMacAddrTableFilePath) as aMacTableFile:
				LmConf.MacAddrTable = json.load(aMacTableFile)
		except OSError:		# No file
			LmConf.MacAddrTable = {}
		except BaseException as e:
			LmTools.display_error(mx('Wrong {} file format, cannot use.', 'wrongMacFile').format(LmConf.MacAddrTableFile))
			LmConf.MacAddrTable = {}


	### Save MAC address table
	@staticmethod
	def saveMacAddrTable():
		aConfigPath = LmConf.getConfigDirectory()

		# Create config directory if doesn't exist
		if not os.path.exists(aConfigPath):
			try:
				os.makedirs(aConfigPath)
			except BaseException as e:
				LmTools.error(f'Cannot create configuration folder. Error: {e}')
				return

		aMacAddrTableFilePath = os.path.join(aConfigPath, LmConf.MacAddrTableFile)
		try:
			with open(aMacAddrTableFilePath, 'w') as aMacTableFile:
				json.dump(LmConf.MacAddrTable, aMacTableFile, indent = 4)
		except BaseException as e:
			LmTools.error(f'Cannot save MacAddress file. Error: {e}')


	### Load spam calls table
	@staticmethod
	def loadSpamCallsTable():
		aSpamCallsTableFilePath = os.path.join(LmConf.getConfigDirectory(), SPAMCALLS_FILE)
		try:
			with open(aSpamCallsTableFilePath) as f:
				t = json.load(f)
				if type(t).__name__ == 'list':
					LmConf.SpamCallsTable = t
				else:
					LmTools.display_error(mx('Wrong {} file format, cannot use.', 'wrongSpamCallsFile').format(SPAMCALLS_FILE))
					LmConf.SpamCallsTable = []
		except OSError:		# No file
			LmConf.SpamCallsTable = []
		except BaseException as e:
			LmTools.display_error(mx('Wrong {} file format, cannot use.', 'wrongSpamCallsFile').format(SPAMCALLS_FILE))
			LmConf.SpamCallsTable = []


	### Declare a phone nb as spam
	@staticmethod
	def setSpamCall(iPhoneNb):
		if iPhoneNb not in LmConf.SpamCallsTable:
			LmConf.SpamCallsTable.append(iPhoneNb)
			LmConf.saveSpamCallsTable()


	### Undeclare a phone nb as spam
	@staticmethod
	def unsetSpamCall(iPhoneNb):
		if iPhoneNb in LmConf.SpamCallsTable:
			LmConf.SpamCallsTable.remove(iPhoneNb)
			LmConf.saveSpamCallsTable()


	### Save spam calls table
	@staticmethod
	def saveSpamCallsTable():
		aConfigPath = LmConf.getConfigDirectory()

		# Create config directory if doesn't exist
		if not os.path.exists(aConfigPath):
			try:
				os.makedirs(aConfigPath)
			except BaseException as e:
				LmTools.error(f'Cannot create configuration folder. Error: {e}')
				return

		aSpamCallsTableFilePath = os.path.join(aConfigPath, SPAMCALLS_FILE)
		try:
			with open(aSpamCallsTableFilePath, 'w') as f:
				json.dump(LmConf.SpamCallsTable, f, indent = 4)
		except BaseException as e:
			LmTools.error(f'Cannot save spam calls file. Error: {e}')


	### Set native run
	@staticmethod
	def setNativeRun(iNativeRun):
		LmConf.NativeRun = iNativeRun


	### Determine config files directory
	@staticmethod
	def getConfigDirectory():
		if hasattr(sys, 'frozen') or not LmConf.NativeRun:
			# If program is built with PyInstaller, use standard OS dirs
			aPlatform =  platform.system()
			if aPlatform == 'Windows':
				return os.path.join(os.environ['APPDATA'], 'LiveboxMonitor')
			elif aPlatform == 'Darwin':
				return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'LiveboxMonitor')
			else:
				return os.path.join(os.path.expanduser('~'), '.config', 'LiveboxMonitor')
		else:
			# If program is Python script mode, use local dir
			return '.'


	### Get a device icon from cache file
	@staticmethod
	def getDeviceIconCache(iDevice, iLBSoftVersion):
		aIconPixMap = None
		aIconDirPath = os.path.join(LmConf.getConfigDirectory(), LIVEBOX_CACHE_DIR + iLBSoftVersion, LIVEBOX_ICON_CACHE_DIR)
		aIconFilePath = os.path.join(aIconDirPath, iDevice['Icon'])
		if os.path.isfile(aIconFilePath):
			aIconPixMap = QtGui.QPixmap()
			if not aIconPixMap.load(aIconFilePath):
				aIconPixMap = None
				LmTools.error(f'Cannot load device icon cache file {aIconFilePath}. Cache file will be recreated.')
		return aIconPixMap


	### Set a device icon to cache file
	@staticmethod
	def setDeviceIconCache(iDevice, iLBSoftVersion, iContent):
		aIconDirPath = os.path.join(LmConf.getConfigDirectory(), LIVEBOX_CACHE_DIR + iLBSoftVersion, LIVEBOX_ICON_CACHE_DIR)
		aIconFilePath = os.path.join(aIconDirPath, iDevice['Icon'])

		# Create icon cache directory if doesn't exist
		if not os.path.isdir(aIconDirPath):
			try:
				os.makedirs(aIconDirPath)
			except BaseException as e:
				LmTools.error(f'Cannot create icon cache folder {aIconDirPath}. Error: {e}')
				return

		# Create and save icon cache file
		try:
			with open(aIconFilePath, 'wb') as aIconFile:
				aIconFile.write(iContent)
		except BaseException as e:
			LmTools.error(f'Cannot save icon cache file {aIconFilePath}. Error: {e}')


	### Get a device icon
	@staticmethod
	def getDeviceIcon(iDevice, iLBSoftVersion):
		if LmConf.AllDeviceIconsLoaded:
			return iDevice['PixMap']
		else:
			aIconPixMap = iDevice.get('PixMap', None)

			# First try to get icon from local cache
			if aIconPixMap is None:
				aIconPixMap = LmConf.getDeviceIconCache(iDevice, iLBSoftVersion)

			# Ultimately load the icon from Livebox URL
			if aIconPixMap is None:
				aIconPixMap = QtGui.QPixmap()
				aStoreInCache = False
				try:
					aIconData = requests.get(LmConf.LiveboxURL + ICON_URL + iDevice['Icon'],
											 timeout = DEFAULT_TIMEOUT + LmConf.TimeoutMargin,
											 verify = LmConf.LiveboxURL.startswith('http://'))
					if aIconPixMap.loadFromData(aIconData.content):
						aStoreInCache = True
					else:
						LmTools.error(f'Cannot load device icon {iDevice["Icon"]}.')
				except requests.exceptions.Timeout as e:
					LmTools.error(f'Device icon {iDevice["Icon"]} request timeout error: {e}.')
				except BaseException as e:
					LmTools.error(f'{e}. Cannot request device icon {iDevice["Icon"]}.')

				# If successfully loaded, try to store in local cache file for faster further loads
				if aStoreInCache:
					LmConf.setDeviceIconCache(iDevice, iLBSoftVersion, aIconData.content)

			iDevice['PixMap'] = aIconPixMap
			return aIconPixMap


	### Load all device icons
	@staticmethod
	def loadDeviceIcons(iLBSoftVersion):
		if not LmConf.AllDeviceIconsLoaded:
			for d in DEVICE_TYPES:
				LmConf.getDeviceIcon(d, iLBSoftVersion)

			LmConf.AllDeviceIconsLoaded = True


	### Load custom device icons
	@staticmethod
	def loadCustomDeviceIcons():
		global DEVICE_TYPES

		# Get custom icon directory path
		aCustomIconDirPath = os.path.join(LmConf.getConfigDirectory(), CUSTOM_ICON_DIR)
		if not os.path.isdir(aCustomIconDirPath):
			return

		# Iterate over all files in the custom icon directory
		aSortDeviceTypes = False
		for f in os.listdir(aCustomIconDirPath):
			aIconFileName = os.fsdecode(f)
			if aIconFileName.endswith('.png'):
				aIconFilePath = os.path.join(aCustomIconDirPath, aIconFileName)
				aIconPixMap = QtGui.QPixmap()
				if aIconPixMap.load(aIconFilePath):
					# Search if device icon name is already referenced
					aCreateDeviceEntry = True
					for d in DEVICE_TYPES:
						if d['Icon'] == aIconFileName:
							aCreateDeviceEntry = False
							d['PixMap'] = aIconPixMap

					# Search if device name is already referenced as key
					aDeviceName = os.path.splitext(aIconFileName)[0]
					if aCreateDeviceEntry:
						for d in DEVICE_TYPES:
							if d['Key'] == aDeviceName:
								aCreateDeviceEntry = False
								d['Icon'] = aIconFileName
								d['PixMap'] = aIconPixMap
								break

					# If doesn't exit, create it
					if aCreateDeviceEntry:
						aDevice = {}
						aDevice['Key'] = aDeviceName
						aDevice['Name'] = aDeviceName
						aDevice['Icon'] = aIconFileName
						aDevice['PixMap'] = aIconPixMap
						DEVICE_TYPES.append(aDevice)
						aSortDeviceTypes = True
				else:
					LmTools.error(f'Cannot load custom device icon {aIconFilePath}.')

		# Resort device type list if required
		if aSortDeviceTypes:
			DEVICE_TYPES = sorted(DEVICE_TYPES, key = lambda x: x['Name'])


	### Load, check and return email configuration
	@staticmethod
	def loadEmailSetup():
		if LmConf.Email is None:
			return None

		c = LmConf.Email
		e = {}

		e['From'] = c.get('From', '')
		e['To'] = c.get('To', '')
		e['Prefix'] = c.get('Prefix', '[LiveboxMonitor] ')
		e['Server'] = c.get('Server', '')
		e['Port'] = c.get('Port', 587)
		e['TLS'] = c.get('TLS', True)
		e['SSL'] = c.get('SSL', False)
		e['Authentication'] = c.get('Authentication', True)
		e['User'] = c.get('User', '')

		aPassword = ''
		p = c.get('Password')
		if p is not None:
			try:
				aPassword = Fernet(LmConf.Secret.encode('utf-8')).decrypt(p.encode('utf-8')).decode('utf-8')
			except:
				LmTools.error('Cannot decrypt email password.')
		e['Password'] = aPassword

		return e


	### Set email configuration
	@staticmethod
	def setEmailSetup(iEmailSetup):
		p = iEmailSetup['Password']
		try:
			iEmailSetup['Password'] = Fernet(LmConf.Secret.encode('utf-8')).encrypt(p.encode('utf-8')).decode('utf-8')
		except:
			LmTools.error('Cannot encrypt email password.')
			iEmailSetup['Password'] = ''
		LmConf.Email = iEmailSetup
