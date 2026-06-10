from PySide6.QtCore import QRectF, Property, Signal
from PySide6.QtGui import QPainter, QImage
from PySide6.QtQuick import QQuickPaintedItem, QQuickImageProvider
from PySide6.QtSvg import QSvgRenderer
from PIL import ImageQt, Image


class AnimatedImage(QQuickPaintedItem):
    sourceChanged = Signal()
    runningChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._source = None
        self.renderer = QSvgRenderer()
        self.renderer.repaintNeeded.connect(self.update)

    def paint(self, painter: QPainter):
        if self.renderer.isValid():
            self.renderer.render(painter, QRectF(0, 0, self.width(), self.height()))

    def getSource(self):
        return self._source

    def setSource(self, source: str):
        if source.startswith('qrc'):
            self.renderer.load(source[3:])
        else:
            self.renderer.load(source)

        if self.renderer.isValid():
            self._source = source

    source = Property(str, getSource, setSource, notify=sourceChanged)

    def getRunning(self):
        return self.renderer.isAnimationEnabled()

    def setRunning(self, value: bool):
        self.renderer.setAnimationEnabled(value)

    running = Property(bool, getRunning, setRunning, notify=runningChanged)


class ImageProvider(QQuickImageProvider):
    def __init__(self):
        super().__init__(QQuickImageProvider.Image)
        self._image = None

    def setImage(self, image: Image.Image):
        self._image = ImageQt.ImageQt(image.convert('RGBA'))

    def requestImage(self, id, size, requestedSize):
        if self._image is None:
            return QImage()
        return self._image
