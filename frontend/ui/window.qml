import QtQuick
import QtQuick.Window
import QtQuick.Controls
import App.Backend
import App.Utils
import "components"


Window {
    id: window

    x: EScreen.globalX
    y: EScreen.globalY
    width: EScreen.globalWidth
    height: EScreen.globalHeight

    visible: true

    title: "OCR Overlay"
    color: "transparent"
    flags: Qt.FramelessWindowHint

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
                Backend.OcrTranslate.terminateTask();
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
                Backend.OcrTranslate.terminateTask();
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
}
