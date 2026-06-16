from qt.qml import qmlRegisterSingletonType, qmlRegisterType, QQmlApplicationEngine
from frontend.viewmodels.types.screen import ScreenManager
from frontend.viewmodels.types.image import ImageProvider, AnimatedImage


def registerUtilsQmlTypes():
    qmlRegisterType(AnimatedImage, 'App.Utils', 1, 0, 'AnimatedImage')
    qmlRegisterSingletonType(ScreenManager, 'App.Utils', 1, 0, 'UtilsScreen')


def registerQmlImageProviders(engine: QQmlApplicationEngine):
    providers = {
        'preview_screens': ImageProvider(),
        'preview_area': ImageProvider()
    }

    for name, provider in providers.items():
        engine.addImageProvider(name, provider)
    return providers
