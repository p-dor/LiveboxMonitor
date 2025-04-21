### Livebox Monitor Reboot APIs ###

from LiveboxMonitor.api.LmApi import LmApi
from LiveboxMonitor.app import LmTools


# ################################ Reboot APIs ################################
class RebootApi(LmApi):
	def __init__(self, iApi, iSession):
		super(RebootApi, self).__init__(iApi, iSession)


	### Reboot the Livebox
	def rebootLivebox(self):
		self.call('NMC', 'reboot', { 'reason': 'GUI_Reboot' })


	### Get reboot history
	def getRebootHistory(self):
		return self.call('NMC.Reboot.Reboot', 'get')
