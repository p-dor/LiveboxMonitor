### Livebox Monitor VoIP APIs ###

from LiveboxMonitor.api.LmApi import LmApi


# ################################ Livebox VoIP APIs ################################
class VoipApi(LmApi):
    def __init__(self, api_registry):
        super(VoipApi, self).__init__(api_registry)


    ### Get VoIP info
    def get_info(self):
        return self.call('VoiceService.VoiceApplication', 'listTrunks')


    ### Get DECT name - warning: no DECT from LB6
    def get_dect_name(self):
        return self.call('DECT', 'getName')


    ### Get DECT PIN - warning: no DECT from LB6
    def get_dect_pin(self):
        return self.call('DECT', 'getPIN')


    ### Get DECT RFPI - warning: no DECT from LB6
    def get_dect_rfpi(self):
        return self.call('DECT', 'getRFPI')


    ### Get DECT Software Version - warning: no DECT from LB6
    def get_dect_software_version(self):
        return self.call('DECT', 'getVersion')


    ### Get DECT CAT-iq Version - warning: no DECT from LB6
    def get_dect_catiq_version(self):
        return self.call('DECT', 'getStandardVersion')


    ### Get DECT Pairing Status - warning: no DECT from LB6
    def get_dect_pairing_status(self):
        return self.call('DECT', 'getPairingStatus')


    ### Get DECT Radio State - warning: no DECT from LB6
    def get_dect_radio_state(self):
        return self.call_no_check('DECT', 'getRadioState')


    ### Get DECT Repeater Status - warning: no DECT from LB6
    def get_dect_repeater_status(self):
        return self.call('DECT.Repeater', 'get')
