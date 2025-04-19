### Livebox Monitor Interface APIs ###

from LiveboxMonitor.api.LmApi import LmApi
from LiveboxMonitor.app import LmTools



# ################################ Interface APIs ################################
class IntfApi(LmApi):
	def __init__(self, iSession):
		super(IntfApi, self).__init__(iSession)


	### Get interface information
	def getIntfInfo(self, iIntf):
		return self.call('NeMo.Intf.' + iIntf, 'get')
