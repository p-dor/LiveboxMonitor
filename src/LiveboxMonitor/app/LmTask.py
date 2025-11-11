### Livebox Monitor task ###

from PyQt6 import QtCore

from LiveboxMonitor.app import LmTools
from LiveboxMonitor.util import LmUtils


# ################################ LmTask class ################################
class LmTask:
    def __init__(self, app):
        self._app = app
        self._index = 0
        self._stack = []


    ### Start a task - they can be nested. Set only mouse cursor if task is None.
    def start(self, task=None):
        self._index += 1
        self._stack.append(task)
        LmTools.mouse_cursor_busy() # Stack cursor change
        self.display(task)
        LmUtils.log_debug(1, f"TASK STARTING stack={self._index} task={task}")


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
            self.display(f"{task} {status}." if task else f"{status}.")
            LmUtils.log_debug(1, f"TASK UPDATE stack={self._index} - task={task} - status={status}")


    ### End a (nested) task
    def end(self):
        if self._index:
            self._index -= 1
            self._stack.pop()
            LmTools.mouse_cursor_normal()   # Unstack cursor change

            if self._index:
                task = self._stack[self._index - 1]
                self.display(task)
            else:
                task = "<None>"
                self.display(None)

            LmUtils.log_debug(1, f"TASK ENDING stack={self._index} - restoring={task}")


    ### Display task / erase status is None
    def display(self, task):
        if task:
            if self._app._status_bar is None:
                self._app.setWindowTitle(f"{self._app.app_window_title()} - {task}")
            else:
                self._app._status_bar.showMessage(task)
                QtCore.QCoreApplication.sendPostedEvents()
                QtCore.QCoreApplication.processEvents()
        else:
            if self._app._status_bar is None:
                self._app.setWindowTitle(self._app.app_window_title())
            else:
                self._app._status_bar.clearMessage()
                QtCore.QCoreApplication.processEvents()
