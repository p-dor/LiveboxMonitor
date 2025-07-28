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
from LiveboxMonitor.api.LmRoutingApi import RoutingApi
from LiveboxMonitor.api.LmDynDnsApi import DynDnsApi
from LiveboxMonitor.api.LmBackupRestoreApi import BackupRestoreApi
from LiveboxMonitor.api.LmScreenApi import ScreenApi


# ################################ API objects registry ################################
class ApiRegistry:
    def __init__(self, session, is_repeater=False):
        self._registry = {}
        self._session = session
        self._is_repeater = is_repeater
        self._info = self.register('info', LiveboxInfoApi(self))
        self._intf = self.register('intf', IntfApi(self))
        self._wifi = self.register('wifi', WifiApi(self))
        self._device = self.register('device', DeviceApi(self))
        self._stats = self.register('stats', StatsApi(self))
        self._dhcp = self.register('dhcp', DhcpApi(self))
        self._voip = self.register('voip', VoipApi(self))
        self._iptv = self.register('iptv', IptvApi(self))
        self._reboot = self.register('reboot', RebootApi(self))
        self._firewall = self.register('firewall', FirewallApi(self))
        self._routing = self.register('routing', RoutingApi(self))
        self._dyndns = self.register('dyndns', DynDnsApi(self))
        self._backup = self.register('backup', BackupRestoreApi(self))
        self._screen = self.register('screen', ScreenApi(self))


    ### Add an API to the registry
    def register(self, name, api):
        self._registry[name] = api
        return api


    ### Close the session
    def close(self):
        if self._session:
            self._session.close()
            self._session = None
        for api in self._registry:
            self._registry[api].session_closed()
