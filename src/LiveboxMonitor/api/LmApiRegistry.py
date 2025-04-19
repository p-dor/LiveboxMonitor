### Livebox Monitor API objects registry ###

from LiveboxMonitor.api.LmIntfApi import IntfApi
from LiveboxMonitor.api.LmWifiApi import WifiApi
from LiveboxMonitor.api.LmRebootApi import RebootApi
from LiveboxMonitor.api.LmFirewallApi import FirewallApi
from LiveboxMonitor.api.LmScreenApi import ScreenApi


# ################################ API objects registry ################################
class ApiRegistry:
	def __init__(self, iApp):
		s = iApp._session
		self._intf = IntfApi(s)
		self._wifi = WifiApi(s)
		self._reboot = RebootApi(s)
		self._firewall = FirewallApi(s)
		self._screen = ScreenApi(s)
