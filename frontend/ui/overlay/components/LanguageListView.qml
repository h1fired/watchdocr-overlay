import QtQuick
import QtQuick.Controls.Basic


Item {
    id: root

    property int selectedIndex: 0
    property var languages: []
    readonly property string current: languages.get(selectedIndex)?.code || "NN"
    readonly property string currentName: languages.get(selectedIndex)?.name || "None"

    ListView {
        id: listView

        anchors.fill: parent

        model: root.languages
        spacing: 0
        clip: true

        ScrollBar.vertical: ScrollBar {
            policy: ScrollBar.AlwaysOn

            contentItem: Rectangle {
                implicitWidth: 6
                color: parent.pressed ? "#21242D" : "#21242D"
                opacity: parent.active ? 1.0 : 0.5

                Behavior on opacity {
                    NumberAnimation { duration: 200 }
                }
            }
        }

        delegate: Rectangle {
            width: listView.width
            height: 36

            color: mouse.containsMouse ? "#171A29" : "transparent"

            Text {
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: 20

                text: model.code
                color: (
                    index === selectedIndex ? "#A78BFA" :
                    mouse.containsMouse ? "#C8D3E8" : "#475569"
                )

                font.family: "Segoe UI"
                font.weight: 600
                font.pixelSize: 10
            }

            Text {
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: 52

                text: model.name
                color: (
                    index === selectedIndex ? "#A78BFA" :
                    mouse.containsMouse ? "#C8D3E8" : "#798499"
                )

                font.family: "Segoe UI"
                font.weight: index === selectedIndex ? 600 : 500
            }

            Rectangle {
                visible: index === selectedIndex
                
                width: 4
                height: 4

                anchors.verticalCenter: parent.verticalCenter
                anchors.right: parent.right
                anchors.rightMargin: 16

                radius: height / 2
                color: "#8B5CF6"
            }

            MouseArea {
                id: mouse

                anchors.fill: parent

                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor

                onClicked: selectedIndex = index
            }
        }
    }
}