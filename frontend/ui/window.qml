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
    }

    Shortcut {
        sequences: ["Escape"]
        onActivated: () => {
            window.close()
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
