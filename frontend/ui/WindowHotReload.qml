import QtQuick
import QtQuick.Window
import QtQuick.Controls


Window {
    id: window

    visible: true

    x: 1280
    y: 0
    width: 1280
    height: 560

    title: "OCR Overlay"
    flags: Qt.FramelessWindowHint

    WatchdOcr {
        anchors.fill: parent
    }
}
