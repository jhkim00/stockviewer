import logging

import pandas as pd
from PyQt5.QtCore import QObject, pyqtSlot, pyqtProperty, pyqtSignal
from PyQt5.QtWidgets import QMainWindow, QVBoxLayout, QWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView

from lightweight_charts.widgets import QtChart

from model import Client
from viewmodel import MainViewModel

logger = logging.getLogger()

class ChartViewModel(QObject):
    upColor = 'rgba(200, 97, 100, 100)'
    downColor = 'rgba(39, 157, 130, 100)'
    def __init__(self, mainViewModel, qmlContext, parent=None):
        super().__init__(parent)
        self.qmlContext = qmlContext
        self.qmlContext.setContextProperty('chartViewModel', self)

        self.mv = mainViewModel

        self.currentTimeSelection = 'day'
        self.chart = None

        self.window = QMainWindow()
        self.layout = QVBoxLayout()
        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.window.resize(1920, 1000)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.line_5 = None
        self.line_20 = None
        self.line_60 = None
        self.line_120 = None

    """
    method for qml side
    """
    @pyqtSlot()
    def closeChart(self):
        logger.debug("")
        if self.window:
            self.window.close()

    @pyqtSlot()
    def load(self):
        logger.debug("")
        if self.mv.currentStock is None or len(self.mv.currentStock['code']) == 0:
            return

        self.__createChart()

        if self.currentTimeSelection == 'day':
            data = Client.getInstance().getDailyChart(self.mv.currentStock['code'])
        elif self.currentTimeSelection == 'week':
            data = Client.getInstance().getWeeklyChart(self.mv.currentStock['code'])
        elif self.currentTimeSelection == 'month':
            data = Client.getInstance().getMonthlyChart(self.mv.currentStock['code'])

        self.__onChartDataReceived(data)


    """
    private method
    """
    def __createChart(self):
        if self.chart is None:
            self.chart = QtChart(self.widget, toolbox=True)
            self.chart.topbar.textbox('symbol')
            self.chart.topbar.switcher('timeframe', ('day', 'week', 'month'), default='day',
                                       func=self.__onTimeframeSelection)
            self.chart.candle_style(up_color=ChartViewModel.upColor, down_color=ChartViewModel.downColor)
            self.chart.volume_config(up_color=ChartViewModel.upColor, down_color=ChartViewModel.downColor)
            self.chart.legend(visible=True, font_size=18, color_based_on_candle=True)

            self.layout.addWidget(self.chart.get_webview())
            self.window.setCentralWidget(self.widget)

    @classmethod
    def __calculate_sma(cls, df, period: int = 50):
        return pd.DataFrame({
            'time': df['time'],
            f'SMA {period}': df['close'].rolling(window=period).mean()
        }).dropna()

    def __onTimeframeSelection(self, chart):
        logger.debug(f"{chart.topbar['symbol'].value}:{chart.topbar['timeframe'].value}")
        self.currentTimeSelection = chart.topbar['timeframe'].value
        self.load()

    def __onChartDataReceived(self, df):
        # print(f"{df}")

        self.chart.topbar['symbol'].set(self.mv.currentStock['name'])

        self.chart.set(df)

        if self.line_5 is None:
            self.line_5 = self.chart.create_line(name='SMA 5', color='lightblue', width=2, price_label=False)
        sma_data_5 = self.__calculate_sma(df, period=5)
        self.line_5.set(sma_data_5)

        if self.line_20 is None:
            self.line_20 = self.chart.create_line(name='SMA 20', color='darkkhaki', width=2, price_label=False)
        sma_data_20 = self.__calculate_sma(df, period=20)
        self.line_20.set(sma_data_20)

        if self.line_60 is None:
            self.line_60 = self.chart.create_line(name='SMA 60', color='darkgreen', width=2, price_label=False)
        sma_data_60 = self.__calculate_sma(df, period=60)
        self.line_60.set(sma_data_60)

        if self.line_120 is None:
            self.line_120 = self.chart.create_line(name='SMA 120', color='purple', width=1, price_label=False)
        sma_data_120 = self.__calculate_sma(df, period=120)
        self.line_120.set(sma_data_120)

        self.window.show()