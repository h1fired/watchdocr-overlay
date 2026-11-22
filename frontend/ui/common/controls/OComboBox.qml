import QtQuick
import QtQuick.Controls.Basic

ComboBox {
    id: root

    implicitWidth: 140
    implicitHeight: 28

    font.family: "Segoe UI"
    font.pixelSize: 12

    contentItem: Text {
        leftPadding: 10
        rightPadding: root.indicator.width + 4

        text: root.displayText
        font: root.font
        color: "#d4d4d4"
        verticalAlignment: Text.AlignVCenter
        elide: Text.ElideRight
    }

    indicator: Text {
        x: root.width - width - 10
        y: (root.height - height) / 2

        text: "▾"
        font.pixelSize: 10
        color: root.hovered || root.popup.visible ? "#d4d4d4" : "#8a8a8a"
    }

    background: Rectangle {
        color: "#242424"
        radius: 6
        border.width: 1
        border.color: root.pressed || root.popup.visible ? "#5a5a5a" : "#2C2C2C"

        Behavior on border.color {
            ColorAnimation { duration: 120 }
        }
    }

    delegate: ItemDelegate {
        id: item

        required property int index

        width: ListView.view.width
        implicitHeight: 28

        contentItem: Text {
            leftPadding: 4

            text: root.textAt(item.index)
            font: root.font
            color: item.hovered || root.highlightedIndex === item.index
                ? "#F3F3F3"
                : "#BDBDBD"
            verticalAlignment: Text.AlignVCenter
            elide: Text.ElideRight
        }

        background: Rectangle {
            radius: 6
            color: item.hovered || root.highlightedIndex === item.index
                ? "#333333"
                : "#1A1A1A"
        }
    }

    popup.padding: 4
    popup.background: Rectangle {
        radius: 9
        color: "#1A1A1A"
        border.width: 1
        border.color: "#353535"
    }
}
