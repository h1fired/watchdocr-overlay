from frontend.common.mvvm_qml import QmlLinkerCore
from PySide6.QtQml import qmlRegisterSingletonInstance
from frontend.viewmodels.components.system import SystemViewModel
from frontend.viewmodels.components.ocrtranslate import OcrTranslateViewModel
from frontend.viewmodels.components.ocr import OcrViewModel
from frontend.viewmodels.types import registerQmlTypes


class WindowQmlLinkerCore(QmlLinkerCore):
    viewmodels = [
        SystemViewModel,
        OcrTranslateViewModel,
        OcrViewModel
    ]


qmlLinkerCore = WindowQmlLinkerCore()
qmlRegisterSingletonInstance(WindowQmlLinkerCore, 'App.Backend', 1, 0, 'Backend', qmlLinkerCore)
registerQmlTypes()
