### Livebox Monitor API objects registry ###

from LiveboxMonitor.api.LmFirewallApi import FirewallApi
from LiveboxMonitor.api.LmScreenApi import ScreenApi


# ################################ API objects registry ################################
class ApiRegistry:
	def __init__(self, iApp):
		s = iApp._session
		self._firewall = FirewallApi(s)
		self._screen = ScreenApi(s)
