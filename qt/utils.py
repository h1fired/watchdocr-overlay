from PySide6 import QtCore
from PySide6.QtWidgets import QApplication
import ctypes


def isTouchSupported():
    touch_input = ctypes.windll.user32.GetSystemMetrics(95)
    return touch_input > 0


def invokeMethod(func):
    def wrapper(self, *args, **kwargs):
        def post():
            func(self, *args, **kwargs)

        if not QApplication.instance():
            raise RuntimeError('QApplication instance is not initialized')

        QApplication.instance().postTask(post)
    return wrapper


def invokeFunc(func):
    def wrapper(*args, **kwargs):
        def post():
            func(*args, **kwargs)

        if not QApplication.instance():
            raise RuntimeError('QApplication instance is not initialized')

        QApplication.instance().postTask(post)
    return wrapper


class DeferredTimer(QtCore.QObject):
    timeout = QtCore.Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._timer = QtCore.QTimer()
        self._timer.timeout.connect(self._onTimeout)
        self._is_executed = False

    def defer(self, msec):
        if self._timer.isActive():
            self._timer.stop()

        self._is_executed = False
        self._timer.start(msec)

    def stop(self):
        self._timer.stop()

    def _onTimeout(self):
        if not self._is_executed:
            self.timeout.emit()
            self._is_executed = True
            self.stop()
