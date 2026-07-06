import QtQuick
import QtQuick.Controls.Basic

Menu {
    id: root

    padding: 4

    background: Rectangle {
        implicitWidth: Math.max(root.contentItem.implicitWidth, 140)
        implicitHeight: root.contentItem.implicitHeight

        radius: 9
        color: "#1A1A1A"
        border.width: 1
        border.color: "#353535"
    }
}