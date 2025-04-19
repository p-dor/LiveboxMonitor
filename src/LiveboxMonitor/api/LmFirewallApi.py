### Livebox Monitor Firewall APIs ###

from LiveboxMonitor.api.LmApi import LmApi
from LiveboxMonitor.app import LmTools


# ################################ VARS & DEFS ################################




# ################################ Firewall APIs ################################
class FirewallApi(LmApi):
	def __init__(self, iSession):
		super(FirewallApi, self).__init__(iSession)


	### Get IPv4 firewall level
	def getIPv4FirewallLevel(self):
		return self.call('Firewall', 'getFirewallLevel')


	### Get IPv6 firewall level
	def getIPv6FirewallLevel(self):
		return self.call('Firewall', 'getFirewallIPv6Level')


	### Set IPv4 firewall level
	def setIPv4FirewallLevel(self, iLevel):
		d = self.call('Firewall', 'setFirewallLevel', { 'level': iLevel })
		if not d:
			raise Exception('Firewall:setFirewallLevel service failed.')


	### Set IPv6 firewall level
	def setIPv6FirewallLevel(self, iLevel):
		d = self.call('Firewall', 'setFirewallIPv6Level', { 'level': iLevel })
		if not d:
			raise Exception('Firewall:setFirewallIPv6Level service failed.')
