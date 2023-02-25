### Livebox Monitor Languages module ###

from src import LmLanguage_EN
from src import LmLanguage_FR


# ################################ Guidelines ################################

# To create a new language:
# - Create LmLanguage_XX module, XX being the language code.
# - Add language code in LANGUAGES_KEY list.
# - Add language name in LANGUAGES_NAME list.
# - Assign LABELS & TOOLS according to language code in SetLanguage().

# Rules for Labels:
# - One function per window/area, using a specific ID / aliased in the module (lx, lix, etc)
# - For each ID, set of keys/values.
# - The native label is the key, translation is the value.
# - If no key found, native label is used.

# Rules for Tooltips:
# - Each window/dialog calls LmConfig.SetToolTips() with a specific ID.
# - For each ID, set of keys/values. Keys designate UI object, value the tooltip to display.
# - If no key found, no tooltip is displayed.
# - Rules for the keys:
#   - Only objects with an assigned name are considered.
#   - QTableWidget -> keys are data with QtCore.Qt.ItemDataRole.UserRole assigned to each header
#   - QTabWidget -> keys are object names of each tab.
#   - All other objects -> keys are assigned object name.


# ################################ VARS & DEFS ################################

# Current language
CURRENT_LANGUAGE = 'EN'

# Supported languages
LANGUAGES_KEY = [ 'FR', 'EN' ]
LANGUAGES_NAME = [ 'Français', 'English']

# Labels & Tooltips - to set according to current language
LABELS = []
TOOLTIPS = []


# ################################ Tools ################################

# Setup according to selected language
def SetLanguage(iLanguage):
	global CURRENT_LANGUAGE
	global LABELS
	global TOOLTIPS

	CURRENT_LANGUAGE = iLanguage
	if iLanguage == 'FR':
		LABELS = LmLanguage_FR.LABELS
		TOOLTIPS = LmLanguage_FR.TOOLTIPS
	elif iLanguage == 'EN':
		TOOLTIPS = LmLanguage_EN.TOOLTIPS
	else:
		TOOLTIPS = LmLanguage_EN.TOOLTIPS


# Get EN label translation
def GetLabel(iKey, iString):
	if CURRENT_LANGUAGE == 'EN':
		return iString
	return LABELS[iKey].get(iString, iString)


# Get item tooltip
def GetToolTip(iKey, iItemKey):
	return TOOLTIPS[iKey].get(iItemKey)



# ################################ Specialized Tools ################################

# Main
def GetMainLabel(iString): return GetLabel('main', iString)

# Device list
def GetDeviceListLabel(iString): return GetLabel('dlist', iString)
def GetIPv6DialogLabel(iString): return GetLabel('ipv6', iString)

# Livebox infos
def GetInfoLabel(iString): return GetLabel('info', iString)

# Device infos
def GetDeviceInfoLabel(iString): return GetLabel('dinfo', iString)
def GetDeviceNameDialogLabel(iString): return GetLabel('dname', iString)
def GetDeviceTypeDialogLabel(iString): return GetLabel('dtype', iString)

# Events
def GetEventsLabel(iString): return GetLabel('events', iString)

# DHCP
def GetDhcpLabel(iString): return GetLabel('dhcp', iString)
def GetDhcpBindingDialogLabel(iString): return GetLabel('dbinding', iString)
def GetDhcpSetupDialogLabel(iString): return GetLabel('dsetup', iString)

# Phone
def GetPhoneLabel(iString): return GetLabel('phone', iString)
def GetPhoneContactDialogLabel(iString): return GetLabel('pcontact', iString)

# Actions
def GetActionsLabel(iString): return GetLabel('actions', iString)
def GetActionsRHistoryDialogLabel(iString): return GetLabel('rhistory', iString)
def GetActionsWGlobalDialogLabel(iString): return GetLabel('wglobal', iString)

# Repeater
def GetRepeaterLabel(iString): return GetLabel('repeater', iString)

# Config
def GetConfigPrefsDialogLabel(iString): return GetLabel('prefs', iString)
def GetConfigCnxDialogLabel(iString): return GetLabel('cnx', iString)
def GetConfigSigninDialogLabel(iString): return GetLabel('signin', iString)

# Tools
def GetToolsLabel(iString): return GetLabel('tools', iString)
