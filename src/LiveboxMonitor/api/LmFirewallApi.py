### Livebox Monitor Firewall APIs ###

from LiveboxMonitor.app import LmTools


# ################################ VARS & DEFS ################################




# ################################ Firewall APIs ################################
class FirewallApi:
	def __init__(self, iApp):
		self._app = iApp
		self._session = iApp._session


	### Get IPv4 firewall level - return level + error message or None if successful
	def getIPv4FirewallLevel(self):
		try:
			aReply = self._session.request('Firewall', 'getFirewallLevel')
		except BaseException as e:
			LmTools.Error('Firewall:getFirewallLevel error: {}'.format(e))
			return None, 'Firewall:getFirewallLevel query error.'

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				return None, aErrors
			return aReply['status'], None
		else:
			return None, 'Firewall:getFirewallLevel query failed.'


	### Get IPv6 firewall level - return level + error message or None if successful
	def getIPv6FirewallLevel(self):
		try:
			aReply = self._session.request('Firewall', 'getFirewallIPv6Level')
		except BaseException as e:
			LmTools.Error('Firewall:getFirewallIPv6Level error: {}'.format(e))
			return None, 'Firewall:getFirewallIPv6Level query error.'

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				return None, aErrors
			return aReply['status'], None
		else:
			return None, 'Firewall:getFirewallIPv6Level query failed.'


	### Set IPv4 firewall level - return error message or None if successful
	def setIPv4FirewallLevel(self, iLevel):
		try:
			aReply = self._session.request('Firewall', 'setFirewallLevel', { 'level': iLevel })
		except BaseException as e:
			LmTools.Error('Firewall:setFirewallLevel error: {}'.format(e))
			return 'Firewall:setFirewallLevel query error.'

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				return aErrors
			elif not aReply['status']:
				return 'Firewall:setFirewallLevel query failed.'
		else:
			return 'Firewall:setFirewallLevel query failed.'

		return None


	### Set IPv6 firewall level - return error message or None if successful
	def setIPv6FirewallLevel(self, iLevel):
		try:
			aReply = self._session.request('Firewall', 'setFirewallIPv6Level', { 'level': iLevel })
		except BaseException as e:
			LmTools.Error('Firewall:setFirewallIPv6Level error: {}'.format(e))
			return 'Firewall:setFirewallIPv6Level query error.'

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				return aErrors
			elif not aReply['status']:
				return 'Firewall:setFirewallIPv6Level query failed.'
		else:
			return 'Firewall:setFirewallIPv6Level query failed.'

		return None
