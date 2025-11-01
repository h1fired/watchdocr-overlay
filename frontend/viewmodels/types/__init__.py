from PySide6.QtQml import qmlRegisterType, qmlRegisterSingletonType
from .image import AnimatedImage
from .screen import ScreenManager


def registerQmlTypes():
    qmlRegisterType(AnimatedImage, "App.External", 1, 0, "EAnimatedImage")
    qmlRegisterSingletonType(ScreenManager, 'App.Utils', 1, 0, 'EScreen')
