import QtQuick 2.15
import QtQuick.Controls.Basic 2.15


Item {
    id: root

    signal fullscreenSelected()

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
            spacing: 4

            Button {
                width: 40
                height: 32
                background: Rectangle {
                    color: "#664CFF"
                    radius: 3
                }
                icon.source: "../../../resources/icons/selection.svg"
                icon.color: "#FFFFFF"

                MouseArea {
                    anchors.fill: parent
                    cursorShape: Qt.PointingHandCursor 
                    onPressed: (mouse) => {
                        mouse.accepted = false
                    }
                }
            }

            Button {
                id: btnFullscreen
                width: 40
                height: 32
                background: Rectangle {
                    color: btnFullscreen.hovered ? "#242638" : "transparent"
                    radius: 3
                }
                icon.source: "../../../resources/icons/fullscreen.svg"
                icon.color: "#FFFFFF"

                onClicked: {
                    root.fullscreenSelected();
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
