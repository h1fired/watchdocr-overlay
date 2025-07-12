import QtQuick 2.15
import QtQuick.Controls 2.15


Item {
    id: root
    property var items: []
    property string selectedTool: items[0].id
    width: row.implicitWidth + 8
    height: row.implicitHeight + 8

    Rectangle {
        anchors.fill: parent
        color: "#1A1B26"
        radius: 6
        border.width: 1
        border.color: "#664DFF"

        Row {
            id: row
            anchors.centerIn: parent
            anchors.margins: 4

            Repeater {
                model: items

                ToolButton {
                    id: btnTool
                    width: 40
                    height: 32
                    background: Rectangle {
                        radius: 3
                        color: btnTool.checked ? "#664CFF" : "transparent"
                    }

                    text: modelData.text.toUpperCase()
                    icon.source: modelData.icon

                    checked: root.selectedTool === modelData.id
                    onClicked: {
                        root.selectedTool = modelData.id
                    }

                    MouseArea {
                        anchors.fill: parent
                        cursorShape: Qt.PointingHandCursor 
                        onPressed: (mouse) => {
                            mouse.accepted = false
                        }
                    }
                }
            }
        }
    }
}
