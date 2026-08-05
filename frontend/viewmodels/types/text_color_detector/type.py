from qt.core import QObject, Property, Signal, QThreadPool, QRunnable
from qt.gui import QImage
from .detector import detect_text_colors


MAX_THREAD_COUNT = 3


class TextColorDetector(QObject):
    imageProviderChanged = Signal()
    rectsChanged = Signal()
    colorsChanged = Signal()

    _pool = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self._image_id = ''
        self._rects = []
        self._colors = []
        self._active_tasks = []

        self._image_provider = None
        self._image_changed = False
        self._rects_changed = False

    @classmethod
    def pool(cls):
        if cls._pool is None:
            cls._pool = QThreadPool()
            cls._pool.setMaxThreadCount(MAX_THREAD_COUNT)
        return cls._pool

    def getImageProvider(self):
        return self._image_id

    def setImageProvider(self, provider: str):
        self._image_id = provider

        from frontend.core import GuiCoreApplication
        engine = GuiCoreApplication().engine()
        if self._image_provider:
            self._image_provider.imageChanged.disconnect(self._on_provider_image_change)
        self._image_provider = engine.imageProvider(self._image_id)
        self._image_provider.imageChanged.connect(self._on_provider_image_change)

        self.imageProviderChanged.emit()

    image = Property(str, getImageProvider, setImageProvider, notify=imageProviderChanged)

    def getRects(self):
        return self._rects

    def setRects(self, rects: list):
        boundings = [b['boundings'] for b in rects]
        self._rects = boundings
        self._rects_changed = True
        self.rectsChanged.emit()

        self.update()

    rects = Property('QVariantList', getRects, setRects, notify=rectsChanged)

    def getColors(self):
        return self._colors

    def setColors(self, colors: list):
        self._colors = colors
        self.colorsChanged.emit()

    colors = Property('QVariantList', getColors, notify=colorsChanged)

    def update(self):
        if not len(self._rects) or not self._image_id:
            self.setColors([])
            return
        elif not self._image_changed or not self._rects_changed:
            self.setColors([])
            return

        self._image_changed = False
        self._rects_changed = False

        provider = self._image_provider

        if not provider:
            return

        image = provider.getImage()
        if image is None or image.isNull():
            return

        task = _Task(image, self._rects)
        task.done.connect(self._on_task_done)
        self._active_tasks.append(task)

        self.pool().start(task)

    def _on_task_done(self, task, colors):
        self._active_tasks.remove(task)
        self.setColors(colors)

    def _on_provider_image_change(self):
        self._image_changed = True
        self.update()


class _Task(QObject, QRunnable):
    done = Signal(object, list)

    def __init__(self, image: QImage, rects: list):
        QObject.__init__(self)
        QRunnable.__init__(self)
        self._image = image
        self._rects = rects

    def run(self):
        try:
            colors = detect_text_colors(self._image, self._rects)
        except Exception:
            colors = []
        self.done.emit(self, colors)
