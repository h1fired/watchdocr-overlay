from src.common.utils.logging import log
from typing import Callable, Any, Generic, TypeVar, Iterable
from collections import defaultdict
from threading import Lock
from functools import wraps


class Observable:
    def __init__(self):
        self._lock = Lock()
        self._notifiers: list[Callable] = []
        self._identified_notifiers = {}

    def register(self, callback: Callable, id: str | None = None):
        with self._lock:
            self._notifiers.append(callback)
            if id:
                if id in self._identified_notifiers.keys():
                    raise KeyError('Callback <id> already exists')
                self._identified_notifiers[id] = callback

    def unregister(self, callback: Callable | str):
        with self._lock:
            if isinstance(callback, str):
                callback = self._identified_notifiers.pop(callback)
                self._notifiers.remove(callback)
            else:
                if callback in self._identified_notifiers.values():
                    key = next(
                        k for k, v
                        in self._identified_notifiers.items()
                        if v == callback
                    )
                    self._identified_notifiers.pop(key)
                self._notifiers.remove(callback)

    def notify(self, *args):
        with self._lock:
            for notifier in self._notifiers:
                try:
                    notifier(*args)
                except Exception as e:
                    log.exception(e, extra={'title': 'CALLBACK'})

    def clear(self):
        self._notifiers.clear()
        self._identified_notifiers.clear()

    def to(
        self,
        observable: 'Observable',
        format: Callable | None = None,
        id: str | None = None
    ):
        def func(*args):
            fargs = format(*args) if format else args
            observable.notify(*fargs)
        self.register(func, id)

    def to_mapped(
        self,
        observable: 'MappedObservable',
        subject: str,
        format: Callable | None = None,
        id: str | None = None
    ):
        def func(*args):
            fargs = format(*args) if format else args
            observable.notify(subject, *fargs)
        self.register(func, id)


class MappedObservable(Observable):
    def __init__(self):
        super().__init__()
        self._notifiers = defaultdict(list)
        self._identified_notifiers = {}

    def register(
        self,
        subject: str,
        callback: Callable,
        id: str | None = None
    ):
        with self._lock:
            self._notifiers[subject].append(callback)
            if id:
                if id in self._identified_notifiers.keys():
                    raise KeyError('Callback <id> already exists')
                self._identified_notifiers[id] = (subject, callback)

    def unregister(self, subject: str, callback: Callable):
        with self._lock:
            self._notifiers[subject].remove(callback)

    def unregister_by_id(self, id: str):
        with self._lock:
            subject, callback = self._identified_notifiers.pop(id)
            self._notifiers[subject].remove(callback)

    def notify(self, subject: str, *args):
        with self._lock:
            if subject not in self._notifiers.keys():
                return
            for notifier in self._notifiers[subject]:
                try:
                    notifier(*args)
                except Exception as e:
                    log.exception(e, extra={'title': 'CALLBACK'})

    def clear(self):
        self._notifiers.clear()

    def to(
        self,
        observable: 'Observable',
        subject: str,
        format: Callable | None = None,
        id: str | None = None
    ):
        def func(*args):
            fargs = format(*args) if format else args
            observable.notify(*fargs)
        self.register(subject, func, id)

    def to_mapped(
        self,
        observable: 'MappedObservable',
        subject_from: str,
        subject_to: str,
        format: Callable | None = None,
        id: str | None = None
    ):
        def func(*args):
            fargs = format(*args) if format else args
            observable.notify(subject_to, *fargs)
        self.register(subject_from, func, id)


class TypedObservable(Observable):
    def __init__(self, *types):
        super().__init__()
        self._types = types

    def notify(self, *args):
        if len(args) != len(self._types):
            raise TypeError('Invalid arguments')
        elif any(type(v) is not t for v, t in zip(args, self._types)):
            raise TypeError('Invalid arguments')
        return super().notify(*args)


def observer(observable: Observable):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            observable.register(func)
        return wrapper
    return decorator


T = TypeVar("T")


class ObservableType:
    def __init__(self):
        self._observable = Observable()

    @property
    def observable(self):
        return self._observable

    def register(self, handler: Callable):
        self._observable.register(handler)

    def unregister(self, handler: Callable):
        self._observable.unregister(handler)


class ObservableVar(ObservableType, Generic[T]):
    __slots__ = ('_type', '_value', '_observable', '_unique')

    def __init__(self, _type: type[T], value: Any, notify_unique=False):
        super().__init__()

        if type(value) is not _type:
            raise TypeError('Invalid value type')
        self._type = _type
        self._value = value
        self._unique = notify_unique

    @property
    def value(self) -> T:
        return self._value

    @value.setter
    def value(self, value: T):
        if self._unique and value == self._value:
            return
        if type(value) is not self._type:
            raise TypeError('Invalid value type')
        self._value = value
        self.observable.notify(value)


class ObservableList(list, ObservableType):
    def __init__(self, iterable: Iterable = (), notify_unique=True):
        list.__init__(self, iterable)
        ObservableType.__init__(self)
        self._unique = notify_unique

    def append(self, object):
        super().append(object)
        self.observable.notify(self)

    def extend(self, iterable):
        super().extend(iterable)
        if self._unique and len(iterable) <= 0:
            return
        self.observable.notify(self)

    def insert(self, index, object):
        value = self[index]
        super().insert(index, object)
        if self._unique and value == object:
            return
        self.observable.notify(self)

    def pop(self, index=-1):
        obj = super().pop(index)
        self.observable.notify(self)
        return obj

    def remove(self, value):
        super().remove(value)
        self.observable.notify(self)

    def clear(self):
        super().clear()
        self.observable.notify(self)

    def update(self, iterable: Iterable):
        super().clear()
        super().extend(iterable)

    def to_list(self):
        return list(self)

    def __iadd__(self, value):
        super().__iadd__(value)
        if self._unique and len(value) <= 0:
            return
        self.observable.notify(self)

    def __imul__(self, value):
        super().__imul__(value)
        if self._unique and value == 1:
            return
        self.observable.notify(self)

    def __delitem__(self, key):
        super().__delitem__(key)
        self.observable.notify(self)

    def __setitem__(self, key, value):
        old = self[key]
        super().__setitem__(key, value)
        if self._unique and old == value:
            return
        self.observable.notify(self)


class ObservableDict(dict, ObservableType):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        ObservableType.__init__(self)
        self._unique = kwargs.get('notify_unique', True)

    def popitem(self):
        item = super().popitem()
        self.observable.notify(self)
        return item

    def pop(self, *args, **kwargs):
        item = super().pop(*args, **kwargs)
        self.observable.notify(self)
        return item

    def __setitem__(self, key, value):
        if self._unique and key in self.keys():
            old = self.get(key)
            if old != value:
                self.observable.notify(self)
        else:
            self.observable.notify(self)
        return super().__setitem__(key, value)

    def __delitem__(self, key):
        super().__delitem__(key)
        self.observable.notify(self)

    def update(self, *args, **kwargs):
        self.observable.notify(self)
        return super().update(*args, **kwargs)

    def clear(self, *args, **kwargs):
        self.observable.notify(self)
        return super().update(*args, **kwargs)


class ObservableIdType(str):
    pass


class ObservableClass:
    def __init__(self):
        self.__observer = MappedObservable()
        self.__observables = self.get_cls_observables()

    def notify(self, subject: ObservableIdType, value: Any):
        if subject not in self.__observables:
            raise ValueError('Observable not declared in class')
        self.__observer.notify(subject, value)

    def observe(self, subject: ObservableIdType, callback: Callable):
        if subject not in self.__observables:
            raise ValueError('Observable not declared in class')
        return self.__observer.register(subject, callback)

    def observable(self):
        return self.__observer

    class Observables:
        pass

    def get_cls_observables(self):
        return tuple(
            value
            for key, value in vars(self.Observables).items()
            if (
                not key.startswith("__")
                and isinstance(value, str)
            )
        )
