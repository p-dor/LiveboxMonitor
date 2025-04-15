### Livebox Monitor API modules registry ###

from LiveboxMonitor.api.LmFirewallApi import FirewallApi


# ################################ VARS & DEFS ################################




# ################################ Screen APIs ################################
class ApiRegistry:
	def __init__(self, iApp):
		self._firewall = FirewallApi(iApp)
