import QtQuick
import QtQuick.Controls.Basic


Item {
    id: root

    property int selectedIndex: 0
    property list<string> languages: ([])
    property string current: languages[selectedIndex] || languages[0] || "empty"

    ListView {
        id: listView

        anchors.fill: parent

        model: root.languages
        spacing: 0
        clip: true

        delegate: Rectangle {
            width: listView.width
            height: 36

            color: mouse.containsMouse ? "#171A29" : "transparent"

            Text {
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: 20

                text: modelData
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
                anchors.rightMargin: 12

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