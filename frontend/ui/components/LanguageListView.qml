import QtQuick
import QtQuick.Controls.Basic


Item {
    id: root

    property int selectedIndex: 0
    property list<string> languages: ([])
    property string current: languages[selectedIndex] || 'empty'

    ListView {
        id: listView

        anchors.fill: parent

        model: root.languages
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

                text: modelData
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
