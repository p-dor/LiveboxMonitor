### Livebox Monitor Backup & Restore APIs ###

from LiveboxMonitor.api.LmApi import LmApi
from LiveboxMonitor.app import LmTools


# ################################ Backup & Restore APIs ################################
class BackupRestoreApi(LmApi):
	def __init__(self, iApi, iSession):
		super(BackupRestoreApi, self).__init__(iApi, iSession)


	### Get status
	def getStatus(self):
		return self.call('NMC.NetworkConfig', 'get')


	### Set Auto Backup enable status
	def setAutoBackupEnable(self, iEnable):
		self.callNoCheck('NMC.NetworkConfig', 'enableNetworkBR', { 'state': iEnable })


	### Start a backup
	def doBackup(self):
		self.callNoCheck('NMC.NetworkConfig', 'launchNetworkBackup', { 'delay' : True })


	### Start a restore
	def doRestore(self):
		self.callNoCheck('NMC.NetworkConfig', 'launchNetworkRestore')
