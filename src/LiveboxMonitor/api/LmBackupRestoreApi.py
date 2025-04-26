### Livebox Monitor Backup & Restore APIs ###

from LiveboxMonitor.api.LmApi import LmApi
from LiveboxMonitor.app import LmTools


# ################################ Backup & Restore APIs ################################
class BackupRestoreApi(LmApi):
    def __init__(self, api, session):
        super(BackupRestoreApi, self).__init__(api, session)


    ### Get status
    def get_status(self):
        return self.call('NMC.NetworkConfig', 'get')


    ### Set Auto Backup enable status
    def set_auto_backup_enable(self, enable):
        self.call_no_check('NMC.NetworkConfig', 'enableNetworkBR', { 'state': enable })


    ### Start a backup
    def do_backup(self):
        self.call_no_check('NMC.NetworkConfig', 'launchNetworkBackup', { 'delay' : True })


    ### Start a restore
    def do_restore(self):
        self.call_no_check('NMC.NetworkConfig', 'launchNetworkRestore')
