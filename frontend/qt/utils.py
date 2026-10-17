from PySide6 import QtCore
from PySide6.QtWidgets import QApplication


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
