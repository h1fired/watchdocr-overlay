import QtQuick
import QtQuick.Window
import QtQuick.Controls
import App.Gui
import App.Utils
import App.System
import App.Backend
import "common/components"


Window {
    id: window

    visible: true

    x: UtilsScreen.globalX
    y: UtilsScreen.globalY
    width: UtilsScreen.globalWidth
    height: UtilsScreen.globalHeight

    title: "OCR Overlay"
    flags: window.mainUiVisible
        ? Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint
        : Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.WindowTransparentForInput
    color: "transparent"

    property bool mainUiVisible: System.visible

    Loader {
        id: loaderWatchdOcr

        anchors.fill: parent

        active: Backend.status === ViewModelStatus.READY
        focus: true
        sourceComponent: Component {
            WatchdOcr {
                id: watchdOcr

                anchors.fill: parent

                controlsVisible: window.mainUiVisible
            }
        }
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

        function onVisibilitySwapRequested() {
            System.visible = !System.visible;
        }
    }

    Component.onCompleted: {
        Gui.setup(windowPopup);
    }
}
