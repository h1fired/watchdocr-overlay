from frontend.viewmodels.common.mvvm import QmlLinkerCore
from frontend.viewmodels.components.vm_processor import ProcessorViewModel


VIEWMODELS = (
    ProcessorViewModel,
)


class WatchdOcrLinkerCore(QmlLinkerCore):
    viewmodels = tuple(VIEWMODELS)
