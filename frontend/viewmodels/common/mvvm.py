from PySide6.QtCore import QObject, Property, Signal, QEnum
from PySide6.QtQuick import QQuickWindow
from PySide6.QtQml import qmlRegisterType
from enum import IntEnum
from src.context import AppContext


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
        context: AppContext
    ):
        self._window = window
        self._context = context
        self._eventsys = context.eventsys

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

    def eventsys(self):
        return self._eventsys

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

    def initialize(self, window, context: AppContext):
        self._window = window
        self._context = context

        for vm in self.__viewmodels__.values():
            vm.initialize(window, context)

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
