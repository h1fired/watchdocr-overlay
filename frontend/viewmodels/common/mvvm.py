from PySide6.QtCore import QObject, Property, Signal, QEnum
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQml import qmlRegisterType
from enum import IntEnum
from src.common.api import (
    KernelAPI,
    KernelAPIStrictCollection,
    KernelAPICollection,
    T, Type
)


class QmlViewModelStatus(IntEnum):
    NOT_READY = 0
    LOADING = 1
    READY = 2


class QQmlViewModelStatus(QObject):
    ViewModelStatus = QEnum(QmlViewModelStatus)


qmlRegisterType(QQmlViewModelStatus, "App.Backend", 1, 0, "ViewModelStatus")


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
    _needed_api: tuple[Type[KernelAPI], ...] = tuple()

    statusChanged = Signal()

    def __init__(self):
        super().__init__()
        self._window = None
        self._status = QmlViewModelStatus.NOT_READY
        self.onInit()

    def window(self):
        return self._window

    def initialize(
        self,
        window: QQuickWindow,
        api_collection: KernelAPIStrictCollection
    ):
        self._window = window
        self._apis = api_collection

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

    def getApi(self, api: Type[T]) -> T:
        return self._apis.get(api)

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

    def initialize(self, window, api: KernelAPICollection):
        self._window = window

        for vm in self.__viewmodels__.values():

            # Create strict API collection
            objs = [a for a in api.all() if type(a) in vm._needed_api]
            strict_api = KernelAPIStrictCollection(tuple(objs))

            # Init viewmodel
            vm.initialize(window, strict_api)

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
