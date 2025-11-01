from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QObject, Property, Signal, QRect


class ScreenManager(QObject):
    primaryScreenChanged = Signal()
    screensChanged = Signal()
    globalXChanged = Signal()
    globalYChanged = Signal()
    globalWidthChanged = Signal()
    globalHeightChanged = Signal()

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

    def getGlobalX(self):
        x = 0
        for screen in QGuiApplication.screens():
            sx = screen.geometry().x()
            if sx < x:
                x = sx
        return x

    globalX = Property(int, getGlobalX, notify=globalXChanged)

    def getGlobalY(self):
        y = 0
        for screen in QGuiApplication.screens():
            sy = screen.geometry().y()
            if sy < y:
                y = sy
        return y

    globalY = Property(int, getGlobalY, notify=globalYChanged)

    def getGlobalWidth(self):
        rect = QRect(0, 0, 0, 0)
        for screen in QGuiApplication.screens():
            rect = rect.united(screen.geometry())
        return rect.width()

    globalWidth = Property(int, getGlobalWidth, notify=globalWidthChanged)

    def getGlobalHeight(self):
        rect = QRect(0, 0, 0, 0)
        for screen in QGuiApplication.screens():
            rect = rect.united(screen.geometry())
        return rect.height()

    globalHeight = Property(int, getGlobalHeight, notify=globalHeightChanged)
