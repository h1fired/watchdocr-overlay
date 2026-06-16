import QtQuick


Rectangle {
    id: root

    implicitWidth: row.implicitWidth + 20

    state: "idle"
    states: [
        State {
            name: "live"
            PropertyChanges {
                target: root
                color: "#0F3226"
            }
            PropertyChanges {
                target: stateText
                text: "Active"
                color: "#82FFAC"
            }
        },
        State {
            name: "idle"
            PropertyChanges {
                target: root
                color: "#2C2C2C"
            }
            PropertyChanges {
                target: stateText
                text: "Idle"
                color: "#B4B4B4"
            }
        },
    ]

    radius: 9

    Row {
        id: row

        anchors.centerIn: parent
        anchors.verticalCenter: parent.verticalCenter

        spacing: 6

        Text {
            id: stateText

            anchors.verticalCenter: parent.verticalCenter

            font.family: "Segoe UI"
            font.weight: 600
        }
    }
}