import QtQuick
import QtQuick.Controls.Basic


Item {
    property int selectedIndex: -1

    ListModel {
        id: listModel
        ListElement { name: "Option 1" }
        ListElement { name: "Option 2" }
        ListElement { name: "Option 3" }
        ListElement { name: "Option 4" }
    }

    ListView {
        id: listView

        anchors.fill: parent

        model: listModel
        spacing: 0
        clip: true

        delegate: Rectangle {
            width: listView.width
            height: 32

            radius: 6
            color: mouse.containsMouse ? "#191919" : "transparent"

            Text {
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: 12

                text: name
                color: "white"
            }

            Rectangle {
                width: 4
                height: 4

                anchors.verticalCenter: parent.verticalCenter
                anchors.right: parent.right
                anchors.rightMargin: 12

                visible: index === selectedIndex
             
                radius: height / 2
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
