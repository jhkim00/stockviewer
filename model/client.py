import sys
import logging
import time
import datetime as dt
from collections import OrderedDict, deque
import pandas as pd
import yfinance as yf

from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QThread, QMutex, QMutexLocker, QWaitCondition

logger = logging.getLogger()

class Client(QObject):
    instance = None
    krxUrl = "https://kind.krx.co.kr/corpgeneral/corpList.do?method=download&searchType=13"

    def __init__(self):
        super().__init__()
        logger.debug("")

        self.krxStocks = None

    @classmethod
    def getInstance(cls):
        if cls.instance is None:
            cls.instance = Client()
        return cls.instance

    """
    public method
    """
    @staticmethod
    def getKrxStocks() -> list:
        # KRX 종목 리스트 가져오기
        krxStocks = pd.read_html(Client.krxUrl, header=0)[0]

        # 종목 코드 형식을 6자리 문자열로 변환
        krxStocks['종목코드'] = krxStocks['종목코드'].astype(str).str.zfill(6)

        # 필요한 컬럼만 선택하여 딕셔너리 리스트로 변환
        stockDictList = krxStocks[['회사명', '종목코드']].rename(columns={'회사명': 'name', '종목코드': 'code'}).to_dict('records')

        # 종목 코드 순으로 오름차순 정렬
        stockDictList.sort(key=lambda x: x['code'])

        return stockDictList

    @staticmethod
    def getDailyChart(stockCode: str):
        logger.debug(f"{stockCode}")
        return Client.__getChartByInterval(stockCode, '1d')

    @staticmethod
    def getWeeklyChart(stockCode: str):
        logger.debug(f"{stockCode}")
        return Client.__getChartByInterval(stockCode, '1wk')

    @staticmethod
    def getMonthlyChart(stockCode: str):
        logger.debug(f"{stockCode}")
        return Client.__getChartByInterval(stockCode, '1mo')

    @staticmethod
    def getMinuteChart(stockCode: str, min_: int):
        logger.debug(f"{stockCode}")
        # min: 1, 2, 5, 15, 30, 60 , 90
        return Client.__getMinuteChartByInterval(stockCode, interval=f'{min_}m')

    """
    private method
    """
    @staticmethod
    def __getChartByInterval(stockCode: str, interval):
        logger.debug(f"{stockCode}:{interval}")

        # 주가 데이터 가져오기
        start_date = None
        df = yf.download(f"{stockCode}.KS", start_date, interval=interval)
        df.columns = df.columns.droplevel(1)  # Ticker 레벨 제거
        df = df.reset_index()  # Date를 일반 컬럼으로 변환

        # 컬럼명 변경
        df = df.rename(columns={
            'Date': 'time',
            'Close': 'close',
            'High': 'high',
            'Open': 'open',
            'Low': 'low',
            'Volume': 'volume'
        })
        return df

    @staticmethod
    def __getMinuteChartByInterval(stockCode: str, interval):
        logger.debug(f"{stockCode}:{interval}")

        # 주가 데이터 가져오기
        start_date = None
        df = yf.download(f"{stockCode}.KS", start_date, interval=interval)
        df.columns = df.columns.droplevel(1)  # Ticker 레벨 제거
        df = df.reset_index()  # Date를 일반 컬럼으로 변환

        # 컬럼명 변경
        df = df.rename(columns={
            'Datetime': 'time',
            'Close': 'close',
            'High': 'high',
            'Open': 'open',
            'Low': 'low',
            'Volume': 'volume'
        })

        # 문자열을 datetime으로 변환 후 UTC 오프셋 제거
        df['time'] = pd.to_datetime(df['time']).dt.tz_convert("Asia/Seoul").dt.strftime("%Y-%m-%d %H:%M:%S")

        return df
