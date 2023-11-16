### Livebox Monitor Configuration module ###

import sys
import os
import platform
import requests
import json
import base64
import webbrowser

from enum import IntEnum

from PyQt6 import QtCore, QtGui, QtWidgets
from cryptography.fernet import Fernet

from src import LmTools
from src.LmSession import DEFAULT_TIMEOUT
from src.LmSession import LmSession
from src import LmLanguages
from src.LmLanguages import (GetConfigPrefsDialogLabel as lx,
							 GetConfigCnxDialogLabel as lcx,
							 GetConfigSigninDialogLabel as lsx,
							 GetSelectProfileDialogLabel as lpx,
							 GetReleaseWarningDialogLabel as lrx)

from __init__ import __url__, __version__, __build__


# ################################ VARS & DEFS ################################

# Config file name
CONFIG_FILE = 'Config.txt'

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

# Static config
GIT_REPO = 'p-dor/LiveboxMonitor'
GITRELEASE_URL = 'https://api.github.com/repos/{}/releases/latest'
ICON_URL = 'assets/common/images/app_conf/'
SECRET = 'mIohg_8Q0pkQCA7x3dOqNTeADYPfcMhJZ4ujomNLNro='

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

# Interfaces
NET_INTF = []

# LB4 Interfaces
NET_INTF_LB4 = [
	{ 'Key': 'eth0',       'Name': 'WAN',          'Type': 'wan', 'SwapStats': False },
	{ 'Key': 'bridge',     'Name': 'LAN',          'Type': 'lan', 'SwapStats': True  },
	{ 'Key': 'eth1',       'Name': 'Ethernet 1',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'eth2',       'Name': 'Ethernet 2',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'eth3',       'Name': 'Ethernet 3',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'eth4',       'Name': 'Ethernet 4',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'wl0',        'Name': 'Wifi 2.4GHz',  'Type': 'wif', 'SwapStats': True  },
	{ 'Key': 'eth6',       'Name': 'Wifi 5GHz',    'Type': 'wif', 'SwapStats': True  },
	{ 'Key': 'wlguest2',   'Name': 'Guest 2.4GHz', 'Type': 'wig', 'SwapStats': True  },
	{ 'Key': 'wlguest5',   'Name': 'Guest 5GHz',   'Type': 'wig', 'SwapStats': True  }
]

# LB5 Interfaces
NET_INTF_LB5 = [
	{ 'Key': 'veip0',       'Name': 'Fiber',        'Type': 'ont', 'SwapStats': False },
	{ 'Key': 'bridge',      'Name': 'LAN',          'Type': 'lan', 'SwapStats': True  },
	{ 'Key': 'eth0',        'Name': 'Ethernet 1',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'eth1',        'Name': 'Ethernet 2',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'eth2',        'Name': 'Ethernet 3',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'eth3',        'Name': 'Ethernet 4',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'wl0',         'Name': 'Wifi 2.4GHz',  'Type': 'wif', 'SwapStats': True  },
	{ 'Key': 'eth4',        'Name': 'Wifi 5GHz',    'Type': 'wif', 'SwapStats': True  },
	{ 'Key': 'wlguest2',    'Name': 'Guest 2.4GHz', 'Type': 'wig', 'SwapStats': True  },
	{ 'Key': 'wlguest5',    'Name': 'Guest 5GHz',   'Type': 'wig', 'SwapStats': True  }
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

# LB7 Interfaces
NET_INTF_LB7 = [
	{ 'Key': 'veip0',        'Name': 'Fiber',        'Type': 'ont', 'SwapStats': False },
	{ 'Key': 'bridge',       'Name': 'LAN',          'Type': 'lan', 'SwapStats': True  },
	{ 'Key': 'ETH1',         'Name': 'Ethernet 1',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'ETH2',         'Name': 'Ethernet 2',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'ETH3',         'Name': 'Ethernet 3',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'ETH4',         'Name': 'Ethernet 4',   'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'ETH0',         'Name': 'Ether 10G',    'Type': 'eth', 'SwapStats': True  },
	{ 'Key': 'vap2g0priv0',  'Name': 'Wifi 2.4GHz',  'Type': 'wif', 'SwapStats': True  },
	{ 'Key': 'vap5g0priv0',  'Name': 'Wifi 5GHz',    'Type': 'wif', 'SwapStats': True  },
	{ 'Key': 'vap6g0priv0',  'Name': 'Wifi 6GHz',    'Type': 'wif', 'SwapStats': True  },
	{ 'Key': 'vap2g0guest0', 'Name': 'Guest 2.4GHz', 'Type': 'wig', 'SwapStats': True  },
	{ 'Key': 'vap5g0guest0', 'Name': 'Guest 5GHz',   'Type': 'wig', 'SwapStats': True  }
]

# Interface name mapping
INTF_NAME_MAP = []

# LB4 Interface name mapping
INTF_NAME_MAP_LB4 = {
	"Livebox":  {"eth1":"Eth1", "eth2":"Eth2", "eth3":"Eth3", "eth4":"Eth4"},
	"Repeater": {"eth0":"Eth1", "eth1":"Eth2"}
}

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

# LB7 Interface name mapping
INTF_NAME_MAP_LB7 = {
	"Livebox":  {"eth0":"Eth4", "eth1":"Eth3", "eth2":"Eth2", "eth3":"Eth1", "eth4":"Eth 10G"},
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



# ################################ Tools ################################

# Setting up application style depending on platform
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


# Assign Tooltips to all QWidgets in a window/dialog/tab
def SetToolTips(iQtObject, iKey):
	if LmConf.Tooltips:
		aItemList = iQtObject.findChildren(QtWidgets.QWidget, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly)
		for aItem in aItemList:
			k = aItem.objectName()
			if len(k):
				aType = type(aItem).__name__
				if aType == 'QTableWidget':
					h = aItem.horizontalHeader()
					m = h.model()
					for c in range(h.count()):
						k = m.headerData(c, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)
						if k is not None:
							aItem.horizontalHeaderItem(c).setToolTip(LmLanguages.GetToolTip(iKey, k))
				elif aType == 'QTabWidget':
					for i in range(aItem.count()):
						k = aItem.widget(i).objectName()
						if len(k):
							aItem.setTabToolTip(i, LmLanguages.GetToolTip(iKey, k))
				elif aType == 'QGroupBox':
					# Set tooltip to the group if any
					aItem.setToolTip(LmLanguages.GetToolTip(iKey, k))
					# Recursive call to handle group content
					SetToolTips(aItem, iKey)
				else:
					aItem.setToolTip(LmLanguages.GetToolTip(iKey, k))


# Setup configuration according to Livebox model
def SetLiveboxModel(iModel):
	global NET_INTF
	global INTF_NAME_MAP

	if iModel == 7:
		NET_INTF = NET_INTF_LB7
		INTF_NAME_MAP = INTF_NAME_MAP_LB7
	elif iModel == 6:
		NET_INTF = NET_INTF_LB6
		INTF_NAME_MAP = INTF_NAME_MAP_LB6
	elif iModel == 5:
		NET_INTF = NET_INTF_LB5
		INTF_NAME_MAP = INTF_NAME_MAP_LB5
	else:
		NET_INTF = NET_INTF_LB4
		INTF_NAME_MAP = INTF_NAME_MAP_LB4


# Check if latest release
def ReleaseCheck():
	# Call GitHub API to fetch latest release infos
	try:
		d = requests.get(GITRELEASE_URL.format(GIT_REPO), timeout = 1)
		d = json.loads(d.content)
		v = d['tag_name']
	except BaseException as e:
		LmTools.Error('Cannot get latest release infos. Error: {}'.format(e))
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
		LmTools.Error('Cannot decode latest release infos. Error: {}'.format(e))
		return

	# Warn if this release is not the latest
	if (r > __build__) and (LmConf.NoReleaseWarning != r):
		aReleaseWarningDialog = ReleaseWarningDialog(v)
		if aReleaseWarningDialog.exec():
			return
		# User decided to not be warned again, remember in config
		LmConf.NoReleaseWarning = r
		LmConf.save()


# ################################ Config Class ################################

class LmConf:
	Profiles = None
	CurrProfile = None
	LiveboxURL = DCFG_LIVEBOX_URL
	LiveboxUser = DCFG_LIVEBOX_USER
	LiveboxPassword = DCFG_LIVEBOX_PASSWORD
	LiveboxMAC = ''
	FilterDevices = DCFG_FILTER_DEVICES
	MacAddrTableFile = DCFG_MACADDR_TABLE_FILE
	MacAddrTable = {}
	Language = DCFG_LANGUAGE
	Tooltips = DCFG_TOOLTIPS
	StatsFrequency = DCFG_STATS_FREQUENCY
	MacAddrApiKey = DCFG_MACADDR_API_KEY
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


	### Load configuration, if returns False the program aborts starting
	@staticmethod
	def load():
		aConfigFile = None
		aDirtyConfig = False
		aConfigFilePath = os.path.join(LmConf.getConfigDirectory(), CONFIG_FILE)
		try:
			aConfigFile = open(aConfigFilePath)
			aConfig = json.load(aConfigFile)
		except OSError:
			LmTools.Error('No configuration file, creating one.')
			aDirtyConfig = True
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			if LmTools.AskQuestion('Wrong {} file, fully reset it?'.format(CONFIG_FILE)):
				aDirtyConfig = True
			else:
				if aConfigFile is not None:
					aConfigFile.close()
				return False
		else:
			# Check if config version is more recent than the application
			aConfigVersion = aConfig.get('Version', 0)
			if aConfigVersion > __build__:
				if not LmTools.AskQuestion('This version of the application is older than the configuration file.\n'
										   'If you continue you might lose some setup.\n'
										   'Are you sure you want to continue?'):
					return False

			# Potentially convert the format to newer version
			aDirtyConfig = LmConf.convert(aConfig)

			# Load all configs
			p = aConfig.get('Language')
			if p is not None:
				LmConf.Language = str(p)
				if LmConf.Language not in LmLanguages.LANGUAGES_KEY:
					LmConf.Language = DCFG_LANGUAGE
			LmLanguages.SetLanguage(LmConf.Language)
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
				LmTools.SetVerbosity(LmConf.LogLevel)
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

		if aConfigFile is not None:
			aConfigFile.close()

		if aDirtyConfig:
			LmConf.save()

		LmConf.apply()

		return True


	### Apply immediate actions derived from configuration
	@staticmethod
	def apply():
		LmLanguages.SetLanguage(LmConf.Language)


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

		# Find dynamically if no default
		if LmConf.CurrProfile is None:
			# First collect reachable profiles and those matching Livebox's MAC address
			LmTools.MouseCursor_Busy()
			aReachableProfiles = []
			aMatchingProfiles = []
			for p in LmConf.Profiles:
				aProfileMAC = p.get('Livebox MacAddr')
				aLiveboxMAC = LmSession.getLiveboxMAC(p.get('Livebox URL'))
				if aLiveboxMAC is not None:
					aReachableProfiles.append(p)
					if aLiveboxMAC == aProfileMAC:
						aMatchingProfiles.append(p)
			LmTools.MouseCursor_Normal()

			# If at least one matching profile, take the first
			if len(aMatchingProfiles):
				LmConf.CurrProfile = aMatchingProfiles[0]
		else:
			aMatchingProfiles = None

		# If no match/default found or if Ctrl key pressed, ask for it
		aModifiers = QtGui.QGuiApplication.queryKeyboardModifiers()
		aDirtyConfig = False
		if (LmConf.CurrProfile is None) or (aModifiers == QtCore.Qt.KeyboardModifier.ControlModifier):
			r = LmConf.askProfile(aMatchingProfiles)
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
	def askProfile(iMatchingProfiles = None):
		if len(LmConf.Profiles) == 0:
			return 1

		LmTools.MouseCursor_Busy()
		if iMatchingProfiles is None:
			iMatchingProfiles = []
			for p in LmConf.Profiles:
				aProfileMAC = p.get('Livebox MacAddr')
				aLiveboxMAC = LmSession.getLiveboxMAC(p.get('Livebox URL'))
				if (aLiveboxMAC is not None) and (aLiveboxMAC == aProfileMAC):
					iMatchingProfiles.append(p)
		LmTools.MouseCursor_Normal()

		aSelectProfileDialog = SelectProfileDialog(iMatchingProfiles)
		if aSelectProfileDialog.exec():
			if aSelectProfileDialog.doCreateProfile():
				return 2
			LmConf.CurrProfile = LmConf.Profiles[aSelectProfileDialog.profileIndex()]
			return 1
		return 0


	### Create a new profile, return False is user cancelled
	#staticmethod
	def createProfile():
		# Loop until finding a unique name or user cancels
		while True:
			aName, aOK = QtWidgets.QInputDialog.getText(None, lpx('Create Profile'), lpx('Profile name:'))
			if aOK:
				q = next((p for p in LmConf.Profiles if p['Name'] == aName), None)
				if q is None:
					break
				else:
					LmTools.DisplayError('This name is already used.')
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
		LmConf.LiveboxURL = LmTools.CleanURL(LmConf.CurrProfile.get('Livebox URL', DCFG_LIVEBOX_URL))
		LmConf.LiveboxUser = LmConf.CurrProfile.get('Livebox User', DCFG_LIVEBOX_USER)

		p = LmConf.CurrProfile.get('Livebox Password')
		if p is not None:
			try:
				LmConf.LiveboxPassword = Fernet(SECRET.encode('utf-8')).decrypt(p.encode('utf-8')).decode('utf-8')
			except:
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

		aMainProfile['Name'] = lx('Main')
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
					LmConf.CurrProfile['Name'] = lx('Main')
					LmConf.CurrProfile['Default'] = True
				LmConf.CurrProfile['Livebox URL'] = LmConf.LiveboxURL
				LmConf.CurrProfile['Livebox User'] = LmConf.LiveboxUser
				LmConf.CurrProfile['Livebox Password'] = Fernet(SECRET.encode('utf-8')).encrypt(LmConf.LiveboxPassword.encode('utf-8')).decode('utf-8')
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
					aIconData = requests.get(LmConf.LiveboxURL + ICON_URL + iDevice['Icon'],
											 timeout = DEFAULT_TIMEOUT,
											 verify = LmConf.LiveboxURL.startswith('http://'))
					if not aIconPixMap.loadFromData(aIconData.content):
						LmTools.Error('Cannot load device icon {}.'.format(e, iDevice['Icon']))
				except requests.exceptions.Timeout as e:
					LmTools.Error('Device icon {} request timeout error: {}.'.format(iDevice['Icon'], e))
				except BaseException as e:
					LmTools.Error('Error: {}. Cannot request device icon {}.'.format(e, iDevice['Icon']))

				iDevice['PixMap'] = aIconPixMap

			return aIconPixMap


	### Load all device icons
	@staticmethod
	def loadDeviceIcons():
		if not LmConf.AllDeviceIconsLoaded:
			for d in DEVICE_TYPES:
				LmConf.getDeviceIcon(d)

			LmConf.AllDeviceIconsLoaded = True



# ################################ Livebox connection dialog ################################
class LiveboxCnxDialog(QtWidgets.QDialog):
	def __init__(self, iURL, iParent = None):
		super(LiveboxCnxDialog, self).__init__(iParent)
		self.resize(450, 150)

		aWarnBox = QtWidgets.QVBoxLayout()
		aWarnBox.setSpacing(4)
		aW1Label = QtWidgets.QLabel(lcx('Cannot connect to the Livebox.'), objectName = 'w1Label')
		aW1Label.setFont(LmTools.BOLD_FONT)
		aWarnBox.addWidget(aW1Label)
		aW2Label = QtWidgets.QLabel(lcx('It might be unreachable, in that case just wait.'), objectName = 'w2Label')
		aWarnBox.addWidget(aW2Label)
		aW3Label = QtWidgets.QLabel(lcx('Otherwise, try {0}, {1} or {2}.').format('http://livebox.home/', 'http://livebox/', 'http://192.168.1.1/'),
									objectName = 'w3Label')
		aWarnBox.addWidget(aW3Label)

		aUrlLabel = QtWidgets.QLabel(lcx('Livebox URL'), objectName = 'urlLabel')
		self._urlEdit = QtWidgets.QLineEdit(objectName = 'urlEdit')
		self._urlEdit.textChanged.connect(self.textChanged)

		aEditGrid = QtWidgets.QGridLayout()
		aEditGrid.setSpacing(10)
		aEditGrid.addWidget(aUrlLabel, 0, 0)
		aEditGrid.addWidget(self._urlEdit, 0, 1)

		aButtonBar = QtWidgets.QHBoxLayout()
		self._okButton = QtWidgets.QPushButton(lcx('OK'), objectName = 'ok')
		self._okButton.clicked.connect(self.accept)
		self._okButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton(lcx('Cancel'), objectName = 'cancel')
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

		SetToolTips(self, 'cnx')

		aTitle = lcx('Livebox connection')
		if len(LmConf.Profiles) > 1:
			aTitle += ' [' + LmConf.CurrProfile['Name'] + ']'
		self.setWindowTitle(aTitle)

		self._urlEdit.setText(iURL)

		self.setModal(True)
		self.show()


	def textChanged(self, iText):
		self._okButton.setDisabled(len(self.getURL()) == 0)


	def getURL(self):
		return self._urlEdit.text()



# ################################ Livebox signin dialog ################################
class LiveboxSigninDialog(QtWidgets.QDialog):
	def __init__(self, iUser, iPassword, iParent = None):
		super(LiveboxSigninDialog, self).__init__(iParent)
		self.resize(450, 130)

		aUserLabel = QtWidgets.QLabel(lsx('User'), objectName = 'userLabel')
		self._userEdit = QtWidgets.QLineEdit(objectName = 'userEdit')
		self._userEdit.textChanged.connect(self.textChanged)

		aPasswordLabel = QtWidgets.QLabel(lsx('Password'), objectName = 'passwordLabel')
		self._passwordEdit = QtWidgets.QLineEdit(objectName = 'passwordEdit')
		self._passwordEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
		self._passwordEdit.textChanged.connect(self.textChanged)

		aEditGrid = QtWidgets.QGridLayout()
		aEditGrid.setSpacing(10)
		aEditGrid.addWidget(aUserLabel, 0, 0)
		aEditGrid.addWidget(self._userEdit, 0, 1)
		aEditGrid.addWidget(aPasswordLabel, 1, 0)
		aEditGrid.addWidget(self._passwordEdit, 1, 1)

		self._okButton = QtWidgets.QPushButton(lsx('OK'), objectName = 'ok')
		self._okButton.clicked.connect(self.accept)
		self._okButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton(lsx('Cancel'), objectName = 'cancel')
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

		SetToolTips(self, 'signin')

		aTitle = lsx('Wrong password')
		if len(LmConf.Profiles) > 1:
			aTitle += ' [' + LmConf.CurrProfile['Name'] + ']'
		self.setWindowTitle(aTitle)

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



# ################################ Profile selection dialog ################################
class SelectProfileDialog(QtWidgets.QDialog):
	def __init__(self, iMatchingProfiles, iParent = None):
		super(SelectProfileDialog, self).__init__(iParent)
		self.resize(350, 130)

		aMainLabel = QtWidgets.QLabel(lpx('Please select a profile to use:'), objectName = 'mainLabel')
		self._profileCombo = QtWidgets.QComboBox(objectName = 'profileCombo')
		i = 0
		aCurrentIndex = 0
		for p in LmConf.Profiles:
			aName = p['Name']
			self._profileCombo.addItem(aName)
			if (LmConf.CurrProfile is not None) and (LmConf.CurrProfile['Name'] == aName):
				aCurrentIndex = i
			i += 1
		self._profileCombo.currentIndexChanged.connect(self.profileSelected)

		aAssociatedMacLabel = QtWidgets.QLabel(lpx('Associated Livebox MAC:'), objectName = 'assMacLabel')
		self._assMac = QtWidgets.QLabel(objectName = 'assMacValue')
		self._assMac.setFont(LmTools.BOLD_FONT)

		aDetectedMacLabel = QtWidgets.QLabel(lpx('Detected Livebox MAC:'), objectName = 'detMacLabel')
		self._detMac = QtWidgets.QLabel(objectName = 'detMacValue')
		self._detMac.setFont(LmTools.BOLD_FONT)

		self._warning = QtWidgets.QLabel('', objectName = 'warnLabel')

		aGrid = QtWidgets.QGridLayout()
		aGrid.setSpacing(10)
		aGrid.addWidget(aMainLabel, 0, 0)
		aGrid.addWidget(self._profileCombo, 1, 0, 1, 2)
		aGrid.addWidget(aAssociatedMacLabel, 2, 0)
		aGrid.addWidget(self._assMac, 2, 1)
		aGrid.addWidget(aDetectedMacLabel, 3, 0)
		aGrid.addWidget(self._detMac, 3, 1)
		aGrid.addWidget(self._warning, 4, 0, 4, 2)

		aCreateProfileButton = QtWidgets.QPushButton(lpx('New Profile...'), objectName = 'createProfile')
		aCreateProfileButton.clicked.connect(self.createProfile)
		aOkButton = QtWidgets.QPushButton(lpx('OK'), objectName = 'ok')
		aOkButton.clicked.connect(self.accept)
		aOkButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton(lpx('Cancel'), objectName = 'cancel')
		aCancelButton.clicked.connect(self.reject)
		aButtonBar = QtWidgets.QHBoxLayout()
		aButtonBar.setSpacing(10)
		aButtonBar.addWidget(aCreateProfileButton, 0, QtCore.Qt.AlignmentFlag.AlignLeft)
		aOkButtonBar = QtWidgets.QHBoxLayout()
		aOkButtonBar.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aOkButtonBar.setSpacing(10)
		aOkButtonBar.addWidget(aOkButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aOkButtonBar.addWidget(aCancelButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aButtonBar.addLayout(aOkButtonBar)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.setSpacing(20)
		aVBox.addLayout(aGrid, 0)
		aVBox.addLayout(aButtonBar, 1)

		SetToolTips(self, 'sprofile')

		self.setWindowTitle(lpx('Profile selection'))

		if aCurrentIndex:
			self._profileCombo.setCurrentIndex(aCurrentIndex)
		else:
			self.profileSelected(0)

		self._createProfile = False

		self.setModal(True)
		self.show()


	def profileSelected(self, iIndex):
		p = LmConf.Profiles[iIndex]
		aAssociatedLiveboxMAC = p.get('Livebox MacAddr')
		if aAssociatedLiveboxMAC is None:
			self._assMac.setText(lpx('<None>'))
			self._assMac.setStyleSheet('QLabel { color : green }')
		else:
			self._assMac.setText(aAssociatedLiveboxMAC)
			self._assMac.setStyleSheet('QLabel { color : black }')

		LmTools.MouseCursor_Busy()
		aDetectedLiveboxMAC = LmSession.getLiveboxMAC(p.get('Livebox URL'))
		LmTools.MouseCursor_Normal()
		if aDetectedLiveboxMAC is None:
			self._detMac.setText(lpx('<None>'))
			self._detMac.setStyleSheet('QLabel { color : red }')
			self._warning.setText(lpx('No Livebox detected at profile\'s URL.'))
			self._warning.setStyleSheet('QLabel { color : red }')
		else:
			self._detMac.setText(aDetectedLiveboxMAC)
			if aAssociatedLiveboxMAC is None:
				self._detMac.setStyleSheet('QLabel { color : green }')
				self._warning.setText(lpx('Detected MAC will be associated to this profile.'))
				self._warning.setStyleSheet('QLabel { color : green }')
			elif aDetectedLiveboxMAC == aAssociatedLiveboxMAC:
				self._detMac.setStyleSheet('QLabel { color : green }')
				self._warning.setText('')
				self._warning.setStyleSheet('QLabel { color : black }')
			else:
				self._detMac.setStyleSheet('QLabel { color : red }')
				self._warning.setText(lpx('Warning: another Livebox is associated to this profile.'))
				self._warning.setStyleSheet('QLabel { color : red }')


	def profileIndex(self):
		return self._profileCombo.currentIndex()


	def doCreateProfile(self):
		return self._createProfile


	def createProfile(self):
		self._createProfile = True
		self.accept()



# ################################ Prefs dialog ################################

class PrefsDialog(QtWidgets.QDialog):
	def __init__(self, iParent = None):
		super(PrefsDialog, self).__init__(iParent)
		self.resize(620, 510)

		# Profiles box
		aProfileLayout = QtWidgets.QHBoxLayout()
		aProfileLayout.setSpacing(30)

		aProfileListLayout = QtWidgets.QVBoxLayout()
		aProfileListLayout.setSpacing(5)

		self._profileSelection = -1
		self._profileList = QtWidgets.QListWidget(objectName = 'profileList')
		self._profileList.setMaximumWidth(190)
		self._profileList.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.SingleSelection)
		self._profileList.itemSelectionChanged.connect(self.profileListClick)
		aProfileListLayout.addWidget(self._profileList, 0)

		aProfileButtonBox = QtWidgets.QHBoxLayout()
		aProfileButtonBox.setSpacing(5)

		aAddProfileButton = QtWidgets.QPushButton(lx('Add'), objectName = 'addProfile')
		aAddProfileButton.clicked.connect(self.addProfileButtonClick)
		aProfileButtonBox.addWidget(aAddProfileButton)
		aDelProfileButton = QtWidgets.QPushButton(lx('Delete'), objectName = 'delProfile')
		aDelProfileButton.clicked.connect(self.delProfileButtonClick)
		aProfileButtonBox.addWidget(aDelProfileButton)
		aProfileListLayout.addLayout(aProfileButtonBox, 0)
		aProfileLayout.addLayout(aProfileListLayout, 0)

		aProfileNameLabel = QtWidgets.QLabel(lx('Name'), objectName = 'profileNameLabel')
		self._profileName = QtWidgets.QLineEdit(objectName = 'profileNameEdit')
		self._profileName.textChanged.connect(self.profileNameChanged)

		aLiveboxUrlLabel = QtWidgets.QLabel(lx('Livebox URL'), objectName = 'liveboxUrlLabel')
		self._liveboxUrl = QtWidgets.QLineEdit(objectName = 'liveboxUrlEdit')

		aLiveboxUserLabel = QtWidgets.QLabel(lx('Livebox User'), objectName = 'liveboxUserLabel')
		self._liveboxUser = QtWidgets.QLineEdit(objectName = 'liveboxUserEdit')

		self._filterDevices = QtWidgets.QCheckBox(lx('Filter Devices'), objectName = 'filterDevices')

		aMacAddrTableFileLabel = QtWidgets.QLabel(lx('MacAddr Table File'), objectName = 'macAddrTableFileLabel')
		self._macAddrTableFile = QtWidgets.QLineEdit(objectName = 'macAddrTableFileEdit')

		self._defaultProfile = QtWidgets.QCheckBox(lx('Default'), objectName = 'defaultProfile')

		aProfileEditGrid = QtWidgets.QGridLayout()
		aProfileEditGrid.setSpacing(10)
		aProfileEditGrid.addWidget(aProfileNameLabel, 0, 0)
		aProfileEditGrid.addWidget(self._profileName, 0, 1)
		aProfileEditGrid.addWidget(aLiveboxUrlLabel, 1, 0)
		aProfileEditGrid.addWidget(self._liveboxUrl, 1, 1)
		aProfileEditGrid.addWidget(aLiveboxUserLabel, 2, 0)
		aProfileEditGrid.addWidget(self._liveboxUser, 2, 1)
		aProfileEditGrid.addWidget(self._filterDevices, 3, 0)
		aProfileEditGrid.addWidget(aMacAddrTableFileLabel, 4, 0)
		aProfileEditGrid.addWidget(self._macAddrTableFile, 4, 1)
		aProfileEditGrid.addWidget(self._defaultProfile, 5, 0)
		aProfileLayout.addLayout(aProfileEditGrid, 1)

		aProfileGroupBox = QtWidgets.QGroupBox(lx('Profiles'), objectName = 'profileGroup')
		aProfileGroupBox.setLayout(aProfileLayout)

		# General preferences box
		aLanguageLabel = QtWidgets.QLabel(lx('Language'), objectName = 'languageLabel')
		self._languageCombo = QtWidgets.QComboBox(objectName = 'languageCombo')
		for i in range(len(LmLanguages.LANGUAGES_KEY)):
			self._languageCombo.addItem(LmLanguages.LANGUAGES_KEY[i] + ' - ' + LmLanguages.LANGUAGES_NAME[i])

		self._tooltips = QtWidgets.QCheckBox(lx('Tooltips'), objectName = 'tooltips')
		aMacAddrApiKeyLabel = QtWidgets.QLabel(lx('macaddress.io API Key'), objectName = 'macAddrApiKeyLabel')
		self._macAddrApiKey = QtWidgets.QLineEdit(objectName = 'macAddrApiKeyEdit')

		aIntValidator = QtGui.QIntValidator()
		aIntValidator.setRange(1, 99)

		aStatsFrequencyLabel = QtWidgets.QLabel(lx('Stats Frequency'), objectName = 'statsFrequencyLabel')
		self._statsFrequency = QtWidgets.QLineEdit(objectName = 'statsFrequencyEdit')
		self._statsFrequency.setValidator(aIntValidator)

		aPhoneCodeLabel = QtWidgets.QLabel(lx('Intl Phone Code'), objectName = 'phoneCodeLabel')
		self._phoneCode = QtWidgets.QLineEdit(objectName = 'phoneCodeEdit')
		aPhoneCodeValidator = QtGui.QIntValidator()
		aPhoneCodeValidator.setRange(1, 999999)
		self._phoneCode.setValidator(aPhoneCodeValidator)

		aListHeaderHeightLabel = QtWidgets.QLabel(lx('List Header Height'), objectName = 'listHeaderHeightLabel')
		self._listHeaderHeight = QtWidgets.QLineEdit(objectName = 'listHeaderHeightEdit')
		self._listHeaderHeight.setValidator(aIntValidator)

		aListHeaderFontSizeLabel = QtWidgets.QLabel(lx('List Header Font Size'), objectName = 'listHeaderFontSizeLabel')
		self._listHeaderFontSize = QtWidgets.QLineEdit(objectName = 'listHeaderFontSizeEdit')
		self._listHeaderFontSize.setValidator(aIntValidator)

		aListLineHeightLabel = QtWidgets.QLabel(lx('List Line Height'), objectName = 'listLineHeightLabel')
		self._listLineHeight = QtWidgets.QLineEdit(objectName = 'listLineHeightEdit')
		self._listLineHeight.setValidator(aIntValidator)

		aListLineFontSizeLabel = QtWidgets.QLabel(lx('List Line Font Size'), objectName = 'listLineFontSizeLabel')
		self._listLineFontSize = QtWidgets.QLineEdit(objectName = 'listLineFontSize')
		self._listLineFontSize.setValidator(aIntValidator)

		self._realtimeWifiStats = QtWidgets.QCheckBox(lx('Realtime wifi device statistics'), objectName = 'realtimeWifiStats')
		self._nativeUIStyle = QtWidgets.QCheckBox(lx('Use native graphical interface style'), objectName = 'nativeUIStyle')

		aPrefsEditGrid = QtWidgets.QGridLayout()
		aPrefsEditGrid.setSpacing(10)

		aPrefsEditGrid.addWidget(aLanguageLabel, 0, 0)
		aPrefsEditGrid.addWidget(self._languageCombo, 0, 1)
		aPrefsEditGrid.addWidget(self._tooltips, 0, 3)

		aPrefsEditGrid.addWidget(aMacAddrApiKeyLabel, 1, 0)
		aPrefsEditGrid.addWidget(self._macAddrApiKey, 1, 1, 1, 3)
		aPrefsEditGrid.addWidget(aStatsFrequencyLabel, 2, 0)
		aPrefsEditGrid.addWidget(self._statsFrequency, 2, 1)
		aPrefsEditGrid.addWidget(aPhoneCodeLabel, 2, 2)
		aPrefsEditGrid.addWidget(self._phoneCode, 2, 3)
		aPrefsEditGrid.addWidget(aListHeaderHeightLabel, 3, 0)
		aPrefsEditGrid.addWidget(self._listHeaderHeight, 3, 1)
		aPrefsEditGrid.addWidget(aListHeaderFontSizeLabel, 3, 2)
		aPrefsEditGrid.addWidget(self._listHeaderFontSize, 3, 3)
		aPrefsEditGrid.addWidget(aListLineHeightLabel, 4, 0)
		aPrefsEditGrid.addWidget(self._listLineHeight, 4, 1)
		aPrefsEditGrid.addWidget(aListLineFontSizeLabel, 4, 2)
		aPrefsEditGrid.addWidget(self._listLineFontSize, 4, 3)
		aPrefsEditGrid.addWidget(self._realtimeWifiStats, 5, 0, 5, 2)
		aPrefsEditGrid.addWidget(self._nativeUIStyle, 6, 0, 6, 2)

		aPrefsGroupBox = QtWidgets.QGroupBox(lx('Preferences'), objectName = 'prefsGroup')
		aPrefsGroupBox.setLayout(aPrefsEditGrid)

		# Button bar
		aButtonBar = QtWidgets.QHBoxLayout()
		aOkButton = QtWidgets.QPushButton(lx('OK'), objectName = 'ok')
		aOkButton.clicked.connect(self.okButtonClick)
		aOkButton.setDefault(True)
		aButtonBar.addWidget(aOkButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aCancelButton = QtWidgets.QPushButton(lx('Cancel'), objectName = 'cancel')
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

		SetToolTips(self, 'prefs')

		self.setWindowTitle(lx('Preferences'))
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
		try:
			i = LmLanguages.LANGUAGES_KEY.index(LmConf.Language)
		except:
			i = 0
		self._languageCombo.setCurrentIndex(i)
		if LmConf.Tooltips:
			self._tooltips.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._tooltips.setCheckState(QtCore.Qt.CheckState.Unchecked)
		self._statsFrequency.setText(str(int(LmConf.StatsFrequency / 1000)))
		self._macAddrApiKey.setText(LmConf.MacAddrApiKey)
		self._phoneCode.setText(LmConf.PhoneCode)
		self._listHeaderHeight.setText(str(LmConf.ListHeaderHeight))
		self._listHeaderFontSize.setText(str(LmConf.ListHeaderFontSize))
		self._listLineHeight.setText(str(LmConf.ListLineHeight))
		self._listLineFontSize.setText(str(LmConf.ListLineFontSize))
		if LmConf.RealtimeWifiStats_save:
			self._realtimeWifiStats.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._realtimeWifiStats.setCheckState(QtCore.Qt.CheckState.Unchecked)
		if LmConf.NativeUIStyle:
			self._nativeUIStyle.setCheckState(QtCore.Qt.CheckState.Checked)
		else:
			self._nativeUIStyle.setCheckState(QtCore.Qt.CheckState.Unchecked)


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
		LmConf.Language = LmLanguages.LANGUAGES_KEY[self._languageCombo.currentIndex()]
		LmConf.Tooltips = self._tooltips.checkState() == QtCore.Qt.CheckState.Checked
		LmConf.StatsFrequency = int(self._statsFrequency.text()) * 1000
		LmConf.MacAddrApiKey = self._macAddrApiKey.text()
		LmConf.PhoneCode = self._phoneCode.text()
		LmConf.ListHeaderHeight = int(self._listHeaderHeight.text())
		LmConf.ListHeaderFontSize = int(self._listHeaderFontSize.text())
		LmConf.ListLineHeight = int(self._listLineHeight.text())
		LmConf.ListLineFontSize = int(self._listLineFontSize.text())
		LmConf.RealtimeWifiStats_save = self._realtimeWifiStats.checkState() == QtCore.Qt.CheckState.Checked
		LmConf.NativeUIStyle = self._nativeUIStyle.checkState() == QtCore.Qt.CheckState.Checked


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
		p['Livebox URL'] = LmTools.CleanURL(self._liveboxUrl.text())
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

		# Set focus on profile's name
		self._profileName.setFocus()


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



# ################################ New release warning dialog ################################
class ReleaseWarningDialog(QtWidgets.QDialog):
	def __init__(self, iNewRelease, iParent = None):
		super(ReleaseWarningDialog, self).__init__(iParent)
		self.resize(450, 150)

		aWarnBox = QtWidgets.QVBoxLayout()
		aWarnBox.setSpacing(4)
		aNewReleaseLabel = QtWidgets.QLabel(lrx('New release {0} has been published.').format(iNewRelease), objectName = 'nreal')
		aNewReleaseLabel.setFont(LmTools.BOLD_FONT)
		aWarnBox.addWidget(aNewReleaseLabel)
		aCurrReleaseLabel = QtWidgets.QLabel(lrx('You are using release {0}.').format(__version__), objectName = 'creal')
		aWarnBox.addWidget(aCurrReleaseLabel)
		aDownloadURL = QtWidgets.QLabel(__url__, objectName = 'downloadURL')
		aDownloadURL.setStyleSheet('QLabel { color : blue }')
		aDownloadURL.mousePressEvent = self.downloadUrlClick
		aWarnBox.addWidget(aDownloadURL, 0, QtCore.Qt.AlignmentFlag.AlignHCenter)

		aButtonBar = QtWidgets.QHBoxLayout()
		aOkButton = QtWidgets.QPushButton(lrx('OK'), objectName = 'ok')
		aOkButton.clicked.connect(self.accept)
		aOkButton.setDefault(True)
		aCancelButton = QtWidgets.QPushButton(lrx('Don\'t warn me again'), objectName = 'nowarning')
		aCancelButton.clicked.connect(self.reject)
		aButtonBar.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
		aButtonBar.setSpacing(10)
		aButtonBar.addWidget(aCancelButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)
		aButtonBar.addWidget(aOkButton, 0, QtCore.Qt.AlignmentFlag.AlignRight)

		aVBox = QtWidgets.QVBoxLayout(self)
		aVBox.setSpacing(15)
		aVBox.addLayout(aWarnBox, 0)
		aVBox.addLayout(aButtonBar, 1)

		SetToolTips(self, 'rwarn')

		self.setWindowTitle(lrx('You are not using the latest release'))

		self.setModal(True)
		self.show()


	### Project's URL web button
	def downloadUrlClick(self, iEvent):
		webbrowser.open_new_tab(__url__)

