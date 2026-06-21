import QtQuick
import QtQuick.Layouts
import "qrc:/qml/ui/common/controls"

OButton {
    id: root

    property string language: "None"
    property string shortLanguage: "NN"

    implicitWidth: contentItemRow.implicitWidth + 16

    font.family: "Segoe UI"

    background: Rectangle {
        color: parent.hovered ? "#2C2C2C" : "transparent"
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
                color: '#E7E7E7'
            }

            Text {
                anchors.verticalCenter: parent.verticalCenter

                text: root.language
                font.family: root.font.family
                font.weight: 600
                font.pixelSize: 12
                color: "#F1F1F1"
            }
        }
    }
}