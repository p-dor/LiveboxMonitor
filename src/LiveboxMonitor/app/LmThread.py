### Livebox Monitor thread ###

from PyQt6 import QtCore


# ################################ LmThread class ################################
class LmThread(QtCore.QObject):
    def __init__(self, api, frequency=0):
        super(LmThread, self).__init__()
        self._api = api
        self._session = api._session
        self._frequency = frequency
        self._timer = None
        self._loop = None
        self._is_running = False
        self._thread = QtCore.QThread()
        self.moveToThread(self._thread)
        self._thread.started.connect(self.run)
        self._resume.connect(self.resume)
        self._thread.start()


    def run(self):
        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self.task)
        self._loop = QtCore.QEventLoop()
        self.resume()


    def resume(self):
        if not self._is_running:
            self._timer.start(self._frequency)
            self._is_running = True
            self._loop.exec()
            self._timer.stop()
            self._is_running = False


    def stop(self):
        if self._is_running:
            self._loop.exit()


    def quit(self):
        self._thread.quit()
        self._thread.wait()
        self._thread = None
