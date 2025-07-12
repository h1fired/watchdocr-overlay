import QtQuick 2.15
import QtQuick.Window 2.15


Window {
    visible: true
    width: 640
    height: 480
    title: "OCR Overlay"
    // color: "transparent"
    // flags: Qt.FramelessWindowHint | Qt.Window

    OCROverlay {
        anchors.fill: parent
    }
}
