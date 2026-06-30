from frontend.viewmodels.common.mvvm import QmlLinkerCore
from frontend.viewmodels.components.vm_processor import ProcessorViewModel
from frontend.viewmodels.components.vm_utils import UtilsViewModel
from frontend.viewmodels.components.vm_translation import TranslationViewModel
from frontend.viewmodels.components.vm_ocr import OcrViewModel
from frontend.viewmodels.components.vm_preview import PreviewViewModel
from frontend.viewmodels.components.vm_settings import SettingsViewModel
from frontend.viewmodels.components.vm_general import GeneralViewModel


VIEWMODELS = (
    GeneralViewModel,
    ProcessorViewModel,
    TranslationViewModel,
    UtilsViewModel,
    OcrViewModel,
    PreviewViewModel,
    SettingsViewModel
)


class WatchdOcrLinkerCore(QmlLinkerCore):
    viewmodels = tuple(VIEWMODELS)
