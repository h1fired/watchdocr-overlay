import QtQuick
import QtQuick.Layouts
import "../../common/controls"


OButton {
    id: root

    property string language: "None"
    property string shortLanguage: "NN"

    implicitWidth: contentItemRow.implicitWidth + 16

    font.family: "Segoe UI"

    background: Rectangle {
        color: parent.hovered ? "#1B1E28" : "transparent"
        radius: 6
    }

    contentItem: Item {
        anchors.fill: parent

        Row {
            id: contentItemRow

            anchors.centerIn: parent

            spacing: 4

            Text {
                anchors.verticalCenter: parent.verticalCenter

                text: root.shortLanguage
                font.family: root.font.family
                font.weight: 600
                font.pixelSize: 10
                color: '#E4E3E9'
            }

            Text {
                anchors.verticalCenter: parent.verticalCenter

                text: root.language
                font.family: root.font.family
                font.weight: 600
                font.pixelSize: 12
                color: "#FAF9FF"
            }
        }
    }
}