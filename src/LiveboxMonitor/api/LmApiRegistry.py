### Livebox Monitor API objects registry ###

from LiveboxMonitor.api.LmFirewallApi import FirewallApi
from LiveboxMonitor.api.LmScreenApi import ScreenApi


# ################################ API objects registry ################################
class ApiRegistry:
	def __init__(self, iApp):
		self._firewall = FirewallApi(iApp)
		self._screen = ScreenApi(iApp)
