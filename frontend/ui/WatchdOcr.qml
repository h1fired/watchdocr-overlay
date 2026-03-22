import QtQuick
import "overlay"
import "overlay/components"


Rectangle {
    color: "gray"

    SelectionArea {
        anchors.fill: parent
    }

    OverlayControlPanel {
        y: 20

        anchors.horizontalCenter: parent.horizontalCenter

        height: 44
    }

    OverlayTextConsole {
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: 20
    }
}