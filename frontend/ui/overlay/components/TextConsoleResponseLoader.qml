import QtQuick
import "qrc:/qml/ui/common/controls"

Item {
    id: root

    implicitWidth: row.implicitWidth
    implicitHeight: row.implicitHeight

    state: "idle"
    states: [
        State {
            name: "idle"
            PropertyChanges {
                target: textItem
                text: "Idle"
            }
        },
        State {
            name: "processing"
            PropertyChanges {
                target: textItem
                text: "Processing..."
            }
        },
    ]

    Row {
        id: row

        spacing: 8

        Row {
            anchors.verticalCenter: parent.verticalCenter

            spacing: 3

            Repeater {
                model: [0, 150, 300]
                Rectangle {
                    width: 4
                    height: 4
                    radius: width / 2
                    transformOrigin: Item.Center

                    SequentialAnimation on scale {
                        loops: Animation.Infinite
                        PauseAnimation { duration: modelData }
                        NumberAnimation { to: 1; duration: 300 }
                        NumberAnimation { to: 0; duration: 300 }
                        PauseAnimation { duration: 600 - modelData }
                    }
                }
            }
        }

        OText {
            id: textItem

            text: "Idle"
            font.weight: 600
            font.pixelSize: 14
            color: "#FAF9FF"
        }
    }
}