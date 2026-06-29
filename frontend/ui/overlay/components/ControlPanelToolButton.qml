import QtQuick


OButton {
    id: root

    checkable: true

    icon.color: "#E9E9E9"
    icon.width: 22
    icon.height: 22

    background: Rectangle {
        color: parent.hovered || parent.checked ? "#2C2C2C" : "transparent"
        radius: 6
    }

    ToolTip.visible: hovered
    ToolTip.delay: 1000

    onClicked: {
        checked = !checked;
    }
}