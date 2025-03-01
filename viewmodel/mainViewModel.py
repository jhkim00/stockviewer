import logging

from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal, QVariant
from PyQt5.QtQml import QJSValue

from model import Client

logger = logging.getLogger()

class MainViewModel(QObject):
    currentStockChanged = pyqtSignal(str, str)
    searchedStockListChanged = pyqtSignal()

    def __init__(self, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('mainViewModel', self)

        self._stockList = []
        self._currentStock = None
        self._searchedStockList = []

    @pyqtProperty(QVariant, notify=currentStockChanged)
    def currentStock(self):
        return self._currentStock

    @currentStock.setter
    def currentStock(self, val: dict):
        if self._currentStock != val:
            logger.debug(f"stock:{val}")
            self._currentStock = val
            self.currentStockChanged.emit(self._currentStock['name'], self._currentStock['code'])

    @pyqtProperty(list, notify=searchedStockListChanged)
    def searchedStockList(self):
        return self._searchedStockList

    @searchedStockList.setter
    def searchedStockList(self, val: list):
        self._searchedStockList = val
        self.searchedStockListChanged.emit()

    """
    public method
    """
    @pyqtSlot()
    def init(self):
        logger.debug("")
        self._stockList = Client.getKrxStocks()
        self.searchedStockList = self._stockList

    @pyqtSlot(QVariant)
    def setCurrentStock(self, val):
        if isinstance(val, dict):
            self.currentStock = val
        elif isinstance(val, QJSValue):
            self.currentStock = val.toVariant()

    @pyqtSlot(str)
    def setInputText(self, inputText):
        logger.debug(inputText)

        if len(inputText) == 0 or inputText == ' ':
            self.searchedStockList = self._stockList
        else:
            self.searchedStockList = list(map(lambda x: x,
                                              list(filter(lambda x: x['name'].lower().find(inputText.lower()) != -1
                                                                    or x['code'].lower().find(inputText.lower()) != -1,
                                                          self._stockList))))