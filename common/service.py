from typing import Type, TypeVar
from types import SimpleNamespace
from .event import EventSystem, IEvent, _Event


T = TypeVar('T')


class ServiceError(Exception):
    pass


class Service:
    def __init__(self, related_services: list['Service'] = []):
        self._cls_events = get_service_events(self.Events)
        self._eventsys = None
        self._relations: tuple['Service'] = tuple(set(related_services))

    @property
    def event(self):
        return self._eventsys

    def events(self):
        return self._cls_events

    def init(self, eventsys: EventSystem):
        self._eventsys = ServiceEventSystem(eventsys, self)
        self.on_init()
        self._shared_objects = SimpleNamespace(**self.propagate_shared_objects())

    def on_init(self):
        pass

    def on_full_init(self):
        pass

    def on_destroy(self):
        pass

    def shutdown(self):
        self.on_destroy()

    def get_related(self, service: Type[T]) -> T:
        for s in self._relations:
            if type(s) is service:
                return s
        raise ServiceError('Service is not related')

    def relations(self):
        return self._relations

    def propagate_shared_objects(self):
        return {}

    @property
    def shared(self):
        return self._shared_objects

    class Events:
        pass


class ServicesCollector:
    def __init__(self):
        self._services = []

    def all(self) -> list[Service]:
        return self._services

    def register(self, service: Service):
        if service in self._services:
            raise ValueError(f'Service already exists {service.__class__.__name__}')
        self._services.append(service)


class ServicesAccessor:
    def __init__(self, collector: ServicesCollector):
        self._collector = collector

    def get(self, cls: Type[T]) -> T:
        for service in self._collector.all():
            if isinstance(service, cls):
                return service
        raise ServiceError('Service not found')

    def get_by_str(self, name: str):
        for service in self._collector.all():
            if service.__class__.__name__ == name:
                return service
        raise ServiceError('Service not found')


def validate_noncyclic_deps(collector: ServicesCollector):
    for service in collector.all():
        for relation in service.relations():
            if service in relation.relations():
                return False
    return True


def get_service_events(cls: type):
    return [
        value
        for key, value in vars(cls).items()
        if (
            not key.startswith("__")
            and isinstance(value, type)
            and issubclass(value, IEvent)
        )
    ]


class ServiceEventSystem:
    def __init__(self, eventsys: EventSystem, service: Service):
        self._es = eventsys
        self._service = service

    def register(self, event: _Event):
        if self._check_member(event.interface):
            self._es.register(event)
        else:
            raise ValueError(
                'Event must be a member of the '
                'main or related classes'
            )

    def dispatch(self, event: IEvent, data: dict):
        self._es.dispatch(event, data)

    def dispose(self, event: _Event):
        self._es.dispatch(event)

    def _check_member(self, event):
        if event in self._service.events():
            return True
        for relation in self._service.relations():
            if event in relation.events():
                return True
        return False
