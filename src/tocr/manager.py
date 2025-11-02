from common.task import TaskManager, Period
from common.observable import TypedObservable
from common.pipeline import ServicePipeline
from src.ocr.ocr import OCR
from src.translator.service import TranslationService
from src.grabber import window as grabber
from enum import IntEnum


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

    def terminate(self):
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

    def terminate(self):
        if TaskManager.objects().exists(self._task_id):
            task = TaskManager.objects().get(self._task_id)
            task.cancel()
            task.wait()

    def worker(self, token):
        self._is_busy = True
        image = grabber.grab_window_area(self._box)
        output = self._ocr.recognize(image)
        self._is_busy = False
        return output


class TOcrStreamWorker(TOcrWorker):
    def __init__(self, ocr):
        super().__init__(ocr)
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
            image = grabber.grab_window_area(self._box)
            output = self._ocr.recognize(image)
            self._is_busy = False
            return output


class TOcr:
    obs_output = TypedObservable(dict)

    def __init__(self, ocr: OCR, eventsys, accessor):
        self._ocr = ocr
        self._mode = TOcrMode.SINGLE
        self._workers = TOcrWorkerManager(
            workers={
                TOcrMode.SINGLE: TOcrSingleWorker(ocr)
            }
        )
        self._pipeline = TOcrPipeline(eventsys, accessor, self._workers.obs_data, self.obs_output)
        self._pipeline.activate()

    def change_mode(self, mode: TOcrMode):
        self._mode = mode

    def process_area(self, box: tuple[int, int, int, int], _from: str, to: str):
        if self._workers.is_busy():
            raise RuntimeError('Some worker already in process')

        self._pipeline.inject_data(1, {'from': _from, 'to': to})
        self._pipeline.inject_data(2, {'mode': self._mode})
        current_worker = self._workers.get(self._mode)
        current_worker.process_area(box)
        self.obs_output.notify({
            'mode': self._mode,
            'status': TOcrStatus.RECOGNIZING,
            'text': 'Recognizing...'
        })

    def terminate(self):
        current_worker = self._workers.get(self._mode)
        current_worker.terminate()


class TOcrPipeline(ServicePipeline):
    services = (TranslationService,)
    tasks = ('task.tocr.translate',)

    def __init__(self, eventsys, accessor, obs_data, obs_output):
        self._obs_data = obs_data
        self._obs_output = obs_output
        super().__init__(eventsys, accessor)

    def create_pipeline(self):
        return (
            (self._obs_data, self.handle_ocr_output_receive),
            (TranslationService.Events.OUTPUT_RECEIVE, self.handle_translation_output_receive)
        )

    def process(self):
        pass

    def terminate(self):
        for id in self.tasks:
            if TaskManager.objects().exists(id):
                task = TaskManager.objects().get(id)
                task.cancel()
                task.wait()

    def handle_ocr_output_receive(self, mode, output):
        inj_data = self.get_injected_data()
        s = self.get_service(TranslationService)
        TaskManager.execute(
            task=lambda _: s.translate(
                output['text'],
                inj_data['from'],
                inj_data['to']
            ),
            id=self.tasks[0]
        )

    def handle_translation_output_receive(self, e):
        self.redirect_to_observer(
            observable=self._obs_output,
            data={
                'mode': self.get_injected_data()['mode'],
                'status': TOcrStatus.SUCCESS,
                'text': e.output['text']
            }
        )
