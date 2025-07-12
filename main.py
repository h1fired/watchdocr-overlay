from PySide6.QtWidgets import QApplication
from PySide6.QtQml import QQmlApplicationEngine
import sys
from src.app import CoreApplication

from frontend.viewmodels.ocroverlay import OCROverlayViewModel


if __name__ == '__main__':
    core = CoreApplication()
    core.init()

    app = QApplication(sys.argv)
    engine = QQmlApplicationEngine()

    # Load viewmodels
    viewmodels = (OCROverlayViewModel,)
    viewmodels_objs = []
    for vm in viewmodels:
        obj = vm(engine, core.accessor(), core.event_system())
        obj.load()
        viewmodels_objs.append(obj)

    # Load QML window
    engine.load('frontend/ui/window.qml')
    if not engine.rootObjects():
        sys.exit(-1)

    # Run GUI
    sys.exit(app.exec())
