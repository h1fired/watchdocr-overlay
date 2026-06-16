import QtQuick


Item {
    id: root

    property string sourceLanguage: "None"
    property string targetLanguage: "None"

    implicitWidth: row.implicitWidth

    Row {
        id: row

        anchors.verticalCenter: parent.verticalCenter

        spacing: 8

        Text {
            anchors.verticalCenter: parent.verticalCenter

            text: root.sourceLanguage

            font.family: "Segoe UI"
            font.weight: 600
            font.pixelSize: 13
            color: "#9A9A9A"
        }

        Text {
            anchors.verticalCenter: parent.verticalCenter

            text: "→"

            font.family: "Segoe UI"
            font.pixelSize: 13
            color: "#9A9A9A"
        }

        Text {
            anchors.verticalCenter: parent.verticalCenter

            text: root.targetLanguage

            font.family: "Segoe UI"
            font.weight: 600
            font.pixelSize: 13
            color: "#9A9A9A"
        }
    }
}