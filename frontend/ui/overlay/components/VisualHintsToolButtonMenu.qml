import QtQuick
import QtQuick.Controls.Basic
import "../../common/controls"

OButton {
    id: root

    property alias showEnabled: optionShow.checked
    property alias asOverlayEnabled: optionAsOverlay.checked

    icon.source: "../../../../resources/icons/visual_hint.svg"
    icon.color: "#E9E9E9"
    icon.width: 20
    icon.height: 20

    background: Rectangle {
        color: parent.hovered || parent.checked ? "#2C2C2C" : "transparent"
        radius: 6
    }

    ToolTip.text: "Visual hints options"
    ToolTip.visible: hovered
    ToolTip.delay: 1000

    onClicked: contextMenu.popup(root, 0, root.height + 8)
    checked: contextMenu.visible

    OMenu {
        id: contextMenu

        OMenuItem {
            id: optionShow

            text: "Show"
            checkable: true
            checked: root.showEnabled
        }

        OMenuItem {
            id: optionAsOverlay

            text: "As overlay"
            checkable: true
            checked: root.asOverlayEnabled
        }
    }
}