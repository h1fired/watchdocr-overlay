from qt.qml import qmlRegisterSingletonType
from frontend.viewmodels.types.screen import ScreenManager


def registerUtilsQmlTypes():
    qmlRegisterSingletonType(ScreenManager, 'App.Utils', 1, 0, 'UtilsScreen')
