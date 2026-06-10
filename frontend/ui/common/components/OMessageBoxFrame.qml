import QtQuick
import QtQuick.Layouts
import "../controls"


Rectangle {
    id: root

    property         string     title:      "Frame"
    default property alias      content:    contentRect.data
    signal                      closed()

    implicitWidth: 100
    implicitHeight: column.implicitHeight

    color: "#171A25"
    border.width: 1
    border.color: "#292C37"
    radius: 12

    clip: true

    MouseArea {
        anchors.fill: parent
    }

    Column {
        id: column

        anchors.fill: parent

        Rectangle {
            width: parent.width
            height: 52

            color: "#171A25"
            topLeftRadius: 12
            topRightRadius: 12

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: 16
                anchors.rightMargin: 10

                OText {
                    text: root.title
                    font.weight: 700
                    font.pixelSize: 13
                    color: "#E2E8F4"
                }

                OButton {
                    Layout.preferredWidth: 40
                    Layout.preferredHeight: 40
                    Layout.alignment: Qt.AlignRight

                    icon.source: "../../../../resources/icons/close.svg"
                    icon.width: 14
                    icon.height: 14
                    icon.color: "#2d323b"

                    background: Item {}

                    onClicked: root.closed()
                }
            }
        }

        Rectangle {
            width: parent.width
            height: 1

            color: "#292C37"
        }

        Rectangle {
            id: contentRect

            width: parent.width
            implicitHeight: children.length !== 0 ? children[0].implicitHeight : 0

            color: "#0E101A"
            bottomLeftRadius: 12
            bottomRightRadius: 12
        }
    }

    onVisibleChanged: {
        if (!root.visible) {
            root.closed();
        }
    }
}
