from PySide6.QtCore import QObject
from common.service import ServicesAccessor
from common.event import EventSystem
from typing import TypeVar, Type


T = TypeVar('T')


class ViewModel(QObject):
    context_id: str

    def __init__(self, engine, accessor: ServicesAccessor, event_system: EventSystem):
        super().__init__(None)
        self.__engine = engine
        self.__accessor = accessor
        self.__event = event_system

    def get_service(self, service: Type[T]) -> T:
        return self.__accessor.get(service)

    def event(self):
        return self.__event

    def on_load(self):
        pass

    def load(self):
        if not self.context_id:
            raise ValueError('context_id is not defined')
        self.on_load()
        self.__engine.rootContext().setContextProperty(self.context_id, self)
