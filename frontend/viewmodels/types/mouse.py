from qt.core import QObject, Property, Signal, QPoint, QApplication, QEvent


class MouseTracker(QObject):
    positionChanged = Signal()
    enabledChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pos = QPoint(0, 0)
        self._enabled = False

    def getPosition(self):
        return self._pos

    position = Property(QPoint, getPosition, notify=positionChanged)

    def eventFilter(self, _, event):
        if event.type() == QEvent.MouseMove:
            self._pos = event.globalPosition().toPoint()
            self.positionChanged.emit()
        return False

    def getEnabled(self):
        return self._enabled

    def setEnabled(self, value: bool):
        if value:
            QApplication.instance().installEventFilter(self)
        else:
            QApplication.instance().removeEventFilter(self)
        self._enabled = value

    enabled = Property(bool, getEnabled, setEnabled, notify=enabledChanged)
