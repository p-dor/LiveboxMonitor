### Livebox Monitor APIs base class ###


# ################################ Livebox Monitor APIs ################################
class LmApi:
	def __init__(self, iApi, iSession):
		self._api = iApi			# ApiRegistry instance
		self._session = iSession	# LmSession instance


	### Compute error string
	def errStr(self, iPackage, iMethod = None, iErrStr = None):
		e = iPackage
		if iMethod is not None:
			e += ':' + iMethod
		if iErrStr is not None:
			e += ' ' + iErrStr
		return e


	### Compute error description from Livebox reply
	@staticmethod
	def getErrorStr(iDesc, iInfo, iID = None):
		d = ''
		if iID:
			d = '[' + str(iID) + ']'
		if iDesc:
			if d:
				d += ' '
			d += iDesc
		if iInfo:
			if d:
				d += ' '
			if iDesc:
				d += '-> ' + iInfo
			else:
				d += iInfo
		if d:
			d += '.\n'
		return d


	### Collect potential error description(s) from Livebox reply
	@staticmethod
	def getErrors(iReply):
		d = ''
		if iReply is not None:
			aErrors = iReply.get('errors')
			if (aErrors is not None) and (type(aErrors).__name__ == 'list'):
				for e in aErrors:
					aDesc = e.get('description')
					aInfo = e.get('info')
					d += LmApi.getErrorStr(aDesc, aInfo)
			else:
				e = iReply.get('error')
				if e is not None:
					aDesc = iReply.get('description')
					aInfo = iReply.get('info')
					d += LmApi.getErrorStr(aDesc, aInfo, e)
		return d


	### Call a Livebox API - raise exception or return the full reply, cannot be None and contains 'status'
	def callRaw(self, iPackage, iMethod = None, iArgs = None, iTimeout = None, iErrStr = None):
		# Call Livebox API
		try:
			if iTimeout is None:
				d = self._session.request(iPackage, iMethod, iArgs)
			else:
				d = self._session.request(iPackage, iMethod, iArgs, iTimeout = iTimeout)
		except BaseException as e:
			raise Exception('{}: {}.'.format(self.errStr(iPackage, iMethod, iErrStr), e))
		if d is not None:
			e = LmApi.getErrors(d)
			if e:
				raise Exception('{}: {}'.format(self.errStr(iPackage, iMethod, iErrStr), e))
			if 'status' in d:
				return d

		raise Exception(self.errStr(iPackage, iMethod, iErrStr) + ' service error.')


	### Call a Livebox API - raise exception or return 'status' value, can be None
	def callNoCheck(self, iPackage, iMethod = None, iArgs = None, iTimeout = None, iErrStr = None):
		return self.callRaw(iPackage, iMethod, iArgs, iTimeout, iErrStr).get('status')


	### Call a Livebox API - raise exception or return 'status' value if not '', 0, False or None
	def call(self, iPackage, iMethod = None, iArgs = None, iTimeout = None, iErrStr = None):
		d = self.callNoCheck(iPackage, iMethod, iArgs, iTimeout, iErrStr)
		if not d:
			raise Exception(self.errStr(iPackage, iMethod, iErrStr) + ' service failed.')
		return d
