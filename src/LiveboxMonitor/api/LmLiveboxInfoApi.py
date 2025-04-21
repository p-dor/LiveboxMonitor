### Livebox Monitor Livebox Info APIs ###

from LiveboxMonitor.api.LmApi import LmApi
from LiveboxMonitor.app import LmTools


# ################################ VARS & DEFS ################################

# Livebox versions map
LIVEBOX_MODEL_MAP = {
	'Livebox 4': 4,
	'Livebox Fibre': 5,
	'Livebox 6': 6,
	'Livebox 7': 7
	}


# ################################ Livebox Info APIs ################################
class LiveboxInfoApi(LmApi):
	def __init__(self, iApi, iSession):
		super(LiveboxInfoApi, self).__init__(iApi, iSession)
		self._liveboxMAC = None
		self._liveboxModel = None
		self._softwareVersion = None


	### Get Livebox basic info
	def getLiveboxInfo(self):
		return self.call('DeviceInfo', 'get')


	### Set Livebox basic info cache
	def setLiveboxInfoCache(self):
		try:
			d = self.getLiveboxInfo()
		except BaseException as e:
			LmTools.Error(str(e))
			LmTools.Error('Cannot determine Livebox model.')
			self._liveboxMAC = ''
			self._liveboxModel = 0
			self._softwareVersion = ''
		else:
			self._liveboxMAC = d.get('BaseMAC', '').upper()
			aModel = d.get('ProductClass', '')
			if aModel:
				self._liveboxModel = LIVEBOX_MODEL_MAP.get(aModel)
			if self._liveboxModel is None:
				LmTools.Error('Unknown Livebox model: {}.'.format(aModel))
				self._liveboxModel = 0
			self._softwareVersion = d.get('SoftwareVersion', '')


	### Get Livebox MAC
	def getLiveboxMAC(self):
		if not self._liveboxMAC:
			self.setLiveboxInfoCache()
		return self._liveboxMAC


	### Get Livebox model
	def getLiveboxModel(self):
		if not self._liveboxModel:
			self.setLiveboxInfoCache()
		return self._liveboxModel


	### Get Livebox software version
	def getSoftwareVersion(self):
		if not self._softwareVersion:
			self.setLiveboxInfoCache()
		return self._softwareVersion
