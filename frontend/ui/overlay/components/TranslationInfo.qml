import QtQuick


Item {
    id: root

    property string sourceLanguage: "None"
    property string sourceShortLanguage: "NN"
    property string targetLanguage: "None"
    property string targetShortLanguage: "NN"

    implicitWidth: row.implicitWidth

    Row {
        id: row

        anchors.verticalCenter: parent.verticalCenter

        spacing: 8

        Text {
            anchors.verticalCenter: parent.verticalCenter

            text: root.sourceShortLanguage

            font.family: "Segoe UI"
            font.weight: 500
            font.pixelSize: 10
            color: "#475569"
        }

        Text {
            anchors.verticalCenter: parent.verticalCenter

            text: root.sourceLanguage

            font.family: "Segoe UI"
            font.weight: 600
            font.pixelSize: 12
            color: "#475569"
        }

        Text {
            anchors.verticalCenter: parent.verticalCenter

            text: "→"

            font.family: "Segoe UI"
            font.pixelSize: 12
            color: "#8B5CF6"
        }

        Text {
            anchors.verticalCenter: parent.verticalCenter

            text: root.targetShortLanguage

            font.family: "Segoe UI"
            font.weight: 500
            font.pixelSize: 10
            color: "#475569"
        }

        Text {
            anchors.verticalCenter: parent.verticalCenter

            text: root.targetLanguage

            font.family: "Segoe UI"
            font.weight: 600
            font.pixelSize: 12
            color: "#475569"
        }
    }
}