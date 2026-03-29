import QtQuick
import "overlay"
import "overlay/components"
import "common/components"


Item {
    OverlaySelectionArea {
        id: selectionArea

        anchors.fill: parent

        area.enabled: controlPanel.selectionToolActive

        Connections {
            target: selectionArea.area

            function onBoxReleased() {
                controlPanel.selectionToolActive = false;
            }
        }
    }

    ScreenArea {
        id: screenArea

        monitor: 0

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
}