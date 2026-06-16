import QtQuick
import QtQuick.Controls.Basic


Item {
    id: root

    property var languages: []
    property string current: ""
    readonly property string currentName: languages.getNameByCode(current) ?? "None"

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
                color: "#646464"
                opacity: parent.active ? 1.0 : 0.5

                Behavior on opacity {
                    NumberAnimation { duration: 200 }
                }
            }
        }

        delegate: Rectangle {
            width: listView.width
            height: 36

            color: mouse.containsMouse ? "#121c31" : "transparent"

            readonly property bool isSelected: model.code === root.current

            Text {
                anchors.verticalCenter: parent.verticalCenter
                anchors.left: parent.left
                anchors.leftMargin: 20

                text: model.code
                color: (
                    isSelected ? "#75A0FF" :
                    mouse.containsMouse ? "#DDDDDD" : "#9C9C9C"
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
                    isSelected ? "#75A0FF" :
                    mouse.containsMouse ? "#DDDDDD" : "#9C9C9C"
                )

                font.family: "Segoe UI"
                font.weight: isSelected ? 600 : 500
            }

            Rectangle {
                visible: isSelected
                
                width: 4
                height: 4

                anchors.verticalCenter: parent.verticalCenter
                anchors.right: parent.right
                anchors.rightMargin: 16

                radius: height / 2
                color: "#75A0FF"
            }

            MouseArea {
                id: mouse

                anchors.fill: parent

                hoverEnabled: true
                cursorShape: Qt.PointingHandCursor

                onClicked: root.current = model.code
            }
        }
    }

    Component.onCompleted: {
        if (
            root.languages.count > 0
            && root.current === ""
            && !root.languages.codeExists(root.current)
        )
            root.current = root.languages.get(0).code;
    }
}