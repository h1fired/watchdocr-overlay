import QtQuick
import QtQuick.Layouts
import "../../common/controls"


Item {
    id: root

    implicitWidth: row.width

    Row {
        id: row

        TranslationSelectorButton {
            height: root.height
        }

        OButton {
            width: height
            height: root.height

            icon.source: "../../../../resources/icons/swap.svg"
            icon.color: hovered ? "#94A3B8" : "#475569"
            icon.width: 18
            icon.height: 18

            background: Rectangle {
                color: parent.hovered ? "#1B1E28" : "transparent"
                radius: 6
            }
        }

        TranslationSelectorButton {
            height: root.height
        }
    }
}