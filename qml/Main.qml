import QtQuick 2.15
import QtQuick.Controls 2.15
import "./component"

ApplicationWindow {
    id: root
    visible: true
    width: fixedWidth
    height: fixedHeight
    minimumWidth: fixedWidth
    maximumWidth: fixedWidth
    minimumHeight: fixedHeight
    maximumHeight: fixedHeight
    title: "Stock Viewer"

    property var fixedWidth: 480
    property var fixedHeight: 480

    Component.onCompleted: {
        console.log("market component completed")
    }

    onClosing: {
        chartViewModel.closeChart()
    }

    StockInputField {
        id: stockInputField
        width: parent.width
        height: 40
        focus: true

        stockListView: _stockListView

        onReturnPressed: {
            console.trace()
            var stock = stockListView.getCurrentStock()
            if (typeof(stock) !== 'undefined') {
                mainViewModel.setCurrentStock(stock)
                chartViewModel.load()
            }
        }

        onDisplayTextChanged: {
            mainViewModel.setInputText(displayText)
        }
    }

    StockListView {
        id: _stockListView
        anchors.top: stockInputField.bottom
        anchors.topMargin: 2
        width: parent.width
        height: parent.height - stockInputField.height - anchors.topMargin
        model: mainViewModel.searchedStockList
    }
}
