from qt.core import QObject, Property, Signal, Slot, QThreadPool, QRunnable
from qt.gui import QImage


MAX_THREAD_COUNT = 3


class TextColorDetector(QObject):
    imageChanged = Signal()
    rectsChanged = Signal()
    colorsChanged = Signal()

    _pool = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self._image = None
        self._rects = []
        self._colors = []

    @classmethod
    def pool(cls):
        if cls._pool is None:
            cls._pool = QThreadPool()
            cls._pool.setMaxThreadCount(MAX_THREAD_COUNT)
        return cls._pool

    def getImage(self):
        return self._image

    def setImage(self, image: QImage):
        self._image = image

    image = Property(QImage, getImage, setImage, notify=imageChanged)

    def getRects(self):
        return self._rects

    def setRects(self, rects: list):
        self._rects = rects

    rects = Property('QVariantList', getRects, setRects, notify=rectsChanged)

    def getColors(self):
        return self._colors

    colors = Property('QVariantList', getColors, notify=colorsChanged)

    @Slot()
    def update(self):
        task = _Task(self._image, self._rects)
        pool = self.pool()
        pool.start(task)


class _Signals(QObject):
    done = Signal(list)


class _Task(QRunnable):

    def __init__(self, image: QImage, rects: list):
        super().__init__()
        self._image = image
        self._rects = rects
        self._signals = _Signals()

    def run(self):
        colors = ['#FFFFFF' for _ in range(len(self._rects))]
        self._signals.done.emit(colors)
