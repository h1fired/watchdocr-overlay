from common.service import (
    ServicesCollector,
    ServicesAccessor,
    ServiceError,
    validate_noncyclic_deps
)
from common.event import EventSystem
from common.task import TaskManager
from src.tocr.service import OcrTranslateService
from src.ocr.service import OcrService


class CoreApplication:
    def __init__(self):
        self._accessor = None
        self._collector = None
        self._eventsys = EventSystem()

    def init(self):
        self._init_task_manager()
        self._init_services()
        self._init_full_services()

    def accessor(self):
        return self._accessor

    def event_system(self):
        return self._eventsys

    def _init_services(self):
        collector = ServicesCollector()

        ocr_s = OcrService()
        collector.register(ocr_s)

        ocr_translate_s = OcrTranslateService(related_services=[
            ocr_s
        ])
        collector.register(ocr_translate_s)

        for s in collector.all():
            s.init(self._eventsys)

        # Cyclic dependencies checking for
        # complicated services relations avoiding
        if not validate_noncyclic_deps(collector):
            raise ServiceError(
                'Cyclic dependency found'
                'between service relations'
            )

        self._accessor = ServicesAccessor(collector)
        self._collector = collector

    def _init_full_services(self):
        for service in self._collector.all():
            service.on_full_init()

    def _init_task_manager(self):
        TaskManager.run()
