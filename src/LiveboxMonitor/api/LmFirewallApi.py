### Livebox Monitor Firewall APIs ###

from LiveboxMonitor.app import LmTools


# ################################ VARS & DEFS ################################




# ################################ Firewall APIs ################################
class FirewallApi:
	def __init__(self, iSession):
		self._session = iSession


	### Get IPv4 firewall level
	def getIPv4FirewallLevel(self):
		try:
			aReply = self._session.request('Firewall', 'getFirewallLevel')
		except BaseException as e:
			LmTools.Error('Firewall:getFirewallLevel error: {}'.format(e))
			raise Exception('Firewall:getFirewallLevel query error.')

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				raise Exception(aErrors)
			return aReply['status']
		else:
			raise Exception('Firewall:getFirewallLevel query failed.')


	### Get IPv6 firewall level
	def getIPv6FirewallLevel(self):
		try:
			aReply = self._session.request('Firewall', 'getFirewallIPv6Level')
		except BaseException as e:
			LmTools.Error('Firewall:getFirewallIPv6Level error: {}'.format(e))
			raise Exception('Firewall:getFirewallIPv6Level query error.')

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				raise Exception(aErrors)
			return aReply['status']
		else:
			raise Exception('Firewall:getFirewallIPv6Level query failed.')


	### Set IPv4 firewall level
	def setIPv4FirewallLevel(self, iLevel):
		try:
			aReply = self._session.request('Firewall', 'setFirewallLevel', { 'level': iLevel })
		except BaseException as e:
			LmTools.Error('Firewall:setFirewallLevel error: {}'.format(e))
			raise Exception('Firewall:setFirewallLevel query error.')

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				raise Exception(aErrors)
			elif not aReply['status']:
				raise Exception('Firewall:setFirewallLevel query failed.')
		else:
			raise Exception('Firewall:setFirewallLevel query failed.')


	### Set IPv6 firewall level
	def setIPv6FirewallLevel(self, iLevel):
		try:
			aReply = self._session.request('Firewall', 'setFirewallIPv6Level', { 'level': iLevel })
		except BaseException as e:
			LmTools.Error('Firewall:setFirewallIPv6Level error: {}'.format(e))
			raise Exception('Firewall:setFirewallIPv6Level query error.')

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				raise Exception(aErrors)
			elif not aReply['status']:
				raise Exception('Firewall:setFirewallIPv6Level query failed.')
		else:
			raise Exception('Firewall:setFirewallIPv6Level query failed.')
