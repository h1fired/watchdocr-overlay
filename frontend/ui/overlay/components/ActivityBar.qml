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
                color: "#0C191F"
            }
            PropertyChanges {
                target: stateText
                text: "live"
                color: "#34D399"
            }
            PropertyChanges {
                target: circle
                color: "#34D399"
            }
        },
        State {
            name: "idle"
            PropertyChanges {
                target: root
                color: "#23272F"
            }
            PropertyChanges {
                target: stateText
                text: "idle"
                color: "#94A3B8"
            }
            PropertyChanges {
                target: circle
                color: "#94A3B8"
            }
        },
    ]

    radius: 6

    Row {
        id: row

        anchors.centerIn: parent
        anchors.verticalCenter: parent.verticalCenter

        spacing: 6

        Rectangle {
            id: circle

            anchors.verticalCenter: parent.verticalCenter
            
            width: 4
            height: 4

            radius: height / 2
        }

        Text {
            id: stateText

            anchors.verticalCenter: parent.verticalCenter

            font.family: "Segoe UI"
            font.weight: 600
        }
    }
}