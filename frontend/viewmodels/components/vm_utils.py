from frontend.viewmodels.common.mvvm import QmlViewModel
from qt.core import QApplication, Slot, Signal


class UtilsViewModel(QmlViewModel):
    _name = 'Utils'

    textCopiedToClipboard = Signal()

    @Slot(str)
    def copyTextToClipboard(self, text: str):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.textCopiedToClipboard.emit()
