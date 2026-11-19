from qt.core import QObject, Property, Signal
from concurrent.futures import ThreadPoolExecutor
from shiboken6 import isValid
from .detector import detect_text_colors
import asyncio


MAX_THREAD_COUNT = 3


class TextColorDetector(QObject):
    imageProviderChanged = Signal()
    coordinatesChanged = Signal()
    colorsOutputChanged = Signal()

    _executor = None

    def __init__(self, parent=None):
        super().__init__(parent)
        self._image_id = ''
        self._coords = []
        self._colors = []

        self._task = None
        self._pending = None  # Latest detection request (image, coordinates)
        self._revision = 0

        self._image_provider = None
        self._image_changed = False
        self._coordinates_changed = False

    @classmethod
    def executor(cls):
        if cls._executor is None:
            cls._executor = ThreadPoolExecutor(
                max_workers=MAX_THREAD_COUNT,
                thread_name_prefix='TextColorDetector'
            )
        return cls._executor

    @classmethod
    def shutdownExecutor(cls):
        if cls._executor is not None:
            cls._executor.shutdown(wait=False, cancel_futures=True)
            cls._executor = None

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
            # Drop running and pending detections
            self._pending = None
            self._revision += 1
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

        # Only the latest request is stored, so detections are never
        # queued while previous one is running
        self._pending = (image, self._coords)
        if self._task is None or self._task.done():
            self._task = asyncio.ensure_future(self._process())

    async def _process(self):
        loop = asyncio.get_running_loop()
        while self._pending:
            image, coords = self._pending
            self._pending = None
            revision = self._revision

            try:
                colors = await loop.run_in_executor(
                    self.executor(),
                    detect_text_colors,
                    image,
                    coords
                )
            except Exception:
                colors = []

            # Object can be deleted by QML while detection is running
            if not isValid(self):
                return
            if revision == self._revision:
                self.setColorsOutput(colors)

    def _on_provider_image_change(self):
        self._image_changed = True
        self.update()
