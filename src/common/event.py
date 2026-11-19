from typing import Protocol, runtime_checkable, Callable, Any
from types import SimpleNamespace
from collections import defaultdict
from .utils.logging import log
import threading


class EventData(SimpleNamespace):
    pass


@runtime_checkable
class IEvent(Protocol):
    ...


def validate_event_data(obj: IEvent, data: dict):
    fields = obj.__annotations__
    if len(data) != len(fields):
        return False
    for name, _type in fields.items():
        if _type is Any:
            continue
        if name not in data:
            return False
        if type(data[name]) is not _type:
            return False
    return True


class _Event:
    def __init__(self, interface: type[IEvent]):
        if not issubclass(interface, IEvent):
            raise TypeError('Wrong event interface type')
        self._interface = interface

    @property
    def interface(self):
        return self._interface


class _BusEvent(_Event):
    def __init__(self, interface, handler: Callable, condition: Callable):
        super().__init__(interface)
        self._handler = handler
        if not condition:
            self._condition = lambda data: True
        else:
            self._condition = condition

    @property
    def handler(self):
        return self._handler

    @property
    def condition(self):
        return self._condition


class _DisposableBusEvent(_BusEvent):
    pass


class EventSystem:
    def __init__(self):
        self._events = defaultdict(list)
        self._listeners: list[Callable] = []
        self._thread_id = threading.get_ident()

    def register(self, event: _Event):
        self._events[event.interface].append(event)
        return event

    def listen(self, callback: Callable):
        self._listeners.append(callback)

    def dispatch(self, event: IEvent, data: dict):
        # Listeners must be called from the event loop thread only
        if threading.get_ident() != self._thread_id:
            raise RuntimeError(
                f'Event {event.__name__} dispatched outside '
                f'of the event loop thread'
            )

        if type(data) is not dict:
            raise TypeError('Only dict is supported for event data')

        if not validate_event_data(event, data):
            log.error('Event data is invalid for %s: %s', event.__name__, data, extra={'title': 'Events'})
            raise ValueError(f'Event data is not valid -> {event.__name__}')

        namespace = EventData(**data)

        for listener in self._listeners:
            try:
                listener(event, namespace)
            except Exception as e:
                log.exception('[EVENT LISTENER ERROR] %s', e, extra={'title': 'Events'})

        entities = self._events[event]
        for e in tuple(entities):  # Copy, disposable events removes itself
            if type(e) is _BusEvent:
                if e.condition(namespace):
                    try:
                        e.handler(namespace)
                    except Exception as e:
                        log.exception(f'[EVENT CALLBACK] {e}', extra={'title': 'Events'})
            elif type(e) is _DisposableBusEvent:
                if e.condition(namespace):
                    try:
                        e.handler(namespace)
                    except Exception as ex:
                        log.exception(f'[EVENT CALLBACK] {ex}', extra={'title': 'Events'})
                    finally:
                        entities.remove(e)

    def dispose(self, event: _Event):
        entities = self._events[event.interface]
        if event in entities:
            entities.remove(event)
