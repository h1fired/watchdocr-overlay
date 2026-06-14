import QtQuick
import QtQuick.Controls.Basic
import "../../common/controls"

OButton {
    id: root

    property alias showEnabled: optionShow.checked
    property alias asOverlayEnabled: optionAsOverlay.checked

    icon.source: "../../../../resources/icons/selection.svg"
    icon.color: hovered || checked ? "#94A3B8" : "#475569"
    icon.width: 22
    icon.height: 22

    background: Rectangle {
        color: parent.hovered || parent.checked ? "#1B1E28" : "transparent"
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
        }

        OMenuItem {
            id: optionAsOverlay

            text: "As overlay"
            checkable: true
        }
    }
}