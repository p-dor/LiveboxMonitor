### Livebox Monitor Wifi APIs ###

from LiveboxMonitor.api.LmApi import LmApi, LmApiException
from LiveboxMonitor.app import LmTools


# ################################ VARS & DEFS ################################

# Wifi status keys
class WifiKey:
    ACCESS_POINT = "Name"
    ENABLE = "WE"
    STATUS = "WS"
    SCHEDULER = "SCH"
    WIFI2_ENABLE = "W2E"
    WIFI2_STATUS = "W2S"
    WIFI2_VAP = "W2V"
    WIFI5_ENABLE = "W5E"
    WIFI5_STATUS = "W5S"
    WIFI5_VAP = "W5V"
    WIFI6_ENABLE = "W6E"
    WIFI6_STATUS = "W6S"
    WIFI6_VAP = "W6V"
    GUEST2_VAP = "G2V"
    GUEST5_VAP = "G5V"

# Wifi status values
class WifiStatus:
    ENABLE = "Y"
    DISABLE = "N"
    ERROR = "E"
    INACTIVE = "I"
    UNSIGNED = "S"



# ################################ Wifi APIs ################################
class WifiApi(LmApi):
    def __init__(self, api_registry):
        super().__init__(api_registry)
        self._has_mlo = None


    ### Get Wifi or Guest Interfaces setup - returns base, radio and vap
    def get_intf(self, guest=False):
        return self._api._intf.get_wifi_mibs(guest)


    ### Get Wifi status
    def get_status(self):
        if self._api._is_repeater:
            d = self.call_raw("NMC.Wifi", "get", timeout=15)
            d = d.get("data")
            if d:
                return d
            raise LmApiException("NMC.Wifi:get query error")
        return self.call("NMC.Wifi", "get", timeout=15)


    ### Get enable status
    def get_enable(self):
        if self._api._is_repeater:
            return self.get_status().get("Enable")
        nmc_status = self.get_status().get("Enable")
        d = self.get_power_management_profiles("WiFi").get("WiFi")
        power_status = d.get("Enable") if d else nmc_status
        return (nmc_status is True) and (power_status is True)


    ### Activate/Deactivate Wifi
    def set_enable(self, enable):
        if self._api._is_repeater:
            self.call_no_check("NMC.Wifi", "set", {"Enable": enable, "Status": enable}, err_str="Enable")
        else:
            self.set_power_management_profiles({"profile": "WiFi", "enable": enable})
            self.call("NMC.Wifi", "set", {"Enable": enable, "Status": enable}, err_str="Enable")


    ### Get guest status
    def get_guest_status(self):
        return self.call("NMC.Guest", "get", timeout=15)


    ### Get guest enable status
    def get_guest_enable(self):
        return self.get_guest_status().get("Status") == "Enabled"


    ### Activate/Deactivate guest Wifi, timer in hours (0 == infinite)
    def set_guest_enable(self, enable, timer=0):
        self.call_no_check("NMC.Guest", "set", {"Enable": enable})

        # Set timer, just log in case of error
        try:
            if enable:
                self.set_guest_activation_timer(timer)
            else:
                self.disable_guest_activation_timer()
        except Exception as e:
            LmTools.error(str(e))


    ### Get guest activation timer - in seconds
    def get_guest_activation_timer(self):
        return int(self.call_no_check("NMC.WlanTimer", "getActivationTimer", {"InterfaceName": "guest"}))


    ### Set guest activation timer - in hours
    def set_guest_activation_timer(self, timer):
        self.call_no_check("NMC.WlanTimer", "setActivationTimer", {"Timeout": timer, "InterfaceName": "guest"})


    ### Disable guest activation timer
    def disable_guest_activation_timer(self):
        self.call("NMC.WlanTimer", "disableActivationTimer", {"InterfaceName": "guest"})


    ### Set Configuration Mode - must be set to True if SSIDs are different between radio bands
    def set_configuration_mode(self, mode):
        self.call("NMC.Wifi", "set", {"ConfigurationMode": mode})


    ### Set WLAN Configuration
    def set_wlan_config(self, mibs):
        self.call_no_check("NeMo.Intf.lan", "setWLANConfig", {"mibs": mibs}, timeout=35)


    ### Check if Wifi scheduler is present
    def has_scheduler(self):
        if self._api._is_repeater:
            return self._api._info.get_model() >= 6    # Scheduler available only starting WR6
        return True


    ### Get Wifi Scheduler enable status
    def get_scheduler_enable(self):
        if self._api._is_repeater:
            return self.get_scheduler_enable_legacy()
        try:
            d = self.get_power_management_profiles("WiFi")
        except Exception as e:
            LmTools.error(str(e))
            # If failed, try legacy method
            return self.get_scheduler_enable_legacy()
        else:
            d = d.get("WiFi")
            if d is not None:
                return d.get("Activate")
            else:
                LmTools.error("PowerManagement:getProfiles - No WiFi profile")
                return self.get_scheduler_enable_legacy()


    ### Get Wifi Scheduler enable status - legacy method
    def get_scheduler_enable_legacy(self):
        d = self.call_raw("Scheduler", "getCompleteSchedules", {"type": "WLAN"})
        if not d.get("status", False):
            raise LmApiException(f"Scheduler:getCompleteSchedules service failed.")
        d = d.get("data")
        if d:
            d = d.get("scheduleInfo", [])
            if d and isinstance(d, list):
                return d[0].get("enable")
        return None


    ### Set Wifi Scheduler enable status
    def set_scheduler_enable(self, enable):
        if self._api._is_repeater:
            self.set_scheduler_enable_repeater(enable)
            return

        # Set PowerManagement profile
        try:
            if enable:
                p = [{"profile": "WiFi",
                      "activate": True,
                      "type": "Weekly",
                      "schedules": [{
                          "Day": 1,
                          "Hour": 0,
                          "Minute": 0,
                          "Second": 0,
                          "enable": True
                        }]
                    }]
                self.call("PowerManagement", "setScheduledProfiles", {"profiles": p})
            else:
                self.call("PowerManagement", "setProfiles", {"profiles": [{"profile": "WiFi", "activate": False}]})
        except Exception as e:
            LmTools.error(f"PowerManagement method failed with error={e}, trying legacy method.")
            return self.set_scheduler_enable_legacy(enable)

        # ID has to remain 'wl0' - it is NOT corresponding to an intf key
        intf_id = "wl0"

        # Get current schedule info
        d = self.call_raw("Scheduler", "getSchedule", {"type": "WLAN", "ID": intf_id})
        status = d.get("status")   #Warning: seems status can be easily false, need to investigate
        if status:
            d = d.get("data")
            if d:
                d = d.get("scheduleInfo")
        else:
            d = None
        if d:
            schedule = d
        else:
            raise LmApiException(f"Scheduler:getSchedule service failed for {intf_id} interface.")

        # Add schedule with proper status
        p = {"base": schedule.get("base"),
             "def": schedule.get("def"),
             "ID": intf_id,
             "schedule": schedule.get("schedule"),
             "enable": enable,
             "override": ""}
        d = self.call("Scheduler", "addSchedule", {"type": "WLAN", "info": p}, err_str=intf_id)


    ### Legacy method to set Wifi Scheduler on or off
    ### These calls were used by the deprecated "MaLiveBox" iOS app
    def set_scheduler_enable_legacy(self, enable):
        # First save network configuration
        self.call("NMC.NetworkConfig", "launchNetworkBackup", {"delay": True})
        failed = False
        restore = False
        err_msg = ""

        # Get Wifi interfaces
        d = self.call("NeMo.Intf.lan", "getMIBs", {"mibs": "wlanvap"}, timeout=25)
        w = d.get("wlanvap")
        if w is None:
            raise LmApiException("NeMo.Intf.lan:getMIBs service failed.")

        # Loop on each Wifi interface
        n = 0
        for i in w:
            # Get current schedule info
            try:
                d = self.call_raw("Scheduler", "getSchedule", {"type": "WLAN", "ID": i}, err_str=i)
            except Exception as e:
                err_msg = str(e)
                LmTools.error(err_msg)
                failed = True
                break
            status = d.get("status")
            if status:     #Warning: seems status can be easily false, need to investigate
                d = d.get("data")
                if d:
                    d = d.get("scheduleInfo")
            else:
                d = None
            if d:
                schedule = d
            else:
                err_msg = f"Scheduler:getSchedule service failed for {i} interface."
                LmTools.error(err_msg)
                failed = True
                break

            # Add schedule with proper status
            p = {"enable": enable,
                 "base": schedule.get("base"),
                 "def": schedule.get("def"),
                 "override": "" if enable else "Enable",
                 "value": schedule.get("value"),
                 "ID": i,
                 "schedule": schedule.get("schedule")}
            try:
                d = self.call_no_check("Scheduler", "addSchedule", {"type": "WLAN", "info": p})
            except Exception as e:
                LmTools.error(str(e))
                d = None
            if not d:
                err_msg = f"Scheduler:addSchedule service failed for {i} interface.\nLivebox might reboot."
                LmTools.error(err_msg)
                failed = True
                if n:   # Trigger a restore (causing a Livebox reboot) if at least one succeeded previously
                    restore = True
                break
            else:
                n += 1

        # Restore network configuration if failed and try another way
        if failed:
            if restore:
                self.call_no_check("NMC.NetworkConfig", "launchNetworkRestore")       # Restore config, triggering a Livebox reboot
            failed = False

            for i in w:
                try:
                    d = self.call_no_check("Scheduler", "enableSchedule", {"type": "WLAN", "ID": i, "enable": enable}, err_str=i)
                except Exception as e:
                    LmTools.error(str(e))
                    d = None
                if not d:
                    err_msg = f"Scheduler:enableSchedule service failed for {i} interface."
                    LmTools.error(err_msg)
                    failed = True

        if failed:
            raise LmApiException(err_msg)


    ### Set Wifi Scheduler on or off for a Wifi repeater
    def set_scheduler_enable_repeater(self, enable):
        # ID has to remain 'wl0' - it is NOT corresponding to an intf key
        self.call("Scheduler", "enableSchedule", {"type": "WLAN", "ID": "wl0", "enable": enable})


    ### Get PowerManagement profiles, by default returns all
    def get_power_management_profiles(self, profile=None):
        return self.call("PowerManagement", "getProfiles", {"profiles": [profile]} if profile else None)


    ### Set a PowerManagement profile, return the resulting new profile
    def set_power_management_profiles(self, profile):
        return self.call("PowerManagement", "setProfiles", {"profiles": [profile]})


    ### Determine if Livebox model supports MLO Wifi 7 technology - returns True if yes
    def has_mlo(self):
        if self._has_mlo is None:
            try:
                mlo = self.get_mlo_enable()
                self._has_mlo = mlo is not None
            except Exception:
                self._has_mlo = False
        return self._has_mlo


    ### Get MLO Wifi 7 technology configuration
    def get_mlo_config(self):
        return self.call("SSW.DataElements.Network.APMLDTemplate.privMlo", "get", timeout=15) 


    ### Get MLO Wifi 7 enable status
    def get_mlo_enable(self):
        return self.get_mlo_config().get("MLOEnable")


    ### Set MLO Wifi 7 enable status
    def set_mlo_enable(self, enable):
        self.call("SSW.DataElements.Network.APMLDTemplate.privMlo", "set", {"MLOEnable": enable}, timeout=15) 


    ### Get Wifi configuration
    def get_config(self):
        config = {}

        # Get enable status + interfaces setup
        try:
            config["Enable"] = self.get_enable()
            b, w, d = self.get_intf()
        except Exception as e:
            LmTools.error(str(e))
            return None

        # Get MLO status if available
        if self.has_mlo():
            try:
                config["MLO"] = self.get_mlo_enable()
            except Exception as e:
                LmTools.error(str(e))
                config["MLO"] = False

        # Get setup for each interface in wlanvap
        intf = []
        for s in d:
            # Get Wifi interface key in wlanradio list
            intf_key = None
            base = b.get(s)
            if base is not None:
                low_level_intf = base.get("LLIntf")
                if low_level_intf is not None:
                    intf_key = next(iter(low_level_intf))

            q = w.get(intf_key) if intf_key is not None else None
            r = d.get(s)
            if (q is None) or (r is None):
                continue

            c = {}
            radio_band = q.get("OperatingFrequencyBand")
            if radio_band is None:
                radio_band = s
            c["Name"] = "Wifi " + radio_band
            c["Key"] = s
            c["LLIntf"] = intf_key
            c["SSID"] = r.get("SSID")
            c["Enable"] = base.get("Enable")
            c["Broadcast"] = r.get("SSIDAdvertisementEnabled")

            t = r.get("Security")
            if t is not None:
                c["Secu"] = t.get("ModeEnabled")
                c["SecuAvail"] = t.get("ModesAvailable")
                c["KeyPass"] = t.get("KeyPassPhrase")
            else:
                c["Secu"] = None
                c["SecuAvail"] = None
                c["KeyPass"] = None

            t = r.get("WPS")
            if t is not None:
                c["WPS"] = t.get("Enable")
            else:
                c["WPS"] = None

            t = r.get("MACFiltering")
            if t is not None:
                c["MACFiltering"] = t.get("Mode")
                entries = t.get("Entry")
                if entries:
                    c["MACFilteringEntries"] = [entries[k].get("MACAddress", None) for k in entries]
                else:
                    c["MACFilteringEntries"] = None
            else:
                c["MACFiltering"] = None
                c["MACFilteringEntries"] = None

            c["Mode"] = q.get("OperatingStandards")
            c["ChannelAutoSupport"] = q.get("AutoChannelSupported")
            c["ChannelAuto"] = q.get("AutoChannelEnable")
            c["Channel"] = q.get("Channel")

            intf.append(c)
        config["Intf"] = intf

        # Get available modes & channels per interface
        modes = {}
        for c in intf:
            intf_key = c["LLIntf"]
            try:
                d = self._api._intf.get_info(intf_key)
            except Exception as e:
                LmTools.error(str(e))
            else:
                m = {}
                m["Modes"] = d.get("SupportedStandards")
                m["Channels"] = d.get("PossibleChannels")
                m["ChannelsInUse"] = d.get("ChannelsInUse")
                modes[intf_key] = m
        config["Modes"] = modes

        return config


    ### Set Wifi configuration - returns True if all successful
    def set_config(self, old_config, new_config):
        old_intf = old_config["Intf"]
        new_intf = new_config["Intf"]
        status = True

        # Check if SSIDs are the same accross frequencies before and after
        s = None
        old_unique_ssid = True
        for o in old_intf:
            if s is None:
                s = o["SSID"]
            else:
                if o["SSID"] != s:
                    old_unique_ssid = False
                    break
        s = None
        new_unique_ssid = True
        for n in new_intf:
            if s is None:
                s = n["SSID"]
            else:
                if n["SSID"] != s:
                    new_unique_ssid = False
                    break

        # If SSID homogeneity changed, change the Configuration Mode
        if old_unique_ssid != new_unique_ssid:
            try:
                self.set_configuration_mode(new_unique_ssid)
            except Exception as e:
                LmTools.error(str(e))
                status = False

        # Initiate parameters
        vap = {}
        radio = {}
        penable = {}

        # Check which setup changed
        for o, n in zip(old_intf, new_intf):
            v = {}
            if (o["SSID"] != n["SSID"]):
                v["SSID"] = n["SSID"]
            if (o["Broadcast"] != n["Broadcast"]):
                v["SSIDAdvertisementEnabled"] = n["Broadcast"]
            if (o["Secu"] != n["Secu"]):
                v["Security"] = {"ModeEnabled": n["Secu"], "KeyPassPhrase": n["KeyPass"]}
            elif (o["KeyPass"] != n["KeyPass"]):
                v["Security"] = {"KeyPassPhrase": n["KeyPass"]}
            if (o["WPS"] != n["WPS"]):
                v["WPS"] = {"Enable": n["WPS"]}
            filtering = {}
            if (o["MACFiltering"] != n["MACFiltering"]):
                filtering["Mode"] = n["MACFiltering"]
            if (o["MACFilteringEntries"] != n["MACFilteringEntries"]):
                entries = n["MACFilteringEntries"]
                filtering["Entry"] = {f"MAC{i+1}": {"MACAddress": mac} for i, mac in enumerate(entries)} if entries else {}
            if filtering:
                v["MACFiltering"] = filtering
            if ((o["ChannelAuto"] != n["ChannelAuto"]) or 
                (o["Channel"] != n["Channel"]) or
                (o["Mode"] != n["Mode"])):
                if n["ChannelAuto"]:
                    r = {"AutoChannelEnable": True, "OperatingStandards": n["Mode"]}
                else:
                    r = {"AutoChannelEnable": False, "Channel": n["Channel"], "OperatingStandards": n["Mode"]}
            else:
                r = {}
            if (o["Enable"] != n["Enable"]):
                enable = n["Enable"]
                p = {"Enable": enable, "PersistentEnable": enable, "Status": enable}
            else:
                p = {}

            if len(v):
                vap[n["Key"]] = v
            if len(r):
                radio[n["LLIntf"]] = r
            if len(p):
                penable[n["Key"]] = p

        # Call the API if at least one parameter changed
        if len(vap) or len(radio) or len(penable):
            params = {}
            params["penable"] = penable
            if len(vap):
                params["wlanvap"] = vap
            if len(radio):
                params["wlanradio"] = radio
            try:
                self.set_wlan_config(params)
            except Exception as e:
                LmTools.error(str(e))
                status = False

        # Activate/Deactivate Wifi
        if (old_config["Enable"] != new_config["Enable"]):
            try:
                self.set_enable(new_config["Enable"])
            except Exception as e:
                LmTools.error(str(e))
                status = False             

        # Activate/Deactivate MLO if relevant
        if self.has_mlo() and (old_config["MLO"] != new_config["MLO"]):
            try:
                self.set_mlo_enable(new_config["MLO"])
            except Exception as e:
                LmTools.error(str(e))
                status = False             

        return status


    ### Get Guest Wifi configuration
    def get_guest_config(self):
        # Get activation total duration
        config = {}

        try:
            s = self.get_guest_status()
            b, w, d = self.get_intf(True)
        except Exception as e:
            LmTools.error(str(e))
            return None

        config["Enable"] = s.get("Status") == "Enabled"

        if s.get("ActivationTimeout", 0) != 0:
            start_time = LmTools.livebox_timestamp(s.get("StartTime"))
            end_time = LmTools.livebox_timestamp(s.get("ValidTime"))
            if (start_time is None) or (end_time is None):
                LmTools.error("Activation timeout timestamps error")
                diff = 0
            else:
                diff = int((end_time - start_time).total_seconds())
            config["Duration"] = diff
        else:
            config["Duration"] = 0

        # Get activation remaining time
        try:
            config["Timer"] = self.get_guest_activation_timer()
        except Exception as e:
            LmTools.error(str(e))
            config["Timer"] = 0

        # Get setup for each interface
        intf = []
        for s in d:
            # Get Wifi interface key in wlanradio list
            intf_key = None
            base = b.get(s)
            if base is not None:
                low_level_intf = base.get("LLIntf")
                if low_level_intf is not None:
                    intf_key = next(iter(low_level_intf))

            q = w.get(intf_key) if intf_key is not None else None
            r = d.get(s)
            if (q is None) or (r is None):
                continue

            c = {}
            radio_band = q.get("OperatingFrequencyBand")
            if radio_band is None:
                radio_band = s
            c["Name"] = "Guest " + radio_band
            c["Key"] = s
            c["LLIntf"] = intf_key
            c["SSID"] = r.get("SSID")
            c["Enable"] = base.get("Enable")
            c["Broadcast"] = r.get("SSIDAdvertisementEnabled")

            t = r.get("Security")
            if t is not None:
                c["Secu"] = t.get("ModeEnabled")
                c["SecuAvail"] = t.get("ModesAvailable")
                c["KeyPass"] = t.get("KeyPassPhrase")
            else:
                c["Secu"] = None
                c["SecuAvail"] = None
                c["KeyPass"] = None

            t = r.get("WPS")
            if t is not None:
                c["WPS"] = t.get("Enable")
            else:
                c["WPS"] = None

            t = r.get("MACFiltering")
            if t is not None:
                c["MACFiltering"] = t.get("Mode")
            else:
                c["MACFiltering"] = None

            intf.append(c)
        config["Intf"] = intf

        return config


    ### Set Guest Wifi configuration - returns True if all successful
    def set_guest_config(self, old_config, new_config):
        old_intf = old_config["Intf"]
        new_intf = new_config["Intf"]
        status = True

        # Initiate parameters
        vap = {}
        penable = {}

        # Check which setup changed
        for o, n in zip(old_intf, new_intf):
            v = {}
            if (o["SSID"] != n["SSID"]):
                v["SSID"] = n["SSID"]
            if (o["Broadcast"] != n["Broadcast"]):
                v["SSIDAdvertisementEnabled"] = n["Broadcast"]
            if (o["Secu"] != n["Secu"]):
                v["Security"] = {"ModeEnabled": n["Secu"], "KeyPassPhrase": n["KeyPass"]}
            elif (o["KeyPass"] != n["KeyPass"]):
                v["Security"] = {"KeyPassPhrase": n["KeyPass"]}
            if (o["WPS"] != n["WPS"]):
                v["WPS"] = {"Enable": n["WPS"]}
            if (o["MACFiltering"] != n["MACFiltering"]):
                v["MACFiltering"] = {"Mode": n["MACFiltering"]}
            if (o["Enable"] != n["Enable"]):
                enable = n["Enable"]
                p = {"Enable": enable, "PersistentEnable": enable, "Status": enable }
            else:
                p = {}

            if len(v):
                vap[n["Key"]] = v
            if len(p):
                penable[n["Key"]] = p

        # Call the API if at least one parameter changed
        if len(vap) or len(penable):
            params = {}
            params["penable"] = penable
            if len(vap):
                params["wlanvap"] = vap
            try:
                self.set_wlan_config(params)
            except Exception as e:
                LmTools.error(str(e))
                status = False

        # Activate/Deactivate Guest Wifi or reset timer
        try:
            if (old_config["Enable"] != new_config["Enable"]):
                self.set_guest_enable(new_config["Enable"], new_config["Duration"] // 3600)
            elif new_config["Enable"]:
                self.set_guest_activation_timer(new_config["Duration"] // 3600)
        except Exception as e:
            LmTools.error(str(e))
            status = False

        return status


    ### Get Global Wifi status
    def get_global_wifi_status(self, name=None, active=True, signed=True):
        u = {}
        u[WifiKey.ACCESS_POINT] = name if name else "Livebox"

        if not active:
            u[WifiKey.ENABLE] = WifiStatus.INACTIVE
            u[WifiKey.STATUS] = WifiStatus.INACTIVE
            u[WifiKey.SCHEDULER] = WifiStatus.INACTIVE
            if self._api._intf.has_radio_band_2():
                u[WifiKey.WIFI2_ENABLE] = WifiStatus.INACTIVE
                u[WifiKey.WIFI2_STATUS] = WifiStatus.INACTIVE
                u[WifiKey.WIFI2_VAP] = WifiStatus.INACTIVE
            if self._api._intf.has_radio_band_5():
                u[WifiKey.WIFI5_ENABLE] = WifiStatus.INACTIVE
                u[WifiKey.WIFI5_STATUS] = WifiStatus.INACTIVE
                u[WifiKey.WIFI5_VAP] = WifiStatus.INACTIVE
            if self._api._intf.has_radio_band_6():
                u[WifiKey.WIFI6_ENABLE] = WifiStatus.INACTIVE
                u[WifiKey.WIFI6_STATUS] = WifiStatus.INACTIVE
                u[WifiKey.WIFI6_VAP] = WifiStatus.INACTIVE
            return u

        if not signed:
            u[WifiKey.ENABLE] = WifiStatus.UNSIGNED
            u[WifiKey.STATUS] = WifiStatus.UNSIGNED
            u[WifiKey.SCHEDULER] = WifiStatus.UNSIGNED
            if self._api._intf.has_radio_band_2():
                u[WifiKey.WIFI2_ENABLE] = WifiStatus.UNSIGNED
                u[WifiKey.WIFI2_STATUS] = WifiStatus.UNSIGNED
                u[WifiKey.WIFI2_VAP] = WifiStatus.UNSIGNED
            if self._api._intf.has_radio_band_5():
                u[WifiKey.WIFI5_ENABLE] = WifiStatus.UNSIGNED
                u[WifiKey.WIFI5_STATUS] = WifiStatus.UNSIGNED
                u[WifiKey.WIFI5_VAP] = WifiStatus.UNSIGNED
            if self._api._intf.has_radio_band_6():
                u[WifiKey.WIFI6_ENABLE] = WifiStatus.UNSIGNED
                u[WifiKey.WIFI6_STATUS] = WifiStatus.UNSIGNED
                u[WifiKey.WIFI6_VAP] = WifiStatus.UNSIGNED
            return u

        # General Wifi status
        wifi_scheduler_status = None
        try:
            d = self.get_status()
        except Exception as e:
            LmTools.error(str(e))
            d = None
        if d is None:
            u[WifiKey.ENABLE] = WifiStatus.ERROR
            u[WifiKey.STATUS] = WifiStatus.ERROR
        else:
            u[WifiKey.ENABLE] = WifiStatus.ENABLE if d.get("Enable", False) else WifiStatus.DISABLE
            u[WifiKey.STATUS] = WifiStatus.ENABLE if d.get("Status", False) else WifiStatus.DISABLE
            wifi_scheduler_status = d.get("SchedulingEnabled")

        # Wifi scheduler status
        if self.has_scheduler():
            try:
                status = self.get_scheduler_enable()
            except Exception as e:
                LmTools.error(str(e))
                status = None

            # Agregate result
            if status is None:
                if wifi_scheduler_status is None:
                    u[WifiKey.SCHEDULER] = WifiStatus.ERROR
                else:
                    u[WifiKey.SCHEDULER] = WifiStatus.ENABLE if wifi_scheduler_status else WifiStatus.DISABLE
            else:
                if wifi_scheduler_status is None:
                    u[WifiKey.SCHEDULER] = WifiStatus.ENABLE if status else WifiStatus.DISABLE
                else:
                    u[WifiKey.SCHEDULER] = WifiStatus.ENABLE if (status and wifi_scheduler_status) else WifiStatus.DISABLE

        # Wifi interfaces status
        try:
            b, w, d = self.get_intf()
        except Exception as e:
            LmTools.error(str(e))
            b = None
            w = None
            d = None

        if (d is None) or (b is None) or (w is None):
            if self._api._intf.has_radio_band_2():
                u[WifiKey.WIFI2_ENABLE] = WifiStatus.ERROR
                u[WifiKey.WIFI2_STATUS] = WifiStatus.ERROR
                u[WifiKey.WIFI2_VAP] = WifiStatus.ERROR
            if self._api._intf.has_radio_band_5():
                u[WifiKey.WIFI5_ENABLE] = WifiStatus.ERROR
                u[WifiKey.WIFI5_STATUS] = WifiStatus.ERROR
                u[WifiKey.WIFI5_VAP] = WifiStatus.ERROR
            if self._api._intf.has_radio_band_6():
                u[WifiKey.WIFI6_ENABLE] = WifiStatus.ERROR
                u[WifiKey.WIFI6_STATUS] = WifiStatus.ERROR
                u[WifiKey.WIFI6_VAP] = WifiStatus.ERROR
        else:
            for s in self._api._intf.get_list():
                if s["Type"] != "wif":
                    continue

                match s["Name"]:
                    case "Wifi 2.4GHz":
                        enable_key = WifiKey.WIFI2_ENABLE
                        status_key = WifiKey.WIFI2_STATUS
                        vap_key = WifiKey.WIFI2_VAP
                    case "Wifi 5GHz":
                        enable_key = WifiKey.WIFI5_ENABLE
                        status_key = WifiKey.WIFI5_STATUS
                        vap_key = WifiKey.WIFI5_VAP
                    case "Wifi 6GHz":
                        enable_key = WifiKey.WIFI6_ENABLE
                        status_key = WifiKey.WIFI6_STATUS
                        vap_key = WifiKey.WIFI6_VAP
                    case _:
                        continue

                # Get Wifi interface key in wlanradio list
                intf_key = None
                base = b.get(s["Key"])
                if base is not None:
                    u[enable_key] = WifiStatus.ENABLE if base.get("Enable", False) else WifiStatus.DISABLE
                    u[status_key] = WifiStatus.ENABLE if base.get("Status", False) else WifiStatus.DISABLE

                    low_level_intf = base.get("LLIntf")
                    if low_level_intf is not None:
                        intf_key = next(iter(low_level_intf))
                else:
                    u[enable_key] = WifiStatus.ERROR
                    u[status_key] = WifiStatus.ERROR

                q = w.get(intf_key) if intf_key is not None else None
                r = d.get(s["Key"])
                if (q is None) or (r is None):
                    u[vap_key] = WifiStatus.ERROR
                else:
                    u[vap_key] = WifiStatus.ENABLE if (r.get("VAPStatus", "Down") == "Up") else WifiStatus.DISABLE


        # Guest Wifi status
        if not self._api._is_repeater:
            try:
                b, w, d = self.get_intf(True)
            except Exception as e:
                LmTools.error(str(e))
                b = None
                w = None
                d = None

            if (d is None) or (b is None) or (w is None):
                if self._api._intf.has_radio_band_2():
                    u[WifiKey.GUEST2_VAP] = WifiStatus.ERROR
                if self._api._intf.has_radio_band_5():
                    u[WifiKey.GUEST5_VAP] = WifiStatus.ERROR
            else:
                for s in self._api._intf.get_list():
                    if s["Type"] != "wig":
                        continue

                    match s["Name"]:
                        case "Guest 2.4GHz":
                            vap_key = WifiKey.GUEST2_VAP
                        case "Guest 5GHz":
                            vap_key = WifiKey.GUEST5_VAP
                        case _:
                            continue

                    r = d.get(s["Key"])
                    if r is None:
                        u[vap_key] = WifiStatus.ERROR
                    else:
                        u[vap_key] = WifiStatus.ENABLE if (r.get("VAPStatus", "Down") == "Up") else WifiStatus.DISABLE

        return u
