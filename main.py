from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
import sys
from src.app import CoreApplication


if __name__ == '__main__':
    core = CoreApplication()
    core.init()
    
    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.load('frontend/window.qml')
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
