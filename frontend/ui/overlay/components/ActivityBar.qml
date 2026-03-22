import QtQuick


Rectangle {
    id: root

    implicitWidth: row.implicitWidth + 20

    state: "live"
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
            name: "stopped"
            PropertyChanges {
                target: root
                color: "#1F0C0C"
            }
            PropertyChanges {
                target: stateText
                text: "stopped"
                color: "#D33437"
            }
            PropertyChanges {
                target: circle
                color: "#D33437"
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
            
            width: 6
            height: 6

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