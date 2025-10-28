from PySide6.QtQml import qmlRegisterType
from .image import AnimatedImage


def registerQmlTypes():
    qmlRegisterType(AnimatedImage, "App.External", 1, 0, "EAnimatedImage")
