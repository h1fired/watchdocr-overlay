from qt.qml import qmlRegisterSingletonType, QQmlApplicationEngine
from frontend.viewmodels.types.screen import ScreenManager
from frontend.viewmodels.types.image import ImageProvider


def registerUtilsQmlTypes():
    qmlRegisterSingletonType(ScreenManager, 'App.Utils', 1, 0, 'UtilsScreen')


def registerQmlImageProviders(engine: QQmlApplicationEngine):
    providers = {'preview_screens': ImageProvider()}

    for name, provider in providers.items():
        engine.addImageProvider(name, provider)
    return providers
