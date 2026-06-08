from frontend.viewmodels.common.mvvm import QmlViewModel
from src.watchdocr.api.translation import TranslationAPI
from src.watchdocr.plugins.translation.types import LANGUAGES_VERBOSE
from qt.core import Property, Signal, Slot, QAbstractListModel, Qt, QModelIndex, QObject


class LanguageListModel(QAbstractListModel):
    CodeRole = Qt.UserRole + 1000
    NameRole = Qt.UserRole + 1001

    def __init__(self, entries: list = [], parent=None):
        super().__init__(parent)
        self._entries = entries

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._entries)

    def roleNames(self):
        roles = dict()
        roles[LanguageListModel.NameRole] = b'name'
        roles[LanguageListModel.CodeRole] = b'code'
        return roles

    def data(self, index, role=Qt.DisplayRole):
        if 0 <= index.row() < self.rowCount() and index.isValid():
            item = self._entries[index.row()]
            if role == LanguageListModel.NameRole:
                return item['name']
            elif role == LanguageListModel.CodeRole:
                return item['code']

    def appendRow(self, code: str, name: str):
        self.beginInsertRows(QModelIndex(), self.rowCount(), self.rowCount())
        self._entries.append(dict(name=name, code=code))
        self.endInsertRows()

    @Slot(int, result='QVariant')
    def get(self, row: int):
        if 0 <= row < self.rowCount():
            return self._entries[row]
        return None

    def provideData(self, entries: list[dict[str, str]]):
        self.beginResetModel()
        self._entries = entries
        self.endResetModel()


class TranslationViewModel(QmlViewModel):
    _name = 'Translation'
    _needed_api = (TranslationAPI,)

    sourceLanguagesChanged = Signal()
    targetLanguagesChanged = Signal()

    def onInit(self):
        self._sl_model = LanguageListModel()
        self._tl_model = LanguageListModel()

    def onLoaded(self):
        self.loadSourceLanguages()
        self.loadTargetLanguages()

    def loadSourceLanguages(self):
        api = self.getApi(TranslationAPI)
        languages = [
            {'code': k, 'name': LANGUAGES_VERBOSE.get(k, 'Unknown')}
            for k in api.get_source_languages().keys()
        ]
        self._sl_model.provideData(languages)
        self.sourceLanguagesChanged.emit()

    def loadTargetLanguages(self):
        api = self.getApi(TranslationAPI)
        languages = [
            {'code': k, 'name': LANGUAGES_VERBOSE.get(k, 'Unknown')}
            for k in api.get_target_languages().keys()
        ]
        self._tl_model.provideData(languages)
        self.targetLanguagesChanged.emit()

    def getSourceLanguages(self):
        return self._sl_model

    sourceLanguages = Property(QObject, getSourceLanguages, notify=sourceLanguagesChanged)

    def getTargetLanguages(self):
        return self._tl_model

    targetLanguages = Property(QObject, getTargetLanguages, notify=targetLanguagesChanged)

    @Slot(str)
    def setSourceLanguage(self, code: str):
        api = self.getApi(TranslationAPI)
        api.set_source_language(code)

    @Slot(str)
    def setTargetLanguage(self, code: str):
        api = self.getApi(TranslationAPI)
        api.set_target_language(code)
