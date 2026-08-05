from qt.qml import qmlRegisterSingletonType, qmlRegisterType, QQmlApplicationEngine
from frontend.viewmodels.types.screen import ScreenManager
from frontend.viewmodels.types.mouse import MouseTracker
from frontend.viewmodels.types.image import ImageProvider, AnimatedImage
from frontend.viewmodels.types.text_color_detector.type import TextColorDetector


def registerUtilsQmlTypes():
    qmlRegisterType(AnimatedImage, 'App.Utils', 1, 0, 'AnimatedImage')
    qmlRegisterType(TextColorDetector, 'App.ImageText', 1, 0, 'TextColorDetector')
    qmlRegisterSingletonType(ScreenManager, 'App.Utils', 1, 0, 'UtilsScreen')
    qmlRegisterSingletonType(MouseTracker, 'App.Utils', 1, 0, 'UtilsMouseTracker')


def registerQmlImageProviders(engine: QQmlApplicationEngine):
    providers = {
        'preview_screens': ImageProvider(),
        'preview_area': ImageProvider(),
        'text_cleared_overlay': ImageProvider(),
    }

    for name, provider in providers.items():
        engine.addImageProvider(name, provider)
    return providers
