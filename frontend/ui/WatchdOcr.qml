import QtQuick
import "overlay"


Rectangle {
    color: "gray"

    OverlayContolPanel {
        y: 20

        anchors.horizontalCenter: parent.horizontalCenter

        width: 200
        height: 40

        radius: 12
    }
}