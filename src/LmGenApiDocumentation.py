### Livebox Monitor module to generate API documentation ###

import os
import json

from src import LmTools



# ################################ VARS & DEFS ################################
MODULES = [
	'AccountManager',
	'Audiphone',
	'AutoDiag',
	'BulkData',
	'CaptivePortal',
	'ConMon',
	'Conntrack',
	'CPUStats',
	'CupsService',				# LB5 only
	'DECT',						# LB5 only
	'DeviceInfo',
	'DeviceLookup',
	'DeviceManagement',
	'DeviceManager',
	'Devices',
	'BCMPlugin',
	'DHCPv4',
	'DHCPv6',
	'DHCPv6Client',
	'DLNA',
	'DNS',
	'DNSSD',
	'Domino',
	'DSPGDECT',					# LB5 only
	'DSPPlugin',
	'DummyPlugin',
	'DynDNS',
	'eventmanager',
	'FaultMonitor',
	'Firewall',
	'Flowstats',
	'GenLog',
	'Gpon',
	'History',
	'HomeLan',
	'HTTPService',
	'IEEE1905',
	'Invocation',
	'IoTService',
	'IPPingDiagnostics',
	'IPsec',
	'KMCD',
	'Launcher',
	'LLMNR',
	'Locations',
	'LXCManager',
	'Maculan',
	'ManagementServer',
	'Manifests',
	'MQTTBroker',
	'MQTTMessages',
	'MSS',
	'NeMo',
	'NetDev',
	'NetMaster',
	'NMC',
	'ObjectMonitor',
	'OopsTracker',
	'OrangeDynDNS',
	'OrangeRemoteAccess',
	'OrangeServices',
	'OUI',
	'Pass',
	'PasswordRecovery',
	'Phonebook',
	'PnP',
	'PowerManagement',			# LB6 only
	'PPP',
	'Probe',
	'Process',
	'ProcessMonitor',
	'Profiles',
	'QueueManagement',
	'RemoteAccess',
	'RouterAdvertisement',
	'sah',
	'SAHPairing',
	'SambaService',
	'ServiceInvocation',		# LB7 only
	'Scheduler',
	'Screen',					# LB6 only
	'SFP',						# LB4 only
	'SpeedTest',
	'SrvInterface',
	'SSLEServer',
	'SSW',
	'SSW.Steering',
	'SSW.FeatureConfig',
	'StorageService',
	'Time',
	'ToD',
	'TopologyDiagnostics',
	'UDPEchoConfig',
	'Upgrade',
	'UplinkMonitor',
	'UPnP',
	'UPnP-IGD',
	'URLMon',					# LB5 only
	'USBHosts',
	'UserInterface',
	'UserManagement',
	'VoiceActivation',
	'VoiceService',
	'VoWifi',
	'VPN',
	'WatchDog',
	'WebuiupgradeService',
	'WiFiBCM',
	'WiFiQUAN',					# LB5 only
	'WLanScheduler',
	'WOL',
	'WOLProxy'
]

INDENT = '  '



# ################################ GenApiDoc Class ################################

class LmGenApiDoc:
	def __init__(self, iApp, iFolder, iFilterValue):
		self._app = iApp
		self._session = iApp._session
		self._softwareVersion = iApp._liveboxSoftwareVersion
		self._folder = iFolder
		self._filter = iFilterValue
		self._file = None


	### Generate files for each known module
	def genModuleFiles(self):
		# Generate for each known module
		for m in MODULES:
			self.genModuleFile(m)

		# Generate for all interfaces
		try:
			d = self._session.request('NeMo.Intf.lo:getIntfs', { "traverse": "all" })
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			d = None
		if d is not None:
			d = d.get('status')
		if type(d).__name__ == 'list':
			for m in d:
				self.genModuleFile('NeMo.Intf.' + m)


	### Generate all modules in flat file
	def genFullFile(self):
		self.genModuleFile('.', '_ALL MODULES_')


	### Generate process list file
	def genProcessListFile(self):
		self.genModuleFile('*', '_PROCESSES_')


	### Generate JSON result file for a module - useful only to get raw results
	def genModuleJsonFile(self, iModule, iName = None):
		if iName is None:
			iName = iModule

		try:
			d = self._session.request(iModule, iGet = True, iTimeout = 15)
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			return

		if d is None:
			return

		# Module doesn't exist error
		if (type(d).__name__ == 'dict') and (d.get('error', 0) == 196618):	
			return

		aFilePath = os.path.join(self._folder, iName + '_json.txt')
		try:
			self._file = open(aFilePath, 'w')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			return

		self._file.write('=== LIVEBOX SOFTWARE VERSION: {}\n\n'.format(self._softwareVersion))
		json.dump(d, self._file, indent = 4)

		try:
			self._file.close()
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
		self._file = None


	### Generate document file for a module
	def genModuleFile(self, iModule, iName = None):
		if iName is None:
			iName = iModule

		self._app.updateTask(iName)

		try:
			d = self._session.request(iModule, iGet = True, iTimeout = 15)
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			return

		if d is None:
			return

		# Module doesn't exist error
		if (type(d).__name__ == 'dict') and (d.get('error', 0) == 196618):	
			return

		aFilePath = os.path.join(self._folder, iName + '.txt')
		try:
			self._file = open(aFilePath, 'w')
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
			return

		self._file.write('=== LIVEBOX SOFTWARE VERSION: {}\n\n'.format(self._softwareVersion))
		if type(d).__name__ != 'list':
			d = [d]
		for o in d:
			if not self.genObject(o):
				json.dump(o, self._file, indent = 4)

		try:
			self._file.close()
		except BaseException as e:
			LmTools.Error('Error: {}'.format(e))
		self._file = None


	### Generate documentation for an object - return False if not an object
	def genObject(self, iObject, iInstance = False, iLevel = 0):
		o = iObject.get('objectInfo')
		if o is None:
			return False

		aIdent = INDENT * iLevel
		if iInstance:
			self._file.write(aIdent + '-----------------------------------------------------------------------\n')
			self._file.write(aIdent + 'INSTANCE: {}.{} - Name: {}.{}\n'.format(o.get('keyPath'), o.get('key'),
																			   o.get('indexPath'), o.get('name')))
		else:
			self._file.write(aIdent + '=======================================================================\n')
			self._file.write(aIdent + 'OBJECT: {}.{} - Name: {}.{}\n'.format(o.get('keyPath'), o.get('key'),
																			 o.get('indexPath'), o.get('name')))

		self.genParameters(iObject, iLevel)
		self.genFunctions(iObject, iLevel)
		self._file.write('\n')
		if not self._filter:
			self.genInstances(iObject, iLevel)
		self.genChildren(iObject, iLevel)

		return True


	### Generate parameters
	def genParameters(self, iObject, iLevel = 0):
		o = iObject.get('parameters')
		if (o is not None) and len(o):
			aIdent = INDENT * iLevel
			self._file.write(aIdent + ' == PARAMETERS:\n')
			for p in o:
				self.genParameter(p, iLevel + 1)


	### Generate a parameter
	def genParameter(self, iParam, iLevel = 0):
		aIdent = INDENT * iLevel

		# Collect values
		aName = iParam.get('name')
		aType = iParam.get('type')
		aAttributes = ''
		aAttributesDict = iParam.get('attributes')
		for a in aAttributesDict:
			if aAttributesDict[a]:
				if len(aAttributes):
					aAttributes += ', '
				aAttributes += a
		aValue = iParam.get('value')
		aValidator = iParam.get('validator')

		# Rendering
		self._file.write(aIdent + '- {} (type: {})\n'.format(aName, aType))
		aIdent = INDENT * (iLevel + 2)
		if len(aAttributes):
			self._file.write(aIdent + 'Attributes: {}\n'.format(aAttributes))
		if (not self._filter) and (aValue is not None):
			if (type(aValue).__name__ == 'str'):
				if len(aValue): 
					self._file.write(aIdent + 'Value: \'{}\'\n'.format(aValue))
			else:
				self._file.write(aIdent + 'Value: {}\n'.format(aValue))
		if aValidator is not None:
			self._file.write(aIdent + 'Validator: {}\n'.format(aValidator))


	### Generate functions
	def genFunctions(self, iObject, iLevel = 0):
		o = iObject.get('functions')
		if (o is not None) and len(o):
			aIdent = INDENT * iLevel
			self._file.write(aIdent + ' == FUNCTIONS:\n')
			for f in o:
				self.genFunction(f, iLevel + 1)


	### Generate a function
	def genFunction(self, iFunc, iLevel = 0):
		aIdent = INDENT * iLevel

		# Collect values
		aName = iFunc.get('name')
		aReturnType = iFunc.get('type')
		aAttributes = ''
		aAttributesDict = iFunc.get('attributes')
		for a in aAttributesDict:
			if aAttributesDict[a]:
				if len(aAttributes):
					aAttributes += ', '
				aAttributes += a
		aArguments = ''
		aArgumentsDict = iFunc.get('arguments')
		for a in aArgumentsDict:
			if len(aArguments):
				aArguments += ', '
			
			aArgName = a.get('name')
			aArgType = a.get('type')
			aArgOptional = True
			aArgAttributesDict = a.get('attributes')
			if (aArgAttributesDict is not None) and (aArgAttributesDict.get('mandatory', False)):
				aArgOptional = False
			if aArgOptional:
				aArguments += '({} {})'.format(aArgType, aArgName)
			else:
				aArguments += '{} {}'.format(aArgType, aArgName)

		# Rendering
		self._file.write(aIdent + '- {} {}({})\n'.format(aReturnType, aName, aArguments))
		aIdent = INDENT * (iLevel + 2)
		if len(aAttributes):
			self._file.write(aIdent + 'Attributes: {}\n'.format(aAttributes))


	### Generate parameters
	def genInstances(self, iObject, iLevel = 0):
		o = iObject.get('instances')
		if (o is not None) and len(o):
			aIdent = INDENT * iLevel
			self._file.write(aIdent + ' == INSTANCES:\n')
			for i in o:
				self.genObject(i, True, iLevel + 1)


	### Generate child objects
	def genChildren(self, iObject, iLevel = 0):
		o = iObject.get('children')
		if (o is not None) and len(o):
			for i in o:
				self.genObject(i, False, iLevel)


	### Test GET request on some characters
#	def doTest(self):
#		self.genModuleJsonFile('.', 'DOT')
#		self.genModuleJsonFile('*', 'STAR')
#		self.genModuleJsonFile('!', 'EXCLAM')
#		self.genModuleJsonFile('#', 'HASH')
#		self.genModuleJsonFile('`', 'QUOTE')
#		self.genModuleJsonFile('+', 'PLUS')
#		self.genModuleJsonFile('@', 'AT')
#		self.genModuleJsonFile('?', 'QUESTION')
#		self.genModuleJsonFile('/', 'SLASH')
#		self.genModuleJsonFile('-', 'MINUS')
#		self.genModuleJsonFile('~', 'TILDA')
#		self.genModuleJsonFile('$', 'DOLLAR')
#		self.genModuleJsonFile('%', 'PERCENT')
#		self.genModuleJsonFile('^', 'HAT')
#		self.genModuleJsonFile('&', 'AND')
#		self.genModuleJsonFile('(', 'LEFTPAR')
#		self.genModuleJsonFile(')', 'RIGHTPAR')
#		self.genModuleJsonFile('_', 'UNDERSCORE')
#		self.genModuleJsonFile('=', 'EGUAL')
#		self.genModuleJsonFile(',', 'COMMA')
#		self.genModuleJsonFile(':', 'COLONN')
#		self.genModuleJsonFile(';', 'SEMICOLONN')
