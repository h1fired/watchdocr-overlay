import QtQuick
import "qrc:/qml/ui/common/controls"

OText {
    id: root

    state: "idle"
    states: [
        State {
            name: "idle"
            PropertyChanges {
                target: root
                text: "Idle"
            }
        },
        State {
            name: "processing"
            PropertyChanges {
                target: root
                text: "Processing..."
            }
        },
        State {
            name: "success"
            PropertyChanges {
                target: root
                text: "Success"
            }
        }
    ]

    font.weight: 600
    font.pixelSize: 12
    color: "#475569"
}