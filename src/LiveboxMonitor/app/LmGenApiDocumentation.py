### Livebox Monitor module to generate API documentation ###

import os
import json

from LiveboxMonitor.tools import LmTools


# ################################ VARS & DEFS ################################
SERVICES = [
    "AccountManager",
    "Audiphone",
    "AutoDiag",
    "BulkData",
    "CaptivePortal",
    "ConMon",
    "Conntrack",
    "CPUStats",
    "CupsService",              # LB5 only
    "DECT",                     # LB5 only
    "DeviceInfo",
    "DeviceLookup",
    "DeviceManagement",
    "DeviceManager",
    "Devices",
    "BCMPlugin",
    "DHCPv4",
    "DHCPv6",
    "DHCPv6Client",
    "DLNA",
    "Dms",                      #LB6/LB7
    "Dms.Configuration",        #LB6/LB7
    "Dms.Database",             #LB6/LB7
    "Dms.Partition",            #LB6/LB7
    "Dms.Streaming",            #LB6/LB7
    "DNS",
    "DNSSD",
    "Domino",
    "Domino.Cellular",
    "Domino.Airbox",
    "Domino.Intf",
    "DSPGDECT",                 # LB5 only
    "DSPPlugin",
    "DummyPlugin",
    "DynDNS",
    "eventmanager",
    "FaultMonitor",
    "Firewall",
    "Flowstats",
    "GenLog",
    "Gpon",
    "History",
    "HomeLan",
    "HTTPService",
    "IEEE1905",
    "Invocation",
    "IoTService",
    "IPPingDiagnostics",
    "IPsec",
    "KMCD",
    "Launcher",
    "LEDs.LED",                 # LB6/LB7
    "LLMNR",
    "Locations",                # LB6/LB7
    "LXCManager",
    "Maculan",
    "ManagementServer",
    "Manifests",
    "MQTTBroker",
    "MQTTMessages",
    "MSS",
    "NeMo",
    "NetDev",
    "NetMaster",
    "NMC",
    "ObjectMonitor",
    "OopsTracker",
    "OrangeDynDNS",
    "OrangeRemoteAccess",
    "OrangeServices",
    "OUI",
    "Pass",
    "PasswordRecovery",
    "Phonebook",
    "PnP",
    "PowerManagement",          # LB6 only
    "PPP",
    "Probe",
    "Process",
    "ProcessMonitor",
    "Profiles",
    "QueueManagement",
    "RemoteAccess",
    "RouterAdvertisement",
    "sah",
    "SAHPairing",
    "SambaService",
    "ServiceInvocation",        # LB7 only
    "Scheduler",
    "Screen",                   # LB6 only
    "SFP",                      # LB4 only
    "SpeedTest",
    "SrvInterface",
    "SSLEServer",
    "SSW",
    "SSW.Steering",
    "SSW.FeatureConfig",
    "StorageService",
    "Time",
    "ToD",
    "TopologyDiagnostics",
    "UDPEchoConfig",
    "Upgrade",
    "UplinkMonitor",
    "UPnP",
    "UPnP-IGD",
    "URLMon",                   # LB5 only
    "USBHosts",
    "UserInterface",
    "UserManagement",
    "VoiceActivation",
    "VoiceService",
    "VoWifi",
    "VPN",
    "WatchDog",
    "WebuiupgradeService",
    "WiFiBCM",
    "WiFiQUAN",                 # LB5 only
    "WLanScheduler",
    "WOL",
    "WOLProxy"
]

INDENT = "  "



# ################################ GenApiDoc Class ################################
class LmGenApiDoc:
    def __init__(self, app, folder, filter_value):
        self._app = app
        self._api = app._api
        self._session = self._api._session
        self._software_version = self._api._info.get_software_version()
        self._folder = folder
        self._filter = filter_value
        self._file = None


    ### Generate files for each known service
    def gen_service_files(self):
        # Generate for each known service
        for s in SERVICES:
            self.gen_service_file(s)

        # Generate for all interfaces
        try:
            d = self._api._intf.get_key_list()
        except Exception as e:
            LmTools.error(str(e))
        else:
            if isinstance(d, list):
                for m in d:
                    self.gen_service_file("NeMo.Intf." + m)
            else:
                LmTools.error("Bad return from interface list API.")


    ### Generate all services in a flat file
    def gen_full_file(self):
        self.gen_service_file(".", "_ALL SERVICES_")


    ### Generate process list file
    def gen_process_list_file(self):
        self.gen_service_file("*", "_PROCESSES_")


    ### Generate JSON result file for a service - useful only to get raw results
    def gen_service_json_file(self, service, name=None):
        if name is None:
            name = service

        try:
            d = self._session.request(service, get=True, timeout=15)
        except Exception as e:
            LmTools.error(str(e))
            return

        if d is None:
            return

        # Service doesn't exist error
        if isinstance(d, dict) and (d.get("error", 0) == 196618):
            return

        file_path = os.path.join(self._folder, name + "_json.txt")
        try:
            self._file = open(file_path, "w")
        except Exception as e:
            LmTools.error(str(e))
            return

        self._file.write(f"=== LIVEBOX SOFTWARE VERSION: {self._software_version}\n\n")
        json.dump(d, self._file, indent = 4)

        try:
            self._file.close()
        except Exception as e:
            LmTools.error(str(e))
        self._file = None


    ### Generate document file for a service
    def gen_service_file(self, service, name=None):
        if name is None:
            name = service

        self._app._task.update(name)

        try:
            d = self._session.request(service, get=True, timeout=15)
        except Exception as e:
            LmTools.error(str(e))
            return

        if d is None:
            return

        # Service doesn't exist error
        if isinstance(d, dict) and (d.get("error", 0) == 196618):  
            return

        file_path = os.path.join(self._folder, name + ".txt")
        try:
            self._file = open(file_path, "w")
        except Exception as e:
            LmTools.error(str(e))
            return

        self._file.write(f"=== LIVEBOX SOFTWARE VERSION: {self._software_version}\n\n")
        if not isinstance(d, list):
            d = [d]
        for o in d:
            if not self.gen_object(o):
                json.dump(o, self._file, indent=4)

        try:
            self._file.close()
        except Exception as e:
            LmTools.error(str(e))
        self._file = None


    ### Generate documentation for an object - return False if not an object
    def gen_object(self, object_info, instance=False, level=0):
        o = object_info.get("objectInfo")
        if o is None:
            return False

        indent = INDENT * level
        key_path = o.get("keyPath")
        key = o.get("key")
        index_path = o.get("indexPath")
        name = o.get("name")
        if instance:
            self._file.write(f"{indent}-----------------------------------------------------------------------\n")
            self._file.write(f"{indent}INSTANCE: {key_path}.{key} - Name: {index_path}.{name}\n")
        else:
            self._file.write(f"{indent}=======================================================================\n")
            self._file.write(f"{indent}OBJECT: {key_path}.{key} - Name: {index_path}.{name}\n")

        self.gen_parameters(object_info, level)
        self.gen_functions(object_info, level)
        self._file.write("\n")
        if not self._filter:
            self.gen_instances(object_info, level)
        self.gen_children(object_info, level)

        return True


    ### Generate parameters
    def gen_parameters(self, object_info, level=0):
        o = object_info.get("parameters")
        if o:
            indent = INDENT * level
            self._file.write(f"{indent} == PARAMETERS:\n")
            for p in o:
                self.gen_parameter(p, level + 1)


    ### Generate a parameter
    def gen_parameter(self, param, level=0):
        indent = INDENT * level

        # Collect values
        name = param.get("name")
        type = param.get("type")
        attributes = ""
        attributes_dict = param.get("attributes")
        for a in attributes_dict:
            if attributes_dict[a]:
                if len(attributes):
                    attributes += ", "
                attributes += a
        value = param.get("value")
        validator = param.get("validator")

        # Rendering
        self._file.write(f"{indent}- {name} (type: {type})\n")
        indent = INDENT * (level + 2)
        if len(attributes):
            self._file.write(f"{indent}Attributes: {attributes}\n")
        if (not self._filter) and (value is not None):
            if isinstance(value, str):
                if len(value):
                    self._file.write(f"{indent}Value: '{value}'\n")
            else:
                self._file.write(f"{indent}Value: {value}\n")
        if validator is not None:
            self._file.write(f"{indent}Validator: {validator}\n")


    ### Generate functions
    def gen_functions(self, object_info, level=0):
        o = object_info.get("functions")
        if o:
            indent = INDENT * level
            self._file.write(f"{indent} == FUNCTIONS:\n")
            for f in o:
                self.gen_function(f, level + 1)


    ### Generate a function
    def gen_function(self, func, level=0):
        indent = INDENT * level

        # Collect values
        name = func.get("name")
        return_type = func.get("type")
        attributes = ""
        attributes_dict = func.get("attributes")
        for a in attributes_dict:
            if attributes_dict[a]:
                if len(attributes):
                    attributes += ", "
                attributes += a
        arguments = ""
        arguments_dict = func.get("arguments")
        for a in arguments_dict:
            if len(arguments):
                arguments += ", "

            arg_name = a.get("name")
            arg_type = a.get("type")
            arg_optional = True
            arg_attributes_dict = a.get("attributes")
            if (arg_attributes_dict is not None) and (arg_attributes_dict.get("mandatory", False)):
                arg_optional = False
            if arg_optional:
                arguments += f"({arg_type} {arg_name})"
            else:
                arguments += f"{arg_type} {arg_name}"

        # Rendering
        self._file.write(f"{indent}- {return_type} {name}({arguments})\n")
        indent = INDENT * (level + 2)
        if len(attributes):
            self._file.write(f"{indent}Attributes: {attributes}\n")


    ### Generate parameters
    def gen_instances(self, object_info, level=0):
        o = object_info.get("instances")
        if o:
            indent = INDENT * level
            self._file.write(f"{indent} == INSTANCES:\n")
            for i in o:
                self.gen_object(i, True, level + 1)


    ### Generate child objects
    def gen_children(self, object_info, level=0):
        o = object_info.get("children")
        if o:
            for i in o:
                self.gen_object(i, False, level)


    ### Test GET request on some characters
#   def doTest(self):
#       self.gen_service_json_file(".", "DOT")
#       self.gen_service_json_file("*", "STAR")
#       self.gen_service_json_file("!", "EXCLAM")
#       self.gen_service_json_file("#", "HASH")
#       self.gen_service_json_file("`", "QUOTE")
#       self.gen_service_json_file("+", "PLUS")
#       self.gen_service_json_file("@", "AT")
#       self.gen_service_json_file("?", "QUESTION")
#       self.gen_service_json_file("/", "SLASH")
#       self.gen_service_json_file("-", "MINUS")
#       self.gen_service_json_file("~", "TILDA")
#       self.gen_service_json_file("$", "DOLLAR")
#       self.gen_service_json_file("%", "PERCENT")
#       self.gen_service_json_file("^", "HAT")
#       self.gen_service_json_file("&", "AND")
#       self.gen_service_json_file("(", "LEFTPAR")
#       self.gen_service_json_file(")", "RIGHTPAR")
#       self.gen_service_json_file("_", "UNDERSCORE")
#       self.gen_service_json_file("=", "EGUAL")
#       self.gen_service_json_file(",", "COMMA")
#       self.gen_service_json_file(":", "COLONN")
#       self.gen_service_json_file(";", "SEMICOLONN")
