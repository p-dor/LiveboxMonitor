### Livebox Monitor API objects registry ###

from LiveboxMonitor.api.LmLiveboxInfoApi import LiveboxInfoApi
from LiveboxMonitor.api.LmIntfApi import IntfApi
from LiveboxMonitor.api.LmWifiApi import WifiApi
from LiveboxMonitor.api.LmRebootApi import RebootApi
from LiveboxMonitor.api.LmFirewallApi import FirewallApi
from LiveboxMonitor.api.LmBackupRestoreApi import BackupRestoreApi
from LiveboxMonitor.api.LmScreenApi import ScreenApi


# ################################ API objects registry ################################
class ApiRegistry:
	def __init__(self, iSession):
		self._info = LiveboxInfoApi(self, iSession)
		self._intf = IntfApi(self, iSession)
		self._wifi = WifiApi(self, iSession)
		self._reboot = RebootApi(self, iSession)
		self._firewall = FirewallApi(self, iSession)
		self._backup = BackupRestoreApi(self, iSession)
		self._screen = ScreenApi(self, iSession)
