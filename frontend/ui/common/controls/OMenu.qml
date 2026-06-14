import QtQuick
import QtQuick.Controls.Basic


Menu {
    id: root

    background: Rectangle {
        implicitWidth: Math.max(root.contentItem.implicitWidth, 140)
        implicitHeight: root.contentItem.implicitHeight

        radius: 12
        color: "#070B14"
        border.width: 1
        border.color: "#21242D"
    }
}
