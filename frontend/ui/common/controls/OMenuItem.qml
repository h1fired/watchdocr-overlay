import QtQuick
import QtQuick.Controls.Basic

MenuItem {
    id: root

    implicitHeight: 28
    implicitWidth: 180

    contentItem: Text {
        text: root.text
        color: root.hovered ? "#F3F3F3" : "#BDBDBD"
        verticalAlignment: Text.AlignVCenter
        leftPadding: 8
        rightPadding: 8
    }

    background: Rectangle {
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        radius: 6
        color: root.hovered ? "#333333" : "#1A1A1A"
    }
}