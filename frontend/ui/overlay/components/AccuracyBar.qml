import QtQuick


Item {
    id: root

    property int accuracy: 0

    implicitWidth: row.implicitWidth

    Row {
        id: row

        anchors.verticalCenter: parent.verticalCenter

        spacing: 6

        Rectangle {
            anchors.verticalCenter: parent.verticalCenter
            
            width: 32
            height: 4

            radius: height / 2
            
            color: "#475569"

            Rectangle {
                width: (root.accuracy / 100) * parent.width
                height: parent.height

                radius: height / 2

                color: root.accuracy > 70 ? "#34D399" : "#8993A1"
            }
        }

        Text {
            anchors.verticalCenter: parent.verticalCenter
            
            text: accuracy + "%"

            font.family: "Segoe UI"
            font.weight: 600
            font.pixelSize: 12
            color: root.accuracy > 70 ? "#34D399" : "#8993A1"
        }
    }
}