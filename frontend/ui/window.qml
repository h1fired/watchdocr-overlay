import QtQuick
import QtQuick.Window
import QtQuick.Controls


Window {
    id: window

    x: 0
    y: 0
    width: Screen.width
    height: Screen.height

    visible: true

    title: "OCR Overlay"
    color: "transparent"
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint

    onVisibleChanged: {
        if (window.visible) {
            overlay.mode = OCROverlay.Mode.Selection;
        } else {
            overlay.mode = OCROverlay.Mode.StandBy;
        }
        overlay.visible = window.visible;
    }

    Connections {
        target: system

        function onVisibilityChanged() {
            if (window.visible) {
                window.close();
                window.visible = false;
            } else {
                window.show();
                window.visible = true;
            }
        }
    }

    Connections {
        target: overlay

        function onCloseRequested() {
            if (window.visible) {
                window.close();
                window.visible = false;
            }
        }
    }

    Shortcut {
        sequence: "Escape"
        context: Qt.ApplicationShortcut
        onActivated: {
            window.close();
            window.visible = false
        }
    }

    OCROverlay {
        id: overlay
        anchors.fill: parent
        focus: true
    }

    DebugPanel {
        x: 0
        y: 0
        width: 400
    }
}
