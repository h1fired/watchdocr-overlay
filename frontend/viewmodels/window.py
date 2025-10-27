from frontend.common.mvvm_qml import QmlLinkerCore
from frontend.viewmodels.components.system import SystemViewModel
from frontend.viewmodels.components.ocrtranslate import OCRTranslateViewModel
from PySide6.QtQml import qmlRegisterSingletonInstance


class WindowQmlLinkerCore(QmlLinkerCore):
    viewmodels = [
        SystemViewModel,
        OCRTranslateViewModel
    ]


qmlLinkerCore = WindowQmlLinkerCore()
qmlRegisterSingletonInstance(WindowQmlLinkerCore, 'App.Backend', 1, 0, 'Backend', qmlLinkerCore)
