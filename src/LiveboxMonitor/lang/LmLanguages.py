### Livebox Monitor Languages module ###

from LiveboxMonitor.lang import LmLanguage_EN, LmLanguage_FR


# ################################ Guidelines ################################

# To create a new language:
# - Create LmLanguage_XX module, XX being the language code.
# - Add language code in LANGUAGES_KEY list.
# - Add language name in LANGUAGES_NAME list.
# - Assign LABELS & TOOLS according to language code in set_language().

# Rules for Labels:
# - One function per window/area, using a specific ID / aliased in the module (lx, lix, etc)
# - For each ID, set of keys/values.
# - The native label is the key, translation is the value.
# - If no key found, native label is used.

# Rules for Tooltips:
# - Each window/dialog calls LmConfig.set_tooltips() with a specific ID.
# - For each ID, set of keys/values. Keys designate UI object, value the tooltip to display.
# - If no key found, no tooltip is displayed.
# - Rules for the keys:
#   - Only objects with an assigned name are considered.
#   - QTableWidget -> keys are data with QtCore.Qt.ItemDataRole.UserRole assigned to each header
#   - QTabWidget -> keys are object names of each tab.
#   - All other objects -> keys are assigned object name.


# ################################ VARS & DEFS ################################

# Current language
current_language = "FR"

# Supported languages
LANGUAGES_KEY = ["FR", "EN"]
LANGUAGES_NAME = ["Français", "English"]
LANGUAGES_LOCALE = {"FR": "fr_FR", "EN": "en_US"}

# Labels & Tooltips - to set according to current language
labels = LmLanguage_FR.LABELS
tooltips = LmLanguage_FR.TOOLTIPS
messages = LmLanguage_FR.MESSAGES


# ################################ Tools ################################

# Setup according to selected language
def set_language(language):
    global current_language
    global labels
    global tooltips
    global messages

    current_language = language
    match language:
        case "FR":
            labels = LmLanguage_FR.LABELS
            tooltips = LmLanguage_FR.TOOLTIPS
            messages = LmLanguage_FR.MESSAGES
        case "EN":
            tooltips = LmLanguage_EN.TOOLTIPS
        case _:
            tooltips = LmLanguage_EN.TOOLTIPS


# Get label translation
def get_label(key, string):
    if current_language == "EN":
        return string
    return labels[key].get(string, string)


# Get item tooltip
def get_tooltip(key, item_key):
    return tooltips[key].get(item_key)


# Get message translation
def get_message(key, string, item_key):
    if current_language == "EN":
        return string
    m = messages[key].get(item_key)
    return m if m else string



# ################################ Specialized Tools ################################

# Main
def get_main_label(string): return get_label("main", string)
def get_main_message(string, key): return get_message("main", string, key)
def get_export_table_label(string): return get_label("export_table", string)

# Device list
def get_device_list_label(string): return get_label("dlist", string)
def get_device_list_message(string, key): return get_message("dlist", string, key)
def get_ipv6_label(string): return get_label("ipv6", string)
def get_dns_label(string): return get_label("dns", string)

# Livebox infos
def get_info_label(string): return get_label("info", string)
def get_info_message(string, key): return get_message("info", string, key)

# Graph
def get_graph_label(string): return get_label("graph", string)
def get_graph_message(string, key): return get_message("graph", string, key)
def get_add_graph_label(string): return get_label("addgraph", string)

# Device infos
def get_device_info_label(string): return get_label("dinfo", string)
def get_device_info_message(string, key): return get_message("dinfo", string, key)
def get_device_name_label(string): return get_label("dname", string)
def get_device_type_label(string): return get_label("dtype", string)

# Events
def get_events_label(string): return get_label("events", string)
def get_events_message(string, key): return get_message("events", string, key)
def get_notification_rules_label(string): return get_label("evnrules", string)

# DHCP
def get_dhcp_label(string): return get_label("dhcp", string)
def get_dhcp_message(string, key): return get_message("dhcp", string, key)
def get_dhcp_binding_label(string): return get_label("dbinding", string)
def get_dhcp_setup_label(string): return get_label("dsetup", string)

# NAT/PAT
def get_nat_pat_label(string): return get_label("natpat", string)
def get_nat_pat_message(string, key): return get_message("natpat", string, key)
def get_pat_rule_label(string): return get_label("patrule", string)
def get_ptf_rule_label(string): return get_label("ptfrule", string)
def get_nat_pat_rule_type_label(string): return get_label("nprtype", string)

# Phone
def get_phone_label(string): return get_label("phone", string)
def get_phone_message(string, key): return get_message("phone", string, key)
def get_phone_contact_label(string): return get_label("pcontact", string)

# Actions
def get_actions_label(string): return get_label("actions", string)
def get_actions_message(string, key): return get_message("actions", string, key)
def get_reboot_history_label(string): return get_label("rhistory", string)
def get_wifi_config_label(string): return get_label("wconfig", string)
def get_wifi_global_label(string): return get_label("wglobal", string)
def get_backup_restore_label(string): return get_label("backrest", string)
def get_screen_label(string): return get_label("screen", string)
def get_firewall_level_label(string): return get_label("fwlevel", string)
def get_ping_response_label(string): return get_label("pingr", string)
def get_dyndns_label(string): return get_label("dyndns", string)
def get_dmz_label(string): return get_label("dmz", string)
def get_routing_label(string): return get_label("routing", string)
def call_api_label(string): return get_label("callapi", string)

# Repeater
def get_repeater_label(string): return get_label("repeater", string)
def get_repeater_message(string, key): return get_message("repeater", string, key)

# TV Decoder
def get_tvdecoder_label(string): return get_label("tvdecoder", string)
def get_tvdecoder_message(string, key): return get_message("tvdecoder", string, key)

# Config
def get_config_prefs_label(string): return get_label("prefs", string)
def get_config_message(string, key): return get_message("prefs", string, key)
def get_config_cnx_label(string): return get_label("cnx", string)
def get_config_signin_label(string): return get_label("signin", string)
def get_config_email_label(string): return get_label("email", string)
def get_select_profile_label(string): return get_label("sprofile", string)
def get_release_warning_label(string): return get_label("rwarn", string)

# Tools
def get_tools_label(string): return get_label("tools", string)
