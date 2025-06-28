### Livebox Monitor API objects registry ###

from LiveboxMonitor.api.LmLiveboxInfoApi import LiveboxInfoApi
from LiveboxMonitor.api.LmIntfApi import IntfApi
from LiveboxMonitor.api.LmWifiApi import WifiApi
from LiveboxMonitor.api.LmDeviceApi import DeviceApi
from LiveboxMonitor.api.LmStatsApi import StatsApi
from LiveboxMonitor.api.LmDhcpApi import DhcpApi
from LiveboxMonitor.api.LmVoipApi import VoipApi
from LiveboxMonitor.api.LmIptvApi import IptvApi
from LiveboxMonitor.api.LmRebootApi import RebootApi
from LiveboxMonitor.api.LmFirewallApi import FirewallApi
from LiveboxMonitor.api.LmDynDnsApi import DynDnsApi
from LiveboxMonitor.api.LmBackupRestoreApi import BackupRestoreApi
from LiveboxMonitor.api.LmScreenApi import ScreenApi


# ################################ API objects registry ################################
class ApiRegistry:
    def __init__(self, session, is_repeater=False):
        self._session = session
        self._is_repeater = is_repeater
        self._info = LiveboxInfoApi(self)
        self._intf = IntfApi(self)
        self._wifi = WifiApi(self)
        self._device = DeviceApi(self)
        self._stats = StatsApi(self)
        self._dhcp = DhcpApi(self)
        self._voip = VoipApi(self)
        self._iptv = IptvApi(self)
        self._reboot = RebootApi(self)
        self._firewall = FirewallApi(self)
        self._dyndns = DynDnsApi(self)
        self._backup = BackupRestoreApi(self)
        self._screen = ScreenApi(self)


    ### Close the session
    def close(self):
        if self._session:
            self._session.close()
            self._session = None
        self._info.session_closed()
        self._intf.session_closed()
        self._wifi.session_closed()
        self._device.session_closed()
        self._stats.session_closed()
        self._dhcp.session_closed()
        self._voip.session_closed()
        self._iptv.session_closed()
        self._reboot.session_closed()
        self._firewall.session_closed()
        self._dyndns.session_closed()
        self._backup.session_closed()
        self._screen.session_closed()
