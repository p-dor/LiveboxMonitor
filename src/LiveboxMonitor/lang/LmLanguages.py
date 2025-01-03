### Livebox Monitor Languages module ###

from LiveboxMonitor.lang import LmLanguage_EN, LmLanguage_FR


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
CURRENT_LANGUAGE = 'FR'

# Supported languages
LANGUAGES_KEY = [ 'FR', 'EN' ]
LANGUAGES_NAME = [ 'Français', 'English']
LANGUAGES_LOCALE = { 'FR': 'fr_FR', 'EN': 'en_US' }

# Labels & Tooltips - to set according to current language
LABELS = LmLanguage_FR.LABELS
TOOLTIPS = LmLanguage_FR.TOOLTIPS
MESSAGES = LmLanguage_FR.MESSAGES


# ################################ Tools ################################

# Setup according to selected language
def SetLanguage(iLanguage):
	global CURRENT_LANGUAGE
	global LABELS
	global TOOLTIPS
	global MESSAGES

	CURRENT_LANGUAGE = iLanguage
	if iLanguage == 'FR':
		LABELS = LmLanguage_FR.LABELS
		TOOLTIPS = LmLanguage_FR.TOOLTIPS
		MESSAGES = LmLanguage_FR.MESSAGES
	elif iLanguage == 'EN':
		TOOLTIPS = LmLanguage_EN.TOOLTIPS
	else:
		TOOLTIPS = LmLanguage_EN.TOOLTIPS


# Get label translation
def GetLabel(iKey, iString):
	if CURRENT_LANGUAGE == 'EN':
		return iString
	return LABELS[iKey].get(iString, iString)


# Get item tooltip
def GetToolTip(iKey, iItemKey):
	return TOOLTIPS[iKey].get(iItemKey)


# Get message translation
def GetMessage(iKey, iString, iItemKey):
	if CURRENT_LANGUAGE == 'EN':
		return iString
	m = MESSAGES[iKey].get(iItemKey)
	return m if m else iString



# ################################ Specialized Tools ################################

# Main
def GetMainLabel(iString): return GetLabel('main', iString)
def GetMainMessage(iString, iKey): return GetMessage('main', iString, iKey)

# Device list
def GetDeviceListLabel(iString): return GetLabel('dlist', iString)
def GetDeviceListMessage(iString, iKey): return GetMessage('dlist', iString, iKey)
def GetIPv6DialogLabel(iString): return GetLabel('ipv6', iString)
def GetDnsDialogLabel(iString): return GetLabel('dns', iString)

# Livebox infos
def GetInfoLabel(iString): return GetLabel('info', iString)
def GetInfoMessage(iString, iKey): return GetMessage('info', iString, iKey)

# Graph
def GetGraphLabel(iString): return GetLabel('graph', iString)
def GetGraphMessage(iString, iKey): return GetMessage('graph', iString, iKey)
def GetAddGraphDialogLabel(iString): return GetLabel('addgraph', iString)

# Device infos
def GetDeviceInfoLabel(iString): return GetLabel('dinfo', iString)
def GetDeviceInfoMessage(iString, iKey): return GetMessage('dinfo', iString, iKey)
def GetDeviceNameDialogLabel(iString): return GetLabel('dname', iString)
def GetDeviceTypeDialogLabel(iString): return GetLabel('dtype', iString)

# Events
def GetEventsLabel(iString): return GetLabel('events', iString)
def GetEventsMessage(iString, iKey): return GetMessage('events', iString, iKey)
def GetNotificationRulesLabel(iString): return GetLabel('evnrules', iString)

# DHCP
def GetDhcpLabel(iString): return GetLabel('dhcp', iString)
def GetDhcpMessage(iString, iKey): return GetMessage('dhcp', iString, iKey)
def GetDhcpBindingDialogLabel(iString): return GetLabel('dbinding', iString)
def GetDhcpSetupDialogLabel(iString): return GetLabel('dsetup', iString)

# NAT/PAT
def GetNatPatLabel(iString): return GetLabel('natpat', iString)
def GetNatPatMessage(iString, iKey): return GetMessage('natpat', iString, iKey)
def GetPatRuleDialogLabel(iString): return GetLabel('patrule', iString)
def GetPtfRuleDialogLabel(iString): return GetLabel('ptfrule', iString)
def GetNatPatRuleTypeDialogLabel(iString): return GetLabel('nprtype', iString)

# Phone
def GetPhoneLabel(iString): return GetLabel('phone', iString)
def GetPhoneMessage(iString, iKey): return GetMessage('phone', iString, iKey)
def GetPhoneContactDialogLabel(iString): return GetLabel('pcontact', iString)

# Actions
def GetActionsLabel(iString): return GetLabel('actions', iString)
def GetActionsMessage(iString, iKey): return GetMessage('actions', iString, iKey)
def GetActionsRHistoryDialogLabel(iString): return GetLabel('rhistory', iString)
def GetActionsWGlobalDialogLabel(iString): return GetLabel('wglobal', iString)
def GetActionsBackupRestoreDialogLabel(iString): return GetLabel('backrest', iString)
def GetActionsFirewallLevelDialogLabel(iString): return GetLabel('fwlevel', iString)
def GetActionsPingResponseDialogLabel(iString): return GetLabel('pingr', iString)
def GetActionsDynDnsDialogLabel(iString): return GetLabel('dyndns', iString)
def GetActionsDmzDialogLabel(iString): return GetLabel('dmz', iString)

# Repeater
def GetRepeaterLabel(iString): return GetLabel('repeater', iString)
def GetRepeaterMessage(iString, iKey): return GetMessage('repeater', iString, iKey)

# Config
def GetConfigPrefsDialogLabel(iString): return GetLabel('prefs', iString)
def GetConfigMessage(iString, iKey): return GetMessage('prefs', iString, iKey)
def GetConfigCnxDialogLabel(iString): return GetLabel('cnx', iString)
def GetConfigSigninDialogLabel(iString): return GetLabel('signin', iString)
def GetConfigEmailDialogLabel(iString): return GetLabel('email', iString)
def GetSelectProfileDialogLabel(iString): return GetLabel('sprofile', iString)
def GetReleaseWarningDialogLabel(iString): return GetLabel('rwarn', iString)

# Tools
def GetToolsLabel(iString): return GetLabel('tools', iString)
