### Livebox Monitor screen & LEDs APIs ###

from LiveboxMonitor.app import LmTools


# ################################ Screen APIs ################################
class ScreenApi:
	def __init__(self, iSession):
		self._session = iSession


	### Get Orange LED levels
	def getOrangeLedLevel(self):
		try:
			aReply = self._session.request('LEDs.LED.Orange', 'get')
		except BaseException as e:
			LmTools.Error('LEDs.LED.Orange:get error: {}'.format(e))
			raise Exception('LEDs.LED.Orange:get query error.')

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				raise Exception(aErrors)
			aBrightness = aReply['status'].get('Brightness')
			if aBrightness is not None:
				return aBrightness
			else:
				LmTools.Error('LEDs.LED.Orange:get error: no Brightness field')

		raise Exception('LEDs.LED.Orange:get query failed.')


	### Get White LED levels
	def getWhiteLedLevel(self):
		try:
			aReply = self._session.request('LEDs.LED.White', 'get')
		except BaseException as e:
			LmTools.Error('LEDs.LED.White:get error: {}'.format(e))
			raise Exception('LEDs.LED.White:get query error.')

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				raise Exception(aErrors)
			aBrightness = aReply['status'].get('Brightness')
			if aBrightness is None:
				return aBrightness
			else:
				LmTools.Error('LEDs.LED.White:get error: no Brightness field')

		raise Exception('LEDs.LED.White:get query failed.')


	### Get Show Wifi Password setup
	def getShowWifiPassword(self):
		try:
			aReply = self._session.request('Screen', 'getShowWifiPassword')
		except BaseException as e:
			LmTools.Error('Screen:getShowWifiPassword error: {}'.format(e))
			raise Exception('Screen:getShowWifiPassword error.')

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				raise Exception(aErrors)
			return aReply['status']

		raise Exception('Screen:getShowWifiPassword query failed.')


	### Set Orange LED level
	def setOrangeLedLevel(self, iLevel):
		try:
			aReply = self._session.request('LEDs.LED.Orange', 'set', { 'Brightness': iLevel })
		except BaseException as e:
			LmTools.Error('LEDs.LED.Orange:set error: {}'.format(e))
			raise Exception('LEDs.LED.Orange:set query error.')

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				raise Exception(aErrors)
			elif not aReply['status']:
				raise Exception('LEDs.LED.Orange:set query failed.')
		else:
			raise Exception('LEDs.LED.Orange:set query failed.')


	### Set White LED level
	def setWhiteLedLevel(self, iLevel):
		try:
			aReply = self._session.request('LEDs.LED.White', 'set', { 'Brightness': iLevel })
		except BaseException as e:
			LmTools.Error('LEDs.LED.White:set error: {}'.format(e))
			raise Exception('LEDs.LED.White:set query error.')

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				raise Exception(aErrors)
			elif not aReply['status']:
				raise Exception('LEDs.LED.White:set query failed.')
		else:
			raise Exception('LEDs.LED.White:set query failed.')


	### Set Show Wifi Password setup
	def setShowWifiPassword(self, iShowWifiPassword):
		try:
			aReply = self._session.request('Screen', 'setShowWifiPassword', { 'Enable': iShowWifiPassword })
		except BaseException as e:
			LmTools.Error('Screen:setShowWifiPassword error: {}'.format(e))
			raise Exception('Screen:setShowWifiPassword query error.')

		if (aReply is not None) and ('status' in aReply):
			aErrors = LmTools.GetErrorsFromLiveboxReply(aReply)
			if len(aErrors):
				raise Exception(aErrors)
		else:
			return 'Screen:setShowWifiPassword query failed.'
