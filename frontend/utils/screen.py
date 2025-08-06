from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QObject, Property, Signal


class ScreenManager(QObject):
    primaryScreenChanged = Signal()
    screensChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        QGuiApplication.instance().primaryScreenChanged.connect(self.primaryScreenChanged)
        QGuiApplication.instance().screenAdded.connect(self.screensChanged)
        QGuiApplication.instance().screenRemoved.connect(self.screensChanged)

    def getPrimaryScreen(self):
        return QGuiApplication.primaryScreen()

    primary = Property(QObject, getPrimaryScreen, notify=primaryScreenChanged)

    def getScreens(self):
        return QGuiApplication.screens()

    screens = Property(list, getScreens, notify=screensChanged)
