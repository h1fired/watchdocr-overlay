from common.event import Event, IEvent, EventSystem
from common.observable import Observable
from typing import Callable


class Pipeline:
    def __init__(self, eventsys: EventSystem):
        self._system = eventsys
        self._pipeline = self.create_pipeline()
        self._observables = []
        self._data = {}
        self._disabled_stages = set()
        self._current_stage = 0

    def create_pipeline(self):
        raise NotImplementedError

    def create_wrapper(self, stage: int, func: Callable):
        def wrapper(*args, **kwargs):
            normalized_stage = stage + 1
            self._current_stage = normalized_stage
            func(*args, **kwargs)
        return wrapper

    def activate(self):
        for i, (e, func) in enumerate(self._pipeline):
            wrapped_func = self.create_wrapper(i, func)

            if isinstance(e, type):
                observer = Event.subscribe(self._system, e, wrapped_func)
                self._observables.append((e, observer))
            else:
                e.register(wrapped_func)
                self._observables.append((e, wrapped_func))

    def deactivate(self):
        for initiator, e in self._observables:
            if isinstance(e, IEvent):
                self._system.dispose(e)
            else:
                initiator.unregister(e)
        self._observables.clear()

    def process(self, *args, **kwargs):
        raise NotImplementedError

    def enable_stage(self, stage: int):
        normalized_stage = stage + 1
        if normalized_stage in self._disabled_stages:
            self._disabled_stages.remove(normalized_stage)

    def disable_stage(self, stage: int):
        normalized_stage = stage + 1
        self._disabled_stages.add(normalized_stage)

    def redirect_to(self, event: type[IEvent], data: dict):
        self._system.dispatch(event, data)

    def redirect_to_observer(self, observable: Observable, data: dict):
        observable.notify(data)

    def inject_data(self, stage: int, data: dict):
        self._data[stage] = data

    def get_injected_data(self):
        return self._data.get(self._current_stage, None)


class ServicePipeline(Pipeline):
    services: tuple

    def __init__(self, eventsys, accessor):
        super().__init__(eventsys)
        self._services = {cls: accessor(cls) for cls in self.services}

    def get_service(self, service: type):
        return self._services[service]
