import QtQuick 2.15
import QtQuick.Window 2.15
import QtQuick.Controls 2.15


Window {
    id: window
    visible: true
    x: 0
    y: 0
    width: Screen.width
    height: Screen.height
    title: "OCR Overlay"
    color: "transparent"
    flags: Qt.FramelessWindowHint | Qt.Window

    OCROverlay {
        id: overlay
        anchors.fill: parent

        focus: true

        Keys.onPressed: (event)=> {
            if (event.key == Qt.Key_Escape) {
                window.close()
                event.accepted = true;
            }
        }
    }

    onVisibleChanged: {
        if (window.visible) {
            overlay.mode = OCROverlay.Mode.Selection
        } else {
            overlay.mode = OCROverlay.Mode.StandBy
        }
    }
}
