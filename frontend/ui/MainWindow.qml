import QtQuick
import QtQuick.Window
import QtQuick.Controls
import App.Gui
import "common/components"


Window {
    id: window

    visible: true

    width: 800
    height: 600

    title: "OCR Overlay"

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

    Component.onCompleted: {
        Gui.setup(windowPopup);
    }
}
