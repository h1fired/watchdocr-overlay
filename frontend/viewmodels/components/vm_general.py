from frontend.viewmodels.common.mvvm import QmlViewModel
from frontend.utils import ghotkey
from qt.core import Slot
from qt.utils import invokeFunc


_ignore_flag = False


@invokeFunc
def toggle_window_visibility():
    if _ignore_flag:
        return

    from frontend.core import GuiCoreApplication
    gui = GuiCoreApplication()
    system_obj = gui.system_obj()
    system_obj.requestVisibilitySwap()


class GeneralViewModel(QmlViewModel):
    _name = 'General'

    @Slot(str)
    def changeOverlayToggleHotkey(self, hotkey: str):
        ghotkey.unbind_all()
        ghotkey.bind(hotkey, toggle_window_visibility)

    @Slot(bool)
    def blockOverlayToggleHotkey(self, value: bool):
        global _ignore_flag
        _ignore_flag = value
