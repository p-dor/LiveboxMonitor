### Livebox Monitor API objects registry ###

from LiveboxMonitor.api.LmLiveboxInfoApi import LiveboxInfoApi
from LiveboxMonitor.api.LmIntfApi import IntfApi
from LiveboxMonitor.api.LmWifiApi import WifiApi
from LiveboxMonitor.api.LmDeviceApi import DeviceApi
from LiveboxMonitor.api.LmRebootApi import RebootApi
from LiveboxMonitor.api.LmFirewallApi import FirewallApi
from LiveboxMonitor.api.LmDynDnsApi import DynDnsApi
from LiveboxMonitor.api.LmBackupRestoreApi import BackupRestoreApi
from LiveboxMonitor.api.LmScreenApi import ScreenApi


# ################################ API objects registry ################################
class ApiRegistry:
    def __init__(self, session):
        self._session = session
        self._info = LiveboxInfoApi(self)
        self._intf = IntfApi(self)
        self._wifi = WifiApi(self)
        self._device = DeviceApi(self)
        self._reboot = RebootApi(self)
        self._firewall = FirewallApi(self)
        self._dyndns = DynDnsApi(self)
        self._backup = BackupRestoreApi(self)
        self._screen = ScreenApi(self)
