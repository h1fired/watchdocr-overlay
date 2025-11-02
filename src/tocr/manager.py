from enum import IntEnum
from src.ocr.ocr import OCR
from src.grabber import window as grabber
from common.task import TaskManager
from common.observable import TypedObservable


class TOcrMode(IntEnum):
    SINGLE = 0


class TOcrStatus(IntEnum):
    ERROR = 0
    SUCCESS = 1
    RECOGNIZING = 2


class TOcrWorker:
    obs_data = TypedObservable(dict)

    def __init__(self, ocr: OCR):
        self._ocr = ocr
        self._box = (0, 0, 0, 0)
        self._is_busy = False

    def process_area(self, box: tuple[int, int, int, int]):
        raise NotImplementedError

    def is_busy(self):
        return self._is_busy


class TOcrWorkerManager:
    obs_data = TypedObservable(TOcrMode, dict)

    def __init__(self, workers: dict[TOcrMode, TOcrWorker]):
        self._workers = workers
        for mode, worker in workers.items():
            worker.obs_data.register(lambda d: self.obs_data.notify(mode, d))

    def get(self, mode: TOcrMode):
        return self._workers[mode]

    def is_busy(self):
        return any(w.is_busy() for w in self._workers.values())


class TOcrSingleWorker(TOcrWorker):
    def __init__(self, ocr: OCR):
        super().__init__(ocr)
        self._task_id = 'task.tocrworker.single'

    def process_area(self, box: tuple[int, int, int, int]):
        self._box = box
        future = TaskManager.execute(self.worker, id=self._task_id)
        future.observe(on_result=self.obs_data.notify)

    def worker(self, token):
        self._is_busy = True
        image = grabber.grab_window_area(self._box)
        output = self._ocr.recognize(image)
        self._is_busy = False
        return output


class TOcr:
    obs_output = TypedObservable(TOcrMode, dict)

    def __init__(self, ocr: OCR):
        self._ocr = ocr
        self._mode = TOcrMode.SINGLE
        self._workers = TOcrWorkerManager(
            workers={
                TOcrMode.SINGLE: TOcrSingleWorker(ocr)
            }
        )
        self._workers.obs_data.register(self.on_worker_data)

    def change_mode(self, mode: TOcrMode):
        self._mode = mode

    def process_area(self, box: tuple[int, int, int, int]):
        if self._workers.is_busy():
            raise RuntimeError('Some worker already in process')

        current_worker = self._workers.get(self._mode)
        current_worker.process_area(box)
        self.obs_output.notify(
            self._mode,
            {'status': TOcrStatus.RECOGNIZING, 'text': 'Recognizing...'}
        )

    def on_worker_data(self, mode: TOcrMode, output):
        status = TOcrStatus(output['status'].value)
        text = output['text']
        self.obs_output.notify(mode, {'status': status, 'text': text})
