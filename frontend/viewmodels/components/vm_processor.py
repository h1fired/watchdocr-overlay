from frontend.viewmodels.common.mvvm import QmlViewModel
from src.watchdocr.processor import Events
from src.common.event import Event
from qt.core import Signal


class ProcessorViewModel(QmlViewModel):
    _name = 'Processor'

    textResultReceived = Signal(str)

    def onLoaded(self):
        Event.subscribe(
            system=self.eventsys(),
            event=Events.TEXT_RESULT_RECEIVED,
            handler=self.onTextResultReceived
        )

    def onTextResultReceived(self, e):
        self.textResultReceived.emit(e.text)
