### Livebox Monitor Configuration module ###

import sys
import os
import platform
import requests
import json
import base64

from enum import IntEnum

from PyQt6 import QtGui
from PyQt6 import QtCore
from PyQt6 import QtWidgets
from cryptography.fernet import Fernet

from src import LmTools

from __init__ import __build__



# ################################ VARS & DEFS ################################

# Config file name
CONFIG_FILE = 'Config.txt'

# Config default
DCFG_LIVEBOX_URL = 'http://livebox.home/'
DCFG_LIVEBOX_USER = 'admin'
DCFG_LIVEBOX_PASSWORD = ''
DCFG_FILTER_DEVICES = True
DCFG_MACADDR_TABLE_FILE = 'MacAddrTable.txt'
DCFG_MACADDR_API_KEY = ''
DCFG_PHONE_CODE = '33'
DCFG_LIST_HEADER_HEIGHT = 25
DCFG_LIST_HEADER_FONT_SIZE = 0
DCFG_LIST_LINE_HEIGHT = 30
DCFG_LIST_LINE_FONT_SIZE = 0
DCFG_LOG_LEVEL = 0
DCFG_REPEATERS = None

# Static config
ICON_URL = 'assets/common/images/app_conf/'
SECRET = 'mIohg_8Q0pkQCA7x3dOqNTeADYPfcMhJZ4ujomNLNro='

# Graphical config
WIND_HEIGHT_ADJUST = 0		# Space to add to a window height to respect a table wished height inside
DIAG_HEIGHT_ADJUST = 0		# Space to add to a dialog height to respect a table wished height inside
TABLE_ADJUST = 4			# Space to add to a table height to respect a table wished height
SCROLL_BAR_ADJUST = 0		# Space to add to last table col to give room for the scroll bar
LIST_HEADER_FONT_SIZE = 0	# 0 = default system font, value can be overriden by LmConf.ListHeaderFontSize
LIST_HEADER_FONT = None
LIST_LINE_FONT_SIZE = 0		# 0 = default system font, value can be overriden by LmConf.ListLineFontSize
LIST_LINE_FONT = None
LIST_STYLESHEET = ''
LIST_HEADER_STYLESHEET = ''

# Interfaces
NET_INTF = []

# LB5 Interfaces
NET_INTF_LB5 = [
	{ 'Key': 'veip0',    'Name': 'Fiber',        'Type': 'ont', 'SwapStats': False },
	{ 'Key': 'bridge',   'Name': 'LAN',          'Type': 'lan', 'SwapStats': True  },
	{ 'Key': 'eth0',     'Name': 'Ethernet 1',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'eth1',     'Name': 'Ethernet 2',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'eth2',     'Name': 'Ethernet 3',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'eth3',     'Name': 'Ethernet 4',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'wl0',      'Name': 'Wifi 2.4GHz',  'Type': 'wif', 'SwapStats': True  },
	{ 'Key': 'eth4',     'Name': 'Wifi 5GHz',    'Type': 'wif', 'SwapStats': True  },
	{ 'Key': 'wlguest2', 'Name': 'Guest 2.4GHz', 'Type': 'wig', 'SwapStats': True  },
	{ 'Key': 'wlguest5', 'Name': 'Guest 5GHz',   'Type': 'wig', 'SwapStats': True  }
]

# LB6 Interfaces
NET_INTF_LB6 = [
	{ 'Key': 'veip0',        'Name': 'Fiber',        'Type': 'ont', 'SwapStats': False },
	{ 'Key': 'bridge',       'Name': 'LAN',          'Type': 'lan', 'SwapStats': True  },
	{ 'Key': 'ETH1',         'Name': 'Ethernet 1',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'ETH2',         'Name': 'Ethernet 2',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'ETH3',         'Name': 'Ethernet 3',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'ETH4',         'Name': 'Ethernet 4',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'ETH0',         'Name': 'Ether 2.5G',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'vap2g0priv0',  'Name': 'Wifi 2.4GHz',  'Type': 'wif', 'SwapStats': True  },
	{ 'Key': 'vap5g0priv0',  'Name': 'Wifi 5GHz',    'Type': 'wif', 'SwapStats': True  },
	{ 'Key': 'vap6g0priv0',  'Name': 'Wifi 6GHz',    'Type': 'wif', 'SwapStats': True  },
	{ 'Key': 'vap2g0guest0', 'Name': 'Guest 2.4GHz', 'Type': 'wig', 'SwapStats': True  },
	{ 'Key': 'vap5g0guest0', 'Name': 'Guest 5GHz',   'Type': 'wig', 'SwapStats': True  }
]

# Interface name mapping
INTF_NAME_MAP = []

# LB5 Interface name mapping
INTF_NAME_MAP_LB5 = {
	"Livebox":  {"eth0":"Eth1", "eth1":"Eth2", "eth2":"Eth3", "eth3":"Eth4"},
	"Repeater": {"eth0":"Eth1", "eth1":"Eth2"}
}

# LB6 Interface name mapping
INTF_NAME_MAP_LB6 = {
	"Livebox":  {"eth0":"Eth4", "eth1":"Eth3", "eth2":"Eth2", "eth3":"Eth1", "eth4":"Eth 2.5G"},
	"Repeater": {"eth0":"Eth1", "eth1":"Eth2"}
}

# Device types & icons
DEVICE_TYPES = [
	{ 'Key': 'Unknown',                     'Name': 'Unknown',                    'Icon': 'e_default_device.png' },
	{ 'Key': 'AC Outlet',                   'Name': 'AC Outlet',                  'Icon': 'e_smart_plug.png' },
	{ 'Key': 'Acces Point',                 'Name': 'Acces Point',                'Icon': 'e_pointacceswifi.png' },
	{ 'Key': 'Airbox',                      'Name': 'Airbox',                     'Icon': 'e_airbox_gen.png' },
	{ 'Key': 'Apple AirPort',               'Name': 'Apple AirPort',              'Icon': 'e_apple_express.png' },
	{ 'Key': 'Apple AirPort Time Capsule',  'Name': 'Apple AirPort Time Capsule', 'Icon': 'e_apple_extreme_capsule.png' },
	{ 'Key': 'Apple Time Capsule',          'Name': 'Apple Time Capsule',         'Icon': 'e_apple_extreme_capsule.png' },
	{ 'Key': 'Apple TV',                    'Name': 'Apple TV',                   'Icon': 'e_apple_tv.png' },
	{ 'Key': 'Chromecast',                  'Name': 'Chromecast',                 'Icon': 'e_chromecast.png' },
	{ 'Key': 'Desktop',                     'Name': 'Computer',                   'Icon': 'e_ordibureau.png' },
	{ 'Key': 'Desktop Linux',               'Name': 'Computer (Linux)',           'Icon': 'e_ordibureau_Linux.png' },
	{ 'Key': 'Desktop iOS',                 'Name': 'Computer (MacOS)',           'Icon': 'e_ordibureau_ios.png' },
	{ 'Key': 'Desktop Windows',             'Name': 'Computer (Windows)',         'Icon': 'e_ordibureau_windows.png' },
	{ 'Key': 'Game Console',                'Name': 'Console',                    'Icon': 'e_consolejeux.png' },
	{ 'Key': 'Dimmable Color Bulb',         'Name': 'Dimmer Light',               'Icon': 'e_smart_bulb.png' },
	{ 'Key': 'Djingo Speaker',              'Name': 'Djingo Speaker',             'Icon': 'e_djingospeaker.png' },   # Not (yet?) supported by LB5
	{ 'Key': 'Domestic Robot',              'Name': 'Domestic Robot',             'Icon': 'e_Homelive.png' },
	{ 'Key': 'Domino',                      'Name': 'Domino',                     'Icon': 'e_domino.png' },
	{ 'Key': 'Door Sensor',                 'Name': 'Door Sensor',                'Icon': 'e_door_sensor.png' },
	{ 'Key': 'ExtenderTV',                  'Name': 'Extender TV',                'Icon': 'e_liveplugsolo.png' },
	{ 'Key': 'ExtenderWiFiPlus',            'Name': 'Extender Wi-Fi Plus',        'Icon': 'e_pointacceswifi.png' },
	{ 'Key': 'Femtocell',                   'Name': 'Femtocell',                  'Icon': 'e_femtocell.png' },
	{ 'Key': 'Google OnHub',                'Name': 'Google OnHub',               'Icon': 'e_google_onhub.png' },
	{ 'Key': 'HiFi',                        'Name': 'HiFi',                       'Icon': 'e_enceinte_hifi.png' },
	{ 'Key': 'HomeLibrary',                 'Name': 'Home Library',               'Icon': 'e_homelibrary.png' },
	{ 'Key': 'HomeLive',                    'Name': 'Home Live',                  'Icon': 'e_Homelive.png' },
	{ 'Key': 'Homepoint',                   'Name': 'Home Point',                 'Icon': 'e_homepoint.png' },
	{ 'Key': 'IP Camera',                   'Name': 'IP Camera',                  'Icon': 'e_camera_ip.png' },
	{ 'Key': 'Laptop',                      'Name': 'Laptop',                     'Icon': 'e_ordiportable.png' },
	{ 'Key': 'Laptop iOS',                  'Name': 'Laptop (iOS)',               'Icon': 'e_ordiportable_ios.png' },
	{ 'Key': 'Laptop Linux',                'Name': 'Laptop (Linux)',             'Icon': 'e_ordiportable_Linux.png' },
	{ 'Key': 'Laptop Windows',              'Name': 'Laptop (Windows)',           'Icon': 'e_ordiportable_windows.png' },
	{ 'Key': 'leBloc',                      'Name': 'Le Bloc d\'Orange',          'Icon': 'e_leblocdorange.png' },
	{ 'Key': 'HomePlug',                    'Name': 'Liveplug',                   'Icon': 'e_liveplug_cpl.png' },
	{ 'Key': 'LivePlugWifi',                'Name': 'Liveplug solo Wi-Fi',        'Icon': 'e_liveplugsolo.png' },
	{ 'Key': 'WiFiExtender',                'Name': 'Liveplug Wi-Fi Extender',    'Icon': 'e_liveplug_extender.png' },
	{ 'Key': 'Liveradio',                   'Name': 'LiveRadio',                  'Icon': 'e_liveradio.png' },
	{ 'Key': 'Motion Sensor',               'Name': 'Motion Sensor',              'Icon': 'e_motion_sensor.png' },
	{ 'Key': 'Nas',                         'Name': 'NAS',                        'Icon': 'e_nas.png' },
	{ 'Key': 'Notebook',                    'Name': 'Notebook',                   'Icon': 'e_notebook.png' },
	{ 'Key': 'Notebook Linux',              'Name': 'Notebook (Linux)',           'Icon': 'e_notebook_Linux.png' },
	{ 'Key': 'Notebook Windows',            'Name': 'Notebook (Windows)',         'Icon': 'e_notebook_windows.png' },
	{ 'Key': 'Old Phone',                   'Name': 'Old Handset Phone',          'Icon': 'e_telephoneold.png' },
	{ 'Key': 'Phone',                       'Name': 'Phone',                      'Icon': 'e_telephonenew.png' },
	{ 'Key': 'Power Meter',                 'Name': 'Power Meter',                'Icon': 'e_smart_plug.png' },
	{ 'Key': 'Printer',                     'Name': 'Printer',                    'Icon': 'e_imprimante.png' },
	{ 'Key': 'Set-top Box',                 'Name': 'Set-top Box',                'Icon': 'e_decodeurTV.png' },
	{ 'Key': 'Set-top Box TV 4',            'Name': 'Set-top Box 4',              'Icon': 'e_decodeur_tv_4.png' },
	{ 'Key': 'Set-top Box TV Play',         'Name': 'Set-top Box Play',           'Icon': 'e_decodeur_tv_play.png' },
	{ 'Key': 'Set-top Box TV UHD',          'Name': 'Set-top Box UHD',            'Icon': 'e_decodeur_tv_uhd.png' },
	{ 'Key': 'Set-top Box TV Universal',    'Name': 'Set-top Box Universal',      'Icon': 'e_decodeur_tv_universel.png' },
	{ 'Key': 'Simple Button',               'Name': 'Simple Button',              'Icon': 'e_simple_button.png' },
	{ 'Key': 'Color Bulb',                  'Name': 'Smart Bulb',                 'Icon': 'e_smart_bulb.png' },
	{ 'Key': 'Smart Plug',                  'Name': 'Smart Plug',                 'Icon': 'e_smart_plug.png' },
	{ 'Key': 'Mobile',                      'Name': 'Smartphone',                 'Icon': 'e_mobile.png' },
	{ 'Key': 'Mobile Android',              'Name': 'Smartphone (Android)',       'Icon': 'e_mobile_android.png' },
	{ 'Key': 'Mobile iOS',                  'Name': 'Smartphone (iOS)',           'Icon': 'e_mobile_ios.png' },
	{ 'Key': 'Mobile Windows',              'Name': 'Smartphone (Windows)',       'Icon': 'e_mobile_windows.png' },
	{ 'Key': 'Smoke Detector',              'Name': 'Smoke Detector',             'Icon': 'e_sensorhome.png' },
	{ 'Key': 'Disk',                        'Name': 'Storage Device',             'Icon': 'e_periphstockage.png' },
	{ 'Key': 'Switch4',                     'Name': 'Switch (4 ports)',           'Icon': 'e_switch4.png' },
	{ 'Key': 'Switch8',                     'Name': 'Switch (8 ports)',           'Icon': 'e_switch8.png' },
	{ 'Key': 'Tablet',                      'Name': 'Tablet',                     'Icon': 'e_tablette.png' },
	{ 'Key': 'Tablet Android',              'Name': 'Tablet (Android)',           'Icon': 'e_tablette_android.png' },
	{ 'Key': 'Tablet iOS',                  'Name': 'Tablet (iOS)',               'Icon': 'e_tablette_ios.png' },
	{ 'Key': 'Tablet Windows',              'Name': 'Tablet (Windows)',           'Icon': 'e_tablette_windows.png' },
	{ 'Key': 'TV',                          'Name': 'TV',                         'Icon': 'e_TV.png' },
	{ 'Key': 'TVKey',                       'Name': 'TV Stick',                   'Icon': 'e_cletv.png' },
	{ 'Key': 'TVKey v2',                    'Name': 'TV Stick v2',                'Icon': 'e_cletv_v2.png' },
	{ 'Key': 'USBKey',                      'Name': 'USB Key',                    'Icon': 'e_cleusb.png' },
	{ 'Key': 'WiFi_Access_Point',           'Name': 'Wi-Fi Access Point',         'Icon': 'e_pointacceswifi.png' },
	{ 'Key': 'Window Sensor',               'Name': 'Window Sensor',              'Icon': 'e_door_sensor.png' },
	{ 'Key': 'Computer',                    'Name': 'Windows Computer',           'Icon': 'e_ordibureau_windows.png' },
	{ 'Key': 'SAH AP',                      'Name': 'Wi-Fi Repeater',             'Icon': 'e_pointacceswifi.png' },
	{ 'Key': 'repeteurwifi6',               'Name': 'Wi-Fi Repeater 6',           'Icon': 'e_pointacceswifi.png' }
]


# Tab indexes
class MonitorTab(IntEnum):
	DeviceList = 0
	LiveboxInfos = 1
	DeviceInfos = 2
	DeviceEvents = 3
	Phone = 4
	Actions = 5
	Repeaters = 6  # Index of first, and others incrementally



# ################################ Tools ################################

# Setting up application style depending on platform
def SetApplicationStyle():
	global WIND_HEIGHT_ADJUST
	global DIAG_HEIGHT_ADJUST
	global SCROLL_BAR_ADJUST
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
	if aPlatform == 'Windows':
		aStyle = 'Windows'
	elif aPlatform == 'Darwin':
		aStyle = 'macOS'

	if aStyle == 'Fusion':
		WIND_HEIGHT_ADJUST = 2
		DIAG_HEIGHT_ADJUST = -4
		TABLE_ADJUST = 4
		SCROLL_BAR_ADJUST = 0
		LIST_HEADER_FONT_SIZE = 12
		LIST_LINE_FONT_SIZE = 10
		LIST_STYLESHEET = 'color:black; background-color:#FAFAFA'
		LIST_HEADER_STYLESHEET = '''
			QHeaderView::section {
				border-width: 0px 0px 1px 0px;
				border-color: grey
			}
			'''
	elif aStyle == 'Windows':
		WIND_HEIGHT_ADJUST = 0
		DIAG_HEIGHT_ADJUST = 0
		TABLE_ADJUST = 4
		SCROLL_BAR_ADJUST = 0
		LIST_HEADER_FONT_SIZE = 0	# Let system default
		LIST_LINE_FONT_SIZE = 0		# Let system default
		LIST_STYLESHEET = 'color:black; background-color:#FAFAFA'
		LIST_HEADER_STYLESHEET = '''
			QHeaderView::section {
				border-width: 0px 0px 1px 0px;
				border-style: solid;
				border-color: grey
			}
			'''
	elif aStyle == 'macOS':
		WIND_HEIGHT_ADJUST = 4
		DIAG_HEIGHT_ADJUST = 30
		TABLE_ADJUST = 4
		SCROLL_BAR_ADJUST = 20
		LIST_HEADER_FONT_SIZE = 11
		LIST_LINE_FONT_SIZE = 10
		LIST_STYLESHEET = 'color:black; background-color:#F0F0F0; gridline-color:#FFFFFF'
		LIST_HEADER_STYLESHEET = '''
			QHeaderView::section {
				border-width: 0px 0px 1px 0px;
				border-color: grey
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


# Setting up table style depending on platform
def SetTableStyle(iTable):
	iTable.setGridStyle(QtCore.Qt.PenStyle.SolidLine)
	iTable.setStyleSheet(LIST_STYLESHEET)
	iTable.setFont(LIST_LINE_FONT)

	aHeader = iTable.horizontalHeader()
	aHeader.setStyleSheet(LIST_HEADER_STYLESHEET)
	aHeader.setFont(LIST_HEADER_FONT)
	aHeader.setFixedHeight(LmConf.ListHeaderHeight)

	aHeader = iTable.verticalHeader()
	aHeader.setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Fixed)
	aHeader.setDefaultSectionSize(LmConf.ListLineHeight)


# Compute table height based on nb of rows
def TableHeight(iRowNb):
	return LmConf.ListHeaderHeight + (LmConf.ListLineHeight * iRowNb) + TABLE_ADJUST


# Compute base height of a window based on nb of rows of a single table
def WindowHeight(iRowNb):
	return TableHeight(iRowNb) + WIND_HEIGHT_ADJUST


# Compute base height of a dialog based on nb of rows of a single table
def DialogHeight(iRowNb):
	return TableHeight(iRowNb) + DIAG_HEIGHT_ADJUST


# Setup configuration according to Livebox model
def SetLiveboxModel(iModel):
	global NET_INTF
	global INTF_NAME_MAP

	if iModel == 'LB6':
		NET_INTF = NET_INTF_LB6
		INTF_NAME_MAP = INTF_NAME_MAP_LB6
	else:
		NET_INTF = NET_INTF_LB5
		INTF_NAME_MAP = INTF_NAME_MAP_LB5



# ################################ Config Class ################################

class LmConf:
	Profiles = None
	CurrProfile = None
	LiveboxURL = DCFG_LIVEBOX_URL
	LiveboxUser = DCFG_LIVEBOX_USER
	LiveboxPassword = DCFG_LIVEBOX_PASSWORD
	FilterDevices = DCFG_FILTER_DEVICES
	MacAddrTableFile = DCFG_MACADDR_TABLE_FILE
	MacAddrTable = {}
	MacAddrApiKey = DCFG_MACADDR_API_KEY
	PhoneCode = DCFG_PHONE_CODE
	ListHeaderHeight = DCFG_LIST_HEADER_HEIGHT
	ListHeaderFontSize = DCFG_LIST_HEADER_FONT_SIZE
	ListLineHeight = DCFG_LIST_LINE_HEIGHT
	ListLineFontSize = DCFG_LIST_LINE_FONT_SIZE
	LogLevel = DCFG_LOG_LEVEL
	Repeaters = DCFG_REPEATERS
	AllDeviceIconsLoaded = False


	### Load configuration, if returns False the program aborts starting
	@staticmethod
	def load():
		aDirtyConfig = False
		aConfigFilePath = os.path.join(LmConf.getConfigDirectory(), CONFIG_FILE)
		try:
			with open(aConfigFilePath) as aConfigFile:
				aConfig = json.load(aConfigFile)
				aDirtyConfig = LmConf.convert(aConfig)
				p = aConfig.get('Profiles')
				if p is not None:
					LmConf.Profiles = p
					if not LmConf.selectProfile():
						return False
				if LmConf.CurrProfile is None:
					raise Exception('No profile detected')
				p = aConfig.get('MacAddr API Key')
				if p is not None:
					LmConf.MacAddrApiKey = p
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
				p = aConfig.get('Log Level')
				if p is not None:
					LmConf.LogLevel = int(p)
					if LmConf.LogLevel < 0:
						LmConf.LogLevel = 0
					elif LmConf.LogLevel > 2:
						LmConf.LogLevel = 2
					LmTools.SetVerbosity(LmConf.LogLevel)
				p = aConfig.get('Repeaters')
				if p is not None:
					LmConf.Repeaters = p
		except OSError:
			LmTools.Error('No configuration file, creating one.')
			aDirtyConfig = True
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			if LmTools.AskQuestion('Wrong {} file, fully reset it?'.format(CONFIG_FILE)):
				aDirtyConfig = True
			else:
				return False

		if aDirtyConfig:
			LmConf.save()
		return True


	### Select a profile in the profile list depending on default parameters
	#   Returns False if user cancels
	@staticmethod
	def selectProfile():
		# Search for first default profile
		LmConf.CurrProfile = next((p for p in LmConf.Profiles if p['Default']), None)

		# If no default found or if Ctrl key pressed, ask for it
		aModifiers = QtGui.QGuiApplication.queryKeyboardModifiers()
		if (LmConf.CurrProfile is None) or (aModifiers == QtCore.Qt.KeyboardModifier.ControlModifier):
			if not LmConf.askProfile():
				return False

		if LmConf.CurrProfile is not None:
			LmConf.assignProfile()

		return True


	### Ask user to choose a profile, returns False if user cancels
	@staticmethod
	def askProfile():
		if len(LmConf.Profiles) == 0:
			return True

		aProfileList = [p['Name'] for p in LmConf.Profiles]
		if LmConf.CurrProfile is None:
			aCurrentIndex = 0
		else:
			aCurrentIndex = aProfileList.index(LmConf.CurrProfile['Name'])

		aProfileName, aOK = QtWidgets.QInputDialog.getItem(None, 'Profile selection',
														   'Please select a profile to use:',
														   aProfileList, aCurrentIndex, False)
		if aOK:
			LmConf.CurrProfile = next((p for p in LmConf.Profiles if p['Name'] == aProfileName), None)
			return True
		return False


	### Assign parameters depending on current profile
	@staticmethod
	def assignProfile():
		LmConf.LiveboxURL = LmTools.cleanURL(LmConf.CurrProfile.get('Livebox URL', DCFG_LIVEBOX_URL))
		LmConf.LiveboxUser = LmConf.CurrProfile.get('Livebox User', DCFG_LIVEBOX_USER)

		p = LmConf.CurrProfile.get('Livebox Password')
		if p is not None:
			try:
				LmConf.LiveboxPassword = Fernet(SECRET.encode('utf-8')).decrypt(p.encode('utf-8')).decode('utf-8')
			except:
				LmConf.LiveboxPassword = DCFG_LIVEBOX_PASSWORD
		else:
			LmConf.LiveboxPassword = DCFG_LIVEBOX_PASSWORD

		LmConf.FilterDevices = LmConf.CurrProfile.get('Filter Devices', DCFG_FILTER_DEVICES)
		LmConf.MacAddrTableFile = LmConf.CurrProfile.get('MacAddr Table File', DCFG_MACADDR_TABLE_FILE)
		if len(LmConf.MacAddrTableFile) == 0:
			LmConf.MacAddrTableFile = DCFG_MACADDR_TABLE_FILE


	### Adapt config format to latest version, returns True is changes were done
	@staticmethod
	def convert(iConfig):
		aDirtyConfig = False
		aVersion = iConfig.get('Version')

		if aVersion is None:
			aVersion = LmConf.convertFor096(iConfig)
			aDirtyConfig = True

		return aDirtyConfig


	### Adapt config format to 0.9.6 version, return corresponding version number
	@staticmethod
	def convertFor096(iConfig):
		iConfig['Version'] = 0x000906

		# Convert Livebox parameters into main profile
		aProfiles = []
		aMainProfile = {}

		aMainProfile['Name'] = 'Main'
		aMainProfile['Livebox URL'] = iConfig.get('Livebox URL', DCFG_LIVEBOX_URL)
		aMainProfile['Livebox User'] = iConfig.get('Livebox User', DCFG_LIVEBOX_USER)
		aMainProfile['Livebox Password'] = iConfig.get('Livebox Password', DCFG_LIVEBOX_PASSWORD)
		aMainProfile['Filter Devices'] = iConfig.get('Filter Devices', DCFG_FILTER_DEVICES)
		aMainProfile['MacAddr Table File'] = iConfig.get('MacAddr Table File', DCFG_MACADDR_TABLE_FILE)
		aMainProfile['Default'] = True
		aProfiles.append(aMainProfile)

		iConfig['Profiles'] = aProfiles

		return 0x000906


	### Save configuration file
	@staticmethod
	def save():
		aConfigPath = LmConf.getConfigDirectory()

		# Create config directory if doesn't exist
		if not os.path.exists(aConfigPath):
			try:
				os.makedirs(aConfigPath)
			except BaseException as e:
				LmTools.Error('Cannot create configuration folder. Error: {}'.format(e))
				return

		aConfigFilePath = os.path.join(aConfigPath, CONFIG_FILE)
		try:
			with open(aConfigFilePath, 'w') as aConfigFile:
				aConfig = {}
				aConfig['Version'] = __build__
				if LmConf.CurrProfile is None:
					LmConf.CurrProfile = {}
					LmConf.CurrProfile['Name'] = 'Main'
					LmConf.CurrProfile['Default'] = True
				LmConf.CurrProfile['Livebox URL'] = LmConf.LiveboxURL
				LmConf.CurrProfile['Livebox User'] = LmConf.LiveboxUser
				LmConf.CurrProfile['Livebox Password'] = Fernet(SECRET.encode('utf-8')).encrypt(LmConf.LiveboxPassword.encode('utf-8')).decode('utf-8')
				LmConf.CurrProfile['Filter Devices'] = LmConf.FilterDevices
				LmConf.CurrProfile['MacAddr Table File'] = LmConf.MacAddrTableFile
				if LmConf.Profiles is None:
					LmConf.Profiles = []
					LmConf.Profiles.append(LmConf.CurrProfile)
				aConfig['Profiles'] = LmConf.Profiles
				aConfig['MacAddr API Key'] = LmConf.MacAddrApiKey
				aConfig['Phone Code'] = LmConf.PhoneCode
				aConfig['List Header Height'] = LmConf.ListHeaderHeight
				aConfig['List Header Font Size'] = LmConf.ListHeaderFontSize
				aConfig['List Line Height'] = LmConf.ListLineHeight
				aConfig['List Line Font Size'] = LmConf.ListLineFontSize
				aConfig['Log Level'] = LmConf.LogLevel
				aConfig['Repeaters'] = LmConf.Repeaters
				json.dump(aConfig, aConfigFile, indent = 4)
		except BaseException as e:
			LmTools.Error('Cannot save configuration file. Error: {}'.format(e))


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


	### Set log level
	@staticmethod
	def setLogLevel(iLevel):
		if iLevel < 0:
			iLevel = 0
		elif iLevel > 2:
			iLevel = 2
		LmConf.LogLevel = iLevel
		LmTools.SetVerbosity(iLevel)
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
						aPassword = Fernet(SECRET.encode('utf-8')).decrypt(p.encode('utf-8')).decode('utf-8')
					except:
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
		aRepeaterConf['Password'] = Fernet(SECRET.encode('utf-8')).encrypt(iPassword.encode('utf-8')).decode('utf-8')

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
			LmTools.DisplayError('Wrong {} file format, cannot use.'.format(LmConf.MacAddrTableFile))
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
				LmTools.Error('Cannot create configuration folder. Error: {}'.format(e))
				return

		aMacAddrTableFilePath = os.path.join(aConfigPath, LmConf.MacAddrTableFile)
		try:
			with open(aMacAddrTableFilePath, 'w') as aMacTableFile:
				json.dump(LmConf.MacAddrTable, aMacTableFile, indent = 4)
		except BaseException as e:
			LmTools.Error('Cannot save MacAddress file. Error: {}'.format(e))


	### Determine config files directory
	@staticmethod
	def getConfigDirectory():
		if hasattr(sys, 'frozen'):
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


	### Get a device icon
	@staticmethod
	def getDeviceIcon(iDevice):
		if LmConf.AllDeviceIconsLoaded:
			return iDevice['PixMap']
		else:
			aIconPixMap = iDevice.get('PixMap', None)
			if aIconPixMap is None:
				aIconPixMap = QtGui.QPixmap()

				try:
					aIconData = requests.get(LmConf.LiveboxURL + ICON_URL + iDevice['Icon'])
					if not aIconPixMap.loadFromData(aIconData.content):
						LmTools.Error('Cannot load device icon ' + iDevice['Icon'] + '.')
				except:
					LmTools.Error('Cannot request device icon ' + iDevice['Icon'] + '.')

				iDevice['PixMap'] = aIconPixMap

			return aIconPixMap


	### Load all device icons
	@staticmethod
	def loadDeviceIcons():
		if not LmConf.AllDeviceIconsLoaded:
			for d in DEVICE_TYPES:
				LmConf.getDeviceIcon(d)

			LmConf.AllDeviceIconsLoaded = True



# ############# Livebox connection dialog #############
class LiveboxCnxDialog(QtWidgets.QDialog):
	def __init__(self, iURL, iParent = None):
		super(LiveboxCnxDialog, self).__init__(iParent)
		self.resize(450, 150)

		aWarnBox = QtWidgets.QVBoxLayout()
		aWarnBox.setSpacing(4)
		aW1Label = QtWidgets.QLabel('Cannot connect to the Livebox.')
		aW1Label.setFont(LmTools.BOLD_FONT)
		aWarnBox.addWidget(aW1Label)
		aW2Label = QtWidgets.QLabel('It might be unreachable, in that case just wait.')
		aWarnBox.addWidget(aW2Label)
		aW3Label = QtWidgets.QLabel('Otherwise, try http://livebox.home/, http://livebox/ or http://192.168.1.1/.')
		aWarnBox.addWidget(aW3Label)

		aUrlLabel = QtWidgets.QLabel('Livebox URL')
		self._urlEdit = QtWidgets.QLineEdit()
		self._urlEdit.textChanged.connect(self.textChanged)

		aEditGrid = QtWidgets.QGridLayout()
		aEditGrid.setSpacing(10)
		aEditGrid.addWidget(aUrlLabel, 1, 0)
		aEditGrid.addWidget(self._urlEdit, 1, 1)

		aButtonBar = QtWidgets.QHBoxLayout()
		self._okButton = QtWidgets.QPushButton('OK')
		self._okButton.clicked.connect(self.accept)
		self._okButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton('Cancel')
		aCancelButton.clicked.connect(self.reject)
		aButtonBar.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aButtonBar.setSpacing(10)
		aButtonBar.addWidget(self._okButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aButtonBar.addWidget(aCancelButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.setSpacing(15)
		aVBox.addLayout(aWarnBox, 0)
		aVBox.addLayout(aEditGrid, 0)
		aVBox.addLayout(aButtonBar, 1)

		self._urlEdit.setFocus()
		self.setWindowTitle('Livebox connection')

		self._urlEdit.setText(iURL)

		self.setModal(True)
		self.show()


	def textChanged(self, iText):
		self._okButton.setDisabled(len(self.getURL()) == 0)


	def getURL(self):
		return self._urlEdit.text()



# ############# Livebox signin dialog #############
class LiveboxSigninDialog(QtWidgets.QDialog):
	def __init__(self, iUser, iPassword, iParent = None):
		super(LiveboxSigninDialog, self).__init__(iParent)
		self.resize(450, 130)

		aUserLabel = QtWidgets.QLabel('User')
		self._userEdit = QtWidgets.QLineEdit()
		self._userEdit.textChanged.connect(self.textChanged)

		aPasswordLabel = QtWidgets.QLabel('Password')
		self._passwordEdit = QtWidgets.QLineEdit()
		self._passwordEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
		self._passwordEdit.textChanged.connect(self.textChanged)

		aEditGrid = QtWidgets.QGridLayout()
		aEditGrid.setSpacing(10)
		aEditGrid.addWidget(aUserLabel, 1, 0)
		aEditGrid.addWidget(self._userEdit, 1, 1)
		aEditGrid.addWidget(aPasswordLabel, 2, 0)
		aEditGrid.addWidget(self._passwordEdit, 2, 1)

		self._okButton = QtWidgets.QPushButton('OK')
		self._okButton.clicked.connect(self.accept)
		self._okButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton('Cancel')
		aCancelButton.clicked.connect(self.reject)
		aButtonBar = QtWidgets.QHBoxLayout()
		aButtonBar.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aButtonBar.setSpacing(10)
		aButtonBar.addWidget(self._okButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aButtonBar.addWidget(aCancelButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.addLayout(aEditGrid, 0)
		aVBox.addLayout(aButtonBar, 1)

		self._userEdit.setFocus()
		self.setWindowTitle('Wrong password')

		self._userEdit.setText(iUser)
		self._passwordEdit.setText(iPassword)

		self.setModal(True)
		self.show()


	def textChanged(self, iText):
		self._okButton.setDisabled((len(self.getUser()) == 0) or (len(self.getPassword()) == 0))


	def getUser(self):
		return self._userEdit.text()


	def getPassword(self):
		return self._passwordEdit.text()



# ################################ Prefs dialog ################################

class PrefsDialog(QtWidgets.QDialog):
	def __init__(self, iParent = None):
		super(PrefsDialog, self).__init__(iParent)
		self.resize(550, 310)

		# Profiles box
		aProfileLayout = QtWidgets.QHBoxLayout()
		aProfileLayout.setSpacing(30)

		aProfileListLayout = QtWidgets.QVBoxLayout()
		aProfileListLayout.setSpacing(5)

		self._profileSelection = -1
		self._profileList = QtWidgets.QListWidget()
		self._profileList.setMaximumWidth(190)
		self._profileList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
		self._profileList.itemSelectionChanged.connect(self.profileListClick)
		aProfileListLayout.addWidget(self._profileList, 0)

		aProfileButtonBox = QtWidgets.QHBoxLayout()
		aProfileButtonBox.setSpacing(5)

		aAddProfileButton = QtWidgets.QPushButton('Add')
		aAddProfileButton.clicked.connect(self.addProfileButtonClick)
		aProfileButtonBox.addWidget(aAddProfileButton)
		aDelProfileButton = QtWidgets.QPushButton('Delete')
		aDelProfileButton.clicked.connect(self.delProfileButtonClick)
		aProfileButtonBox.addWidget(aDelProfileButton)
		aProfileListLayout.addLayout(aProfileButtonBox, 0)
		aProfileLayout.addLayout(aProfileListLayout, 0)

		aProfileNameLabel = QtWidgets.QLabel('Name')
		self._profileName = QtWidgets.QLineEdit()
		self._profileName.textChanged.connect(self.profileNameChanged)

		aLiveboxUrlLabel = QtWidgets.QLabel('Livebox URL')
		self._liveboxUrl = QtWidgets.QLineEdit()

		aLiveboxUserLabel = QtWidgets.QLabel('Livebox User')
		self._liveboxUser = QtWidgets.QLineEdit()

		self._filterDevices = QtWidgets.QCheckBox('Filter Devices')

		aMacAddrTableFileLabel = QtWidgets.QLabel('MacAddr Table File')
		self._macAddrTableFile = QtWidgets.QLineEdit()

		self._defaultProfile = QtWidgets.QCheckBox('Default')

		aProfileEditGrid = QtWidgets.QGridLayout()
		aProfileEditGrid.setSpacing(10)
		aProfileEditGrid.addWidget(aProfileNameLabel, 1, 0)
		aProfileEditGrid.addWidget(self._profileName, 1, 1)
		aProfileEditGrid.addWidget(aLiveboxUrlLabel, 2, 0)
		aProfileEditGrid.addWidget(self._liveboxUrl, 2, 1)
		aProfileEditGrid.addWidget(aLiveboxUserLabel, 3, 0)
		aProfileEditGrid.addWidget(self._liveboxUser, 3, 1)
		aProfileEditGrid.addWidget(self._filterDevices, 4, 0)
		aProfileEditGrid.addWidget(aMacAddrTableFileLabel, 5, 0)
		aProfileEditGrid.addWidget(self._macAddrTableFile, 5, 1)
		aProfileEditGrid.addWidget(self._defaultProfile, 6, 0)
		aProfileLayout.addLayout(aProfileEditGrid, 1)

		aProfileGroupBox = QtWidgets.QGroupBox('Profiles')
		aProfileGroupBox.setLayout(aProfileLayout)

		# General preferences box
		aMacAddrApiKeyLabel = QtWidgets.QLabel('macaddress.io API Key')
		self._macAddrApiKey = QtWidgets.QLineEdit()

		aPhoneCodeLabel = QtWidgets.QLabel('Intl Phone Code')
		self._phoneCode = QtWidgets.QLineEdit()
		aPhoneCodeValidator = QtGui.QIntValidator()
		aPhoneCodeValidator.setRange(1, 999999)
		self._phoneCode.setValidator(aPhoneCodeValidator)

		aIntValidator = QtGui.QIntValidator()
		aIntValidator.setRange(1, 99)

		aListHeaderHeightLabel = QtWidgets.QLabel('List Header Height')
		self._listHeaderHeight = QtWidgets.QLineEdit()
		self._listHeaderHeight.setValidator(aIntValidator)

		aListHeaderFontSizeLabel = QtWidgets.QLabel('List Header Font Size')
		self._listHeaderFontSize = QtWidgets.QLineEdit()
		self._listHeaderFontSize.setValidator(aIntValidator)

		aListLineHeightLabel = QtWidgets.QLabel('List Line Height')
		self._listLineHeight = QtWidgets.QLineEdit()
		self._listLineHeight.setValidator(aIntValidator)

		aListLineFontSizeLabel = QtWidgets.QLabel('List Line Font Size')
		self._listLineFontSize = QtWidgets.QLineEdit()
		self._listLineFontSize.setValidator(aIntValidator)

		aPrefsEditGrid = QtWidgets.QGridLayout()
		aPrefsEditGrid.setSpacing(10)
		aPrefsEditGrid.addWidget(aMacAddrApiKeyLabel, 1, 0)
		aPrefsEditGrid.addWidget(self._macAddrApiKey, 1, 1)
		aPrefsEditGrid.addWidget(aPhoneCodeLabel, 2, 0)
		aPrefsEditGrid.addWidget(self._phoneCode, 2, 1)
		aPrefsEditGrid.addWidget(aListHeaderHeightLabel, 3, 0)
		aPrefsEditGrid.addWidget(self._listHeaderHeight, 3, 1)
		aPrefsEditGrid.addWidget(aListHeaderFontSizeLabel, 4, 0)
		aPrefsEditGrid.addWidget(self._listHeaderFontSize, 4, 1)
		aPrefsEditGrid.addWidget(aListLineHeightLabel, 5, 0)
		aPrefsEditGrid.addWidget(self._listLineHeight, 5, 1)
		aPrefsEditGrid.addWidget(aListLineFontSizeLabel, 6, 0)
		aPrefsEditGrid.addWidget(self._listLineFontSize, 6, 1)

		aPrefsGroupBox = QtWidgets.QGroupBox('Preferences')
		aPrefsGroupBox.setLayout(aPrefsEditGrid)		

		# Button bar
		aButtonBar = QtWidgets.QHBoxLayout()
		aOkButton = QtWidgets.QPushButton('OK')
		aOkButton.clicked.connect(self.okButtonClick)
		aOkButton.setDefault(True)
		aButtonBar.addWidget(aOkButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aCancelButton = QtWidgets.QPushButton('Cancel')
		aCancelButton.clicked.connect(self.reject)
		aButtonBar.addWidget(aCancelButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aButtonBar.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aButtonBar.setSpacing(10)

		# Final layout
		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.setSpacing(20)
		aVBox.addWidget(aProfileGroupBox, 0, QtCore.Qt.AlignmentFlag.AlignTop)
		aVBox.addWidget(aPrefsGroupBox, 0, QtCore.Qt.AlignmentFlag.AlignTop)
		aVBox.addLayout(aButtonBar, 1)

		self.setWindowTitle('Preferences')
		self.setModal(True)
		self.loadPrefs()
		self.show()


	### Load preferences data
	def loadPrefs(self):
		self._profiles = []

		# Load profile list
		for p in LmConf.Profiles:
			self._profiles.append(p.copy())
			i = QtWidgets.QListWidgetItem(p['Name'], self._profileList)
			if p == LmConf.CurrProfile:
				self._profileList.setCurrentItem(i)

		# Load paramaters
		self._macAddrApiKey.setText(LmConf.MacAddrApiKey)
		self._phoneCode.setText(LmConf.PhoneCode)
		self._listHeaderHeight.setText(str(LmConf.ListHeaderHeight))
		self._listHeaderFontSize.setText(str(LmConf.ListHeaderFontSize))
		self._listLineHeight.setText(str(LmConf.ListLineHeight))
		self._listLineFontSize.setText(str(LmConf.ListLineFontSize))


	### Save preferences data
	def savePrefs(self):
		# Save profile data
		LmConf.Profiles = self._profiles

		# Try to restore current profile by name
		aCurrProfileName = LmConf.CurrProfile.get('Name')
		p = next((p for p in LmConf.Profiles if p['Name'] == aCurrProfileName), None)
		if p is None:
			# Otherwise take the default
			p = next((p for p in LmConf.Profiles if p['Default']), None)
		if p is None:
			# If not default take the first
			p = LmConf.Profiles[0]
		LmConf.CurrProfile = p

		# Save parameters
		LmConf.MacAddrApiKey = self._macAddrApiKey.text()
		LmConf.PhoneCode = self._phoneCode.text()
		LmConf.ListHeaderHeight = int(self._listHeaderHeight.text())
		LmConf.ListHeaderFontSize = int(self._listHeaderFontSize.text())
		LmConf.ListLineHeight = int(self._listLineHeight.text())
		LmConf.ListLineFontSize = int(self._listLineFontSize.text())


	### Click on profile list item
	def profileListClick(self):
		aNewSelection = self._profileList.currentRow()

		# Save previous values before switch to new
		if self._profileSelection >= 0:
			# Check of selection really changed
			if self._profileSelection == aNewSelection:
				return

			# Save values
			if not self.saveProfile():
				self._profileList.setCurrentRow(self._profileSelection)
				return

		# Load new values
		self._profileSelection = -1		# To inhibit name text change event
		p = self._profiles[aNewSelection]
		self._profileName.setText(p['Name'])
		self._liveboxUrl.setText(p['Livebox URL'])
		self._liveboxUser.setText(p['Livebox User'])
		if p['Filter Devices']:
			self._filterDevices.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._filterDevices.setCheckState(QtCore.Qt.CheckState.Unchecked)
		self._macAddrTableFile.setText(p['MacAddr Table File'])
		if p['Default']:
			self._defaultProfile.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._defaultProfile.setCheckState(QtCore.Qt.CheckState.Unchecked)
		self._profileSelection = aNewSelection


	### Save current profile in profiles buffer, returns False if failed
	def saveProfile(self):
		# Check if name is not duplicated
		aProfileName = self._profileName.text()
		if len(aProfileName) == 0:
			LmTools.DisplayError('Please set profile name.')
			return False

		if self.countProfileName(aProfileName) > 1:
			LmTools.DisplayError('Duplicated name.')
			return False

		# If default profile is selected, set all others to false
		aDefault = self._defaultProfile.checkState() == QtCore.Qt.CheckState.Checked
		if aDefault:
			for p in self._profiles:
				p['Default'] = False

		# Save in profiles buffer
		p = self._profiles[self._profileSelection]
		p['Name'] = self._profileName.text()
		p['Livebox URL'] = LmTools.cleanURL(self._liveboxUrl.text())
		p['Livebox User'] = self._liveboxUser.text()
		p['Filter Devices'] = self._filterDevices.checkState() == QtCore.Qt.CheckState.Checked
		p['MacAddr Table File'] = self._macAddrTableFile.text()
		p['Default'] = aDefault
		return True


	### Profile name text changed
	def profileNameChanged(self, iText):
		if self._profileSelection >= 0:
			self._profileList.item(self._profileSelection).setText(iText)


	### Find number of profiles in list matching a name
	def countProfileName(self, iName):
		return len(self._profileList.findItems(iName, QtCore.Qt.MatchFlag.MatchExactly))


	### Click on add profile button
	def addProfileButtonClick(self):
		# First try to save current profile adding one
		if not self.saveProfile():
			return

		# Add new empty profile in buffer
		p = {}
		p['Name'] = ''
		p['Livebox URL'] = DCFG_LIVEBOX_URL
		p['Livebox User'] = DCFG_LIVEBOX_USER
		p['Filter Devices'] = DCFG_FILTER_DEVICES
		p['MacAddr Table File'] = DCFG_MACADDR_TABLE_FILE
		p['Default'] = False
		self._profiles.append(p)

		# Add new item in list and select it
		i = QtWidgets.QListWidgetItem(p['Name'], self._profileList)
		self._profileList.setCurrentItem(i)


	### Click on delete profile button
	def delProfileButtonClick(self):
		if len(self._profiles) == 1:
			LmTools.DisplayError('You must have at least one profile.')
			return

		# Delete the list line
		i = self._profileSelection
		self._profileSelection = -1 	# Inhibit event handling
		self._profileList.takeItem(i)

		# Remove the profile from profiles buffer
		self._profiles.pop(i)

		# Update selection
		self._profileSelection = self._profileList.currentRow()


	### Click on OK button
	def okButtonClick(self):
		# First try to save current profile before leaving
		if self.saveProfile():
			self.savePrefs()
			self.accept()
