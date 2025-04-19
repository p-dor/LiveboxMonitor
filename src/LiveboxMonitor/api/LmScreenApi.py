### Livebox Monitor screen & LEDs APIs ###

from LiveboxMonitor.api.LmApi import LmApi
from LiveboxMonitor.app import LmTools


# ################################ Screen APIs ################################
class ScreenApi(LmApi):
	def __init__(self, iSession):
		super(ScreenApi, self).__init__(iSession)


	### Get Orange LED levels
	def getOrangeLedLevel(self):
		d = self.call('LEDs.LED.Orange', 'get')
		aBrightness = d.get('Brightness')
		if aBrightness is None:
			raise Exception('LEDs.LED.Orange:get error: no Brightness field')
		return aBrightness


	### Get White LED levels
	def getWhiteLedLevel(self):
		d = self.call('LEDs.LED.White', 'get')
		aBrightness = d.get('Brightness')
		if aBrightness is None:
			raise Exception('LEDs.LED.White:get error: no Brightness field')
		return aBrightness


	### Get Show Wifi Password setup
	def getShowWifiPassword(self):
		return self.callNoCheck('Screen', 'getShowWifiPassword')


	### Set Orange LED level
	def setOrangeLedLevel(self, iLevel):
		self.call('LEDs.LED.Orange', 'set', { 'Brightness': iLevel })


	### Set White LED level
	def setWhiteLedLevel(self, iLevel):
		self.call('LEDs.LED.White', 'set', { 'Brightness': iLevel })


	### Set Show Wifi Password setup
	def setShowWifiPassword(self, iShowWifiPassword):
		self.callNoCheck('Screen', 'setShowWifiPassword', { 'Enable': iShowWifiPassword })
