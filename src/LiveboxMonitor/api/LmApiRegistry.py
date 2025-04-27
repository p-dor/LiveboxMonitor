### Livebox Monitor API objects registry ###

from LiveboxMonitor.api.LmLiveboxInfoApi import LiveboxInfoApi
from LiveboxMonitor.api.LmIntfApi import IntfApi
from LiveboxMonitor.api.LmWifiApi import WifiApi
from LiveboxMonitor.api.LmRebootApi import RebootApi
from LiveboxMonitor.api.LmFirewallApi import FirewallApi
from LiveboxMonitor.api.LmDynDnsApi import DynDnsApi
from LiveboxMonitor.api.LmBackupRestoreApi import BackupRestoreApi
from LiveboxMonitor.api.LmScreenApi import ScreenApi


# ################################ API objects registry ################################
class ApiRegistry:
    def __init__(self, session):
        self._info = LiveboxInfoApi(self, session)
        self._intf = IntfApi(self, session)
        self._wifi = WifiApi(self, session)
        self._reboot = RebootApi(self, session)
        self._firewall = FirewallApi(self, session)
        self._dyndns = DynDnsApi(self, session)
        self._backup = BackupRestoreApi(self, session)
        self._screen = ScreenApi(self, session)
