import QtQuick
import QtQuick.Controls
import "qrc:/qml/ui/common/controls"

OButton {
    id: root

    icon.color: enabled ? "#E9E9E9" : "#A0A0A0"
    icon.width: 22
    icon.height: 22

    background: Rectangle {
        color: (
            !parent.enabled ? "transparent" :
            parent.hovered || parent.checked ? "#2C2C2C" : "transparent"
        )
        radius: 6
    }

    ToolTip.visible: hovered
    ToolTip.delay: 1000
}