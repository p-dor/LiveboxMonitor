### Livebox Monitor Firewall APIs ###

from LiveboxMonitor.api.LmApi import LmApi
from LiveboxMonitor.app import LmTools


# ################################ VARS & DEFS ################################




# ################################ Firewall APIs ################################
class FirewallApi(LmApi):
	def __init__(self, iApi, iSession):
		super(FirewallApi, self).__init__(iApi, iSession)


	### Get IPv4 firewall level
	def getIPv4FirewallLevel(self):
		return self.call('Firewall', 'getFirewallLevel')


	### Get IPv6 firewall level
	def getIPv6FirewallLevel(self):
		return self.call('Firewall', 'getFirewallIPv6Level')


	### Set IPv4 firewall level
	def setIPv4FirewallLevel(self, iLevel):
		self.call('Firewall', 'setFirewallLevel', { 'level': iLevel })


	### Set IPv6 firewall level
	def setIPv6FirewallLevel(self, iLevel):
		self.call('Firewall', 'setFirewallIPv6Level', { 'level': iLevel })


	### Get IPv4 & IPv6 respond to ping setup
	def getRespondToPing(self):
		# ###Info### - works also for other sourceInterfaces such as veip0, eth0, voip, etc, but usefulness?
		return self.call('Firewall', 'getRespondToPing', { 'sourceInterface': 'data' })


	### Set IPv6 firewall level - iEnable must be a dict with 'enableIPv4' & 'enableIPv6' boolean values
	def setRespondToPing(self, iEnable):
		self.call('Firewall', 'setRespondToPing', { 'sourceInterface': 'data', 'service_enable': iEnable })
