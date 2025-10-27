from frontend.common.mvvm_qml import QmlViewModel
from qt.core import QApplication, Slot, Signal


class SystemViewModel(QmlViewModel):
    _name = 'System'

    textCopiedToClipboard = Signal()

    @Slot(str)
    def copyTextToClipboard(self, text: str):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        self.textCopiedToClipboard.emit()
