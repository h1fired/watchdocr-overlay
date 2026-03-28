import QtQuick
import "overlay"
import "overlay/components"
import "common/components"


Rectangle {
    OverlaySelectionArea {
        id: selectionArea

        anchors.fill: parent

        area.enabled: controlPanel.selectionToolActive
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