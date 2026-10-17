from PySide6.QtCore import QObject, Property, Signal, QEnum
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQml import qmlRegisterType
from enum import IntEnum
from typing import TypeVar


class QmlViewModelStatus(IntEnum):
    NOT_READY = 0
    LOADING = 1
    READY = 2


class QQmlViewModelStatus(QObject):
    ViewModelStatus = QEnum(QmlViewModelStatus)


qmlRegisterType(QQmlViewModelStatus, "App.Backend", 1, 0, "ViewModelStatus")


QM = TypeVar('QM', bound='QmlModel')


class QmlModel:
    async def initialize(self):
        pass

    async def destroy(self):
        pass


class QmlModelProvider:
    def __init__(self):
        self._models: dict[type[QmlModel], QmlModel] = {}

    def register(self, model: QmlModel) -> QmlModel:
        model_type = type(model)
        if model_type in self._models:
            raise KeyError(f'Model {model_type.__name__} already registered')
        self._models[model_type] = model
        return model

    def get_model(self, model_type: type[QM]) -> QM:
        return self._models[model_type]

    def models(self):
        return tuple(self._models.values())


class QmlLinkerCoreMeta(type(QObject)):
    def __new__(mcs, name, bases, dct):
        __viewmodels__ = {}
        viewmodels: list[QmlViewModel] = dct.get("viewmodels", [])

        for vm in viewmodels:
            if vm._name in __viewmodels__.keys():
                raise NameError('View model name already exists')
            obj = vm()
            propname = vm._name
            dct[propname] = Property(QObject, lambda _, o=obj: o, constant=True)
            __viewmodels__[vm._name] = obj

        dct['__viewmodels__'] = __viewmodels__

        return super().__new__(mcs, name, bases, dct)


class QmlViewModel(QObject):
    _name: str
    models: tuple[type[QmlModel], ...] = ()

    statusChanged = Signal()

    def __init__(self):
        super().__init__()
        self._window = None
        self._model_provider: QmlModelProvider | None = None
        self._status = QmlViewModelStatus.NOT_READY
        self.onInit()

    def window(self):
        return self._window

    def getModel(self, model_type: type[QM]) -> QM:
        if model_type not in self.models:
            raise PermissionError(
                f'{type(self).__name__} has no access to model {model_type.__name__}'
            )
        if self._model_provider is None:
            raise RuntimeError('View model is not initialized')
        return self._model_provider.get_model(model_type)

    def initialize(
        self,
        window: QQuickWindow,
        model_provider: QmlModelProvider
    ):
        self._window = window
        self._model_provider = model_provider

    def loadContent(self):
        self.setStatus(QmlViewModelStatus.LOADING)
        self.onLoaded()
        self.setStatus(QmlViewModelStatus.READY)

    def loadFullyContent(self):
        self.onFullyLoaded()

    def destroyContent(self):
        self.onDestroy()

    def getStatus(self):
        return self._status

    def setStatus(self, arg__1: QmlViewModelStatus):
        self._status = arg__1
        self.statusChanged.emit()

    status = Property(int, getStatus, notify=statusChanged)

    def onInit(self):
        pass

    def onLoaded(self):
        pass

    def onFullyLoaded(self):
        pass

    def onDestroy(self):
        pass


class QmlLinkerCore(QObject, metaclass=QmlLinkerCoreMeta):
    viewmodels: list[type[QmlViewModel]] = []

    statusChanged = Signal()

    def __init__(self):
        super().__init__()
        self._status = QmlViewModelStatus.NOT_READY
        self._window = None
        self._eventsys = None

    def window(self):
        return self._window

    def initialize(self, window, model_provider: QmlModelProvider):
        self._window = window

        for vm in self.__viewmodels__.values():
            vm.initialize(window, model_provider)

    def loadContent(self):
        self.setStatus(QmlViewModelStatus.LOADING)
        for vm in self.__viewmodels__.values():
            vm.loadContent()
        self.setStatus(QmlViewModelStatus.READY)

    def loadFullyContent(self):
        for vm in self.__viewmodels__.values():
            vm.loadFullyContent()

    def destroyContent(self):
        for vm in self.__viewmodels__.values():
            vm.destroyContent()

    def getStatus(self):
        return self._status

    def setStatus(self, arg__1: QmlViewModelStatus):
        self._status = arg__1
        self.statusChanged.emit()

    status = Property(int, getStatus, notify=statusChanged)
