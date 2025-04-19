### Livebox Monitor Wifi APIs ###

from LiveboxMonitor.api.LmApi import LmApi
from LiveboxMonitor.api.LmIntfApi import IntfApi
from LiveboxMonitor.app import LmTools


# ################################ Wifi APIs ################################
class WifiApi(LmApi):
	def __init__(self, iSession):
		super(WifiApi, self).__init__(iSession)


	### Get Wifi or Guest Interfaces setup - returns base, radio and vap
	def getIntf(self, iGuest = False):
		if iGuest:
			i = 'guest'
		else:
			i = 'lan'
		b = None
		w = None
		d = self.call('NeMo.Intf.' + i, 'getMIBs', { 'mibs': 'base wlanradio wlanvap' }, iTimeout = 25)
		if d is not None:
			b = d.get('base')
			w = d.get('wlanradio')
			d = d.get('wlanvap')
		if (b is None) or (w is None) or (d is None):
			raise Exception('NeMo.Intf.' + i + ':getMIBs service failed.')

		return b, w, d


	### Get Wifi status
	def getStatus(self):
		d = self.call('NMC.Wifi', 'get', iTimeout = 15)
		if not d:
			raise Exception('NMC.Wifi:get service failed.')
		return d


	### Get enable status
	def getEnable(self):
		return self.getStatus().get('Enable')


	### Activate/Deactivate Wifi
	def setEnable(self, iEnable):
		d = self.call('NMC.Wifi', 'set', { 'Enable': iEnable, 'Status' : iEnable }, iErrStr = 'Enable')
		if not d:
			raise Exception('NMC.Wifi:set Enable service failed.')


	### Get guest status
	def getGuestStatus(self):
		d = self.call('NMC.Guest', 'get', iTimeout = 15)
		if not d:
			raise Exception('NMC.Guest:get service failed.')
		return d


	### Get guest enable status
	def getGuestEnable(self):
		return self.getGuestStatus().get('Status') == 'Enabled'


	### Activate/Deactivate guest Wifi, timer in hours (0 == infinite)
	def setGuestEnable(self, iEnable, iTimer = 0):
		self.call('NMC.Guest', 'set', { 'Enable': iEnable })

		# Set timer, just log in case of error
		try:
			if iEnable:
				self.setGuestActivationTimer(iTimer)
			else:
				self.disableGuestActivationTimer()
		except:
			LmTools.Error(str(e))


	### Get guest activation timer - in seconds
	def getGuestActivationTimer(self):
		return int(self.call('NMC.WlanTimer', 'getActivationTimer', { 'InterfaceName': 'guest' }))


	### Set guest activation timer - in hours
	def setGuestActivationTimer(self, iTimer):
		self.call('NMC.WlanTimer', 'setActivationTimer', { 'Timeout': iTimer, 'InterfaceName': 'guest' })


	### Disable guest activation timer
	def disableGuestActivationTimer(self):
		d = self.call('NMC.WlanTimer', 'disableActivationTimer', { 'InterfaceName': 'guest' })
		if not d:
			raise Exception('NMC.WlanTimer:disableActivationTimer service failed.')


	### Set Configuration Mode - must be set to True if SSIDs are different between radio bands
	def setConfigurationMode(self, iMode):
		d = self.call('NMC.Wifi', 'set', { 'ConfigurationMode': iMode })
		if not d:
			raise Exception('NMC.Wifi:set ConfigurationMode service failed.')


	### Set WLAN Configuration
	def setWlanConfig(self, iMibs):
		self.call('NeMo.Intf.lan', 'setWLANConfig', { 'mibs': iMibs }, iTimeout = 35)


	### Set Wifi Scheduler on or off
	def setSchedulerEnable(self, iEnable):
		# Set PowerManagement profile
		if iEnable:
			p = [{ 'profile': 'WiFi',
				   'activate': True,
				   'type': 'Weekly',
				   'schedules': [{
                        'Day': 1,
                        'Hour': 0,
                        'Minute': 0,
                        'Second': 0,
                        'enable': True
                    }]
				}]
			d = self.call('PowerManagement', 'setScheduledProfiles', { 'profiles' : p })
		else:
			d = self.call('PowerManagement', 'setProfiles', { 'profiles' : [{'profile' : 'WiFi', 'activate' : False}] })
		if not d:
			LmTools.Error('PowerManagement method failed, trying legacy method.')
			return self.setSchedulerEnable_Legacy(iEnable)

		# ID has to remain 'wl0' - it is NOT corresponding to an intf key
		aID = 'wl0'

		# Get current schedule info
		d = self.call('Scheduler', 'getSchedule', { 'type' : 'WLAN', 'ID' : aID }, iFullReply = True)
		aStatus = d.get('status')	#Warning: seems status can be easily false, need to investigate
		if aStatus:
			d = d.get('data')
			if d:
				d = d.get('scheduleInfo')
		else:
			d = None
		if d:
			aSchedule = d
		else:
			raise Exception('Scheduler:getSchedule service failed for {} interface.'.format(aID))

		# Add schedule with proper status
		p = {}
		p['base'] = aSchedule.get('base')
		p['def'] = aSchedule.get('def')
		p['ID'] = aID
		p['schedule'] = aSchedule.get('schedule')
		p['enable'] = iEnable
		p['override'] = ''
		d = self.call('Scheduler', 'addSchedule', { 'type' : 'WLAN', 'info' : p })
		if not d:
			raise Exception('Scheduler:addSchedule service failed for {} interface.'.format(aID))


	### Legacy method to set Wifi Scheduler on or off
	### These calls were used by the deprecated "MaLiveBox" iOS app
	def setSchedulerEnable_Legacy(self, iEnable):
		# First save network configuration
		self.call('NMC.NetworkConfig', 'launchNetworkBackup', { 'delay' : True })
		aFailed = False
		aRestore = False
		aErrMsg = ''

		# Get Wifi interfaces
		d = self.call('NeMo.Intf.lan', 'getMIBs', { 'mibs': 'wlanvap' }, iTimeout = 25)
		w = d.get('wlanvap')
		if w is None:
			raise Exception('NeMo.Intf.lan:getMIBs service failed.')

		# Loop on each Wifi interface
		n = 0
		for i in w:
			# Get current schedule info
			d = self.call('Scheduler', 'getSchedule', { 'type' : 'WLAN', 'ID' : i }, iErrStr = i, iFullReply = True)
			aStatus = d.get('status')
			if aStatus:		#Warning: seems status can be easily false, need to investigate
				d = d.get('data')
				if d:
					d = d.get('scheduleInfo')
			else:
				d = None
			if d:
				aSchedule = d
			else:
				aErrMsg = 'Scheduler:getSchedule service failed for {} interface.'.format(i)
				LmTools.Error(aErrMsg)
				aFailed = True
				break

			# Add schedule with proper status
			p = {}
			p['enable'] = iEnable
			p['base'] = aSchedule.get('base')
			p['def'] = aSchedule.get('def')
			if iEnable:
				p['override'] = ''
			else:
				p['override'] = 'Enable'
			p['value'] = aSchedule.get('value')
			p['ID'] = i
			p['schedule'] = aSchedule.get('schedule')
			d = self.call('Scheduler', 'addSchedule', { 'type' : 'WLAN', 'info' : p })
			if not d:
				aErrMsg = 'Scheduler:addSchedule service failed for {} interface.\nLivebox might reboot.'.format(i)
				LmTools.Error(aErrMsg)
				aFailed = True
				if n:	# Trigger a restore (causing a Livebox reboot) if at least one succeeded previously
					aRestore = True
				break
			else:
				n += 1

		# Restore network configuration if failed and try another way
		if aFailed:
			if aRestore:
				self.call('NMC.NetworkConfig', 'launchNetworkRestore')		# Restore config, triggering a Livebox reboot
			aFailed = False

			for i in w:
				d = self.call('Scheduler', 'enableSchedule', { 'type' : 'WLAN', 'ID' : i, 'enable': iEnable }, iErrStr = i)
				if not d:
					aErrMsg = 'Scheduler:enableSchedule service failed for {} interface.'.format(i)
					LmTools.Error(aErrMsg)
					aFailed = True

		if aFailed:
			raise Exception(aErrMsg)


	### Get Wifi configuration
	def getConfig(self):
		aConfig = {}

		try:
			aConfig['Enable'] = self.getEnable()
			b, w, d = self.getIntf()
		except BaseException as e:
			LmTools.Error(str(e))
			return None

		# Get setup for each interface in wlanvap
		aIntf = []
		for s in d:
			# Get Wifi interface key in wlanradio list
			aIntfKey = None
			aBase = b.get(s)
			if aBase is not None:
				aLowLevelIntf = aBase.get('LLIntf')
				if aLowLevelIntf is not None:
					aIntfKey = next(iter(aLowLevelIntf))

			q = w.get(aIntfKey) if aIntfKey is not None else None
			r = d.get(s)
			if (q is None) or (r is None):
				continue

			c = {}
			aRadioBand = q.get('OperatingFrequencyBand')
			if aRadioBand is None:
				aRadioBand = s
			c['Name'] = 'Wifi ' + aRadioBand
			c['Key'] = s
			c['LLIntf'] = aIntfKey
			c['SSID'] = r.get('SSID')
			c['Enable'] = aBase.get('Enable')
			c['Broadcast'] = r.get('SSIDAdvertisementEnabled')

			t = r.get('Security')
			if t is not None:
				c['Secu'] = t.get('ModeEnabled')
				c['SecuAvail'] = t.get('ModesAvailable')
				c['KeyPass'] = t.get('KeyPassPhrase')
			else:
				c['Secu'] = None
				c['SecuAvail'] = None
				c['KeyPass'] = None

			t = r.get('WPS')
			if t is not None:
				c['WPS'] = t.get('Enable')
			else:
				c['WPS'] = None

			t = r.get('MACFiltering')
			if t is not None:
				c['MACFiltering'] = t.get('Mode')
			else:
				c['MACFiltering'] = None

			c['Mode'] = q.get('OperatingStandards')
			c['ChannelAutoSupport'] = q.get('AutoChannelSupported')
			c['ChannelAuto'] = q.get('AutoChannelEnable')
			c['Channel'] = q.get('Channel')

			aIntf.append(c)
		aConfig['Intf'] = aIntf

		# Get available modes & channels per interface
		aModes = {}
		for c in aIntf:
			aIntfKey = c['LLIntf']
			aIntfApi = IntfApi(self._session)
			try:
				d = aIntfApi.getIntfInfo(aIntfKey)
			except BaseException as e:
				LmTools.Error(str(e))
				d = None
			if d is not None:
				m = {}
				m['Modes'] = d.get('SupportedStandards')
				m['Channels'] = d.get('PossibleChannels')
				m['ChannelsInUse'] = d.get('ChannelsInUse')
				aModes[aIntfKey] = m
		aConfig['Modes'] = aModes

		return aConfig


	### Set Wifi configuration - returns True if all successful
	def setConfig(self, iOldConfig, iNewConfig):
		aOldIntf = iOldConfig['Intf']
		aNewIntf = iNewConfig['Intf']
		aStatus = True

		# Check if SSIDs are the same accross frequencies before and after
		s = None
		aOldUniqueSSID = True
		for o in aOldIntf:
			if s is None:
				s = o['SSID']
			else:
				if o['SSID'] != s:
					aOldUniqueSSID = False
					break
		s = None
		aNewUniqueSSID = True
		for n in aNewIntf:
			if s is None:
				s = n['SSID']
			else:
				if n['SSID'] != s:
					aNewUniqueSSID = False
					break

		# If SSID homogeneity changed, change the Configuration Mode
		if aOldUniqueSSID != aNewUniqueSSID:
			try:
				self.setConfigurationMode(aNewUniqueSSID)
			except BaseException as e:
				LmTools.Error(str(e))
				aStatus = False

		# Initiate parameters
		aVap = {}
		aRadio = {}
		aPenable = {}

		# Check which setup changed
		for o, n in zip(aOldIntf, aNewIntf):
			v = {}
			if (o['SSID'] != n['SSID']):
				v['SSID'] = n['SSID']
			if (o['Broadcast'] != n['Broadcast']):
				v['SSIDAdvertisementEnabled'] = n['Broadcast']
			if (o['Secu'] != n['Secu']):
				v['Security'] = { 'ModeEnabled': n['Secu'], 'KeyPassPhrase': n['KeyPass'] }
			elif (o['KeyPass'] != n['KeyPass']):
				v['Security'] = { 'KeyPassPhrase': n['KeyPass'] }
			if (o['WPS'] != n['WPS']):
				v['WPS'] = { 'Enable': n['WPS'] }
			if (o['MACFiltering'] != n['MACFiltering']):
				v['MACFiltering'] = { 'Mode': n['MACFiltering'] }
			if ((o['ChannelAuto'] != n['ChannelAuto']) or 
				(o['Channel'] != n['Channel']) or
				(o['Mode'] != n['Mode'])):
				if n['ChannelAuto']:
					r = { 'AutoChannelEnable': True, 'OperatingStandards': n['Mode'] }
				else:
					r = { 'AutoChannelEnable': False, 'Channel': n['Channel'], 'OperatingStandards': n['Mode'] }
			else:
				r = {}
			if (o['Enable'] != n['Enable']):
				aEnable = n['Enable']
				p = {'Enable': aEnable, 'PersistentEnable': aEnable, 'Status': aEnable }
			else:
				p = {}

			if len(v):
				aVap[n['Key']] = v
			if len(r):
				aRadio[n['LLIntf']] = r
			if len(p):
				aPenable[n['Key']] = p

		# Call the API if at least one parameter changed
		if len(aVap) or len(aRadio) or len(aPenable):
			aParams = {}
			aParams['penable'] = aPenable
			if len(aVap):
				aParams['wlanvap'] = aVap
			if len(aRadio):
				aParams['wlanradio'] = aRadio
			try:
				self.setWlanConfig(aParams)
			except BaseException as e:
				LmTools.Error(str(e))
				aStatus = False

		# Activate/Deactivate Wifi
		if (iOldConfig['Enable'] != iNewConfig['Enable']):
			try:
				self.setEnable(iNewConfig['Enable'])
			except BaseException as e:
				LmTools.Error(str(e))
				aStatus = False				

		return aStatus


	### Get Guest Wifi configuration
	def getGuestConfig(self):
		# Get activation total duration
		aConfig = {}

		try:
			s = self.getGuestStatus()
			b, w, d = self.getIntf(True)
		except BaseException as e:
			LmTools.Error(str(e))
			return None

		aConfig['Enable'] = s.get('Status') == 'Enabled'

		if s.get('ActivationTimeout', 0) != 0:
			aStartTime = LmTools.LiveboxTimestamp(s.get('StartTime'))
			aEndTime = LmTools.LiveboxTimestamp(s.get('ValidTime'))
			if (aStartTime is None) or (aEndTime is None):
				LmTools.Error('Activation timeout timestamps error')
				aDiff = 0
			else:
				aDiff = int((aEndTime - aStartTime).total_seconds())
			aConfig['Duration'] = aDiff
		else:
			aConfig['Duration'] = 0

		# Get activation remaining time
		try:
			aConfig['Timer'] = self.getGuestActivationTimer()
		except BaseException as e:
			LmTools.Error(str(e))
			aConfig['Timer'] = 0

		# Get setup for each interface
		aIntf = []
		for s in d:
			# Get Wifi interface key in wlanradio list
			aIntfKey = None
			aBase = b.get(s)
			if aBase is not None:
				aLowLevelIntf = aBase.get('LLIntf')
				if aLowLevelIntf is not None:
					aIntfKey = next(iter(aLowLevelIntf))

			q = w.get(aIntfKey) if aIntfKey is not None else None
			r = d.get(s)
			if (q is None) or (r is None):
				continue

			c = {}
			aRadioBand = q.get('OperatingFrequencyBand')
			if aRadioBand is None:
				aRadioBand = s
			c['Name'] = 'Guest ' + aRadioBand
			c['Key'] = s
			c['LLIntf'] = aIntfKey
			c['SSID'] = r.get('SSID')
			c['Enable'] = aBase.get('Enable')
			c['Broadcast'] = r.get('SSIDAdvertisementEnabled')

			t = r.get('Security')
			if t is not None:
				c['Secu'] = t.get('ModeEnabled')
				c['SecuAvail'] = t.get('ModesAvailable')
				c['KeyPass'] = t.get('KeyPassPhrase')
			else:
				c['Secu'] = None
				c['SecuAvail'] = None
				c['KeyPass'] = None

			t = r.get('WPS')
			if t is not None:
				c['WPS'] = t.get('Enable')
			else:
				c['WPS'] = None

			t = r.get('MACFiltering')
			if t is not None:
				c['MACFiltering'] = t.get('Mode')
			else:
				c['MACFiltering'] = None

			aIntf.append(c)
		aConfig['Intf'] = aIntf

		return aConfig


	### Set Guest Wifi configuration - returns True if all successful
	def setGuestConfig(self, iOldConfig, iNewConfig):
		aOldIntf = iOldConfig['Intf']
		aNewIntf = iNewConfig['Intf']
		aStatus = True

		# Initiate parameters
		aVap = {}
		aPenable = {}

		# Check which setup changed
		for o, n in zip(aOldIntf, aNewIntf):
			v = {}
			if (o['SSID'] != n['SSID']):
				v['SSID'] = n['SSID']
			if (o['Broadcast'] != n['Broadcast']):
				v['SSIDAdvertisementEnabled'] = n['Broadcast']
			if (o['Secu'] != n['Secu']):
				v['Security'] = { 'ModeEnabled': n['Secu'], 'KeyPassPhrase': n['KeyPass'] }
			elif (o['KeyPass'] != n['KeyPass']):
				v['Security'] = { 'KeyPassPhrase': n['KeyPass'] }
			if (o['WPS'] != n['WPS']):
				v['WPS'] = { 'Enable': n['WPS'] }
			if (o['MACFiltering'] != n['MACFiltering']):
				v['MACFiltering'] = { 'Mode': n['MACFiltering'] }
			if (o['Enable'] != n['Enable']):
				aEnable = n['Enable']
				p = {'Enable': aEnable, 'PersistentEnable': aEnable, 'Status': aEnable }
			else:
				p = {}

			if len(v):
				aVap[n['Key']] = v
			if len(p):
				aPenable[n['Key']] = p

		# Call the API if at least one parameter changed
		if len(aVap) or len(aPenable):
			aParams = {}
			aParams['penable'] = aPenable
			if len(aVap):
				aParams['wlanvap'] = aVap
			try:
				self.setWlanConfig(aParams)
			except BaseException as e:
				LmTools.Error(str(e))
				aStatus = False

		# Activate/Deactivate Guest Wifi or reset timer
		try:
			if (iOldConfig['Enable'] != iNewConfig['Enable']):
				self.setGuestEnable(iNewConfig['Enable'], iNewConfig['Duration'] // 3600)
			elif iNewConfig['Enable']:
				self.setGuestActivationTimer(iNewConfig['Duration'] // 3600)
		except BaseException as e:
			LmTools.Error(str(e))
			aStatus = False

		return aStatus
