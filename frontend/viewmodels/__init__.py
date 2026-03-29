from frontend.viewmodels.common.mvvm import QmlLinkerCore
from frontend.viewmodels.components.vm_processor import ProcessorViewModel
from frontend.viewmodels.components.vm_utils import UtilsViewModel


VIEWMODELS = (
    ProcessorViewModel,
    UtilsViewModel
)


class WatchdOcrLinkerCore(QmlLinkerCore):
    viewmodels = tuple(VIEWMODELS)
