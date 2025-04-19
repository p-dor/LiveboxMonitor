### Livebox Monitor APIs base class ###

from LiveboxMonitor.app import LmTools


# ################################ Livebox Monitor APIs ################################
class LmApi:
	def __init__(self, iSession):
		self._session = iSession


	### Call a Livebox API - raise exception or return status value
	def call(self, iPackage, iMethod = None, iArgs = None, iTimeout = None, iErrStr = None, iFullReply = False):
		# Compute error string
		aErrStr = iPackage
		if iMethod is not None:
			aErrStr += ':' + iMethod
		if iErrStr is not None:
			aErrStr += ' ' + iErrStr

		# Call Livebox API
		try:
			if iTimeout is None:
				d = self._session.request(iPackage, iMethod, iArgs)
			else:
				d = self._session.request(iPackage, iMethod, iArgs, iTimeout = iTimeout)
		except BaseException as e:
			raise Exception('{}: {}.'.format(aErrStr, e))
		if (d is not None) and ('status' in d):
			e = LmTools.GetErrorsFromLiveboxReply(d)
			if e:
				raise Exception('{}: {}'.format(aErrStr, e))
			if iFullReply:
				return d
			else:
				return d.get('status')
		else:
			raise Exception(aErrStr + ' service error.')
