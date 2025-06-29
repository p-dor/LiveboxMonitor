### Livebox Monitor VoIP APIs ###

from LiveboxMonitor.api.LmApi import LmApi, LmApiException


# ################################ Livebox VoIP APIs ################################
class VoipApi(LmApi):
    def __init__(self, api_registry):
        super().__init__(api_registry)


    ### Get VoIP info
    def get_info(self):
        return self.call('VoiceService.VoiceApplication', 'listTrunks')


    ### Get list of calls for the given line
    def get_call_list(self, line='1'):
        d = self.call_no_check('VoiceService.VoiceApplication', 'getCallList', [{'line': '1'}], timeout=8)
        if isinstance(d, list):
            return d
        raise LmApiException('VoiceService.VoiceApplication:getCallList query error')


    ### Delete a call from its ID. If no ID indicated delete all.
    def delete_call(self, call_id=None):
        param = {'callId': call_id} if call_id else None
        self.call_no_check('VoiceService.VoiceApplication', 'clearCallList', param)


    ### Get list of contacts
    def get_contact_list(self):
        d = self.call_no_check('Phonebook', 'getAllContacts', timeout=20)
        if isinstance(d, list):
            return d
        raise LmApiException('Phonebook:getAllContacts query error')


    ### Get contact from its ID, return empty dict if not found
    def get_contact(self, contact_id):
        d = self.call_no_check('Phonebook', 'getContactByUniqueID', {'uniqueID': contact_id})
        if isinstance(d, dict):
            return d
        raise LmApiException('Phonebook:getContactByUniqueID query error')


    ### Add a contact, return its ID or none if max nb of contacts reached
    def add_contact(self, contact):
        return self.call_no_check('Phonebook', 'addContactAndGenUUID', {'contact': contact})


    ### Change a contact from its ID
    def change_contact(self, contact_id, contact):
        self.call('Phonebook', 'modifyContactByUniqueID', {'uniqueID': contact_id, 'contact': contact})


    ### Delete a contact from its ID. If no ID indicated delete all.
    def delete_contact(self, contact_id=None):
        if contact_id:
            self.call('Phonebook', 'removeContactByUniqueID', {'uniqueID': contact_id})
        else:
            self.call('Phonebook', 'removeAllContacts')


    ### Trigger ringtone. Default sound if none indicated.
    def ring(self, ringtone=None):
        param = {'ringtone': ringtone} if ringtone else None
        self.call_no_check('VoiceService.VoiceApplication', 'ring', param)


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
