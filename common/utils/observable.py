from typing import Callable
from ..observable import Observer
from ..event import IEvent, EventSystem


def observer_to_event(
    sys: EventSystem,
    observable: Observer | Callable,
    event: IEvent,
    fields: tuple
):
    def handler(*args):
        data = {k: v for k, v in zip(fields, args)}
        sys.dispatch(event, data)

    if isinstance(observable, Observer):
        observable.register(handler)
    else:
        observable(handler)
