from frontend.viewmodels.common.mvvm import QmlLinkerCore
from frontend.viewmodels.components.vm_processor import ProcessorViewModel
from frontend.viewmodels.components.vm_utils import UtilsViewModel
from frontend.viewmodels.components.vm_translation import TranslationViewModel


VIEWMODELS = (
    ProcessorViewModel,
    TranslationViewModel,
    UtilsViewModel,
)


class WatchdOcrLinkerCore(QmlLinkerCore):
    viewmodels = tuple(VIEWMODELS)
