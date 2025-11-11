### Livebox Monitor Livebox Info APIs ###

import requests

from LiveboxMonitor.api.LmApi import LmApi, LmApiException
from LiveboxMonitor.api.LmSession import LmSession
from LiveboxMonitor.util import LmUtils


# ################################ VARS & DEFS ################################
LIVEBOX_SCAN_TIMEOUT = 0.6

# Livebox versions name map (raw to commercial)
LIVEBOX_MODEL_NAME_MAP = {
    "Livebox 3": "Livebox 3",
    "Livebox 4": "Livebox 4",
    "Livebox Fibre": "Livebox 5",
    "Livebox 6": "Livebox 6",
    "Livebox 7": "Livebox 7",
    "Livebox W7": "Livebox W7",
    "Livebox Nautilus": "Livebox S",
    "Livebox S": "Livebox S"
    }

# Livebox versions map (commercial to version number)
LIVEBOX_MODEL_MAP = {
    "Livebox 3": 3,
    "Livebox 4": 4,
    "Livebox 5": 5,
    "Livebox 6": 6,
    "Livebox 7": 7,
    "Livebox W7": 7.1,
    "Livebox S": 7.2
    }
DEFAULT_RAW_MODEL = "Livebox 7"


# ################################ Livebox Info APIs ################################
class LiveboxInfoApi(LmApi):
    def __init__(self, api_registry):
        super().__init__(api_registry)
        self._mac_addr = None
        self._model = None              # Model version number
        self._raw_model_name = None     # Raw model name as returned by Livebox
        self._model_name = None         # Commercial model name
        self._software_version = None


    ### Get Livebox / Repeater basic info
    def get_device_info(self):
        return self.call("DeviceInfo", "get")


    ### Get Livebox device info
    def get_device_config(self):
        livebox_mac = self.get_mac()
        if livebox_mac:
            return self.call("Devices.Device." + livebox_mac, "get")
        raise LmApiException("Cannot determine Livebox MAC address")


    ### Set Livebox basic info cache
    def set_livebox_info_cache(self):
        try:
            d = self.get_device_info()
        except Exception as e:
            LmUtils.error(str(e))
            LmUtils.error("Cannot determine Livebox model.")
            self._mac_addr = ""
            self._model = 0
            self._raw_model_name = ""
            self._model_name = ""
            self._software_version = ""
        else:
            self._mac_addr = d.get("BaseMAC", "").upper()
            model = d.get("ProductClass", "")
            if model:
                self._model_name = LIVEBOX_MODEL_NAME_MAP.get(model)
                self._raw_model_name = model
            if self._model_name is None:
                LmUtils.error(f"Unknown Livebox model: {model}, defaulting to {DEFAULT_RAW_MODEL}.")
                self._model_name = LIVEBOX_MODEL_NAME_MAP.get(DEFAULT_RAW_MODEL)
            self._model = LIVEBOX_MODEL_MAP.get(self._model_name)
            if self._model is None:
                LmUtils.error(f"Incorrect internal Livebox model setup: {self._model_name} is unknown.")

            self._software_version = d.get("SoftwareVersion", "")


    ### Get Livebox / Repeater MAC
    def get_mac(self):
        if not self._mac_addr:
            self.set_livebox_info_cache()
        return self._mac_addr


    ### Set Livebox / Repeater MAC
    def set_mac(self, mac_addr):
        self._mac_addr = mac_addr


    ### Get Livebox / Repeater model
    def get_model(self):
        if not self._model:
            self.set_livebox_info_cache()
        return self._model


    ### Set Livebox / Repeater model
    def set_model(self, model):
        self._model = model


    ### Get Livebox raw model name
    def get_raw_model_name(self):
        if not self._raw_model_name:
            self.set_livebox_info_cache()
        return self._raw_model_name


    ### Get Livebox / Repeater model name
    def get_model_name(self):
        if not self._model_name:
            self.set_livebox_info_cache()
        return self._model_name


    ### Set Livebox / Repeater model name
    def set_model_name(self, model_name):
        self._model_name = model_name


    ### Get Livebox / Repeater software version
    def get_software_version(self):
        if not self._software_version:
            self.set_livebox_info_cache()
        return self._software_version


    ### Get Livebox model info
    def get_model_info(self):
        return self.call("UPnP-IGD", "get")


    ### Get memory status
    def get_memory_status(self):
        return self.call("DeviceInfo.MemoryStatus", "get")


    ### Get time
    def get_time(self):
        d = self.call_raw("Time", "getTime")
        d = d.get("data")
        if not d:
            raise LmApiException("Time:getTime data error")
        return d


    ### Get WAN status
    def get_wan_status(self):
        d = self.call_raw("NMC", "getWANStatus")
        d = d.get("data")
        if not d:
            raise LmApiException("NMC:getWANStatus data error")
        return d


    ### Get connection status
    def get_connection_status(self):
        return self.call("NMC", "get")


    ### Get VLAN ID
    def get_vlan_id(self):
        return int(self.call_no_check("NeMo.Intf.data", "getFirstParameter", {"name": "VLANID"}))


    ### Get MTU
    def get_mtu(self):
        return int(self.call_no_check("NeMo.Intf.data", "getFirstParameter", {"name": "MTU"}))


    ### Get uplink info
    def get_uplink_info(self):
        return self.call("UplinkMonitor.DefaultGateway", "get")


    ### Get IPv6 status
    def get_ipv6_status(self):
        d = self.call_raw("NMC.IPv6", "get")
        return d.get("data")


    ### Get IPv6 mode
    def get_ipv6_mode(self):
        return self.call("NMC.Autodetect", "get")


    ### Get CGNat status
    def get_cgnat_status(self):
        return self.call("NMC.ServiceEligibility.DSLITE", "get")


    ### Set CGNat enable
    def set_cgnat_enable(self, enable):
        self.call("NMC.ServiceEligibility.DSLITE", "set", {"Demand": enable})


    ### It is possible to query DeviceInfo service without being logged, e.g. to get MAC address
    @staticmethod
    def get_livebox_mac_nosign(livebox_url):
        if livebox_url is not None:
            try:
                r = requests.Session().post(livebox_url  + "ws",
                           data='{"service":"sysbus.DeviceInfo", "method":"get", "parameters":{}}',
                           headers={"Accept":"*/*", "Content-Type":"application/x-sah-ws-4-call+json"},
                           timeout=LIVEBOX_SCAN_TIMEOUT + LmSession.TimeoutMargin)
            except Exception:
                r = None
            if r is not None:
                s = r.json().get("status")
                if s is not None:
                    s = s.get("BaseMAC")
                    if s is not None:
                        return s.upper()

        return None
