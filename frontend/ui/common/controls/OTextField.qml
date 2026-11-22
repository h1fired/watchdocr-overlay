import QtQuick
import QtQuick.Controls.Basic

TextField {
    id: root

    implicitWidth: 140
    implicitHeight: 28

    leftPadding: 10
    rightPadding: 10
    verticalAlignment: TextInput.AlignVCenter

    font.family: "Segoe UI"
    font.pixelSize: 12
    color: "#d4d4d4"
    placeholderTextColor: "#4d4d4d"
    selectionColor: "#3A5A9C"
    selectedTextColor: "#F1F1F1"

    background: Rectangle {
        color: "#242424"
        radius: 6
        border.width: 1
        border.color: root.activeFocus
            ? "#5a5a5a"
            : root.hovered ? "#3a3a3a" : "#2C2C2C"

        Behavior on border.color {
            ColorAnimation { duration: 120 }
        }
    }
}
