### Livebox Monitor Reboot APIs ###

from LiveboxMonitor.api.LmApi import LmApi
from LiveboxMonitor.app import LmTools


# ################################ Reboot APIs ################################
class RebootApi(LmApi):
    def __init__(self, api, session):
        super(RebootApi, self).__init__(api, session)


    ### Reboot the Livebox
    def reboot_livebox(self):
        self.call('NMC', 'reboot', {'reason': 'GUI_Reboot'})


    ### Get reboot history
    def get_reboot_history(self):
        return self.call('NMC.Reboot.Reboot', 'get')
