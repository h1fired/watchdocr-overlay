from PySide6.QtQml import qmlRegisterType, qmlRegisterSingletonType, QQmlApplicationEngine
from frontend.viewmodels.types.image import AnimatedImage, ImageProvider
from frontend.viewmodels.types.screen import ScreenManager


def registerQmlTypes():
    qmlRegisterType(AnimatedImage, "App.External", 1, 0, "EAnimatedImage")
    qmlRegisterSingletonType(ScreenManager, 'App.Utils', 1, 0, 'EScreen')


def registerQmlImageProviders(engine: QQmlApplicationEngine):
    providers = {'preview_screens': ImageProvider()}

    for name, provider in providers.items():
        engine.addImageProvider(name, provider)
    return providers
