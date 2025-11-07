from common.observable import TypedObservable
from common.task import TaskManager, Period
from src.ocr.backends import OcrBackendManager, OcrStatus as _BOcrStatus, NO_IMAGE_RESIZE
# from src.ocr.backends.gemini import GeminiOcrBackend
from src.ocr.backends.tesseract import TesseractOcrBackend
from src.ocr.filtering import OCRImageFilter, OCRImageOptimizer
from src.grabber.window import ScreenGrabber
from config import config
from enum import IntEnum
from PIL import Image


backends = [
    # GeminiOcrBackend,
    TesseractOcrBackend
]


class OcrCore:
    def __init__(self):
        self._backends = OcrBackendManager(backends)

    def recognize(self, image: Image.Image):
        original_size = image.size
        if NO_IMAGE_RESIZE not in config.MAX_IMAGE_RESOLUTION:
            OCRImageOptimizer.optimize_size(image, config.MAX_IMAGE_RESOLUTION)
        scaler = original_size[0] / image.width
        adjusted_image = OCRImageFilter.adjust(image)
        backend = self._backends.current()
        response = backend.recognize(adjusted_image, scaler)

        return response

    def backends(self):
        return self._backends


class OcrMode(IntEnum):
    SINGLE = 0
    STREAM = 1


class OcrStatus(IntEnum):
    ERROR = 0
    SUCCESS = 1
    RECOGNIZING = 2


class OcrWorker:
    def __init__(self, core: OcrCore, grabber):
        self._core = core
        self._grabber = grabber
        self._box = (0, 0, 0, 0)
        self._is_busy = False
        self.obs_data = TypedObservable(dict)

    def process_area(self, box: tuple[int, int, int, int]):
        raise NotImplementedError

    def terminate(self):
        raise NotImplementedError

    def is_busy(self):
        return self._is_busy


class OcrWorkerManager:
    obs_data = TypedObservable(dict)

    def __init__(self, workers: dict[OcrMode, OcrWorker]):
        self._workers = workers
        for mode, worker in workers.items():
            worker.obs_data.register(lambda d: self.on_data(mode, d))

    def get(self, mode: OcrMode):
        return self._workers[mode]

    def is_busy(self):
        return any(w.is_busy() for w in self._workers.values())

    def on_data(self, mode: OcrMode, data: dict):
        data['mode'] = mode
        self.obs_data.notify(data)


class OcrSingleWorker(OcrWorker):
    def __init__(self, core, grabber):
        super().__init__(core, grabber)
        self._task_id = 'task.tocrworker.single'

    def process_area(self, box: tuple[int, int, int, int]):
        self._box = box
        future = TaskManager.execute(self.worker, id=self._task_id)
        future.observe(on_result=self.obs_data.notify)

    def terminate(self):
        if TaskManager.objects().exists(self._task_id):
            task = TaskManager.objects().get(self._task_id)
            task.cancel()
            task.wait()

    def worker(self, token):
        self._is_busy = True
        image = self._grabber.grab_screen_area(self._box)
        output = self._core.recognize(image)
        self._is_busy = False
        return output


class OcrStreamWorker(OcrWorker):
    def __init__(self, core, grabber):
        super().__init__(core, grabber)
        self._task_id = 'task.tocrworker.stream'

    def process_area(self, box: tuple[int, int, int, int]):
        self._box = box
        future = TaskManager.execute(
            task=self.worker,
            period=Period(1),
            id=self._task_id
        )
        future.observe(on_result=self.obs_data.notify)

    def terminate(self):
        if TaskManager.objects().exists(self._task_id):
            task = TaskManager.objects().get(self._task_id)
            task.cancel()
            task.wait()

    def worker(self, token):
        while True:
            self._is_busy = True
            image = self._grabber.grab_screen_area(self._box)
            output = self._core.recognize(image)
            self._is_busy = False
            return output


class Ocr:
    def __init__(self):
        self._core = OcrCore()
        self._mode = OcrMode.SINGLE
        self._workers = OcrWorkerManager({
            OcrMode.SINGLE: OcrSingleWorker(self._core, ScreenGrabber),
            OcrMode.STREAM: OcrStreamWorker(self._core, ScreenGrabber)
        })

    def change_mode(self, mode: OcrMode):
        if self._workers.is_busy():
            raise RuntimeError('OCR should be terminated')
        self._mode = mode

    def process_area(self, box: tuple[int, int, int, int]):
        if self._workers.is_busy():
            raise RuntimeError('Some OCR worker already in process')
        current = self._workers.get(self._mode)
        current.process_area(box)

    def terminate(self):
        current_worker = self._workers.get(self._mode)
        current_worker.terminate()

    def observable(self):
        return self._workers.obs_data

    def backends(self):
        return self._core.backends()

    def modes(self):
        return tuple(OcrMode)

    def current_mode(self):
        return self._mode


def mode_to_str(mode: OcrMode):
    match mode:
        case OcrMode.SINGLE:
            return 'single'
        case OcrMode.STREAM:
            return 'stream'
    raise ValueError('Mode does not exists')


def str_to_mode(mode: str):
    match mode:
        case 'single':
            return OcrMode.SINGLE
        case 'stream':
            return OcrMode.STREAM
    raise ValueError('Mode does not exists')
