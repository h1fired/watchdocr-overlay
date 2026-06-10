from frontend.viewmodels.common.mvvm import QmlViewModel
from src.watchdocr.api.translation import TranslationAPI
from src.watchdocr.plugins.translation.types import LANGUAGES_VERBOSE
from qt.core import (
    Qt,
    Property,
    Signal,
    Slot,
    QAbstractListModel,
    QSortFilterProxyModel,
    QModelIndex,
    QObject,
    QRegularExpression
)


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

    def entries(self):
        return self._entries


class LanguageFilterProxyModel(QSortFilterProxyModel):
    countChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilterCaseSensitivity(Qt.CaseInsensitive)
        self.setFilterRole(LanguageListModel.NameRole)

    @Slot(str)
    def setSearchQuery(self, query: str):
        escaped = QRegularExpression.escape(query)
        self.setFilterRegularExpression(escaped)

    @Slot(str, result=str)
    def getNameByCode(self, code: str):
        if self.rowCount() == 0:
            return None
        items = tuple(filter(
            lambda e: e['code'] == code,
            self.sourceModel().entries()
        ))
        if not len(items):
            return None
        return items[0]['name']

    @Property(int, notify=countChanged)
    def count(self):
        return self.rowCount()

    @Slot(int, result='QVariant')
    def get(self, row: int):
        return self.sourceModel().get(row)

    @Slot(str, result=bool)
    def codeExists(self, code: str):
        if self.rowCount() == 0:
            return None
        items = tuple(filter(
            lambda e: e['code'] == code,
            self.sourceModel().entries()
        ))
        return len(items) > 0


class TranslationViewModel(QmlViewModel):
    _name = 'Translation'
    _needed_api = (TranslationAPI,)

    sourceLanguagesChanged = Signal()
    targetLanguagesChanged = Signal()
    providerNameChanged = Signal()

    def onInit(self):
        self._sl_model = LanguageListModel()
        self._tl_model = LanguageListModel()
        self._sl_model_proxy = LanguageFilterProxyModel()
        self._sl_model_proxy.setSourceModel(self._sl_model)
        self._tl_model_proxy = LanguageFilterProxyModel()
        self._tl_model_proxy.setSourceModel(self._tl_model)

    def onLoaded(self):
        self.loadSourceLanguages()
        self.loadTargetLanguages()

    def getProviderName(self):
        api = self.getApi(TranslationAPI)
        return api.get_provider_name()

    providerName = Property(str, getProviderName, notify=providerNameChanged)

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
        return self._sl_model_proxy

    sourceLanguages = Property(QObject, getSourceLanguages, notify=sourceLanguagesChanged)

    def getTargetLanguages(self):
        return self._tl_model_proxy

    targetLanguages = Property(QObject, getTargetLanguages, notify=targetLanguagesChanged)

    @Slot(str)
    def setLanguageSearchQuery(self, text: str):
        self._sl_model_proxy.setSearchQuery(text)
        self._tl_model_proxy.setSearchQuery(text)

    @Slot(str)
    def setSourceLanguage(self, code: str):
        api = self.getApi(TranslationAPI)
        api.set_source_language(code)

    @Slot(str)
    def setTargetLanguage(self, code: str):
        api = self.getApi(TranslationAPI)
        api.set_target_language(code)
