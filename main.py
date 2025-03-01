import sys
import logging
import time
import multiprocessing

from PyQt5.QtCore import QUrl, QT_VERSION_STR
from PyQt5.QtWidgets import *
from PyQt5.QtQml import QQmlApplicationEngine
from PyQt5.QtCore import QCoreApplication, Qt

QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

from viewmodel import MainViewModel, ChartViewModel

logger = logging.getLogger()

def _handleQmlWarnings(warnings):
    for warning in warnings:
        print("QML Warning:", warning.toString())

def __onExit():
    logger.debug("")

if __name__ == "__main__":
    logger.setLevel(logging.DEBUG)
    logger.propagate = 0
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(thread)d][%(filename)s:%(funcName)s:%(lineno)d]'
                                  ' %(message)s')
    streamHandler = logging.StreamHandler()
    streamHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)

    logger.debug(f"Qt version:{QT_VERSION_STR}")

    app = QApplication(sys.argv)
    app.aboutToQuit.connect(__onExit)

    engine = QQmlApplicationEngine()
    engine.warnings.connect(_handleQmlWarnings)

    mainViewModel = MainViewModel(engine.rootContext(), app)
    mainViewModel.init()
    chartViewModel = ChartViewModel(mainViewModel, engine.rootContext(), app)

    engine.load(QUrl.fromLocalFile("qml/Main.qml"))

    if not engine.rootObjects():
        sys.exit(-1)

    sys.exit(app.exec_())
