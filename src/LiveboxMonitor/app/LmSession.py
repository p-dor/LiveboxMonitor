### Livebox Monitor session module ###
# Interfaces copied/adapted from sysbus package - https://github.com/rene-d/sysbus

import os
import sys
import json
import tempfile
import pickle
import datetime
import requests
import requests.utils

from LiveboxMonitor.app import LmTools


# ################################ VARS & DEFS ################################
APP_NAME = 'so_sdkut'
DEFAULT_TIMEOUT = 5
LIVEBOX_SCAN_TIMEOUT = 0.6
URL_REDIRECTIONS = {}



# ################################ LmSession class ################################

class LmSession:
	### Setup
	TimeoutMargin = 0

	### Constructor
	def __init__(self, iUrl, iSessionName = 'LiveboxMonitor'):
		iUrl = iUrl.rstrip(' /') + '/'
	
		# URL redirection handling
		if iUrl in URL_REDIRECTIONS:
			self._url = URL_REDIRECTIONS[iUrl]
			print(f"Redirecting '{iUrl}' to '{self._url}'.")
		else:
			self._url = iUrl

		self._verify = self._url.startswith('http://')
		self._user = ''
		self._password = ''
		self._name = iSessionName
		self._session = None
		self._channelID = 0
		self._sahServiceHeaders = None
		self._sahEventHeaders = None


	### Read a url redirection list and store it in the global dict URL_REDIRECTIONS
	### this fails silently
	@staticmethod
	def loadUrlRedirections(iRedirections):
		def fixTrailingSlash(iUrl):
			return iUrl.rstrip(' /') + '/'

		global URL_REDIRECTIONS
		if not iRedirections:
			return

		try:
			for i in iRedirections:
				aUrlFrom, aUrlTo = i.split('=', 1)
				aUrlFrom = fixTrailingSlash(aUrlFrom)
				aUrlTo = fixTrailingSlash(aUrlTo)
				if aUrlFrom in URL_REDIRECTIONS:
					raise Exception('Source redirection URL already declared.')
				URL_REDIRECTIONS[aUrlFrom] = aUrlTo
				LmTools.LogDebug(1, 'Added redirection', aUrlFrom, 'to', aUrlTo)
		except BaseException as e:
			LmTools.Error('Error while processing redirections: {}'.format(e))


	### Setup timeout margin
	@staticmethod
	def setTimeoutMargin(iTimeout):
		LmSession.TimeoutMargin = iTimeout


	### Sign in - return -1 in case of connectivity issue, 0 if sign failed, 1 if sign successful
	def signin(self, iUser, iPassword, iNewSession = False):
		# Set cookie & contextID file path
		aStateFilePath = os.path.join(tempfile.gettempdir(), self._name + '_state')

		LmTools.LogDebug(1, 'State file', aStateFilePath)

		# Close current session if any
		self.close()

		# Save current user/password
		self._user = iUser
		self._password = iPassword

		for i in range(2):
			if not iNewSession and os.path.exists(aStateFilePath):
				LmTools.LogDebug(1, 'Loading saved cookies')

				with open(aStateFilePath, 'rb') as f:
					aCookies = requests.utils.cookiejar_from_dict(pickle.load(f))
					self._session = requests.Session()
					self._channelID = 0
					self._session.cookies = aCookies
					aContextID = pickle.load(f)
			else:
				LmTools.LogDebug(1, 'New session')
				self._session = requests.Session()
				self._channelID = 0

				LmTools.LogDebug(1, 'Authentication')
	 
				aAuth = '{"service":"sah.Device.Information","method":"createContext","parameters":{"applicationName":"%s","username":"%s","password":"%s"}}' % (APP_NAME, iUser, iPassword)

				self._sahServiceHeaders = { 'Accept':'*/*',
											'Authorization':'X-Sah-Login',
											'Content-Type':'application/x-sah-ws-4-call+json' }

				LmTools.LogDebug(2, 'Auth with', str(aAuth))
				try:
					r = self._session.post(self._url + 'ws',
										   data = aAuth,
										   headers = self._sahServiceHeaders,
										   timeout = DEFAULT_TIMEOUT + LmSession.TimeoutMargin,
										   verify = self._verify)
				except BaseException as e:
					LmTools.Error(str(e))
					self._session = None
					return -1
				LmTools.LogDebug(2, 'Auth return', r.text)

				if not 'contextID' in r.json()['data']:
					LmTools.Error('Auth error', str(r.text))
					break

				aContextID = r.json()['data']['contextID']

				# Saving cookie & contextID
				LmTools.LogDebug(1, 'Setting cookies')
				with open(aStateFilePath, 'wb') as f:
					aData = requests.utils.dict_from_cookiejar(self._session.cookies)
					pickle.dump(aData, f, pickle.HIGHEST_PROTOCOL)
					aData = aContextID
					pickle.dump(aData, f, pickle.HIGHEST_PROTOCOL)

			self._sahServiceHeaders = { 'Accept':'*/*',
										'Authorization':'X-Sah ' + aContextID,
										'Content-Type':'application/x-sah-ws-4-call+json; charset=UTF-8',
										'X-Context':aContextID }

			self._sahEventHeaders = { 'Accept':'*/*',
									  'Authorization':'X-Sah ' + aContextID,
									  'Content-Type':'application/x-sah-event-4-call+json; charset=UTF-8',
									  'X-Context':aContextID }

			# Check authentication
			try:
				r = self._session.post(self._url + 'ws',
									   data = '{"service":"Time", "method":"getTime", "parameters":{}}',
									   headers = self._sahServiceHeaders,
									   timeout = DEFAULT_TIMEOUT + LmSession.TimeoutMargin,
									   verify = self._verify)
			except BaseException as e:
				LmTools.Error(str(e))
				LmTools.Error('Authentification check query failed.')
				os.remove(aStateFilePath)
				self.close()
				return -1

			if r.json()['status'] == True:
				return 1
			else:
				os.remove(aStateFilePath)

		LmTools.Error('Authentification failed.')
		return 0


	### Close session
	def close(self):
		if self._session is not None:
			# Fails with access denied error (but same behavior from the web interface...)
			self.request('sah.Device.Information:releaseContext', { 'applicationName': APP_NAME })
			self._session = None
			self._channelID = 0
			self._sahServiceHeaders = None
			self._sahEventHeaders = None


	### Send service request
	def request(self, iPackage, iMethod = None, iArgs = None, iGet = False, iSilent = False, iTimeout = DEFAULT_TIMEOUT):
		# Check session is established
		if self._session is None:
			if self.signin(self._user, self._password) <= 0:
				return { 'errors' : 'No session' }

		if iGet:
			# Build request path
			c = 'sysbus/' + iPackage.replace('.', '/')
			if iMethod is not None:
				c += ':' + iMethod

			if iArgs is None:
				c += '?_restDepth=-1'
			else:
				c += '?_restDepth=' + str(iArgs)

			LmTools.LogDebug(2, 'Request: %s' % (c))
			aTimeStamp = datetime.datetime.now()
			try:
				t = self._session.get(self._url + c,
									  headers = self._sahServiceHeaders,
									  timeout = iTimeout + LmSession.TimeoutMargin,
									  verify = self._verify)
				LmTools.LogDebug(2, 'Request duration: %s' % (datetime.datetime.now() - aTimeStamp))
				t = t.content
			except requests.exceptions.Timeout as e:
				if not iSilent:
					LmTools.Error('Request timeout error: {}'.format(e))
				return None
			except BaseException as e:
				if not iSilent:
					LmTools.Error('Request error: {}'.format(e))
				return { 'errors' : 'Request exception' }

			t = t.decode('utf-8', errors = 'replace')
			t = t.replace('[,]', '[]')	# Some lists, like in GET '*' request, contain a failing comma
			if t.startswith(',"errors":'):
				t = '{' + t[1:] + '}'
			elif t.find('}{') > 0:
				LmTools.LogDebug(2, 'Multiple json lists')
				t = '[' + t.replace('}{', '},{') + ']'
		else:
			# Setup request parameters
			aData = {}
			aData['service'] = 'sysbus.' + iPackage

			if iMethod is not None:
				aData['method'] = iMethod

			if iArgs is not None:
				aData['parameters'] = iArgs
			else:
				aData['parameters'] = {}

			# Send request & headers
			LmTools.LogDebug(2, 'Request: %s' % (str(aData)))
			aTimeStamp = datetime.datetime.now()
			try:
				t = self._session.post(self._url + 'ws',
									   data = json.dumps(aData),
									   headers = self._sahServiceHeaders,
									   timeout = iTimeout + LmSession.TimeoutMargin,
									   verify = self._verify)
				LmTools.LogDebug(2, 'Request duration: %s' % (datetime.datetime.now() - aTimeStamp))
				t = t.content
			except requests.exceptions.Timeout as e:
				if not iSilent:
					LmTools.Error('Request timeout error: {}'.format(e))
				return None
			except BaseException as e:
				if not iSilent:
					LmTools.Error('Request error: {}'.format(e))
				return { 'errors' : 'Request exception' }

			t = t.decode('utf-8', errors = 'replace')

		try:
			r = json.loads(t)
		except:
			if not iSilent:
				LmTools.Error(sys.exc_info()[0])
				LmTools.Error('Bad json:', t)
			return None

		aOverview = str(r)
		if len(aOverview) > 128:
			aOverview = aOverview[:128] + '...'
		LmTools.LogDebug(2, 'Reply:', aOverview)

		if not iGet and 'result' in r:
			r = r['result']
			if 'errors' in r:
				if not iSilent:
					LmTools.Error(t)
				return None

		LmTools.LogDebug(2, '-------------------------')
		return r


	### Send event request
	def eventRequest(self, iEvents, iSilent = False, iTimeout = DEFAULT_TIMEOUT):
		# Check session is established
		if self._session is None:
			if self.signin(self._user, self._password) <= 0:
				return { 'errors' : 'No session' }

		aData = {}

		aData['events'] = iEvents
		if self._channelID:
			aData['channelid'] = str(self._channelID)

		# Send request & headers
		LmTools.LogDebug(2, 'Event Request: %s' % (str(aData)))
		aTimeStamp = datetime.datetime.now()
		try:
			t = self._session.post(self._url + 'ws',
								   data = json.dumps(aData),
								   headers = self._sahEventHeaders,
								   timeout = iTimeout,
								   verify = self._verify)
			LmTools.LogDebug(2, 'Request duration: %s' % (datetime.datetime.now() - aTimeStamp))
			t = t.content
		except requests.exceptions.Timeout as e:
			if not iSilent:
				LmTools.LogDebug(2, 'Event request timeout error: {}'.format(e))
			return None
		except BaseException as e:
			if not iSilent:
				LmTools.Error('Event request error: {}'.format(e))
			return { 'errors' : 'Event request exception' }

		t = t.decode('utf-8', errors = 'replace')

		# Remove tailing null if present
		if t.endswith('null'):
			t = t[:-4]

		try:
			r = json.loads(t)
		except:
			if not iSilent:
				LmTools.Error(sys.exc_info()[0])
				LmTools.Error('Bad json:', t)
			return None

		aOverview = str(r)
		if len(aOverview) > 50:
			aOverview = aOverview[:50] + '...'
		LmTools.LogDebug(2, 'Reply:', aOverview)

		if 'result' in r:
			r = r['result']
			if 'errors' in r:
				if not iSilent:
					LmTools.Error(t)
				return None

		LmTools.LogDebug(2, '-------------------------')
		self._channelID = r.get('channelid', 0)
		return r


	# It is possible to query DeviceInfo service without being logged, e.g. to get MAC address
	@staticmethod
	def getLiveboxMAC(iLiveboxURL):
		if iLiveboxURL is not None:
			try:
				r = requests.Session().post(iLiveboxURL  + 'ws',
						   data = '{"service":"sysbus.DeviceInfo", "method":"get", "parameters":{}}',
						   headers = {'Accept':'*/*', 'Content-Type':'application/x-sah-ws-4-call+json'},
						   timeout = LIVEBOX_SCAN_TIMEOUT + LmSession.TimeoutMargin)
			except:
				r = None
			if r is not None:
				s = r.json().get('status')
				if s is not None:
					s = s.get('BaseMAC')
					if s is not None:
						return s.upper()

		return None
