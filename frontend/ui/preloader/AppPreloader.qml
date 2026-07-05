import QtQuick
import QtQuick.Controls.Basic


Rectangle {
    id: root
    
    property alias label: text.text
    property alias progress: progressBar.value

    implicitWidth: 380
    implicitHeight: column.implicitHeight + (48)

    radius: 15
    color: "#1A1A1A"
    border.width: 1
    border.color: "#353535"

    Column {
        id: column

        width: parent.implicitWidth

        anchors.centerIn: parent

        spacing: 12

        Image {
            anchors.horizontalCenter: parent.horizontalCenter

            width: 60
            height: 60

            source: "qrc:/qml/resources/icons/preloader_logo.png"
            sourceSize.width: width
            sourceSize.height: height
        }

        LoaderAnim {
            anchors.horizontalCenter: parent.horizontalCenter
        }

        Text {
            id: text

            anchors.horizontalCenter: parent.horizontalCenter

            font.family: "Segoe UI"
            font.weight: 700
            font.pixelSize: 14
            color: text !== "" ? "#FAF9FF" : "#060606"

            text: " "
        }

        ProgressBar {
            id: progressBar

            width: parent.width / 1.5
            height: 3

            anchors.horizontalCenter: parent.horizontalCenter

            background: Rectangle {
                anchors.fill: parent

                radius: height / 2
                color: "#2F2F2F"
            }

            contentItem: Item {
                implicitWidth: parent.implicitWidth
                implicitHeight: parent.implicitHeight

                Rectangle {
                    width: parent.width * progressBar.visualPosition
                    height: parent.height

                    radius: height / 2
                    color: "#75A0FF"
                }
            }
        }
    }
}