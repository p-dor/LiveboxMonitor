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
DCFG_NOTIFICATION_FLUSH_FREQUENCY = 30  # Consolidated notifs flush + time diff between events to merge - in seconds
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
WIND_HEIGHT_ADJUST = 0      # Space to add to a window height to respect a table wished height inside
DIAG_HEIGHT_ADJUST = 0      # Space to add to a dialog height to respect a table wished height inside
TABLE_ADJUST = 4            # Space to add to a table height to respect a table wished height
LIST_HEADER_FONT_SIZE = 0   # 0 = default system font, value can be overriden by LmConf.ListHeaderFontSize
LIST_HEADER_FONT = None
LIST_LINE_FONT_SIZE = 0     # 0 = default system font, value can be overriden by LmConf.ListLineFontSize
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
def set_application_style():
    global WIND_HEIGHT_ADJUST
    global DIAG_HEIGHT_ADJUST
    global TABLE_ADJUST
    global LIST_HEADER_FONT_SIZE
    global LIST_HEADER_FONT
    global LIST_LINE_FONT_SIZE
    global LIST_LINE_FONT
    global LIST_STYLESHEET
    global LIST_HEADER_STYLESHEET

    keys = QtWidgets.QStyleFactory.keys()
    system =  platform.system()
    style = 'Fusion'
    if LmConf.NativeUIStyle:
        if system == 'Windows':
            style = 'Windows'
        elif system == 'Darwin':
            style = 'macOS'

    if style == 'Fusion':
        if system == 'Windows':
            WIND_HEIGHT_ADJUST = 2
            DIAG_HEIGHT_ADJUST = -4
            TABLE_ADJUST = 2
            LIST_HEADER_FONT_SIZE = 0   # Let system default
            LIST_LINE_FONT_SIZE = 0     # Let system default
            LIST_STYLESHEET = 'QTableView { color:black; background-color:#FAFAFA }'
            LIST_HEADER_STYLESHEET = '''
                QHeaderView::section {
                    border-width: 0px 0px 1px 0px;
                    border-color: grey
                }
                '''
        elif system == 'Darwin':
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
    elif style == 'Windows':
        WIND_HEIGHT_ADJUST = -1
        DIAG_HEIGHT_ADJUST = 0
        TABLE_ADJUST = 4
        LIST_HEADER_FONT_SIZE = 0   # Let system default
        LIST_LINE_FONT_SIZE = 0     # Let system default
        LIST_STYLESHEET = 'QTableView { color:black; background-color:#FAFAFA }'
        LIST_HEADER_STYLESHEET = '''
            QHeaderView::section {
                border-width: 0px 0px 1px 0px;
                border-style: solid;
                border-color: grey
            }
            '''
    elif style == 'macOS':
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

    if style in keys:
        QtWidgets.QApplication.setStyle(QtWidgets.QStyleFactory.create(style))


### Compute table height based on nb of rows
def table_height(row_nb):
    return LmConf.ListHeaderHeight + (LmConf.ListLineHeight * row_nb) + TABLE_ADJUST


### Compute base height of a window based on nb of rows of a single table
def window_height(row_nb):
    return table_height(row_nb) + WIND_HEIGHT_ADJUST


### Compute base height of a dialog based on nb of rows of a single table
def dialog_height(row_nb):
    return table_height(row_nb) + DIAG_HEIGHT_ADJUST


### Assign Tooltips to all QWidgets in a window/dialog/tab
def set_tooltips(qt_object, key):
    if LmConf.Tooltips:
        item_list = qt_object.findChildren(QtWidgets.QWidget, options = QtCore.Qt.FindChildOption.FindDirectChildrenOnly)
        for item in item_list:
            k = item.objectName()
            if len(k):
                if isinstance(item, QtWidgets.QTableWidget):
                    h = item.horizontalHeader()
                    m = h.model()
                    for c in range(h.count()):
                        k = m.headerData(c, QtCore.Qt.Orientation.Horizontal, QtCore.Qt.ItemDataRole.UserRole)
                        if k is not None:
                            item.horizontalHeaderItem(c).setToolTip(LmLanguages.get_tooltip(key, k))
                elif isinstance(item, QtWidgets.QTabWidget):
                    for i in range(item.count()):
                        k = item.widget(i).objectName()
                        if len(k):
                            item.setTabToolTip(i, LmLanguages.get_tooltip(key, k))
                elif isinstance(item, QtWidgets.QGroupBox):
                    # Set tooltip to the group if any
                    item.setToolTip(LmLanguages.get_tooltip(key, k))
                    # Recursive call to handle group content
                    set_tooltips(item, key)
                else:
                    item.setToolTip(LmLanguages.get_tooltip(key, k))


### Setup configuration according to Livebox model
def set_livebox_model(model):
    global INTF_NAME_MAP

    match model:
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
def release_check():
    # Call GitHub API to fetch latest release infos
    try:
        d = requests.get(GITRELEASE_URL.format(GIT_REPO), timeout=1)
        d = json.loads(d.content)
        v = d['tag_name']
    except BaseException as e:
        LmTools.error(f'Cannot get latest release infos. Error: {e}')
        return

    # Convert version string into hex int aligned with __build__ representation
    s = v.split('.')
    l = len(s)
    major = s[0]
    if l >= 2:
        minor = s[1]
    else:
        minor = '00'
    if l >= 3:
        patch = s[2]
    else:
        patch = '00'
    try:
        r = int(major.zfill(2) + minor.zfill(2) + patch.zfill(2), 16)
    except BaseException as e:
        LmTools.error(f'Cannot decode latest release infos. Error: {e}')
        return

    # Warn if this release is not the latest
    if (r > __build__) and (LmConf.NoReleaseWarning != r):
        release_warning_dialog = ReleaseWarningDialog(v)
        if release_warning_dialog.exec():
            return
        # User decided to not be warned again, remember in config
        LmConf.NoReleaseWarning = r
        LmConf.save()


### Get a cross platform 32 bytes unique hardware key as base64 string
def get_hardware_key():
    # Use platform calls to get a unique string
    hardware_id = platform.system() + platform.machine() + platform.node() + platform.processor()

    # Hashing to 32 bytes array
    hardware_hash = hashlib.sha256(hardware_id.encode('utf-8')).digest()

    # Return as 44-chars base64 string
    return base64.urlsafe_b64encode(hardware_hash).decode('utf-8')



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
    RealtimeWifiStats_save = RealtimeWifiStats  # Need to decouple saving as master value must not be changed live
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
    NativeRun = True    # Run mode - Python script (True) / PyPI package (False)
    CsvDelimiter = DCFG_CSV_DELIMITER
    TimeoutMargin = DCFG_TIMEOUT_MARGIN
    PreventSleep = DCFG_PREVENT_SLEEP
    SavePasswords = DCFG_SAVE_PASSWORDS


    ### Load configuration, returns False the program aborts starting
    @staticmethod
    def load():
        # First load secret key
        if not LmConf.load_key():
            return False

        config_file = None
        dirty_config = False
        config_file_path = os.path.join(LmConf.get_config_directory(), CONFIG_FILE)
        LmTools.log_debug(1, 'Reading configuration in', config_file_path)
        try:
            config_file = open(config_file_path)
            config = json.load(config_file)
        except OSError:
            LmTools.error('No configuration file, creating one.')
            dirty_config = True
        except BaseException as e:
            LmTools.error(str(e))
            if LmTools.ask_question(mx('Wrong {} file, fully reset it?', 'wrongFile').format(CONFIG_FILE)):
                dirty_config = True
            else:
                if config_file is not None:
                    config_file.close()
                return False
        else:
            # Try to load language as soon as possible
            p = config.get('Language')
            if p is not None:
                LmConf.Language = str(p)
                if LmConf.Language not in LmLanguages.LANGUAGES_KEY:
                    LmConf.Language = DCFG_LANGUAGE
            LmLanguages.set_language(LmConf.Language)

            # Check if config version is more recent than the application
            config_version = config.get('Version', 0)
            if config_version > __build__:
                if not LmTools.ask_question(mx('This version of the application is older than the configuration file.\n'
                                               'If you continue you might lose some setup.\n'
                                               'Are you sure you want to continue?', 'configVersion')):
                    return False

            # Potentially convert the format to newer version
            dirty_config = LmConf.convert(config)

            # Load all configs
            p = config.get('Profiles')
            if p is not None:
                LmConf.Profiles = p
                ok, dirty = LmConf.select_profile()
                if ok:
                    if dirty:
                        dirty_config = True
                else:
                    return False
            if LmConf.CurrProfile is None:
                raise Exception('No profile detected')
            p = config.get('Tooltips')
            if p is not None:
                LmConf.Tooltips = bool(p)
            p = config.get('Stats Frequency')
            if p is not None:
                LmConf.StatsFrequency = int(p)
            p = config.get('MacAddr API Key')
            if p is not None:
                LmConf.MacAddrApiKey = p
            p = config.get('CallFilter API Key')
            if p is not None:
                LmConf.CallFilterApiKey = p
            p = config.get('Phone Code')
            if p is not None:
                LmConf.PhoneCode = str(p)
            p = config.get('List Header Height')
            if p is not None:
                LmConf.ListHeaderHeight = int(p)
            p = config.get('List Header Font Size')
            if p is not None:
                LmConf.ListHeaderFontSize = int(p)
            p = config.get('List Line Height')
            if p is not None:
                LmConf.ListLineHeight = int(p)
            p = config.get('List Line Font Size')
            if p is not None:
                LmConf.ListLineFontSize = int(p)
            p = config.get('Realtime Wifi Stats')
            if p is not None:
                LmConf.RealtimeWifiStats = bool(p)
                LmConf.RealtimeWifiStats_save = LmConf.RealtimeWifiStats
            p = config.get('Native UI Style')
            if p is not None:
                LmConf.NativeUIStyle = bool(p)
            p = config.get('Log Level')
            if p is not None:
                LmConf.LogLevel = int(p)
                if LmConf.LogLevel < 0:
                    LmConf.LogLevel = 0
                elif LmConf.LogLevel > 2:
                    LmConf.LogLevel = 2
                LmTools.set_verbosity(LmConf.LogLevel)
            p = config.get('No Release Warning')
            if p is not None:
                LmConf.NoReleaseWarning = int(p)
            p = config.get('Repeaters')
            if p is not None:
                LmConf.Repeaters = p
            p = config.get('Graph')
            if p is not None:
                LmConf.Graph = p
            p = config.get('Tabs')
            if p is not None:
                LmConf.Tabs = p
            p = config.get('NotificationRules')
            if p is not None:
                LmConf.NotificationRules = p
            p = config.get('NotificationFlushFrequency')
            if p is not None:
                LmConf.NotificationFlushFrequency = int(p)
            p = config.get('NotificationFilePath')
            if p is not None:
                LmConf.NotificationFilePath = p
            p = config.get('email')
            if p is not None:
                LmConf.Email = p
            p = config.get('CSV Delimiter')
            if p is not None:
                LmConf.CsvDelimiter = str(p)
                if len(LmConf.CsvDelimiter):
                    LmConf.CsvDelimiter = LmConf.CsvDelimiter[0]
                else:
                    LmConf.CsvDelimiter = DCFG_CSV_DELIMITER
            p = config.get('Timeout Margin')
            if p is not None:
                LmConf.TimeoutMargin = int(p)
                if LmConf.TimeoutMargin < 0:
                    LmConf.TimeoutMargin = 0
            p = config.get('Prevent Sleep')
            if p is not None:
                LmConf.PreventSleep = bool(p)
            p = config.get('Save Passwords')
            if p is not None:
                LmConf.SavePasswords = bool(p)

        if config_file is not None:
            config_file.close()

        if dirty_config:
            LmConf.save()

        LmConf.apply()

        return True


    ### Load key file, creating one if not present, returns False if fails
    @staticmethod
    def load_key():
        config_path = LmConf.get_config_directory()
        key_file = None
        key = None
        key_file_path = os.path.join(config_path, KEY_FILE)

        # Get unique hardware key
        hw_key = get_hardware_key()

        # Read file if it exists
        LmTools.log_debug(1, 'Reading key file in', key_file_path)
        try:
            key_file = open(key_file_path, 'rb')
            key = key_file.read()
            key_file.close()
        except OSError:
            LmTools.error('No key file, creating one.')
            key = None
        except BaseException as e:
            LmTools.error(str(e))
            LmTools.display_error(mx('Cannot read key file.', 'keyFileErr'))
            if key_file is not None:
                key_file.close()
                return False
        else:
            # Decrypt key to get secret
            try:
                LmConf.Secret = Fernet(hw_key.encode('utf-8')).decrypt(key).decode('utf-8')
            except:
                LmTools.error('Invalid key file, recreating it.')
            else:
                return True

        # Create config directory if doesn't exist
        if not os.path.isdir(config_path):
            LmTools.log_debug(1, 'Creating config directory', config_path)
            try:
                os.makedirs(config_path)
            except BaseException as e:
                LmTools.error(f'Cannot create configuration folder. Error: {e}')
                LmTools.display_error(mx('Cannot create configuration folder.', 'configFolderErr'))
                return False

        # Create key file
        LmConf.Secret = Fernet.generate_key().decode()
        key = Fernet(hw_key.encode('utf-8')).encrypt(LmConf.Secret.encode('utf-8'))
        LmTools.log_debug(1, 'Creating key file', key_file_path)
        try:
            with open(key_file_path, 'wb') as key_file:
                key_file.write(key)
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
    def apply_saved_prefs():
        LmConf.RealtimeWifiStats = LmConf.RealtimeWifiStats_save


    ### Select a profile in the profile list depending on default parameters
    #   Returns a tuple of 2 booleans: 1/ False if user cancels, 2/ True if config needs to be saved
    @staticmethod
    def select_profile():
        # First search for a default profile
        LmConf.CurrProfile = next((p for p in LmConf.Profiles if p['Default']), None)

        # Find dynamically if no default, take the first
        if LmConf.CurrProfile is None:
            # First collect reachable profiles and those matching Livebox's MAC address
            LmTools.mouse_cursor_busy()
            for p in LmConf.Profiles:
                livebox_mac = LiveboxInfoApi.get_livebox_mac_nosign(p.get('Livebox URL'))
                if (livebox_mac is not None) and (livebox_mac == p.get('Livebox MacAddr')):
                    LmConf.CurrProfile = p
                    break
            LmTools.mouse_cursor_normal()

        # If no match/default found or if Ctrl key pressed, ask for it
        modifiers = QtGui.QGuiApplication.queryKeyboardModifiers()
        dirty_config = False
        if (LmConf.CurrProfile is None) or (modifiers == QtCore.Qt.KeyboardModifier.ControlModifier):
            r = LmConf.ask_profile()
            if r == 0:
                return False, False
            elif r == 2:
                if LmConf.create_profile():
                    dirty_config = True
                else:
                    return False, False

        if LmConf.CurrProfile is not None:
            LmConf.assign_profile()

        return True, dirty_config


    ### Ask user to choose a profile, returns 0 if user cancels, 1 if one selected, 2 if need to create a new one
    @staticmethod
    def ask_profile():
        if len(LmConf.Profiles) == 0:
            return 1

        from LiveboxMonitor.dlg.LmSelectProfile import SelectProfileDialog

        select_profile_dialog = SelectProfileDialog()
        if select_profile_dialog.exec():
            if select_profile_dialog.do_create_profile():
                return 2
            LmConf.CurrProfile = LmConf.Profiles[select_profile_dialog.profile_index()]
            return 1
        return 0


    ### Create a new profile, return False is user cancelled
    #staticmethod
    def create_profile():
        # Loop until finding a unique name or user cancels
        while True:
            name, ok = QtWidgets.QInputDialog.getText(None, lx('Create Profile'), lx('Profile name:'))
            if ok:
                q = next((p for p in LmConf.Profiles if p['Name'] == name), None)
                if q is None:
                    break
                else:
                    LmTools.display_error(mx('This name is already used.', 'profileNameErr'))
            else:
                return False

        # Create a new profile with default values
        p = {}
        p['Name'] = name
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
    def assign_profile():
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
    def convert(config):
        dirty_config = False
        version = config.get('Version')

        if version is None:
            version = LmConf.convert_for_096(config)
            dirty_config = True

        if version <= 0x010400:
            version = LmConf.convert_for_150(config)

        return dirty_config


    ### Adapt config format to 0.9.6 version, return corresponding version number
    @staticmethod
    def convert_for_096(config):
        v = 0x000906
        config['Version'] = v

        # Convert Livebox parameters into main profile
        profiles = []
        main_profile = {}

        main_profile['Name'] = lx('Main')
        main_profile['Livebox URL'] = config.get('Livebox URL', DCFG_LIVEBOX_URL)
        main_profile['Livebox User'] = config.get('Livebox User', DCFG_LIVEBOX_USER)
        main_profile['Livebox Password'] = config.get('Livebox Password', DCFG_LIVEBOX_PASSWORD)
        main_profile['Filter Devices'] = config.get('Filter Devices', DCFG_FILTER_DEVICES)
        main_profile['MacAddr Table File'] = config.get('MacAddr Table File', DCFG_MACADDR_TABLE_FILE)
        main_profile['Default'] = True
        profiles.append(main_profile)

        config['Profiles'] = profiles

        return v


    ### Adapt config format to 1.5.0 version, return corresponding version number
    @staticmethod
    def convert_for_150(config):
        v = 0x010500
        config['Version'] = v

        # Remove all profile passwords following security key management evolution
        profiles = config.get('Profiles')
        if profiles is not None:
            for p in profiles:
                p['Livebox Password'] = None

        # Remove all repeaters passwords following security key management evolution
        repeaters = config.get('Repeaters')
        if repeaters is not None:
            for r in repeaters:
                repeaters[r]['Password'] = None

        return v


    ### Save configuration file
    @staticmethod
    def save():
        config_path = LmConf.get_config_directory()

        # Create config directory if doesn't exist
        if not os.path.isdir(config_path):
            LmTools.log_debug(1, 'Creating config directory', config_path)
            try:
                os.makedirs(config_path)
            except BaseException as e:
                LmTools.error(f'Cannot create configuration folder. Error: {e}')
                return

        config_file_path = os.path.join(config_path, CONFIG_FILE)
        LmTools.log_debug(1, 'Saving configuration in', config_file_path)
        try:
            with open(config_file_path, 'w') as config_file:
                config = {}
                config['Version'] = __build__
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
                config['Profiles'] = LmConf.Profiles
                config['Language'] = LmConf.Language
                config['Tooltips'] = LmConf.Tooltips
                config['Stats Frequency'] = LmConf.StatsFrequency
                config['MacAddr API Key'] = LmConf.MacAddrApiKey
                config['CallFilter API Key'] = LmConf.CallFilterApiKey
                config['Phone Code'] = LmConf.PhoneCode
                config['List Header Height'] = LmConf.ListHeaderHeight
                config['List Header Font Size'] = LmConf.ListHeaderFontSize
                config['List Line Height'] = LmConf.ListLineHeight
                config['List Line Font Size'] = LmConf.ListLineFontSize
                config['Realtime Wifi Stats'] = LmConf.RealtimeWifiStats_save
                config['Native UI Style'] = LmConf.NativeUIStyle
                config['Log Level'] = LmConf.LogLevel
                config['No Release Warning'] = LmConf.NoReleaseWarning
                config['Repeaters'] = LmConf.Repeaters
                config['Graph'] = LmConf.Graph
                config['Tabs'] = LmConf.Tabs
                config['NotificationRules'] = LmConf.NotificationRules
                config['NotificationFlushFrequency'] = LmConf.NotificationFlushFrequency
                config['NotificationFilePath'] = LmConf.NotificationFilePath
                config['email'] = LmConf.Email
                config['CSV Delimiter'] = LmConf.CsvDelimiter
                config['Timeout Margin'] = LmConf.TimeoutMargin
                config['Prevent Sleep'] = LmConf.PreventSleep
                config['Save Passwords'] = LmConf.SavePasswords
                json.dump(config, config_file, indent=4)
        except BaseException as e:
            LmTools.error(f'Cannot save configuration file. Error: {e}')


    ### Set Livebox password
    @staticmethod
    def set_livebox_url(url):
        LmConf.LiveboxURL = url
        LmConf.save()


    ### Set Livebox password
    @staticmethod
    def set_livebox_user_password(user, password):
        LmConf.LiveboxUser = user
        LmConf.LiveboxPassword = password
        LmConf.save()


    ### Set Livebox MAC address
    @staticmethod
    def set_livebox_mac(mac_addr):
        if LmConf.LiveboxMAC != mac_addr:
            LmConf.LiveboxMAC = mac_addr
            LmConf.save()


    ### Set log level
    @staticmethod
    def set_log_level(level):
        if level < 0:
            level = 0
        elif level > 2:
            level = 2
        LmConf.LogLevel = level
        LmTools.set_verbosity(level)
        LmConf.save()


    ### Get password of a repeater given its MAC address
    @staticmethod
    def get_repeater_user_password(mac_addr):
        # First look up for a specific password
        if LmConf.Repeaters is not None:
            repeater_conf = LmConf.Repeaters.get(mac_addr, None)
            if repeater_conf is not None:
                user = repeater_conf.get('User', '')
                p = repeater_conf.get('Password')
                if p is None:
                    password = LmConf.LiveboxPassword
                else:
                    try:
                        password = Fernet(LmConf.Secret.encode('utf-8')).decrypt(p.encode('utf-8')).decode('utf-8')
                    except:
                        LmTools.error('Cannot decrypt repeater password.')
                        password = LmConf.LiveboxPassword
                return user, password

        # Defaut to Livebox user & password
        return LmConf.LiveboxUser, LmConf.LiveboxPassword


    ### Set password of a repeater given its MAC address
    @staticmethod
    def set_repeater_password(mac_addr, password):
        # Init repeater conf root if not present
        if LmConf.Repeaters is None:
            LmConf.Repeaters = {}

        # Retrieve conf of given repeater, init it if not present
        repeater_conf = LmConf.Repeaters.get(mac_addr, None)
        if repeater_conf is None:
            repeater_conf = {}
            LmConf.Repeaters[mac_addr] = repeater_conf

        # Init user name if not present
        user = repeater_conf.get('User')
        if user is None:
            repeater_conf['User'] = LmConf.LiveboxUser

        # Setup password
        if LmConf.SavePasswords:
            repeater_conf['Password'] = Fernet(LmConf.Secret.encode('utf-8')).encrypt(password.encode('utf-8')).decode('utf-8')
        else:
            repeater_conf['Password'] = None

        # Save to config file
        LmConf.save()


    ### Load MAC address table
    @staticmethod
    def load_mac_addr_table():
        mac_addr_table_file_path = os.path.join(LmConf.get_config_directory(), LmConf.MacAddrTableFile)
        try:
            with open(mac_addr_table_file_path) as mac_table_file:
                LmConf.MacAddrTable = json.load(mac_table_file)
        except OSError:     # No file
            LmConf.MacAddrTable = {}
        except BaseException as e:
            LmTools.display_error(mx('Wrong {} file format, cannot use.', 'wrongMacFile').format(LmConf.MacAddrTableFile))
            LmConf.MacAddrTable = {}


    ### Save MAC address table
    @staticmethod
    def save_mac_addr_table():
        config_path = LmConf.get_config_directory()

        # Create config directory if doesn't exist
        if not os.path.exists(config_path):
            try:
                os.makedirs(config_path)
            except BaseException as e:
                LmTools.error(f'Cannot create configuration folder. Error: {e}')
                return

        mac_addr_table_file_path = os.path.join(config_path, LmConf.MacAddrTableFile)
        try:
            with open(mac_addr_table_file_path, 'w') as mac_table_file:
                json.dump(LmConf.MacAddrTable, mac_table_file, indent=4)
        except BaseException as e:
            LmTools.error(f'Cannot save MacAddress file. Error: {e}')


    ### Load spam calls table
    @staticmethod
    def load_spam_calls_table():
        spam_calls_table_file_path = os.path.join(LmConf.get_config_directory(), SPAMCALLS_FILE)
        try:
            with open(spam_calls_table_file_path) as f:
                t = json.load(f)
                if isinstance(t, list):
                    LmConf.SpamCallsTable = t
                else:
                    LmTools.display_error(mx('Wrong {} file format, cannot use.', 'wrongSpamCallsFile').format(SPAMCALLS_FILE))
                    LmConf.SpamCallsTable = []
        except OSError:     # No file
            LmConf.SpamCallsTable = []
        except BaseException as e:
            LmTools.display_error(mx('Wrong {} file format, cannot use.', 'wrongSpamCallsFile').format(SPAMCALLS_FILE))
            LmConf.SpamCallsTable = []


    ### Declare a phone nb as spam
    @staticmethod
    def set_spam_call(phone_nb):
        if phone_nb not in LmConf.SpamCallsTable:
            LmConf.SpamCallsTable.append(phone_nb)
            LmConf.save_spam_calls_table()


    ### Undeclare a phone nb as spam
    @staticmethod
    def unset_spam_call(phone_nb):
        if phone_nb in LmConf.SpamCallsTable:
            LmConf.SpamCallsTable.remove(phone_nb)
            LmConf.save_spam_calls_table()


    ### Save spam calls table
    @staticmethod
    def save_spam_calls_table():
        config_path = LmConf.get_config_directory()

        # Create config directory if doesn't exist
        if not os.path.exists(config_path):
            try:
                os.makedirs(config_path)
            except BaseException as e:
                LmTools.error(f'Cannot create configuration folder. Error: {e}')
                return

        spam_calls_table_file_path = os.path.join(config_path, SPAMCALLS_FILE)
        try:
            with open(spam_calls_table_file_path, 'w') as f:
                json.dump(LmConf.SpamCallsTable, f, indent = 4)
        except BaseException as e:
            LmTools.error(f'Cannot save spam calls file. Error: {e}')


    ### Set native run
    @staticmethod
    def set_native_run(native_run):
        LmConf.NativeRun = native_run


    ### Determine config files directory
    @staticmethod
    def get_config_directory():
        if hasattr(sys, 'frozen') or not LmConf.NativeRun:
            # If program is built with PyInstaller, use standard OS dirs
            system =  platform.system()
            if system == 'Windows':
                return os.path.join(os.environ['APPDATA'], 'LiveboxMonitor')
            elif system == 'Darwin':
                return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'LiveboxMonitor')
            else:
                return os.path.join(os.path.expanduser('~'), '.config', 'LiveboxMonitor')
        else:
            # If program is Python script mode, use local dir
            return '.'


    ### Get a device icon from cache file
    @staticmethod
    def get_device_icon_cache(device, lb_soft_version):
        icon_pixmap = None
        icon_dir_path = os.path.join(LmConf.get_config_directory(), LIVEBOX_CACHE_DIR + lb_soft_version, LIVEBOX_ICON_CACHE_DIR)
        icon_file_path = os.path.join(icon_dir_path, device['Icon'])
        if os.path.isfile(icon_file_path):
            icon_pixmap = QtGui.QPixmap()
            if not icon_pixmap.load(icon_file_path):
                icon_pixmap = None
                LmTools.error(f'Cannot load device icon cache file {icon_file_path}. Cache file will be recreated.')
        return icon_pixmap


    ### Set a device icon to cache file
    @staticmethod
    def set_device_icon_cache(device, lb_soft_version, content):
        icon_dir_path = os.path.join(LmConf.get_config_directory(), LIVEBOX_CACHE_DIR + lb_soft_version, LIVEBOX_ICON_CACHE_DIR)
        icon_file_path = os.path.join(icon_dir_path, device['Icon'])

        # Create icon cache directory if doesn't exist
        if not os.path.isdir(icon_dir_path):
            try:
                os.makedirs(icon_dir_path)
            except BaseException as e:
                LmTools.error(f'Cannot create icon cache folder {icon_dir_path}. Error: {e}')
                return

        # Create and save icon cache file
        try:
            with open(icon_file_path, 'wb') as icon_file:
                icon_file.write(content)
        except BaseException as e:
            LmTools.error(f'Cannot save icon cache file {icon_file_path}. Error: {e}')


    ### Get a device icon
    @staticmethod
    def get_device_icon(device, lb_soft_version):
        if LmConf.AllDeviceIconsLoaded:
            return device['PixMap']
        else:
            icon_pixmap = device.get('PixMap', None)

            # First try to get icon from local cache
            if icon_pixmap is None:
                icon_pixmap = LmConf.get_device_icon_cache(device, lb_soft_version)

            # Ultimately load the icon from Livebox URL
            if icon_pixmap is None:
                icon_pixmap = QtGui.QPixmap()
                store_in_cache = False
                try:
                    icon_data = requests.get(LmConf.LiveboxURL + ICON_URL + device['Icon'],
                                             timeout=DEFAULT_TIMEOUT + LmConf.TimeoutMargin,
                                             verify=LmConf.LiveboxURL.startswith('http://'))
                    if icon_pixmap.loadFromData(icon_data.content):
                        store_in_cache = True
                    else:
                        LmTools.error(f'Cannot load device icon {device["Icon"]}.')
                except requests.exceptions.Timeout as e:
                    LmTools.error(f'Device icon {device["Icon"]} request timeout error: {e}.')
                except BaseException as e:
                    LmTools.error(f'{e}. Cannot request device icon {device["Icon"]}.')

                # If successfully loaded, try to store in local cache file for faster further loads
                if store_in_cache:
                    LmConf.set_device_icon_cache(device, lb_soft_version, icon_data.content)

            device['PixMap'] = icon_pixmap
            return icon_pixmap


    ### Load all device icons
    @staticmethod
    def load_device_icons(lb_soft_version):
        if not LmConf.AllDeviceIconsLoaded:
            for d in DEVICE_TYPES:
                LmConf.get_device_icon(d, lb_soft_version)

            LmConf.AllDeviceIconsLoaded = True


    ### Load custom device icons
    @staticmethod
    def load_custom_device_icons():
        global DEVICE_TYPES

        # Get custom icon directory path
        custom_icon_dir_path = os.path.join(LmConf.get_config_directory(), CUSTOM_ICON_DIR)
        if not os.path.isdir(custom_icon_dir_path):
            return

        # Iterate over all files in the custom icon directory
        sort_device_types = False
        for f in os.listdir(custom_icon_dir_path):
            icon_file_name = os.fsdecode(f)
            if icon_file_name.endswith('.png'):
                icon_file_path = os.path.join(custom_icon_dir_path, icon_file_name)
                icon_pixmap = QtGui.QPixmap()
                if icon_pixmap.load(icon_file_path):
                    # Search if device icon name is already referenced
                    create_device_entry = True
                    for d in DEVICE_TYPES:
                        if d['Icon'] == icon_file_name:
                            create_device_entry = False
                            d['PixMap'] = icon_pixmap

                    # Search if device name is already referenced as key
                    device_name = os.path.splitext(icon_file_name)[0]
                    if create_device_entry:
                        for d in DEVICE_TYPES:
                            if d['Key'] == device_name:
                                create_device_entry = False
                                d['Icon'] = icon_file_name
                                d['PixMap'] = icon_pixmap
                                break

                    # If doesn't exit, create it
                    if create_device_entry:
                        device = {}
                        device['Key'] = device_name
                        device['Name'] = device_name
                        device['Icon'] = icon_file_name
                        device['PixMap'] = icon_pixmap
                        DEVICE_TYPES.append(device)
                        sort_device_types = True
                else:
                    LmTools.error(f'Cannot load custom device icon {icon_file_path}.')

        # Resort device type list if required
        if sort_device_types:
            DEVICE_TYPES = sorted(DEVICE_TYPES, key = lambda x: x['Name'])


    ### Load, check and return email configuration
    @staticmethod
    def load_email_setup():
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

        password = ''
        p = c.get('Password')
        if p is not None:
            try:
                password = Fernet(LmConf.Secret.encode('utf-8')).decrypt(p.encode('utf-8')).decode('utf-8')
            except:
                LmTools.error('Cannot decrypt email password.')
        e['Password'] = password

        return e


    ### Set email configuration
    @staticmethod
    def set_email_setup(email_setup):
        p = email_setup['Password']
        try:
            email_setup['Password'] = Fernet(LmConf.Secret.encode('utf-8')).encrypt(p.encode('utf-8')).decode('utf-8')
        except:
            LmTools.error('Cannot encrypt email password.')
            email_setup['Password'] = ''
        LmConf.Email = email_setup
