### Livebox Monitor task ###

from PyQt6 import QtCore

from LiveboxMonitor.app import LmTools


# ################################ LmTask class ################################
class LmTask:
    def __init__(self, app):
        self._app = app
        self._index = 0
        self._stack = []


    ### Show the start of a long task - they can be nested
    def start(self, task):
        self._index += 1
        self._stack.append(task)
        LmTools.mouse_cursor_busy() # Stack cursor change

        if self._app._statusBar is None:
            self._app.setWindowTitle(self._app.appWindowTitle() + ' - ' + task)
        else:
            self._app._statusBar.showMessage(task)
            QtCore.QCoreApplication.sendPostedEvents()
            QtCore.QCoreApplication.processEvents()

        LmTools.log_debug(1, f'TASK STARTING stack={self._index} task={task}')


    ### Suspend a potential running task
    def suspend(self):
        if self._index:
            LmTools.mouse_cursor_force_normal()


    ### Resume a potential running task
    def resume(self):
        if self._index:
            LmTools.mouse_cursor_force_busy()


    ### Update a task by adding a status
    def update(self, status):
        if self._index:
            task = self._stack[self._index - 1]
            if self._app._statusBar is None:
                self._app.setWindowTitle(self._app.appWindowTitle() + ' - ' + task + ' ' + status + '.')
            else:
                self._app._statusBar.showMessage(task + ' ' + status + '.')
                QtCore.QCoreApplication.sendPostedEvents()
                QtCore.QCoreApplication.processEvents()

            LmTools.log_debug(1, f'TASK UPDATE stack={self._index} - task={task} - status={status}')


    ### End a long (nested) task
    def end(self):
        if self._index:
            self._index -= 1
            self._stack.pop()
            LmTools.mouse_cursor_normal()   # Unstack cursor change

            if self._index:
                task = self._stack[self._index - 1]
                if self._app._statusBar is None:
                    self._app.setWindowTitle(self._app.appWindowTitle() + ' - ' + task)
                else:
                    self._app._statusBar.showMessage(task)
                    QtCore.QCoreApplication.sendPostedEvents()
                    QtCore.QCoreApplication.processEvents()
            else:
                task = '<None>'
                if self._app._statusBar is None:
                    self._app.setWindowTitle(self._app.appWindowTitle())
                else:
                    self._app._statusBar.clearMessage()
                    QtCore.QCoreApplication.processEvents()

            LmTools.log_debug(1, f'TASK ENDING stack={self._index} - restoring={task}')
