import QtQuick
import QtQuick.Window
import QtQuick.Controls
import App.Gui
import App.Utils
import App.System
import App.Backend
import "common/components"
import "overlay/components"

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

    ScreenArea {
        id: screenArea

        monitor: 0
    
        OWindowPopup {
            id: windowPopup

            x: 0
            y: 0
            width: parent.width
            height: parent.height
        }
    }

    Connections {
        target: System

        function onVisibilitySwapRequested() {
            System.visible = !System.visible;
        }

        function onVisibleChanged() {
            if (!System.visible) {
                Gui.closeWindowPopup();
                System.focusHelper.restore_focus();
            } else {
                requestActivate();
                System.focusHelper.grab_focus(window);
            }
        }
    }

    Component.onCompleted: {
        Gui.setup(windowPopup);
    }
}
