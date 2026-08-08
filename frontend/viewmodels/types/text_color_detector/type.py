from qt.core import QObject, Property, Signal, QThreadPool, QRunnable
from qt.gui import QImage
from .detector import detect_text_colors


MAX_THREAD_COUNT = 3


class TextColorDetector(QObject):
    imageProviderChanged = Signal()
    coordinatesChanged = Signal()
    colorsOutputChanged = Signal()

    _pool = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self._image_id = ''
        self._coords = []
        self._colors = []
        self._active_tasks = []

        self._image_provider = None
        self._image_changed = False
        self._coordinates_changed = False

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

    def getCoordinates(self):
        return self._coords

    def setCoordinates(self, coordinates: list):
        coordinates = [b['coordinates'] for b in coordinates]
        self._coords = coordinates
        self._coordinates_changed = True
        self.coordinatesChanged.emit()

        self.update()

    coordinates = Property('QVariantList', getCoordinates, setCoordinates, notify=coordinatesChanged)

    def getColorsOutput(self):
        return self._colors

    def setColorsOutput(self, colors: list):
        self._colors = colors
        self.colorsOutputChanged.emit()

    colorsOutput = Property('QVariantList', getColorsOutput, notify=colorsOutputChanged)

    def update(self):
        if not len(self._coords) or not self._image_id:
            self.setColorsOutput([])
            return
        elif not self._image_changed or not self._coordinates_changed:
            return

        self._image_changed = False
        self._coordinates_changed = False

        provider = self._image_provider

        if not provider:
            return

        image = provider.getImage()
        if image is None or image.isNull():
            return

        task = _Task(image, self._coords)
        task.done.connect(self._on_task_done)
        self._active_tasks.append(task)

        self.pool().start(task)

    def _on_task_done(self, task, colors):
        self._active_tasks.remove(task)
        self.setColorsOutput(colors)

    def _on_provider_image_change(self):
        self._image_changed = True
        self.update()


class _Task(QObject, QRunnable):
    done = Signal(object, list)

    def __init__(self, image: QImage, coordinates: list):
        QObject.__init__(self)
        QRunnable.__init__(self)
        self._image = image
        self._coords = coordinates

    def run(self):
        try:
            colors = detect_text_colors(self._image, self._coords)
        except Exception:
            colors = []
        self.done.emit(self, colors)
