### Livebox Monitor Reboot APIs ###

from LiveboxMonitor.app import LmTools


# ################################ Reboot APIs ################################
class RebootApi:
	def __init__(self, iSession):
		self._session = iSession


	### Reboot the Livebox
	def rebootLivebox(self):
		try:
			r = self._session.request('NMC', 'reboot', { 'reason': 'GUI_Reboot' })
		except BaseException as e:
			LmTools.Error('NMC:reboot error: {}'.format(e))
			raise Exception('NMC:reboot service error.')

		if r is None:
			raise Exception('NMC:reboot service failed.')


	### Get reboot history
	def getRebootHistory(self):
		try:
			d = self._session.request('NMC.Reboot.Reboot', 'get')
		except BaseException as e:
			LmTools.Error('NMC.Reboot.Reboot:get error: {}'.format(e))
			raise Exception('NMC:reboot service error.')
	
		if d is not None:
			d = d.get('status')
		if d is None:
			raise Exception('NMC.Reboot.Reboot:get service failed.')
		return d

