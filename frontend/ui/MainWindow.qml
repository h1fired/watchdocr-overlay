import QtQuick
import QtQuick.Window
import QtQuick.Controls
import App.Gui
import App.Utils
import App.System
import "common/components"


Window {
    id: window

    visible: true

    x: UtilsScreen.globalX
    y: UtilsScreen.globalY
    width: UtilsScreen.globalWidth
    height: UtilsScreen.globalHeight

    title: "OCR Overlay"
    flags: Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
    color: "transparent"

    WatchdOcr {
        anchors.fill: parent
    }

    OWindowPopup {
        id: windowPopup

        x: 0
        y: 0
        width: window.width
        height: window.height
    }

    Connections {
        target: System

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

    Component.onCompleted: {
        Gui.setup(windowPopup);
    }
}
