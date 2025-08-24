### Livebox Monitor English Language module ###


# ################################ LABELS ################################

# No need - native application language


# ################################ TOOLTIPS ################################

TOOLTIPS = {
    # Main window
    "main": {
        "deviceListTab": "Manage the list of devices.",
        "liveboxInfoTab": "Detailed information about the Livebox and traffic statistics.",
        "graphTab": "Traffic curves per interface and per device.",
        "deviceInfoTab": "Detailed information and settings for each device.",
        "eventsTab": "Event log for each device.",
        "dhcpTab": "Detailed DHCP information and settings.",
        "netPatTab": "Port & protocol forwarding settings.",
        "phoneTab": "Manage phone calls and contact list.",
        "actionTab": "Various actions, settings, preferences, and information about the application.",
        "repeaterTab": "Detailed information about the Wifi repeater and traffic statistics.\n"
                       "Connection status with the repeater:\n"
                       "- Red cross: the repeater is inactive or does not have an assigned IP address.\n"
                       "- Red barred: the repeater is active but no session is open.\n"
                       "If this state persists you can try to force session creation by clicking the \"Resign...\" button.\n"
                       "- Green: the repeater is active and a session has been created to communicate with it."
    },

    # Export table dialog
    "export_table": {
        "exportHeaderCheckbox": "Allows you to choose whether or not to export column headers."
    },

    # Device list
    "dlist": {
        "dlist_Type": "Icon corresponding to the device type.\n"
                      "This type can be assigned or changed via the \"Assign Type...\" button in the \"Device Info\" tab.",
        "dlist_Name": "Local name of the device.\n"
                      "This name can be assigned, changed, or deleted via the \"Assign Name...\" button in the \"Device Info\" tab.\n"
                      "It is normal that at the first launch of the application all devices are shown as UNKNOWN.",
        "dlist_LBName": "Device name as set in the Livebox and visible in the Livebox web interface.\n"
                        "This name can be assigned, changed, or deleted via the \"Assign Name...\" button in the \"Device Info\" tab.",
        "dlist_MAC": "MAC address, also called the physical address of the device.",
        "dlist_IP": "IPv4 address of the device on the LAN.\n"
                    "This address appears in bold if it is reserved for this device\n"
                    "in the Livebox DHCP configuration.\n"
                    "And it appears in red if the address is unreachable on the network,\n"
                    "typically when the device is not active.",
        "dlist_Link": "Device's access point on the network.\nFirst, the device name, i.e., the Livebox itself or the name of one of "
                      "the connected Orange Wifi repeaters, then the interface on this device.\n"
                      "\"Eth\" means one of the Ethernet ports followed by the port number.\n"
                      "\"Wifi\" means a Wifi connection followed by the connection band.",
        "dlist_Active": "Indicates with an icon whether the device is active or not.\n"
                        "By default, the list is sorted to show active devices first.",
        "dlist_Wifi": "Quality of the Wifi connection.",
        "dlist_Event": "Indicates with an icon when an event is received for this device.\n"
                       "The detailed list of events, as well as the content of the events themselves,\n"
                       "can be viewed via the \"Events\" tab.",
        "dlist_Rx": "Number of bytes received by the device since the last Livebox restart.",
        "dlist_Tx": "Number of bytes sent by the device since the last Livebox restart.",
        "dlist_RxRate": "Number of bytes received per second by the device in the last 30 seconds if shown in black,\n"
                        "in the last three seconds if shown in blue (frequency adjustable in preferences).",
        "dlist_TxRate": "Number of bytes sent per second by the device in the last 30 seconds if shown in black,\n"
                        "in the last three seconds if shown in blue (frequency adjustable in preferences).",
        "refresh": "Forces the refresh of the device list, in this tab but also in the \"Device Info\" and \"Events\" tabs.\n"
                   "Useful for example if the program is active while the computer wakes from sleep: "
                   "events may have been missed by the program, a refresh will restore an up-to-date view.",
        "assignNames": "Assigns to all unknown devices a local name equivalent to that known by the Livebox.",
        "deviceInfo": "Switches to the \"Device Info\" tab for the selected device to view its information directly.",
        "deviceEvents": "Switches to the \"Events\" tab for the selected device to view directly the events received about it.",
        "ipv6": "Allows you to get the IPv6 activation status, the Livebox IPv6 address and its prefix,\n"
                "and the list of connected or non-connected devices with one or more assigned IPv6 addresses.\n"
                "Also allows you to view the connection mode and control the CGNat setting.",
        "dns": "Allows you to get the list of DNS names assigned to devices"
    },

    # Device list - IPv6 dialog
    "ipv6": {
        "ipv6_Name": "Local name of the device.\n"
                     "This name can be assigned, changed, or deleted via the \"Assign Name...\" button in the \"Device Info\" tab.",
        "ipv6_LBName": "Device name as set in the Livebox and visible in the Livebox web interface.\n"
                       "This name can be assigned, changed, or deleted via the \"Assign Name...\" button in the \"Device Info\" tab.",
        "ipv6_MAC": "MAC address, also called the physical address of the device.",
        "ipv6_Active": "Indicates with an icon whether the device is active or not.",
        "ipv6_IPv4": "IPv4 address of the device on the LAN.\n"
                     "This address appears in bold if it is reserved for this device\n"
                     "in the Livebox DHCP configuration.\n"
                     "And it appears in red if the address is unreachable on the network,\n"
                     "typically when the device is not active.",
        "ipv6_IPv6": "IPv6 address(es) of the device on the LAN.",
        "ipv6_Prefix": "IPv6 prefix(es) assigned to the device by the Livebox DHCPv6 server.",
        "ipv6Enabled": "Indicates with an icon whether IPv6 connectivity is active or not.",
        "cgNat": "If CGNat mode is active it is possible that the public IPv4 address you use\n"
                 "to browse the Internet is shared within Orange's network.",
        "ipv6Mode": "Connection mode.",
        "addr": "Livebox IPv6 address.",
        "prefix": "Livebox IPv6 prefix.",
        "gateway": "Livebox IPv6 gateway.",
        "cgNatButton": "Allows you to enable or disable CGNat mode, i.e. sharing\n"
                       "the IPv4 address with other users."
    },

    # Device list - DNS dialog
    "dns": {
        "dns_Name": "Local name of the device.\n"
                    "This name can be assigned, changed, or deleted via the \"Assign Name...\" button in the \"Device Info\" tab.",
        "dns_LBName": "Device name as set in the Livebox and visible in the Livebox web interface.\n"
                      "This name can be assigned, changed, or deleted via the \"Assign Name...\" button in the \"Device Info\" tab.",
        "dns_MAC": "MAC address, also called the physical address of the device.",
        "dns_Active": "Indicates with an icon whether the device is active or not.",
        "dns_IP": "IP address of the device on the LAN.\n"
                  "This address appears in bold if it is reserved for this device\n"
                  "in the Livebox DHCP configuration.\n"
                  "And it appears in red if the address is unreachable on the network,\n"
                  "typically when the device is not active.",
        "dns_DNS": "DNS name of the device.\n"
                   "This name can be assigned, changed, or deleted via the \"Assign Name...\" button in the \"Device Info\" tab."
    },

    # Livebox infos
    "info": {
        "stats_Name": "Name of the network interface.\n"
                      "\"Fiber\" concerns all WAN traffic, that is, external traffic between the Livebox and the Internet.\n"
                      "\"LAN\" all internal traffic passing through the Livebox.\n"
                      "Then, there are statistics per specific interface.\n"
                      "\"Guest\" interfaces concern guest Wifi network traffic, if enabled.",
        "stats_Rx": "Number of bytes received by the interface.\n"
                    "The time window for this total is unknown.\n"
                    "Displays in red if transmission errors are detected.\n"
                    "Note this counter is circular and does not exceed 4 GB for some interfaces.",
        "stats_Tx": "Number of bytes sent by the interface.\n"
                    "The time window for this total is unknown.\n"
                    "Displays in red if transmission errors are detected.\n"
                    "Note this counter is circular and does not exceed 4 GB for some interfaces.",
        "stats_RxRate": "Number of bytes received per second by the interface in the last three seconds.\n"
                        "The frequency is adjustable in preferences.\n"
                        "Displays in red if transmission errors are detected.",
        "stats_TxRate": "Number of bytes sent per second by the interface in the last three seconds.\n"
                        "The frequency is adjustable in preferences.\n"
                        "Displays in red if transmission errors are detected.",
        "liveboxInfo": "Displays the main information about the Livebox, such as software versions,\n"
                       "WAN IP address, active services, memory status, etc.",
        "internetInfo": "Displays the type of internet access, connection identifiers, IPv4 & v6 addresses,\n"
                        "the date and time of the last connection, connection bandwidth, MTU, etc.",
        "wifiInfo": "Displays general information about Wifi connectivity, and the status of each access including guest access.\n"
                    "For each access, detailed information such as channel, standard, bandwidth, quality, band,\n"
                    "number of connected devices, etc.",
        "lanInfo": "Displays general information about LAN connectivity.\n"
                   "This is basic DHCP information and for each Ethernet interface\n"
                   "you can identify if it is active or not, the bandwidth, etc.",
        "ontInfo": "Displays important information about the connection and the Fiber module (ONT), such as bandwidth,\n"
                   "signal quality, serial number, and software versions, etc.\n"
                   "The fields \"Signal RxPower\", \"Signal TxPower\", \"Temperature\", \"Voltage\" and \"BIAS\"\n"
                   "display green values if they are within acceptable quality standards for the connection,\n"
                   "in red if they represent a problem.",
        "voipInfo": "Displays general information about telephony, such as protocol,\n"
                    "phone number, DECT interface software version, etc.",
        "iptvInfo": "Displays general information related to television services.",
        "usbInfo": "Displays information about the USB port(s).\n"
                   "If a USB key is inserted, or has been inserted since the last Livebox restart,\n"
                   "its information is displayed.",
        "exportInfo": "Allows you to export all information displayed by each button into a text file.\n"
                      "Useful for sharing this information or for tracking changes."
    },

    # Graph
    "graph": {
        "graphList_Name": "Name of the network interface or device.",
        "graphList_Type": "Type of object to display.",
        "graphList_ID": "Internal identifier of the interface or device.\n"
                        "For interfaces, this is the internal name used by the Livebox.\n"
                        "For devices, this is the physical address (MAC).",
        "graphList_Color": "Color to use to display the graph for each object.",
        "addGraph": "Allows you to add an interface or device to the list of graphs to display.",
        "delGraph": "Allows you to remove the selected interface or device from the list of graphs.",
        "windowEdit": "Time window in hours for displaying graphs, from now.\n"
                      "A value of 0 will display all statistics available in the Livebox.",
        "backColor": "Background color to use for reception and transmission graphs.\n"
                     "A right click removes any color.",
        "apply": "Apply the configuration selected above and draw the graphs.\n"
                 "This action also saves the configuration, which will\n"
                 "be restored at the next program launch.",
        "export": "Allows you to export data corresponding to the above configuration into\n"
                  "CSV files. One file per interface/device is generated.\n"
                  "The configuration must have been applied before export.\n"
                  "Exported times are in \"Unix Epoch\" format.",
        "downGraph": "Graph of data received for each selected interface/device.\n"
                     "Volumes are in megabytes received between two samples, typically\n"
                     "every 30 seconds. The graph updates automatically upon receiving\n"
                     "new samples.\n"
                     "It is possible to navigate and zoom with the mouse, then return to\n"
                     "the normal view by clicking in the bottom left corner.",
        "upGraph": "Graph of data sent for each selected interface/device.\n"
                   "Volumes are in megabytes sent between two samples, typically\n"
                   "every 30 seconds. The graph updates automatically upon receiving\n"
                   "new samples.\n"
                   "It is possible to navigate and zoom with the mouse, then return to\n"
                   "the normal view by clicking in the bottom left corner."
    },

    # Add graph dialog
    "addgraph": {
        "typeCombo": "Selection of the type of object to add.",
        "objectCombo": "Selection of the interface or device to add.\n"
                       "For devices, this is the local name (MacAddr table file), if no\n"
                       "local name has been assigned the physical address (MAC) will be used.",
        "colorEdit": "Color to use to display the corresponding graph.",
        "IDValue": "Internal identifier of the interface or device.\n"
                   "For interfaces, this is the internal name used by the Livebox.\n"
                   "For devices, this is the physical address (MAC).",
        "measureValue": "Number of statistic measurements currently stored by the Livebox for\n"
                        "the interface or device. Generally, the sampling frequency is\n"
                        "30 seconds and the maximum number of stored measurements is 8680.",
        "historyValue": "Total time window of statistics estimated from the number of\n"
                        "measurements and the sampling frequency."
    },

    # Device infos
    "dinfo": {
        "dlist_Name": "Local device name.\n"
                      "This name can be assigned, changed, or deleted via the \"Assign Name...\" button.",
        "dlist_MAC": "MAC address, also called the physical address of the device.",
        "alist_Attribute": "The manufacturer of this device may be displayed, deduced from its MAC address.\n"
                           "The program uses the API from macaddress.io to determine it.\n"
                           "This is a free service, but you must create an account and enter the corresponding API Key\n"
                           "in the preferences to use this feature.",
        "refresh": "Refreshes the displayed information for the selected device.",
        "assignName": "Allows you to assign or erase the local name and/or the Livebox name of the selected device.",
        "assignType": "Allows you to assign or erase the type of the selected device.",
        "forget": "Allows you to ask the Livebox to permanently forget this device.\n"
                  "It will immediately disappear from all lists.\n"
                  "Warning: if the device in question is active, its connection will not be suspended,\n"
                  "however, all its activity will remain invisible until its next connection attempt.",
        "wol": "Allows you to send a Wake-on-LAN (WOL) signal to the selected device.",
        "block": "Allows you to block the connection of the selected device.",
        "unblock": "Allows you to unblock the connection of the selected device.\n"
                   "The blocked or unblocked state is shown in the device information, \"Blocked\" field."
    },

    # Device infos - Assign name dialog
    "dname": {
        "nameCheckBox": "Uncheck the box to erase the local name.",
        "nameEdit": "This local name will be stored in the MacAddr Table file configured in the preferences.",
        "liveboxNameCheckBox": "Uncheck the box to erase the Livebox name.",
        "liveboxNameEdit": "This name will be stored by the Livebox.",
        "dnsNameCheckBox": "Uncheck the box to erase the DNS name.",
        "dnsNameEdit": "DNS name to assign to the device."
    },

    # Device infos - Assign type dialog
    "dtype": {
        "typeNameCombo": "List of standard types known by the Livebox.\n"
                         "When a standard type is selected, its name as known by the Livebox is\n"
                         "automatically filled in the text area.",
        "typeKeyEdit": "It is still possible to manually assign a type not known by the Livebox by typing it directly here."
    },

    # Events
    "events": {
        "dlist_Name": "Local name of the device.\n"
                      "This name can be assigned, changed, or deleted via the \"Assign Name...\" button.",
        "dlist_MAC": "MAC address, also called the physical address of the device.",
        "elist_Time": "Time the event was received.",
        "elist_Reason": "The type of event generated by the Livebox.",
        "elist_Attribute": "Preview of the raw data of the event itself, in JSON format.",
        "notifications": "Displays the configuration window for automatic notifications to generate (for example by email)\n"
                         "upon detection of certain events.",
        "displayEvent": "Displays a dialog containing the complete information for the selected event."
    },

    # Event Notification Rules
    "evnrules" : {
        "rlist_Key": "Designation of devices for which to receive notifications.",
        "rlist_Add": "Notification option when a device is added.",
        "rlist_Delete": "Notification option when a device is deleted.",
        "rlist_Active": "Notification option when a device connects.",
        "rlist_Inactive": "Notification option when a device disconnects.",
        "rlist_Link": "Notification option when a device changes its access point.",
        "rlist_File": "Notification option in a CSV file.",
        "rlist_Email": "Notification option by sending an email.",
        "addRule": "Allows you to add a new notification rule.",
        "delRule": "Allows you to delete the selected notification rule.",
        "deviceCombo": "Allows you to select the device(s) for which to receive a notification.\n"
                       "\"Any device\" will apply the rule to all devices.\n"
                       "\"Any unknown device\" will apply the rule to any unknown device.",
        "macEdit": "Physical address of the selected device.",
        "eventsLabel": "Select the events for which to receive a notification.",
        "addEvent": "Receive a notification when a matching device is added.",
        "delEvent": "Receive a notification when a matching device is deleted.",
        "actEvent": "Receive a notification when a matching device connects.",
        "inaEvent": "Receive a notification when a matching device disconnects.",
        "lnkEvent": "Receive a notification when a matching device changes access point (for example Wifi repeater).",
        "actionsLabel": "Select the actions to perform for notification.",
        "fileAction": "Log the events in a daily CSV file.",
        "emailAction": "Send the information of each event by instant email.\n"
                       "This option requires configuring email sending via the \"Actions\" tab.",
        "flushFrequencyEdit": "Events are detected instantly, however some events may cancel each other out\n"
                              "when generated within a short time window, such as disconnection\n"
                              "followed by reconnection within 15 seconds for a given device (happens frequently).\n"
                              "To avoid unnecessary notifications, a waiting time of 30 seconds is strongly recommended\n"
                              "to let the program identify these situations.\n"
                              "A time less than 5 seconds is strongly discouraged to prevent the program\n"
                              "from consuming too many resources.",
        "eventFilePathEdit": "Directory in which to generate the daily CSV files.",
        "eventFilePathSelectButton": "Allows you to select the directory in which to generate\n"
                                     "the daily CSV files.",
        "defaultFilePath": "Check to generate the daily CSV files in the default directory,\n"
                           "which is the same as the configuration directory."
    },

    # DHCP
    "dhcp": {
        "dlist_Name": "Local device name.\n"
                      "This name can be assigned, changed, or removed via the \"Assign Name...\" button.",
        "dlist_Domain": "Assigned DHCP domain, \"Home\" or \"Guest\".",
        "dlist_MAC": "MAC address, also called the physical address of the device.",
        "dlist_IP": "IP address statically assigned to the device.",
        "refreshBinding": "Refreshes the list of static leases.",
        "addBinding": "Allows you to add a lease.",
        "delBinding": "Deletes the selected lease.",
        "refreshDhcpAttribute": "Refreshes the list of DHCP information.",
        "dhcpSetup": "Allows you to configure the DHCP server."
    },

    # DHCP - Binding dialog
    "dbinding": {
        "deviceCombo": "The list of suggested devices is sorted and consists of a mix of connected\n"
                       "devices and those referenced in the local MAC address file.",
        "macEdit": "The MAC address is directly derived from the selected device\n"
                   "but you can also enter one manually.",
        "domainCombo": "Choose the network domain between \"Home\" or \"Guest\".\n"
                       "A free IP address is automatically suggested.",
        "ipEdit": "The address remains configurable.\n"
                  "Note that the same device can only be configured on a single domain,\n"
                  "and if it connects to a domain where a static lease is configured on the other,\n"
                  "that lease will be automatically deleted."
    },

    # DHCP - Setup dialog
    "dsetup": {
        "enableCheckbox": "Enables or disables the DHCP server.",
        "liveboxIpEdit": "Allows you to change the Livebox IP address.",
        "maskEdit": "Allows you to change the DHCP server subnet mask.",
        "minEdit": "Starting IP address for the \"Home\" domain.",
        "maxEdit": "Ending IP address for the \"Home\" domain."
    },

    # NAT/PAT
    "natpat": {
        "plist_Enabled": "Indicates with an icon whether the rule is active or not.",
        "plist_Type": "Indicates the type of rule.",
        "plist_ID": "Indicates the name of the rule.",
        "plist_Description": "Description of the rule.",
        "plist_Protocols": "List of protocols concerned by the rule.",
        "plist_IntPort": "Internal port to which traffic is redirected.",
        "plist_ExtPort": "External port to redirect.",
        "plist_Device": "Device to which the traffic is redirected.",
        "plist_ExtIPs": "List of external IP addresses concerned by the rule.",
        "refreshPat": "Refreshes the list of port forwarding rules.",
        "enablePat": "Enables/disables the selected rule.",
        "addPat": "Allows you to add a port forwarding rule.",
        "editPat": "Allows you to modify the selected port forwarding rule.",
        "deletePat": "Allows you to delete the selected port forwarding rule.",
        "deleteAllPat": "Allows you to delete all port forwarding rules\n"
                        "of one or more selected types.",
        "exportPat": "Allows you to export to a file the port forwarding rules\n"
                     "of one or more selected types.",
        "importPat": "Allows you to re-import previously exported port forwarding rules from a file.\n"
                     "If rules with the same name already exist, they will be overwritten by the imported ones.",
        "tlist_Enabled": "Indicates with an icon whether the rule is active or not.",
        "tlist_Type": "Indicates the type of rule.",
        "tlist_ID": "Indicates the name of the rule.",
        "tlist_Description": "Description of the rule.",
        "tlist_Protocols": "List of protocols concerned by the rule.",
        "tlist_Device": "Device to which the traffic is redirected.",
        "tlist_ExtIPs": "List of external IP addresses concerned by the rule.",
        "refreshPtf": "Refreshes the list of protocol forwarding rules.",
        "enablePtf": "Enables/disables the selected rule.",
        "addPtf": "Allows you to add a protocol forwarding rule.",
        "editPtf": "Allows you to modify the selected protocol forwarding rule.",
        "deletePtf": "Allows you to delete the selected protocol forwarding rule.",
        "deleteAllPtf": "Allows you to delete all protocol forwarding rules.",
        "exportPtf": "Allows you to export to a file the protocol forwarding rules\n"
                     "of one or more selected types.",
        "importPtf": "Allows you to re-import previously exported protocol forwarding rules from a file.\n"
                     "If rules with the same name already exist, they will be overwritten by the imported ones."
    },

    # NAT/PAT - PAT rule dialog
    "patrule": {
        "enableCheckbox": "Enables or disables the rule.",
        "typeCombo": "Select the type of rule. UPnP is an internal type,\n"
                     "you should not need to create or modify a rule of this type.",
        "nameEdit": "Unique name for the rule. If a rule with the same name already exists,\n"
                    "it will be overwritten.",
        "descEdit": "Description of the rule.",
        "tcpCheckbox": "Redirects TCP traffic or not.",
        "udpCheckbox": "Redirects UDP traffic or not.",
        "intPortEdit": "Internal port to which traffic should be redirected.\n"
                       "Use the - character between two ports to specify a range.",
        "extPortEdit": "External port to redirect.\n"
                       "Does not work in IPv6.\n"
                       "Leave this field empty if it is the same as the internal port.\n"
                       "Use the - character between two ports to specify a range.",
        "deviceCombo": "Device to which the traffic should be redirected.",
        "ipEdit": "IP address (v4 or v6 depending on the type) to which the traffic\n"
                  "should be redirected.",
        "extIPsEdit": "List of external IP addresses (v4 or v6 depending on the type) concerned by the rule.\n"
                      "Each address must be separated by a comma.\n"
                      "Leave empty if no external IP filtering is required."
    },

    # NAT/PAT - PTF rule dialog
    "ptfrule": {
        "enableCheckbox": "Enables or disables the rule.",
        "typeCombo": "Select the type of rule.",
        "nameEdit": "Unique name for the rule. If a rule with the same name already exists,\n"
                    "it will be overwritten.",
        "descEdit": "Description of the rule.",
        "protocolsCombo": "Select the protocols to redirect.",
        "deviceCombo": "Device to which the traffic should be redirected.",
        "ipEdit": "IP address (v4 or v6 depending on the type) to which the traffic\n"
                  "should be redirected. It is also possible to specify a prefix.",
        "extIPsEdit": "List of external IP addresses (v4 or v6 depending on the type) concerned by the rule.\n"
                      "Each address must be separated by a comma.\n"
                      "Leave empty if no external IP filtering is required."
    },

    # NAT/PAT - rule type selection dialog
    "nprtype": {
        "ipV4Checkbox": "Selects or not IPv4 type rules.",
        "ipV6Checkbox": "Selects or not IPv6 type rules.",
        "upnpCheckbox": "Selects or not UPnP type rules."
    },

    # Phone
    "phone": {
        "calist_Type": "Icon corresponding to the type of call.\n"
                       "- Received call.\n"
                       "- Missed call. In this case, the entire line is shown in red.\n"
                       "- Outgoing call.\n"
                       "- Outgoing call but not connected.",
        "calist_Time": "Date and time of the call.",
        "calist_Number": "Phone number involved.\n"
                         "Double-clicking on a call allows you to easily create or edit the corresponding contact.",
        "calist_Contact": "The name of the contact determined by the Livebox based on the contact list at the time of the call.\n"
                          "If the Livebox did not store any name, the program tries to find one dynamically from\n"
                          "the list of saved contacts by matching the phone number.",
        "calist_Duration": "Duration of the call.",
        "colist_Name": "Contact name, in the format last name + first name.",
        "colist_Cell": "Mobile phone number.",
        "colist_Home": "Home phone number.",
        "colist_Work": "Work phone number.",
        "colist_Ring": "Type of ringtone selected from the 7 supported by the Livebox.",
        "refreshCall": "Refreshes the call list.",
        "deleteCall": "Deletes the selected call.",
        "deleteAllCalls": "Deletes all calls.",
        "spamCallScan": "Scans all unidentified incoming calls and checks on the callfilter.app website\n"
                        "if these calls are spam or not. This feature requires a Call Filter API Key\n"
                        "and it must be configured in the preferences.",
        "spamCallSites": "Opens two websites in your browser to check the origin\n"
                         "of the selected call.",
        "setSpamCall": "Allows you to manually mark the selected call as spam or not.",
        "refreshContact": "Refreshes the contact list.",
        "addContact": "Allows you to add a contact.\n"
                      "Note: No duplicate check is performed.",
        "editContact": "To edit the selected contact.",
        "deleteContact": "Deletes the selected contact.",
        "deleteAllContacts": "Deletes all contacts.",
        "ringToneCombo": "Select one of the 7 types of ringtones offered by the Livebox.\n"
                         "If none is selected, the default ringtone is used.",
        "phoneRing": "Allows you to test the phone with the selected ringtone.",
        "exportContacts": "Allows you to export all contacts into a VCF file.\n"
                          "Very useful for backups.",
        "importContacts": "Allows you to import one or more VCF files.\n"
                          "Note: No duplicate check is performed.\n"
                          "If the maximum supported number of contacts (255) is reached, the import is stopped."
    },

    # Phone - Contact edit
    "pcontact": {
        "ringToneCombo": "Ringtone for this contact among the 7 supported by the Livebox."
    },

    # Actions
    "actions": {
        "wifiConfig": "Allows you to configure all radio bands of the Wifi network.",
        "wifiGuestConfig": "Allows you to configure all radio bands of the Guest Wifi network.",
        "wifiOn": "Allows you to enable the Wifi interface of the Livebox.",
        "wifiOff": "Allows you to disable the Wifi interface of the Livebox.",
        "guestWifiOn": "Allows you to enable the guest Wifi interface of the Livebox.",
        "guestWifiOff": "Allows you to disable the guest Wifi interface of the Livebox.",
        "schedulerOn": "Allows you to enable the Wifi scheduler of the Livebox.\n"
                       "This scheduler must be configured from the Livebox web interface.",
        "schedulerOff": "Allows you to disable the Wifi scheduler of the Livebox.",
        "wifiGlobalStatus": "Allows you to display the global status of Wifi, including the Wifi status of all\n"
                            "potentially connected Orange Wifi repeaters.",
        "backupRestore": "Allows you to set up automatic backup of the Livebox configuration,\n"
                         "trigger a backup, or request a configuration restore.",
        "screen": "Allows you to set the LED level and display the Wifi password\n"
                  "on the screen. Feature available only from Livebox 6 onwards.",
        "rebootLivebox": "Allows you to force a reboot of the Livebox.",
        "resetLivebox": "Allows you to reset the Livebox to factory settings.\n"
                        "If automatic configuration restoration is enabled, a dialog will allow you to disable it.",
        "rebootHistory": "Allows you to display the history of the latest reboots.\n"
                         "Useful to detect reboots forced by Orange to update the Livebox software.",
        "firewallLevel": "Allows you to set the levels of the IPv4 and IPv6 firewalls.",
        "pingResponse": "Allows you to set responses to IPv4 and IPv6 ping requests.",
        "dynDNS": "Allows you to assign a domain and fixed host name, easy to remember, to a static or dynamic IP address\n"
                  "or a long URL.\n"
                  "Useful, for example, if you host a website or FTP server behind your Livebox to\n"
                  "find it easily (name like myserver.dydns.org).",
        "dmz": "Allows you to add a device to the DMZ.\n"
               "By adding a device to the DMZ, you make it accessible from the Internet.\n"
               "You must first assign a static IP address to this device in the DHCP tab.",
        "routingTable": "Allows you to configure the static routing table.\n"
                        "This option is only available for Livebox Pro.",
        "openSourceURL": "A click will open the application's web page in your browser.",
        "prefs": "Allows you to display the program preferences screen.",
        "changeProfile": "Allows you to change the current profile and restart the program.",
        "emailSetup": "Allows you to configure automatic email sending, for example for notifications.",
        "setLogLevel": "Allows you to change the log level in the console.\n"
                       "This level is stored in the program configuration and will be retained at the next launch.",
        "callApis": "Allows you to call the REST/JSON Livebox APIs.",
        "getApiDoc": "Allows you to export the available documentation on the Livebox REST/JSON APIs\n"
                     "into a set of files. This feature is blocked on Livebox W7 & S.",
        "quit": "To quit the application. Strictly equivalent to closing the application window."
    },

    # Actions - Reboot history
    "rhistory": {
        "reboot_BootDate": "Startup date and time.",
        "reboot_BootReason": "The reason for this startup.\n"
                             "Typically \"NMC\" or \"POR\" indicates a software-forced startup and \"Unsupported chipset\"\n"
                             "a reboot caused by a power outage or the switch.",
        "reboot_ShutdownDate": "Shutdown date and time.",
        "reboot_ShutdownReason": "The reason for this shutdown.\n"
                                 "Typically empty for a power outage, \"Upgrade\" for a software update, and \"GUI_Reboot\" for\n"
                                 "a reboot requested from the Web interface or LiveboxMonitor.",
    },

    # Actions - Wifi configuration
    "wconfig": {
        "enableCheckbox": "Enables or disables all radio bands.",
        "mloCheckbox": "Enables or disables Wifi 7 MLO technology (Multi-Link Operation).",
        "durationEdit": "Duration in hours of Guest Wifi activation.\n"
                        "Enter 0 for unlimited duration.",
        "freqCombo": "Allows you to select the radio band to configure.",
        "ssidEdit": "Name of the network to broadcast for the selected radio band.",
        "freqEnabledCheckbox": "Enables or disables the selected radio band.",
        "broadcastCheckbox": "Allows you to broadcast the network name to make it discoverable.",
        "wpsCheckbox": "Enables or disables WPS connection methods\n"
                       "(Wi-Fi Protected Setup) for the selected radio band.",
        "macFilteringCombo": "Select 'Off' to disable MAC filtering.\n"
                             "'WhiteList' to enable MAC filtering and allow\n"
                             "connection only to listed devices.\n"
                             "'BlackList' to enable MAC filtering and allow\n"
                             "connection to all devices except those listed.",
        "macFilteringEntriesCombo": "Select the devices to be filtered.\n"
                                    "The 'Add...' option allows you to enter a new physical address\n"
                                    "(MAC address) to the list.",
        "secuCombo": "Type of security for the selected radio band.\n"
                     "Select 'None' for open access without a password.",
        "passEdit": "Password for the selected radio band.",
        "passShow": "Allows you to show/hide the password.",
        "chanCombo": "Channel to use for the selected radio band.\n"
                     "Select 'Auto' for automatic selection.",
        "modeCombo": "Connection mode for the selected radio band."
    },

    # Actions - Wifi global status
    "wglobal": {},

    # Actions - Backup & Restore
    "backrest": {
        "autoBackEnabled": "Indicates whether automatic backup is enabled or not.",
        "status": "Indicates the current backup status.",
        "lastBackup": "Date and time of the last backup.",
        "refresh": "Allows you to refresh the above information.",
        "enaAutoBack": "Enables automatic backup of the Livebox configuration.",
        "disAutoBack": "Disables automatic backup of the Livebox configuration.",
        "forceBackup": "Forces a backup of the Livebox configuration.",
        "forceRestore": "Forces a restoration of the Livebox configuration from\n"
                        "the last backup. A Livebox restart is triggered."
    },

    # Actions - Screen & LEDs
    "screen" : {
        "orangeSlider": "Adjusts the brightness level of the Orange LED.",
        "showWifiPasswordCheckbox": "Display the security key on the Livebox screen."
    },

    # Actions - Firewall level
    "fwlevel": {
        "ipV4Combo": "IPv4 firewall level.",
        "ipV6Combo": "IPv6 firewall level."
    },

    # Actions - Ping Response
    "pingr": {
        "ipV4Checkbox": "Select to respond to IPv4 ping requests.",
        "ipV6Checkbox": "Select to respond to IPv6 ping requests."
    },

    # Actions - DynDNS
    "dyndns": {
        "hlist_Service": "Service type.",
        "hlist_HostName": "Host or domain name.",
        "hlist_UserName": "User email.",
        "hlist_Password": "User password.",
        "hlist_LastUpdate": "Date and time of the last update.",
        "refresh": "Refreshes the list of hosts/domains.",
        "showPassword": "Shows or hides passwords in the list.",
        "delHost": "Deletes the selected host/domain.",
        "serviceCombo": "Service selection.",
        "hostNameEdit": "Host or domain name.",
        "userNameEdit": "User email.",
        "passwordEdit": "User password.",
        "addHost": "Adds a host/domain.",
        "disableAll": "Disables or enables all hosts/domains.",
        "ok": "Closes this screen."
    },

    # Actions - DMZ
    "dmz": {
        "zlist_ID": "Unique identifier of the DMZ rule. The Orange application only uses a single rule\n"
                    "with \"webui\" as the identifier.",
        "zlist_IP": "IP address of the device in the DMZ.",
        "zlist_Device": "Name of the device in the DMZ.",
        "zlist_ExtIPs": "List of external IP addresses concerned by the rule.",
        "refresh": "Refreshes the list of devices in the DMZ.",
        "delDmz": "Deletes the selected rule.",
        "id": "Unique identifier of the DMZ rule. The Orange application only uses a single rule\n"
              "with \"webui\" as the identifier.",
        "deviceCombo": "Device to add to the DMZ.",
        "ipEdit": "IP address of the device to add to the DMZ.",
        "extIPsEdit": "List of external IP addresses concerned by the rule.\n"
                      "Each address must be separated by a comma.\n"
                      "Leave empty if no external IP filtering is required.",
        "addDmz": "Adds the device to the DMZ. If a rule is already present with the same identifier,\n"
                  "it will be overwritten.",
        "ok": "Closes this screen."
    },

    # Actions - Routing
    "routing": {
        "rlist_DestMask": "Destination subnet mask.",
        "rlist_Priority": "Priority given to each route.",
        "rlist_Enabled": "Indicates whether you have requested to activate the route.",
        "rlist_Status": "Current rule activation status.",
        "refresh": "Refreshes the list of routes.",
        "enableRule": "Enables/disables the selected route.",
        "delRule": "Deletes the selected route.",
        "destMaskEdit": "Destination subnet mask.",
        "priorityEdit": "Priority to be given to the route.",
        "addRule": "Adds a new route with the specified values.",
        "editRule": "Modifies the selected route with the specified values.",
        "ok": "Closes this screen."
    },

    # Actions - Call API
    "callapi": {
        "presetCombo": "List of predefined calls.",
        "service": "Service name, for example \"NMC\".",
        "method": "Method name, for example \"get\".",
        "parametersEdit": "Parameters to use, JSON format.",
        "call": "Trigger the corresponding API call.",
        "replyEdit": "Displays API call response, JSON format."
    },

    # Repeater
    "repeater": {
        "stats_Name": "Network interface name.\n"
                      "\"LAN\" concerns all traffic between the repeater and the Livebox.\n"
                      "Then, you have statistics for each specific interface (the Ethernet ports as well as the Wifi bands).",
        "stats_Rx": "Number of bytes received by the interface.\n"
                    "The time window for this total is unknown.\n"
                    "Displays in red if transmission errors are detected.\n"
                    "Note: this counter is circular and does not exceed 4 GB.",
        "stats_Tx": "Number of bytes sent by the interface.\n"
                    "The time window for this total is unknown.\n"
                    "Displays in red if transmission errors are detected.\n"
                    "Note: this counter is circular and does not exceed 4 GB.",
        "stats_RxRate": "Rate of bytes received per second by the interface over the last three seconds.\n"
                        "The frequency can be set in the preferences.",
        "stats_TxRate": "Rate of bytes sent per second by the interface over the last three seconds.\n"
                        "The frequency can be set in the preferences.",
        "wifiOn": "Allows you to enable the repeater's Wifi interface.",
        "wifiOff": "Allows you to disable the repeater's Wifi interface.",
        "schedulerOn": "Allows you to enable the Wifi scheduler of the repeater.\n"
                       "This scheduler must be configured from the repeater's web interface.",
        "schedulerOff": "Allows you to disable the Wifi scheduler of the repeater.",
        "rebootRepeater": "Allows you to force a reboot of the repeater.",
        "resetRepeater": "Allows you to reset the repeater to factory settings.",
        "rebootHistory": "Allows you to display the history of the latest reboots.\n"
                         "Useful for detecting reboots forced by Orange to update the repeater's software.",
        "callApis": "Allows you to call the REST/JSON repeater APIs.",
        "resign": "To force the creation of a new session with the repeater.\n"
                  "If you leave the program running too long without viewing the repeater's statistics or\n"
                  "performing any action, the session will be automatically released by the repeater.\n"
                  "In this case, errors will occur when performing actions: this button will allow you to recreate\n"
                  "the session, enabling you to resume actions without errors.",
        "repeaterInfo": "Displays the main information about the repeater, such as software versions,\n"
                        "model name, internal clock time, etc.",
        "wifiInfo": "Displays general information about Wifi connectivity, and the status of each access.\n"
                    "For each access point, you get detailed information such as channel, standard, bandwidth,\n"
                    "quality, band, number of connected devices, etc.",
        "lanInfo": "Displays general information about LAN connectivity.\n"
                   "For each Ethernet interface, you can identify if it is active or not, bandwidth, etc.",
        "exportInfo": "Allows you to export all the information displayed by each button into a text file.\n"
                      "Useful for sharing this information or for tracking changes."
    },

    # TV Decoder
    "tvdecoder": {
        ###TODO###
    },

    # Config - Preferences
    "prefs": {
        "profileList": "The program supports managing multiple Liveboxes using different profiles.\n"
                       "Each profile must have a unique name. By default, a main profile is created automatically.\n"
                       "If several profiles are configured, the name of the current profile is displayed in the main window title in brackets.\n"
                       "When the program starts, the default profile is used, but if no default profile is configured or\n"
                       "if the `Ctrl` key is pressed, the program displays a dialog to select the profile to use.",
        "addProfile": "Allows you to add a profile.",
        "delProfile": "Delete the selected profile.",
        "profileNameEdit": "Profile name.",
        "liveboxUrlEdit": "Livebox address. The default value is \"http://livebox.home/\".",
        "liveboxUserEdit": "Login for session opening.\n"
                           "Default is \"admin\".\n"
                           "The password is requested automatically when using the profile\n"
                           "if it is not provided or if it is incorrect.",
        "filterDevices": "Enables device filtering to avoid showing certain \"phantom\" devices detected by the Livebox.\n"
                         "When this setting is enabled, the program displays the same devices as the Livebox web interface.\n"
                         "This setting is enabled by default.",
        "macAddrTableFileEdit": "Filename for storing device names associated with their MAC address.\n"
                                "Default is \"MacAddrTable.txt\".\n"
                                "Any detected device whose MAC address is not listed will be displayed as \"UNKNOWN\" in red.\n"
                                "This feature is mainly useful for detecting new devices or intrusion attempts.",
        "defaultProfile": "Indicates that this is the default profile to use when the program starts.\n"
                          "There can only be one default profile.",
        "languageCombo": "Language used by the application.",
        "tooltips": "Enable or disable tooltips.",
        "statsFrequencyEdit": "Refresh frequency, in seconds, for all statistics.\n"
                              "Default is 3 seconds.",
        "macAddrApiKeyEdit": "The program uses the API from the macaddress.io website to determine the manufacturer of a device\n"
                             "from its MAC address (the \"Manufacturer\" field in the detailed device information).\n"
                             "It is a free service, but you must create an account and enter the corresponding API Key here\n"
                             "to use this feature.",
        "callFilterApiKeyEdit": "The program uses the API from the callfilter.app website to determine if a phone call\n"
                                "is telemarketing or fraud based on its number.\n"
                                "It is a free service, but you must request a key by email in English (info@callfilter.app)\n"
                                "and enter the given API Key here to use this feature.",
        "phoneCodeEdit": "Local telephone code, useful for matching phone calls with contact numbers.\n"
                         "By default, the code for France is used, which is 33.",
        "listHeaderHeightEdit": "Height in pixels of list headers, default is 25.",
        "listHeaderFontSizeEdit": "Font size of list headers.\n"
                                  "A value of zero means to use the system size.\n"
                                  "By default, this setting is zero.",
        "listLineHeightEdit": "Height in pixels of list lines, default is 30.",
        "listLineFontSize": "Font size of list lines.\n"
                            "A value of zero means to use the system size.\n"
                            "By default, this setting is zero.",
        "timeoutMarginEdit": "Additional timeout value, to be used for example if you access a Livebox remotely\n"
                             "with high network latency.",
        "csvDelimiterEdit": "List separator (delimiter) to use when exporting\n"
                            "data to CSV format files.",
        "realtimeWifiStats": "Enable or disable real-time statistics for wifi devices.\n"
                             "These are displayed in blue in the \"Devices\" tab and overlay\n"
                             "the standard statistics, which are displayed in black every 30 seconds.",
        "preventSleepMode": "Allows you to prevent your computer from going to sleep while this\n"
                            "program is running. Useful for keeping the application running continuously, for example for\n"
                            "statistics export or real-time notification generation.",
        "nativeUIStyle": "By default, the \"Fusion\" style is used on all platforms.\n"
                         "This option allows Windows and MacOS platforms to use\n"
                         "a more native graphical style.\n"
                         "It has no effect on Linux platforms.",
        "savePasswords": "Allows you to save passwords in the configuration (encrypted) to avoid\n"
                         "having to re-enter them each time the program starts."
    },

    # Config - Connection
    "cnx": {
        "urlEdit": "You must use for the connection exactly the same information as for the Livebox Web Interface\n"
                   "For the URL try http://livebox.home/, http://livebox/ or http://192.168.1.1/."
    },

    # Config - Signin
    "signin": {
        "userEdit": "You must use for the connection exactly the same information as for the Livebox Web Interface\n"
                    "User must remain set to the default \"admin\".",
        "passwordEdit": "The password is either what you set up yourself or if you didn't change it, it is what is in\n"
                        "your Wifi card (corresponds to the first 8 characters, without spaces, of the security key visible\n"
                        "on the sticker at the back of your Livebox).\n"
                        "Read the documentation for more details.",
        "savePasswords": "Allows you to save passwords in the configuration (encrypted) to avoid\n"
                         "having to re-enter them each time you start."
    },

    # Config - email
    "email": {
        "fromAddrEdit": "Sender email address for messages.",
        "toAddrEdit": "Recipient email address for messages.",
        "subjectPrefixEdit": "Prefix added to the subjects of sent messages.",
        "smtpServerEdit": "SMTP server of your email provider.",
        "smtpPortEdit": "SMTP port to use. 465 is recommended for SSL & TLS,\n"
                        "587 for any other protocol.",
        "useSTARTTLS": "Use the STARTTLS encryption protocol (recommended).",
        "useTLS": "Use the TLS encryption protocol.",
        "authentication": "Select if the server requires authentication.",
        "test": "Allows you to send a test message with the current settings\n"
                "without saving them."
    },

    # Config - Select profile
    "sprofile": {
        "assMacValue": "Physical address of the Livebox associated with the selected profile.\n"
                       "If no address is associated, the profile has never been used and can be associated\n"
                       "with any Livebox on the network.",
        "detMacValue": "Physical address of the Livebox detected via the selected profile's URL.\n"
                       "If no Livebox is detected, it means the connection will fail and another\n"
                       "URL will be requested.\n"
                       "If the physical address is different from the one associated with the selected profile,\n"
                       "the old address will be replaced by the new one.",
        "createProfile": "Allows you to create a new profile and use it directly."
    },

    # Config - Release warning
    "rwarn": {
        "downloadURL": "Click here to open the application's web page in your browser.\n"
                       "You will be able to download the new version there.",
        "nowarning": "Click here to no longer be notified about this version."
    }
}



# ################################ MESSAGES ################################

# No need - native application language
