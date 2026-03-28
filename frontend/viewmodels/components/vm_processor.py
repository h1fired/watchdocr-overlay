from frontend.viewmodels.common.mvvm import QmlViewModel
from src.watchdocr.processor import Events
from src.common.event import Event
from qt.core import Signal


class ProcessorViewModel(QmlViewModel):
    _name = 'Processor'

    resultReceived = Signal(str)

    def onLoaded(self):
        Event.subscribe(
            system=self.eventsys(),
            event=Events.PROCESSOR_RESULT_RECEIVED,
            handler=self.onProcessorResultReceived
        )

    def onProcessorResultReceived(self, e):
        self.resultReceived.emit(e.text)
