### Livebox Monitor Reboot APIs ###

from LiveboxMonitor.api.LmApi import LmApi


# ################################ Reboot APIs ################################
class RebootApi(LmApi):
    def __init__(self, api_registry):
        super().__init__(api_registry)


    ### Get device reboot info
    def get_info(self):
        return self.call("NMC.Reboot", "get")


    ### Get reboot history
    def get_history(self):
        return self.call("NMC.Reboot.Reboot", "get")


    ### Reboot the device
    def reboot_device(self, reason="GUI_Reboot"):
        self.call("NMC", "reboot", {"reason": reason})


    ### Factory reset
    def factory_reset(self, reason="GUI_Reset", timeout=30):
        self.call("NMC", "reset", {"reason": reason})
