import QtQuick
import QtQuick.Controls.Basic


Switch {
    id: root

    implicitWidth: 42
    implicitHeight: 16

    indicator: Rectangle {
        implicitWidth: root.implicitWidth
        implicitHeight: root.implicitHeight
        radius: height / 2
        color: "#070B14"
        border.width: 1
        border.color: "#21242D"
        clip: true

        Rectangle {
            implicitWidth: parent.implicitWidth
            implicitHeight: parent.implicitHeight
            radius: height / 2
            color: (
                root.checked
                ? root.enabled ? "#75a0ff" : Qt.darker("#75a0ff", 3.0)
                : "transparent"
            )

            Behavior on color {
                ColorAnimation {
                    duration: 200
                    easing.type: Easing.InOutQuad
                }
            }
        }

        Rectangle {
            id: handle

            x: root.checked ? parent.width - width - 2 : 2

            width: parent.implicitHeight - 4
            height: parent.implicitHeight - 4

            anchors.verticalCenter: parent.verticalCenter

            radius: width / 2
            color: (
                root.checked
                ? "#151515"
                : root.enabled ? "#DBDBDB" : "#151515"
            )

            Behavior on x {
                NumberAnimation { duration: 200; easing.type: Easing.InOutQuad }
            }

            Behavior on color {
                ColorAnimation {
                    duration: 200
                    easing.type: Easing.InOutQuad
                }
            }
        }
    }

    MouseArea {
        anchors.fill: parent
        cursorShape: Qt.PointingHandCursor

        onPressed: (e) => {
            e.accepted = false;
        }
    }
}