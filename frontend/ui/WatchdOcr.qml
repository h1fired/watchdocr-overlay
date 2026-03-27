import QtQuick
import "overlay"
import "overlay/components"
import "common/components"


Rectangle {
    color: "gray"

    OverlaySelectionArea {
        id: selectionArea

        anchors.fill: parent
    }

    OverlayControlPanel {
        id: controlPanel

        y: 20

        anchors.horizontalCenter: parent.horizontalCenter

        height: 44
    }

    OverlayTextConsole {
        id: textConsole

        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
    }
}